# import string
# import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime as dt
# import calendar
import sys
import json
from selenium.common.exceptions import NoSuchElementException
import smtplib

# NOTE: Sleeps are important for ensuring page load

def login(element, driver, site_data):
    print("Logging in user...")
    
    # Click the login button
    element.click()

    # Wait for page to load
    # time.sleep(4)

    emailField = driver.find_element("xpath", site_data["emailInputElem"])
    passwordField = driver.find_element("xpath", site_data["passwordInputElem"])
    submitButton = driver.find_element("xpath", site_data["signInButton"])

    emailField.send_keys(site_data["siteCreds"][0]["username"])
    passwordField.send_keys(site_data["siteCreds"][0]["password"])

    submitButton.click()

def email(site_data, userResults):
    print("Sending email with your information...")
    print("Creating email...")

    # Get login information
    emailName = site_data["emailCreds"][0]["username"]
    emailPass = site_data["emailCreds"][0]["password"]

    # Email recipient
    toEmail = site_data["emailRec"]

    # Create session
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login(emailName, emailPass)

    # Build email
    emailBody = ("Here are your lookup results: % s" % (userResults))
    emailSubject = ("ASHA Cert Results on % s" % dt.now())

    headers = "\r\n".join(
        ["from: " + emailName, "subject: " + emailSubject, "to: " + toEmail, "mine-version: 1.0", "content-type: text/html"])

    content = headers + "\r\n\r\n" + emailBody

    # Sent email
    s.sendmail(emailName, toEmail, content)
    s.quit()

    print("Email sent successfully")

def checkValid(date):

    inputType = date
    formatType = '%m/%d/%Y'
    convertedTime =  dt.strptime(inputType, formatType)

    if convertedTime < dt.now():
        return False
    return True

def numLookup(driver, site_data, sys):
    print("Looking up by number...")

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


    # NOTE: REMOVE IF NO LOGIN NEEDED
    # Login check
    # loginElement = site_data["loginElem"]
    # if driver.find_element("xpath",loginElement).is_displayed():
    #     try: 
    #         login(driver.find_element("xpath", loginElement))
    #         print("User is not logged in...")
    #     except:
    #         print("ERROR WITH THE LOGIN PROCESS")

    # Dismiss cookie banner
    try:
        driver.find_element("xpath", site_data["cookieButton"]).click()
        time.sleep(.5)
    except:
        print("No cookie banner")

    time.sleep(.5)

    # Enter cert number
    driver.find_element("id", site_data["certNumElem"]).send_keys(sys.argv[1])

    # Submit
    driver.find_element("xpath", site_data["verifyCertButtonNum"]).click()

    # Wait for page render
    time.sleep(1)

    # Ensure result found
    try:
        driver.find_element("xpath", site_data["resultLink"]).is_displayed()
    except:
        return("No results found")

    driver.find_element("xpath", site_data["resultLink"]).click()

    time.sleep(1)

    accNum = driver.find_element("xpath", site_data["accountNumber"]).text
    formatAccNum = accNum.split()
    last4 = formatAccNum[3]

    expDate = driver.find_element("xpath", site_data["expirationDate"]).text
    formatExpDate = expDate.split()
    date = formatExpDate[2]
    
    # Results Object
    userResults = {}
    # userResults["Name"] = "{} {}".format(sys.argv[1], sys.argv[2])
    userResults["Account Number"] = last4
    userResults["Valid"] = checkValid(date)
    userResults["Valid Through"] = date
    print(userResults)
    return userResults

def nameLookup(driver, site_data, sys):
    print("Looking up by name...")

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


    # NOTE: REMOVE IF NO LOGIN NEEDED
    # Login check
    # loginElement = site_data["loginElem"]
    # if driver.find_element("xpath",loginElement).is_displayed():
    #     try: 
    #         login(driver.find_element("xpath", loginElement))
    #         print("User is not logged in...")
    #     except:
    #         print("ERROR WITH THE LOGIN PROCESS")

    # Dismiss cookie banner
    try:
        driver.find_element("xpath", site_data["cookieButton"]).click()
        time.sleep(.5)
    except:
        print("No cookie banner")

    time.sleep(.5)

    # Select the Name & Location search form
    verifyElem = site_data["verifyByNameLocationElem"]
    driver.find_element("xpath", verifyElem).click()

    # Enter first & last name
    driver.find_element("id", site_data["fNameElem"]).send_keys(sys.argv[1])
    driver.find_element("id", site_data["lNameElem"]).send_keys(sys.argv[2])

    # TODO: Is there a select/active element focus without clicking?
    # Click the dropdown and enter State
    driver.find_element("xpath", site_data["stateDropdown"]).click()
    driver.find_element("xpath", site_data["stateDropdown"]).send_keys(sys.argv[3])

    # Submit
    driver.find_element("xpath", site_data["verifyCertButton"]).click()

    # Wait for page render
    time.sleep(1)

    # Ensure result found
    try:
        driver.find_element("xpath", site_data["resultLink"]).is_displayed()
    except:
        return("No results found")

    driver.find_element("xpath", site_data["resultLink"]).click()

    time.sleep(1)

    accNum = driver.find_element("xpath", site_data["accountNumber"]).text
    formatAccNum = accNum.split()
    last4 = formatAccNum[3]

    expDate = driver.find_element("xpath", site_data["expirationDate"]).text
    formatExpDate = expDate.split()
    date = formatExpDate[2]

    # Results Object
    userResults = {}
    userResults["Name"] = "{} {}".format(sys.argv[1], sys.argv[2])
    userResults["Account Number"] = last4
    userResults["Valid"] = checkValid(date)
    userResults["Valid Through"] = date
    print(userResults)
    return userResults

def main(sys):
    # datetime debugging
    # checkValid("03/31/2024")
    
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
        print("Error loading JSON data")
        quit()

    # Exit if missing the 3 params
    if len(sys.argv) == 4:
        results = nameLookup(driver, site_data, sys)
        return results
    elif len(sys.argv) == 2 and int(sys.argv[1]):
        results = numLookup(driver, site_data, sys)
        return results
    print("ERROR: Missing search params. Please include first name, last name, and State...")
    quit()



    # NOTE: Log writing functionality
    # # Finish off writing to log
    # output_file.write("Done searching on % s \n" % (dt.now()))
    # output_file.write("\n")
    # output_file.write(
    #     "User: %s \n" % userResults["Name"]
    # )
    # output_file.write(
    #     "Account Number: % s \n" % userResults["Account Number"]
    # )
    # output_file.write(
    #     "Is Valid: % s \n" % userResults["Valid"]
    # )
    # output_file.write(
    #     "Expires: % s \n" % userResults["Valid Through"]
    # )

    # # Display results in console
    # print("Done searching...")
    # print("Results : % s" % userResults)

main(sys)
