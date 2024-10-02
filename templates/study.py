import streamlit as st
from utils import llm_interaction, progress

def go_to_step(step_number):
    """Callback function to navigate to a specific step."""
    st.session_state.selected_step = step_number
    update_content(st.session_state.selected_step - 1, st.session_state.user_data.get("roadmap", []))

def update_content(step_index, roadmap_data):
    """Update the displayed content based on the selected step."""
    current_step = roadmap_data[step_index]

    explanation_md, mcq_data = llm_interaction.get_explanation(current_step["topic"])  # Pass the prompt here
    st.markdown(explanation_md)   # Display explanation

    
def study_page(user_data, roadmap_data):
    st.title("Study Time!")

    if "roadmap" in user_data and user_data["roadmap"]:
        progress_data = user_data.get("progress", {})

        # Initialize step selection
        if "selected_step" not in st.session_state:
            st.session_state.selected_step = 1  # Start at step 1

        # Get current step data dynamically based on the selected step
        step_options = [f"Step {step['step_number']}: {step['topic']}" for step in roadmap_data]
        selected_step_index = st.session_state.selected_step - 1  # Index for the selected step
        selected_step = st.selectbox("Select Step", step_options, index=selected_step_index, key="step_select")

        # Update content based on selected step
        update_content(st.session_state.selected_step - 1, roadmap_data)

        if st.button("Mark as Completed", key=f"mark_complete_{roadmap_data[st.session_state.selected_step - 1]['step_number']}"):
            progress.update_progress(user_data, roadmap_data[st.session_state.selected_step - 1]["step_number"], completed=True)
            st.success("Step marked as completed!")

            # Move to the next step if exists
            if st.session_state.selected_step < len(roadmap_data):
                go_to_step(st.session_state.selected_step + 1)

    else:
        st.write("Please generate a roadmap first.")
