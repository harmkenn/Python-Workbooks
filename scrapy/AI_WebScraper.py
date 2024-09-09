# https://www.youtube.com/watch?v=Oo8-nEuDBkk&list=PLr51Y6xnCThP7MFXPplDCxWGBCvdQKmE8&index=16

import streamlit as st
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

def extract_body_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    body_content = soup.body
    if body_content:
        return str(body_content)
    else:
        return ""
  
def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()

    cleaned_content = soup.get_text(separator="\n") 
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]
   

st.title('AI Web Scraper')
url = st.text_input('Enter URL: ', 'https://techwithtim.net')

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
    body_content = extract_body_content(html)
    cleaned_content = clean_body_content(body_content)

    st.session_state.dom_content = cleaned_content

    with st.expander('View DOM Content'):
       st.text_area('DOM Content', cleaned_content, height=300)

if "dom_content" in st.session_state:
    parse_description = st.text_area('Describe what you want to parse.')
    if st.button('Parse Content'):
        if parse_description:
            st.write('Parsing the content...')
            dom_chuncks = split_dom_content(st.session_state.dom_content)


if st.button('Finished') and st.session_state.loaded:
    st.session_state.driver.quit()
  
# https://youtu.be/Oo8-nEuDBkk?si=W1rU0kR3XB1sJJ3s&t=1989

  



  

  
