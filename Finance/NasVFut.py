import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Define the time range
end_date = datetime.now()
start_date = end_date - timedelta(days=200)

# Fetch data from Yahoo Finance
@st.cache_data
def fetch_data():
    # Fetch daily data
    data = yf.download('NQ=F', start=start_date, end=end_date, interval='1d')
    return data

# Extract price at 13:00 UTC
def extract_price(data):
    # Since interval='1d', data is daily, and there's no need to filter by time within this interval
    # but for completeness, ensure data is in expected time zone and format
    data.index = pd.to_datetime(data.index).tz_localize('UTC')
    return data

# Main function to display the data
def main():
    st.title('Daily Price for NQ=F at 13:00 UTC')
    st.write(f"Displaying daily prices at 13:00 UTC from {start_date.date()} to {end_date.date()}")

    # Fetch and display the data
    data = fetch_data()
    if not data.empty:
        # Extract and display the price
        data = extract_price(data)
        st.write("Daily price data at 13:00 UTC:")
        st.dataframe(data[['Close']])  # Displaying only the 'Close' prices
    else:
        st.write("No data available for the selected period.")

if __name__ == "__main__":
    main()
