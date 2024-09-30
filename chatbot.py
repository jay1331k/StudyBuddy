import streamlit as st
import uuid
from typing import List, Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
import hashlib
import os

from file_processing import StudyMaterialProcessor, LOADERS
from ai_functions import analyze_syllabus, generate_roadmap, get_answer_and_explanation
from persistence import load_chatbots, save_chatbots, get_chatbot_by_id

# --- Load environment variables (API keys, etc.) ---
load_dotenv()
llm = genai.GenerativeModel('gemini-1.0-pro-latest')
google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

# --- Directory and File Management (Shared with app.py) ---
CHATBOTS_DIR = "chatbots"
EMBEDDINGS_DIR = "embeddings"

# --- Global Objects and Initialization ---
study_material_processor = StudyMaterialProcessor(embedding_model="text-embedding-gecko-001")
chatbots = load_chatbots()

# --- Utility Functions ---
def display_error(message: str):
    """Displays an error message with Streamlit."""
    st.error(message)

def display_warning(message: str):
    """Displays a warning message with Streamlit."""
    st.warning(message)



# --- Chatbot Management Functions ---
def create_new_chatbot(chatbots: List[Dict]) -> None:
    """Guides the user through creating a new chatbot."""
    topic = st.text_input("Chatbot Topic (e.g., Calculus I):")

    if st.button("Create"):
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
            st.session_state.selected_chatbot_id = new_chatbot['chatbot_id'] 
            st.session_state.chatbots = chatbots # Important: Update session state 
            st.success(f"Chatbot '{topic}' created!")
            st.rerun()  # Essential to refresh the app
        else:
            display_warning("Please enter a topic for your chatbot.")


def process_syllabus(chatbot: Dict) -> None:
    """Handles syllabus upload and analysis for a chatbot."""
    upload_choice = st.radio(
        "How would you like to upload your syllabus?",
        ("Upload file", "Paste text")
    )

    syllabus_text = None
    if upload_choice == "Upload file":
        uploaded_syllabus = st.file_uploader(
            "Choose a file (PDF/DOC)", type=["pdf", "doc", "docx"]
        )
        if uploaded_syllabus:
            extracted_data = study_material_processor.extract_text_from_file(uploaded_syllabus)
            if extracted_data:
                syllabus_text = "\n\n".join([page.page_content for page in extracted_data])
            else:
                display_warning("No text could be extracted from the uploaded file.")
    elif upload_choice == "Paste text":
        syllabus_text = st.text_area("Syllabus Text", height=100)

    if syllabus_text and st.button("Analyze Syllabus"):
        with st.spinner("Analyzing syllabus..."):
            try:
                chatbot['syllabus_data'] = analyze_syllabus(syllabus_text, llm)
                st.success("Syllabus analyzed!")
            except Exception as e:
                display_error(f"An error occurred while analyzing the syllabus: {e}")

def generate_study_roadmap(chatbot: Dict[str, any]) -> None:
    """Generates and displays a study roadmap."""
    if chatbot['syllabus_data'] and st.button("Generate Roadmap"):
        with st.spinner("Generating your study roadmap..."):
            try:
                relevant_topics = chatbot['syllabus_data'].get("main_topics", [])
                if chatbot.get('embedding_id'):
                    relevant_text = study_material_processor.get_relevant_text(
                        f"Provide information related to these topics: {', '.join(relevant_topics)}",
                        chatbot['embedding_id'],
                        chatbot['chatbot_id']
                    )
                else:
                    relevant_text = "No study materials processed yet. Upload files to improve roadmap."

                chatbot['roadmap'] = generate_roadmap(
                    chatbot['syllabus_data'], relevant_text, llm
                )
                st.success("Roadmap generated!")
                with st.expander("View Roadmap"):
                    st.write(chatbot['roadmap'])
            except Exception as e:
                display_error(f"An error occurred while generating the roadmap: {e}")

