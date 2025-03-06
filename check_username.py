import json
import requests
from concurrent.futures import ThreadPoolExecutor
import re

class WebsiteChecker:
    def __init__(self, data_file):
        self.data = self.load_data(data_file)

    def load_data(self, data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            raise ValueError("The data file cannot be read due to invalid JSON format")

    def check_username(self, username, site=None):
        results = []
        sites_to_check = self.data if not site else {k: v for k, v in self.data.items() if site.lower() in k.lower()}

        if not sites_to_check:
            raise ValueError("The requested site is not supported")

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(self._check_site, site_name, site_info, username) for site_name, site_info in sites_to_check.items()]
            for future in futures:
                result = future.result()
                if result:
                    results.append(result)

        return results

    def _check_site(self, site_name, site_info, username):
        if 'regexCheck' in site_info and not re.match(site_info['regexCheck'], username):
            return None

        url = site_info['url'].replace("{}", username)
        result = {'name': site_name, 'url': url, 'found': False}

        try:
            response = requests.get(url, timeout=20)
            if site_info['errorType'] == 'status_code':
                if response.status_code == 200:
                    result['found'] = True
            elif site_info['errorType'] == 'message':
                error_messages = site_info['errorMsg']
                if isinstance(error_messages, list):
                    if not any(msg in response.text for msg in error_messages):
                        result['found'] = True
                elif error_messages not in response.text:
                    result['found'] = True
        except requests.RequestException as e:
            print(f"Error checking {site_name}: {e}")

        return result

# if __name__ == "__main__":
    # checker = WebsiteChecker('./data.json')
    # username_to_check = "sarvadnyachavhan"
    # results = checker.check_username(username_to_check)
    # for result in results:
    #     print(f"Site: {result['name']}, URL: {result['url']}, Found: {result['found']}") 