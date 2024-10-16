import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import datetime as dt

# Set the page layout to wide
st.set_page_config(layout="wide", page_title=f"Investment Plan")

# Define the app title
st.title(f"Investment Plan")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    ticker = st.text_input("Ticker", "SOXL")
with c2:
    inc = st.number_input("Trigger", min_value=0.001, max_value=1.010, value=0.030, step=0.005, format="%.3f")
with c3:
    chunk = st.number_input("Chunk", min_value=.05, max_value=.95, value=.30, step=.05, format="%.3f")
with c4:
    start_date = st.date_input("Select start date", value=dt.date(2022, 1, 1), min_value=dt.date(2010, 1, 1), max_value=dt.date.today())  # replace with your desired start date
with c5:
    end_date = st.date_input("Select end date", value=dt.date.today(), min_value=dt.date(2010, 1, 1), max_value=dt.date.today())  # replace with your desired start date



tqqq_data = yf.download(ticker, start=start_date, end=end_date)

tqqq_data = tqqq_data.drop(['Volume', 'Adj Close'], axis=1)

# Create the OHLC graph
fig = go.Figure(data=[go.Candlestick(
    x=tqqq_data.index,
    open=tqqq_data["Open"],
    high=tqqq_data["High"],
    low=tqqq_data["Low"],
    close=tqqq_data["Close"]
)])
 
# Initialize the starting cash and shares
tqqq_data['Drop'] = 0.0
tqqq_data['Raise'] = 0.0
tqqq_data['Move $'] = 0.0
tqqq_data['Move shares'] = 0
tqqq_data['Cash'] = 100000.00
# Calculate the initial number of shares
start_price = tqqq_data.iloc[0]['Close']
initial_shares = int(100000 / start_price)
tqqq_data['Shares'] = initial_shares
tqqq_data['Buy/Sell'] = ''



