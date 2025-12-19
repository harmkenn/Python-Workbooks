import streamlit as st
import plotly.graph_objects as go

st.title("Click to Place Points v2.0")

# Store clicks in session_state
if "points" not in st.session_state:
    st.session_state.points = []

fig = go.Figure()
fig.update_layout(
    width=700,
    height=700,
    xaxis=dict(range=[-5, 5]),
    yaxis=dict(range=[-5, 5]),
    dragmode=False,
)

# Add existing points
for p in st.session_state.points:
    fig.add_trace(go.Scatter(
        x=[p[0]], y=[p[1]],
        mode="markers",
        marker=dict(size=12, color="red")
    ))

# Capture click
clicked = st.plotly_chart(fig, use_container_width=True, click=True)

if clicked and clicked["points"]:
    x = clicked["points"][0]["x"]
    y = clicked["points"][0]["y"]
    st.session_state.points.append((x, y))

st.write("Points:", st.session_state.points)
