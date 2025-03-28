import streamlit as st
from db import get_users
import pandas as pd


"""Admin Dashboard - View & Manage Users"""
st.title("🔧 Admin Panel")

# Fetch Users (Admins can only view, not approve)
users = get_users()
user_data = [{**user, "_id": str(user["_id"])} for user in users]

# Display Users in a Table
st.subheader("📋 All Users")
# st.table(user_data)
user_data = pd.DataFrame(user_data)
st.dataframe(user_data)
