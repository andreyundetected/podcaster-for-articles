import requests
import base64
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Function to encode a PIL image to base64
def encode_image_to_base64(image):
    """Encodes a PIL image to a base64 string."""
    img = Image.frombytes("RGB", [image.width, image.height], image.samples)
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# Function to generate a response from OpenAI API
def generate_chat_response(messages, max_tokens):
    """Sends a chat message to the OpenAI API and returns the response."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "messages": messages,
        "max_tokens": max_tokens
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

if __name__ == '__main__':
    # Example of generating a chat response
    chat_messages = [{'role': 'user', 'content': 'Hello!'}]
    max_tokens = 4096
    print(generate_chat_response(chat_messages, max_tokens))
