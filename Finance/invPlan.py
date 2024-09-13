import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# Define the ETF tickers and time period
tickers = ["TQQQ", "SQQQ"]
start_date = datetime.today() - timedelta(days=5*365)
end_date = datetime.today()

# Create a Streamlit app
st.title("ETF Price Collector")

# Download the ETF prices
st.write("Downloading ETF prices...")
data = yf.download(tickers, start=start_date, end=end_date)

# Reset the index and rename the columns
df = data.reset_index()
df = df.rename(columns={'level_0': 'Date', 'level_1': 'Ticker'})


# Display the DataFrame
st.write("ETF Prices:")
st.write(df)

# Make the DataFrame downloadable
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False)

csv = convert_df(df)

st.download_button(
    label="Download ETF Prices as CSV",
    data=csv,
    file_name="etf_prices.csv",
    mime="text/csv",
)