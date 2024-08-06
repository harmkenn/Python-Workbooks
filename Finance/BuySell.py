import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import streamlit as st

# Read the existing nasdaq_data.csv file
nasdaq_data = pd.read_csv('nasdaq_data.csv', index_col=0, skiprows=lambda x: x >= len(nasdaq_data) - 5)

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

    # Create a date range
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Fetch data
    data = yf.download(nasdaq_ticker, start=start_date, end=end_date)

    return data

@st.cache_data
def load_data():
# Get the latest date from the collected data
    today = datetime.today().date()

    start_date = latest_date.strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    nasdaq_data_new = get_nasdaq_data(start_date, end_date)

    combined_data = pd.concat([nasdaq_data, nasdaq_data_new])
    combined_data.to_csv('nasdaq_data.csv')


    combined_data['Date2'] = combined_data.index
    combined_data.set_index('Date2', inplace=True)

    return combined_data


def plot_data(data):
    fig, ax = plt.subplots(figsize=(20, 6))
    data.plot(y=['Close', 'ra200', 'ra100', 'ra400'], legend=True, ax=ax)
    st.pyplot(fig)

def main():
    st.title("NASDAQ Composite Index")

    combined_data = load_data()

    # Slice the DataFrame to include only the last 200 days
    last_200_days = combined_data.tail(2000)

    plot_data(last_200_days)

    st.write(combined_data.head())
    st.write(combined_data.tail())

if __name__ == "__main__":
    main()
