from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import tempfile
import numpy as np
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import streamlit as st
import random

# Load environment variables
load_dotenv()

# Get the Groq API key from Streamlit secrets
groq_api_key = st.secrets["GROQ_API_KEY"]

# Initialize Groq LLM
llm = ChatGroq(temperature=0.7, groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile")

# Define the output parser
json_parser = JsonOutputParser()

# Define a new prompt template for feedback generation
feedback_prompt_template = PromptTemplate(
    input_variables=["topic", "total_score", "total_questions", "correct_count", "incorrect_count", "difficulty", "difficulty_performance"],
    template="""
    You are a learning assistant that provides personalized feedback to students based on their quiz performance.

    ### Task:
    - Based on the quiz performance, generate a detailed feedback report that includes:
        1. **Overall Performance Summary**: Provide a brief summary of how well the student did (e.g., Excellent, Good, Needs Improvement).
        2. **Correct vs Incorrect Analysis**: Mention how many answers were correct and incorrect, and explain why certain questions might have been answered incorrectly.
        3. **Area of Improvement**: Based on the difficulty level of the questions, suggest specific areas for improvement.
        4. **Topic-Specific Feedback**: Provide feedback specific to the topic (e.g., Cybersecurity, Machine Learning, etc.) with actionable suggestions.
        5. **Next Steps**: Provide a set of recommended actions for the student to improve their understanding of the topic.

    ### Input Details:
    - **Topic**: {topic}
    - **Total Score**: {total_score}
    - **Total Questions**: {total_questions}
    - **Correct Answers**: {correct_count}
    - **Incorrect Answers**: {incorrect_count}
    - **Difficulty Level**: {difficulty}
    - **Difficulty Performance**: {difficulty_performance}

    ### Output:
    The response should be structured as a JSON array with the following details:
    ```json
    {{
        "overall_performance": "[Short performance summary]",
        "correct_vs_incorrect": {{
            "correct_count": "[Number of correct answers]",
            "incorrect_count": "[Number of incorrect answers]",
            "analysis": "[Analysis of why certain questions might have been answered incorrectly]"
        }},
        "areas_of_improvement": "[Specific areas to improve based on performance]",
        "topic_specific_feedback": "[Topic-specific suggestions to deepen knowledge]",
        "next_steps": "[Actions to take next for improvement]"
    }}
    ```

    ### Example:
    **Topic:** Cybersecurity | **Difficulty:** Medium  
    **Total Score:** 8/10  
    **Correct Answers:** 8  
    **Incorrect Answers:** 2  
    **Difficulty Level:** Medium  
    **Difficulty Performance:** Moderate performance on hard questions  

    **Feedback:**  
    Overall Performance: You did well, scoring 8 out of 10! Keep up the good work.  
    Correct vs Incorrect: You answered 8 questions correctly, but struggled with 2 harder questions related to network security.  
    Areas of Improvement: Focus more on understanding advanced cybersecurity protocols and network security management.  
    Topic-Specific Feedback: Learn more about firewalls, VPNs, and encryption techniques.  
    Next Steps: Read up on advanced security strategies and practice real-world scenarios to strengthen your understanding.

    **Now, generate feedback based on the following quiz results for:**  
    **Topic:** {topic} | **Total Score:** {total_score} | **Total Questions:** {total_questions} | **Correct Answers:** {correct_count} | **Incorrect Answers:** {incorrect_count} | **Difficulty:** {difficulty} | **Difficulty Performance:** {difficulty_performance}
    """
)

# Define the feedback prompt chain
feedback_chain = feedback_prompt_template | llm | json_parser


def generate_feedback_from_results(topic, total_score, total_questions, correct_count, incorrect_count, difficulty, difficulty_performance):
    """Generate feedback based on quiz results."""
    try:
        # Generate a unique seed for feedback generation to introduce variety in responses
        seed = random.randint(1, 100000)
        
        # Invoke the feedback generation chain
        feedback_result = feedback_chain.invoke({
            "topic": topic,
            "total_score": total_score,
            "total_questions": total_questions,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "difficulty": difficulty,
            "difficulty_performance": difficulty_performance,
            "seed": seed
        })
        
        if feedback_result:
            print("\n\n\nGenerated Feedback Response:", feedback_result)  # Debugging output
        return feedback_result
    except OutputParserException as e:
        st.error(f"Error parsing output: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None
        
def generate_difficulty_performance_feedback(difficulty_scores):
    """Generate feedback based on difficulty performance."""
    feedback = {}

    for level, scores in difficulty_scores.items():
        correct = scores["correct"]
        total = scores["total"]
        performance_percentage = (correct / total) * 100 if total > 0 else 0

        if performance_percentage >= 80:
            feedback[level] = f"Excellent performance on {level} level questions! Keep it up."
        elif performance_percentage >= 50:
            feedback[level] = f"Good job on {level} level questions, but there's room for improvement."
        else:
            feedback[level] = f"You struggled with {level} level questions. Consider revisiting this topic for better understanding."

    return feedback

def track_performance_by_difficulty():
    """Track performance by difficulty (easy, medium, hard)."""
    difficulty_scores = {
        "easy": {"correct": 0, "total": 0},
        "medium": {"correct": 0, "total": 0},
        "hard": {"correct": 0, "total": 0}
    }

    # Calculate correct answers for each difficulty level
    for answer in st.session_state.total_answers:
        difficulty = answer['difficulty']
        if answer['user_answer'] == answer['correct_answer']:
            difficulty_scores[difficulty]['correct'] += 1
        difficulty_scores[difficulty]['total'] += 1

    return difficulty_scores

def generate_pdf_with_feedback_and_analytics(quiz_results, feedback, filename="quiz_results_with_feedback_and_analytics.pdf"):
    """Generate PDF to store quiz results along with feedback and analytics."""
    # Create PDF instance
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set title
    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(200, 10, txt="Quiz Results, Feedback, and Analytics", ln=True, align="C")

    # Add Date/Time
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    # Add Quiz Results Section
    pdf.ln(10)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Quiz Results", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Total Correct: {quiz_results['total_correct']}/{quiz_results['total_questions']}", ln=True)
    pdf.cell(200, 10, txt=f"Score: {quiz_results['total_correct']} out of {quiz_results['total_questions']}", ln=True)

    # Add Analytics Section
    pdf.ln(10)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Quiz Analytics", ln=True)

    # Add pie chart for correct vs incorrect answers
    correct_count = quiz_results['total_correct']
    incorrect_count = quiz_results['total_questions'] - correct_count

    # Create a pie chart for correct vs incorrect answers
    fig, ax = plt.subplots(figsize=(3, 3))
    labels = ['Correct', 'Incorrect']
    sizes = [correct_count, incorrect_count]
    colors = ['green', 'red']
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, shadow=True)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the chart as a PNG image in a BytesIO object
    chart_image = io.BytesIO()
    plt.savefig(chart_image, format='png')
    chart_image.seek(0)  # Rewind the file pointer to the start

    # Create a temporary file to store the image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(chart_image.getbuffer())  # Write BytesIO content to the temporary file
        temp_file_path = temp_file.name  # Get the file path

    # Add chart image to PDF
    pdf.ln(10)
    pdf.image(temp_file_path, x=None, y=None, w=100)

    # Add Feedback Section
    pdf.ln(10)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Feedback", ln=True)

    # Include feedback data
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"Overall Performance: {feedback['overall_performance']}")
    pdf.multi_cell(0, 10, f"Correct Answers: {feedback['correct_vs_incorrect']['correct_count']}")
    pdf.multi_cell(0, 10, f"Incorrect Answers: {feedback['correct_vs_incorrect']['incorrect_count']}")
    pdf.multi_cell(0, 10, f"Analysis of Incorrect Answers: {feedback['correct_vs_incorrect']['analysis']}")
    pdf.multi_cell(0, 10, f"Areas for Improvement: {feedback['areas_of_improvement']}")
    pdf.multi_cell(0, 10, f"Topic-Specific Feedback: {feedback['topic_specific_feedback']}")
    pdf.multi_cell(0, 10, f"Next Steps: {feedback['next_steps']}")

    # Save PDF to a file
    pdf.output(filename)
    print(f"PDF saved as {filename}")

