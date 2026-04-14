import streamlit as st
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def authenticate_gdrive():
    """Authenticates the user and returns the Drive service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                st.error("Error: 'credentials.json' not found. Please provide it to authenticate.")
                st.stop()
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)

def list_mp3_recursive(service, folder_id, current_path=""):
    """Recursively finds all MP3 files starting from folder_id."""
    mp3_list = []
    
    # Query for both mp3 files and subfolders
    query = f"'{folder_id}' in parents and (mimeType = 'audio/mpeg' or mimeType = 'application/vnd.google-apps.folder') and trashed = false"
    
    results = service.files().list(
        q=query, fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])

    for item in items:
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            # It's a folder, dive deeper
            subfolder_files = list_mp3_recursive(service, item['id'], f"{current_path}/{item['name']}")
            mp3_list.extend(subfolder_files)
        else:
            # It's an MP3 file
            mp3_list.append(f"{current_path}/{item['name']}")
            
    return mp3_list

# --- Streamlit App Layout ---
st.set_page_config(page_title="GDrive MP3 Indexer", page_icon="☁️")

st.title("☁️ Google Drive MP3 Indexer")
st.write("""
    This app indexes MP3 files from a specific Google Drive folder. 
    You need to provide the **Folder ID** (the long string of characters in the URL when you open the folder in Drive).
""")

# Input for the Folder ID
target_folder_id = st.text_input("Enter Google Drive Folder ID", placeholder="e.g., 1abc123456789...")

if st.button("Authenticate & Index"):
    if not target_folder_id:
        st.warning("Please enter a Folder ID.")
    else:
        try:
            with st.spinner("Authenticating..."):
                service = authenticate_gdrive()
            
            with st.spinner("Indexing files (this may take a moment for large directories)..."):
                # Get the root folder name for the display path
                root_folder = service.files().get(fileId=target_folder_id, fields="name").execute()
                all_mp3s = list_mp3_recursive(service, target_folder_id, root_folder['name'])

            if not all_mp3s:
                st.info("No MP3 files found in that folder or its subdirectories.")
            else:
                st.success(f"Successfully indexed {len(all_mp3s)} files.")
                
                # Display results in a searchable dataframe or list
                st.write("### Found Files:")
                for path in sorted(all_mp3s):
                    st.text(path)
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.info("Ensure the Folder ID is correct and you have shared access to it.")
