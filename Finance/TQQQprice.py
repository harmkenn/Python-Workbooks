import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from sklearn.multioutput import MultiOutputRegressor
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



# Extract relevant columns and rename them
def extract_data(data, ticker):
    return data[['Open', 'High', 'Low', 'Close']].rename(columns={'Open': f'{ticker} Open', 'High': f'{ticker} High', 'Low': f'{ticker} Low', 'Close': f'{ticker} Close'})



# Main function to display the data
def main():
    # Initialize an empty DataFrame
    combined_data = pd.DataFrame()


    # Fetch and combine data for NIKKEI
    nikkei_data = fetch_data('^N225')
    if not nikkei_data.empty:
        nikkei_data = extract_data(nikkei_data, '^N225')
        combined_data = pd.concat([combined_data, nikkei_data], axis=1)


    # Fetch and combine data for Shanghai Composite
    ssec_data = fetch_data('000001.SS')
    if not ssec_data.empty:
        ssec_data = extract_data(ssec_data, '000001.SS')
        combined_data = pd.concat([combined_data, ssec_data], axis=1)


    # Fetch and combine data for DAX
    dax_data = fetch_data('^GDAXI')
    if not dax_data.empty:
        dax_data = extract_data(dax_data, '^GDAXI')
        combined_data = pd.concat([combined_data, dax_data], axis=1)


    # Fetch and combine data for FTSE
    ftse_data = fetch_data('^FTSE')
    if not ftse_data.empty:
        ftse_data = extract_data(ftse_data, '^FTSE')
        combined_data = pd.concat([combined_data, ftse_data], axis=1)


    # Fetch and combine data for TQQQ
    tqqq_data = fetch_data('TQQQ')
    if not tqqq_data.empty:
        tqqq_data = extract_data(tqqq_data, 'TQQQ')
        combined_data = pd.concat([combined_data, tqqq_data], axis=1)


    # Drop rows with NaN values (usually the first row)
    combined_data = combined_data.dropna()
    yn = pd.DataFrame({'TQQQ y Close': combined_data['TQQQ Close'].shift(1),
                   'TQQQ y High': combined_data['TQQQ High'].shift(1),
                   'TQQQ y Low': combined_data['TQQQ Low'].shift(1)})
    combined_data = pd.concat([yn, combined_data], axis=1).drop(combined_data.index[0])
    

    # Define the features (X) and the target (y)
    X = combined_data[['TQQQ y Low', 'TQQQ y High', 'TQQQ y Close',
                       '^N225 Low','^N225 High', '^N225 Close',  
                       '000001.SS Low', '000001.SS High',  '000001.SS Close', 
                       '^GDAXI Low', '^GDAXI High',  '^GDAXI Close', 
                       '^FTSE Low', '^FTSE High',  '^FTSE Close'                       
                    ]]
    

    y = combined_data[['TQQQ Low', 'TQQQ High',  'TQQQ Close']]

    # Create a multi-output regression model
    model = MultiOutputRegressor(GradientBoostingRegressor())

    # Train the model on the entire dataset
    model.fit(X, y)

    # Make predictions on the model
    y_pred = model.predict(X)
    
    # Create a DataFrame with the predicted values and dates as index
    tqqq_pred = pd.DataFrame(y_pred, columns=['P TQQQ Low', 'P TQQQ High', 'P TQQQ Close'], index=X.index)
   
    # Concatenate the predicted and actual DataFrames
    comparison = pd.concat([tqqq_pred, y], axis=1)
    
    # User inputs for today's FTSE, NIKKEI, DAX, and Shanghai Composite prices
    st.subheader("Predict Today's TQQQ")

    last_nq = combined_data['TQQQ Close'].iloc[-1]
    last_n225 = combined_data['^N225 Close'].iloc[-1]
    last_ssec = combined_data['000001.SS Close'].iloc[-1]
    curr_dax = combined_data['^GDAXI Close'].iloc[-1]
    curr_ftse = combined_data['^FTSE Close'].iloc[-1]

    a1, a2, a3 = st.columns(3)

    with a1:
        TQQQ_yesterday_low = st.number_input(f"Enter yesterday's TQQQ Low: {combined_data['TQQQ Low'].iloc[-1]}", format="%.2f", value=combined_data['TQQQ Low'].iloc[-1], step=0.01)
        nikkei_today_low = st.number_input(f"Enter today's NIKKEI Low: {combined_data['^N225 Low'].iloc[-1]}", format="%.2f", value=combined_data['^N225 Low'].iloc[-1], step=0.01)
        ssec_today_low = st.number_input(f"Enter today's Shanghai Composite Low: {combined_data['000001.SS Low'].iloc[-1]}", format="%.2f", value=combined_data['000001.SS Low'].iloc[-1], step=0.01)
        dax_today_low = st.number_input(f"Enter today's DAX Low: {combined_data['^GDAXI Low'].iloc[-1]}", format="%.2f", value=combined_data['^GDAXI Low'].iloc[-1], step=0.01)
        ftse_today_low = st.number_input(f"Enter today's FTSE Low: {combined_data['^FTSE Low'].iloc[-1]}", format="%.2f", value=combined_data['^FTSE Low'].iloc[-1], step=0.01)
        
    with a2:
        TQQQ_yesterday_high = st.number_input(f"Enter yesterday's TQQQ High: {combined_data['TQQQ High'].iloc[-1]}", format="%.2f", value=combined_data['TQQQ High'].iloc[-1], step=0.01)
        nikkei_today_high = st.number_input(f"Enter today's NIKKEI High: {combined_data['^N225 High'].iloc[-1]}", format="%.2f", value=combined_data['^N225 High'].iloc[-1], step=0.01)
        ssec_today_high = st.number_input(f"Enter today's Shanghai Composite High: {combined_data['000001.SS High'].iloc[-1]}", format="%.2f", value=combined_data['000001.SS High'].iloc[-1], step=0.01)
        dax_today_high = st.number_input(f"Enter today's DAX High: {combined_data['^GDAXI High'].iloc[-1]}", format="%.2f", value=combined_data['^GDAXI High'].iloc[-1], step=0.01)
        ftse_today_high = st.number_input(f"Enter today's FTSE High: {combined_data['^FTSE High'].iloc[-1]}", format="%.2f", value=combined_data['^FTSE High'].iloc[-1], step=0.01)
        
    with a3:
        TQQQ_yesterday_close = st.number_input(f"Enter yesterday's TQQQ Close: {last_nq}", format="%.2f", value=last_nq, step=0.01)
        nikkei_today_close = st.number_input(f"Enter today's NIKKEI Close: {last_n225}", format="%.2f", value=last_n225, step=0.01)
        ssec_today_close = st.number_input(f"Enter today's Shanghai Composite Close: {last_ssec}", format="%.2f", value=last_ssec, step=0.01)
        dax_today_close = st.number_input(f"Enter today's DAX Close: {curr_dax}", format="%.2f", value=curr_dax, step=0.01)
        ftse_today_close = st.number_input(f"Enter today's FTSE Close: {curr_ftse}", format="%.2f", value=curr_ftse, step=0.01)

    # Create a DataFrame with the same column names as the original training data
    today_data = pd.DataFrame({
        'TQQQ y Low': [TQQQ_yesterday_low],
        'TQQQ y High': [TQQQ_yesterday_high],
        'TQQQ y Close': [TQQQ_yesterday_close],
        '^N225 Low': [nikkei_today_low],
        '^N225 High': [nikkei_today_high],
        '^N225 Close': [nikkei_today_close],
        '000001.SS Low': [ssec_today_low],
        '000001.SS High': [ssec_today_high],
        '000001.SS Close': [ssec_today_close],
        '^GDAXI Low': [dax_today_low],
        '^GDAXI High': [dax_today_high],
        '^GDAXI Close': [dax_today_close],
        '^FTSE Low': [ftse_today_low],
        '^FTSE High': [ftse_today_high],
        '^FTSE Close': [ftse_today_close]
    })

    # Predict today's TQQQ Close based on user inputs
    if st.button("Predict Today's TQQQ"):
        tp = model.predict(today_data)
        st.write(f'Low: {round(tp[0][0],2)}, High: {round(tp[0][1],2)}, Close: {round(tp[0][2],2)}')
        st.write(f'Low:{round((tp[0][0] - TQQQ_yesterday_close)/TQQQ_yesterday_close*100,2)}%, High: {round((tp[0][1]- TQQQ_yesterday_close)/TQQQ_yesterday_close*100,2)}%, Close: {round((tp[0][2]- TQQQ_yesterday_close)/TQQQ_yesterday_close*100,2)}% From Yesterday close of: {round(TQQQ_yesterday_close,2)} ')

    st.write("Actual vs Predicted TQQQ Close:")
    comparison = comparison.apply(lambda x: x.map(lambda y: format(y, '.2f')))
    st.dataframe(comparison, use_container_width=True)
    X = X.apply(lambda x: x.map(lambda y: format(y, '.2f')))
    st.dataframe(X)
    
if __name__ == "__main__":
    main()