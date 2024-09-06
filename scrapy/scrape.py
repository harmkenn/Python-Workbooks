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

  # Set up undetected-chromedriver
  options = uc.ChromeOptions()
  options.add_argument("--disable-blink-features=AutomationControlled")

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
    
  