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

    # Normalize closing prices (scale between 0 and 1)
    data['Close'] = (data['Close'] - data['Close'].min()) / (data['Close'].max() - data['Close'].min())

    # Add a scatter trace (line) for closing prices of each index
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name=index_symbol
    ))

# Set chart layout and title
fig.update_layout(
    title="Stock Indices - 5-Year Closing Prices (Normalized)",
    xaxis_title='',
    yaxis_title='Normalized Price',
    xaxis_rangeslider_visible=False,
    plot_bgcolor='lightgray',
    width=800,
    height=600
)

# Display the chart using Streamlit
st.write(fig)
