import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.title("Click to Place Points v2.3")

# Store clicks in session_state
if "points" not in st.session_state:
    st.session_state.points = []

# Callback for click events
def handle_click(event):
    if event and "points" in event:
        x = event["points"][0]["x"]
        y = event["points"][0]["y"]
        st.session_state.points.append((x, y))

# Create invisible grid of points to capture clicks
grid_x, grid_y = np.meshgrid(
    np.linspace(-5, 5, 50),
    np.linspace(-5, 5, 50)
)

fig = go.Figure()

# ✅ Invisible click‑capture layer
fig.add_trace(go.Scatter(
    x=grid_x.flatten(),
    y=grid_y.flatten(),
    mode="markers",
    marker=dict(size=1, opacity=0),
    showlegend=False,
    hoverinfo="skip"
))

# Draw existing points
for p in st.session_state.points:
    fig.add_trace(go.Scatter(
        x=[p[0]], y=[p[1]],
        mode="markers",
        marker=dict(size=12, color="red")
    ))

fig.update_layout(
    width=700,
    height=700,
    xaxis=dict(range=[-5, 5]),
    yaxis=dict(range=[-5, 5]),
    dragmode=False,
)

# Display chart with click callback
st.plotly_chart(
    fig,
    width="stretch",
    on_click=handle_click,
)

st.write("Points:", st.session_state.points)
