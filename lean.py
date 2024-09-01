import streamlit as st
import openai
import time

# Set the OpenAI API key
openai.api_key = st.secrets["openai"]["openai_api_key"]

# Function to generate text using the Chat API (gpt-4)
def generate_text(prompt, max_tokens=500):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides specific and practical advice."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content'].strip()

# Step 1: Problem and Solution Description
st.title("Startup Idea Validator")

st.header("Step 1: Define the Problem and Solution")
problem_description = st.text_area(
    "Describe the Problem", 
    "Please describe briefly the problem that you are addressing. Consider the pain points and the outcome the customers desire."
)
solution_description = st.text_area(
    "Describe Your Solution or Idea", 
    "Describe how your solution addresses the problem. What is the key value proposition?"
)

# Button to move to Step 2
if st.button("Proceed to Customer Segments"):
    if problem_description and solution_description:
        st.session_state.problem_description = problem_description
        st.session_state.solution_description = solution_description
    else:
        st.warning("Please complete both the problem and solution description before proceeding.")

# Step 2: Customer Segments (Appears after Step 1 is completed)
if 'problem_description' in st.session_state and 'solution_description' in st.session_state:
    st.header("Step 2: Identify Target Customer Segments")
    
    # Generate a tailored question based on the input from Step 1
    customer_segments_prompt = (
        f"Based on the following problem: '{st.session_state.problem_description}', and solution: '{st.session_state.solution_description}', "
        "please describe the customer segments or user groups most affected by the problem and who would benefit the most from the solution."
    )
    st.write(customer_segments_prompt)

    customer_segments = st.text_area(
        "Who are your target customers?",
        "Describe the customer segments or user groups."
    )

    # Button to confirm customer segments and proceed to next steps
    if st.button("Proceed to Hypotheses and MVP"):
        if customer_segments:
            st.session_state.customer_segments = customer_segments
        else:
            st.warning("Please describe the customer segments before proceeding.")

# Step 3: Hypotheses Generation (Appears after Step 2 is completed)
if 'customer_segments' in st.session_state:
    st.header("Step 3: Hypotheses for Validation")
    
    hypotheses_prompt = (
        f"Based on the following details:\n"
        f"Problem: {st.session_state.problem_description}\n"
        f"Solution: {st.session_state.solution_description}\n"
        f"Customer Segments: {st.session_state.customer_segments}\n\n"
        "Please generate the following hypotheses:\n"
        "1. A Value Hypothesis that identifies the critical uncertainties and open questions related to whether the solution will effectively address the specific problems of the identified customer segments.\n"
        "2. A Growth Hypothesis that focuses on the uncertainties related to the solution's scalability within these customer segments and market potential.\n"
        "3. Additional hypotheses that address the most relevant and uncertain aspects like pricing, market size, or customer behavior specifically related to these customer segments.\n\n"
        "In addition, please provide 4-5 specific, one-sentence hypotheses that focus on critical uncertainties essential for the success of the solution. These could include hypotheses related to customer usage patterns, long-term benefits for customers, willingness to pay, time required to adopt the solution, and the convenience of the solution."
    )
    
    try:
        hypotheses_response = generate_text(hypotheses_prompt)
        st.session_state.hypotheses = hypotheses_response  # Store the hypotheses for later use
        st.write(hypotheses_response)
    except openai.error.RateLimitError:
        st.warning("Rate limit reached. Please wait a moment and try again.")
        time.sleep(20)

    # Step 4: MVP Suggestion
    st.header("Step 4: Minimum Viable Product (MVP) and Feature Integration Roadmap")
    
    mvp_prompt = (
        f"Given the problem '{st.session_state.problem_description}', solution '{st.session_state.solution_description}', and customer segments '{st.session_state.customer_segments}', "
        "please provide a highly focused suggestion for a Minimum Viable Product (MVP) that includes only the most essential features necessary to test the core hypothesis with these customer segments. "
        "Also, provide a roadmap for integrating additional features over time, focusing on early prototypes, simulations, or experiments that allow for low-risk testing of the solution among the identified customer segments."
    )
    
    try:
        mvp_response = generate_text(mvp_prompt)
        st.session_state.mvp_suggestions = mvp_response  # Store the MVP suggestions for later use
        st.write(mvp_response)
    except openai.error.RateLimitError:
        st.warning("Rate limit reached. Please wait a moment and try again.")
        time.sleep(20)

    # Step 5: Recommendations for Initial Testing
    st.header("Step 5: Recommendations for Initial Testing")
    
    testing_prompt = (
        f"Based on the following hypotheses:\n{st.session_state.hypotheses}\n"
        f"And the following MVP suggestions:\n{st.session_state.mvp_suggestions}\n"
        "Recommend the three most important initial tests, checks, analyses, surveys, observational studies, or data analysis steps "
        "that the innovators and founders should prioritize to validate their assumptions with the identified customer segments and de-risk the project. "
        "Please include specific questions to ask these customer segments, key data points to analyze, types of test customers to involve, and the critical financial variables to assess."
    )
    
    try:
        testing_response = generate_text(testing_prompt)
        st.write(testing_response)
    except openai.error.RateLimitError:
        st.warning("Rate limit reached. Please wait a moment and try again.")
        time.sleep(20)
