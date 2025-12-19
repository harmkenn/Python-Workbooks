import streamlit as st
import plotly.graph_objects as go

st.title("Drag Points + Velocity Vectors Demo")

# Initial positions
pos = [
    {"x": -1, "y": 0},
    {"x": 1, "y": 0},
    {"x": 0, "y": 1}
]

# Initial velocities
vel = [
    {"vx": 0.5, "vy": 0.2},
    {"vx": -0.3, "vy": 0.1},
    {"vx": 0.1, "vy": -0.4}
]

fig = go.Figure()

# Add draggable position points
for i, p in enumerate(pos):
    fig.add_annotation(
        x=p["x"], y=p["y"],
        ax=p["x"], ay=p["y"],
        text=f"P{i+1}",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=2,
        arrowcolor="red",
    )

# Add draggable velocity vectors
for i, p in enumerate(pos):
    fig.add_annotation(
        x=p["x"] + vel[i]["vx"],
        y=p["y"] + vel[i]["vy"],
        ax=p["x"],
        ay=p["y"],
        arrowhead=3,
        arrowsize=1.5,
        arrowwidth=2,
        arrowcolor="blue",
        text=f"v{i+1}",
        showarrow=True,
    )

fig.update_layout(
    editable=True,
    dragmode="move",
    width=700,
    height=700,
    xaxis=dict(range=[-5, 5], zeroline=False),
    yaxis=dict(range=[-5, 5], zeroline=False),
)

result = st.plotly_chart(fig, use_container_width=True)

st.write("Drag the red points or blue velocity arrows. After dragging, Streamlit will capture the new annotation positions.")
