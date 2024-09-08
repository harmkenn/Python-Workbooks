import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
import time
import undetected_chromedriver as uc
import pandas as pd
from selenium.webdriver.common.by import By
import time
import re

def scrape_website(website):
  print('Launching chrome browser...')

  chrome_driver_path = './chromedriver.exe'
  options = webdriver.ChromeOptions()
  driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

  # Create the WebDriver instance
  driver = uc.Chrome(options=options)
  try:
    driver.get(website)
    print('Website loaded successfully')
    html = driver.page_source
    time.sleep(10)
    
    return html
  finally:
    driver.quit()
    
  