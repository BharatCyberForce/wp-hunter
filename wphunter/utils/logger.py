import sys
import json
import csv
import os
from colorama import Fore, Style
try:
    from tqdm import tqdm as actual_tqdm
    _tqdm_write = actual_tqdm.write
except ImportError:
    _tqdm_write = print
from rich.tree import Tree
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from collections import defaultdict

class Logger:

    def __init__(self, verbose=False, silent=False):
        self.verbose = verbose
        self.silent = silent
        self.vulnerable_findings = {}
        self.console = Console(file=sys.stdout)
        self.severity_colors = {
            'critical': 'bold red',
            'high': 'bold yellow',
            'medium': 'bold orange1',
            'low': 'bold red',
            'informational': 'bold blue',
            'n/a': 'white'
        }

    def log(self, message, level='info'):

        if level in ['warning', 'error']:
            return
        
        if self.silent:
            return
        if level == 'verbose' and not self.verbose:
            return
        if level == 'error':
            _tqdm_write(f"{Fore.RED}[!] ERROR: {message}{Style.RESET_ALL}", file=sys.stderr)
        elif level == 'warning':
            _tqdm_write(f"{Fore.YELLOW}[-] WARNING: {message}{Style.RESET_ALL}")
        elif level == 'info':
            _tqdm_write(f"{Fore.GREEN}[+] {message}{Style.RESET_ALL}")
        elif level == 'verbose':
            _tqdm_write(f"{Fore.BLUE}[DEBUG] {message}{Style.RESET_ALL}")
        else:
            _tqdm_write(message)

    def add_vuln_find3r(self, target_url, plugin_slug, plugin_version, vuln_info): #vuln find on target site

        if target_url not in self.vulnerable_findings:
            self.vulnerable_findings[target_url] = []
        self.vulnerable_findings[target_url].append({
            'plugin_slug': plugin_slug,
            'plugin_version': plugin_version,
            'vulnerability': vuln_info
        })

    def trees(self, full_results): #Tree Structure

        has_output = False
        report_tree = Tree(
            Text(f"Vulnerable Targets", style="bold cyan"),
            guide_style="red",
        )
        
        for target_url, result in full_results.items():
            is_vulnerable = result.get('vulnerable_plugins')
            has_users = result.get('users')
            
            # Skip targets that's may be non wordpress
            if result.get('error') == 'Could not confirm WordPress installation':
                continue
            
            if is_vulnerable or has_users:
                has_output = True
                
                target_node = report_tree.add(Text(f"Target: ", style="white") + Text(target_url, style="cyan"))
                
                if result.get('error'):
                    target_node.add(Text(f"Status: ", style="white") + Text(result.get('status', 'N/A'), style="yellow"))
                    target_node.add(Text(f"Error: ", style="white") + Text(result.get('error', 'N/A'), style="red"))
                elif is_vulnerable:
                    
                    #vulnerable plugins show group wise
                    grouped_plugins = defaultdict(list)
                    for finding in result['vulnerable_plugins']:
                        grouped_plugins[finding['plugin_slug']].append(finding)

                    plugin_node_group = target_node.add(Text("Vulnerable Plugins", style="bold yellow"))
                    for plugin_slug, findings in grouped_plugins.items():
                        # Get a single version
                        plugin_version = findings[0]['plugin_version']
                        
                        plugin_node_text = Text.from_markup(f"Plugin: {plugin_slug} (Version: [red]{plugin_version}[/red])")
                        plugin_node = plugin_node_group.add(plugin_node_text)
                        
                        for finding in findings:
                            vuln_info = finding['vulnerability']
                            vuln_id = vuln_info.get('id', 'N/A')
                            vuln_type = vuln_info.get('type', 'N/A')
                            vuln_severity = vuln_info.get('severity', 'N/A').lower()
                            vuln_desc = vuln_info.get('description', 'No description provided.').split('\n')[0]
                            affected_versions = vuln_info.get('affected_versions', {})
                            affected_range = ""
                            
                            if affected_versions.get('less_than_or_equal'):
                                affected_range += f"<= {affected_versions['less_than_or_equal']}"
                            if affected_versions.get('greater_than_or_equal'):
                                if affected_range:
                                    affected_range = f">= {affected_versions['greater_than_or_equal']} and {affected_range}"
                                else:
                                    affected_range = f">= {affected_versions['greater_than_or_equal']}"
                            
                            finding_node = plugin_node.add(Text(f"ID: ", style="white") + Text(vuln_id, style="white"))
                            finding_node.add(Text(f"Severity: ", style="white") + Text(vuln_severity.upper(), style=self.severity_colors.get(vuln_severity, 'white')))
                            finding_node.add(Text(f"Type: ", style="white") + Text(vuln_type, style="light_green"))
                            finding_node.add(Text(f"Affected Versions: ", style="white") + Text(affected_range if affected_range else 'N/A', style="red"))
                            finding_node.add(Text(f"Description: ", style="white") + Text(vuln_desc, style="yellow"))

                if has_users:
                    user_node = target_node.add(Text("Found Users", style="bold magenta"))
                    for user in result['users']:
                        user_node.add(Text(f" - ", style="white") + Text(user, style="light_blue"))
        
        if not has_output:
            print("No vulnerabilities or users found across scanned targets.")
            return

        panel = Panel(report_tree, title="[bold red]OUTPUT[/bold red]", border_style="bold red")
        self.console.print(panel)


    def jsonform(self, filename, results): #json format

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4)
        except Exception as e:
            self.log(f"Error saving JSON report to {filename}: {e}", level='error')
    
    def csvform(self, filename, results): #csv format (save with full info like cve, version, description, severity)

        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                header = ['Target URL', 'Status', 'Error', 'Plugin Slug', 'Plugin Version',
                          'Vulnerability ID', 'Vulnerability Type', 'Severity',
                          'Affected Versions (LTE)', 'Affected Versions (GTE)', 'Description', 'Users Found']
                writer.writerow(header)
                for target_url, result in results.items():
                    users_found = ", ".join(result.get('users', [])) if result.get('users') else "N/A"
                    if result.get('vulnerable_plugins'):
                        for vp in result['vulnerable_plugins']:
                            vuln_info = vp['vulnerability']
                            affected_versions = vuln_info.get('affected_versions', {})
                            row = [
                                target_url,
                                result.get('status', 'N/A'),
                                result.get('error', 'N/A'),
                                vp.get('plugin_slug', 'N/A'),
                                vp.get('plugin_version', 'N/A'),
                                vuln_info.get('id', 'N/A'),
                                vuln_info.get('type', 'N/A'),
                                vuln_info.get('severity', 'N/A'),
                                affected_versions.get('less_than_or_equal', 'N/A'),
                                affected_versions.get('greater_than_or_equal', 'N/A'),
                                vuln_info.get('description', 'N/A'),
                                users_found
                            ]
                            writer.writerow(row)
                    elif users_found != 'N/A':
                        row = [
                            target_url,
                            result.get('status', 'N/A'),
                            result.get('error', 'N/A'),
                            'N/A',
                            'N/A',
                            'N/A',
                            'N/A',
                            'N/A',
                            'N/A',
                            'N/A',
                            'N/A',
                            users_found
                        ]
                        writer.writerow(row)
        except Exception as e:
            self.log(f"Error saving CSV info {filename}: {e}", level='error')

    def vulnxsites(self, filename, results):

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for target_url, result in results.items():
                    if result.get('vulnerable_plugins'):
                        f.write(f"{target_url}\n")
        except Exception as e:
            self.log(f"Error saving vulnerable sites list to {filename}: {e}", level='error')
            
    def savebypluginname(self): #Save Vulnerable SiteS in Vulnerable plugins name txt File

        if not self.vulnerable_findings:
            return
        
        plugins_to_sites = {}
        for target_url, findings in self.vulnerable_findings.items():
            for finding in findings:
                plugin_slug = finding['plugin_slug']

                if plugin_slug not in plugins_to_sites:
                    plugins_to_sites[plugin_slug] = set()
                plugins_to_sites[plugin_slug].add(target_url)

        report_dir = "vulnerable_sites"
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        for plugin_slug, urls_set in plugins_to_sites.items():
            filename = os.path.join(report_dir, f"{plugin_slug}.txt")
            try:
                with open(filename, 'w', encoding='utf-8') as f:

                    for url in sorted(list(urls_set)):
                        f.write(f"{url}\n")
            except Exception as e:
                self.log(f"Error saving report for {plugin_slug}: {e}", level='error')
