import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# Define the time range for the last 60 days
end_date = datetime.now()
start_date = end_date - timedelta(days=60)

# Fetch data from Yahoo Finance
@st.cache_data
def fetch_data(ticker):
    # Fetch daily data
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    return data

# Extract price at close and rename the column to the ticker
def extract_price(data, ticker):
    return data[['Close']].rename(columns={'Close': ticker})

# Main function to display the data
def main():
    st.title('Nasdaq vs Nasdaq Futures')

    # Initialize an empty DataFrame
    combined_data = pd.DataFrame()

    # Fetch and combine data for NASDAQ
    nasdaq_data = fetch_data('^IXIC')
    if not nasdaq_data.empty:
        nasdaq_data = extract_price(nasdaq_data, '^IXIC')
        combined_data = pd.concat([combined_data, nasdaq_data], axis=1)

    # Fetch and combine data for NASDAQ Futures
    nq_f_data = fetch_data('NQ=F')
    if not nq_f_data.empty:
        nq_f_data = extract_price(nq_f_data, 'NQ=F')
        combined_data = pd.concat([combined_data, nq_f_data], axis=1)

    # Compute the percent change for each index
    percent_change = combined_data.pct_change().rename(columns=lambda x: f'{x} % Change')

    # Concatenate the percent change data with the closing prices
    combined_data = pd.concat([combined_data, percent_change], axis=1)

    # Display the combined data
    if not combined_data.empty:
        st.write(f"Combined closing prices and percent changes from {start_date.date()} to {end_date.date()}:")
        st.dataframe(combined_data)
    else:
        st.write("No data available for the selected indices in the selected period.")

    download = combined_data.to_csv(index=True).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=download,
        file_name='nasdaq_data.csv',
        mime='text/csv',
        help="Click to download the CSV file containing the NASDAQ data."
    )

if __name__ == "__main__":
    main()
