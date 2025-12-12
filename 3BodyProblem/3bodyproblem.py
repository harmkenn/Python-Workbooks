import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Three-Body Problem Playground", layout="wide")

st.title("Three-Body Problem Playground")
st.write(
    "Watch three gravitationally interacting bodies dance in 2D. "
    "This is a simple numerical simulation of the classic three-body problem. "
    "You can randomize initial conditions or tweak them yourself."
)

# -----------------------------
# Physics helpers
# -----------------------------
G = 1.0  # gravitational constant (scaled units)

def accelerations(positions, masses):
    """
    Compute accelerations on each body due to gravity from the others.
    positions: (3, 2) array
    masses: (3,) array
    return: (3, 2) accelerations
    """
    acc = np.zeros_like(positions)
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            r_vec = positions[j] - positions[i]
            dist_sq = np.dot(r_vec, r_vec) + 1e-6  # softening to avoid singularities
            dist = np.sqrt(dist_sq)
            acc[i] += G * masses[j] * r_vec / (dist_sq * dist)
    return acc

def simulate_three_body(pos_init, vel_init, masses, dt, steps):
    """
    Velocity Verlet integration for three-body motion in 2D.
    pos_init, vel_init: (3, 2)
    masses: (3,)
    returns: positions over time, shape (steps, 3, 2)
    """
    positions = np.zeros((steps, 3, 2))
    pos = pos_init.copy()
    vel = vel_init.copy()

    acc = accelerations(pos, masses)

    for t in range(steps):
        positions[t] = pos

        # velocity Verlet
        pos_new = pos + vel * dt + 0.5 * acc * dt * dt
        acc_new = accelerations(pos_new, masses)
        vel_new = vel + 0.5 * (acc + acc_new) * dt

        pos, vel, acc = pos_new, vel_new, acc_new

    return positions

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Simulation settings")

with st.sidebar.expander("Initial conditions", expanded=True):
    randomize = st.checkbox("Randomize initial conditions each run", value=True)

    mass1 = st.slider("Mass 1", 0.5, 5.0, 1.0, 0.1)
    mass2 = st.slider("Mass 2", 0.5, 5.0, 1.0, 0.1)
    mass3 = st.slider("Mass 3", 0.5, 5.0, 1.0, 1.0)

    # Only used if randomize is False
    x1 = st.number_input("Body 1 - x", -5.0, 5.0, -1.0, 0.1)
    y1 = st.number_input("Body 1 - y", -5.0, 5.0, 0.0, 0.1)
    vx1 = st.number_input("Body 1 - vx", -3.0, 3.0, 0.0, 0.1)
    vy1 = st.number_input("Body 1 - vy", -3.0, 3.0, 0.5, 0.1)

    x2 = st.number_input("Body 2 - x", -5.0, 5.0, 1.0, 0.1)
    y2 = st.number_input("Body 2 - y", -5.0, 5.0, 0.0, 0.1)
    vx2 = st.number_input("Body 2 - vx", -3.0, 3.0, 0.0, 0.1)
    vy2 = st.number_input("Body 2 - vy", -3.0, 3.0, -0.5, 0.1)

    x3 = st.number_input("Body 3 - x", -5.0, 5.0, 0.0, 0.1)
    y3 = st.number_input("Body 3 - y", -5.0, 5.0, 0.8, 0.1)
    vx3 = st.number_input("Body 3 - vx", -3.0, 3.0, -0.5, 0.1)
    vy3 = st.number_input("Body 3 - vy", -3.0, 3.0, 0.0, 0.1)

with st.sidebar.expander("Integrator & visualization", expanded=True):
    total_time = st.slider("Total time (arbitrary units)", 10.0, 200.0, 80.0, 5.0)
    dt = st.slider("Time step", 0.001, 0.05, 0.01, 0.001)
    trail_fraction = st.slider("Trail length (fraction of total)", 0.05, 1.0, 0.4, 0.05)
    animate = st.checkbox("Animate evolution", value=True)

steps = int(total_time / dt)
trail_steps = max(1, int(trail_fraction * steps))

st.sidebar.write(f"Total steps: {steps}")

# -----------------------------
# Build initial conditions
# -----------------------------
rng = np.random.default_rng()

masses = np.array([mass1, mass2, mass3])

