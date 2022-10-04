import requests
import os
import json

crux_api_key = os.environ.get("CRUX_API_KEY")
crux_endpoint = f"https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={crux_api_key}"

header = {
    "Content-Type": "application/json"
}

data = {
    "url": "https://fhior.com/"
}

response = requests.post(url=crux_endpoint, headers=header, json=data)
response.raise_for_status()

json = response.json()

print(json["record"]["metrics"]["largest_contentful_paint"]["histogram"][0]["density"])
