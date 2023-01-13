# Core Web Vitals Checker

### Video Demo:  https://youtu.be/VetSbRSZAFE

### Website:  https://cwv-checker.edwardjanson.dev/

<br>

## Contents 

* [Description](#description)
* [Limitations](#limitations)
* [What’s next](#whats-next)
* [EC2 Deployment](#ec2-deployment)

<br>

## Description

<br>

### **Introduction**
With Core Web Vitals (CWV) becoming an increasing ranking factor in Google’s search engine algorithm, it is important to stay on top of the performance of all pages on a website.

Google’s PageSpeed Insights report contains CWV metric stats, but requires individual checks to review multiple pages. Search Console provides an overview of CWV issues on a website per page, and this project aims to provide an alternative outwith Search Console.

Google provides CWV metrics via the CrUX API (https://developer.chrome.com/docs/crux/api/) and allows to get data at origin (homepage) and page level. This project uses the CrUX API and is currently deployed on an AWS EC2 instance.

The process that this tool follows is as per the below:

- A user inputs a website to investigate with the option to include and/or exclude specific URLs.
- Website URLs are collected using internal links.
- The CrUX API fetches CWV metrics for the collected URLs.
- The metrics are displayed in a table at page level with a score of ‘good’, ‘needs improvement’ or ‘poor’.

<br>

### **main.py**
This file runs the Flask App and contains the setup for the individual website pages. 

- The ‘crawl_required’ function ensures that the stats page can only be viewed when a website has initially been fetched.
- The ‘cached_session’ function determines if a website was checked, which is used to display the correct navigation elements.
- The homepage contains the form for the website to be reviewed. It requires a website URL and provides an option to include and/or exclude specific pages via ‘contains’ or ‘matches regex’ fields.
- The about page contains top level information about CWV.
- The ‘new_crawl’ function clears all data and cache to allow for a new website check.
- The stats page contains the table with all CWV metric data at page level. DataTables was used to provide search and filter functionalities.
- The ‘loading’ function informs the user that the request is loading.

<br>

### **helpers.py**
This file contains the functions required for the collection of website URLs and data, form filters and data reset for any other website checks.

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

<br>

### **url.py**
This file contains the Url class, which is a blueprint for the URLs and contains specific values (e.g. URL path), and CWV metrics data.

When initialised, a URL object contains values for:
- The full URL.
- The hostname using the ‘get_hostname’ function.
- The URL path using the ‘get_path’ function.
- CWV data for the First Content Paint (FCP), Largest Content Paint (LCP), First Input Delay (FID), and Cumulative Layout Shift (CLS) metrics using the crux_data function.

The ‘crux_data’ function fetches the CWV metrics data for each URL using the CrUX API. The values for FCP, LCP, FID, and CLS are subsequently updated if data could be retrieved. The values are structured in a list and contain the score of either ‘good’, ‘needs improvement’, or ‘poor’ using the ‘score’ function (based on CWV’s scoring system) and the data in seconds or the shift metric in the case of CLS. This implementation was used for easier access to the data in Jinja within the stats table.

<br>

### **config.py**
This file includes:
- The required functionality for the app to run.
- The secret key for the CrUX API.
- The lists, and domain and API quota reached variables used within the files.

<br>

### **templates**
This folder contains all the HTML files used in the Flask app. The website is built on the Bootstrap framework. 

Refer to the main.py section for more information about the individual pages.

<br>

### **static**
The static folder contains:
- The images used on the website.
- The CSS file is used to style and layout the web pages.
- The ‘script_header’ file for any scripts that need to run in the header i.e., the DataTable script for the stats table.
- The ‘script_footer’ file for the remaining scripts, which include scripts that:
  - Shows or hides the filter options in the form using the radio buttons.
  - Display the loading message when a form is submitted.
  - Changes the domain name label to red if there are any issues with the provided website.

<br>

### **Other**
- Procfile listing the app’s web server.
- requirements.txt listing all the dependencies for the app to run.

<br>

## Limitations
- As mentioned in the helpers.py section, there can be issues with reaching the API quota if two ore more users are running a check at one time. This would lead to the stats table displaying data labeled as ‘API quota reached’ and a flash message being displayed on the stats page warning the user that not all data could be fetched.

<br>

## What’s next
- Initially the loading function provided a progress bar with percentages for the fetching of URLs and CrUX data. This worked locally but there were issues when hosted on a web server. The functionality may be added in the future.

<br>

## EC2 Deployment

<br>

### **Articles used for the instructions:** ###
- https://www.twilio.com/blog/deploy-flask-python-app-aws
- https://medium.com/techfront/step-by-step-visual-guide-on-deploying-a-flask-application-on-aws-ec2-8e3e8b82c4f7
- https://techincent.com/how-to-add-ssl-certificate-in-aws-ec2-ubuntu-nginx-server-with-a-custom-domain/

<br>

### **Requirements** ##
- Flask
- Gunicorn

<br>

### **Instructions** ##

<br>

#### 1. Set up an EC2 instance on AWS: ####
- Select 'Ubuntu'
- Create a KeyPair and ensure it is in .pem format
- Create a security group and select 'SSH', 'HTTPS', and 'HTTP'
- Launch the Instance

<br>

#### 2. Navigate to Security Groups found in the left hand-side menu: ####
- Select 'Edit inbound rules'
- Select add rule and add (Type: Custom TCP | Port range: 8080 | Source: Custom 0.0.0.0/0)

<br>

#### 3. Navigate to Elastic IPs found in the left hand-side menu: ####
- Select the region
- Select 'Allocate'
- Select the newly created elastic IP
- Select 'Associate Elastic IP address' 
- Choose the newly created instance
- Select 'Associate'

<br>

#### 4. Open your terminal and locate the directory with the .pem file ####
- Run the below commands, replacing <PEM_NAME> with the name of your pem file
```
$ chmod 600 ./<PEM_NAME>.pem
$ ssh-add ./<PEM_NAME>.pem
```
- Navigate to the EC2 instance and take a note of the public IPv4 address
- Run the below command, replacing <EC2_PUBLIC_IP_ADDRESS> with the public IPv4 address of the EC2 instance
```
$ ssh ubuntu@<EC2_PUBLIC_IP_ADDRESS>
```
- Type 'yes' when prompted

<br>

#### 5. Once in the ubuntu shell, follow the below steps: ####
- Run the below commands
```
$ sudo apt update
$ sudo apt install python3 python3-pip tmux htop
```
- Create a directory for the project with:
```
$ mkdir your_app_name
```

<br>

#### 6. Ensure your project has a requirements.txt file. This can be created by running the below command within your projects terminal: ####
```
$ pip freeze > requirements.txt
```

<br>

#### 7. Open a new tab or window in your terminal and transfer your project to your EC2 instance running the below command. Replace <YOUR_PROJECT_PATH> with the location of your project on your machine, <EC2_PUBLIC_IP_ADDRESS> with the public IPv4 address of the EC2, and <PROJECT_DIRECTORY> with the name of the directory you created in step 5. ####
```
$ sudo rsync -rv <YOUR_PROJECT_PATH> ubuntu@<EC2_PUBLIC_IP_ADDRESS>:/home/ubuntu/<PROJECT_DIRECTORY>
```

<br>

#### 8. Navigate back to the Ubuntu shell terminal and cd within the directory you created. ####

<br>

#### 9. Use tmux commands to create a new session: ####
```
tmux new -s projectsession
```

<br>

#### 10. Install your project requirements with: ####
```
$ pip3 install -r requirements.txt
```

<br>

#### 11. Run the app with the below command. Replace <MAIN_FILE_NAME> with the name of the Flask file being run (usually app). ####
```
$ gunicorn -b 0.0.0.0:8080 <MAIN_FILE_NAME>:app
```

<br>

#### 13. Exit the session with ctrl + B and then pressing B. Note that a session can be rejoined with: ####
```
$ tmux attach -t projectsession
```
And fully stopped with the below command
```
$tmux kill-session
```

<br>

#### 14. Create systemd to manage Gunicorn by creating a unit file with: ####
```
sudo nano /etc/systemd/system/project.service
```

<br>

#### 15. Add the below to the file and save it (ctrl + o to save and ctr + x to exit). Replace <PROJECT_DIRECTORY> with the name of the directory you created in step 5 and <MAIN_FILE_NAME> with the name of the Flask file being run (usually app). ####
```
[Unit]
Description=Gunicorn instance for the project
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/<PROJECT_DIRECTORY>
ExecStart=/home/ubuntu/<PROJECT_DIRECTORY>/venv/bin/gunicorn -b localhost:8080 <MAIN_FILE_NAME>:app
Restart=always
[Install]
WantedBy=multi-user.target
```

<br>

#### 16. Enable the service by running the below commands: ####
```
$ sudo systemctl daemon-reload
$ sudo systemctl start project
$ sudo systemctl enable project
```

<br>

#### 17. Run the below commands to install Nginx: ####
```
$ sudo apt update
$ sudo apt install nginx
```

<br>

#### 18. Run the below to start the service: ####
```
$ sudo systemctl start nginx
$ sudo systemctl enable nginx
```

<br>

#### 19. Run the following commands: ####
- Open the default fil in the sites-available folder:
```
$ sudo nano /etc/nginx/sites-available/default
```
- Add the below code above the server (below #Default server configuration):
```
upstream flaskproject {
    server 127.0.0.1:8080;
}
```
- Within location remove the line with "try_files" and replace with the below:
```
proxy_pass http://flaskproject;
```
- Save and close the file (ctrl + o to save and ctr + x to exit)

<br>

#### 20. Restart Nginx with: ####
```
$ sudo systemctl restart nginx
```

<br>

#### 21. For SSL, follow the below steps: ####
- install certbot
```
$ sudo apt-get install certbot python3-certbot-nginx -y
```
- Install SSL on the project domain:
```
$ sudo certbot --nginx
```
- Add your email
- Agree to the Terms of Service
- Provide the names of the domains that require HTTPS (separated by a comma for multiple domains)

<br>

#### 22. Within your domain registrar console, add an A type custom record for the domain name you provided in step 19 and set the IP to the EC2 public IP. ####

<br>

The app should now be live on the domain :)