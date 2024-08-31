import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the OpenAI API Key from the environment variable
API_KEY = os.getenv("OPENAI_API_KEY")

# Check if the API key is available, else raise an error
if not API_KEY:
    st.error("No OpenAI API key found. Please set the 'OPENAI_API_KEY' environment variable.")
    st.stop()

# Function to simulate agents' work
def agent_interactions(problem, barrier, affected, wish):
    openai.api_key = API_KEY  # Use the API key from the environment variable

    # Agent 2: Problem Analysis
    problem_analysis_prompt = f"""
    Based on the following input:
    Problem: {problem}
    Barriers: {barrier}
    Affected Parties: {affected}
    Please provide a detailed problem analysis, including relevant studies and data showing the problem's size and significance.
    """
    problem_analysis_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that helps with problem analysis and innovation generation."},
            {"role": "user", "content": problem_analysis_prompt}
        ]
    ).choices[0].message["content"].strip()

    # Agent 4: Value Proposition Canvas
    value_proposition_prompt = f"""
    Please analyze the problem in the following structure:
    1. Problem: {problem}
    2. Why is it relevant and urgent to solve?
    3. Why will it be even more relevant in the future?
    4. Who is mostly affected by the problem?
    5. Describe an ideal scenario based on the following wish: {wish}.
    """
    value_proposition_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that helps with value proposition analysis."},
            {"role": "user", "content": value_proposition_prompt}
        ]
    ).choices[0].message["content"].strip()

    return problem_analysis_response, value_proposition_response

# Streamlit App
st.title("Trend to Opportunity Transformer")

st.write("This AI helps you generate innovative ideas from urgent problems and unmet needs.")

st.header("Agent 1: Define the Unmet Need or Problem")
problem = st.text_area("Describe a problem that justifies developing a solution or innovation.")  # Ensure the string is properly enclosed in quotes
barrier = st.text_area("What is stopping us from solving or overcoming the problem?")
affected = st.text_area("Who is mostly affected by this problem?")

st.header("Agent 3: Ideal Situation")
wish = st.text_area("If you could wish for what you want, what would be an ideal situation or process?")

# Button to run the agents
if st.button("Generate Analysis and Ideas"):
    if problem and barrier and affected and wish:
        try:
            problem_analysis, value_proposition = agent_interactions(problem, barrier, affected, wish)
            
            st.subheader("Agent 2: Problem Analysis")
            st.write(problem_analysis)
            
            st.subheader("Agent 4: Value Proposition Canvas Analysis")
            st.write(value_proposition)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please fill in all fields.")
