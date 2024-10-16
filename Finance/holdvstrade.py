import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import datetime as dt

# Set the page layout to wide
st.set_page_config(layout="wide", page_title=f"Hold vs. Trade Strategy")
# Step 1: Set up the Streamlit interface
st.title("Buy and Hold vs Intraday Trading Strategy")

# Inputs for strategy parameters
c1, c2, c3, c4 = st.columns(4)
with c1:
    ticker = st.text_input("Ticker", "TQQQ")
    chunk = st.number_input("Chunk Size", min_value=.05, max_value=1.1, value=.25, step=.05, format="%.3f")
with c2:
    start_cash = st.number_input("Starting Cash ($)", min_value=0, value=100000, step=10000)
    money_in_shares = st.number_input("Money in Shares", min_value=0, value=100000, step=10000)
with c3:
    sell_pct = st.number_input("Sell Percentage Trigger (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
    buy_pct = st.number_input("Buy Percentage Trigger (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
with c4:
    start_date = st.date_input("Select start date", value=dt.date(2019, 1, 1), min_value=dt.date(2010, 1, 1), max_value=dt.date.today())  # replace with your desired start date
    end_date = st.date_input("Select end date", value=dt.date.today(), min_value=dt.date(2010, 1, 1), max_value=dt.date.today())  # replace with your desired start date

# Step 2: Fetch historical data
data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
data = data.drop(['Volume', 'Adj Close'], axis=1)

# Step 3: Implement the Buy and Hold Strategy
def buy_and_hold(data,  bh_num_shares):
    data['Hold Value'] = bh_num_shares * data['Close']
    return data

# Step 4: Implement the Intraday Trading Strategy
def intraday_trading(data, start_cash, num_shares, sell_pct=2, buy_pct=2):
    cash = start_cash
    shares = num_shares
    
    for i in range(1, len(data)):
        high = data['High'].iloc[i]
        low = data['Low'].iloc[i]
        close = data['Close'].iloc[i-1]  # Previous close
        
        # Sell shares on spike
        if (high - close) / close * 100 > sell_pct:
            shares_to_sell = shares * chunk  # Sell 10% of shares
            cash += shares_to_sell * high
            shares -= shares_to_sell
        
        # Buy shares on dip
        if (close - low) / close * 100 > buy_pct:
            shares_to_buy = cash / low * chunk  # Buy 10% of cash value
            cash -= shares_to_buy * low
            shares += shares_to_buy
        
        # Track portfolio value
        data.loc[data.index[i], 'Trade Value'] = shares * close
        data.loc[data.index[i], 'Cash'] = cash
        data.loc[data.index[i], 'Total Value Trade'] = data['Trade Value'].iloc[i] + cash
    
    return data

# Step 5: Run both strategies
bh_num_shares = (start_cash + money_in_shares) / data['Close'].iloc[0]  # Initial shares
idt_num_shares = money_in_shares / data['Close'].iloc[0]  # Initial shares
buy_hold_result = buy_and_hold(data.copy(), bh_num_shares)

trade_result = intraday_trading(data.copy(), start_cash, idt_num_shares, sell_pct=sell_pct, buy_pct=buy_pct)

# Step 7: Display Data Summary
st.subheader("Portfolio Value Summary")
st.write("Buy and Hold Final Value: ${:,.2f}".format(buy_hold_result['Hold Value'].iloc[-1]))
st.write("Intraday Trading Final Value: ${:,.2f}".format(trade_result['Total Value Trade'].iloc[-1]))

# Step 6: Plot the performance comparison
st.subheader("Strategy Performance Comparison")

fig = go.Figure()

fig.add_trace(go.Scatter(x=buy_hold_result.index, y=buy_hold_result['Hold Value'],
                          mode='lines', name='Buy and Hold', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=trade_result.index, y=trade_result['Total Value Trade'],
                          mode='lines', name='Intraday Trading', line=dict(color='green')))

fig.update_layout(
    title=f"Buy and Hold vs Intraday Trading with {ticker}",
    xaxis_title="Date",
    yaxis_title="Portfolio Value ($)",
    legend_title_text="Strategy",
)

st.write(fig)

st.write(buy_hold_result)


