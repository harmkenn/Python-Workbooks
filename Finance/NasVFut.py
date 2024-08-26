import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Define the time range
end_date = datetime.now()
start_date = end_date - timedelta(days=300)

# Fetch data from Yahoo Finance
@st.cache_data
def fetch_data():
    data = yf.download('NQ=F', start=start_date, end=end_date, interval='1h')
    return data

# Main function to display the data
def main():
    st.title('Hourly Prices for NQ=F')
    st.write(f"Displaying hourly prices from {start_date.date()} to {end_date.date()}")

    # Fetch and display the data
    data = fetch_data()
    if not data.empty:
        st.write("Hourly price data:")
        st.dataframe(data)
    else:
        st.write("No data available for the selected period.")

if __name__ == "__main__":
    main()
