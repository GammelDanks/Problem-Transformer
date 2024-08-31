import streamlit as st
import openai
import matplotlib.pyplot as plt

# Function to simulate agents' work
def agent_interactions(api_key, problem, barrier, affected, wish):
    openai.api_key = api_key  # Use the API key provided by the user

    # Problem Summary with Insights
    problem_summary_prompt = f"""
    Please summarize the following problem, providing additional insights that may help in understanding the problem better:
    Problem: {problem}
    Barriers: {barrier}
    Affected Parties: {affected}
    Ideal Situation: {wish}
    """
    problem_summary_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert analyst who provides summaries and insights on complex problems."},
            {"role": "user", "content": problem_summary_prompt}
        ]
    ).choices[0].message["content"].strip()

    # Empirical Evidence and Data-Driven Arguments
    empirical_evidence_prompt = f"""
    Based on the following problem description:
    Problem: {problem}
    Barriers: {barrier}
    Affected Parties: {affected}
    Please provide empirical evidence and data-driven arguments supporting the relevance and magnitude of the problem. Include relevant statistics, studies, and expert opinions.
    """
    empirical_evidence_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert researcher who provides empirical evidence and data-driven arguments."},
            {"role": "user", "content": empirical_evidence_prompt}
        ]
    ).choices[0].message["content"].strip()

    # Unconsidered Impacts
    unconsidered_impacts_prompt = f"""
    Please identify and describe impacts of the following problem that might not have been considered, including long-term, broader organizational, and indirect effects:
    Problem: {problem}
    Immediate Effects: {barrier}
    """
    unconsidered_impacts_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert analyst who identifies unconsidered impacts of complex problems."},
            {"role": "user", "content": unconsidered_impacts_prompt}
        ]
    ).choices[0].message["content"].strip()

    # Market Potential and Challenges Analysis
    market_analysis_prompt = f"""
    Analyze the following problem and determine whether it represents a business opportunity. Consider market size, profitability, adoption readiness, technology development challenges, and market entry challenges:
    Problem: {problem}
    """
    market_analysis_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in market analysis, specializing in identifying business opportunities based on problem descriptions."},
            {"role": "user", "content": market_analysis_prompt}
        ]
    ).choices[0].message["content"].strip()

    return problem_summary_response, empirical_evidence_response, unconsidered_impacts_response, market_analysis_response

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
st.title("Trend to Opportunity Transformer")

st.write("This AI helps you generate innovative ideas from urgent problems and unmet needs.")

# Input for OpenAI API Key
api_key = st.text_input("Enter your OpenAI API Key:", type="password", help="Your OpenAI API key is needed to generate responses.")

if not api_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()

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
if st.button("Generate Analysis and Ideas"):
    if problem and barrier and affected and wish:
        try:
            # Get the analysis from the agent
            problem_summary, empirical_evidence, unconsidered_impacts, market_analysis = agent_interactions(api_key, problem, barrier, affected, wish)
            
            st.subheader("Problem Summary with Insights")
            st.write(problem_summary)
            
            st.subheader("Empirical Evidence and Data-Driven Arguments")
            st.write(empirical_evidence)
            
            st.subheader("Unconsidered Impacts")
            st.write(unconsidered_impacts)
            
            st.subheader("Market Potential and Challenges Analysis")
            st.write(market_analysis)
            
            # Example potential and challenge scores (this would be dynamically calculated based on the market analysis)
            potential_score = 8.5  # Scale of 1-10
            challenge_score = 6.0  # Scale of 1-10

            st.subheader("Opportunity Matrix")
            plot_opportunity_matrix(potential_score, challenge_score)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please fill in all fields before generating the analysis.")