if randomize:
    # Random positions in a disk, random velocities with small magnitude
    r = rng.uniform(0.2, 2.0, size=3)
    theta = rng.uniform(0, 2 * np.pi, size=3)
    pos_init = np.stack([r * np.cos(theta), r * np.sin(theta)], axis=1)

    vel_dir = rng.uniform(0, 2 * np.pi, size=3)
    vel_mag = rng.uniform(0.0, 1.0, size=3)
    vel_init = np.stack([vel_mag * np.cos(vel_dir), vel_mag * np.sin(vel_dir)], axis=1)

    # Subtract center-of-mass velocity so system isn't drifting too fast
    total_mass = masses.sum()
    com_vel = (masses[:, None] * vel_init).sum(axis=0) / total_mass
    vel_init -= com_vel
else:
    pos_init = np.array([[x1, y1],
                         [x2, y2],
                         [x3, y3]], dtype=float)
    vel_init = np.array([[vx1, vy1],
                         [vx2, vy2],
                         [vx3, vy3]], dtype=float)

# -----------------------------
# Run simulation
# -----------------------------
with st.spinner("Simulating three-body system..."):
    positions = simulate_three_body(pos_init, vel_init, masses, dt, steps)

# positions shape: (steps, 3, 2)
x = positions[:, :, 0]
y = positions[:, :, 1]

# -----------------------------
# Build static or animated plot
# -----------------------------
colors = ["#ff595e", "#1982c4", "#8ac926"]
labels = ["Body 1", "Body 2", "Body 3"]

fig = go.Figure()

if animate:
    # We'll create frames that progressively reveal more of the trajectory
    frame_indices = np.linspace(0, steps - 1, num=min(200, steps), dtype=int)
    frames = []

    for k in frame_indices:
        start = max(0, k - trail_steps)
        data = []
        # Paths (trails)
        for i in range(3):
            data.append(
                go.Scatter(
                    x=x[start:k+1, i],
                    y=y[start:k+1, i],
                    mode="lines",
                    line=dict(color=colors[i], width=2),
                    showlegend=False,
                )
            )
        # Current positions
        for i in range(3):
            data.append(
                go.Scatter(
                    x=[x[k, i]],
                    y=[y[k, i]],
                    mode="markers",
                    marker=dict(color=colors[i], size=10),
                    name=labels[i],
                    showlegend=bool(k == frame_indices[0]),
                )
            )

        frames.append(go.Frame(data=data, name=str(k)))

    # Add initial (first frame) data
    fig.add_trace(
        go.Scatter(
            x=x[:1, 0],
            y=y[:1, 0],
            mode="markers",
            marker=dict(color=colors[0], size=10),
            name=labels[0],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x[:1, 1],
            y=y[:1, 1],
            mode="markers",
            marker=dict(color=colors[1], size=10),
            name=labels[1],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x[:1, 2],
            y=y[:1, 2],
            mode="markers",
            marker=dict(color=colors[2], size=10),
            name=labels[2],
        )
    )

    fig.frames = frames

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=40, redraw=True),
                                fromcurrent=True,
                                transition=dict(duration=0),
                            ),
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],
                            dict(frame=dict(duration=0, redraw=False),
                                 mode="immediate",
                                 transition=dict(duration=0)),
                        ],
                    ),
                ],
                x=0.1,
                y=-0.1,
                xanchor="left",
                yanchor="top",
            )
        ]
    )

else:
    # Static: plot full trajectories
    for i in range(3):
        fig.add_trace(
            go.Scatter(
                x=x[:, i],
                y=y[:, i],
                mode="lines",
                line=dict(color=colors[i], width=2),
                name=f"{labels[i]} path",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[x[-1, i]],
                y=[y[-1, i]],
                mode="markers",
                marker=dict(color=colors[i], size=10),
                name=f"{labels[i]} final",
            )
        )

# Common layout
max_extent = np.max(np.abs(positions)) * 1.1 + 1e-6
fig.update_layout(
    width=800,
    height=800,
    xaxis=dict(
        scaleanchor="y",
        scaleratio=1,
        range=[-max_extent, max_extent],
        title="x",
    ),
    yaxis=dict(
        range=[-max_extent, max_extent],
        title="y",
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),
    margin=dict(l=10, r=10, t=40, b=40),
    title="Three-Body Orbits in 2D (Toy Model)",
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
**Notes:**

- Units here are arbitrary and rescaled so things look nice.
- The system is chaotic: tiny changes in initial conditions can lead to wildly different motion.
- Try turning off *Randomize initial conditions* and building your own tri‑star system, slingshots, or escape trajectories.
"""
)
