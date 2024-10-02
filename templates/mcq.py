# templates/mcq.py
import streamlit as st
from utils import llm_interaction


def mcq_page(user_data, roadmap_data):
    st.title("MCQ Time!")

    if "roadmap" in user_data and user_data["roadmap"]:
        if "selected_step" not in st.session_state:
            st.session_state.selected_step = 1  # Start at step 1

        step_options = [f"Step {step['step_number']}: {step['topic']}" for step in roadmap_data]
        selected_step_index = st.session_state.selected_step - 1
        selected_step = st.selectbox("Select Topic for MCQ", step_options, index=selected_step_index, key="mcq_topic_select")

        current_step = roadmap_data[st.session_state.selected_step - 1]

        # Pass the prompt to get_explanation, NOT the topic
        explanation_md, mcq_data = llm_interaction.get_explanation(current_step["prompt"])  

        st.write("## MCQ Questions")
        for i, question_data in enumerate(mcq_data):
            st.write(f"**Question {i+1}:** {question_data['question']}")
            selected_option = st.selectbox(
                f"Select an option for question {i+1}:",
                question_data['options'],
                key=f"mcq_select_{i}"
            )

            if st.button(f"Check Answer for Q{i+1}", key=f"check_{i}"):
                if selected_option == question_data['answer']:
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect. The correct answer is: {question_data['answer']}")
    else:
        st.write("Please generate a roadmap first.")
