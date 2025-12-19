from streamlit_drawable_canvas import st_canvas
import streamlit as st

st.title("Canvas Test")

canvas_result = st_canvas(
    fill_color="rgba(255, 0, 0, 0.3)",
    stroke_width=2,
    stroke_color="red",
    background_color="white",
    height=500,
    width=500,
    drawing_mode="circle",
    key="canvas",
)

st.write(canvas_result)
