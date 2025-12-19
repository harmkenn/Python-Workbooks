import streamlit as st
import plotly.graph_objects as go

st.title("Click to Place Points v2.2")

# Store clicks in session_state
if "points" not in st.session_state:
    st.session_state.points = []

# Callback for click events
def handle_click(event):
    if event and "points" in event:
        x = event["points"][0]["x"]
        y = event["points"][0]["y"]
        st.session_state.points.append((x, y))

fig = go.Figure()

# ✅ Add a transparent base trace so clicks register
fig.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode="markers",
    marker=dict(opacity=0),
    showlegend=False
))

fig.update_layout(
    width=700,
    height=700,
    xaxis=dict(range=[-5, 5]),
    yaxis=dict(range=[-5, 5]),
    dragmode=False,
)

# Draw existing points
for p in st.session_state.points:
    fig.add_trace(go.Scatter(
        x=[p[0]], y=[p[1]],
        mode="markers",
        marker=dict(size=12, color="red")
    ))

# Display chart with click callback
st.plotly_chart(
    fig,
    width="stretch",
    on_click=handle_click,
)

st.write("Points:", st.session_state.points)
