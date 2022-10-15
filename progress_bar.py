from main import crawled_links, link_count, app, crawled_urls, url_count
from flask import render_template


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