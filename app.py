import streamlit as st
import json
from utils import syllabus, roadmap, llm_interaction, progress
from templates import home, study, progress  # Import the page functions
from pymongo import MongoClient

# MongoDB Connection (no authentication for now)
client = MongoClient("mongodb://localhost:27017/")
db = client["study_buddy"]
users = db["users"]

# Initialize session state for user data and page
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Page navigation (dynamically updated)
page_options = ["Home", "Study", "Progress"]
if "syllabus" in st.session_state.user_data and not st.session_state.user_data.get("roadmap"):
    page_options = ["Home", "Generate Roadmap", "Progress"]
elif "roadmap" in st.session_state.user_data:
    page_options = ["Home", "Study", "Progress"]

st.session_state.page = st.sidebar.selectbox("Navigation", page_options, index=page_options.index(st.session_state.page))

if st.session_state.page == "Home":
    home.home_page()

elif st.session_state.page == "Generate Roadmap":
    if "syllabus" in st.session_state.user_data:
        st.title("Generating Roadmap...")
        roadmap_data = roadmap.generate_roadmap(st.session_state.user_data["syllabus"])
        st.session_state.user_data["roadmap"] = roadmap_data
        users.update_one({"username": st.session_state.user_data["username"]}, {"$set": {"roadmap": roadmap_data}})
        st.success("Roadmap generated successfully!")
        st.session_state.page = "Study"  # Automatically switch to the Study page

elif st.session_state.page == "Study":
    study.study_page(st.session_state.user_data, st.session_state.user_data.get("roadmap", []))

elif st.session_state.page == "Progress":
    progress.progress_page(st.session_state.user_data, st.session_state.user_data.get("roadmap", []))

# Error handling
@st.cache_data()
def get_error_message():
    return ""

if "error_message" not in st.session_state:
    st.session_state.error_message = ""

try:
    pass  # No additional code needed here for now
except Exception as e:
    error_message = str(e)
    if error_message != st.session_state.error_message:
        st.session_state.error_message = error_message
        st.error(error_message)