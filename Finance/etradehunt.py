import streamlit as st
import yfinance as yf
import plotly.graph_objs as go

# List of index symbols
index_symbols = ["^IXIC", "^GSPC", "^DJI"]

# Loop through the index symbols
for index_symbol in index_symbols:
    # Fetch historical data for the current index
    data = yf.download(index_symbol, period="5y", interval="1d")

    # Create a candlestick chart
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candlesticks"
    )])

    # Set chart layout and title
    fig.update_layout(
        title=f"{index_symbol} - 5-Year Candlestick Chart",
        xaxis_title='',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        plot_bgcolor='lightgray',
        width=800,
        height=600
    )

    # Display the chart using Streamlit
    st.write(fig)
