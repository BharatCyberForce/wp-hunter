import asyncio
from urllib.parse import urljoin
import json
from tqdm.asyncio import tqdm as async_tqdm
from wphunter.scanner.httpcl import HTTPClient
from wphunter.scanner.parser import WordPressParser
from wphunter.scanner.db import VulnerabilityDB
from wphunter.utils.logger import Logger

class WPScanner:
    def __init__(self, config, logger: Logger):
        self.config = config
        self.logger = logger
        self.http_client = HTTPClient(
            timeout=config.timeout,
            follow_redirects=True,
            max_retries=config.retries,
            logger=self.logger
        )
        self.parser = WordPressParser(logger=self.logger)
        self.vuln_db = VulnerabilityDB()
        self.full_scan_results = {}
        self.vuln_plugin_slugs = self.vuln_db.pluginsXslugs()

    async def _scan_single_target(self, target_url):
        target_url = target_url.rstrip('/')
        scan_result = {
            'target_url': target_url,
            'status': 'Failed',
            'error': None,
            'plugins': [],
            'vulnerable_plugins': [],
            'users': []
        }
        try:
            wp_indicator_found = False
            response = await self.http_client.get(target_url)
            if response and response.status_code == 200:
                if 'wp-content' in response.text or 'wp-includes' in response.text or '/wp-json/' in response.text:
                    wp_indicator_found = True
                else:
                    wp_login_url = urljoin(target_url, '/wp-login.php')
                    wp_login_response = await self.http_client.get(wp_login_url)
                    if wp_login_response and wp_login_response.status_code == 200 and 'WordPress' in wp_login_response.text:
                        wp_indicator_found = True
            if not wp_indicator_found:
                scan_result['status'] = 'Not WordPress or inaccessible'
                scan_result['error'] = 'Could not confirm WordPress installation'
                self.full_scan_results[target_url] = scan_result
                return
            scan_result['status'] = 'Scanned'
            plugins_found_map = {}
            if response and response.status_code == 200:
                html_plugins = self.parser.plugin_p4rs3(response.text)
                for p in html_plugins:
                    if p['plugin_slug'] not in plugins_found_map or \
                       (plugins_found_map[p['plugin_slug']]['plugin_version'] == 'unknown' and p['plugin_slug'] != 'unknown'):
                        plugins_found_map[p['plugin_slug']] = p
            for known_slug in self.vuln_plugin_slugs:
                if self.config.specific_plugin_slug and known_slug != self.config.specific_plugin_slug:
                    continue
                if known_slug not in plugins_found_map or plugins_found_map[known_slug]['plugin_version'] == 'unknown':
                    readme_url = urljoin(target_url, f'/wp-content/plugins/{known_slug}/readme.txt')
                    readme_response = await self.http_client.get(readme_url)
                    if readme_response and readme_response.status_code == 200:
                        plugin_info = self.parser.versionparsing(readme_response.text)
                        if plugin_info and plugin_info['plugin_slug'] == known_slug and plugin_info['plugin_version'] != 'unknown':
                            plugins_found_map[known_slug] = plugin_info
                            continue
            scan_result['plugins'] = list(plugins_found_map.values())
            for plugin in scan_result['plugins']:
                if self.config.specific_plugin_slug and plugin['plugin_slug'] != self.config.specific_plugin_slug:
                    continue 
                detected_vulns = self.vuln_db.is_vulnerable(
                    plugin['plugin_slug'],
                    plugin['plugin_version'],
                    specific_cve_id=self.config.specific_cve_id
                )
                if detected_vulns:
                    for vuln_info in detected_vulns:
                        scan_result['vulnerable_plugins'].append({
                            'plugin_slug': plugin['plugin_slug'],
                            'plugin_version': plugin['plugin_version'],
                            'vulnerability': vuln_info
                        })
                        self.logger.add_vuln_find3r(target_url, plugin['plugin_slug'], plugin['plugin_version'], vuln_info)
            """if self.config.enumerate_users:
                users_api_url = urljoin(target_url, '/wp-json/wp/v2/users')
                users_response = await self.http_client.get(users_api_url)
                if users_response and users_response.status_code == 200:
                    try:
                        users_data = users_response.json()
                        users = self.parser.wpus3r_parse(users_data)
                        if users:
                            scan_result['users'] = users
                    except json.JSONDecodeError as e:
                        try:
                            users_data = json.loads(users_response.content.decode('utf-8-sig'))
                            users = self.parser.wpus3r_parse(users_data)
                            if users:
                                scan_result['users'] = users
                        except Exception as inner_e:
                            pass
                    except Exception as e:
                        pass
        except Exception as e:
            scan_result['error'] = str(e)
        finally:
            self.full_scan_results[target_url] = scan_result"""

    async def start_scan(self, targets):
        semaphore = asyncio.Semaphore(self.config.threads)
        async def bounded_scan(target):
            async with semaphore:
                await self._scan_single_target(target)
        tasks = [bounded_scan(target_url) for target_url in targets]
        await async_tqdm.gather(*tasks, desc="Scanning Targets", unit="target")
        await self.http_client.close()
        return self.full_scan_results

    def get_vulnerable_sites_data(self):
        return self.logger.vulnerable_findings
