import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Define the time range for the last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=60)

# Fetch data from Yahoo Finance
@st.cache_data
def fetch_data(ticker):
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    return data

# Extract price at close and rename the column to the ticker
def extract_price(data, ticker):
    return data[['Close']].rename(columns={'Close': ticker})

# Main function to build and train the model
def main():
    st.title('Predicting NASDAQ (^IXIC) Using Other Indices with Gradient Boosting Regressor')

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

    # Fetch and combine data for NASDAQ Futures
    nq_f_data = fetch_data('NQ=F')
    if not nq_f_data.empty:
        nq_f_data = extract_price(nq_f_data, 'NQ=F')
        combined_data = pd.concat([combined_data, nq_f_data], axis=1)

    # Fetch and combine data for NIKKEI
    nikkei_data = fetch_data('^N225')
    if not nikkei_data.empty:
        nikkei_data = extract_price(nikkei_data, '^N225')
        combined_data = pd.concat([combined_data, nikkei_data], axis=1)

    # Drop any rows with missing values
    combined_data.dropna(inplace=True)

    # Split the data into features (X) and target (y)
    X = combined_data[['^FTSE', 'NQ=F', '^N225']]
    y = combined_data['^IXIC']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize the Gradient Boosting Regressor model
    model = GradientBoostingRegressor(random_state=42)

    # Train the model
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Display the results
    st.write(f"Mean Squared Error: {mse}")
    st.write(f"R-squared: {r2}")

    # Display predicted vs actual values
    results = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    st.write("Predicted vs Actual NASDAQ (^IXIC) prices:")
    st.dataframe(results)

if __name__ == "__main__":
    main()
