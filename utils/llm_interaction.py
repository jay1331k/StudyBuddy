import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_explanation(prompt):
    """
    Sends a prompt to the LLM (Gemini) and returns the explanation in a clean format.

    Args:
        prompt (str): The prompt to send to the LLM.

    Returns:
        tuple: (explanation_md, mcq_data)
    """
    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
    completion = model.generate_content(prompt)

    try:
        explanation_data = json.loads(completion.text.strip())

        # Build the explanation Markdown (natural format, no JSON)
        explanation_md = f"""
        ## Introduction
        {explanation_data['introduction']}

        ## Definition
        {explanation_data['definition']}

        ## Analogy
        {explanation_data['analogy']}

        ## Examples
        """
        for example in explanation_data['examples']:
            explanation_md += f"- {example}\n"

        # MCQ Section
        mcq_data = explanation_data.get('mcq_questions', [])
        
        return explanation_md, mcq_data  # Return both explanation and MCQ data

    except json.JSONDecodeError:
        # Handle cases where the response is not JSON
        return completion.text, []  # Return just the text and empty MCQ data
