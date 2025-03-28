import streamlit as st
import json
from datetime import datetime
from pages.modules.generate_from_topic import generate_mcqs_from_topic
from db import db

# MongoDB collections
quiz_collection = db["challenge_quiz"]  # Quiz collection
challenges_collection = db["challenges"]  # Challenges collection
attempts_collection = db["challenge_attempts"]  # Challenge attempts collection
users_collection = db["users"]  # Users collection

# Initialize session state
if "selected_quiz" not in st.session_state:
    st.session_state.selected_quiz = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "quiz_status" not in st.session_state:
    st.session_state.quiz_status = None
if "quiz_id" not in st.session_state:
    st.session_state.quiz_id = None

# Function to reset the quiz attempt state
def reset_quiz_state():
    st.session_state.selected_quiz = None
    st.session_state.submitted = False
    st.session_state.quiz_status = None
    st.session_state.quiz_id = None
    st.rerun()  # Refresh the page to reset the state

# Function to generate and store MCQs
def generate_and_store_mcqs(selected_topic, selected_difficulty):
    if selected_topic and selected_difficulty:
        with st.spinner(f"Generating MCQs for '{selected_topic}' at '{selected_difficulty}' level. Please wait..."):
            mcq_data = generate_mcqs_from_topic(selected_topic, difficulty=selected_difficulty)

        if mcq_data:
            if isinstance(mcq_data, list):
                quiz_data = mcq_data
            else:
                quiz_data = json.loads(mcq_data)  # Assuming MCQ data might be a JSON string

            total_questions = sum(len(scenario.get("questions", [])) for scenario in quiz_data)

            quiz_doc = {
                "selected_topic": selected_topic,
                "difficulty": selected_difficulty,
                "created_at": datetime.now(),
                "total_questions": total_questions,
                "quiz_data": quiz_data
            }

            result = quiz_collection.insert_one(quiz_doc)

            if result.inserted_id:
                return result.inserted_id  # Return the generated quiz's ID
            else:
                st.toast("Failed to generate MCQs. Please try again.", icon="❌")
        else:
            st.toast("Failed to generate MCQs. Please try again.", icon="❌")
    else:
        st.toast("Please select both a topic and a difficulty level before generating a quiz.", icon="⚠️")
    return None

def attempt_challenge_tab():
    username = st.session_state.username  # Get the current username from session state
    
    # Fetch challenges where the current user is either the challenger or opponent and status is "pending"
    pending_challenges = list(challenges_collection.find({
        "$or": [
            {"challenger": username},
            {"opponent": username}
        ],
        "status": "pending"
    }))

    # Filter out challenges that the user has already completed
    pending_challenges = [
        challenge for challenge in pending_challenges
        if username not in challenge.get("completed_by", [])
    ]

    if pending_challenges:
        st.subheader("Your Pending Challenges")
        
        # Define how many columns you want per row
        columns_per_row = 4
        rows = (len(pending_challenges) + columns_per_row - 1) // columns_per_row  # Calculate the number of rows

        for row_idx in range(rows):
            cols = st.columns(columns_per_row)

            for col_idx in range(columns_per_row):
                challenge_idx = row_idx * columns_per_row + col_idx
                if challenge_idx < len(pending_challenges):
                    challenge = pending_challenges[challenge_idx]
                    challenger = challenge["challenger"]
                    opponent = challenge["opponent"]
                    quiz_id = challenge["quiz_id"]
                    
                    # Fetch quiz details based on quiz_id
                    quiz = quiz_collection.find_one({"_id": quiz_id})

                    if quiz:
                        with cols[col_idx]:
                            with st.container(border=True):
                                st.subheader(f"Challenge: {challenger} vs {opponent}")
                                st.write(f"**Topic:** {quiz.get('selected_topic', 'N/A')}")
                                st.write(f"**Difficulty:** {quiz.get('difficulty', 'N/A')}")
                                st.write(f"**Created At:** {challenge['created_at']}")
                                
                                # Button to attempt the challenge
                                if st.button(f"Attempt Challenge with {opponent}", key=f"attempt_{quiz_id}"):
                                    st.session_state.selected_quiz = quiz
                                    st.session_state.quiz_status = "pending"
                                    st.session_state.quiz_id = quiz_id  # Store quiz_id for score calculation
                                    st.rerun()  # Refresh the page to load the quiz attempt
    else:
        st.info("No pending challenges found.")

