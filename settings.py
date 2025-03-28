import streamlit as st
from db import users_collection

st.header("Settings")
st.write(f"You are logged in as {st.session_state.role}.")

"""Update Profile Photo Page"""
st.header("Update Profile Photo")
if "username" not in st.session_state:
    st.warning("You must be logged in to update your profile photo.")
    st.stop()

# Fetch user data
user = users_collection.find_one({"username": st.session_state["username"]})

# Display user information in disabled text inputs
st.text_input("Username", value=st.session_state["username"], disabled=True)
st.text_input("Email", value=st.session_state["email"], disabled=True)
st.text_input("Role", value=st.session_state["role"], disabled=True)
st.text_input("Gender", value=st.session_state["gender"], disabled=True)

# Display current profile photo
st.image(user["profile_photo"], caption="Current Profile Photo", width=200)

# File uploader for new profile photo
profile_photo = st.file_uploader("Upload a new profile photo", type=["jpg", "png", "jpeg"])

# Toggle button for editing profile details
edit_toggle = st.toggle("Edit Profile")

if edit_toggle:
    # Popover-like form to edit profile details
    with st.expander("Edit Profile", expanded=True):
        # Pre-fill fields with existing values for editing (excluding role)
        new_username = st.text_input("Username", value=st.session_state["username"], key="new_username")
        new_email = st.text_input("Email", value=st.session_state["email"],key="new_email")
        new_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state["gender"]), key="new_gender")

        if st.button("Save Changes", key="save_changes"):
            # Update the user data in the database
            users_collection.update_one(
                {"username": st.session_state["username"]},
                {"$set": {"username": new_username, "email": new_email, "gender": new_gender}}
            )
            # Update session state
            st.session_state["username"] = new_username
            st.session_state["email"] = new_email
            st.session_state["gender"] = new_gender
            st.success("Profile updated successfully!")

            # Refresh the page to reflect changes
            st.rerun()

# Button to update the profile photo
if st.button("Update Photo"):
    if profile_photo:
        photo_bytes = profile_photo.read()
        users_collection.update_one({"username": st.session_state["username"]}, {"$set": {"profile_photo": photo_bytes}})
        st.session_state["profile_photo"] = photo_bytes
        st.success("Profile photo updated successfully!")
        st.rerun()
    else:
        st.error("Please select an image to upload.")
