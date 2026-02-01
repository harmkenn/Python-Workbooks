import streamlit as st
import os
import tempfile
import zipfile
import io
from moviepy import AudioFileClip

def convert_mp4_to_mp3(uploaded_file):
    """
    Converts an uploaded MP4 file to MP3 format.
    Returns the MP3 binary data and the new filename.
    """
    # Create a temporary file to save the uploaded MP4
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_mp4:
        tmp_mp4.write(uploaded_file.getvalue())
        tmp_mp4_path = tmp_mp4.name

    # Define the output MP3 path
    tmp_mp3_path = tmp_mp4_path.replace(".mp4", ".mp3")
    
    try:
        # Load the video file
        video_clip = AudioFileClip(tmp_mp4_path)
        
        # Write the audio to the MP3 file
        # logger=None suppresses the moviepy console output
        video_clip.write_audiofile(tmp_mp3_path, logger=None)
        video_clip.close()

        # Read the generated MP3 file into memory
        with open(tmp_mp3_path, "rb") as f:
            mp3_data = f.read()
            
        # Generate new filename
        original_name = uploaded_file.name
        new_filename = os.path.splitext(original_name)[0] + ".mp3"
        
        return mp3_data, new_filename

    except Exception as e:
        st.error(f"Error converting {uploaded_file.name}: {e}")
        return None, None
        
    finally:
        # Cleanup temporary files
        if os.path.exists(tmp_mp4_path):
            os.remove(tmp_mp4_path)
        if os.path.exists(tmp_mp3_path):
            os.remove(tmp_mp3_path)

# --- Streamlit App Layout ---
st.set_page_config(page_title="MP4 to MP3 Converter", page_icon="🎵")

st.title("🎵 Batch MP4 to MP3 Converter")
st.write("Upload your MP4 video files below to extract the audio.")

# File uploader widget
uploaded_files = st.file_uploader(
    "Choose MP4 files", 
    type=["mp4"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"**{len(uploaded_files)}** file(s) uploaded.")
    
    if st.button("Start Conversion"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        converted_files = []

        for i, file in enumerate(uploaded_files):
            status_text.text(f"Converting {file.name}...")
            
            mp3_data, mp3_name = convert_mp4_to_mp3(file)
            
            if mp3_data:
                converted_files.append({"name": mp3_name, "data": mp3_data})
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.text("Conversion complete!")
        
        if converted_files:
            st.success(f"Successfully converted {len(converted_files)} files.")
            
            # If only one file, show direct download button
            if len(converted_files) == 1:
                file = converted_files[0]
                st.download_button(
                    label=f"Download {file['name']}",
                    data=file['data'],
                    file_name=file['name'],
                    mime="audio/mpeg"
                )
            # If multiple files, create a ZIP archive
            else:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for file in converted_files:
                        zf.writestr(file['name'], file['data'])
                
                st.download_button(
                    label="Download All (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="converted_mp3s.zip",
                    mime="application/zip"
                )
