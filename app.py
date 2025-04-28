import streamlit as st
import requests
import json
import re
from io import BytesIO
from PIL import Image

# --- CONFIG ---
GEMINI_API_KEY = "AIzaSyDMPQ-gXja7sjEOuCq9x10OZUYIbEifgsM"  # Replace with your Gemini API key
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Stability AI API configuration
STABILITY_API_KEY = "sk-BMhOvXl348UkXcHO0pV9GIlK6QSkL8cQSxBfggQqL7Ge8Yva"  # Replace with your actual API key
STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"

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

# Generate a related image using Stability AI
def generate_story_image(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "image/*"
        }
        
        # Corrected multipart form-data
        files = {
            "prompt": (None, f"children's story book illustration, {prompt}, cute style, colorful, safe for kids"),
            "cfg_scale": (None, "7"),
            "height": (None, "512"),
            "width": (None, "512"),
            "steps": (None, "30"),
            "samples": (None, "1")
        }

        # Debug output
        st.write("Debug - Request details:")
        st.write(f"URL: {STABILITY_URL}")
        st.write("Headers:", headers)
        st.write("Files:", files)

        response = requests.post(
            STABILITY_URL,
            headers=headers,
            files=files
        )

        # Debug output
        st.write(f"Response Status: {response.status_code}")
        st.write(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            img_byte_arr = BytesIO(response.content)
            img = Image.open(img_byte_arr)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            return buffer
        else:
            try:
                error_data = response.json()
                st.error(f"❌ Image Generation Error: {error_data.get('name', 'Unknown error')}")
                if 'errors' in error_data:
                    for error in error_data['errors']:
                        st.error(f"- {error}")
            except Exception as e:
                st.error("❌ Unexpected Error parsing error response")
            return None

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
