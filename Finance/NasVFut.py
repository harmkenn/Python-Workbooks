import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Function to fetch the required prices
def fetch_prices(ticker, start_time, end_time):
    data = yf.download(ticker, period='1mo', interval='1m')
    data['Datetime'] = data.index
    data['Time'] = data['Datetime'].dt.time
    start_prices = data[data['Time'] == start_time]['Close']
    end_prices = data[data['Time'] == end_time]['Close']
    return start_prices, end_prices

# Streamlit app
st.title('Nasdaq 100 Futures Prices')
st.write('Fetching start and end prices for NQ=F from Yahoo Finance')

# Define the times
start_time = datetime.strptime('05:30', '%H:%M').time()
end_time = datetime.strptime('13:30', '%H:%M').time()

# Fetch the prices
start_prices, end_prices = fetch_prices('NQ=F', start_time, end_time)

# Display the prices
st.write('Start Prices at 05:30 UTC:')
st.write(start_prices)
st.write('End Prices at 13:30 UTC:')
st.write(end_prices)
