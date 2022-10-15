from flask import render_template
from main import app

import config as c
from rq import Queue
from worker import conn


@app.route("/progress")
def progress():
    """Record the progress of crawl load after the index page form submission"""
    # Keep track of progress of URLs fetch requests or if done, track progress of CrUX data collection
    try:
        if c.crawled_links <= c.link_count:
            c.steps = "Step 1 of 2: Fetching URLs"
            c.progress = round((c.crawled_links / c.link_count) * 100)
            if c.progress >= 100:
                c.progress = 100
        else:
            c.steps = "Step 2 of 2: Fetching CrUX data"
            c.progress = round((c.crawled_urls / c.url_count) * 100)
            if c.progress >= 100:
                c.progress = 100
    except ZeroDivisionError:
        pass
    
    return render_template("progress.html", progress=c.progress, steps=c.steps)


q = Queue(connection=conn)
q.enqueue(progress)


# if __name__ == "__main__":
#     app.run()