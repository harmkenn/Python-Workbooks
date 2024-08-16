import streamlit as st
import pandas as pd
import plotly.express as px

# Sample GDP data (replace with actual data)
data = {
    "Year": list(range(2000, 2024)),
    "GDP": [9.8, 10.6, 11.0, 10.4, 10.9, 11.7, 12.4, 13.2, 14.2, 14.0, 12.4, 14.0, 15.0, 15.5, 16.7, 17.4, 18.1, 18.6, 19.4, 20.4, 21.4, 20.9, 23.0, 24.8]
}

df = pd.DataFrame(data)

# Streamlit app
def app():
    st.title("US GDP over the past 25 years")

    fig = px.line(df, x="Year", y="GDP", title="US GDP")
    st.plotly_chart(fig)

if __name__ == "__main__":
    app()