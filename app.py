import streamlit as st
import json
from utils import syllabus, roadmap, llm_interaction, progress
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["study_buddy"]
users = db["users"]

# Initialize session state for user data
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# Page navigation
page = st.sidebar.selectbox("Navigation", ["Home", "Study", "Progress"])

if page == "Home":
    st.title("Welcome to Your Personalized Tutor")

    # User login/signup (replace with your preferred authentication method)
    username = st.text_input("Username")
    if st.button("Login/Signup"):
        user_data = users.find_one({"username": username})
        if user_data:
            st.session_state.user_data = user_data
        else:
            st.session_state.user_data = {"username": username, "syllabus": {}, "roadmap": [], "progress": {}}
            users.insert_one(st.session_state.user_data)

    if "username" in st.session_state.user_data:
        st.write(f"Welcome, {st.session_state.user_data['username']}!")

        # Course topic and syllabus
        course_topic = st.text_input("Enter Course Topic (e.g., Machine Learning)")
        difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"])
        focus_topics = st.text_area("Enter Focus Topics (optional, comma-separated)")

        if st.button("Generate Syllabus"):
            if course_topic:
                syllabus_data = syllabus.generate_syllabus(course_topic, difficulty, focus_topics)
                st.session_state.user_data["syllabus"] = syllabus_data
                users.update_one({"username": username}, {"$set": {"syllabus": syllabus_data}})
                st.success("Syllabus generated successfully!")

        if st.session_state.user_data.get("syllabus"):
            st.write("## Syllabus:")
            st.json(st.session_state.user_data["syllabus"])

            if st.button("Generate Roadmap"):
                roadmap_data = roadmap.generate_roadmap(st.session_state.user_data["syllabus"])
                st.session_state.user_data["roadmap"] = roadmap_data
                users.update_one({"username": username}, {"$set": {"roadmap": roadmap_data}})
                st.success("Roadmap generated successfully!")

elif page == "Study":
    if "roadmap" in st.session_state.user_data and st.session_state.user_data["roadmap"]:
        roadmap_data = st.session_state.user_data["roadmap"]
        progress_data = st.session_state.user_data.get("progress", {})

        # Step selection
        step_options = [f"Step {step['step_number']}: {step['topic']}" for step in roadmap_data]
        selected_step = st.selectbox("Select Step", step_options)
        selected_step_index = step_options.index(selected_step)
        current_step = roadmap_data[selected_step_index]

        # Display step content and interact with LLM
        st.write(f"## {current_step['topic']}")
        if current_step["step_number"] not in progress_data:
            explanation = llm_interaction.get_explanation(current_step["prompt"])
            st.write(explanation)

            if st.button("Mark as Completed"):
                progress_data[current_step["step_number"]] = True
                st.session_state.user_data["progress"] = progress_data
                users.update_one({"username": st.session_state.user_data["username"]}, {"$set": {"progress": progress_data}})
                st.success("Step marked as completed!")
        else:
            st.write("You have already completed this step.")

    else:
        st.write("Please generate a roadmap first.")

elif page == "Progress":
    if "progress" in st.session_state.user_data and st.session_state.user_data["progress"]:
        progress_data = st.session_state.user_data["progress"]
        roadmap_data = st.session_state.user_data["roadmap"]
        completed_steps = len(progress_data)
        total_steps = len(roadmap_data)
        completion_percentage = (completed_steps / total_steps) * 100

        st.write(f"## Progress: {completion_percentage:.2f}%")
        st.write(f"Completed Steps: {completed_steps}/{total_steps}")

        # Display progress details (e.g., completed steps, scores, etc.)
        # ...

    else:
        st.write("No progress data available yet.")

# Error handling (example)
@st.cache(allow_output_mutation=True)
def get_error_message():
    return ""

if "error_message" not in st.session_state:
    st.session_state.error_message = ""

try:
    # Your code here
    pass
except Exception as e:
    error_message = str(e)
    if error_message != st.session_state.error_message:
        st.session_state.error_message = error_message
        st.error(error_message)