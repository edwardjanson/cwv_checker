import re
import requests
import os
import json


class Url():

    def __init__(self, url):
        self.full = url
        self.hostname = self.get_hostname()
        self.path = self.get_path()
        self.p75_lcp = 0
        self.crux_data()
    
    def __repr__(self):
        return self.path

    def get_hostname(self):
        re_sub = re.search(r'(?:http|https)\:\/\/(.*?)[^\/]+.*', self.full)
        return re_sub.group(1)

    def get_path(self):
        re_sub = re.match(r'(?:http|https)\:\/\/[^\/]+(.*)', self.full)
        return re_sub.group(1)

    def crux_data(self):
        crux_api_key = os.environ.get("CRUX_API_KEY")
        crux_endpoint = f"https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={crux_api_key}"

        header = {
            "Content-Type": "application/json"
        }

        data = {
            "url": self.full
        }

        try:
            response = requests.post(url=crux_endpoint, headers=header, json=data)
            json = response.json()["record"]["metrics"]
            self.p75_lcp = json["largest_contentful_paint"]["percentiles"]["p75"]
        except (requests.exceptions.HTTPError, KeyError) as errors:
            self.p75_lcp = "No data"