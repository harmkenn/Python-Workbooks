import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import plotly.graph_objects as go

st.title("Stable Three-Body Problem: Figure-8 Orbit with Fading Trails")
st.write("""
This app simulates the famous **figure-8 orbit** of three equal masses.
The bodies now leave **fading trails** to better visualize their motion.
""")

# ---------------------------------------------
# Parameters
# ---------------------------------------------
G = 1.0
m = 1.0
initial_state = np.array([
    -0.97000436, 0.24308753, 0.466203685, 0.43236573,
     0.0,        0.0,       -0.93240737, -0.86473146,
     0.97000436,-0.24308753,0.466203685, 0.43236573
])

t_end = st.slider("Simulation duration", 1.0, 20.0, 6.0, 0.5)
fps = st.slider("Animation speed (higher = smoother)", 50, 500, 200)
trail_length = st.slider("Trail length (number of steps)", 5, 200, 50)

# ---------------------------------------------
# Three-body differential equations
# ---------------------------------------------
def three_body_equations(t, state):
    x1, y1, vx1, vy1,  x2, y2, vx2, vy2,  x3, y3, vx3, vy3 = state
    def accel(xa, ya, xb, yb):
        dx = xb - xa
        dy = yb - ya
        r3 = (dx*dx + dy*dy)**1.5
        return G * m * dx / r3, G * m * dy / r3
    ax12, ay12 = accel(x1, y1, x2, y2)
    ax13, ay13 = accel(x1, y1, x3, y3)
    ax21, ay21 = accel(x2, y2, x1, y1)
    ax23, ay23 = accel(x2, y2, x3, y3)
    ax31, ay31 = accel(x3, y3, x1, y1)
    ax32, ay32 = accel(x3, y3, x2, y2)
    return [
        vx1, vy1, ax12 + ax13, ay12 + ay13,
        vx2, vy2, ax21 + ax23, ay21 + ay23,
        vx3, vy3, ax31 + ax32, ay31 + ay32
    ]

# ---------------------------------------------
# Solve ODE
# ---------------------------------------------
t_eval = np.linspace(0, t_end, fps * int(t_end))
solution = solve_ivp(
    three_body_equations, [0, t_end], initial_state, t_eval=t_eval,
    rtol=1e-9, atol=1e-9
)

x1, y1 = solution.y[0], solution.y[1]
x2, y2 = solution.y[4], solution.y[5]
x3, y3 = solution.y[8], solution.y[9]

# ---------------------------------------------
# Plotly animation with fading trails
# ---------------------------------------------
fig = go.Figure()

for k in range(len(t_eval)):
    # For fading trail, take last 'trail_length' points
    start_idx = max(0, k - trail_length)
    
    fig.add_trace(go.Scatter(
        x=x1[start_idx:k+1], y=y1[start_idx:k+1],
        mode="lines+markers",
        line=dict(color='red', width=2),
        marker=dict(size=8, color='red'),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=x2[start_idx:k+1], y=y2[start_idx:k+1],
        mode="lines+markers",
        line=dict(color='green', width=2),
        marker=dict(size=8, color='green'),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=x3[start_idx:k+1], y=y3[start_idx:k+1],
        mode="lines+markers",
        line=dict(color='blue', width=2),
        marker=dict(size=8, color='blue'),
        showlegend=False
    ))

fig.update_layout(
    width=700, height=700,
    title="Three-Body Figure-8 Orbit with Fading Trails",
    xaxis=dict(scaleanchor="y", range=[-1.5,1.5]),
    yaxis=dict(range=[-1.5,1.5]),
)

st.plotly_chart(fig)
