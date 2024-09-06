import streamlit as st

st.title('AI Web Scraper')
url = st.text_input('Enter URL: ')

if st.button('Scrape'):
  st.write('Scrapping...'  )