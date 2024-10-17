import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import numpy as np
import datetime as dt

# Set the page layout to wide
st.set_page_config(layout="wide", page_title=f"ETF Search")
# Step 1: Set up the Streamlit interface
st.title("ETF Search")
# Inputs for strategy parameters
c1, c2, c3, c4 = st.columns(4)
with c1:
    tickers = st.text_input("Enter ticker symbols (comma-separated):", value="AAPL,GOOG,AMZN")
    ticker_list = tickers.split(",")
with c2:
    start_date = st.date_input("Select start date", value=dt.date(2019, 1, 1), min_value=dt.date(2010, 1, 1), max_value=dt.date.today())  # replace with your desired start date
with c3:
    end_date = st.date_input("Select end date", value=dt.date.today(), min_value=dt.date(2010, 1, 1), max_value=dt.date.today())  # replace with your desired start date
# List of index symbols


# Initialize an empty figure
fig = go.Figure()

# Function to calculate CAGR
def calculate_cagr(data):
    n = len(data)
    return ((data + 1).prod()**(1/n) - 1) * 100

# Loop through the index symbols
for ticker in ticker_list:
    
    # Step 2: Fetch historical data
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    data = data.drop(['Volume', 'Adj Close'], axis=1)

    # Normalize closing prices to start at 1
    data['Close'] = data['Close'] / data['Close'][0]

    # Calculate annual returns
    data['Returns'] = data['Close'].pct_change() * 100

    # Calculate Standard Deviation  
    std_dev = data['Returns'].std() * np.sqrt(252)
    st.write(f"Standard Deviation for {ticker}: {std_dev:.2f}%")
    
    # Add a scatter trace (line) for closing prices of each index
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name= ticker
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