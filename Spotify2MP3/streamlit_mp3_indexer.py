import streamlit as st
import os

def index_mp3_files(folder_path):
    """
    Indexes all MP3 files in the given folder path and its subfolders.
    Returns a list of absolute paths to the MP3 files.
    """
    mp3_files = []
    if not os.path.isdir(folder_path):
        return mp3_files, f"Error: Folder '{folder_path}' not found."

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".mp3"):
                mp3_files.append(os.path.join(root, file))
    return mp3_files, None

# --- Streamlit App Layout ---
st.set_page_config(page_title="MP3 Folder Indexer", page_icon="🎵")

st.title("🎵 Local MP3 Folder Indexer")
st.write("Enter a local folder path on the server to list all MP3 files within it and its subfolders.")

# Text input for the folder path
folder_path_input = st.text_input("Enter folder path (e.g., /path/to/your/music or C:\\Users\\YourUser\\Music)")

if st.button("Index MP3 Files"):
    if not folder_path_input:
        st.warning("Please enter a folder path.")
    else:
        mp3_files, error_message = index_mp3_files(folder_path_input)

        if error_message:
            st.error(error_message)
        elif not mp3_files:
            st.info(f"No MP3 files found in '{folder_path_input}'.")
        else:
            st.success(f"Found {len(mp3_files)} MP3 files in '{folder_path_input}':")
            for mp3_file in mp3_files:
                st.write(f"- {mp3_file}")