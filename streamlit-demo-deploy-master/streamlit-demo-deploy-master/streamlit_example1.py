import streamlit as st
import time
import altair as alt
import pandas as pd

x = st.slider("Select a value")
st.write(x, "Squared value is ",x*x)

bar = st.progress(0)
for percentage_complete in range(100):
    time.sleep(0.1)
    bar.progress(percentage_complete+1)

chart_data = pd.DataFrame([[1,2,1],[0,2,1],[1,3,5]],
                          columns=['a','b','c'],
                          index=[1,2,3])
st.area_chart(chart_data)

data = pd.DataFrame({
    'city' : ['Delhi', 'Kolkata', 'Chennai'],
    'sports_teams' : [6, 8, 9]
})
chart = alt.Chart(data).mark_bar().encode(
    x = 'city',
    y = 'sports_teams'
).properties(width = 500, height = 500)

st.altair_chart(chart)

series = pd.DataFrame({
  'year': ['2010', '2011', '2012', '2013','2010', '2011', '2012', '2013'],
  'animal': ['antelope', 'antelope', 'antelope', 'antelope', 'velociraptor', 'velociraptor', 'velociraptor', 'velociraptor',],
  'count': [8, 6, 3, 1, 2, 4, 5, 5]
})
st.write("Basic Chart")
basic_chart = alt.Chart(series).mark_line().encode(
    x='year',
    y = 'count',
    color= 'animal'
).properties(width=500,height=500)
st.altair_chart(basic_chart)

st.write("Custom Chart")
custom_chart = alt.Chart(series).mark_line().encode(
  x = 'year',
  y= 'count',
    color = alt.Color('animal',
                      scale = alt.Scale(
                          domain= ('antelope', 'velociraptor'),
                          range = ['blue','red']
                      ))
).properties(width=500, height=500)
st.altair_chart(custom_chart)
