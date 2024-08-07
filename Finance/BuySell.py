import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

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
    nasdaq_data = pd.read_csv('Finance/nasdaq_data.csv', index_col=0)

    # Get the latest date from the collected data
    latest_date = pd.to_datetime(nasdaq_data.index[-1]).date()
    today = datetime.today().date()

    start_date = latest_date
    end_date = today

    nasdaq_data_new = get_nasdaq_data(start_date, end_date)

    combined_data = pd.concat([nasdaq_data, nasdaq_data_new])

    # Calculate rolling averages
    combined_data['ra200'] = combined_data['Close'].rolling(window=200).mean()
    combined_data['ra100'] = combined_data['Close'].rolling(window=100).mean()
    combined_data['ra400'] = combined_data['Close'].rolling(window=400).mean()

    combined_data['PE'] = combined_data['Close'] / combined_data['ra200']

    # Save the combined data
    combined_data.to_csv('Finance/nasdaq_data.csv')

    return combined_data

def main():
    st.title("NASDAQ Data")

    combined_data = get_combined_data()

    # Plot the daterange
    max_line = len(combined_data)

    start = st.slider("Start Day", min_value=1, max_value=max_line-200, value=1, step=1)
    end = st.slider("End Day", min_value=start+200, max_value=max_line, value=max_line, step=1)

    date_range_zoom = combined_data.iloc[start:end]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['Close'], name='Close', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['ra200'], name='RA200', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['ra100'], name='RA100', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['ra400'], name='RA400', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
