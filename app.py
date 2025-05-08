from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import re
import requests
from io import BytesIO
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
hf_client = InferenceClient(provider="fal-ai", api_key=HF_API_KEY)


def generate_tamil_story(prompt):
    data = {
        "contents": [{
            "parts": [{"text": f"ஒரு சிறிய தமிழ் குழந்தைகள் கதையை எழுதவும். தலைப்பு: {prompt}"}]
        }]
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    return f"Error: {response.text}"


def generate_story_image(prompt):
    try:
        image = hf_client.text_to_image(
            prompt=f"children's story book illustration, {prompt}, cute style, colorful, safe for kids",
            model="openfree/flux-chatgpt-ghibli-lora"
        )
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer
    except Exception as e:
        return None


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    theme = data.get('theme', '')
    story = generate_tamil_story(theme)
    return jsonify({"story": story})


@app.route('/image', methods=['POST'])
def image():
    data = request.get_json()
    theme = data.get('theme', '')
    image_buffer = generate_story_image(theme)
    if image_buffer:
        return send_file(image_buffer, mimetype='image/png')
    return jsonify({"error": "Image generation failed"}), 500


if __name__ == '__main__':
    app.run(debug=True)
