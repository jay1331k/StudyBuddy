import streamlit as st
import uuid
from typing import List, Dict, Optional
import hashlib
import os

from chatbot import (
    create_new_chatbot,
    process_syllabus,
    generate_study_roadmap,
    run_chatbot,
    process_uploaded_files,
    process_uploaded_syllabus,
    display_warning,
    chatbots
)

import os
import json

# --- Directory and File Management ---
CHATBOTS_DIR = "chatbots"
EMBEDDINGS_DIR = "embeddings"

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon=":books:",
    layout="wide"
)

# --- Persistence Functions ---
CHATBOTS_FILE = "chatbots.json"

def load_chatbots():
    """Loads chatbot data from JSON file."""
    if os.path.exists(CHATBOTS_FILE):
        with open(CHATBOTS_FILE, "r") as f:
            return json.load(f)["chatbots"]
    return []

def save_chatbots(chatbots):
    """Saves chatbot data to JSON file."""
    with open(CHATBOTS_FILE, "w") as f:
        json.dump({"chatbots": chatbots}, f)

# --- Main Streamlit App Flow ---
if __name__ == "__main__":
    # Load Chatbots
    chatbots = load_chatbots()

    # --- Header ---
    st.title("AI Study Buddy")

    # --- Sidebar ---
    st.sidebar.title("Chatbot Management")

    # --- Chatbot Actions ---
    action = st.sidebar.selectbox(
        "Choose an action:", ["Select Chatbot", "Create New Chatbot"]
    )

    if action == "Create New Chatbot":
        topic = st.sidebar.text_input("Chatbot Topic (e.g., Calculus I):")
        if st.sidebar.button("Create"):
            if topic:
                new_chatbot = {
                    "chatbot_id": str(uuid.uuid4()),
                    "topic": topic,
                    "syllabus_data": None,
                    "roadmap": None,
                    "study_materials": {}, 
                    "embedding_id": None
                }
                chatbots.append(new_chatbot)
                save_chatbots(chatbots)
                st.sidebar.success(f"Chatbot '{topic}' created!")
                # No need for st.rerun() here
    elif action == "Select Chatbot":
        # --- Chatbot Selection ---
        chatbot_names = [c['topic'] for c in chatbots]
        if chatbot_names:
            selected_chatbot_name = st.sidebar.selectbox(
                "Select a Chatbot:", chatbot_names
            )
            selected_chatbot = next(
                (c for c in chatbots if c['topic'] == selected_chatbot_name), None
            )
            if selected_chatbot:
                st.session_state.selected_chatbot_id = selected_chatbot['chatbot_id']
        else:
            st.sidebar.warning("No chatbots created yet. Create one above!")

    # --- File Upload (in Sidebar) ---
    uploaded_files = st.sidebar.file_uploader(
        "Upload course materials (PDF/DOC)",
        type=["pdf", "doc", "docx"],
        accept_multiple_files=True
    )

    # --- Syllabus Upload (in Sidebar) ---
    uploaded_syllabus = st.sidebar.file_uploader(
        "Upload syllabus (PDF/DOC)", type=["pdf", "doc", "docx"]
    )

    # --- Process Files and Syllabus ---
    if 'selected_chatbot_id' in st.session_state:
        selected_chatbot = next(
            (c for c in chatbots if c['chatbot_id'] == st.session_state.selected_chatbot_id), None
        )
        if selected_chatbot:
            if uploaded_files:  # Check if files were uploaded
                file_hash = hashlib.sha256()
                for uploaded_file in uploaded_files:
                    file_hash.update(uploaded_file.name.encode('utf-8'))
                embedding_id = file_hash.hexdigest()
                selected_chatbot['embedding_id'] = embedding_id

                # Pass embedding_id to process_uploaded_files
                process_uploaded_files(uploaded_files, selected_chatbot, embedding_id)  

            process_uploaded_syllabus(uploaded_syllabus, selected_chatbot)
            save_chatbots(chatbots)  # Save after processing

    # --- Run the selected chatbot ---
    if 'selected_chatbot_id' in st.session_state:
        selected_chatbot = next(
            (c for c in chatbots if c['chatbot_id'] == st.session_state.selected_chatbot_id), None
        )
        if selected_chatbot:
            col2 = st.empty()
            with col2:
                run_chatbot(selected_chatbot)