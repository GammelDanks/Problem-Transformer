import streamlit as st
import openai

# Hardcoded OpenAI API Key (replace with your actual key)
API_KEY = "your_openai_api_key_here"  # <-- Replace this with your actual OpenAI API key

# Function to simulate agents' work
def agent_interactions(problem, barrier, affected, wish):
    openai.api_key = API_KEY  # Use the hardcoded API key

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
        model="
