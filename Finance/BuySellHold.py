import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from numpy import sqrt, maximum, minimum

# Set the page layout to wide
st.set_page_config(layout="wide", page_title=f"Buy Sell Hold Strategy")

# Step 1: Set up the Streamlit interface
st.title("Buy Sell Hold Strategy")

# Set the ticker symbol
c1,c2,c3,c4 = st.columns(4)
with c1:
    ticker = st.selectbox("Select Ticker", ["TQQQ", "SOXL", "DGRO"])

# Fetch historical data for the past year
data = yf.download(ticker, period='5y', interval='1d')

# Calculate moving averages
data['50_MA'] = data['Close'].rolling(window=50).mean()
data['50_SD'] = data['Close'].rolling(window=50).std()
data['200_MA'] = data['Close'].rolling(window=200).mean()
data['UB'] = maximum(data['50_MA'],data['200_MA']) + data['50_SD']*1.5
data['LB'] = minimum(data['50_MA'],data['200_MA']) - data['50_SD']*1.5

# Calculate annual returns
data['Returns'] = data['Close'].pct_change() * 100

# Calculate Standard Deviation  
std_dev = data['Returns'].std() * sqrt(252)
with c2:
    st.write(f"Standard Deviation for {ticker}: {std_dev:.2f}%")
with c3:
    st.write(f'Sell at: {data["UB"].iloc[-1]:.2f}')
    st.write(f'High: {data["High"].iloc[-1]:.2f}')
with c4:
    st.write(f'Buy at: {data["LB"].iloc[-1]:.2f}')
    st.write(f'Low: {data["Low"].iloc[-1]:.2f}')

# Create the OHLC chart
fig = go.Figure()

# Add OHLC data
fig.add_trace(go.Ohlc(x=data.index,
                       open=data['Open'],
                       high=data['High'],
                       low=data['Low'],
                       close=data['Close'],
                       name='OHLC'))

# Add moving averages
fig.add_trace(go.Scatter(x=data.index, y=data['50_MA'], mode='lines', name='50-Day MA', line=dict(color='blue', width=1)))
fig.add_trace(go.Scatter(x=data.index, y=data['200_MA'], mode='lines', name='200-Day MA', line=dict(color='red', width=1)))
fig.add_trace(go.Scatter(x=data.index, y=data['UB'], mode='lines', name='Sell Line', line=dict(color='green', width=1, dash='dash')))
fig.add_trace(go.Scatter(x=data.index, y=data['LB'], mode='lines', name='Buy Line', line=dict(color='green', width=1, dash='dash')))

# Update layout
fig.update_layout(title=f'OHLC Chart for {ticker} with 50 & 200 Day Moving Averages',
                  xaxis_title='Date',
                  yaxis_title='Price',
                  xaxis_rangeslider_visible=True)

# Streamlit app layout
st.plotly_chart(fig)

