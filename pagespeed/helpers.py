import os
import requests
import urllib.parse
from bs4 import BeautifulSoup as bs
import re

from flask import redirect, render_template, request, session
from functools import wraps
from url import Url


def crawl_required(f):
    """Decorate routes to require initial crawl of website."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("crawled") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def crawl_urls(domain, url, links, urls, filters):
    """Get all the urls from the same hostname and appends them to the URL list if not already present."""
    # Get page data
    page = requests.get(url)
    page.raise_for_status()
    page_soup = bs(page.content, "lxml")

    # Get all internal links from the user selected domain
    links_found = page_soup.find_all("a", href=re.compile(f'{url}.*|^\/.*'))

    links_kept = []
    
    # If filter is selected, only include links that match the filters
    if len(filters) != 0:
        for link in links_found:
            if url_filter(filters, link):
                links_kept.append(link)
    else:
        links_kept = links_found

    # Append new links to the link list
    for link in links_kept:
        link_href = link["href"]

        # Ignore any links with a query string or .pdf
        if "?" in link_href or ".pdf" in link_href:
            continue

        # Update link to contain domain
        if link_href.startswith("/"):
            link_href = domain.rstrip("/") + link_href

        # Add the link to the list if not already recorded
        if not link_href in links:
            links.append(link_href)

    # Add URL to URL list if 200 OK and not already recorded
    if not page.url in urls:
        if len(filters) != 0:
            if url_filter(filters, page.url):
                urls.append(page.url)
        else:
            urls.append(page.url)
            

def url_filter(filters, url):
    """Check if a URL matches the include and exclusion filters and return the appropriate boolean value."""
    include = filters[0]
    exclude = filters[1]
    keep_url = True

    if isinstance(url, str):
        url_check = url
    else:
        url_check = url["href"]

    # Check if the URL matches the contain filter
    if "contains" in include: 
        if not bool(re.match(f'.*{include["contains"]}.*', url_check)):
            keep_url = False
    elif "matches-regex" in include:
        if not bool(re.match(include["matches-regex"], url_check)):
            keep_url = False

    # Remove any links from links_kept that match the contain filter
    if "contains" in exclude:
        if bool(re.match(f'.*{exclude["contains"]}.*', url_check)):
            keep_url = False
    elif "matches-regex" in exclude:
        if bool(re.match(exclude["matches-regex"], url_check)):
            keep_url = False
    
    return keep_url