# Iterate through each day
for i in range(1, len(tqqq_data)):
    # Initialize cash and shares for the current day
    tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Cash')]
    tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Shares')]

    # Check if the price rose one Trigger
    if tqqq_data.iloc[i, tqqq_data.columns.get_loc('High')] > tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')] * (1+inc):
        # Sell first chunk of the shares
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Raise')] = (tqqq_data.iloc[i, tqqq_data.columns.get_loc('High')]-tqqq_data.iloc[i-1,
                                                                 tqqq_data.columns.get_loc('Close')])/tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')]
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Buy/Sell')] = 'Sell'
        shares_to_sell = int(tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Shares')] * chunk)
        cash_to_receive = shares_to_sell * (tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')] * (1+inc))
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Shares')] - shares_to_sell
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Cash')] + cash_to_receive

    # Check if the price rose two Triggers
    if tqqq_data.iloc[i, tqqq_data.columns.get_loc('High')] > tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')] * (1+2*inc):
        # Sell second chunk of the shares
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Raise')] = (tqqq_data.iloc[i, tqqq_data.columns.get_loc('High')]-tqqq_data.iloc[i-1,
                                                                 tqqq_data.columns.get_loc('Close')])/tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')]
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Buy/Sell')] = 'Sell2'
        shares_to_sell = int(shares_to_sell + tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] * chunk)
        cash_to_receive = shares_to_sell * (tqqq_data.iloc[i, tqqq_data.columns.get_loc('Close')] * (1+2*inc))
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Shares')] - shares_to_sell
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Cash')] + cash_to_receive

    # Check if the price rose three triggers
    if tqqq_data.iloc[i, tqqq_data.columns.get_loc('High')] > tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')] * (1+3*inc):
        # Sell third chunk of the shares
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Raise')] = (tqqq_data.iloc[i, tqqq_data.columns.get_loc('High')]-tqqq_data.iloc[i-1,
                                                                 tqqq_data.columns.get_loc('Close')])/tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')]
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Buy/Sell')] = 'Sell3'
        shares_to_sell = int(shares_to_sell + tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] * chunk)
        cash_to_receive = shares_to_sell * (tqqq_data.iloc[i, tqqq_data.columns.get_loc('Close')] * (1+3*inc))
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Shares')] - shares_to_sell
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Cash')] + cash_to_receive

    # Check if the price dropped one trigger
    if tqqq_data.iloc[i, tqqq_data.columns.get_loc('Low')] < tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')] * (1-inc):
        # Buy shares with first chunk of the available cash
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Drop')] = (tqqq_data.iloc[i, tqqq_data.columns.get_loc('Low')]-tqqq_data.iloc[i-1,
                                                                tqqq_data.columns.get_loc('Close')])/tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')]
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Buy/Sell')] = 'Buy'
        cash_to_spend = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Cash')] * chunk
        shares_to_buy = int(cash_to_spend / (tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')] * (1-inc)))
        cash_to_spend = shares_to_buy * (tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')] * (1-inc))
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Shares')] + shares_to_buy
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Cash')] - cash_to_spend

    # Check if the price dropped two triggers
    if tqqq_data.iloc[i, tqqq_data.columns.get_loc('Low')] < tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')] * (1-2*inc):
        # Buy shares with second chunk of the available cash
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Drop')] = (tqqq_data.iloc[i, tqqq_data.columns.get_loc('Low')]-tqqq_data.iloc[i-1,
                                                                tqqq_data.columns.get_loc('Close')])/tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')]
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Buy/Sell')] = 'Buy2'
        cash_to_spend = cash_to_spend + tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] * chunk
        shares_to_buy = int(cash_to_spend / (tqqq_data.iloc[i, tqqq_data.columns.get_loc('Close')] * (1-2*inc)))
        cash_to_spend = shares_to_buy * (tqqq_data.iloc[i, tqqq_data.columns.get_loc('Close')] * (1-2*inc))
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Shares')] + shares_to_buy
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Cash')] - cash_to_spend

    # Check if the price dropped three triggers
    if tqqq_data.iloc[i, tqqq_data.columns.get_loc('Low')] < tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')] * (1-3*inc):
        # Buy shares with second chunk of the available cash
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Drop')] = (tqqq_data.iloc[i, tqqq_data.columns.get_loc('Low')]-tqqq_data.iloc[i-1,
                                                                tqqq_data.columns.get_loc('Close')])/tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Close')]
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Buy/Sell')] = 'Buy3'
        cash_to_spend = cash_to_spend + tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] * chunk
        shares_to_buy = int(cash_to_spend / (tqqq_data.iloc[i, tqqq_data.columns.get_loc('Close')] * (1-3*inc)))
        cash_to_spend = shares_to_buy * (tqqq_data.iloc[i, tqqq_data.columns.get_loc('Close')] * (1-3*inc))
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Shares')] + shares_to_buy
        tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] = tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Cash')] - cash_to_spend

    tqqq_data.iloc[i, tqqq_data.columns.get_loc('Move $')] = tqqq_data.iloc[i, tqqq_data.columns.get_loc('Cash')] - tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Cash')]
    tqqq_data.iloc[i, tqqq_data.columns.get_loc('Move shares')] = tqqq_data.iloc[i, tqqq_data.columns.get_loc('Shares')] - tqqq_data.iloc[i-1, tqqq_data.columns.get_loc('Shares')]

tqqq_data['value'] = tqqq_data['Shares'] * tqqq_data['Close']
tqqq_data["total"] = tqqq_data["Cash"] + tqqq_data["value"]
tqqq_data['Close%'] = tqqq_data['Close'].pct_change()
tqqq_data['Total%'] = tqqq_data['total'].pct_change()

st.dataframe(tqqq_data.iloc[::-1], width=None, use_container_width=True)

# Add a button to download the data as a CSV
st.download_button(
    label="Download CSV",
    data=tqqq_data.to_csv(index=False),
    file_name="tqqq_data.csv",
    mime="text/csv"
)

# Add the OHLC graph to the Streamlit app

st.plotly_chart(fig, use_container_width=True)

