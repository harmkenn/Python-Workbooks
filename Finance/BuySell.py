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
    # Get the current date
    today = datetime.today().date()

    # Calculate the start date 20 years ago
    start_date = today - timedelta(days=20*365)

    # Fetch new data for the last 20 years up to today
    nasdaq_data_new = get_nasdaq_data(start_date, today)

    # Calculate rolling averages
    nasdaq_data_new['ra200'] = nasdaq_data_new['Close'].rolling(window=200).mean()
    nasdaq_data_new['ra100'] = nasdaq_data_new['Close'].rolling(window=100).mean()
    nasdaq_data_new['ra400'] = nasdaq_data_new['Close'].rolling(window=400).mean()

    

    # Save the new data
    nasdaq_data_new.to_csv('Finance/nasdaq_data.csv')

    return nasdaq_data_new

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

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['Close']/date_range_zoom['ra100'], 
        name='PE100', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['Close']/date_range_zoom['ra200'], 
        name='PE200', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['Close']/date_range_zoom['ra400'], 
        name='PE400', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))
    st.plotly_chart(fig, use_container_width=True)
    
    st.write('PE100: '+str(combined_data.iloc[-1]['Close']/combined_data.iloc[-1]['ra100']))
    st.write('PE200: '+str(combined_data.iloc[-1]['Close']/combined_data.iloc[-1]['ra200']))
    st.write('PE400: '+str(combined_data.iloc[-1]['Close']/combined_data.iloc[-1]['ra400']))
if __name__ == "__main__":
    main()
