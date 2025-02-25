import streamlit as st
from generate_from_topic import generate_mcqs_from_topic  # Assuming this supports difficulty levels
from pdf_export import generate_feedback_from_results, generate_pdf_with_feedback_and_analytics



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

def display_results(selected_topics):
    """Display final quiz results."""
    st.title("Quiz Results")
    
    total_correct = sum(1 for answer in st.session_state.total_answers if answer['user_answer'] == answer['correct_answer'])
    total_questions = len(st.session_state.total_answers)
    st.write(f"### Grand Total: {total_correct}/{total_questions} Correct")
    
    category_scores = {}
    for answer in st.session_state.total_answers:
        category = answer['difficulty'].capitalize()
        if category not in category_scores:
            category_scores[category] = {'correct': 0, 'total': 0}
        category_scores[category]['total'] += 1
        if answer['user_answer'] == answer['correct_answer']:
            category_scores[category]['correct'] += 1

    for category, scores in category_scores.items():
        st.write(f"### {category} Level: {scores['correct']}/{scores['total']} Correct")
    
    st.write("### Review Your Answers")
    for answer in st.session_state.total_answers:
        st.write(f"**Q:** {answer['question']}")
        st.write(f"- **Your Answer:** {answer['user_answer']}")
        st.write(f"- **Correct Answer:** {answer['correct_answer']}")
        st.write("---")
    
    # Generate feedback based on results
    feedback = generate_feedback_from_results(
        topic=selected_topics,  # Pass selected topics dynamically
        total_score=total_correct,
        total_questions=total_questions,
        correct_count=total_correct,
        incorrect_count=total_questions - total_correct,
        difficulty=st.session_state.difficulty,
        difficulty_performance="Moderate performance on hard questions"  # Add your logic for difficulty performance
    )
    
    if feedback:
        st.write("### Feedback")
        st.json(feedback)

        # Generate and store feedback in PDF
        quiz_results = {
            "total_correct": total_correct,
            "total_questions": total_questions
        }
        
        # Generate PDF with results, feedback, and analytics
        generate_pdf_with_feedback_and_analytics(quiz_results, feedback)  
        st.success("PDF with results, feedback, and analytics has been generated.")
        
        # Provide download button for the generated PDF
        st.download_button(
            label="Download Quiz Results PDF",
            data=open("quiz_results_with_feedback_and_analytics.pdf", "rb").read(),
            file_name="quiz_results_with_feedback_and_analytics.pdf",
            mime="application/pdf"
        )

def main():
    """Main function to run the Streamlit app."""
    st.sidebar.title("Adaptive MCQ Generator")
    
    topics_list = ["DBMS", "ML", "RPA", "CLOUD", "JAVA", "SQL", "PYTHON", "OS", "MONGODB", "NETWORKING", "CYBER SECURITY"]
    selected_topics = st.sidebar.multiselect("Select up to 4 topics", options=topics_list, max_selections=4)
    
    # Initialize session state variables
    if 'total_answers' not in st.session_state:
        st.session_state.total_answers = []
    if 'question_batch' not in st.session_state:
        st.session_state.question_batch = 1
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = "easy"
    if 'correct_count' not in st.session_state:
        st.session_state.correct_count = 0

    if len(st.session_state.total_answers) >= 20:
        display_results(selected_topics)
        return

    # Start Quiz button logic
    if st.sidebar.button("Start Quiz"):
        if selected_topics:
            with st.spinner(f"Generating MCQs for the topics: {', '.join(selected_topics)}..."):
                mcq_data = generate_mcqs_from_topic(selected_topics, difficulty=st.session_state.difficulty)
            
            if mcq_data:
                # Get scenario and questions from generated data
                scenario = mcq_data[0].get("scenario", "No scenario provided.")
                questions = mcq_data[0].get("questions", [])
                
                # Store the scenario and questions in session state
                st.session_state.scenario = scenario
                st.session_state.mcqs = questions
                st.session_state.submitted = False
                st.session_state[f'user_answers_{st.session_state.question_batch}'] = [None] * len(questions)
                st.rerun()
        else:
            st.sidebar.error("Please select at least one topic.")

    # If questions are available, display them
    if 'mcqs' in st.session_state and st.session_state.mcqs:
        correct_count = display_mcq(
            st.session_state.mcqs,
            current_level=st.session_state.difficulty,
            question_batch=st.session_state.question_batch,
            total_answers=st.session_state.total_answers,
        )
        
        # Update the difficulty level based on the user's performance
        st.session_state.difficulty = get_next_difficulty(correct_count)

        # If the batch has been submitted, move to the next batch
        if st.session_state[f'submitted_{st.session_state.question_batch}']:
            st.session_state.correct_count += correct_count
            st.session_state.question_batch += 1
            st.session_state.previous_score = correct_count

            # Generate the next batch if fewer than 20 questions have been answered
            if len(st.session_state.total_answers) < 20:
                next_difficulty = st.session_state.difficulty
                with st.spinner(f"Fetching next batch of questions for difficulty: {next_difficulty}..."):
                    mcq_data = generate_mcqs_from_topic(selected_topics, difficulty=next_difficulty)
                if mcq_data:
                    scenario = mcq_data[0].get("scenario", "No scenario provided.")
                    questions = mcq_data[0].get("questions", [])
                    st.session_state.scenario = scenario
                    st.session_state.mcqs = questions
                    st.session_state[f'user_answers_{st.session_state.question_batch}'] = [None] * len(questions)
                st.rerun()
            else:
                st.write("### Quiz Completed!")
                display_results(selected_topics)

main()
