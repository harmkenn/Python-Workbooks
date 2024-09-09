# https://www.youtube.com/watch?v=Oo8-nEuDBkk&list=PLr51Y6xnCThP7MFXPplDCxWGBCvdQKmE8&index=16

import streamlit as st
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time


st.title('AI Web Scraper')
url = st.text_input('Enter URL: ', 'https://www.familysearch.org/')

driver = None

if 'driver' not in st.session_state:
    st.session_state.driver = None
    st.session_state.loaded = False

if st.button('Load Initial Page'):
    print('Launching chrome browser...')
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    st.session_state.driver = uc.Chrome(options=options)
    st.session_state.driver.get(url)
    st.write('Page loaded. Please navigate to the desired page.')
    st.warning('Click the "Continue" button when you are finished navigating.')
    st.session_state.loaded = True

if st.button('Continue') and st.session_state.loaded:
    new_url = st.session_state.driver.current_url
    st.session_state.driver.get(new_url)
    st.write('Scrapping...'  )
    html = st.session_state.driver.page_source
    time.sleep(10)
    st.write(html)

if st.button('Finished') and st.session_state.loaded:
    st.session_state.driver.quit()
  

  



  

  
