import flask
from flask import request, jsonify, make_response
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime as dt
import sys
import json
from selenium.common.exceptions import NoSuchElementException

app = flask.Flask(__name__)
app.config["DEBUG"] = True


def checkValid(date):

    inputType = date
    formatType = '%m/%d/%Y'
    convertedTime =  dt.strptime(inputType, formatType)

    if convertedTime < dt.now():
        return False
    return True

def lookup(data):
    # Read from json file
    with open("settings.json", "r") as f:
        site_data = json.load(f)

    # Establish web driver
    print("Establishing web driver...")
    options = Options()

    # Run headless
    options.add_argument("--headless")

    # Avoid detection
    # options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # Initialize log file
    output_file = open("cert-list.txt", "a")

    # Check that settings file has content
    try:
        assert len(site_data)
        print("Settings file loaded")
    except AssertionError:
        # TODO: Logging package
        print("Error loading JSON data")
        # TODO: Return error

    # Grab URL in settings file
    url = site_data["siteURL"]

    # # Current Date & Time
    # timeStamp = dt.now()

    # Open the url
    driver.get(url)

    # Wait for page to render
    time.sleep(1)

    # NOTE: Remove for optimization if needed
    # This is the page title text
    pageTitle = driver.title
    targetTitle = site_data["title"]

    # Check we didn"t 404 or other error
    print("Did site load?")
    try:
        assert targetTitle in pageTitle
        print("Okay, cool. Page exists!")
    except AssertionError:
        print("Crap! Page Error!!")

    # Dismiss cookie banner
    try:
        driver.find_element("xpath", site_data["cookieButton"]).click()
        time.sleep(.5)
    except:
        print("No cookie banner")

    time.sleep(.5)
    print(data)

# try:
    # Exit if missing the 3 params
    if len(data) == 3:
        # Select the name & location search form
        verifyElem = site_data["verifyByNameLocationElem"]
        driver.find_element("xpath", verifyElem).click()

        # Enter first & last name
        driver.find_element("id", site_data["fNameElem"]).send_keys(data["f"])
        driver.find_element("id", site_data["lNameElem"]).send_keys(data["l"])

        # NOTE: Is there a select/active element focus without clicking?
        # Click the dropdown and enter State
        driver.find_element("xpath", site_data["stateDropdown"]).click()
        driver.find_element("xpath", site_data["stateDropdown"]).send_keys(data["s"])

        # Submit
        driver.find_element("xpath", site_data["verifyCertButton"]).click()

    elif len(data) == 1:
        assert int(data[0])
        # Enter cert number
        driver.find_element("id", site_data["certNumElem"]).send_keys(data["n"])
        # Submit
        driver.find_element("xpath", site_data["verifyCertButtonNum"]).click()
# except:
    # TODO: Get rid of this print and add a logging feature instead
    # print("ERROR: Missing search params. Please include first name, last name, and State...")

    # Wait for page render
    time.sleep(1)

    # Ensure result found
    try:
        driver.find_element("xpath", site_data["resultLink"]).is_displayed()
    except:
        return("No results found")

    # Click the results
    driver.find_element("xpath", site_data["resultLink"]).click()

    # Allow page load
    time.sleep(.5)

    # Scrape information
    # TODO: Get the name
    accNum = driver.find_element("xpath", site_data["accountNumber"]).text
    formatAccNum = accNum.split()
    last4 = formatAccNum[3]

    expDate = driver.find_element("xpath", site_data["expirationDate"]).text
    formatExpDate = expDate.split()
    date = formatExpDate[2]
    
    # Results Object
    userResults = {}
    # FIXME: Need to scrape the name too
    # userResults["Name"] = "{} {}".format(sys.argv[1], sys.argv[2])
    userResults["Account Number"] = last4
    userResults["Valid"] = checkValid(date)
    userResults["Valid Through"] = date
    print(userResults)
    return userResults


methods = ["GET", "POST"]
headers = {"Content-Type": "application/json"}

@app.route("/info", methods=methods)
def _info():
    if request.method != "GET":
        response = make_response(
            {"Status": "Error", "Message": "Method not allowed"},
            405,
        )
        response.headers = headers
        return response

    return make_response(
            {"Status": "Success", "Message": 'Please search using the /search route. Allowed lookup types are by Cert Num, or by First/Last/State. Format should be f=First l=Last s=State Here or n=123456789 (as type int)'}, 200
        )

@app.route("/search", methods=methods)
def _search():
    if request.method != "GET":
        response = make_response(
            {"Status": "Error", "Message": "Nah, keep the change"},
            405,
        )
        response.headers = headers
        return response

    results = lookup(request.args)
    if len(results):
        return make_response(
                {"Status": "Success", "Message": "Result found", "Results": results}, 200
            )

    else:
        return make_response(
            {"Status": "Error", "Message": "No results found..."}, 200
        )

