import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from sklearn.ensemble import GradientBoostingRegressor

# Define the time range for the last 60 days
end_date = datetime.now()
start_date = end_date - timedelta(days=60)

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
    st.title('Prediction of NASDAQ (^IXIC) Percent Change using FTSE (^FTSE) and NIKKEI (^N225)')

    # Initialize an empty DataFrame
    combined_data = pd.DataFrame()

    # Fetch and combine data for NASDAQ
    nasdaq_data = fetch_data('^IXIC')
    if not nasdaq_data.empty:
        nasdaq_data = extract_price(nasdaq_data, '^IXIC')
        combined_data = pd.concat([combined_data, nasdaq_data], axis=1)

    # Fetch and combine data for FTSE
    ftse_data = fetch_data('^FTSE')
    if not ftse_data.empty:
        ftse_data = extract_price(ftse_data, '^FTSE')
        combined_data = pd.concat([combined_data, ftse_data], axis=1)

    # Fetch and combine data for NIKKEI
    nikkei_data = fetch_data('^N225')
    if not nikkei_data.empty:
        nikkei_data = extract_price(nikkei_data, '^N225')
        combined_data = pd.concat([combined_data, nikkei_data], axis=1)

    # Compute the percent change for each index
    percent_change = combined_data.pct_change().rename(columns=lambda x: f'{x} % Change')

    # Concatenate the percent change data with the closing prices
    combined_data = pd.concat([combined_data, percent_change], axis=1)

    # Drop rows with NaN values (usually the first row)
    combined_data = combined_data.dropna()

    # Define the features (X) and the target (y)
    X = combined_data[['^FTSE % Change', '^N225 % Change']]
    y = combined_data['^IXIC % Change']

    # Initialize the GradientBoostingRegressor model
    model = GradientBoostingRegressor()

    # Train the model on the entire dataset
    model.fit(X, y)

    # Predict on the entire dataset
    y_pred = model.predict(X)

    # Display the actual and predicted values
    comparison = pd.DataFrame({'Actual ^IXIC % Change': y, 'Predicted ^IXIC % Change': y_pred})
    st.write("Actual vs Predicted NASDAQ Percent Change:")
    st.dataframe(comparison)

    # User inputs for today's FTSE and NIKKEI percent changes
    st.subheader("Predict Today's NASDAQ Percent Change")
    ftse_today = st.number_input("Enter today's FTSE % Change:", format="%.5f", value=0.0, step=0.00001)
    nikkei_today = st.number_input("Enter today's NIKKEI % Change:", format="%.5f", value=0.0, step=0.00001)

    # Predict today's NASDAQ % Change based on user inputs
    if st.button("Predict NASDAQ % Change"):
        today_prediction = model.predict([[ftse_today, nikkei_today]])
        st.write(f"Predicted NASDAQ % Change for today: {today_prediction[0]:.5f}%")

if __name__ == "__main__":
    main()
