import streamlit as st
import os
import shutil
import uuid
from pathlib import Path

# Configuration
BASE_UPLOAD_FOLDER = "uploads"
GLOBAL_FOLDER = "global"
DEPARTMENTS = {"AI": "ai", "Dev": "dev", "Testing": "testing"}
MAX_FILE_SIZE_MB = 1024  # 1GB

# Ensure directories exist
for folder in [BASE_UPLOAD_FOLDER, os.path.join(BASE_UPLOAD_FOLDER, GLOBAL_FOLDER)] + [os.path.join(BASE_UPLOAD_FOLDER, dept) for dept in DEPARTMENTS.values()]:
    Path(folder).mkdir(parents=True, exist_ok=True)

# Load credentials from secrets
def load_credentials():
    return st.secrets["credentials"]

def authenticate(username, password):
    credentials = load_credentials()
    if username in credentials and credentials[username]["password"] == password:
        return credentials[username]["department"]
    return None

# Streamlit UI
st.set_page_config(page_title="File Sharing System", layout="wide")
st.title("📂 File Sharing System By Neusco AI Team")

# User Login
st.header("🔑 Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["department"] = None

if login_button:
    department = authenticate(username, password)
    if department:
        st.session_state["authenticated"] = True
        st.session_state["department"] = department
        st.success("Login successful!")
    else:
        st.error("Invalid credentials!")

if st.session_state["authenticated"]:
    user_folder = os.path.join(BASE_UPLOAD_FOLDER, DEPARTMENTS[st.session_state["department"]])
    
    # Upload Section
    st.header("📤 Upload a File")
    uploaded_file = st.file_uploader("Choose a file", type=None, accept_multiple_files=False)
    if uploaded_file:
        if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.error("File size exceeds 1GB limit.")
        else:
            file_id = str(uuid.uuid4())
            file_path = os.path.join(user_folder, file_id + "_" + uploaded_file.name)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(uploaded_file, f)
            st.success(f"File uploaded successfully: {uploaded_file.name}")
    
    # File List Section
    st.header("📁 Your Department Files & Global Files")
    st.subheader(f"Department: {st.session_state['department']}")
    
    department_files = [f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder, f))]
    global_files = [f for f in os.listdir(os.path.join(BASE_UPLOAD_FOLDER, GLOBAL_FOLDER)) if os.path.isfile(os.path.join(BASE_UPLOAD_FOLDER, GLOBAL_FOLDER, f))]
    
    st.subheader("📁 Your Department Files")
    if department_files:
        for file in department_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(file)
            with open(os.path.join(user_folder, file), "rb") as f:
                col2.download_button(label="⬇️ Download", data=f, file_name=file, mime="application/octet-stream")
            if col3.button("🗑️ Delete", key=f"dept_{file}"):
                os.remove(os.path.join(user_folder, file))
                st.rerun()
    else:
        st.info("No files uploaded in your department folder.")
    
    st.subheader("🌍 Global Files (Available to All Departments)")
    if global_files:
        for file in global_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(file)
            with open(os.path.join(BASE_UPLOAD_FOLDER, GLOBAL_FOLDER, file), "rb") as f:
                col2.download_button(label="⬇️ Download", data=f, file_name=file, mime="application/octet-stream")
            if col3.button("🗑️ Delete", key=f"global_{file}"):
                os.remove(os.path.join(BASE_UPLOAD_FOLDER, GLOBAL_FOLDER, file))
                st.rerun()
    else:
        st.info("No files in the Global folder.")
