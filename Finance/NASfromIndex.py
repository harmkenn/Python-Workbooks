import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from sklearn.ensemble import GradientBoostingRegressor


# Set the page layout to wide
st.set_page_config(layout="wide")


# Define the time range for the last 368 days
end_date = datetime.now()
start_date = end_date - timedelta(days=368)


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
    #st.title('Prediction of NASDAQ (^IXIC) From (^FTSE), NIKKEI (^N225), DAX (^GDAXI), and Shanghai Composite (000001.SS)')


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
    nf_data = fetch_data('NQ=F')
    if not nf_data.empty:
        nf_data = extract_price(nf_data, 'NQ=F')
        combined_data = pd.concat([combined_data, nf_data], axis=1)

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
    yn = pd.DataFrame({'^IXIC % yesterday':combined_data['^IXIC % Change'].shift(1)})
    
    # Define the features (X) and the target (y)
    X = combined_data[['^N225 % Change', '000001.SS % Change','^GDAXI % Change', '^FTSE % Change', 'NQ=F % Change']]
    X = pd.concat([yn,X], axis=1).drop(X.index[0])
    y = combined_data['^IXIC % Change'][1:]

    # Initialize the GradientBoostingRegressor model
    model = GradientBoostingRegressor()


    # Train the model on the entire dataset
    model.fit(X, y)


    # Predict on the entire dataset
    y_pred = model.predict(X)


    # Display the actual and predicted values
    comparison = pd.DataFrame({'^IXIC yesterday':X['^IXIC % yesterday'], '^N225 %':X['^N225 % Change'], '000001.SS %':X['000001.SS % Change'], '^GDAXI %':X['^GDAXI % Change'],'^FTSE %':X['^FTSE % Change'],'NQ=F %':X['NQ=F % Change'] ,'Predicted ^IXIC %': y_pred, 'Actual ^IXIC %': y})
    


    # User inputs for today's FTSE, NIKKEI, DAX, and Shanghai Composite percent changes
    st.subheader("Predict Today's NASDAQ Percent Change")
    nikkei = yf.Ticker("^N225")
    n225_data = nikkei.history(period="1d")
    current_n225 = n225_data["Close"].iloc[-1]
    ssec = yf.Ticker("000001.SS")
    data = ssec.history(period="1d")
    current_ssec = data["Close"].iloc[-1]
    dax = yf.Ticker("^GDAXI")
    data = dax.history(period="1d")
    current_dax = data["Close"].iloc[-1]
    ftse = yf.Ticker("^FTSE")
    data = ftse.history(period="1d")
    current_ftse = data["Close"].iloc[-1]
    nqf = yf.Ticker("NQ=F")
    data = nqf.history(period="1d")
    current_nqf = data["Close"].iloc[-1]

    last_nq = combined_data['^IXIC % Change'][-1]
    last_n225 = (current_n225-n225_data['^N225'][-1])/n225_data['^N225'][-1]
    last_ssec = (ssec_data['000001.SS'][-1]-ssec_data['000001.SS'][-2])/ssec_data['000001.SS'][-2]
    curr_dax = (current_dax-dax_data['^GDAXI'][-1])/dax_data['^GDAXI'][-1]
    curr_ftse = (current_ftse-ftse_data['^FTSE'][-1])/ftse_data['^FTSE'][-1]
    curr_nqf = (current_nqf-nf_data['NQ=F'][-1])/nf_data['NQ=F'][-1]
    st.write(f"{model.predict([[last_nq,last_n225,last_ssec,curr_dax,curr_ftse,curr_nqf]])[0]:.6f}")

    nasdaq_yesterday = st.number_input(f"Enter yesterday's NASDAQ % Change: {last_nq}", format="%.5f", value=0.0, step=0.00001)
    nikkei_today = st.number_input(f"Enter today's NIKKEI % Change: {last_n225}", format="%.5f", value=0.0, step=0.00001)
    ssec_today = st.number_input(f"Enter today's Shanghai Composite % Change: {last_ssec}", format="%.5f", value=0.0, step=0.00001)
    dax_today = st.number_input(f"Enter today's DAX % Change: {curr_dax}", format="%.5f", value=0.0, step=0.00001)
    ftse_today = st.number_input(f"Enter today's FTSE % Change: {curr_ftse}", format="%.5f", value=0.0, step=0.00001)
    nqf_today = st.number_input(f"Enter today's NQ=F % Change: {curr_nqf}", format="%.5f", value=0.0, step=0.00001)
    

    # Predict today's NASDAQ % Change based on user inputs
    if st.button("Predict NASDAQ % Change"):
        today_prediction = model.predict([[nasdaq_yesterday, nikkei_today, ssec_today, dax_today, ftse_today, nqf_today]])
        st.write(f"Predicted NASDAQ % Change for today: {today_prediction[0]:.5f}")

    
    st.write("Actual vs Predicted NASDAQ Percent Change:")
    pd.options.display.float_format = '{:.15f}'.format
    st.dataframe(comparison, use_container_width=True)


if __name__ == "__main__":
    main()