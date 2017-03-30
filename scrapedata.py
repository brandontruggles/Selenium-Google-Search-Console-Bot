#################################################################################################################################################################
#Written by Brandon Ruggles (brandonrninefive@gmail.com) :)
##################################################################################################################################################################

import json
import time
import datetime
import getpass
import pickle

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
	import argparse
	parser = argparse.ArgumentParser(parents=[tools.argparser])
	parser.add_argument("--refresh", help="Only refresh the cookies and oAuth tokens, do NOT parse any data or upload any data to Google Sheets.", action="store_true")
	flags = parser.parse_args()
except ImportError:
	flags = None

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

confFile = None
cookieFile = None
cookieData = None
username = ""
password = ""
debug = True

try:
	#We read our JSON data from a file called 'scrape.conf' for simplicity and readability.
	confFile = open(os.path.join(os.path.dirname(__file__), "scrape.conf"))
	confJSON = json.loads(confFile.read())
	site = confJSON["site"]
	spreadsheetId = confJSON["spreadsheetId"]
	sheetId = confJSON["sheetId"]
	rowIndex = confJSON["rowIndex"]
	columnIndex = confJSON["columnIndex"]
	confOutput = confJSON["output"]
except Exception as e:
	print "Error: either no scrape.conf was found, or it contains invalid JSON syntax!"
	if(debug):
		print "Error Details: " + str(e)
try:
	#We read our cookies from a file called 'cookies.dat' (used for storing Google login credentials securely.
	cookieFile = open(os.path.join(os.path.dirname(__file__), "cookies.dat"))
	cookieData = pickle.loads(cookieFile.read())
except Exception as e:
	print "Error: either no cookies.dat was found, or the data it contains could not be read!"
	if(debug):
		print "Error Details: " + str(e)

	username = raw_input("Please type in your Google username: ")
	password = getpass.getpass(prompt="Please type in your Google password: ")

def login(username, password, cookieData):
	if(cookieData != None):
		driver.get('https://www.google.com/')
		for cookie in cookieData:
			driver.add_cookie(cookie)
		driver.get('https://www.google.com/webmasters/tools/home')
	else:
		driver.get('https://www.google.com/webmasters/tools/home')
		boxDiv = driver.find_element_by_xpath('/html/body/div/div/div/div/form/div/div/div/div/div')
		usernameBox = boxDiv.find_element_by_xpath('./input[@id="Email"]')

		usernameBox.send_keys(username)
		usernameBox.send_keys(Keys.ENTER)
		boxDiv = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div/div[2]/div[2]/div[1]/form/div[2]/div/div[2]/div/div')))
		passwordBox = boxDiv.find_element_by_xpath('./input[@id="Passwd"]')
		passwordBox.send_keys(password)
		passwordBox.send_keys(Keys.ENTER)
	
def scrape():
	print "Attempting to scrape the Google Search Console data..."
	siteLink = None
	siteLinks = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/div/div/div/div/table/tbody/tr/td[2]/table/thead/tr/th[2]/div[1]/a')))
	for link in siteLinks:
		if(link.text == site):
			siteLink = link
			break
	siteLink.click()
	soft404Div = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="wmx_gwt_feature_DASHBOARD"]/div/div[5]/div[1]/div/table/tbody/tr[1]/td/div/div/div[2]/div[2]/table/tbody/tr/td[2]/div/div[1]')))
	notFoundDiv = driver.find_element_by_xpath('//*[@id="wmx_gwt_feature_DASHBOARD"]/div/div[5]/div[1]/div/table/tbody/tr[1]/td/div/div/div[2]/div[2]/table/tbody/tr/td[2]/div/div[2]')
	otherDiv = driver.find_element_by_xpath('//*[@id="wmx_gwt_feature_DASHBOARD"]/div/div[5]/div[1]/div/table/tbody/tr[1]/td/div/div/div[2]/div[2]/table/tbody/tr/td[1]/div/div[3]')
	soft404Num = long(soft404Div.find_element_by_xpath('./b').get_attribute('innerHTML').replace(",", ""))
	notFoundNum = long(notFoundDiv.find_element_by_xpath('./b').get_attribute('innerHTML').replace(",", ""))
	otherNum = long(otherDiv.find_element_by_xpath('./b').get_attribute('innerHTML').replace(",", ""))
	month = str(datetime.date.today().month)
	year = str(datetime.date.today().year)
	if(int(month) < 10):
		month = "0" + month
	date = year + "|" + month
	indexDiv = driver.find_element_by_xpath('//*[@id="navigation"]/li[5]/div')
	indexDiv.click()
	indexStatusButton = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="navigation"]/li[5]/ul/li[1]/a')))
	indexStatusButton.click()
	indexDiv = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="index-status-chart-legend"]/div/table/tbody/tr[2]/td/div')))
	indexNum = long(indexDiv.get_attribute('innerHTML').replace(",", ""))

	#Change the order of these values to change the order that they are pasted into the spreadsheet
	outputArr = eval(confOutput)
	print "Successfully scraped all of the requested data!"
	return outputArr

