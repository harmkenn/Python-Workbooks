import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import GradientBoostingRegressor

# Get {today_date} date
today_date = datetime.today().strftime('%Y-%m-%d')

# Set the page layout to wide
st.set_page_config(layout="wide")

# Define the time range for the last 2000 days
end_date = datetime.now()
start_date = end_date - timedelta(days=2000)


# Fetch data from Yahoo Finance
@st.cache_data
def fetch_data(ticker):
    # Fetch daily data
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    return data


# Extract relevant columns and rename them
def extract_data(data, ticker):
    return data[['Open', 'High', 'Low', 'Close']].rename(
        columns={
            'Open': f'{ticker} Open',
            'High': f'{ticker} High',
            'Low': f'{ticker} Low',
            'Close': f'{ticker} Close'
        })


# Main function to display the data
def main():
    # Initialize an empty DataFrame
    combined_data = pd.DataFrame()

    # Fetch and combine data for N225
    N225_data = fetch_data('^N225')
    if not N225_data.empty:
        N225_data = extract_data(N225_data, 'N225')
        combined_data = pd.concat([combined_data, N225_data], axis=1)

    # Fetch and combine data for SSEC
    ssec_data = fetch_data('000001.SS')
    if not ssec_data.empty:
        ssec_data = extract_data(ssec_data, 'SSEC')
        combined_data = pd.concat([combined_data, ssec_data], axis=1)

    # Fetch and combine data for DAX
    dax_data = fetch_data('^GDAXI')
    if not dax_data.empty:
        dax_data = extract_data(dax_data, 'DAX')
        combined_data = pd.concat([combined_data, dax_data], axis=1)

    # Fetch and combine data for FTSE
    ftse_data = fetch_data('^FTSE')
    if not ftse_data.empty:
        ftse_data = extract_data(ftse_data, 'FTSE')
        combined_data = pd.concat([combined_data, ftse_data], axis=1)

    # Fetch and combine data for TQQQ
    tqqq_data = fetch_data('TQQQ')
    if not tqqq_data.empty:
        tqqq_data = extract_data(tqqq_data, 'TQQQ')
        combined_data = pd.concat([combined_data, tqqq_data], axis=1)

    # Drop rows with NaN values (usually the first row)
    combined_data = combined_data.dropna()
    yn = pd.DataFrame({
        'y Close': combined_data['TQQQ Close'].shift(1),
        'y High': combined_data['TQQQ High'].shift(1),
        'y Low': combined_data['TQQQ Low'].shift(1),
        'y N225': combined_data['N225 Close'].shift(1),
        'y SSEC': combined_data['SSEC Close'].shift(1),
        'y DAX': combined_data['DAX Close'].shift(1),
        'y FTSE': combined_data['FTSE Close'].shift(1)
    })
    combined_data = pd.concat([yn, combined_data],axis=1).drop(combined_data.index[0])
    combined_data.index = pd.to_datetime(combined_data.index).strftime('%Y-%m-%d')
    # Define the features (X) and the target (y)
    X = combined_data[[
        'y Low', 'y High', 'y Close', 'y N225', 'N225 Close', 'y SSEC',
        'SSEC Close', 'y DAX', 'DAX Close', 'y FTSE', 'FTSE Close'
    ]]

    y = combined_data[['TQQQ Low', 'TQQQ High', 'TQQQ Close']]
    yesterdate = combined_data.index.max()

    # Create a multi-output regression model
    model = MultiOutputRegressor(GradientBoostingRegressor())

    # Train the model on the entire dataset
    model.fit(X, y)

    # Make predictions on the model
    y_pred = model.predict(X)

    # Create a DataFrame with the predicted values and dates as index
    tqqq_pred = pd.DataFrame(y_pred,
                             columns=['P Low', 'P High', 'P Close'],
                             index=X.index)

    # Concatenate the predicted and actual DataFrames
    comparison = pd.concat([tqqq_pred, y], axis=1)

    # User inputs for {today_date} FTSE, N225, DAX, and SSEC prices
    st.subheader(f"Predict {today_date} TQQQ")

    a1, a2, a3 = st.columns(3)

    with a1:
        TQQQ_yesterday_low = st.number_input(f"Enter {yesterdate} TQQQ Low: {combined_data['TQQQ Low'].iloc[-1]}", 
                                             format="%.2f", value=combined_data['TQQQ Low'].iloc[-1], step=0.01)
        TQQQ_yesterday_high = st.number_input(f"Enter {yesterdate} TQQQ High: {combined_data['TQQQ High'].iloc[-1]}",
                                              format="%.2f",value=combined_data['TQQQ High'].iloc[-1],step=0.01)
        TQQQ_yesterday_close = st.number_input(f"Enter {yesterdate} TQQQ Close: {combined_data['TQQQ Close'].iloc[-1]}",
                                               format="%.2f",value=combined_data['TQQQ Close'].iloc[-1],step=0.01)

    with a2:
        N225_y = st.number_input(f"Enter {yesterdate} N225 Close: {combined_data['N225 Close'].iloc[-1]}",
                                 format="%.2f",value=combined_data['N225 Close'].iloc[-1],step=0.01)
        N225_today = st.number_input(f"Enter {today_date} N225 Close: {combined_data['N225 Close'].iloc[-1]}",
                                     format="%.2f",value=combined_data['N225 Close'].iloc[-1],step=0.01)
        ssec_y = st.number_input(f"Enter {yesterdate} SSEC Close: {combined_data['SSEC Close'].iloc[-1]}",
                                 format="%.2f",value=combined_data['SSEC Close'].iloc[-1],step=0.01)
        ssec_today = st.number_input(f"Enter {today_date} SSEC Close: {combined_data['SSEC Close'].iloc[-1]}",
                                     format="%.2f",value=combined_data['SSEC Close'].iloc[-1],step=0.01)

    with a3:
        dax_y = st.number_input(f"Enter {yesterdate} DAX Close: {combined_data['DAX Close'].iloc[-1]}",
                                format="%.2f",value=combined_data['DAX Close'].iloc[-1],step=0.01)
        dax_today = st.number_input(f"Enter {today_date} DAX Close: {combined_data['DAX Close'].iloc[-1]}",
                                    format="%.2f",value=combined_data['DAX Close'].iloc[-1],step=0.01)
        ftse_y = st.number_input(f"Enter {yesterdate} FTSE Close: {combined_data['FTSE Close'].iloc[-1]}",
                                 format="%.2f",value=combined_data['FTSE Close'].iloc[-1],step=0.01)
        ftse_today = st.number_input(f"Enter {today_date} FTSE Close: {combined_data['FTSE Close'].iloc[-1]}",
                                     format="%.2f",value=combined_data['FTSE Close'].iloc[-1],step=0.01)

    with a1:
        # Create a DataFrame with the same column names as the original training data
        today_data = pd.DataFrame({
            'y Low': [TQQQ_yesterday_low],
            'y High': [TQQQ_yesterday_high],
            'y Close': [TQQQ_yesterday_close],
            'y N225': [N225_y],
            'N225 Close': [N225_today],
            'y SSEC': [ssec_y],
            'SSEC Close': [ssec_today],
            'y DAX': [dax_y],
            'DAX Close': [dax_today],
            'y FTSE': [ftse_y],
            'FTSE Close': [ftse_today]
        })

        # Predict {today_date} TQQQ Close based on user inputs
        if st.button(f"Predict {today_date} TQQQ"):
            tp = model.predict(today_data)
            st.write(
                f'Low: {round(tp[0][0],2)}, High: {round(tp[0][1],2)}, Close: {round(tp[0][2],2)}'
            )
            st.write(
                f'Low:{round((tp[0][0] - TQQQ_yesterday_close)/TQQQ_yesterday_close*100,2)}%, High: {round((tp[0][1]- TQQQ_yesterday_close)/TQQQ_yesterday_close*100,2)}%, Close: {round((tp[0][2]- TQQQ_yesterday_close)/TQQQ_yesterday_close*100,2)}%'
            )

    st.write("Actual vs Predicted TQQQ Close:")
    X = X.apply(lambda x: x.map(lambda y: format(y, '.2f')))
    X = X.sort_index(ascending=False)

    comparison = comparison.apply(lambda x: x.map(lambda y: format(y, '.2f')))
    comparison = comparison.sort_index(ascending=False)
    all = pd.concat([X, comparison], axis=1)
    st.dataframe(all, use_container_width=True)


if __name__ == "__main__":
    main()
