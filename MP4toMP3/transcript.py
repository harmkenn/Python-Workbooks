import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator
import tempfile
import os
from moviepy import AudioFileClip
import math

st.title("🎧 Italian Audio Transcriber & Translator (Free)")

uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    if st.button("Transcribe"):
        # Create a temporary file to save the uploaded MP3
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_mp3:
            tmp_mp3.write(uploaded_file.getvalue())
            tmp_mp3_path = tmp_mp3.name

        # Define WAV path for conversion
        tmp_wav_path = tmp_mp3_path.replace(".mp3", ".wav")

        try:
            with st.spinner("Processing audio..."):
                # Convert MP3 to WAV using moviepy
                audioclip = AudioFileClip(tmp_mp3_path)
                
                duration = audioclip.duration
                chunk_duration = 60 # seconds
                chunks = math.ceil(duration / chunk_duration)
                
                italian_text_parts = []
                recognizer = sr.Recognizer()
                progress_bar = st.progress(0)
                
                for i in range(chunks):
                    start = i * chunk_duration
                    end = min((i + 1) * chunk_duration, duration)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_chunk:
                        chunk_path = tmp_chunk.name
                        
                    subclip = audioclip.subclipped(start, end)
                    subclip.write_audiofile(chunk_path, logger=None, codec='pcm_s16le')
                    
                    with sr.AudioFile(chunk_path) as source:
                        audio_data = recognizer.record(source)
                        try:
                            text = recognizer.recognize_google(audio_data, language="it-IT")
                            italian_text_parts.append(text)
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError as e:
                            st.error(f"API Error: {e}")
                            
                    if os.path.exists(chunk_path):
                        os.remove(chunk_path)
                    progress_bar.progress((i + 1) / chunks)
                
                audioclip.close()
                italian_text = " ".join(italian_text_parts)

            st.subheader("📜 Italian Transcript")
            st.write(italian_text)
            st.download_button("Download Italian Transcript", italian_text, file_name="transcript_it.txt")

            with st.spinner("Translating to English..."):
                translator = GoogleTranslator(source='auto', target='en')
                
                # Split text into chunks to avoid 5000 char limit
                chunk_size = 4500
                english_text_parts = []
                for i in range(0, len(italian_text), chunk_size):
                    chunk = italian_text[i:i+chunk_size]
                    english_text_parts.append(translator.translate(chunk))
                
                english_text = " ".join(english_text_parts)

            st.subheader("🇬🇧 English Translation")
            st.write(english_text)
            st.download_button("Download English Translation", english_text, file_name="transcript_en.txt")

        except Exception as e:
            st.error(f"An error occurred: {e}")
        
        finally:
            # Cleanup temporary files
            if os.path.exists(tmp_mp3_path):
                os.remove(tmp_mp3_path)
            if os.path.exists(tmp_wav_path):
                os.remove(tmp_wav_path)
