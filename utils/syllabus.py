import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))

def generate_syllabus(course_topic, difficulty, focus_topics):
    """
    Generates a syllabus based on the course topic, difficulty level, and focus topics.

    Args:
        course_topic (str): The topic of the course.
        difficulty (str): The difficulty level (Beginner, Intermediate, Advanced).
        focus_topics (str): Comma-separated list of focus topics (optional).

    Returns:
        dict: A dictionary representing the syllabus with units, topics, and subtopics.
    """

    prompt = f"""
    Generate a detailed syllabus for a course on "{course_topic}" with a difficulty level of "{difficulty}". 

    The syllabus should be divided into units, each containing several topics and subtopics. 

    If the user has specified any focus topics (e.g., "{focus_topics}"), ensure that these topics are covered in detail within the syllabus.

    Format the syllabus as a JSON object with the following structure:

    ```json
    {{
      "course_topic": "Course Topic",
      "difficulty": "Difficulty Level",
      "units": [
        {{
          "unit_number": 1,
          "unit_title": "Unit Title",
          "topics": [
            {{
              "topic_number": 1,
              "topic_title": "Topic Title",
              "subtopics": [
                "Subtopic 1",
                "Subtopic 2",
                // ...
              ]
            }},
            // ... more topics
          ]
        }},
        // ... more units
      ]
    }}
    ```
    """
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    completion = model.generate_content(
        prompt=prompt,
    )

    syllabus_data = json.loads(completion.result)
    return syllabus_data