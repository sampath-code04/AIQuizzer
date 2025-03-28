import streamlit as st
import base64

# Function to convert image to base64 string
def convert_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Convert your work-in-progress image to base64
work_in_progress_image_path = "pages/images/dark.png"  # Replace with your image path
work_in_progress_base64 = convert_to_base64(work_in_progress_image_path)

# Inject custom CSS to set the work in progress image as the background
background_css = f"""
    <style>
        .stApp {{
            background-image: url(data:image/png;base64,{work_in_progress_base64});
            background-size: transparent;
            background-position: center center;
            background-repeat: no-repeat;
            height: 100vh;
            color: white;  /* Text color to be visible on the background */
        }}
        .stApp .block-container {{
            background: rgba(0, 0, 0, 0);  /* Optional: Adds a semi-transparent overlay to the content */
            padding: 50px;
        }}
    </style>
"""
st.markdown(background_css, unsafe_allow_html=True)

# Add content with markdown text
st.markdown("""
# Work in Progress

This page is currently under maintenance. Please check back later.

We are working hard to improve the page. Thank you for your patience!

""", unsafe_allow_html=True)
