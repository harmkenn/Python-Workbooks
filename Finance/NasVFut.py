import yfinance as yf
import pandas as pd
import streamlit as st

# Fetch NQ=F data for the last month
nq_data = yf.download('NQ=F', period='1mo', interval='1m')

# Convert the index to a DatetimeIndex and localize to UTC
nq_data.index = pd.to_datetime(nq_data.index).tz_localize('UTC')

# Filter data for 05:30 UTC (Open) and 13:30 UTC (Close)
open_prices = nq_data.between_time('05:30', '05:31')['Open']
close_prices = nq_data.between_time('13:30', '13:31')['Close']

# Combine the data into a single DataFrame
filtered_data = pd.DataFrame({
    'Date': open_prices.index.date,
    '05:30 UTC Open': open_prices.values,
    '13:30 UTC Close': close_prices.values
})

# Display the filtered data in Streamlit
st.title('NQ=F Open and Close Prices')
st.write(filtered_data)
