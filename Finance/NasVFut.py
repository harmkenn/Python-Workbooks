import yfinance as yf
import pandas as pd
import streamlit as st

# Define the symbol and the time period
symbol = "NQ=F"
period = "1mo"
interval = "1m"  # 1-minute interval to capture precise times

# Download intraday data
futures_intraday = yf.download(symbol, period=period, interval=interval)

# Localize the index to UTC and then convert to Eastern Time (EDT)
futures_intraday.index = futures_intraday.index.tz_localize('UTC').tz_convert('US/Eastern')

# Filter data for 01:30 and 09:30 EDT
prices_0130 = futures_intraday.between_time("01:30", "01:30")
prices_0930 = futures_intraday.between_time("09:30", "09:30")

# Combine the data for easier viewing
combined_prices = pd.DataFrame({
    '01:30 EDT Open': prices_0130['Open'],
    '09:30 EDT Close': prices_0930['Close']
})

# Display the data using Streamlit
st.write(combined_prices)
