import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Function to fetch the required prices
def fetch_prices(ticker, start_time, end_time):
    data = yf.download(ticker, period='1mo', interval='1m')
    data['Datetime'] = data.index
    data['Time'] = data['Datetime'].dt.time

    # Find the closest times within a 1-minute range
    start_prices = data[data['Time'].between((datetime.combine(datetime.today(), start_time) - timedelta(minutes=1)).time(),
                                             (datetime.combine(datetime.today(), start_time) + timedelta(minutes=1)).time())]['Close']

    end_prices = data[data['Time'].between((datetime.combine(datetime.today(), end_time) - timedelta(minutes=1)).time(),
                                           (datetime.combine(datetime.today(), end_time) + timedelta(minutes=1)).time())]['Close']
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
st.write(start_prices if not start_prices.empty else 'No data found for 05:30 UTC.')
st.write('End Prices at 13:30 UTC:')
st.write(end_prices if not end_prices.empty else 'No data found for 13:30 UTC.')
