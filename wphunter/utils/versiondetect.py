import httpx
import os
import re
from packaging.version import parse as parse_version
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

class VersionManager:

    actversion = "https://raw.githubusercontent.com/BharatCyberForce/wp-hunter/refs/heads/main/version/version.txt"
    icf_github = "https://github.com/BharatCyberForce/wp-hunter"

    @staticmethod
    async def latestv(): #wphunter latest version
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(VersionManager.actversion, timeout=5)
                response.raise_for_status()
                return response.text.strip()
        except httpx.HTTPStatusError as e:
            print(f"Error fetching latest version: HTTP {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            print(f"Network error, check Internet connection {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while fetching latest version: {e}")
            return None

    @staticmethod
    def currentv(): #wphunter current version
        version_file_path = os.path.join(os.path.dirname(__file__), '..', '__version__.py')
        try:
            with open(version_file_path, 'r', encoding='utf-8') as f:
                version_line = f.readline()
                match = re.search(r'__version__\s*=\s*[\'"]([\d.]+)[\'"]', version_line)
                if match:
                    return match.group(1)
        except FileNotFoundError:
            print(f"Error: Local version file not found at {version_file_path}")
        except Exception as e:
            print(f"Error reading local version: {e}")
        return "25.1.0"

    @staticmethod
    async def update_checker(logger): #check version outdated or latest (version compare part)
        cversionstr = VersionManager.currentv()
        lversionstr = await VersionManager.latestv()
        console = Console()

        if not lversionstr:
            logger.log("Please check your network connection!", level='warning')
            return False

        try:
            currentVersion = parse_version(cversionstr)
            latestVersion = parse_version(lversionstr)

            if currentVersion < latestVersion:
                panelmsg = Text(f"Your WPHunter version {cversionstr} is OUTDATED, Latest: {lversionstr}. Please update the tool.", style="bold red")
                console.print(Panel(panelmsg, title="[bold red]Tool is Outdated[/bold red]", border_style="bold red"))
                return True
            else:
                return False
        except ImportError:
            logger.log("Warning: 'packaging' library not found. Please install it: pip install packaging", level='warning')
            if cversionstr != lversionstr:
                logger.log(f"Current version: {cversionstr}, Latest available: {lversionstr}. Consider manual update.", level='warning')
            return False
        except Exception as e:
            logger.log(f"Error versions: {e}", level='error')
            return False

    @staticmethod
    def updatewarn(logger):

        logger.log("Please Redownload Latest Version", level='info')
        logger.log(f"{VersionManager.icf_github}/archive/refs/heads/main.zip", level='info')
