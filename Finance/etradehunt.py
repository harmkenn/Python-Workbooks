import streamlit as st
import yfinance as yf
import plotly.graph_objs as go

# List of index symbols
index_symbols = ["^IXIC", "^GSPC", "^DJI"]

# Initialize an empty figure
fig = go.Figure()

# Loop through the index symbols
for index_symbol in index_symbols:
    # Fetch historical data for the current index
    data = yf.download(index_symbol, period="5y", interval="1d")

    # Add a candlestick trace for each index
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=index_symbol
    ))

# Set chart layout and title
fig.update_layout(
    title="Stock Indices - 5-Year Candlestick Chart",
    xaxis_title='',
    yaxis_title='Price',
    xaxis_rangeslider_visible=False,
    plot_bgcolor='lightgray',
    width=800,
    height=600
)

# Display the chart using Streamlit
st.write(fig)
