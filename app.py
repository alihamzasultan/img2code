import os
import uuid
import pathlib
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

# Storage directory for images
IMAGE_DIR = "generated_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

client = genai.Client(api_key="AIzaSyCPw79xvCt4ZNOXJh4ORZ0OBZ4S7bZka7U")
MODEL_ID = "gemini-2.0-flash-exp"

def delete_old_images():
    """Deletes all previous images from the storage directory."""
    for file in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def generate_image(prompt):
    """Generates images and saves them with unique names."""
    delete_old_images()  # Remove old images before generating new ones
    filenames = []

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(IMAGE_DIR, filename)
            data = part.inline_data.data
            pathlib.Path(filepath).write_bytes(data)
            filenames.append(filename)

    return filenames if filenames else None

def edit_image_with_prompt(prompt, image_file):
    """Edits an uploaded image based on a prompt and generates multiple images."""
    delete_old_images()  # Remove old images before generating new ones
    filenames = []

    image = Image.open(image_file)
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[prompt, image],
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(IMAGE_DIR, filename)
            data = part.inline_data.data
            pathlib.Path(filepath).write_bytes(data)
            filenames.append(filename)

    return filenames if filenames else None

def display_images(filenames):
    """Displays generated images in Streamlit."""
    if filenames:
        st.success("Images generated successfully!")
        cols = st.columns(len(filenames))
        for idx, filename in enumerate(filenames):
            filepath = os.path.join(IMAGE_DIR, filename)
            with cols[idx]:
                st.image(filepath, use_column_width=True)
                with open(filepath, "rb") as file:
                    st.download_button(
                        label="Download",
                        data=file,
                        file_name=filename,
                        mime="image/png",
                        key=f"dl_{idx}"
                    )
    else:
        st.error("Failed to generate images")

def main():
    st.title("AI Image Generator with Gemini")
    
    tab1, tab2 = st.tabs(["Generate", "Edit"])
    
    with tab1:
        st.header("Generate New Images")
        prompt = st.text_area("Enter your prompt", "A futuristic city")
        
        if st.button("Generate Images"):
            with st.spinner("Generating images..."):
                filenames = generate_image(prompt)
                display_images(filenames)
    
    with tab2:
        st.header("Edit Existing Image")
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        edit_prompt = st.text_area("Enter your edit prompt", "Convert this rough sketch into an image of a low-poly 3D model. Include only the object in the image, with nothing else.")
        
        if uploaded_file and st.button("Edit Image"):
            with st.spinner("Editing image..."):
                filenames = edit_image_with_prompt(edit_prompt, uploaded_file)
                display_images(filenames)

if __name__ == "__main__":
    main()
