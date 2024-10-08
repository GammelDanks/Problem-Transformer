import streamlit as st
import openai
import matplotlib.pyplot as plt
import time

# Retrieve the OpenAI API Key from Streamlit secrets
openai_api_key = st.secrets["general"]["OPENAI_API_KEY"]

# Set the OpenAI API key
openai.api_key = openai_api_key

# Function to simulate agents' work with rate limit handling and a delay between API requests
def agent_interactions(problem, barrier, affected, wish):

    def make_api_call(prompt, system_message):
        retries = 3  # Number of retries in case of rate limit errors
        delay = 2    # Initial delay in seconds before retrying after a rate limit error
        for i in range(retries):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message['content'].strip()
            except openai.error.RateLimitError:
                if i < retries - 1:
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    raise Exception("Rate limit exceeded. Please try again later.")
            except Exception as e:
                raise Exception(f"An error occurred: {e}")

    # Problem Summary with Insights
    problem_summary_prompt = f"""
    Summarize the problem and provide key insights:
    Problem: {problem}
    Barriers: {barrier}
    Affected Parties: {affected}
    Ideal Situation: {wish}
    """
    problem_summary_response = make_api_call(
        problem_summary_prompt,
        "You are an expert analyst who provides concise summaries and insights on complex problems."
    )

    # Empirical Evidence and Data-Driven Arguments
    empirical_evidence_prompt = f"""
    Provide empirical evidence and data-driven arguments supporting the relevance and magnitude of the problem:
    Problem: {problem}
    Barriers: {barrier}
    Affected Parties: {affected}
    """
    empirical_evidence_response = make_api_call(
        empirical_evidence_prompt,
        "You are an expert researcher who provides concise empirical evidence and data-driven arguments."
    )

    # Potential: Market Size, Profitability, and Adoption Readiness
    potential_analysis_prompt = f"""
    Analyze the market potential considering market size, profitability, and adoption readiness:
    Problem: {problem}
    Barriers: {barrier}
    Affected Parties: {affected}
    Ideal Situation: {wish}
    """
    potential_analysis_response = make_api_call(
        potential_analysis_prompt,
        "You are an expert in market analysis, providing concise evaluations of market potential."
    )

    # Challenges: Technology Development Challenges and Market Entry Challenges
    challenges_analysis_prompt = f"""
    Identify the key challenges in solving the problem, focusing on:
    1. Technology Development Challenges.
    2. Market Entry Challenges.
    
    Problem: {problem}
    Barriers: {barrier}
    Affected Parties: {affected}
    """
    challenges_analysis_response = make_api_call(
        challenges_analysis_prompt,
        "You are an expert in analyzing challenges related to technology development and market entry."
    )

    return problem_summary_response, empirical_evidence_response, potential_analysis_response, challenges_analysis_response

# Function to plot the opportunity matrix
def plot_opportunity_matrix(potential_score, challenge_score):
    fig, ax = plt.subplots()
    
    # Set the limits for the axes
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    
    # Plot the opportunity as a dot
    ax.scatter(challenge_score, potential_score, color='blue', s=100)
    
    # Add labels and grid
    ax.set_xlabel('Challenges (Lower is Better)')
    ax.set_ylabel('Market Potential (Higher is Better)')
    ax.set_title('Opportunity Matrix')
    ax.grid(True)
    
    # Add annotations
    ax.text(challenge_score, potential_score, 'Opportunity', fontsize=12, ha='right')

    st.pyplot(fig)

# Streamlit App
st.title("Problem Analyser")

st.write("This AI helps to analyze the problem that you are aiming to solve.")

# Step 1: Define the Core Problem
st.header("Step 1: Define the Core Problem")
with st.expander("Click here to describe the core problem", expanded=True):
    problem = st.text_area(
        "What is the core problem you are facing?",
        placeholder="Describe the problem in one or two sentences.",
        help="Please describe the problem in one or two sentences. Provide the context (the industry, the environment, the task, the process in which the problem is located). Example: In many production plants such as steel or automotive production, high noise levels and extreme heat create a harsh work environment for the workers."
    )

# Step 2: Immediate Effect
st.header("Step 2: Immediate Effect")
with st.expander("Click here to describe the immediate effect of the problem", expanded=True):
    barrier = st.text_area(
        "What is the immediate effect of the problem?",
        placeholder="Describe the immediate consequences of the problem.",
        help="Please describe the consequences of the problem. Try to indicate why it is a relevant problem. Do not go into numbers and details yet. Example: The harsh environment leads to worker fatigue, increased safety incidents, and lower productivity. Prolonged exposure to noise and heat can result in long-term health issues, including hearing loss and heat-related illnesses, and turnover."
    )

# Step 3: Context Relevance
st.header("Step 3: Context Relevance")
with st.expander("Click here to describe the contexts where the problem is more or less relevant", expanded=True):
    context = st.text_area(
        "Are there situations or contexts in which this problem is less relevant or particularly relevant?",
        placeholder="Describe the contexts where the problem is more or less present.",
        help="The problem may not always be equally relevant and severe. Try to describe when or in which context the problem is more or less present. Example: This problem is more relevant in continuous, high-intensity operations like steel forging and for workers that cannot even leave the production plant during the breaks (long distances)."
    )

# Step 4: Affected Parties
st.header("Step 4: Affected Parties")
with st.expander("Click here to describe who is affected by the problem", expanded=True):
    affected = st.text_area(
        "Who is particularly affected?",
        placeholder="Specify the groups affected by the problem.",
        help="Try to specify the group of subjects (people, firms, governments, animals and plants, etc.) that are mostly affected by the problem. Example: The group affected are production workers, machine operators, and maintenance staff who are directly exposed to the harsh conditions. Additionally, supervisors, production plant designers, and safety personnel responsible for monitoring and ensuring a safe work environment are also impacted."
    )

# Step 5: Challenges
st.header("Step 5: Challenges to Solve the Problem")
with st.expander("Click here to describe the challenges in solving the problem", expanded=True):
    wish = st.text_area(
        "What are the factors making this problem very challenging to remove?",
        placeholder="Describe the challenges in solving the problem.",
        help="Try to describe briefly why it is hard to solve the problem. What are the restrictions, interdependencies, etc., that make many potential solutions not effective or feasible? Example: Implementing protective measures, such as improved ventilation or soundproofing, can be costly and may disrupt workflow, while personal protective equipment, though helpful, can be uncomfortable and may hinder workers' mobility and performance. Additionally, regulatory compliance and budget constraints further complicate the implementation of effective solutions."
    )

# Button to run the agents
if st.button("Analyse Problem"):
    if problem and barrier and affected and wish:
        try:
            # Get the analysis from the agent
            problem_summary, empirical_evidence, potential_analysis, challenges_analysis = agent_interactions(problem, barrier, affected, wish)
            
            st.subheader("Problem Summary with Insights")
            st.write(problem_summary)
            
            st.subheader("Empirical Evidence and Data-Driven Arguments")
            st.write(empirical_evidence)
            
            st.subheader("Market Potential Analysis")
            st.write(potential_analysis)
            
            st.subheader("Challenges Analysis")
            st.write(challenges_analysis)
            
            # Example potential and challenge scores (this would be dynamically calculated based on the market analysis)
            potential_score = 8.5  # Scale of 1-10
            challenge_score = 6.0  # Scale of 1-10

            st.subheader("Opportunity Matrix")
            plot_opportunity_matrix(potential_score, challenge_score)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please fill in all fields before generating the analysis.")
