import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------
# Streamlit Page Setup
# ---------------------------------------------------------
st.set_page_config(page_title="Three‑Body Problem Explorer", layout="wide")
st.title("Three‑Body Problem Explorer v1.1")
st.write(
    "A clean, modern playground for exploring stable and chaotic three‑body orbits. "
    "Choose a preset or define your own initial conditions."
)

# ---------------------------------------------------------
# Physics Engine
# ---------------------------------------------------------
G = 1.0  # Scaled gravitational constant

def accelerations(positions, masses):
    """Compute gravitational accelerations for 3 bodies in 2D."""
    acc = np.zeros_like(positions)
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            r = positions[j] - positions[i]
            dist_sq = np.dot(r, r) + 1e-6
            dist = np.sqrt(dist_sq)
            acc[i] += G * masses[j] * r / (dist_sq * dist)
    return acc

def simulate(pos_init, vel_init, masses, dt, steps):
    """Velocity Verlet integration."""
    positions = np.zeros((steps, 3, 2))
    pos = pos_init.copy()
    vel = vel_init.copy()
    acc = accelerations(pos, masses)

    for t in range(steps):
        positions[t] = pos
        pos_new = pos + vel * dt + 0.5 * acc * dt * dt
        acc_new = accelerations(pos_new, masses)
        vel_new = vel + 0.5 * (acc + acc_new) * dt
        pos, vel, acc = pos_new, vel_new, acc_new

    return positions

# ---------------------------------------------------------
# Presets
# ---------------------------------------------------------
def preset_lagrange():
    pos = np.array([
        [-1.0, 0.0],
        [ 1.0, 0.0],
        [ 0.0, np.sqrt(3)]
    ])
    vel = np.array([
        [ 0.5,  0.28867513459],
        [ 0.5, -0.28867513459],
        [-1.0,  0.0]
    ])
    masses = np.array([1.0, 1.0, 1.0])
    return pos, vel, masses

def preset_figure_eight():
    pos = np.array([
        [-0.97000436,  0.24308753],
        [ 0.97000436, -0.24308753],
        [ 0.0,         0.0]
    ])
    vel = np.array([
        [ 0.466203685,  0.43236573],
        [ 0.466203685,  0.43236573],
        [-0.93240737,  -0.86473146]
    ])
    masses = np.array([1.0, 1.0, 1.0])
    return pos, vel, masses

def preset_criss_cross():
    pos = np.array([
        [0.0,  1.0],
        [0.0, -1.0],
        [0.0,  0.0]
    ])
    vel = np.array([
        [ 0.347111,  0.532728],
        [ 0.347111,  0.532728],
        [-0.694222, -1.065456]
    ])
    masses = np.array([1.0, 1.0, 1.0])
    return pos, vel, masses

def preset_binary_companion():
    pos = np.array([
        [-0.5, 0.0],
        [ 0.5, 0.0],
        [ 0.0, 5.0]
    ])
    vel = np.array([
        [0.0,  0.8],
        [0.0, -0.8],
        [1.0,  0.0]
    ])
    masses = np.array([1.0, 1.0, 0.1])
    return pos, vel, masses

PRESETS = {
    "Equilateral Lagrange (Stable)": preset_lagrange,
    "Figure‑Eight Orbit": preset_figure_eight,
    "Henon Criss‑Cross": preset_criss_cross,
    "Binary + Distant Companion": preset_binary_companion,
    "Custom (Manual Input)": None,
}

# ---------------------------------------------------------
# Sidebar Controls
# ---------------------------------------------------------
st.sidebar.header("Simulation Controls")

preset_name = st.sidebar.selectbox("Choose a preset", list(PRESETS.keys()))

dt = st.sidebar.slider("Time step", 0.001, 0.05, 0.01, 0.001)
total_time = st.sidebar.slider("Total time", 10.0, 200.0, 80.0, 5.0)
animate = st.sidebar.checkbox("Animate", True)
trail_fraction = st.sidebar.slider("Trail length fraction", 0.05, 1.0, 0.4, 0.05)

steps = int(total_time / dt)
trail_steps = max(1, int(trail_fraction * steps))

# ---------------------------------------------------------
# Initial Conditions
# ---------------------------------------------------------
if preset_name != "Custom (Manual Input)":
    pos_init, vel_init, masses = PRESETS[preset_name]()
