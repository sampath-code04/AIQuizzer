import streamlit as st
from db import db
import json
import time
from datetime import datetime

st.title("Admin Dashboard")
st.write("---")
# MongoDB collection
quiz_collection = db["quizzes"]  # Ensure this is correctly connected to your MongoDB instance

# Import the generate_mcqs_from_topic function
from pages.modules.generate_from_topic import generate_mcqs_from_topic  # Replace with the correct path

# Initialize session state variables
if "quiz_generated" not in st.session_state:
    st.session_state.quiz_generated = False
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "selected_difficulty" not in st.session_state:
    st.session_state.selected_difficulty = None
if "username" not in st.session_state:
    st.session_state.username = "default_user"  # Replace this with actual logged-in user's username


# Function to reset session state to the initial state
def reset_state():
    st.session_state.quiz_generated = False
    st.session_state.quiz_data = None
    st.session_state.selected_topic = None
    st.session_state.selected_difficulty = None
    st.rerun()


# Function to display and edit generated MCQs
def display_mcqs(quiz_data, topic, difficulty):
    st.toast("Quiz generated successfully! Review and edit below before saving.")
    edited_mcqs = []

    
    # Form to edit the quiz
    with st.form("edit_quiz_form"):
        for idx, mcq in enumerate(quiz_data):
            st.subheader(f"Scenario {idx + 1}")
            scenario = st.text_area(f"Scenario {idx + 1}", mcq["scenario"], key=f"scenario_{idx}")

            # Loop through questions
            for q_idx, question in enumerate(mcq["questions"]):
                st.write(f"**Question {q_idx + 1}:**")
                col1, col2 = st.columns([3, 1])

                with col1:
                    q_text = st.text_input(f"Question ", question["question"], key=f"q_{idx}_{q_idx}")

                with col2:
                    answer = st.text_input(f"Answer ", question["answer"], key=f"answer_{idx}_{q_idx}")

                # Display choices in another row with columns
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    choice_a = st.text_input("A",question["choices"][0], key=f"choice_a_{idx}_{q_idx}")
                with col_b:
                    choice_b = st.text_input("B",question["choices"][1], key=f"choice_b_{idx}_{q_idx}")
                with col_c:
                    choice_c = st.text_input("C", question["choices"][2], key=f"choice_c_{idx}_{q_idx}")
                with col_d:
                    choice_d = st.text_input("D", question["choices"][3], key=f"choice_d_{idx}_{q_idx}")

                # Append the edited question and choices
                edited_mcqs.append({
                    "question": q_text,
                    "choices": [choice_a, choice_b, choice_c, choice_d],
                    "answer": answer,
                })

        # Save button inside the form
        save_button = st.form_submit_button("Save Quiz to Database")

    if save_button:
        try:
            with st.spinner("Saving quiz to the database..."):
                quiz_entry = {
                    "created_at": datetime.now(),
                    "created_by": st.session_state.username,
                    "total_questions": len(edited_mcqs),
                    "selected_topic": topic,
                    "difficulty": difficulty,
                    "mcqs": edited_mcqs,
                }
                result = quiz_collection.insert_one(quiz_entry)  # Insert into MongoDB
                if result.inserted_id:
                    st.toast("Quiz saved successfully!", icon="✅")  # Success toast
                    st.toast(f"Quiz saved successfully! ID: {result.inserted_id}")
                    time.sleep(5)
                    reset_state()
                    st.rerun()
                else:
                    st.toast("Failed to save quiz. Please try again.", icon="❌")
                    st.error("Quiz could not be saved. No ID was returned.")
        except Exception as e:
            st.toast("An error occurred while saving the quiz.", icon="❌")
            st.error(f"Error: {e}")


# Display the form to generate a quiz if no quiz has been generated yet
col1, col2, col3, col4 = st.columns([1,1,1,1.5])
if not st.session_state.quiz_generated:
    with col4.form("generate_quiz_form"):
        st.subheader("Select Quiz Criteria")
        col1, col2 = st.columns(2)

        # Topic selection in one column
        with col1:
            selected_topic = st.selectbox("Select a topic for the quiz:", 
                                          ["Cybersecurity", "Data Science", "Artificial Intelligence", "Networking", "Python Programming"], 
                                          key="select_topic")

        # Difficulty selection in the other column
        with col2:
            selected_difficulty = st.selectbox("Select a difficulty level:", 
                                               ["Easy", "Medium", "Hard"], 
                                               key="select_difficulty")

        # Generate button within the form
        generate_button = st.form_submit_button("Generate Quiz")

    if generate_button:
        if selected_topic and selected_difficulty:
            with st.spinner(f"Generating MCQs for '{selected_topic}' at '{selected_difficulty}' level. Please wait..."):
                mcq_data = generate_mcqs_from_topic(selected_topic, difficulty=selected_difficulty)

            if mcq_data:
                if isinstance(mcq_data, list):
                    quiz_data = mcq_data
                else:
                    quiz_data = json.loads(mcq_data)

                st.session_state.quiz_generated = True
                st.session_state.quiz_data = quiz_data
                st.session_state.selected_topic = selected_topic
                st.session_state.selected_difficulty = selected_difficulty
                st.rerun()
            else:
                st.toast("Failed to generate MCQs. Please try again.", icon="❌")
        else:
            st.toast("Please select both a topic and a difficulty level before generating a quiz.", icon="⚠️")

# Display the edit and save quiz form if a quiz has been generated
if st.session_state.quiz_generated:
    display_mcqs(st.session_state.quiz_data, st.session_state.selected_topic, st.session_state.selected_difficulty)
