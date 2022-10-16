import os
import requests
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import config as c

from helpers import crawl_required, reset_data, crawl_all_urls

quota_reached = False
domain = None
filters = []
all_links = []
all_urls = []
urls_data = []

# Configure application
app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Make sure API key is set
if not os.environ.get("CRUX_API_KEY"):
    raise RuntimeError("CRUX_API_KEY not set")

# Configure session to use filesystem (instead of signed cookies)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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

        global domain

        # Reset date before new crawl
        reset_data()

        # Handle any errors related to invalid domains run by user
        try:
            domain = request.form.get("domain")
            domain_check = requests.get(domain)
            domain_check.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
            return redirect("/?error=domain")

        # If filter is selected, add provided filters in dictionaries 
        filter = request.form["radio-filter"]

        if filter == "filter":
            filters.append({request.form.get("include-select"): request.form.get("include-value")})
            filters.append({request.form.get("exclude-select"): request.form.get("exclude-value")})
    
        crawl_all_urls()

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
    reset_data()

    # Redirect user to crawl form
    return redirect("/")


@app.route("/stats")
@crawl_required
def stats():
    """Page Speed Stats"""
    if not urls_data:
        return redirect("/new-crawl")

    return render_template("stats.html", urls=urls_data)


@app.route("/loading")
def loading():
    """Record the progress of the URL crawl after the index page form submission"""

    return render_template("loading.html")


if __name__ == "__main__":
    app.run()