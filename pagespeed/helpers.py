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

    # Get all URLs from the same domain being crawled
    links_found = page_soup.find_all("a", href=re.compile(f'{url}.*|^\/.*'))
    
    # Append new URLs to the URL list
    for link in links_found:
        # Remove any links that do not match user selected filters
        if len(filters) != 0:
            include = filters[0]
            exclude = filters[1]
            if include["contains"] and re.match(f'.*{include["contains"]}.*', link) != 0:
                link.extract()
            elif include["matches-regex"] and re.match(include["matches-regex"], link) != 0:
                link.extract()
            if exclude["contains"] and re.match(f'.*{include["contains"]}.*', link) > 0:
                link.extract()
            elif exclude["matches-regex"] and re.match(include["matches-regex"], link) > 0:
                link.extract()

        link_check = link["href"]

        # Ignore any URLs with a query string or .pdf
        if "?" in link_check or ".pdf" in link_check:
            continue

        # Update URL to contain domain
        if link_check.startswith("/"):
            link_check = domain.rstrip("/") + link_check

        # Add the URL to the list if not already recorded
        if not link_check in links:
            links.append(link_check)

    # Add URL to URL list if 200 OK and not already recorded
    if not page.url in urls:
        urls.append(page.url)