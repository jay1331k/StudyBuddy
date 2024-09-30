import json
import os

CHATBOTS_FILE = "chatbots.json"  # File to store chatbot data

def load_chatbots():
  """Loads chatbots from the JSON file."""
  if os.path.exists(CHATBOTS_FILE):
    with open(CHATBOTS_FILE, 'r') as f:
      data = json.load(f)
      return data.get('chatbots', [])
  return []  # Return an empty list if the file doesn't exist

def save_chatbots(chatbots):
    """Saves chatbots to the JSON file, handling potential errors."""
    try:
        with open(CHATBOTS_FILE, 'w') as f:
            json.dump({'chatbots': chatbots}, f, indent=2) 
    except (IOError, OSError) as e:
        print(f"Error saving chatbots to file: {e}")

def get_chatbot_by_id(chatbot_id, chatbots):
  """Finds a chatbot by its ID."""
  for chatbot in chatbots:
    if chatbot['chatbot_id'] == chatbot_id:
      return chatbot
  return None