import streamlit as st

if "layout" not in st.session_state:
    st.session_state.layout="centered"

# page config
st.set_page_config(
    page_title="AIQuizzer",
    page_icon="👋",
    layout=st.session_state.layout
)

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from home import home
from db import users_collection
import bcrypt
import os
from bson import Binary



# Initialize session state if not set
if "role" not in st.session_state:
    st.session_state.role = None

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


def login():
    """User Login Page"""
    st.header("Login Page")

    login_input = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    if st.button("Log in"):
        with st.spinner("Logging in..."):
            # Check if input is an email or username
            user = users_collection.find_one(
                {"$or": [{"username": login_input}, {"email": login_input}]}
            )
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                # Store session details
                st.session_state["logged_in"] = True
                st.session_state["username"] = user["username"]
                st.session_state["email"] = user["email"]
                st.session_state.role = user["role"]
                st.session_state["profile_photo"] = user["profile_photo"]
                st.session_state["gender"] = user["gender"]
                st.success("Login successful!")
                st.session_state.layout = "wide"
                st.rerun()
            else:
                st.error("Invalid username/email or password!")


def generate_random_profile_photo(gender):
    """Generate a random profile photo based on gender, store as binary data."""
    
    # Determine image file based on gender
    image_path = "pages/images/man.png" if gender == "Male" else "pages/images/woman.png"
    
    # Read the image file as binary data
    with open(image_path, "rb") as img_file:
        image_binary = Binary(img_file.read())
    
    return image_binary

def signup():
    """User Signup Page"""
    st.header("Signup Page")

    username = st.text_input("Username")
    email = st.text_input("Email")
    gender = st.selectbox("Gender", ["Male", "Female"])
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    is_admin_request = st.checkbox("Register as Admin")

    if st.button("Sign up"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif users_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
            st.error("Username or Email already exists!")
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            role = "pending_admin" if is_admin_request else "User"
            status = "pending" if is_admin_request else "approved"
            user_data = {
                "username": username,
                "email": email,
                "gender": gender,
                "role": role,
                "password": hashed_password,
                "profile_photo": generate_random_profile_photo(gender),
                "created_at": datetime.now(),
                "status": status
            }

            users_collection.insert_one(user_data)
            st.success("Signup successful! Please log in.")
            
            


st.logo("pages/images/horizontal_logo.png", icon_image="pages/images/quiz.png")

# Main navigation logic
if st.session_state.role is None or not st.session_state.logged_in:
    # If user is not logged in, show login/signup pages
    pg = st.navigation([st.Page(login), st.Page(signup)])  # Login and Signup are separate pages
    pg.run()      
else:
    home()
