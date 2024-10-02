def get_progress(user_data):
    """
    Retrieves the user's progress data.

    Args:
        user_data (dict): The user's data, including the progress dictionary.

    Returns:
        dict: The user's progress data, with step numbers as keys and completion status (True/False) as values.
    """

    return user_data.get("progress", {})


def update_progress(user_data, step_number, completed=True):
    """
    Updates the user's progress data.

    Args:
        user_data (dict): The user's data, including the progress dictionary.
        step_number (int): The step number to update.
        completed (bool, optional): Whether the step is completed or not. Defaults to True.
    """

    progress_data = get_progress(user_data)
    progress_data[step_number] = completed
    user_data["progress"] = progress_data


def calculate_completion_percentage(user_data, roadmap_data):
    """
    Calculates the completion percentage of the course.

    Args:
        user_data (dict): The user's data, including the progress dictionary.
        roadmap_data (list): The roadmap data, containing the total number of steps.

    Returns:
        float: The completion percentage (0.0 to 100.0).
    """

    progress_data = get_progress(user_data)
    completed_steps = sum(progress_data.values())
    total_steps = len(roadmap_data)

    if total_steps == 0:
        return 0.0
    else:
        return (completed_steps / total_steps) * 100