from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import time
from random import randint
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, ValidationError
from time import sleep
import re
import traceback


app = FastAPI()

class schema(BaseModel):
    number: str

    @field_validator('number')
    def validate_phone_number(cls, v):
        # Define the regex pattern for the desired phone number format
        pattern = r'^\d{1,3} \d{1,4} \d{6,10}$'

        # Check if the phone number matches the pattern
        if not re.match(pattern, v):
            raise ValueError('Invalid phone number format. The format should be: <Country code> <Area code> <Number>, no need to add + or the 00 before the country code.')
        return v

chrome_service = Service(executable_path='/usr/bin/chromedriver')
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-notifications")

@app.post("/getBusinessName")
async def getBusinessName(number: schema):
    try:
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        driver.get("https://www.google.com")
        driver.implicitly_wait(10)

        sleep(3)

        searchArea = driver.find_elements(By.TAG_NAME, "textarea")
        searchArea[0].send_keys(number.number)

        searchArea[0].send_keys(Keys.RETURN)
        driver.implicitly_wait(10)
        sleep(5)

        preciseLoc = driver.find_elements(By.CLASS_NAME, "sjVJQd")
        for j in preciseLoc:
            if j.text.lower() == "not now":
                j.click()
                sleep(4)

        nameComp = driver.find_elements(By.CLASS_NAME, 'SPZz6b')

        if len(nameComp) == 0:
            nameComp2 = driver.find_elements(By.CLASS_NAME, "DoxwDb")
            if len(nameComp2) == 0:
                print("Company Does not exist!")
                # driver.quit()
                return "Company Does not exist!" , driver.quit()
            print("Phone Number:\t", number)
            print("Company Name:\t", nameComp2[0].text)
            # driver.quit()
            return nameComp2[0].text, driver.quit()
            
        else:
            print("Phone Number:\t", number)
            
            print("Company Name:\t", nameComp[0].find_element(By.TAG_NAME, "span").text)
            # driver.quit()
            return nameComp[0].find_element(By.TAG_NAME, "span").text , driver.quit()
        
    except Exception as e:
        # driver.quit()
        print(f"Error occured:\t {e}", "\n", traceback.print_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        try:
            driver.quit()
        except Exception as cleanup_error:
            print(f"Error during driver cleanup: {cleanup_error}")

