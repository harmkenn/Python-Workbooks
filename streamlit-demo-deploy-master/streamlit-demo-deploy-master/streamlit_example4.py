import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
json1 = f"states_india.geojson"

m = folium.Map(location=[23.47, 77.94], tiles='CartoDB positron',name="Light Map",
           zoom_start=5,
           attr='My Data Attribution')

india_covid = f"covid_cases_india.csv"
india_covid_data = pd.read_csv(india_covid)
choice = ['Confirmed Cases','Active Cases', 'Cured/Discharged', 'Death']
choice_selected = st.selectbox("Select Choice ", choice)
folium.Choropleth(
    geo_data=json1,
    name="choropleth",
    data=india_covid_data,
    columns=["state_code", choice_selected],
    key_on="feature.properties.state_code",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=.1,
    legend_name=choice_selected+"(%)",
).add_to(m)
folium.features.GeoJson('states_india.geojson', name="LSOA Code",
                           popup=folium.features.GeoJsonPopup(fields=['st_nm'])).add_to(m)
folium_static(m, width=1600, height=950)

