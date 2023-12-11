from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import requests
import json

debug_cookie = None

def main():
    authCookie = dict()
    authCookie['Authorization'] = debug_cookie if debug_cookie else selenium_obtain_authToken()   
    
    response = get_receipts_from_pageindex(0, authCookie)

    totalItem = response['totalCount']

    print(f"Found {totalItem} receipts...")

    availablePages = int(int(totalItem)/10)+1
    
    data = []

    for page in range(availablePages):
        print(f"Fetching receipts from page {page+1}/{availablePages}...")
        response = get_receipts_from_pageindex(page, authCookie)
        pageItems = response['items']
        for receipt in range(len(pageItems)):
            response = get_receipt_by_id(pageItems[receipt]['id'], authCookie)
            data.append(response)
    return data

def get_receipts_from_pageindex(index, authCookie):
    req = requests.get(f"https://www.lidl.de/mre/api/v1/tickets?country=DE&page={index+1}", headers=authCookie)
    if req.status_code != 200:
        print("Unable to authorize. Aborting...")
        return
    return req.json()

def get_receipt_by_id(id, authCookie):
    req = requests.get(f"https://www.lidl.de/mre/api/v1/tickets/{id}?country=DE&languageCode=de-DE", headers=authCookie)
    if req.status_code != 200:
        print("Unable to authorize. Aborting...")
        return
    return req.json()

def selenium_obtain_authToken():
    twoFactor = True if input("Are you using 2-factor authentication for LIDL Plus? (y/n): ") == "y" else False
    driver = webdriver.Chrome()


    driver.get("https://lidl.de/user-api/login?step=login&redirect=https%3A%2F%2Fwww.lidl.de%2F")

    delay = 300

    try:
        wrapper = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/form[1]/div/section/div/div/div[2]/div/div[1]/div[2]/div[2]/div/div/input'))
        )
        print("Found LIDL login page, please insert your email/phone number")
        wrapper = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/form[1]/div/section/div/div/div[3]/div/div[1]/div[2]/div/div/input'))
        )
        print("Please continue by providing your password")
        if twoFactor:
            wrapper = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div/form/div/section/div/div[1]/div/div[3]/div/div/input'))
            )
            print("Please continue by confirming your phone number")
        
        wrapper = WebDriverWait(driver, delay).until(
            EC.title_contains("LIDL lohnt sich")
        )
        print("Login succeeded! Extracting auth token...")        
    except TimeoutException:
        print("Could not find expected ui control! Please retry...")



    authCookie = driver.get_cookie("authToken")
    if not authCookie:
        print("Unable to obtain authToken from cookies. Aborting...")
        return

    return "Bearer " + authCookie.get('value')

if __name__ == "__main__":
    receipts = main()
    print("Writing receipts to json file...")
    json_objects = json.dumps(receipts, indent=2)
    with open("receipts.json", 'w+') as f:
        f.write(json_objects)