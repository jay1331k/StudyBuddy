import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import streamlit as st
import yaml


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_syllabus(course_topic, difficulty, focus_topics):
    """
    Generates a syllabus based on the course topic, difficulty level, and focus topics.

    Args:
        course_topic (str): The topic of the course.
        difficulty (str): The difficulty level (Beginner, Intermediate, Advanced).
        focus_topics (str): Comma-separated list of focus topics (optional).

    Returns:
        dict: A dictionary representing the syllabus (or None if there's an error).
    """

    prompt = f"""
    Generate a detailed syllabus for a course on "{course_topic}" with a difficulty level of "{difficulty}". 

    The syllabus should be divided into units, each containing several topics and subtopics. 

    If the user has specified any focus topics (e.g., "{focus_topics}"), ensure that these topics are covered in detail within the syllabus.

    Format the syllabus as a JSON object with the following structure:

    
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
    
    Ensure that the entire response is a valid JSON object without preamble. 
    """

    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    completion = model.generate_content(prompt)

    try:
        syllabus_data = yaml.safe_load(completion.text.strip()) # changed here json.loads to yaml.safe_load
        return syllabus_data
    except (yaml.YAMLError, json.JSONDecodeError) as e:  # Handle both YAML and JSON errors
        print(f"Error decoding: {e}")
        print(f"Raw LLM Response: {completion.text}")
        st.error("There was an error generating the syllabus. Please try again or rephrase your query.")
        return None
