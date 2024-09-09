import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

def scrape_website(website):
  print('Launching chrome browser...')

  options = uc.ChromeOptions()
  options.add_argument("--disable-blink-features=AutomationControlled")
  #options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"    # Replace with actual path
  driver = uc.Chrome(options=options)

  try:
    driver.get(website)
    print('Website loaded successfully')
    html = driver.page_source
    time.sleep(10)
    
    return html
  finally:
    driver.quit()

def extract_body_content(html_content):
  soup = BeautifulSoup(html_content, 'html.parser')
  body_content = soup.body
  if body_content:
    return str(body_content)
  return "Body content not found."

# https://youtu.be/Oo8-nEuDBkk?si=bUQr0kAADI17dD2n&t=1469
    
  