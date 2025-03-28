# AI-Powered Adaptive Quiz App

## Overview
This AI-powered quiz application generates scenario-based multiple-choice questions (MCQs) and adapts to the user's answers by adjusting difficulty levels dynamically. The app leverages AI to create engaging quizzes that test users' understanding of real-world scenarios.

## Features
- **Scenario-Based MCQs**: The app generates questions relevant to the selected topic and presents them within an industrial or real-world scenario.
- **Adaptive Difficulty**: Based on the user's performance, the difficulty of the next set of questions is adjusted dynamically (Easy → Medium → Hard).
- **User Authentication**: Users can sign up and log in using a traditional method or Google authentication.
- **Performance Analytics**: After completing the quiz, users receive detailed feedback and analytics.
- **PDF Report Generation**: The app generates a PDF report with feedback, user performance statistics, and insights.

## How It Works
1. **Quiz Generation**: 
   - Users select up to 4 topics from a predefined list.
   - The app generates MCQs based on the selected topics and a starting difficulty level.
2. **Adaptive Learning Mechanism**:
   - As users answer questions, their responses are evaluated.
   - The next batch of questions adapts based on their performance.
3. **Quiz Completion & Results**:
   - After answering 20 questions, users receive a detailed performance report.
   - The system generates a feedback-driven PDF for download.

## Installation & Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/AIQuizzer.git
   cd AIQuizzer
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the Streamlit app:**
   ```sh
   streamlit run main.py
   ```


## Deployment on Streamlit Cloud
1. Push the project to GitHub.
2. Deploy it on Streamlit Community Cloud.
3. Ensure you configure environment variables for secure authentication.

## Technologies Used
- **Python**
- **Streamlit**
- **PDF Generation**
- **Dynamic Adaptive Quiz Logic**

## Future Enhancements
- **Leaderboard System**
- **AI-Driven Personalized Learning Paths**
- **Multiplayer Quiz Challenges**


