import streamlit as st
import openai

# Set the OpenAI API key
openai.api_key = st.secrets["openai"]["openai_api_key"]

# Function to retrieve competitors using OpenAI
def get_competitors(solution_description):
    prompt = f"""
    Based on the following solution description:
    "{solution_description}"
    
    Please list companies that offer similar solutions. For each company, provide:
    - The name of the company
    - A brief description of their products/services
    - If possible, provide a few links to articles, blog posts, or resources where these competitors are discussed or reviewed.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a market analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )
    
    competitors = response.choices[0].message['content'].strip()
    return competitors

# Function to analyze the most important features
def analyze_features(solution_description):
    prompt = f"""
    Based on the companies offering similar solutions to the following description:
    "{solution_description}"
    
    Which features of competitors seem to resonate most in the market and with paying users? Please provide a list of features with a short description of why they are so important and beneficial. Add any relevant sources if possible.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a market analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )
    
    features = response.choices[0].message['content'].strip()
    return features

# Function to analyze key hypotheses
def analyze_hypotheses(solution_description):
    prompt = f"""
    Based on the companies offering similar solutions to the following description:
    "{solution_description}"
    
    Which key hypotheses need to be tested to ensure that the product meets the needs and solves the problem? Please provide a list of hypotheses with a short description of what needs to be tested because it is an open question or uncertainty.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a market analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )
    
    hypotheses = response.choices[0].message['content'].strip()
    return hypotheses

# Streamlit App
st.title("Simplified Competitor Analysis Tool")

# Step 1: Input Solution Description
solution_description = st.text_area(
    "Describe the solution you are working on:",
    placeholder="Enter a detailed description of your product or service idea..."
)

if st.button("Analyze Solution"):
    if solution_description:
        # Step 2: Get Competitors
        st.subheader("1. Competitor Analysis")
        competitors = get_competitors(solution_description)
        st.write(competitors)
        
        # Step 3: Analyze Features
        st.subheader("2. Key Features Resonating in the Market")
        features = analyze_features(solution_description)
        st.write(features)
        
        # Step 4: Analyze Key Hypotheses
        st.subheader("3. Key Hypotheses to Test")
        hypotheses = analyze_hypotheses(solution_description)
        st.write(hypotheses)
    else:
        st.warning("Please enter a solution description to proceed.")
