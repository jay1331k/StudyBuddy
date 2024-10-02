import streamlit as st
from pymongo import MongoClient
from utils import syllabus, roadmap
import markdown  # Import markdown library
import json 
import yaml


# MongoDB Connection (no authentication for now)
client = MongoClient("mongodb://localhost:27017/")
db = client["study_buddy"]
users = db["users"]

def home_page():
    st.title("Welcome to Your Personalized Tutor")

    # User login (simplified for now - no authentication)
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False 

    if not st.session_state.logged_in: # Show login form only if not logged in
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                # Automatically log in the user (no password check for now)
                st.session_state.user_data = {"username": username, "password": password, "syllabus": {}, "roadmap": [], "progress": {}}
                st.session_state.logged_in = True  # Set logged_in to True
                st.success("Logged in successfully!")
                st.rerun() # Rerun the script to update the page

    if st.session_state.logged_in: # Show course details only if logged in
        st.write(f"Welcome, {st.session_state.user_data['username']}!")

        # Course details input (only after login)
        with st.form("course_details"):
            course_topic = st.text_input("Enter Course Topic (e.g., Machine Learning)")
            difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])
            focus_topics = st.text_area("Enter Focus Topics (optional, comma-separated)")
            generate_syllabus_button = st.form_submit_button("Generate Syllabus")

            if generate_syllabus_button and course_topic:
                syllabus_data = syllabus.generate_syllabus(course_topic, difficulty, focus_topics)
                if syllabus_data:
                    st.session_state.user_data["syllabus"] = syllabus_data
                    users.update_one({"username": st.session_state.user_data["username"]}, {"$set": {"syllabus": syllabus_data}})
                    st.success("Syllabus generated successfully!")

        if st.session_state.user_data.get("syllabus"):
            st.write("## Syllabus:")

            syllabus_data = st.session_state.user_data["syllabus"]

            syllabus_markdown = ""
            for unit in syllabus_data["units"]:
                syllabus_markdown += f"**Unit {unit['unit_number']}: {unit['unit_title']}**\n"
                for topic in unit["topics"]:
                    syllabus_markdown += f"* **Topic {topic['topic_number']}: {topic['topic_title']}**\n"
                    for subtopic in topic["subtopics"]:
                        syllabus_markdown += f"    * {subtopic}\n"
                syllabus_markdown += "\n" # Add a newline for spacing

            st.markdown(syllabus_markdown) 

            if st.button("Generate Roadmap"):
                roadmap_data = roadmap.generate_roadmap(st.session_state.user_data["syllabus"])
                st.session_state.user_data["roadmap"] = roadmap_data
                users.update_one({"username": st.session_state.user_data["username"]}, {"$set": {"roadmap": roadmap_data}})
                st.success("Roadmap generated successfully!")
