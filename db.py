import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import bcrypt


# MongoDB connection setup
@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["MONGODB_URI"], server_api=ServerApi('1'))


client = init_connection()
db = client["user_database"]
users_collection = db["users"]
quiz_results_collection = db["quiz_results"]
quiz_collection = db["quizzes"]

quiz_results_collection.create_index([("quiz_started_at", 1)], expireAfterSeconds=86400)  # 86400 seconds = 24 hours

def get_users(role=None, status=None):
    """Fetch users based on role (optional)"""
    if role:
        return list(users_collection.find({"role": role}))
    
    if status:
        return list(users_collection.find({"status": status}))
    return list(users_collection.find())