import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def get_nasdaq_data(start_date, end_date):
    """
    Fetches NASDAQ composite index closing prices from Yahoo Finance.

    Args:
        start_date: Start date of the data.
        end_date: End date of the data.

    Returns:
        pandas DataFrame containing the NASDAQ closing prices.
    """

    # NASDAQ composite index ticker
    nasdaq_ticker = "^IXIC"

    # Fetch data
    data = yf.download(nasdaq_ticker, start=start_date, end=end_date)

    return data

@st.cache_data
def get_combined_data():
    # Load existing data
    nasdaq_data = pd.read_csv('nasdaq_data.csv', index_col=0)

    # Get the latest date from the collected data
    latest_date = pd.to_datetime(nasdaq_data.index[-1]).date()
    today = datetime.today().date()

    start_date = latest_date.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    nasdaq_data_new = get_nasdaq_data(start_date, end_date)

    combined_data = pd.concat([nasdaq_data, nasdaq_data_new])

    # Calculate rolling averages
    combined_data['ra200'] = combined_data['Close'].rolling(window=200).mean()
    combined_data['ra100'] = combined_data['Close'].rolling(window=100).mean()
    combined_data['ra400'] = combined_data['Close'].rolling(window=400).mean()

    # Save the combined data
    combined_data.to_csv('nasdaq_data.csv')

    return combined_data

def main():
    st.title("NASDAQ Data")

    combined_data = get_combined_data()

    # Plot the daterange
    max_line = len(combined_data)

    start = st.slider("Start Day", min_value=1, max_value=max_line-200, value=1000, step=1)
    end = st.slider("End Day", min_value=start+200, max_value=max_line, value=1200, step=1)

    date_range_zoom = combined_data.iloc[start:end]
    fig, ax = plt.subplots(figsize=(20, 6))
    date_range_zoom.plot(y=['Close', 'ra200', 'ra100', 'ra400'], legend=True, ax=ax)
    st.pyplot(fig)

if __name__ == "__main__":
    main()
