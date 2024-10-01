import streamlit as st
from utils import llm_interaction, progress

def study_page(user_data, roadmap_data):
    """
    Displays the study page content.

    Args:
        user_data (dict): The user's data, including the progress dictionary.
        roadmap_data (list): The roadmap data, containing the steps and prompts.
    """

    st.title("Study Time!")

    if "roadmap" in user_data and user_data["roadmap"]:
        progress_data = user_data.get("progress", {})

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
                progress.update_progress(user_data, current_step["step_number"], completed=True)
                st.success("Step marked as completed!")
        else:
            st.write("You have already completed this step.")

            # Option to review the content again
            if st.button("Review Content"):
                explanation = llm_interaction.get_explanation(current_step["prompt"])
                st.write(explanation)

    else:
        st.write("Please generate a roadmap first.")