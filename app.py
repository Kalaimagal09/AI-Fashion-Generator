import streamlit as st
import requests
import io
from PIL import Image
import os

# --- Configuration & Helper Functions ---

# Load the API key from Streamlit's secrets manager
# This block will show an error when you run locally, which is normal.
# It's designed to work when deployed on Streamlit Cloud.
try:
    HF_API_TOKEN = st.secrets["HF_API_TOKEN"]
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
except (KeyError, FileNotFoundError):
    st.error("API Key not found in Streamlit Secrets. This app will only work when deployed.")
    # We use st.stop() to halt the app if the key isn't found during deployment.
    # We will comment this out for local testing if needed.
    st.stop()

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

def generate_fashion_design(prompt):
    """Sends a prompt to the Hugging Face API and returns the generated image."""
    full_prompt = f"professional fashion design sketch of a {prompt}, centered, white background, 4k, high quality, no text"
    payload = {"inputs": full_prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            return Image.open(io.BytesIO(response.content))
        except Exception:
            return None
    return None

def find_similar_products(prompt):
    """Simulates finding similar products by matching keywords in the prompt with filenames."""
    prompt_keywords = set(prompt.lower().split())
    similar_products = []
    image_folder = "product_images"
    if not os.path.exists(image_folder):
        return []

    for filename in os.listdir(image_folder):
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            file_keywords = set(filename.lower().replace('_', ' ').replace('-', ' ').replace('.jpg', '').replace('.png', '').split())
            if prompt_keywords.intersection(file_keywords):
                similar_products.append(os.path.join(image_folder, filename))
    return similar_products[:5]

# --- Streamlit User Interface ---

st.set_page_config(layout="wide", page_title="AI Fashion Design Generator")

st.title("👗 AI Fashion Design Generator 👠")
st.markdown("Turn your fashion ideas into reality. Describe what you want to create, and let AI do the rest!")

# Sidebar for user input
st.sidebar.header("Design Your Item")
prompt = st.sidebar.text_area("Describe the clothing in detail:", "a stylish blue denim jacket for women, streetwear style", height=100)

if st.sidebar.button("✨ Generate Design"):
    if prompt:
        st.header("Your AI-Generated Design")
        with st.spinner("Generating your unique design... This may take up to a minute."):
            generated_image = generate_fashion_design(prompt)

        if generated_image:
            st.image(generated_image, caption="Your custom AI design", use_column_width=True)
            st.divider()
            st.header("🛒 Similar Products You Can Buy")
            similar_products = find_similar_products(prompt)

            if similar_products:
                cols = st.columns(len(similar_products))
                for i, product_path in enumerate(similar_products):
                    with cols[i]:
                        st.image(product_path)
                        caption_text = os.path.basename(product_path).split('.')[0].replace('_', ' ').title()
                        st.caption(caption_text)
            else:
                st.info("No similar products found in our catalog for this design.")
        else:
            st.error("😥 Sorry, the AI service is busy or an error occurred. Please try again in a moment.")
    else:
        st.sidebar.warning("Please enter a description to generate a design.")