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
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["department"] = None

if not st.session_state["authenticated"]:
    st.header("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        department = authenticate(username, password)
        if department:
            st.session_state["authenticated"] = True
            st.session_state["department"] = department
            st.rerun()
        else:
            st.error("Invalid credentials!")
else:
    st.subheader(f"Logged in as: {st.session_state['department']}")
    logout_button = st.button("Logout")
    if logout_button:
        st.session_state["authenticated"] = False
        st.session_state["department"] = None
        st.rerun()
    
    user_folder = os.path.join(BASE_UPLOAD_FOLDER, DEPARTMENTS[st.session_state["department"]])
    global_folder = os.path.join(BASE_UPLOAD_FOLDER, GLOBAL_FOLDER)

    # Upload Section
    st.header("📤 Upload a File")
    uploaded_file = st.file_uploader("Choose a file", type=None, accept_multiple_files=False)
    upload_to_global = st.checkbox("Upload to Global Folder", value=False)

    if uploaded_file and st.session_state.get("file_uploaded") is None:
        if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.error("File size exceeds 1GB limit.")
        else:
            file_id = str(uuid.uuid4())
            target_folder = global_folder if upload_to_global else user_folder
            file_path = os.path.join(target_folder, file_id + "_" + uploaded_file.name)
            
            with open(file_path, "wb") as f:
                shutil.copyfileobj(uploaded_file, f)
            
            folder_name = "Global Folder" if upload_to_global else "Department Folder"
            st.session_state["file_uploaded"] = file_path
            st.success(f"File uploaded successfully to {folder_name}: {uploaded_file.name}")
            st.rerun()
    
    # File List Section
    st.header("📁 Your Department Files & Global Files")
    st.subheader(f"Department: {st.session_state['department']}")
    
    department_files = [f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder, f))]
    global_files = [f for f in os.listdir(global_folder) if os.path.isfile(os.path.join(global_folder, f))]
    
    st.subheader("📁 Your Department Files")
    if department_files:
        for file in department_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(file)
            file_path = os.path.join(user_folder, file)
            with open(file_path, "rb") as f:
                col2.download_button(label="⬇️ Download", data=f, file_name=file, mime="application/octet-stream")
            if col3.button("🗑️ Delete", key=f"dept_{file}"):
                os.remove(file_path)
                st.session_state["deleted"] = True
                st.rerun()
    else:
        st.info("No files uploaded in your department folder.")
    
    st.subheader("🌍 Global Files (Available to All Departments)")
    if global_files:
        for file in global_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(file)
            file_path = os.path.join(global_folder, file)
            with open(file_path, "rb") as f:
                col2.download_button(label="⬇️ Download", data=f, file_name=file, mime="application/octet-stream")
            if col3.button("🗑️ Delete", key=f"global_{file}"):
                os.remove(file_path)
                st.session_state["deleted"] = True
                st.rerun()
    else:
        st.info("No files in the Global folder.")