def attempt_quiz(quiz):
    st.title(f"Attempting Quiz: {quiz.get('selected_topic', 'Unnamed Quiz')}")
    st.write(f"Difficulty: {quiz.get('difficulty', 'N/A')}")

    # Ensure mcqs is a list of scenarios, then extract the questions
    scenarios = quiz.get("quiz_data", [])
    
    # Safety check
    if not scenarios:
        st.error("No quiz data found.")
        return

    answers = []
    correct_answers = 0
    total_questions = 0  # To keep track of total questions answered

    if st.button("Stop Quiz"):
        reset_quiz_state()

    # Iterate over each scenario and its questions
    with st.form("quiz_form"):
        for scenario_idx, scenario in enumerate(scenarios):
            st.subheader(f"Scenario {scenario_idx + 1}: {scenario.get('scenario', 'No scenario description')}")
            
            # Extract the list of questions from the scenario
            questions = scenario.get("questions", [])
            
            if not questions:
                st.warning(f"No questions found for Scenario {scenario_idx + 1}")
                continue

            # Iterate over each question and display it
            for q_idx, question in enumerate(questions):
                question_text = question.get("question", "No question text")
                st.write(f"**Q{q_idx + 1}:** {question_text}")

                choices = question.get("choices", [])
                
                # Ensure we have choices
                if not choices:
                    st.warning(f"No choices found for Question {q_idx + 1}")
                    continue

                # Create radio button for answer selection
                selected_answer = st.radio(
                    f"Select an answer for Q{q_idx + 1}:",
                    options=choices,
                    key=f"answer_{scenario_idx}_{q_idx}",  # Unique key for each question
                    index=None
                )
                
                # Append to answers
                answers.append({
                    "question": question_text,
                    "selected_answer": selected_answer,
                    "correct_answer": question.get("answer")
                })

                # Check if the selected answer is correct
                if selected_answer == question.get("answer"):
                    correct_answers += 1
                
                total_questions += 1  # Count total answered questions

        submit_button = st.form_submit_button("Submit Answers")

    if submit_button:
        try:
            with st.spinner("Submitting your answers..."):
                attempt_data = {
                    "quiz_id": quiz["_id"],
                    "attempted_at": datetime.now(),
                    "attempted_by": st.session_state.username,
                    "answers": answers,
                    "correct_answers_count": correct_answers,  # Store the actual correct answers count
                    "total_questions": total_questions  # Store the total questions count
                }

                # Insert attempt data into MongoDB
                result = attempts_collection.insert_one(attempt_data)

                if result.inserted_id:
                    st.success(f"Your answers have been submitted successfully!\nYou got {correct_answers} out of {total_questions} correct!")
                    
                    # Mark the challenge as completed for the user
                    challenge = challenges_collection.find_one({"quiz_id": quiz["_id"]})
                    if challenge:
                        # Add the current user to the completed_by list
                        completed_by = challenge.get("completed_by", [])
                        if st.session_state.username not in completed_by:
                            completed_by.append(st.session_state.username)
                        
                        # Check if both challenger and opponent have completed
                        challenger = challenge["challenger"]
                        opponent = challenge["opponent"]
                        
                        if challenger in completed_by and opponent in completed_by:
                            # If both users completed the challenge, set the status to "completed"
                            challenges_collection.update_one(
                                {"quiz_id": quiz["_id"]},
                                {"$set": {"completed_by": completed_by, "status": "completed"}}
                            )
                        else:
                            # If either user hasn't completed, leave it as "pending"
                            challenges_collection.update_one(
                                {"quiz_id": quiz["_id"]},
                                {"$set": {"completed_by": completed_by, "status": "pending"}}
                            )

                    reset_quiz_state()  # Reset quiz state
                else:
                    st.error("Failed to submit your answers. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {e}")



