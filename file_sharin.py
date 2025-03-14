import streamlit as st
import os
import shutil
import uuid
from pathlib import Path

# Configuration
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE_MB = 1024  # 1GB

# Ensure the upload directory exists
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def save_uploaded_file(uploaded_file):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, file_id + "_" + uploaded_file.name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)
    return file_path, file_id + "_" + uploaded_file.name

def list_files():
    files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    return files

def delete_file(file_name):
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

# Streamlit UI
st.set_page_config(page_title="File Sharing System", layout="wide")
st.title("📂 File Sharing System")

# Upload Section
st.header("Upload a File")
uploaded_file = st.file_uploader("Choose a file", type=None, accept_multiple_files=False)

if uploaded_file:
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error("File size exceeds 1GB limit.")
    else:
        file_path, file_name = save_uploaded_file(uploaded_file)
        st.success(f"File uploaded successfully: {uploaded_file.name}")

# File List Section
st.header("📁 Uploaded Files")
files = list_files()
if files:
    for file in files:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(file)
        
        with open(os.path.join(UPLOAD_FOLDER, file), "rb") as f:
            col2.download_button(
                label="⬇️ Download",
                data=f,
                file_name=file,
                mime="application/octet-stream"
            )
        
        if col3.button("🗑️ Delete", key=file):
            delete_file(file)
            st.rerun()
)
else:
    st.info("No files uploaded yet.")
