import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError as APIError
from langchain.prompts import PromptTemplate
import json
import os
from dotenv import load_dotenv
import re
import streamlit as st
from typing import Dict


# Load environment variables from .env
load_dotenv()

genai.configure(api_key='AIzaSyBF1jSW7V95pB23XnJSDczjcUe1OImN4A4')  # Replace with your actual API key
llm = genai.GenerativeModel('gemini-1.5-flash') 

def analyze_syllabus(syllabus_text: str, llm: genai.GenerativeModel) -> Dict:
    """
    Analyzes a syllabus to extract key information.

    Args:
        syllabus_text: The text content of the syllabus.
        llm: A Google Generative AI model instance.

    Returns:
        A dictionary containing extracted syllabus data, including:
            - main_topics: The main topics covered in the syllabus.
            - learning_outcomes: Key learning outcomes or objectives.
            - assessment_methods:  Assessment methods used (e.g., exams, quizzes).
    """

    # Define the prompt for the LLM
    prompt_template = PromptTemplate(
        template="Analyze the following syllabus text and provide the following information in JSON format: \n"
        "```json\n"
        "{{\n"
        "  \"main_topics\": [],\n"
        "  \"learning_outcomes\": [],\n"
        "  \"assessment_methods\": []\n"
        "}}\n"
        "```\n"
        "{syllabus_text}",
        input_variables=["syllabus_text"]
    )

    # Generate the response from the LLM
    response = llm.generate_text(prompt_template.format(syllabus_text=syllabus_text))

    try:
        # Parse the JSON response 
        syllabus_data = json.loads(response.text)
    except json.JSONDecodeError:
        st.error("The LLM's response was not valid JSON. Please try again.")
        return None 

    return syllabus_data

def generate_roadmap(syllabus_analysis, course_content, credentials):
    """Generates a study roadmap from syllabus analysis and course content."""

    if not syllabus_analysis:
        st.error("Syllabus analysis is missing. Please analyze the syllabus first.")
        return None

    prompt_template = PromptTemplate(
        input_variables=["analysis", "content"],
        template="""
        You are a helpful AI study assistant.
        Given this course syllabus analysis: 
        ```json
        {analysis}
        ```
        and the course content:
        ```
        {content}
        ```
        Create a detailed study roadmap to help students succeed. 
        The roadmap should include:
        - A day-by-day or topic-by-topic breakdown of material based on complexity.
        - Suggestions for readings, practice problems, and other resources.
        - Tips for effective studying and time management strategies.
        """
    )

    prompt = prompt_template.format(analysis=json.dumps(syllabus_analysis), content=course_content)
    response = llm.generate_content(contents=[prompt])
    roadmap_text = response.text  

    return roadmap_text

def get_answer_and_explanation(user_question, relevant_text, llm):
    """
    Generates an answer and explanation using the LLM, incorporating relevant text
    if available.
    """

    try:
        # Construct the prompt for the LLM
        prompt_template = PromptTemplate(
            template="""
            Use the following context to answer the question:
            {context}
            Question: {question}
            """,
            input_variables=["context", "question"],
        )

        prompt = prompt_template.format(context=relevant_text, question=user_question)
        print("Prompt:", prompt)  # Debug: Print the prompt

        # Call the LLM and generate the response
        response = llm.generate_content(contents=[prompt])  # Update with your LLM call

        print("Response:", response)  # Debug: Check the response
        print("Content:", response["content"])

        return response["content"]  # Return the content from the response

    except APIError as e:
        print(f"API Error: {e}")  # Log the error
        return f"An error occurred while communicating with the API. Please try again later."

    except Exception as e:
        print(f"General Error: {e}")  # Log the error
        return f"An unexpected error occurred. Please try again later."