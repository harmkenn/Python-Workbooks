import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# Function to fetch data
def fetch_data(ticker):
    data = yf.download(ticker, start="2020-01-01")
    return data

# Function to calculate Bollinger Bands
def calculate_bollinger_bands(data):
    data['SMA'] = data['Close'].rolling(window=20).mean()
    data['Upper Band'] = data['SMA'] + 1.5 * data['Close'].rolling(window=20).std()
    data['Lower Band'] = data['SMA'] - 1.5 * data['Close'].rolling(window=20).std()
    return data

# Function to plot data with Bollinger Bands using Plotly
def plot_bollinger_bands(data):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='blue')))
    #fig.add_trace(go.Scatter(x=data.index, y=data['SMA'], name='Simple Moving Average', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Upper Band'], name='Upper Bollinger Band', line=dict(color='red',dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Lower Band'], name='Lower Bollinger Band', line=dict(color='green',dash='dash')))

    fig.update_layout(title='TQQQ Bollinger Bands', xaxis_title='Date', yaxis_title='Price', template='plotly_dark')
    st.plotly_chart(fig)

# Main app
st.title('TQQQ Bollinger Bands Analysis')
ticker = 'TQQQ'

data = fetch_data(ticker)
data = calculate_bollinger_bands(data)
plot_bollinger_bands(data)

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# Function to fetch data
def fetch_data(ticker):
    data = yf.download(ticker, start="2020-01-01")
    return data

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

# Function to plot data with RSI using Plotly
def plot_rsi(data):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='orange')))

    fig.update_layout(title='TQQQ Relative Strength Index (RSI)', xaxis_title='Date', yaxis_title='Price/RSI', template='plotly_dark')
    st.plotly_chart(fig)

# Main app
st.title('TQQQ RSI Analysis')
ticker = 'TQQQ'

data = fetch_data(ticker)
data = calculate_rsi(data)
plot_rsi(data)

