from streamlit_drawable_canvas import st_canvas
import streamlit as st

st.title("Canvas Click Test — Place Circles")

canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.3)",
    stroke_width=2,
    stroke_color="red",
    background_color="white",
    height=500,
    width=500,
    drawing_mode="circle",   # ✅ clicking places circles
    key="canvas_test2",
)

st.write("Raw JSON:", canvas_result.json_data)

# Extract circle centers
points = []
if canvas_result.json_data is not None:
    for obj in canvas_result.json_data.get("objects", []):
        if obj["type"] == "circle":
            cx = obj["left"] + obj["radius"]
            cy = obj["top"] + obj["radius"]
            points.append((cx, cy))

st.write("Extracted points:", points)
