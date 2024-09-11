import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt

etf_symbol = "TQQQ"
start_date = pd.Timestamp.today() - pd.Timedelta(days=5)
end_date = pd.Timestamp.today()
interval = "1m"  # 1-minute interval

ticker = yf.Ticker(etf_symbol)
data = ticker.history(start=start_date, end=end_date, interval=interval)

# Create a DataFrame with the desired columns
df = data[['Open', 'High', 'Low', 'Close']]

# Group the data by date and create a boxplot
df.groupby(df.index.date).boxplot()

# Display the plot in Streamlit
st.pyplot()

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
    nasdaq_ticker = ["^IXIC"]

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
    #st.write(nasdaq_data_new)
    # Calculate rolling averages
    nasdaq_data_new['ra100'] = nasdaq_data_new['Close'].rolling(window=100).mean()
    nasdaq_data_new['ra200'] = nasdaq_data_new['Close'].rolling(window=200).mean()
    nasdaq_data_new['ra400'] = nasdaq_data_new['Close'].rolling(window=400).mean()

    

    # Save the new data
    nasdaq_data_new.to_csv('Finance/nasdaq_data.csv')

    return nasdaq_data_new

def main():
    st.title("NASDAQ Data")

    combined_data = get_combined_data()

    # Plot the daterange
    max_line = len(combined_data)

    #start = st.slider("Start Day", min_value=1, max_value=max_line-200, value=1, step=1)
    #end = st.slider("End Day", min_value=start+200, max_value=max_line, value=max_line, step=1)

    date_range_zoom = combined_data.iloc[1:max_line]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['ra100'], name='RA100', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['ra200'], name='RA200', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))
    
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['ra400'], name='RA400', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))
    fig.add_trace(go.Scatter(x=date_range_zoom.index, y=date_range_zoom['Close'], name='Close', hovertemplate='Date: %{x}<br>Price: %{y:.2f}'))

    st.plotly_chart(fig, use_container_width=True)
   
    st.write('PE100: '+str(combined_data.iloc[-1]['Close']/combined_data.iloc[-1]['ra100']))
    st.write('PE200: '+str(combined_data.iloc[-1]['Close']/combined_data.iloc[-1]['ra200']))
    st.write('PE400: '+str(combined_data.iloc[-1]['Close']/combined_data.iloc[-1]['ra400']))

# List of index symbols
index_symbols = ["^IXIC",'AMAGX','BPTRX','DXQLX','EILGX','FADTX','FKDNX','FSELX','FSHOX','FSPTX','JAGTX','PGTAX','PRDGX','RMQHX','ROGSX','SMPIX','SMPSX','UOPIX','SQQQ','TQQQ']

# Initialize an empty figure
fig = go.Figure()

# Function to calculate CAGR
def calculate_cagr(data):
    n = len(data)
    return ((data + 1).prod()**(1/n) - 1) * 100

# Loop through the index symbols
for index_symbol in index_symbols:
    # Fetch historical data for the current index
    data = yf.download(index_symbol, period="5y", interval="1d")

    # Normalize closing prices to start at 1
    data['Close'] = data['Close'] / data['Close'][0]

    # Calculate annual returns
    data['Returns'] = data['Close'].pct_change() * 100

    # Calculate Standard Deviation  
    std_dev = data['Returns'].std() * np.sqrt(252)
    st.write(f"Standard Deviation for {index_symbol}: {std_dev:.2f}%")

    # Add a scatter trace (line) for closing prices of each index
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name=index_symbol
    ))

# Set chart layout and title
fig.update_layout(
    title="Stock Indices - 5-Year Closing Prices (Normalized to Start at 1)",
    xaxis_title='',
    yaxis_title='Normalized Price',
    xaxis_rangeslider_visible=False,
    plot_bgcolor='white',  # Change plot background color to white
    paper_bgcolor='white', # Change the entire figure background color to white
    width=800,
    height=600
)

# Display the chart using Streamlit
st.write(fig)
if __name__ == "__main__":
    main()
