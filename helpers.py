import requests
from bs4 import BeautifulSoup as bs
import re
from flask import redirect, session
from functools import wraps
import time
from url import Url

import config as c


def crawl_required(f):
    """Decorate routes to require initial crawl of website"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("crawled") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def crawl_urls(domain, url, links, urls, filters):
    """Get all the urls from the same hostname and appends them to the URL list if not already present"""
    # Get page data
    try:
        page = requests.get(url)
        page.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        return
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
        if "?" in link_href or ".pdf" in link_href or "#" in link_href:
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
    """Check if a URL matches the include and exclusion filters and return the appropriate boolean value"""
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


def crawl_all_urls():
    # Crawl the main page given for URLs of same domain
    crawl_urls(c.domain, c.domain, c.all_links, c.all_urls, c.filters)

    # Crawl all URLs in the URL list to check for any new URLs from the same domain
    for link in c.all_links:
        crawl_urls(c.domain, link, c.all_links, c.all_urls, c.filters)

    # Create URL objects to record CRUX data and append to URL data list
    c.quota_reached = False
    for url in c.all_urls:
        start_time = time.time()
        url_data = Url(url)
        c.urls_data.append(url_data)
        end_time = time.time()
        # Delay the CRUX function if there a more than 150 URLs to avoid API rate limit
        if end_time - start_time < 0.4 and len(c.all_urls) > 150:
            time.sleep(0.4 - (end_time - start_time))

        if url_data.p75_fcp[0] == "API quota reached":
            c.quota_reached = True


def reset_data():
    c.domain = None
    c.filters = []
    c.all_links = []
    c.all_urls = []
    c.urls_data = []