import os
import requests
from flask import Flask, flash, redirect, render_template, request, session
from flask_session.__init__ import Session
import time

from helpers import crawl_required, crawl_urls
from url import Url

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Make sure API key is set
if not os.environ.get("CRUX_API_KEY"):
    raise RuntimeError("CRUX_API_KEY not set")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# List of all the hostname URLs to include
all_links = []
all_urls = []
urls_data = []

# Set counters for progress bars
link_count = 0
crawled_links = 0
url_count = 0
crawled_urls = 0


@app.after_request
def after_request(response):
    """Ensure responses are not cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    """Get user to crawl a website"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Set global variables for progress bars
        global link_count
        global crawled_links
        global url_count
        global crawled_urls

        # Reset counters for progress bars
        link_count = 0
        crawled_links = 0
        url_count = 0
        crawled_urls = 0

        # Handle any errors related to invalid domains run by user
        try:
            domain = request.form.get("domain")
            domain_check = requests.get(domain)
            domain_check.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
            return redirect("/?error=domain")

        # If filter is selected, add provided filters in dictionaries 
        filter = request.form["radio-filter"]
        filters = []

        if filter == "filter":
            filters.append({request.form.get("include-select"): request.form.get("include-value")})
            filters.append({request.form.get("exclude-select"): request.form.get("exclude-value")})

        # Crawl the main page given for URLs of same domain
        crawl_urls(domain, domain, all_links, all_urls, filters)
        link_count = len(all_links)
        crawled_links += 1

        # Crawl all URLs in the URL list to check for any new URLs from the same domain
        for link in all_links:
            crawl_urls(domain, link, all_links, all_urls, filters)
            link_count = len(all_links)
            crawled_links += 1

        # Create URL objects to record CRUX data and append to URL data list
        quota_reached = False
        url_count = len(all_urls)
        for url in all_urls:
            start_time = time.time()
            url_data = Url(url)
            urls_data.append(url_data)
            end_time = time.time()
            # Delay the CRUX function if there a more than 150 URLs to avoid API rate limit
            if end_time - start_time < 0.4 and len(all_urls) > 150:
                time.sleep(0.4 - (end_time - start_time))
            
            crawled_urls += 1
            if url_data.p75_fcp[0] == "API quota reached":
                quota_reached = True

        # Remember which domain was crawled
        session["crawled"] = domain

        # Redirect user to stats page and notify user in case the API quota was reached
        if quota_reached:
            flash("The API quota was reached and not all URLs' performance data could be fetched. This is due to another user also checking a website. Please wait 10 minutes and run a new check if required.")
        return redirect("/stats")

    elif not session:
        return render_template("index.html")

    else:
        return redirect("/stats")


@app.route("/progress")
def progress():
    """Record the progress of crawl load after the index page form submission"""
    progress = 0
    steps = 0

    # Keep track of progress of URLs fetch requests or if done, track progress of CrUX data collection
    try:
        if crawled_links <= link_count:
            steps = "Step 1 of 2: Fetching URLs"
            progress = round((crawled_links / link_count) * 100)
            if progress >= 100:
                progress = 100
        else:
            steps = "Step 2 of 2: Fetching CrUX data"
            progress = round((crawled_urls / url_count) * 100)
            if progress >= 100:
                progress = 100
    except ZeroDivisionError:
        pass
    
    return render_template("progress.html", progress=progress, steps=steps)


@app.route("/about")
def about():
    """Information about the application"""
    # Redirect user to crawl form
    return render_template("about.html")


@app.route("/new-crawl")
def new_crawl():
    """Remove crawled website"""
    # Forget any crawled website
    session.clear()
    all_links.clear()
    all_urls.clear()
    urls_data.clear()   

    # Redirect user to crawl form
    return redirect("/")


@app.route("/stats")
@crawl_required
def stats():
    """Page Speed Stats"""
    if not urls_data:
        return redirect("/new-crawl")

    return render_template("stats.html", urls=urls_data)


if __name__=='__main__':
    app.run(debug=True, port=4444)