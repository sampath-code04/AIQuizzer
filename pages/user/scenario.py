import streamlit as st
from pages.modules.generate_from_topic import generate_mcqs_from_topic  # Assuming this supports difficulty levels
from pages.modules.pdf_export import generate_feedback_from_results, generate_pdf_with_feedback_and_analytics
from db import quiz_results_collection
from datetime import datetime
import time

def get_next_difficulty(correct_count):
    """Determine next difficulty based on correct count."""
    if correct_count >= 4:
        return "hard"
    elif correct_count >= 2:
        return "medium"
    else:
        return "easy"


def display_mcq(mcqs, current_level, question_batch, total_answers):
    """Display multiple-choice questions (MCQs)."""
    st.title("Multiple Choice Questions")

    # Display scenario if available
    if 'scenario' in st.session_state:
        st.write("### Scenario:")
        st.info(st.session_state.scenario)

    # Initialize session state for user answers if not already set
    if f'user_answers_{question_batch}' not in st.session_state:
        st.session_state[f'user_answers_{question_batch}'] = [None] * len(mcqs)
    
    # Initialize session state for submitted flag if not already set
    if f'submitted_{question_batch}' not in st.session_state:
        st.session_state[f'submitted_{question_batch}'] = False

    # Display questions in a form
    with st.form(f"mcq_form_{question_batch}"):
        for idx, mcq in enumerate(mcqs):
            if 'question' in mcq:
                st.subheader(f"{mcq['question']} (Difficulty: {current_level.capitalize()})")
                options = mcq.get('choices', [])
                choice = st.radio(
                    f"Select your answer for Question {idx + 1}:",
                    options,
                    key=f"q_{idx}_{question_batch}",
                    index=None  # Ensures no answer is pre-selected
                )
                st.session_state[f'user_answers_{question_batch}'][idx] = choice

        submitted = st.form_submit_button("Submit Answers")
        
        if submitted:
            st.session_state[f'submitted_{question_batch}'] = True

    # If the form is not submitted, return early
    if not st.session_state[f'submitted_{question_batch}']:
        return 0

    correct_count = 0
    for idx, mcq in enumerate(mcqs):
        if 'question' in mcq and 'answer' in mcq:
            correct_answer = mcq['answer']
            user_answer = st.session_state[f'user_answers_{question_batch}'][idx]
            
            if user_answer == correct_answer:
                correct_count += 1
                st.success(f"Question {idx + 1}: Correct! The answer is {correct_answer}")
            else:
                st.error(f"Question {idx + 1}: Incorrect. The correct answer is {correct_answer}")

            total_answers.append({
                "question": mcq['question'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "difficulty": current_level,
            })

    return correct_count

def store_quiz_results_in_mongo(username, selected_topics, total_correct, total_questions, feedback):
    """Store the quiz results in MongoDB with a timestamp and user identifier."""
    quiz_data = {
        "username": username,  # Store the username for user-specific results
        "selected_topics": selected_topics,
        "total_correct": total_correct,
        "total_questions": total_questions,
        "feedback": feedback,
        "quiz_started_at": datetime.now(),  # Store the current time as timestamp
        "results": []  # Store the question-answer results here
    }

    # Add each question's data (question, user_answer, correct_answer) to 'results'
    for answer in st.session_state.total_answers:
        quiz_data["results"].append({
            "question": answer["question"],
            "user_answer": answer["user_answer"],
            "correct_answer": answer["correct_answer"],
            "difficulty": answer["difficulty"]
        })

    # Insert the result into MongoDB
    quiz_results_collection.insert_one(quiz_data)
    print(f"Quiz results for {username} stored in MongoDB.")
    return True

def simplified_results_and_reset(selected_topics):
    """Display simplified quiz results, save to DB and automatically reset."""
    total_correct = sum(1 for answer in st.session_state.total_answers if answer['user_answer'] == answer['correct_answer'])
    total_questions = len(st.session_state.total_answers)
    
    # Only show the grand total
    st.toast(f"Quiz completed! Your score: {total_correct}/{total_questions}", icon='🎉')
    
    # Generate feedback based on results
    feedback = generate_feedback_from_results(
        topic=selected_topics,
        total_score=total_correct,
        total_questions=total_questions,
        correct_count=total_correct,
        incorrect_count=total_questions - total_correct,
        difficulty=st.session_state.difficulty,
        difficulty_performance="Moderate performance on hard questions"
    )
    
    # Store results in database
    if store_quiz_results_in_mongo(st.session_state.username, selected_topics, total_correct, total_questions, feedback):
        st.toast("Results have been stored successfully. The quiz will reset automatically...", icon='🎉')
    
    # Wait briefly to show the message
    time.sleep(2)
    
    # Set flag to reset on next rerun
    st.session_state.should_reset = True
    st.rerun()


def reset_quiz_state():
    """Reset all quiz-related session state variables."""
    # List of prefixes for keys that need to be deleted
    prefixes_to_delete = ['user_answers_', 'submitted_']
    
    # Keys to completely reset
    keys_to_reset = [
        'total_answers', 'question_batch', 'difficulty', 
        'correct_count', 'quiz_started', 'mcqs', 
        'scenario', 'selected_topics', 'previous_score',
        'should_reset'
    ]
    
    # Delete all keys with prefixes
    keys_to_delete = []
    for key in st.session_state:
        for prefix in prefixes_to_delete:
            if key.startswith(prefix):
                keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del st.session_state[key]
    
    # Reset standard keys
    st.session_state.total_answers = []
    st.session_state.question_batch = 1
    st.session_state.difficulty = "easy"
    st.session_state.correct_count = 0
    st.session_state.quiz_started = False
    st.session_state.selected_topics = []
    
    # Remove other quiz-related keys if they exist
    for key in keys_to_reset:
        if key in st.session_state:
            if key == 'total_answers' or key == 'selected_topics':
                st.session_state[key] = []
            else:
                del st.session_state[key]


def main():
    """Main function to run the Streamlit app."""
    
    # Check if we need to reset
    if 'should_reset' in st.session_state and st.session_state.should_reset:
        reset_quiz_state()
    
    # Initialize session state variables if they are not set already
    if 'total_answers' not in st.session_state:
        st.session_state.total_answers = []
    if 'question_batch' not in st.session_state:
        st.session_state.question_batch = 1
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = "easy"
    if 'correct_count' not in st.session_state:
        st.session_state.correct_count = 0
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'selected_topics' not in st.session_state:
        st.session_state.selected_topics = []  # Initialize selected_topics as an empty list
    

    # If the quiz has been completed
    if len(st.session_state.total_answers) >= 20:
        simplified_results_and_reset(st.session_state.selected_topics)
        return

    # Select topics and start quiz
    st.title("Scenario based Adaptive Quiz")
    
    # Display topics selection only if the quiz has not started
    if not st.session_state.quiz_started:
        topics_list = ["DBMS", "ML", "RPA", "CLOUD", "JAVA", "SQL", "PYTHON", "OS", "MONGODB", "NETWORKING", "CYBER SECURITY"]
        selected_topics = st.multiselect("Select up to 4 topics", options=topics_list, max_selections=4)

        start_button = st.button("Start Quiz")
        if start_button:
            if selected_topics:
                st.session_state.selected_topics = selected_topics  # Store the selected topics in session state
                st.session_state.quiz_started = True

                with st.spinner(f"Generating MCQs for the topics: {', '.join(selected_topics)}..."):
                    mcq_data = generate_mcqs_from_topic(selected_topics, difficulty=st.session_state.difficulty)
                
                if mcq_data:
                    # Get scenario and questions from generated data
                    scenario = mcq_data[0].get("scenario", "No scenario provided.")
                    questions = mcq_data[0].get("questions", [])
                    
                    # Store the scenario and questions in session state
                    st.session_state.scenario = scenario
                    st.session_state.mcqs = questions
                    st.session_state[f'user_answers_{st.session_state.question_batch}'] = [None] * len(questions)
                    st.rerun()
            else:
                st.error("Please select at least one topic.")
    else:
        # If quiz is in progress, show stop button
        if st.button("Stop Quiz"):
            reset_quiz_state()
            st.rerun()

        # Only process questions if MCQs exist in the session state
        if 'mcqs' in st.session_state and st.session_state.mcqs:
            correct_count = display_mcq(
                st.session_state.mcqs,
                current_level=st.session_state.difficulty,
                question_batch=st.session_state.question_batch,
                total_answers=st.session_state.total_answers,
            )
            
            # Only update difficulty and generate new questions if this batch was submitted
            if f'submitted_{st.session_state.question_batch}' in st.session_state and st.session_state[f'submitted_{st.session_state.question_batch}']:
                # Update the difficulty level based on the user's performance
                st.session_state.difficulty = get_next_difficulty(correct_count)
                st.session_state.correct_count += correct_count
                st.session_state.previous_score = correct_count
                
                # Store the current batch number that was submitted
                submitted_batch = st.session_state.question_batch
                
                # Increment the batch counter
                st.session_state.question_batch += 1

                # Generate the next batch if fewer than 20 questions have been answered
                if len(st.session_state.total_answers) < 20:
                    next_difficulty = st.session_state.difficulty
                    with st.spinner(f"Fetching next batch of questions for difficulty: {next_difficulty}..."):
                        mcq_data = generate_mcqs_from_topic(st.session_state.selected_topics, difficulty=next_difficulty)
                    if mcq_data:
                        scenario = mcq_data[0].get("scenario", "No scenario provided.")
                        questions = mcq_data[0].get("questions", [])
                        st.session_state.scenario = scenario
                        st.session_state.mcqs = questions
                        st.session_state[f'user_answers_{st.session_state.question_batch}'] = [None] * len(questions)
                    st.rerun()
                else:
                    # Clear the submitted flag to avoid auto-advancing
                    st.session_state[f'submitted_{submitted_batch}'] = False
                    st.toast("Quiz completed! Processing your results...",icon='🎉')
                    time.sleep(2)
                    st.rerun()  # This will trigger simplified_results_and_reset on the next run



main()