import streamlit as st
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from streamlit_bokeh_events import streamlit_bokeh_events

st.title("Click to Place Points (Bokeh Version) v3.0")

# Store points
if "points" not in st.session_state:
    st.session_state.points = []

# Data source for plotted points
source = ColumnDataSource(data=dict(x=[], y=[]))

# Create Bokeh figure
p = figure(
    width=700,
    height=700,
    x_range=(-5, 5),
    y_range=(-5, 5),
    tools="tap",
    title="Click anywhere to place a point"
)

# Draw existing points
if st.session_state.points:
    xs, ys = zip(*st.session_state.points)
    source.data = dict(x=list(xs), y=list(ys))

p.circle('x', 'y', size=12, color="red", source=source)

# Capture click events
event = streamlit_bokeh_events(
    p,
    events="tap",
    key="bokeh_click",
    refresh_on_update=False,
    debounce_time=0
)

# If a click happened, store it
if event and "tap" in event:
    x = event["tap"]["x"]
    y = event["tap"]["y"]
    st.session_state.points.append((x, y))
    source.stream(dict(x=[x], y=[y]))

st.write("Points:", st.session_state.points)
