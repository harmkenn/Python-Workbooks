import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="3-Body Problem Viewer", layout="wide")

# -----------------------------------------
# Physics: 3-body gravitational system
# -----------------------------------------

def acceleration(positions, masses):
    G = 1.0
    acc = np.zeros_like(positions)
    for i in range(3):
        for j in range(3):
            if i != j:
                r = positions[j] - positions[i]
                dist3 = np.linalg.norm(r)**3 + 1e-9
                acc[i] += G * masses[j] * r / dist3
    return acc

def rk4_step(pos, vel, masses, dt):
    a1 = acceleration(pos, masses)
    k1_pos = vel
    k1_vel = a1

    a2 = acceleration(pos + 0.5*dt*k1_pos, masses)
    k2_pos = vel + 0.5*dt*k1_vel
    k2_vel = a2

    a3 = acceleration(pos + 0.5*dt*k2_pos, masses)
    k3_pos = vel + 0.5*dt*k2_vel
    k3_vel = a3

    a4 = acceleration(pos + dt*k3_pos, masses)
    k4_pos = vel + dt*k3_vel
    k4_vel = a4

    pos_new = pos + (dt/6)*(k1_pos + 2*k2_pos + 2*k3_pos + k4_pos)
    vel_new = vel + (dt/6)*(k1_vel + 2*k2_vel + 2*k3_vel + k4_vel)

    return pos_new, vel_new

def simulate(masses, pos, vel, steps, dt):
    positions = np.zeros((steps, 3, 2))
    positions[0] = pos

    for i in range(1, steps):
        pos, vel = rk4_step(pos, vel, masses, dt)
        positions[i] = pos

    return positions


# ----------------------------------------------------
# Sidebar Controls
# ----------------------------------------------------
st.sidebar.header("Simulation Controls")

steps = st.sidebar.slider("Steps", 200, 3000, 1200)
dt = st.sidebar.slider("Δt (time step)", 0.001, 0.05, 0.01)
trail_length = st.sidebar.slider("Trail Fade Length", 20, 150, 80)
mass_min, mass_max = st.sidebar.slider("Mass Range", 0.5, 5.0, (1.0, 2.0))

if st.sidebar.button("Generate New Random System"):
    st.session_state["regen"] = True
else:
    st.session_state.setdefault("regen", True)

# ----------------------------------------------------
# Generate Random Initial Conditions
# ----------------------------------------------------
if st.session_state["regen"]:
    np.random.seed()  # new randomness

    masses = np.random.uniform(mass_min, mass_max, 3)

    pos = np.random.uniform(-1, 1, (3, 2))
    vel = np.random.uniform(-0.5, 0.5, (3, 2))

    st.session_state["masses"] = masses
    st.session_state["pos"] = pos
    st.session_state["vel"] = vel
    st.session_state["regen"] = False

masses = st.session_state["masses"]
pos0 = st.session_state["pos"]
vel0 = st.session_state["vel"]

# ----------------------------------------------------
# Run Simulation
# ----------------------------------------------------
positions = simulate(masses, pos0, vel0, steps, dt)


# ----------------------------------------------------
# Plotly Animation
# ----------------------------------------------------

fig = go.Figure()

colors = ["red", "green", "blue"]

# initial frame
for i in range(3):
    fig.add_trace(go.Scatter(
        x=[positions[0, i, 0]],
        y=[positions[0, i, 1]],
        mode="markers",
        marker=dict(size=12, color=colors[i]),
        name=f"Body {i+1}"
    ))

# animation frames
frames = []
for t in range(steps):
    frame_data = []
    for i in range(3):
        trail_start = max(0, t - trail_length)
        alpha_values = np.linspace(0.05, 1.0, t - trail_start + 1)

        frame_data.append(
            go.Scatter(
                x=positions[trail_start:t+1, i, 0],
                y=positions[trail_start:t+1, i, 1],
                mode="lines+markers",
                line=dict(width=2, color=colors[i]),
                marker=dict(size=8, color=colors[i]),
                opacity=1.0
            )
        )
    frames.append(go.Frame(data=frame_data, name=str(t)))


fig.frames = frames

fig.update_layout(
    xaxis=dict(range=[-3, 3], autorange=False, zeroline=False),
    yaxis=dict(range=[-3, 3], autorange=False, zeroline=False),
    width=800,
    height=800,
    title="Random 3-Body Problem (with fading trails)",
    updatemenus=[
        dict(type="buttons",
             buttons=[dict(label="Play",
                           method="animate",
                           args=[None, {"frame": {"duration": 20}, "fromcurrent": True}])])
    ]
)

st.plotly_chart(fig, use_container_width=True)
