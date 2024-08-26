import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Function to fetch the required prices
def fetch_prices(ticker, start_time_str, end_time_str):
    # Download historical data
    data = yf.download(ticker, period='1mo', interval='1m')

    # Ensure the index is datetime
    data.index = pd.to_datetime(data.index)

    # Create time objects for comparison
    start_time = datetime.strptime(start_time_str, '%H:%M').time()
    end_time = datetime.strptime(end_time_str, '%H:%M').time()

    # Find the closest times within a 1-minute range
    start_time_range = (datetime.combine(datetime.today(), start_time) - timedelta(minutes=1)).time()
    end_time_range = (datetime.combine(datetime.today(), end_time) + timedelta(minutes=1)).time()

    # Extract time from index
    data['Time'] = data.index.time

    # Filter the data for start and end times
    start_prices = data[(data['Time'] >= start_time_range) & (data['Time'] <= end_time_range)]['Close']

    end_prices = data[(data['Time'] >= start_time_range) & (data['Time'] <= end_time_range)]['Close']

    return start_prices, end_prices

# Streamlit app
st.title('Nasdaq 100 Futures Prices')
st.write('Fetching start and end prices for NQ=F from Yahoo Finance')

# Define the times
start_time_str = '05:30'
end_time_str = '13:30'

# Fetch the prices
start_prices, end_prices = fetch_prices('NQ=F', start_time_str, end_time_str)

# Display the prices
st.write('Start Prices at 05:30 UTC:')
st.write(start_prices if not start_prices.empty else 'No data found for 05:30 UTC.')
st.write('End Prices at 13:30 UTC:')
st.write(end_prices if not end_prices.empty else 'No data found for 13:30 UTC.')
