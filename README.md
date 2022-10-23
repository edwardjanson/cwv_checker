# Core Web Vitals Checker

### Video Demo:  https://vimeo.com/763116652

### Website:  https://core-web-vitals-checker.herokuapp.com/

### Description:

#### Introduction

With Core Web Vitals (CWV) becoming an increasing ranking factor in Google’s search engine algorithm, it is important to stay on top of the performance of all pages on a website.

Google’s PageSpeed Insights report contains CWV metric stats, but requires individual checks to review multiple pages. Search Console provides an overview of CWV issues on a website per page, and this project aims to provide an alternative outwith Search Console.

Google provides CWV metrics via the CrUX API (https://developer.chrome.com/docs/crux/api/) and allows to get data at origin (homepage) and page level. This project uses the CrUX API and is currently deployed on Heroku.

The process that this tool follows is as per the below:

- A user inputs a website to investigate with the option to include and/or exclude specific URLs.
- Website URLs are collected using internal links.
- The CrUX API fetches CWV metrics for the collected URLs.
- The metrics are displayed in a table at page level with a score of ‘good’, ‘needs improvement’ or ‘poor’.

#### main.py
This file runs the Flask App and contains the setup for the individual website pages. 

- The ‘cached_session’ function determines if a website was checked, which is used to display the correct navigation elements.
- The homepage contains the form for the website to be reviewed. It requires a website URL and provides an option to include and/or exclude specific pages via ‘contains’ or ‘matches regex’ fields.
- The about page contains top level information about CWV.
- The ‘new_crawl’ function clears all data and cache to allow for a new website check.
- The stats page contains the table with all CWV metric data at page level. DataTables was used to provide search and filter functionalities.
- The ‘loading’ function informs the user that the request is loading.

#### helpers.py
This file contains the functions required for the collection of website URLs and data, form filters and data reset for any other website checks.

- The ‘crawl_required’ function ensures that the stats page can only be viewed when a website has initially been fetched.
- The ‘crawl_urls’ function logic is outlined below:
  - Fetch the HTML of a given page
  - Collects all internal links that are relative URLs or that match the website domain. 
  - Reformat the URL if it does not include the website domain and exclude any PDFs and URLs with query parameters.
  - Any collected links that were not already recorded are added to the list of links.
  - Check that the given page returns a 200 OK status code and if so, add it to the list of ‘all_urls’
- The ‘url_filter’ function takes a URL and checks if the URL should be kept depending on the user’s selected filters. The function is used in the ‘crawl_urls’ function to avoid any unnecessary API calls for pages that should not be included in the CWV report.
- The ‘craw_all_urls’ function logic is outlined below:
  - Initially fetch internal links using the user’s website domain input and add them to the ‘all_links’ list.
  - Check the HTML of all pages within the list for potential unrecorded internal links and add them the links.
  - Initiate a Url object (described in the url.py section below) for all pages found in the ‘all_urls’ list. If the number of pages is above 150, the iteration of each page is slowed to remain below the 150 API calls per 60 seconds limit.
  - If another user was to run a CWV check at the same time, it is possible that the API quota is reached, which would result in missing data. The function updates the ‘quota_reached’ variable, which is used to alert the user and to recommend a new check if required.
- The ‘reset_data’ function resets the lists, filters, domain, and cache used in the helpers functions to avoid any data issues with a new check.

#### url.py
This file contains the Url class, which is a blueprint for the URLs and contains specific values (e.g. URL path), and CWV metrics data.

When initialised, a URL object contains values for:
- The full URL.
- The hostname using the ‘get_hostname’ function.
- The URL path using the ‘get_path’ function.
- CWV data for the First Content Paint (FCP), Largest Content Paint (LCP), First Input Delay (FID), and Cumulative Layout Shift (CLS) metrics using the crux_data function.

The ‘crux_data’ function fetches the CWV metrics data for each URL using the CrUX API. The values for FCP, LCP, FID, and CLS are subsequently updated if data could be retrieved. The values are structured in a list and contain the score of either ‘good’, ‘needs improvement’, or ‘poor’ using the ‘score’ function (based on CWV’s scoring system) and the data in seconds or the shift metric in the case of CLS. This implementation was used for easier access to the data in Jinja within the stats table.

#### config.py
This file includes:
- The required functionality for Heroku to run.
- The secret key for the CrUX API.
- The lists, and domain and API quota reached variables used within the files.

#### templates
This folder contains all the HTML files used in the Flask app. The website is built on the Bootstrap framework. 

Refer to the main.py section for more information about the individual pages.

#### static
The static folder contains:
- The images used on the website.
- The CSS file is used to style and layout the web pages.
- The ‘script_header’ file for any scripts that need to run in the header i.e., the DataTable script for the stats table.
- The ‘script_footer’ file for the remaining scripts, which include scripts that:
  - Shows or hides the filter options in the form using the radio buttons.
  - Display the loading message when a form is submitted.
  - Changes the domain name label to red if there are any issues with the provided website.

#### Other
- Procfile listing the app’s web server.
- requirements.txt listing all the dependencies for the app to run.

### Limitations
- As mentioned in the helpers.py section, there can be issues with reaching the API quota if two ore more users are running a check at one time. This would lead to the stats table displaying data labeled as ‘API quota reached’ and a flash message being displayed on the stats page warning the user that not all data could be fetched.

### What’s next?
- Initially the loading function provided a progress bar with percentages for the fetching of URLs and CrUX data. This worked locally but not on Heroku due to the web server limitations on the free tier. The functionality may be added in the future.
