import os
import re
import requests


class Url():

    def __init__(self, url):
        self.full = url
        self.hostname = self.get_hostname()
        self.path = self.get_path()
        self.p75_fcp = ["-", "No data"]
        self.p75_lcp = ["-", "No data"]
        self.p75_fid = ["-", "No data"]
        self.p75_cls = ["-", "No data"]
        self.crux_data()
    

    def __repr__(self):
        return self.path


    def get_hostname(self):
        """Get the website hostname of a URL"""
        re_sub = re.search(r'(?:http|https)\:\/\/(.*?)[^\/]+.*', self.full)
        return re_sub.group(1)


    def get_path(self):
        """Get the page path of a URL"""
        re_sub = re.match(r'(?:http|https)\:\/\/[^\/]+(.*)', self.full)
        return re_sub.group(1)


    def crux_data(self):
        """Get Core Web Vitals data for a URL using the CrUX API"""
        crux_api_key = os.environ.get("CRUX_API_KEY")
        crux_endpoint = f"https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={crux_api_key}"

        header = {
            "Content-Type": "application/json"
        }

        data = {
            "url": self.full
        }

        # Get api data from CrUX and return if the API quota is reached or if no data is available
        try:
            response = requests.post(url=crux_endpoint, headers=header, json=data)
            response.raise_for_status()
            json = response.json()["record"]["metrics"]
        except (requests.exceptions.HTTPError, KeyError) as error:
            status_code = error.response.status_code
            if status_code == 429:
                self.p75_fcp = ["API quota reached", "Please wait 10 minutes and run a new check"]
                self.p75_lcp = ["API quota reached", "Please wait 10 minutes and run a new check"]
                self.p75_fid = ["API quota reached", "Please wait 10 minutes and run a new check"]
                self.p75_cls = ["API quota reached", "Please wait 10 minutes and run a new check"]
            return

        # Set data values for FCP, LCP, FID, and CLS
        try:
            p75_fcp = json["first_contentful_paint"]["percentiles"]["p75"]
            self.p75_fcp = [self.score(p75_fcp, 3000, 1800), self.to_seconds(p75_fcp)]
        except (KeyError):
            pass
            
        try:
            p75_lcp = json["largest_contentful_paint"]["percentiles"]["p75"]
            self.p75_lcp = [self.score(p75_lcp, 4000, 2500), self.to_seconds(p75_lcp)]
        except (KeyError):
            pass

        try:
            p75_fid = json["first_input_delay"]["percentiles"]["p75"]
            self.p75_fid = [self.score(p75_fid, 300, 100), self.to_seconds(p75_fid)]
        except (KeyError):
            pass

        try:
            p75_cls = json["cumulative_layout_shift"]["percentiles"]["p75"]
            self.p75_cls = [self.score(p75_cls, 0.25, 0.10), p75_cls]
        except (KeyError):
            pass


    def to_seconds(self, milliseconds):
        """Convert milliseconds to seconds"""
        return f"{milliseconds / 1000.0:.2f}s"
    

    def score(self, p75, poor, good):
        """Provide Core Web Vitals score based on benchmark data"""
        if float(p75) < good:
            return "Good"
        elif float(p75) >= poor:
            return "Poor"
        else:
            return "Needs improvement"