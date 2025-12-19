import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np

st.title("Three‑Body Initial Conditions Editor v4.3")

# -------------------------------
# Session State Initialization
# -------------------------------
if "step" not in st.session_state:
    st.session_state.step = 0  # 0–5 (circle, line, circle, line, circle, line)
if "bodies" not in st.session_state:
    st.session_state.bodies = []  # list of (x, y)
if "velocities" not in st.session_state:
    st.session_state.velocities = []  # list of (vx, vy)

# -------------------------------
# Determine Current Mode
# -------------------------------
is_circle_step = (st.session_state.step % 2 == 0)
mode = "circle" if is_circle_step else "line"

st.subheader(f"Step {st.session_state.step + 1} of 6")
if is_circle_step:
    st.write("Draw a **circle** to place the next body.")
else:
    st.write("Draw a **line** to set the velocity for the nearest body.")

# -------------------------------
# Canvas
# -------------------------------
canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.3)",
    stroke_width=2,
    stroke_color="red",
    background_color="white",
    height=500,
    width=500,
    drawing_mode=mode,
    key=f"canvas_step_{st.session_state.step}",
)

# -------------------------------
# Process Canvas Output
# -------------------------------
if canvas_result.json_data is not None:
    objects = canvas_result.json_data.get("objects", [])

    # Only process if a new shape was drawn
    if len(objects) > st.session_state.step:

        new_obj = objects[-1]

        # -------------------------------
        # Circle → Body Position
        # -------------------------------
        if new_obj["type"] == "circle" and is_circle_step:
            cx = new_obj["left"] + new_obj["radius"]
            cy = new_obj["top"] + new_obj["radius"]
            st.session_state.bodies.append((cx, cy))
            st.session_state.step += 1  # auto‑advance

        # -------------------------------
        # Line → Velocity Vector
        # -------------------------------
        elif new_obj["type"] == "line" and not is_circle_step:
            x1, y1, x2, y2 = new_obj["x1"], new_obj["y1"], new_obj["x2"], new_obj["y2"]

            # Compute midpoint to find nearest body
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            bodies = np.array(st.session_state.bodies)
            dists = np.linalg.norm(bodies - np.array([mx, my]), axis=1)
            nearest_idx = np.argmin(dists)

            # Velocity vector
            vx = x2 - x1
            vy = y2 - y1

            st.session_state.velocities.append((vx, vy))
            st.session_state.step += 1  # auto‑advance

# -------------------------------
# Display Current State
# -------------------------------
st.write("Bodies:", st.session_state.bodies)
st.write("Velocities:", st.session_state.velocities)

# -------------------------------
# Ready to Run Simulation?
# -------------------------------
ready = (len(st.session_state.bodies) == 3 and
         len(st.session_state.velocities) == 3)

if ready:
    st.success("All bodies and velocities defined. Ready to run simulation.")

    if st.button("Run Simulation"):
        pos_init = np.array(st.session_state.bodies)
        vel_init = np.array(st.session_state.velocities)

        st.session_state.pos_init = pos_init
        st.session_state.vel_init = vel_init

        st.write("✅ Initial conditions captured.")
        st.write("Positions:", pos_init)
        st.write("Velocities:", vel_init)

        # You can now call your physics engine here
        # positions = simulate(pos_init, vel_init, masses, dt, steps)
