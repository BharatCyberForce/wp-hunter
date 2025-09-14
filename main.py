import argparse
import asyncio
import os
import sys
from colorama import init, Fore, Style
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

from wphunter.scanner.core import WPScanner
from wphunter.utils.logger import Logger
from wphunter.utils.fileio import FileIO
from wphunter.utils.versiondetect import VersionManager

class Config:

    def __init__(self, args):
        self.url = args.url
        self.targets_file = args.targets
        self.threads = args.threads
        self.silent = args.silent
        self.verbose = args.verbose
        self.enumerate_users = args.users
        self.output_file = args.output
        self.timeout = args.timeout
        self.retries = args.retries
        self.specific_plugin_slug = args.plugin
        self.specific_cve_id = args.cve
        self.save_by_plugin = args.save_by_plugin

async def main():

    init(autoreset=True)
    console = Console()

    banner_text = Text("Mass WordPress Vulnerability Scanner bY Indian Cyber Force", style="bold cyan")
    banner_panel = Panel(
        banner_text,
        title="[bold red]WPHunter[/bold red]",
        title_align="center",
        border_style="bold red",
        padding=(1, 2)
    )
    console.print(banner_panel)

    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}A Mass Wordpress Vulnerability Scanner{Style.RESET_ALL}",
        formatter_class=argparse.RawTextHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--url",
        help="Scan a single target Wordpress url (https://target.pk)"
    )
    group.add_argument(
        "--targets",
        help="Contain Targets in file for Mass scan"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=50,
        help="Number of threads"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="No output show on terminal"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging, including informational and debugging messages."
    )
    parser.add_argument(
        "--users",
        action="store_true",
        help=" Enumerate WordPress users ."
    )
    parser.add_argument(
        "--output",
        help="File path to save the scan report. \n\n"
             "The output format and content depends on the file extension:\n"
             " - .txt: Saves only vulnerable site URLs (no other details).\n"
             " - .csv: Saves vulnerable sites with their details.\n"
             " - .json: Saves full scan data for all sites.\n"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="request timeout in seconds."
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Number of retries for failed HTTP requests."
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Check for and provide instructions to update WPHunter"
    )
    parser.add_argument(
        "--plugin",
        help="Scan For a specific Plugin."
    )
    parser.add_argument(
        "--cve",
        help="Scan for a specific CVE ID."
    )
    parser.add_argument(
        "--save-by-plugin",
        action="store_true",
        help="Save separate text File For Each vulnerable plugin Found."
    )
    args = parser.parse_args()
    logger = Logger(verbose=args.verbose, silent=args.silent)

    # check version
    if await VersionManager.update_checker(logger=logger):
        VersionManager.updatewarn(logger)
        sys.exit(0)
    
    if args.update:
        sys.exit(0)

    config = Config(args)

    targets = []
    if config.url:
        targets.append(config.url)
    elif config.targets_file:
        try:
            targets = FileIO.readinput(config.targets_file)
            if not targets:
                logger.log(f"No Targets Found in '{config.targets_file}'", level='error')
                sys.exit(1)
        except FileNotFoundError:
            logger.log(f"The Target File '{config.targets_file}' Was Not Found.", level='error')
            sys.exit(1)
        except IOError as e:
            logger.log(f"Error Reading target file '{config.targets_file}': {e}", level='error')
            sys.exit(1)

    scanner = WPScanner(config, logger)
    full_results = await scanner.start_scan(targets)

    logger.trees()

    if config.output_file:
        file_extension = os.path.splitext(config.output_file)[1].lower()
        
        vulnerable_report_data = {
            target_url: result for target_url, result in full_results.items()
            if result.get('vulnerable_plugins')
        }
        
        if file_extension == '.txt':
            if vulnerable_report_data:
                logger.vulnxsites(config.output_file, vulnerable_report_data)
        elif file_extension == '.csv':
            if vulnerable_report_data:
                logger.csvform(config.output_file, vulnerable_report_data)
        elif file_extension == '.json':
            logger.jsonform(config.output_file, full_results)
        else:
            logger.log(f"Unsupported output extension '{file_extension}'. use .txt, .csv, or .json.", level='error')

    if config.save_by_plugin:
        logger.savebypluginname()

if __name__ == "__main__":
    asyncio.run(main())

