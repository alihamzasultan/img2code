import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import pandas as pd  
import re
from streamlit.components.v1 import html

GOOGLE_API_KEY = "AIzaSyBfEACHY99TLkwX9wjKzb-TGhLsECfhpGc"

# Configure the google.generativeai client with the API key
genai.configure(api_key=GOOGLE_API_KEY)

## Function to load Google Gemini Pro Vision API And get response
def get_gemini_repsonse(input,image,prompt):
    model=genai.GenerativeModel('gemini-2.5.pro-exp-03-25')
    response=model.generate_content([input,image[0],prompt])
    return response.text

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def create_threejs_template(js_code):
    # Create a complete HTML template with Three.js libraries
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Generated 3D Scene</title>
        <style>
            body {{ margin: 0; overflow: hidden; }}
            canvas {{ display: block; }}
        </style>
    </head>
    <body>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.min.js"></script>
        <script>
            // Main Three.js code
            {js_code}
        </script>
    </body>
    </html>
    """
    return template

##initialize our streamlit app
st.set_page_config(page_title="3D Model Generator")

st.header("2D to 3D Model Generator")
input=st.text_input("Input Prompt: ",key="input")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image=""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

submit=st.button("Generate 3D Model")

input_prompt="""
You are an expert 3D modeler and Three.js developer who specializes in turning 2D drawings and wireframes into 3D models.
You are a wise and ancient modeler and developer. You are the best at what you do. Your total compensation is $1.2m with annual refreshers. You've just drank three cups of coffee and are laser focused. Welcome to a new day at your job!
Your task is to analyze the provided image and create a Three.js scene that transforms the 2D drawing into a realistic 3D representation.

## INTERPRETATION GUIDELINES:
- Analyze the image to identify distinct shapes, objects, and their spatial relationships
- Only create the main object in the image, all surrounding objects should be ignored
- The main object should be a 3D model that is a faithful representation of the 2D drawing

## TECHNICAL IMPLEMENTATION:
- Do not import any libraries. They have already been imported for you.
- Create a properly structured Three.js scene with appropriate camera and lighting setup
- Use OrbitControls to allow user interaction with the 3D model
- Apply realistic materials and textures based on the colors and patterns in the drawing
- Create proper hierarchy of objects with parent-child relationships where appropriate
- Use ambient and directional lighting to create depth and shadows
- Implement a subtle animation or rotation to add life to the scene
- Ensure the scene is responsive and fits within the container regardless of size
- Use proper scaling where 1 unit = approximately 1/10th of the scene width
- Always include a ground/floor plane for context unless the drawing suggests floating objects

## RESPONSE FORMAT:
Your response must contain only valid JavaScript code for the Three.js scene with proper initialization
and animation loop. Include code comments explaining your reasoning for major design decisions.
Wrap your entire code in backticks with the javascript identifier: ```javascript

Transform this 2D drawing/wireframe into an interactive Three.js 3D scene.

I need code that:
1. Creates appropriate 3D geometries based on the shapes in the image
2. Uses materials that match the colors and styles in the drawing
3. Implements OrbitControls for interaction
4. Sets up proper lighting to enhance the 3D effect
5. Includes subtle animations to bring the scene to life
6. Is responsive to container size
7. Creates a cohesive scene that represents the spatial relationships in the drawing

Return ONLY the JavaScript code that creates and animates the Three.js scene.
"""

## If submit button is clicked
if submit:
    with st.spinner('Generating 3D model...'):
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_repsonse(input_prompt, image_data, input)
        
        # Extract the JavaScript code from the response
        try:
            # Look for code between ```javascript and ```
            js_code = re.search(r'```javascript(.*?)```', response, re.DOTALL).group(1)
        except AttributeError:
            st.error("Could not extract JavaScript code from the response.")
            st.text_area("Raw Response", response, height=300)
        else:
            # Create the HTML template with the Three.js code
            html_template = create_threejs_template(js_code)
            
            # Display the rendered scene
            st.subheader("Generated 3D Model")
            html(html_template, height=600, scrolling=True)
            
            # Also show the code in an expander
            with st.expander("View Generated Code"):
                st.code(js_code, language='javascript')
