import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
import time

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
    
  