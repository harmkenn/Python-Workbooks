import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import numpy as np

# List of index symbols
index_symbols = ["^IXIC",'AMAGX','BPTRX','DXQLX','EILGX','FADTX','FKDNX','FSELX','FSHOX','FSPTX','JAGTX','PGTAX','PRDGX','RMQHX','ROGSX','SMPIX','SMPSX','UOPIX','SQQQ','QLD']

# Initialize an empty figure
fig = go.Figure()

# Function to calculate CAGR
def calculate_cagr(data):
    n = len(data)
    return ((data + 1).prod()**(1/n) - 1) * 100

# Loop through the index symbols
for index_symbol in index_symbols:
    # Fetch historical data for the current index
    data = yf.download(index_symbol, period="5y", interval="1d")

    # Normalize closing prices to start at 1
    data['Close'] = data['Close'] / data['Close'][0]

    # Calculate annual returns
    data['Returns'] = data['Close'].pct_change() * 100

    # Calculate Standard Deviation  
    std_dev = data['Returns'].std() * np.sqrt(252)
    st.write(f"Standard Deviation for {index_symbol}: {std_dev:.2f}%")
    
    # Add a scatter trace (line) for closing prices of each index
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name=index_symbol
    ))

# Set chart layout and title
fig.update_layout(
    title="Stock Indices - 5-Year Closing Prices (Normalized to Start at 1)",
    xaxis_title='',
    yaxis_title='Normalized Price',
    xaxis_rangeslider_visible=False,
    plot_bgcolor='white',  # Change plot background color to white
    paper_bgcolor='white', # Change the entire figure background color to white
    width=800,
    height=600
)

# Display the chart using Streamlit
st.write(fig)

st.write()
