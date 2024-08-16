import streamlit as st
import pandas as pd
import plotly.express as px

# Sample GDP, Unemployment, Inflation, CPI, Interest Rate, and Consumer Confidence Index data (replace with actual data)
data = {
    "Year": list(range(2000, 2024)),
    "GDP": [9.8, 10.6, 11.0, 10.4, 10.9, 11.7, 12.4, 13.2, 14.2, 14.0, 12.4, 14.0, 15.0, 15.5, 16.7, 17.4, 18.1, 18.6, 19.4, 20.4, 21.4, 20.9, 23.0, 24.8],
    "Unemployment_Rate": [4.2, 4.0, 4.7, 5.8, 6.0, 5.5, 4.6, 4.4, 4.6, 7.8, 9.6, 8.9, 8.1, 7.4, 6.7, 6.2, 5.3, 4.9, 4.4, 3.9, 3.6, 3.8, 3.6, 3.7],
    "Inflation_Rate": [2.2, 2.5, 2.8, 1.6, 1.9, 2.3, 3.2, 2.1, 2.4, -0.3, -0.4, 1.6, 3.2, 2.1, 1.4, 1.6, 0.1, 1.4, 2.1, 2.4, 1.8, 4.7, 6.5, 3.2],
    "CPI": [166.6, 169.1, 171.9, 174.0, 176.7, 179.8, 182.9, 185.7, 188.9, 188.0, 186.9, 190.0, 195.3, 197.8, 198.7, 199.2, 199.7, 200.2, 201.6, 202.4, 203.5, 207.6, 211.1, 214.6],
    "Interest_Rate": [6.5, 6.0, 4.0, 1.75, 1.0, 1.0, 1.25, 5.25, 5.25, 2.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 1.5, 2.25, 1.75, 0.25, 0.75, 4.5],
    "Consumer_Confidence_Index": [105, 108, 102, 98, 95, 97, 100, 103, 105, 92, 88, 90, 95, 98, 100, 102, 105, 108, 110, 112, 115, 110, 108, 110]
}

df = pd.DataFrame(data)

def app():
    st.title("US Economic Indicators")

    # GDP Plot
    fig_gdp = px.line(df, x="Year", y="GDP", title="US GDP")

    # Unemployment Rate Plot
    fig_unemployment = px.line(df, x="Year", y="Unemployment_Rate", title="US Unemployment Rate")

    # Inflation Rate Plot
    fig_inflation = px.line(df, x="Year", y="Inflation_Rate", title="US Inflation Rate")

    # CPI Plot
    fig_cpi = px.line(df, x="Year", y="CPI", title="US CPI")

    # Interest Rate Plot
    fig_interest_rate = px.line(df, x="Year", y="Interest_Rate", title="US Interest Rate")

    # Consumer Confidence Index Plot
    fig_consumer_confidence = px.line(df, x="Year", y="Consumer_Confidence_Index", title="US Consumer Confidence Index")

    # Display all plots
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.plotly_chart(fig_gdp)
    with col2:
        st.plotly_chart(fig_unemployment)
    with col3:
        st.plotly_chart(fig_inflation)
    with col4:
        st.plotly_chart(fig_cpi)
    with col5:
        st.plotly_chart(fig_interest_rate)
    with col6:
        st.plotly_chart(fig_consumer_confidence)

if __name__ == "__main__":
    app()