def run_chatbot(chatbot: Dict[str, any]) -> None:
    """Main function to run the selected chatbot."""
    st.header(f"AI Study Buddy: {chatbot['topic']}")

    display_chatbot_status(chatbot)

    # --- Load embeddings if they exist ---
    faiss_index = None  
    if chatbot.get('embedding_id'):
        faiss_index = study_material_processor.load_faiss_index(chatbot['embedding_id'], chatbot['chatbot_id'])
        print("FAISS Index Loaded:", faiss_index)  # Debug: Check if the index loads

    # --- Chat Interface ---
    st.header("Ask Your Study Questions")
    user_question = st.text_input("Your Question:", key=f"question_{chatbot['chatbot_id']}")

    # Use session_state to ensure the check happens after user input
    if 'question_{}'.format(chatbot['chatbot_id']) in st.session_state: 
        if st.session_state['question_{}'.format(chatbot['chatbot_id'])].strip():
            with st.spinner("Thinking..."):
                try:
                    if faiss_index:
                        relevant_text = study_material_processor.get_relevant_text(
                            st.session_state['question_{}'.format(chatbot['chatbot_id'])], 
                            chatbot['embedding_id'], chatbot['chatbot_id']
                        )
                        print("Relevant Text:", relevant_text)  # Debug: Check if relevant text is retrieved

                        response = get_answer_and_explanation(
                            st.session_state['question_{}'.format(chatbot['chatbot_id'])], 
                            relevant_text, llm
                        )
                    else:
                        response = get_answer_and_explanation(
                            st.session_state['question_{}'.format(chatbot['chatbot_id'])], 
                            None, llm 
                        )
                        st.warning(
                            "This chatbot doesn't have any uploaded content yet. To improve its responses, upload your syllabus and study materials."
                        )
                    st.write("Chatbot:", response)
                except Exception as e:
                    display_error(f"An error occurred with the Google Generative AI API: {e}")
                except FileNotFoundError as e:
                    display_error(f"Could not find the embedding file: {e}")
                except Exception as e:
                    display_error(f"An unexpected error occurred: {e}")
                    # Log the error here
    else:
        display_warning("Please enter a valid question.")

# --- Functions for File and Syllabus Processing ---
def process_uploaded_files(uploaded_files: List, chatbot: Dict[str, any], embedding_id: str) -> None: 
    if uploaded_files:

        study_material_processor.process_uploaded_files(uploaded_files, chatbot['chatbot_id'], embedding_id)
        chatbot['study_materials'][f"processed_{chatbot['chatbot_id']}"] = True
        save_chatbots(chatbots)

        st.sidebar.success("Files processed successfully!")


def process_uploaded_syllabus(uploaded_syllabus, chatbot: Dict[str, any]) -> None:
    if uploaded_syllabus:
        extracted_data = study_material_processor.extract_text_from_file(uploaded_syllabus)
        if extracted_data:
            syllabus_text = "\n\n".join([page.page_content for page in extracted_data])
            with st.sidebar.status("Analyzing syllabus..."):
                try:
                    chatbot['syllabus_data'] = analyze_syllabus(syllabus_text, llm)
                    st.sidebar.success("Syllabus analyzed!")
                except Exception as e:
                    display_error(f"An error occurred while analyzing the syllabus: {e}")
        else:
            display_warning("No text could be extracted from the uploaded file.")


# --- Chatbot Status Display Function (moved from app.py) ---
def display_chatbot_status(chatbot):
    """Displays the status of a chatbot, including embedding information."""

    # Check if syllabus is analyzed
    if chatbot.get('syllabus_data'):
        st.success("Syllabus analyzed!")
    else:
        st.warning("Syllabus not yet analyzed. Please upload your syllabus.")

    # Check for uploaded files and embedding status
    if chatbot.get('embedding_id'):
        embedding_path = os.path.join(
            EMBEDDINGS_DIR, f"index_{chatbot['embedding_id']}.faiss"
        )
        if os.path.exists(embedding_path):
            st.success("Study materials processed and ready to use!")
        else:
            st.warning(
                "Study materials were processed previously, but embeddings not found. Please re-upload."
            )
    else:
        st.warning(
            "No study materials processed. Upload files to enable AI responses."
        )  