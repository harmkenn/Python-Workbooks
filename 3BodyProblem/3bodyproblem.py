import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Function to compute the derivatives for the three-body problem
def three_body_derivatives(t, y, masses):
    # Unpack positions and velocities
    x1, y1, x2, y2, x3, y3, vx1, vy1, vx2, vy2, vx3, vy3 = y
    m1, m2, m3 = masses

    # Compute distances
    r12 = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    r13 = np.sqrt((x3 - x1)**2 + (y3 - y1)**2)
    r23 = np.sqrt((x3 - x2)**2 + (y3 - y2)**2)

    # Compute accelerations
    ax1 = m2 * (x2 - x1) / r12**3 + m3 * (x3 - x1) / r13**3
    ay1 = m2 * (y2 - y1) / r12**3 + m3 * (y3 - y1) / r13**3
    ax2 = m1 * (x1 - x2) / r12**3 + m3 * (x3 - x2) / r23**3
    ay2 = m1 * (y1 - y2) / r12**3 + m3 * (y3 - y2) / r23**3
    ax3 = m1 * (x1 - x3) / r13**3 + m2 * (x2 - x3) / r23**3
    ay3 = m1 * (y1 - y3) / r13**3 + m2 * (y2 - y3) / r23**3

    # Return derivatives
    return [vx1, vy1, vx2, vy2, vx3, vy3, ax1, ay1, ax2, ay2, ax3, ay3]

# Streamlit app
st.title("Three-Body Problem Simulator v1.0")

# Sidebar for masses
st.sidebar.header("Masses")
m1 = st.sidebar.slider("Mass of Body 1", 0.1, 10.0, 1.0)
m2 = st.sidebar.slider("Mass of Body 2", 0.1, 10.0, 1.0)
m3 = st.sidebar.slider("Mass of Body 3", 0.1, 10.0, 1.0)
masses = [m1, m2, m3]

# Initial positions and velocities
st.sidebar.header("Initial Conditions")
initial_positions = st.sidebar.text_input("Initial Positions (x1, y1, x2, y2, x3, y3)", "0, 0, 1, 0, -1, 0")
initial_velocities = st.sidebar.text_input("Initial Velocities (vx1, vy1, vx2, vy2, vx3, vy3)", "0, 0, 0, 1, 0, -1")

# Parse input
try:
    positions = list(map(float, initial_positions.split(",")))
    velocities = list(map(float, initial_velocities.split(",")))
    initial_conditions = positions + velocities
except ValueError:
    st.error("Please enter valid initial conditions.")

# Simulation parameters
st.sidebar.header("Simulation Parameters")
t_span = st.sidebar.slider("Simulation Time", 0.0, 100.0, 10.0)
t_eval = np.linspace(0, t_span, 1000)

# Solve the three-body problem
if st.button("Run Simulation"):
    try:
        solution = solve_ivp(
            three_body_derivatives,
            [0, t_span],
            initial_conditions,
            t_eval=t_eval,
            args=(masses,),
            rtol=1e-9,
            atol=1e-9,
        )

        # Extract positions
        x1, y1, x2, y2, x3, y3 = solution.y[:6]

        # Plot the results
        fig, ax = plt.subplots()
        ax.plot(x1, y1, label="Body 1")
        ax.plot(x2, y2, label="Body 2")
        ax.plot(x3, y3, label="Body 3")
        ax.legend()
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Three-Body Problem Simulation")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")
