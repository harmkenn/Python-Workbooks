import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Define the time range for the last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=200)

# Fetch data from Yahoo Finance
@st.cache_data
def fetch_data(ticker):
    # Fetch daily data
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    return data

# Extract price at close
def extract_price(data):
    return data[['Close']]

# Main function to display the data
def main():
    st.title('Closing Prices for NASDAQ (^IXIC), FTSE (^FTSE), and NASDAQ Futures (NQ=F)')

    # Fetch and display the data for NASDAQ
    nasdaq_data = fetch_data('^IXIC')
    if not nasdaq_data.empty:
        st.write(f"Closing prices for NASDAQ (^IXIC) from {start_date.date()} to {end_date.date()}:")
        nasdaq_data = extract_price(nasdaq_data)
        st.dataframe(nasdaq_data)
    else:
        st.write("No data available for NASDAQ (^IXIC) in the selected period.")

    # Fetch and display the data for FTSE
    ftse_data = fetch_data('^FTSE')
    if not ftse_data.empty:
        st.write(f"Closing prices for FTSE (^FTSE) from {start_date.date()} to {end_date.date()}:")
        ftse_data = extract_price(ftse_data)
        st.dataframe(ftse_data)
    else:
        st.write("No data available for FTSE (^FTSE) in the selected period.")

    # Fetch and display the data for NASDAQ Futures
    nq_f_data = fetch_data('NQ=F')
    if not nq_f_data.empty:
        st.write(f"Closing prices for NASDAQ Futures (NQ=F) from {start_date.date()} to {end_date.date()}:")
        nq_f_data = extract_price(nq_f_data)
        st.dataframe(nq_f_data)
    else:
        st.write("No data available for NASDAQ Futures (NQ=F) in the selected period.")

if __name__ == "__main__":
    main()
