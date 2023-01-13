import os
import requests
from flask import Flask, flash, redirect, render_template, request
from functools import wraps
from flask_caching import Cache
import config as c

from helpers import crawl_all_urls


# Configure application
app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Make sure API key is set
if not os.environ.get("CRUX_API_KEY"):
    raise RuntimeError("CRUX_API_KEY not set")

# Initialise cache for urls data
app.config["CACHE_TYPE"] = "FileSystemCache"
app.config["CACHE_THRESHOLD"] = 1000
app.config["CACHE_DIR"] = "cache"
cache = Cache(app)


# Check if urls are already cached
def crawl_required(f):
    """Decorate routes to require initial crawl of website"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not cache.get("cached_urls"):
            return redirect("/new-crawl")
        return f(*args, **kwargs)
    return decorated_function


# Reset all crawl data
def reset_data():
    c.domain = None
    c.filters = []
    c.all_links = []
    c.all_urls = []
    c.urls_data = []
    cache.clear()


@app.context_processor
def cached_session():
    """Return the cache status in all templates"""
    if cache.get("cached_urls"):
        cache_status = True
    else:
        cache_status = False
    
    return dict(cached=cache_status)


@app.route("/", methods=["GET", "POST"])
def index():
    """Get user to crawl a website"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Reset data before new crawl
        reset_data()

        # Handle any errors related to invalid domains run by user
        try:
            domain = request.form.get("domain")
            if domain.endswith("/"): # type: ignore
                domain = domain[:-1] # type: ignore
            c.domain = domain
            domain_check = requests.get(domain) # type: ignore
            domain_check.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
            return redirect("/?error=domain")

        # If filter is selected, add provided filters in dictionaries 
        filter = request.form["radio-filter"]

        if filter == "filter":
            c.filters.append({request.form.get("include-select"): request.form.get("include-value")})
            c.filters.append({request.form.get("exclude-select"): request.form.get("exclude-value")})
    
        crawl_all_urls()

        # Set cache for URLs data
        cache.set("cached_urls", c.urls_data)

        # Redirect user to stats page and notify user in case the API quota was reached
        if c.quota_reached:
            flash("The API quota was reached and not all URLs' performance data could be fetched. This is due to another user also checking a website. Please wait 10 minutes and run a new check if required.")
        return redirect("/stats")

    elif not cache.get("cached_urls"):
        reset_data()
        return render_template("index.html")

    else:
        return redirect("/stats")


@app.route("/about")
def about():
    """Information about the application"""
    # Redirect user to crawl form
    return render_template("about.html")


@app.route("/new-crawl")
def new_crawl():
    """Remove crawled website"""
    # Forget any crawled website
    reset_data()

    # Redirect user to crawl form
    return redirect("/")


@app.route("/stats")
@crawl_required
def stats():
    """Page Speed Stats"""
    cached_urls = cache.get("cached_urls")

    return render_template("stats.html", urls=cached_urls)


@app.route("/loading")
def loading():
    """Display the loading template after the index page form submission"""

    return render_template("loading.html")

if __name__ == "__main__":
	app.run()