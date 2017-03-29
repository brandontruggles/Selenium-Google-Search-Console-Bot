# Selenium Google Search Console Bot
This is a simple Python bot which uses Selenium to scrape the Google Search Console Dashboard [https://www.google.com/webmasters/tools/home](https://www.google.com/webmasters/tools/home)  for the number of total indexed urls for a particular site. This should be possible with a simple API call, however, Google has not yet implemented an API call for this particular number. This script also scrapes other data available from the dashboard including the total number of *soft 404* errors, the total number of *not found* errors, and the total of *other* errors for a particular site. However, these numbers **can** be obtained through the use of the [Google Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original/v3/urlcrawlerrorscounts/query). After scraping the data, the script then writes the data to a Google Sheet using the [Google Sheets API](https://developers.google.com/sheets/). The script is configured to use PhantomJS, which is included as a Node.js dependency, but Chromedriver is included as a Pip dependency in the case that you want to use a non-headless webdriver.

## Installation Instructions (Linux/Mac)

1. Make sure that you have Python 2.7.X installed, along with Pip.

2. Install Node.JS and NPM.

3. Download or clone this repository to a directory on your machine.

4. Add the directory containing this project into your global PYTHONPATH environment variable.

5. Open the terminal, navigate to the project directory, and type the command `pip install -r requirements.txt`. This should install the Python dependencies Selenium and Chromedriver. *NOTE: On Mac, the dependency chromedriver-installer may not download. If this is the case, you will have to install Chromedriver manually.*

6. From the terminal, type the command `npm install`. This should install PhantomJS.

7. Edit the `scrape.conf` JSON file to your liking, but make sure that it still contains valid JSON syntax. This file allows you to control which website on your dashboard will be analyzed by the script, the ID of the Google Spreadsheet to write output to, the ID of the Google Sheet within the Google Spreadsheet to write output to, the coordinates of where the output row should be written on the Google Sheet, as well as the order that the output is written. The order and size of the output is determined by the "output" key in `scrape.conf`, which uses the following variables to represent different numbers:

* `date` - The current month and current year.

* `soft404Num` - The number of "soft 404" errors for the current month.

* `notFoundNum` - The number of "not found" errors for the current month.

* `otherNum` - The number of "other" errors for the current month.

* `indexNum` - The total number of pages indexed.

8. You may edit `scrapedata.py` to use PhantomJS instead of Chromedriver if you do not wish to view the browser navigation performed by the script.

9. In order to access the Google Sheets API with this script, you must follow the insructions for creating an API project and downloading a `client_secret.json` file to the root project directory. These instructions are available here: [https://developers.google.com/api-client-library/python/auth/installed-app#creatingcred](https://developers.google.com/api-client-library/python/auth/installed-app#creatingcred). 

10. Run the program from the terminal with `python scrapedata.py`. **NOTE:** There are a series of flags that can be used when executing the script which will change its behavior. The following are the most useful of these flags:

* `--noauth_local_webserver` - Displays an authentication link in the terminal rather than opening an authentication page in a browser window. Allows you to authenticate while logged into a server remotely.

* `--refresh` - The script will not perform the data scraping or Google Sheets uploading processes, and will instead simply redownload the cookies from the browser after logging in. This is useful for keeping login information persistent over long periods of time with no user intervention.

11. If it is your first time running this script, or your login tokens have expired since your last run, you will be prompted for your Google credentials upon running the script. To securely avoid having to ask for these credentials upon every run, the script will save your Selenium browser cookies each time you run the script. These cookies are saved to the local file `cookies.dat`, where they are read for subsequent runs.

## Installation Instructions (Windows)

This script has not been tested for Windows, but it should still work if a similar procedure is followed as the one for Linux/Mac.
