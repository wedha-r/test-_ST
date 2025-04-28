import streamlit as st
import requests
import json
import re
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

# --- CONFIG ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Get from environment variable
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Get API key from environment variables
HF_API_KEY = os.getenv("HF_API_KEY")

# Add this after loading environment variables
if not GEMINI_API_KEY:
    st.error("❌ Gemini API key not found in environment variables")
    st.stop()

if not HF_API_KEY:
    st.error("❌ Hugging Face API key not found in environment variables")
    st.stop()

# Initialize Hugging Face client
client = InferenceClient(
    provider="fal-ai",
    api_key=HF_API_KEY
)

# Detect Tamil characters in the input text
def is_tamil(text):
    return bool(re.search(r'[\u0B80-\u0BFF]', text))

# Generate a Tamil children's story using Gemini API
def generate_tamil_story(prompt):
    data = {
        "contents": [{
            "parts": [{"text": f"ஒரு சிறிய தமிழ் குழந்தைகள் கதையை எழுதவும். தலைப்பு: {prompt}"}]
        }]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        st.error(f"❌ Gemini API Error {response.status_code}: {response.text}")
        return None

# Generate a related image using Hugging Face client
def generate_story_image(prompt):
    try:
        # Generate image using Hugging Face client
        image = client.text_to_image(
            prompt=f"children's story book illustration, {prompt}, cute style, colorful, safe for kids",
            model="openfree/flux-chatgpt-ghibli-lora"  # Using Ghibli style model for child-friendly illustrations
        )
        
        # Convert PIL Image to buffer
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        
        return buffer
    except Exception as e:
        st.error(f"❌ Image generation failed: {str(e)}")
        return None

# --- STREAMLIT UI ---
st.set_page_config(page_title="Kathai Sollum Paati 🧓📖", layout="centered")
st.title("📚 Kathai Sollum Paati - Tamil Story Generator")

st.markdown("தலைப்பை (Theme or title) கீழே எழுதவும். கதையும் படமும் தானாக உருவாகும்!")

theme = st.text_input("🎨 Enter a story theme (in English or Tamil):")

if st.button("✨ Generate Story") and theme:
    with st.spinner("📖 Kathai Sollum Paati is weaving a tale..."):
        story = generate_tamil_story(theme)

    if story:
        with st.spinner("🖼️ Creating a magical illustration..."):
            image_buffer = generate_story_image(theme)

        if image_buffer:
            st.image(image_buffer, width=400, caption="Story Illustration")

        st.subheader("📝 Tamil Story")
        st.write(story)
