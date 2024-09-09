# https://www.youtube.com/watch?v=Oo8-nEuDBkk&list=PLr51Y6xnCThP7MFXPplDCxWGBCvdQKmE8&index=16

import streamlit as st
from scrape import scrape_website

st.title('AI Web Scraper')
url = st.text_input('Enter URL: ', 'https://www.bing.com/')

st.button("Click here after logging in")

if st.button('Scrape'):
  st.button("Click here after logging in")
  st.write('Scrapping...'  )
  result = scrape_website(url)
  st.write(result)