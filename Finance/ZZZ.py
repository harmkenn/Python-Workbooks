import streamlit as st

# Initialize the key in session state
if 'clicked' not in st.session_state:
    st.session_state.clicked = {1:False,2:False}

# Function to update the value in session state
def clicked(button):
    st.session_state.clicked[button] = True

# Button with callback function
st.button('First Button', on_click=clicked, args=[1])

# Conditional based on value in session state, not the output
if st.session_state.clicked[1]:
    st.write('The first button was clicked.')
    st.button('Second Button', on_click=clicked, args=[2])
    if st.session_state.clicked[2]:
        st.write('The second button was clicked')