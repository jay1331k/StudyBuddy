import streamlit as st
from utils import progress

def progress_page(user_data, roadmap_data):
    """
    Displays the progress page content.

    Args:
        user_data (dict): The user's data, including the progress dictionary.
        roadmap_data (list): The roadmap data, containing the total number of steps.
    """

    st.title("Your Progress")

    if "progress" in user_data and user_data["progress"]:
        progress_data = user_data["progress"]
        completed_steps = sum(progress_data.values())
        total_steps = len(roadmap_data)
        completion_percentage = progress.calculate_completion_percentage(user_data, roadmap_data)

        st.write(f"**Overall Progress:** {completion_percentage:.2f}%")
        st.progress(completion_percentage / 100)  # Display a progress bar

        st.write(f"**Completed Steps:** {completed_steps}/{total_steps}")

        # Display progress details for each step
        st.write("## Step-wise Progress")
        for step in roadmap_data:
            step_number = step["step_number"]
            step_title = step["topic"]
            status = "Completed" if progress_data.get(step_number) else "Not Completed"
            st.write(f"**Step {step_number}:** {step_title} - **{status}**")

    else:
        st.write("No progress data available yet.")