def getDictForItem(item):
	returnDict = {}
	if(isinstance(item, int) or isinstance(item, float) or isinstance(item, long) or isinstance(item, complex)):
		returnDict = {"numberValue": item}
	elif(isinstance(item, bool)):
		returnDict = {"boolValue": item}
	elif(isinstance(item, basestring)):
		returnDict = {"stringValue": item}
	else:
		returnDict = {"stringValue": ""}
		print "The type of the item was not compatible with the Sheets API! Item: " + str(item)
	return returnDict

def getAPICredentials():
	print "Attempting to retrieve API credentials..."
	SCOPES = "https://www.googleapis.com/auth/spreadsheets"
	CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")
	CREDENTIAL_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
	APPLICATION_NAME = "Selenium Google Search Console Bot"	
	store = Storage(CREDENTIAL_FILE)
	credentials = store.get()

	if(not credentials or credentials.invalid):
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		if(flags):
			credentials = tools.run_flow(flow, store, flags)
		else:
			credentials = tools.run(flow, store)
	print "The API credentials were retrieved successfully!"
	return credentials

def writeToCSV(outputArr):
	print 'Attempting to write data to the specified Google Sheet...'
	
	http = getAPICredentials().authorize(httplib2.Http())
	discoveryUrl = ("https://sheets.googleapis.com/$discovery/rest?version=v4")
	service = discovery.build("sheets", "v4", http=http, discoveryServiceUrl=discoveryUrl)
	valuesToWrite = []
	for item in outputArr:
		valuesToWrite.append({"userEnteredValue": getDictForItem(item)})
	update_request_body = {
		"requests": [
			{
				"updateCells": {
					"rows": [{"values": valuesToWrite}],
					"fields": "*",
					"start": {"sheetId": sheetId, "rowIndex": rowIndex, "columnIndex": columnIndex}
				}
			}
		]
	}
	
	result = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=update_request_body).execute()
	print "Response to update request: " + str(result)

startTime = time.time()

#driver = webdriver.Chrome() #Non-headless webdriver
driver = webdriver.PhantomJS() #Headless webdriver

try:
	login(username, password, cookieData)
	if(not flags.refresh):
		writeToCSV(scrape())
	else:
		getAPICredentials()
	print "Writing cookie data to 'cookies.dat'..." 
	dump = pickle.dumps(driver.get_cookies())
	cookieFile = open(os.path.join(os.path.dirname(__file__), "cookies.dat"), "w")
	cookieFile.write(dump)
	cookieFile.close()
	print "Successfully wrote cookies to 'cookies.dat'!"
	driver.close()
	if(flags.refresh):
		print "The script has finished refreshing the cookies and oAuth tokens successfully!"
	else:
		print "The script has successfully finished executing!"
except Exception as e:
	print "An error occurred!"
	if(debug):
		print "Error Details: " + str(e) 

print "Total elapsed script time: " + str(time.time() - startTime) + " second(s)."
