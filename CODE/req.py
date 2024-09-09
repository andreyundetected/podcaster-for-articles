import requests
import base64
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Function that encodes a PIL image to base64 and returns the encoded string.
def encode_image_to_base64(image):
    img = Image.frombytes("RGB", [image.width, image.height], image.samples)
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# Function that sends a chat request to OpenAI API and returns the response message.
def generate_chat_response(messages, max_tokens):
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

# Function that sends a text input to OpenAI API to generate audio, returns the audio content.
def generate_audio(text, voice="alloy", model="tts-1"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "voice": voice,
        "input": text
    }
    response = requests.post("https://api.openai.com/v1/audio/speech", headers=headers, json=payload)
    return response.content


if __name__ == '__main__':
    # Example usage: generating audio from a sample chat response
    chat_messages = [{'role': 'user', 'content': 'hello!'}]
    max_tokens = 4096

    output_dir = 'out'
    os.makedirs(output_dir, exist_ok=True)

    audio_content = generate_audio(generate_chat_response(chat_messages, max_tokens))
    
    with open(os.path.join(output_dir, 'output.mp3'), 'wb') as audio_file:
        audio_file.write(audio_content)

    print(f"Audio saved in {os.path.join(output_dir, 'output.mp3')}")
