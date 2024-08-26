import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import numpy as np

# List of index symbols
index_symbols = {"NASDAQ": "^IXIC", "NASDAQ Futures": "NQ=F"}

# Initialize an empty figure
fig = go.Figure()

# Function to calculate CAGR
def calculate_cagr(data):
    n = len(data)
    return ((data + 1).prod()**(1/n) - 1) * 100

# Fetch historical data for the current index and futures
nasdaq_data = yf.download(index_symbols["NASDAQ"], period="5y", interval="1d")
futures_data = yf.download(index_symbols["NASDAQ Futures"], period="5y", interval="1d")

# Calculate returns for day and overnight sessions
nasdaq_data['Returns'] = nasdaq_data['Close'].pct_change() * 100
futures_data['Returns'] = futures_data['Close'].pct_change() * 100

# Calculate day return (previous day's close to current day's close)
nasdaq_data['Day Return'] = nasdaq_data['Close'].pct_change() * 100

# Calculate overnight return (previous day's close to current day's futures open)
nasdaq_data['Overnight Return'] = (futures_data['Open'] / nasdaq_data['Close'].shift(1) - 1) * 100

# Normalize closing prices to start at 1 for both day and overnight sessions
nasdaq_data['Normalized Day'] = nasdaq_data['Close'] / nasdaq_data['Close'][0]
futures_data['Normalized Overnight'] = futures_data['Close'] / futures_data['Close'][0]

# Add traces for both day and overnight normalized prices
fig.add_trace(go.Scatter(
    x=nasdaq_data.index,
    y=nasdaq_data['Normalized Day'],
    mode='lines',
    name="NASDAQ Day"
))

fig.add_trace(go.Scatter(
    x=futures_data.index,
    y=futures_data['Normalized Overnight'],
    mode='lines',
    name="NASDAQ Overnight"
))

# Set chart layout and title
fig.update_layout(
    title="NASDAQ Day vs. NASDAQ Futures Overnight (5-Year Normalized Prices)",
    xaxis_title='Date',
    yaxis_title='Normalized Price',
    xaxis_rangeslider_visible=False,
    plot_bgcolor='white',
    paper_bgcolor='white',
    width=800,
    height=600
)

# Display the chart using Streamlit
st.write(fig)

# Display standard deviations
day_std_dev = nasdaq_data['Day Return'].std() * np.sqrt(252)
overnight_std_dev = nasdaq_data['Overnight Return'].std() * np.sqrt(252)
st.write(f"Standard Deviation for NASDAQ Day: {day_std_dev:.2f}%")
st.write(f"Standard Deviation for NASDAQ Overnight: {overnight_std_dev:.2f}%")
