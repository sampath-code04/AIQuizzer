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

# Updated prompt template with scenario-based adaptive learning
prompt_template = PromptTemplate(
    input_variables=["topic", "difficulty"],
    template="""
    You are an advanced quiz generator focused on scenario-based adaptive learning.

    ### Task:
    - Present a **real-world problem or scenario** relevant to the specified topic.
    - The scenario should be engaging and **realistically applicable in an industrial or daily life setting**.
    - Following the scenario, generate **5 multiple-choice questions (MCQs)** based on it.
    - The questions should progress in difficulty and align with the level specified.

    ### Difficulty Levels:
    - **Easy (0-4):** Basic understanding, recall, or simple application of knowledge.
    - **Medium (5-8):** Requires moderate analysis, problem-solving,mathematical problems, coding challenges and conceptual application.Give numerical problems.
    - **Hard (9-10):** Complex decision-making, real-world application, or critical thinking.Give coding problems.

    ### Output Format:
    The response must be a JSON array structured as follows:
    ```json
    [
        {{
            "scenario": "[Brief scenario description relevant to the topic]",
            "questions": [
                {{
                    "question": "[MCQ Question 1 text]",
                    "choices": [
                        "a) [Option A text]",
                        "b) [Option B text]",
                        "c) [Option C text]",
                        "d) [Option D text]"
                    ],
                    "answer": "[Full text of the correct option, e.g., 'a) Option A text']"
                }},
                // Repeat for 4 more questions
            ]
        }}
    ]
    ```

    ### Example:
    **Topic:** Cybersecurity | **Difficulty:** Medium  
    **Scenario:**  
    A small business is experiencing frequent unauthorized access attempts on its internal servers.  
    Employees have weak passwords and often use the same credentials across multiple services.  

    **MCQs Generated:**
    1. What is the most immediate security risk in this situation?
    2. Which security protocol would be most effective to mitigate the risk?
    3. How can employees be educated to reduce cybersecurity threats?
    4. What is the role of multi-factor authentication in this context?
    5. If a breach occurs, what is the best response strategy?

    **Now, generate a scenario-based MCQ set for:**  
    **Topic:** {topic} | **Difficulty:** {difficulty}
    """
)


def generate_mcqs_from_topic(topic, difficulty):
    """Generates MCQs with different seed values to avoid repetition."""
    chain = prompt_template | llm | json_parser

    try:
        # Introduce randomness in question generation
        seed = random.randint(1, 100000)  
        result = chain.invoke({"topic": topic, "difficulty": difficulty, "seed": seed})
        
        if result:
            print("\n\n\nGenerated MCQs Response!!!")  # Debugging output
        return result
    except OutputParserException as e:
        st.error(f"Error parsing output: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None