else:
    st.sidebar.subheader("Manual Initial Conditions")

    masses = np.array([
        st.sidebar.number_input("Mass 1", 0.1, 10.0, 1.0),
        st.sidebar.number_input("Mass 2", 0.1, 10.0, 1.0),
        st.sidebar.number_input("Mass 3", 0.1, 10.0, 1.0),
    ])

    pos_init = np.array([
        [st.sidebar.number_input("x1", -5.0, 5.0, -1.0),
         st.sidebar.number_input("y1", -5.0, 5.0, 0.0)],
        [st.sidebar.number_input("x2", -5.0, 5.0, 1.0),
         st.sidebar.number_input("y2", -5.0, 5.0, 0.0)],
        [st.sidebar.number_input("x3", -5.0, 5.0, 0.0),
         st.sidebar.number_input("y3", -5.0, 5.0, 1.0)],
    ])

    vel_init = np.array([
        [st.sidebar.number_input("vx1", -3.0, 3.0, 0.0),
         st.sidebar.number_input("vy1", -3.0, 3.0, 0.5)],
        [st.sidebar.number_input("vx2", -3.0, 3.0, 0.0),
         st.sidebar.number_input("vy2", -3.0, 3.0, -0.5)],
        [st.sidebar.number_input("vx3", -3.0, 3.0, -0.5),
         st.sidebar.number_input("vy3", -3.0, 3.0, 0.0)],
    ])

# ---------------------------------------------------------
# Run Simulation
# ---------------------------------------------------------
with st.spinner("Simulating..."):
    positions = simulate(pos_init, vel_init, masses, dt, steps)

x = positions[:, :, 0]
y = positions[:, :, 1]

# ---------------------------------------------------------
# Plotting
# ---------------------------------------------------------
colors = ["#ff595e", "#1982c4", "#8ac926"]
labels = ["Body 1", "Body 2", "Body 3"]

fig = go.Figure()

if animate:
    frame_indices = np.linspace(0, steps - 1, num=min(200, steps), dtype=int)
    frames = []

    for k in frame_indices:
        start = max(0, k - trail_steps)
        data = []

        for i in range(3):
            data.append(go.Scatter(
                x=x[start:k+1, i],
                y=y[start:k+1, i],
                mode="lines",
                line=dict(color=colors[i], width=2),
                showlegend=False,
            ))

        for i in range(3):
            data.append(go.Scatter(
                x=[x[k, i]],
                y=[y[k, i]],
                mode="markers",
                marker=dict(color=colors[i], size=10),
                name=labels[i],
                showlegend=bool(k == frame_indices[0]),
            ))

        frames.append(go.Frame(data=data, name=str(k)))

    fig.frames = frames

    for i in range(3):
        fig.add_trace(go.Scatter(
            x=[x[0, i]],
            y=[y[0, i]],
            mode="markers",
            marker=dict(color=colors[i], size=10),
            name=labels[i],
        ))

    fig.update_layout(
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {"label": "Play", "method": "animate",
                 "args": [None, {"frame": {"duration": 40, "redraw": True},
                                 "fromcurrent": True}]},
                {"label": "Pause", "method": "animate",
                 "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                   "mode": "immediate"}]},
            ],
            "x": 0.1, "y": -0.1
        }]
    )

else:
    for i in range(3):
        fig.add_trace(go.Scatter(
            x=x[:, i], y=y[:, i],
            mode="lines",
            line=dict(color=colors[i], width=2),
            name=f"{labels[i]} path",
        ))
        fig.add_trace(go.Scatter(
            x=[x[-1, i]], y=[y[-1, i]],
            mode="markers",
            marker=dict(color=colors[i], size=10),
            name=f"{labels[i]} final",
        ))

max_extent = np.max(np.abs(positions)) * 1.1
fig.update_layout(
    width=800, height=800,
    xaxis=dict(scaleanchor="y", scaleratio=1,
               range=[-max_extent, max_extent]),
    yaxis=dict(range=[-max_extent, max_extent]),
    margin=dict(l=10, r=10, t=40, b=40),
    title=f"Three‑Body Orbit — {preset_name}",
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
### Notes
- The Velocity Verlet integrator is symplectic and preserves energy well.
- The Lagrange equilateral solution is the only truly stable 3‑body configuration.
- The figure‑eight and criss‑cross orbits are periodic but sensitive to numerical drift.
""")
