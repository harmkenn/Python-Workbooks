import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import re



def scrape_website(website):
  print('Launching chrome browser...')

  chrome_driver_path = "./chromedriver.exe"
  options = webdriver.ChromeOptions()
  driver = webdriver.Chrome(service=Service(chrome_driver_path), options = options)
  try:
    driver.get(website)
    print('Website loaded successfully')
    html = driver.page_source
    time.sleep(10)
    
    return html
  finally:
    driver.quit()
    
  