import re
from urllib.parse import urlparse

class WordPressParser:

    def __init__(self, logger=None):
        self.logger = logger

    def plugin_p4rs3(self, html_content): #get version from readme file
        plugins = []
        plugin_pattern = re.compile(r'/wp-content/plugins/([^/]+)/.*?\.((?:css|js)(?:\?ver=([\d.]+))?|readme\.txt)')
        found_slugs = set()
        for match in plugin_pattern.finditer(html_content):
            plugin_slug = match.group(1)
            version = match.group(3) if match.group(3) else 'unknown'
            if plugin_slug not in found_slugs:
                plugins.append({
                    'plugin_slug': plugin_slug,
                    'plugin_version': version
                })
                found_slugs.add(plugin_slug)
            else:
                for p in plugins:
                    if p['plugin_slug'] == plugin_slug and p['plugin_version'] == 'unknown' and version != 'unknown':
                        p['plugin_version'] = version
                        break
        return plugins

    def versionparsing(self, readme_content): #versions parse
        plugin_name = "unknown"
        plugin_version = "unknown"
        plugin_slug = "unknown_slug"
        name_match = re.search(r'===\s*(.*?)\s*===', readme_content, re.IGNORECASE)
        if name_match:
            plugin_name = name_match.group(1).strip()
            plugin_slug = re.sub(r'[^a-z0-9-]', '', plugin_name.lower().replace(' ', '-'))
        version_match = re.search(r'Stable tag:\s*([\d.]+)', readme_content, re.IGNORECASE)
        if version_match:
            plugin_version = version_match.group(1).strip()
        else:
            version_match = re.search(r'Version:\s*([\d.]+)', readme_content, re.IGNORECASE)
            if version_match:
                plugin_version = version_match.group(1).strip()
        if plugin_name == "unknown" and plugin_version == "unknown":
            return None
        return {
            'plugin_slug': plugin_slug,
            'plugin_version': plugin_version
        }

    def wpus3r_parse(self, json_data):
        users = []
        if isinstance(json_data, list):
            for user_obj in json_data:
                if isinstance(user_obj, dict) and 'slug' in user_obj:
                    users.append(user_obj['slug'])
        return users
