import json
import os
import sys
from packaging.version import parse as parse_version

class VulnerabilityDB:

    def __init__(self, db_path='wphunter/data/pluginsdb.json'):
        self.db_path = db_path
        self.vulnerabilities_by_slug = self._load_db()
        self.all_known_plugin_slugs = set(self.vulnerabilities_by_slug.keys())

    def _load_db(self):

        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        if not os.path.exists(self.db_path):
            print(f"Error: Vulnerability database not found at {self.db_path}. Creating an empty one.", file=sys.stderr)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return {}
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {entry['plugin_slug']: entry['vulnerabilities'] for entry in data}
        except json.JSONDecodeError as e:
            print(f"Error decoding vulnerability database JSON: {e}", file=sys.stderr)
            return {}
        except Exception as e:
            print(f"An unexpected error occurred loading the vulnerability database: {e}", file=sys.stderr)
            return {}

    def get_plugin_vulnerabilities(self, plugin_slug):
        return self.vulnerabilities_by_slug.get(plugin_slug, [])

    def get_all_plugin_slugs(self):
        return self.all_known_plugin_slugs

    def is_vulnerable(self, plugin_slug, current_version_str, specific_cve_id=None):

        if plugin_slug not in self.vulnerabilities_by_slug:
            return []

        try:
            current_version = parse_version(current_version_str)
        except Exception:
            return []

        plugin_vulns = self.vulnerabilities_by_slug[plugin_slug]
        found_vulnerabilities = []

        for vuln_detail in plugin_vulns:
            if specific_cve_id and vuln_detail.get('id') != specific_cve_id:
                continue

            is_affected = True
            affected_versions = vuln_detail.get('affected_versions', {})

            if 'less_than_or_equal' in affected_versions:
                try:
                    lte_version = parse_version(affected_versions['less_than_or_equal'])
                    if current_version > lte_version:
                        is_affected = False
                except Exception:
                    is_affected = False
            
            if is_affected and 'greater_than_or_equal' in affected_versions:
                try:
                    gte_version = parse_version(affected_versions['greater_than_or_equal'])
                    if current_version < gte_version:
                        is_affected = False
                except Exception:
                    is_affected = False

            if is_affected:
                found_vulnerabilities.append(vuln_detail.copy())

        return found_vulnerabilities
