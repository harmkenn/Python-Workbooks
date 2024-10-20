import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from numpy import sqrt, maximum, minimum
import datetime as dt

# Set the page layout to wide
st.set_page_config(layout="wide", page_title=f"Buy Sell Hold Strategy")

# Set up the Streamlit interface
st.title("Buy Sell Hold Strategy")

# Set the ticker symbol
c1, c2, c3, c4 = st.columns(4)
with c1:
    ticker = st.selectbox("Select Ticker", ['DGRO','EDEN','GBTC','INCO','KBWP','SMIN','SOXL','SPXL','SSO','TECL','TQQQ','UPRO'])
with c2:
    bound = st.number_input("Bound", min_value=0.0, max_value=10.0, value=1.1, step=0.1)
with c4:
    start_date = st.date_input("Select start date", value=dt.date(2020, 1, 1), min_value=dt.date(2010, 1, 1), max_value=dt.date.today())  # replace with your desired start date
    end_date = st.date_input("Select end date", value=dt.date.today(), min_value=dt.date(2010, 1, 1), max_value=dt.date.today())  # replace with your desired start date

# Fetch historical data for the past year
data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
data = data.drop(['Volume', 'Adj Close'], axis=1)

# Calculate moving averages
data['50_MA'] = data['Close'].rolling(window=50).mean()
data['50_SD'] = data['Close'].rolling(window=50).std()
data['200_MA'] = data['Close'].rolling(window=200).mean()
data['UB'] = maximum(data['50_MA'], data['200_MA']) + data['50_SD'] * bound
data['LB'] = minimum(data['50_MA'], data['200_MA']) - data['50_SD'] * bound

# Calculate annual returns
data['Returns'] = data['Close'].pct_change() * 100

# Calculate Standard Deviation
std_dev = data['Returns'].std() * sqrt(252)

# Calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

data = calculate_rsi(data)

# Calculate MFI
def calculate_mfi(data, window=14):
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    money_flow = typical_price * data['Volume']
    positive_flow = (money_flow.where(typical_price > typical_price.shift(1), 0)).rolling(window=window).sum()
    negative_flow = (money_flow.where(typical_price < typical_price.shift(1), 0)).rolling(window=window).sum()
    money_flow_index = 100 - (100 / (1 + (positive_flow / negative_flow)))
    data['MFI'] = money_flow_index
    return data

data = calculate_mfi(data)

# Display final RSI and MFI
with c1:
    st.write(f"Final RSI (30,70) for {ticker}: {data['RSI'].iloc[-1]:.2f}")
    st.write(f"Final MFI (20,80) for {ticker}: {data['MFI'].iloc[-1]:.2f}")

# Display Standard Deviation and Buy/Sell levels
with c2:
    st.write(f"Standard Deviation for {ticker}: {std_dev:.2f}%")
with c3:
    st.write(f'Sell at: {data["UB"].iloc[-1]:.2f}')
    st.write(f'High: {data["High"].iloc[-1]:.2f}')
    st.write(f'Low: {data["Low"].iloc[-1]:.2f}')
    st.write(f'Buy at: {data["LB"].iloc[-1]:.2f}')

# Drop the first 200 rows
data = data.iloc[200:].copy()

# Create the OHLC chart
fig = go.Figure()

# Add OHLC data
fig.add_trace(go.Ohlc(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='OHLC'))

# Add moving averages
fig.add_trace(go.Scatter(x=data.index, y=data['50_MA'], mode='lines', name='50-Day MA', line=dict(color='blue', width=1)))
fig.add_trace(go.Scatter(x=data.index, y=data['200_MA'], mode='lines', name='200-Day MA', line=dict(color='red', width=1)))
fig.add_trace(go.Scatter(x=data.index, y=data['UB'], mode='lines', name='Sell Line', line=dict(color='green', width=1, dash='dash')))
fig.add_trace(go.Scatter(x=data.index, y=data['LB'], mode='lines', name='Buy Line', line=dict(color='purple', width=1, dash='dash')))

# Update layout
fig.update_layout(title=f'OHLC Chart for {ticker} with 50 & 200 Day Moving Averages',
                  xaxis_title='Date',
                  yaxis_title='Price',
                  xaxis_rangeslider_visible=True)

# Streamlit app layout
st.plotly_chart(fig)
