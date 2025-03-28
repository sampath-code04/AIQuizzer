import streamlit as st
from db import db
from datetime import datetime

# MongoDB collections
quiz_collection = db["quizzes"]  # Quiz collection
attempts_collection = db["quiz_attempts"]  # Quiz attempts collection

# Initialize session state
if "selected_quiz" not in st.session_state:
    st.session_state.selected_quiz = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Function to reset the quiz attempt state
def reset_quiz_state():
    st.session_state.selected_quiz = None
    st.session_state.submitted = False
    st.rerun()

# Function to check if the quiz has been attempted
def is_quiz_attempted(quiz_id):
    # Check if there is a record in the attempts collection for the current user and quiz_id
    result = attempts_collection.find_one({
        "quiz_id": quiz_id,
        "attempted_by": st.session_state.username
    })
    return result is not None

# Function to display available quizzes
def display_quizzes():
    st.title("Available Quizzes")
    
    # Fetch quizzes from the database
    quizzes = list(quiz_collection.find({}))

    if quizzes:
        columns_per_row = 4
        rows = (len(quizzes) + columns_per_row - 1) // columns_per_row  # Calculate the number of rows

        for row_idx in range(rows):
            cols = st.columns(columns_per_row)

            for col_idx in range(columns_per_row):
                quiz_idx = row_idx * columns_per_row + col_idx
                if quiz_idx < len(quizzes):
                    quiz = quizzes[quiz_idx]
                    with cols[col_idx]:
                        with st.container(border=True):
                            st.subheader(quiz.get("selected_topic", "Unnamed Topic"))
                            st.write("**Difficulty:**", quiz.get("difficulty", "N/A"))
                            
                            # Calculate total questions
                            total_questions = quiz.get("total_questions", 0)
                            st.write("**Total Questions:**", total_questions)

                            # Check if the quiz has been attempted by the current user
                            attempted = is_quiz_attempted(quiz["_id"])

                            # Generate a unique key for the button based on the quiz_id
                            button_key = f"attempt_{quiz['_id']}"

                            if attempted:
                                # Disable the button and show "Attempted" if quiz is completed
                                st.button("Attempted", key=button_key, disabled=True)
                            else:
                                # Otherwise, show the "Attempt Quiz" button
                                if st.button("Attempt Quiz", key=button_key):
                                    # Store the entire quiz object in session state
                                    st.session_state.selected_quiz = quiz
                                    st.session_state.quiz_status = "pending"
                                    st.rerun()
                                    return  # Exit to show the quiz once it's selected

    else:
        st.warning("No quizzes available.")

# Function to display and submit quiz
def attempt_quiz(quiz):
    st.title(f"Attempting Quiz: {quiz.get('selected_topic', 'Unnamed Quiz')}")
    st.write(f"Difficulty: {quiz.get('difficulty', 'N/A')}")

    # Ensure mcqs is a list
    mcqs = quiz.get("mcqs", [])
    
    # Safety check
    if not mcqs:
        st.error("No questions found in this quiz.")
        return

    # Initialize counters
    correct_answers = 0
    total_answers = 0
    answers = []

    if st.button("Stop Quiz"):
        reset_quiz_state()

    with st.form("quiz_form"):
        for idx, mcq in enumerate(mcqs):
            st.subheader(f"Question {idx + 1}")
            
            # Get question text
            question_text = mcq.get("question", "No question text")
            st.write(question_text)
            
            # Get choices
            choices = mcq.get("choices", [])
            
            # Ensure we have choices
            if not choices:
                st.warning(f"No choices found for Question {idx + 1}")
                continue
            
            # Create radio button for answer selection
            selected_answer = st.radio(
                f"Q{idx + 1}: Choose an answer", 
                options=choices, 
                key=f"answer_{idx}",
                index=None
            )
            
            answers.append({
                "question": question_text,
                "selected_answer": selected_answer,
                "correct_answer": mcq.get("answer","")
            })

            if selected_answer == mcq.get("answer"):
                correct_answers += 1

            total_answers += 1

        submit_button = st.form_submit_button("Submit Answers")
    
    if submit_button:
        try:
            with st.spinner("Submitting your answers..."):
                attempt_data = {
                    "quiz_id": quiz["_id"],
                    "attempted_at": datetime.now(),
                    "attempted_by": st.session_state.username,
                    "answers": answers,
                    "correct_answers_count": correct_answers,
                    "total_questions": total_answers  # Use total_answers here
                }
                result = attempts_collection.insert_one(attempt_data)  # Insert into MongoDB
                if result.inserted_id:
                    st.toast("Your answers have been submitted successfully!", icon='🎉')
                    reset_quiz_state() 
                else:
                    st.error("Failed to submit your answers. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Main logic
def main():
    if st.session_state.selected_quiz is None:
        display_quizzes()  # Show quizzes if no quiz is selected
    else:
        attempt_quiz(st.session_state.selected_quiz)  # Attempt selected quiz

# Run the main function
main()
