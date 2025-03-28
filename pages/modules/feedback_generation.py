# feedback_generation.py
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
    {
        "overall_performance": "[Short performance summary]",
        "correct_vs_incorrect": {
            "correct_count": "[Number of correct answers]",
            "incorrect_count": "[Number of incorrect answers]",
            "analysis": "[Analysis of why certain questions might have been answered incorrectly]"
        },
        "areas_of_improvement": "[Specific areas to improve based on performance]",
        "topic_specific_feedback": "[Topic-specific suggestions to deepen knowledge]",
        "next_steps": "[Actions to take next for improvement]"
    }
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
