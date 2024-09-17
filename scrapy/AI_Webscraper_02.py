import streamlit as st
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from transformers import AutoTokenizer, AutoModelForCausalLM



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

def parse_with_transformers(dom_chunks, parse_description):
    inputs = tokenizer.batch_encode_plus(
        dom_chunks,
        padding=True,
        truncation=True,
        max_length=1024,
        return_tensors="pt"
    )
    outputs = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_new_tokens=512,
        num_return_sequences=1
    )
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)

st.title('AI Web Scraper')
url = st.text_input('Enter URL: ', 'https://techwithtim.net')

# Load pre-trained model and tokenizer
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

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
    st.write('Scraping...')
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