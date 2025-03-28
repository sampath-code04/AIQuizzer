import streamlit as st
import pandas as pd
from db import users_collection, get_users
from streamlit_extras.row import row
from datetime import datetime

"""Super Admin Panel - Approve Admin Requests & Manage Users"""
st.title("👑 Super Admin Panel")

# Fetch Users
pending_admins = get_users(status="pending")
approved_admins = get_users("Admin")
normal_users = get_users("User")

# Function to handle approval of selected users
@st.fragment
def approve_selected_users(selected_rows):
    for row_index in selected_rows:
        user = pending_admins[row_index]  # Fetch user by row index
        users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "role": "Admin",
                    "approved_at": datetime.now(),
                    "status": "approved",
                    "declined_at": None
                }
            }
        )
    st.success("Selected users have been approved as admins!")
    st.rerun()

# Function to handle decline of selected users
@st.fragment
def decline_selected_users(selected_rows):
    for row_index in selected_rows:
        user = pending_admins[row_index]  # Fetch user by row index
        users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "role": "",
                    "status": "declined",
                    "declined_at": datetime.now(),
                    "approved_at": None
                }
            }
        )
    st.info("Selected users have been declined.")
    st.rerun()


# Pending Admin Requests
st.subheader("🔄 Pending Admin Requests")
if pending_admins:
    pending_admins_df = pd.DataFrame(pending_admins)
    pending_admins_df["_id"] = pending_admins_df["_id"].astype(str)  # Ensure _id is a string for display

    # Display dataframe for pending admin requests
    event = st.dataframe(
        pending_admins_df[['username', 'email', 'gender', 'role', 'created_at', 'status']], 
        use_container_width=True,
        on_select="rerun",  # Trigger a rerun on selection
        selection_mode="multi-row"  # Allow multi-row selection
    )

    # If rows are selected, process the selected rows
    if event.selection["rows"]:
        selected_row_indices = event.selection["rows"]
        # Create two buttons: Approve All Selected or Decline All Selected
        col1, col2 = st.columns([0.1, 1])  # Create two columns for buttons
        
        with col1:
            if st.button("Approve"):
                approve_selected_users(selected_row_indices)  # Call the function to approve selected users
        
        with col2:
            if st.button("Decline"):
                decline_selected_users(selected_row_indices) 
else:
    st.info("No pending admin requests.")


# Approved Admins List
st.subheader("✅ Approved Admins")
# Convert approved_admins to DataFrame for interactive display
approved_admins_df = pd.DataFrame(approved_admins)
approved_admins_df["_id"] = approved_admins_df["_id"].astype(str)  # Ensure _id is a string for display
st.dataframe(approved_admins_df)

# Normal Users List
st.subheader("👤 Normal Users")
# Convert normal_users to DataFrame for interactive display
normal_users_df = pd.DataFrame(normal_users)
normal_users_df["_id"] = normal_users_df["_id"].astype(str)  # Ensure _id is a string for display
st.dataframe(normal_users_df)
