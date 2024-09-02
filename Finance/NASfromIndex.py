import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from sklearn.ensemble import GradientBoostingRegressor


# Set the page layout to wide
st.set_page_config(layout="wide")


# Define the time range for the last 90 days
end_date = datetime.now()
start_date = end_date - timedelta(days=90)


# Fetch data from Yahoo Finance
@st.cache_data
def fetch_data(ticker):
    # Fetch daily data
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    return data


# Extract price at close and rename the column to the ticker
def extract_price(data, ticker):
    return data[['Close']].rename(columns={'Close': ticker})


# Main function to display the data
def main():
    st.title('Prediction of NASDAQ (^IXIC) From (^FTSE), NIKKEI (^N225), DAX (^GDAXI), and Shanghai Composite (000001.SS)')


    # Initialize an empty DataFrame
    combined_data = pd.DataFrame()

    # Fetch and combine data for NIKKEI
    nikkei_data = fetch_data('^N225')
    if not nikkei_data.empty:
        nikkei_data = extract_price(nikkei_data, '^N225')
        combined_data = pd.concat([combined_data, nikkei_data], axis=1)


    # Fetch and combine data for Shanghai Composite
    ssec_data = fetch_data('000001.SS')
    if not ssec_data.empty:
        ssec_data = extract_price(ssec_data, '000001.SS')
        combined_data = pd.concat([combined_data, ssec_data], axis=1)

    # Fetch and combine data for DAX
    dax_data = fetch_data('^GDAXI')
    if not dax_data.empty:
        dax_data = extract_price(dax_data, '^GDAXI')
        combined_data = pd.concat([combined_data, dax_data], axis=1)


    # Fetch and combine data for FTSE
    ftse_data = fetch_data('^FTSE')
    if not ftse_data.empty:
        ftse_data = extract_price(ftse_data, '^FTSE')
        combined_data = pd.concat([combined_data, ftse_data], axis=1)


    # Fetch and combine data for NASDAQ
    nasdaq_data = fetch_data('^IXIC')
    if not nasdaq_data.empty:
        nasdaq_data = extract_price(nasdaq_data, '^IXIC')
        combined_data = pd.concat([combined_data, nasdaq_data], axis=1)


    # Compute the percent change for each index
    percent_change = combined_data.pct_change().rename(columns=lambda x: f'{x} % Change')


    # Concatenate the percent change data with the closing prices
    combined_data = pd.concat([combined_data, percent_change], axis=1)


    # Drop rows with NaN values (usually the first row)
    combined_data = combined_data.dropna()


    # Define the features (X) and the target (y)
    X = combined_data[['^N225 % Change', '000001.SS % Change','^GDAXI % Change', '^FTSE % Change' ]]
    y = combined_data['^IXIC % Change']


    # Initialize the GradientBoostingRegressor model
    model = GradientBoostingRegressor()


    # Train the model on the entire dataset
    model.fit(X, y)


    # Predict on the entire dataset
    y_pred = model.predict(X)


    # Display the actual and predicted values
    comparison = pd.DataFrame({'^N225 % Change':X['^N225 % Change'], '000001.SS % Change':X['000001.SS % Change'], '^GDAXI % Change':X['^GDAXI % Change'],'^FTSE % Change':X['^FTSE % Change'], 'Predicted ^IXIC % Change': y_pred, 'Actual ^IXIC % Change': y})
    st.write("Actual vs Predicted NASDAQ Percent Change:")
    st.dataframe(comparison, use_container_width=True)


    # User inputs for today's FTSE, NIKKEI, DAX, and Shanghai Composite percent changes
    st.subheader("Predict Today's NASDAQ Percent Change")


    nikkei_today = st.number_input("Enter today's NIKKEI % Change:", format="%.5f", value=0.0, step=0.00001)
    ssec_today = st.number_input("Enter today's Shanghai Composite % Change:", format="%.5f", value=0.0, step=0.00001)
    dax_today = st.number_input("Enter today's DAX % Change:", format="%.5f", value=0.0, step=0.00001)
    ftse_today = st.number_input("Enter today's FTSE % Change:", format="%.5f", value=0.0, step=0.00001)
    
    # Predict today's NASDAQ % Change based on user inputs
    if st.button("Predict NASDAQ % Change"):
        today_prediction = model.predict([[nikkei_today, ssec_today, dax_today, ftse_today]])
        st.write(f"Predicted NASDAQ % Change for today: {today_prediction[0]:.5f}%")


if __name__ == "__main__":
    main()