def results_tab():

    username = st.session_state.username  # Get the current logged-in username

    # Fetch completed challenges where the logged-in user is either the challenger or opponent
    completed_challenges = list(challenges_collection.find({
        "status": "completed",
        "$or": [
            {"challenger": username},
            {"opponent": username}
        ]
    }))

    if completed_challenges:
        st.subheader("Your Completed Challenges and Results")

        # Define how many columns you want per row
        columns_per_row = 3
        rows = (len(completed_challenges) + columns_per_row - 1) // columns_per_row  # Calculate the number of rows

        for row_idx in range(rows):
            cols = st.columns(columns_per_row)  # Create the columns dynamically

            for col_idx in range(columns_per_row):
                challenge_idx = row_idx * columns_per_row + col_idx
                if challenge_idx < len(completed_challenges):
                    challenge = completed_challenges[challenge_idx]
                    challenger = challenge["challenger"]
                    opponent = challenge["opponent"]
                    quiz_id = challenge["quiz_id"]
                    
                    # Fetch the quiz details (optional but to display quiz topic, etc.)
                    quiz = quiz_collection.find_one({"_id": quiz_id})
                    quiz_topic = quiz.get("selected_topic", "Unknown Topic") if quiz else "Unknown Topic"

                    with cols[col_idx]:
                        with st.container(border=True):
                            st.subheader(f"Quiz: {quiz_topic}")
                            
                            # Fetch the attempt data for both the challenger and the opponent from attempts_collection
                            attempts = list(attempts_collection.find({"quiz_id": quiz_id}))

                            # Get the attempt data for the challenger
                            challenger_attempt = next((attempt for attempt in attempts if attempt["attempted_by"] == challenger), None)
                            # Get the attempt data for the opponent
                            opponent_attempt = next((attempt for attempt in attempts if attempt["attempted_by"] == opponent), None)

                            if challenger_attempt and opponent_attempt:
                                challenger_score = challenger_attempt.get("correct_answers_count", 0)
                                opponent_score = opponent_attempt.get("correct_answers_count", 0)
                                challenger_total = challenger_attempt.get("total_questions", 0)
                                opponent_total = opponent_attempt.get("total_questions", 0)

                                # Display scores for both users
                                st.write(f"**{challenger}**: {challenger_score} / {challenger_total} correct")
                                st.write(f"**{opponent}**: {opponent_score} / {opponent_total} correct")

                                # Determine and display the winner
                                if challenger_score > opponent_score:
                                    winner = challenger
                                    st.success(f"**Winner**: {winner}")
                                elif opponent_score > challenger_score:
                                    winner = opponent
                                    st.success(f"**Winner**: {winner}")
                                else:
                                    st.write("It's a **tie**!")
                            else:
                                st.warning(f"Results for challenge {challenger} vs {opponent} are incomplete.")

                            # st.markdown("---")

                            
    else:
        st.warning("No completed challenges found.")



# Function to create a challenge
def create_challenge_form():
    # Get all users except the current user
    users = list(users_collection.find({"username": {"$ne": st.session_state.username}}))

    # Select topic, difficulty level, and opponent
    with st.form("create_challenge_form"):
        st.subheader("Create a Challenge")
        selected_topic = st.selectbox("Select a topic for the quiz:", ["Cybersecurity", "Data Science", "Artificial Intelligence", "Networking", "Python Programming"])
        selected_difficulty = st.selectbox("Select a difficulty level:", ["Easy", "Medium", "Hard"])
        opponent = st.selectbox("Select opponent:", [user["username"] for user in users])

        # Submit button
        submit_button = st.form_submit_button("Create Challenge")

    if submit_button:
        quiz_id = generate_and_store_mcqs(selected_topic, selected_difficulty)

        if quiz_id:
            # Store challenge details
            challenge_data = {
                "challenger": st.session_state.username,
                "opponent": opponent,
                "quiz_id": quiz_id,
                "status": "pending",  # Initially, the challenge is pending
                "created_at": datetime.now(),
            }

            # Insert challenge into challenges collection
            challenges_collection.insert_one(challenge_data)
            st.toast(f"Challenge created! You have challenged {opponent} to a quiz.")
        else:
            st.error("Failed to create challenge. Please try again.")

def main():
    # Check if a quiz is selected, if so, display the quiz attempt form
    if st.session_state.get("selected_quiz"):
        # Show the quiz attempt form if a quiz is selected
        attempt_quiz(st.session_state.selected_quiz)
    else:
        # If no quiz is selected, display the normal tabs
        tab1, tab2, tab3 = st.tabs(['Create Challenge', 'Attempt Challenge', 'Results'])

        with tab1:
            create_challenge_form()  # Create challenge content

        with tab2:
            attempt_challenge_tab()  # Show pending challenges content

        with tab3:
            results_tab()  # Show results content


# Run the main function
main()
