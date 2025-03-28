import streamlit as st
from pymongo import MongoClient
from db import quiz_results_collection
from datetime import datetime

# Fetch all quiz results for a specific user
def fetch_user_results(username):
    return quiz_results_collection.find({"username": username}).sort("quiz_started_at", -1)

# Display results for the quiz
def display_quiz_results(user_data):
    st.title(f"Quiz Results for {user_data[0]['username']}")
    
    current_time = datetime.now()

    # Display results for each quiz attempt
    for idx, quiz_result in enumerate(user_data, 1):
        quiz_start_time = quiz_result['quiz_started_at']
        
        # Calculate time difference
        time_diff = current_time - quiz_start_time
        time_diff_minutes = time_diff.total_seconds() / 60  # convert to minutes
        time_diff_hours = time_diff_minutes / 60  # convert to hours
        
        # Determine time difference description
        if time_diff_minutes < 1:
            time_description = "**Now**"
        elif time_diff_minutes < 60:
            time_description = f"**{int(time_diff_minutes)} minute{'s' if int(time_diff_minutes) > 1 else ''} ago**"
        elif time_diff_hours < 24:
            time_description = f"{int(time_diff_hours)} hour{'s' if int(time_diff_hours) > 1 else ''} ago"
        else:
            time_description = quiz_start_time.strftime("%Y-%m-%d %H:%M:%S")

        with st.expander(f"Quiz Attempt {idx} - {time_description}"):
            # Display selected topics
            st.write(f"**Attempted time:** {quiz_result['quiz_started_at']}")
            st.write("**Selected Topics:**")
            st.write(", ".join(quiz_result['selected_topics']))
            
            # Display total correct and total questions
            st.write("**Quiz Summary:**")
            st.write(f"Total Correct: {quiz_result['total_correct']}/20")
            st.write(f"Total Questions: 20")
            
            # Display feedback
            st.write("### Feedback")
            st.write("**Overall Performance:**")
            st.write(quiz_result['feedback']['overall_performance'])
            
            st.write("**Correct vs Incorrect:**")
            st.write(quiz_result['feedback']['correct_vs_incorrect']['analysis'])
            
            st.write("**Areas of Improvement:**")
            st.write(quiz_result['feedback']['areas_of_improvement'])
            
            st.write("**Topic-Specific Feedback:**")
            st.write(quiz_result['feedback']['topic_specific_feedback'])
            
            st.write("**Next Steps:**")
            st.write(quiz_result['feedback']['next_steps'])
            
            # Display quiz results in a table format
            st.write("### Quiz Results")
            results = quiz_result['results']
            for question_idx, result in enumerate(results, 1):
                st.write(f"**Question {question_idx}:** {result['question']}")
                st.write(f"- **Your Answer:** {result['user_answer']}")
                st.write(f"- **Correct Answer:** {result['correct_answer']}")
                st.write(f"- **Difficulty:** {result['difficulty'].capitalize()}")
                st.write("---")

def main():
    """Main function to display user quiz results."""
    
    # User's username (this should come from the session or user login)
    username = st.session_state.username
    
    if username:
        user_data_cursor = fetch_user_results(username)
        user_data = list(user_data_cursor)  # Convert cursor to list
        
        if user_data:
            display_quiz_results(user_data)
        else:
            st.error(f"No quiz results found for user: {username}")

main()