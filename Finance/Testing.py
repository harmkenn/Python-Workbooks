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

# Function to simulate RSI trading strategy with delayed signals
def rsi_strategy(data):
    buy_price = None
    sell_price = None
    returns = 1
    buy_and_hold_returns = data['Close'][-1] / data['Close'][0]
    
    for i in range(1, len(data)):
        if data['RSI'][i] < 30 and data['RSI'][i-1] >= 30 and buy_price is None:
            buy_price = data['Close'][i]
        elif data['RSI'][i] > 70 and data['RSI'][i-1] <= 70 and buy_price is not None:
            sell_price = data['Close'][i]
            returns *= (sell_price / buy_price)
            buy_price = None
    
    # If there's a leftover buy that wasn't sold
    if buy_price is not None:
        returns *= (data['Close'][-1] / buy_price)
    
    return returns, buy_and_hold_returns

# Function to plot RSI and prices using Plotly
def plot_rsi(data):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='orange')))

    fig.update_layout(title='TQQQ Relative Strength Index (RSI)', xaxis_title='Date', yaxis_title='Price/RSI', template='plotly_dark')
    st.plotly_chart(fig)

# Main app
st.title('TQQQ RSI Trading Strategy Simulation')
ticker = 'TQQQ'

data = fetch_data(ticker)
data = calculate_rsi(data)

# Run simulation
rsi_returns, buy_and_hold_returns = rsi_strategy(data)
plot_rsi(data)

# Display results
st.write(f"RSI Trading Strategy Returns: {rsi_returns:.2f}")
st.write(f"Buy and Hold Strategy Returns: {buy_and_hold_returns:.2f}")
