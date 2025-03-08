import openai
import requests
import datetime
import re
import streamlit as st

# 🔹 Set Your API Keys Here
GOOGLE_API_KEY = "AIzaSyDAdbb_xnGRsbI77-ZfnlhMc-6iLDTVxiE"  # 🔴 Replace with your Google API Key
SEARCH_ENGINE_ID = "94d30f152c43a48a7"  # 🔴 Replace with your Custom Search Engine ID

# ✅ Function to Extract Keywords from User Input
def extract_keywords(text):
    """Extracts important keywords from user input using regex-based filtering."""
    try:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)  # Extract words (min 4 letters)
        keywords = " ".join(words[:5])  # Limit to first 5 meaningful words
        return keywords if keywords else "technology innovation"
    except Exception as e:
        return "technology innovation"  # Default keywords if extraction fails

# ✅ Function to Fetch Search Results from Google (with 3-Year Filter)
def fetch_from_google(problem_description, target_audience):
    """Fetches search results from Google Custom Search API with intelligent queries and a 3-year time filter."""
    try:
        # Extract keywords safely
        problem_keywords = extract_keywords(problem_description)
        audience_keywords = extract_keywords(target_audience)

        # Construct an intelligent search query
        search_query = f"latest AI OR technology OR solutions for {problem_keywords} {audience_keywords}"

        # Get today's date and calculate the 3-year time range
        today = datetime.datetime.today()
        three_years_ago = today.year - 3
        date_filter = f"after:{three_years_ago}-01-01"

        # API request with a time filter
        url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&dateRestrict={date_filter}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"

        response = requests.get(url)
        data = response.json()

        if "items" not in data:
            return "No search results found or API limit exceeded."

        results = []
        for item in data.get("items", [])[:5]:  # Get top 5 results
            title = item.get("title", "No Title")
            link = item.get("link", "#")
            snippet = item.get("snippet", "No description available")
            results.append(f"🔗 [{title}]({link}) - {snippet}")

        return "\n\n".join(results) if results else "No relevant search results found."

    except Exception as e:
        return f"Error fetching from Google: {e}"

# ✅ Streamlit App UI
st.title("Advanced Innovation Generator")
st.write("Generate deep, tech-driven, and broad solutions using AI-powered frameworks.")

# Ensure API keys are set before running
if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
    st.error("🚨 Google API Key or Search Engine ID is missing! Add it to Streamlit secrets or your script.")
    st.stop()

# User Input Fields
problem_description = st.text_area(
    "Describe the problem:",
    placeholder="What is the problem?",
    help="Describe the problem you want to solve."
)

target_audience = st.text_area(
    "Who has the problem?",
    placeholder="Who is affected by this problem?",
    help="Describe the group or individuals who are affected by the problem."
)

# Ensure inputs are always visible by checking if the script execution is stopping prematurely
if problem_description is None or target_audience is None:
    st.error("🚨 Please enter a problem description and target audience.")
    st.stop()

# ✅ Function to Analyze the Problem
def analyze_problem(problem_description, target_audience):
    prompt = f"""
    You are an expert problem analyst. Given the following problem and audience, provide:
    1. A deeper breakdown of the root causes of the problem.
    2. A summary of similar problems in different industries.
    3. Key obstacles to solving this problem.

    Problem: {problem_description}
    Target Audience: {target_audience}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a problem analysis expert."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message['content']

# ✅ Function to Generate New Technology-Based Ideas
def generate_new_ideas(problem_description, target_audience, existing_solutions):
    prompt = f"""
    Generate five **unique, technology-based** solutions to the problem. Each idea should include:
    - A product/service name
    - A detailed description of how it works
    - The key technology behind it
    - Possible challenges and how to overcome them
    - The potential market impact

    Problem: {problem_description}
    Target Audience: {target_audience}
    Existing Solutions: {existing_solutions}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an AI innovation strategist creating deep and technical solutions."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message['content']

# ✅ Function to Refine and Evaluate the Best Idea
def refine_best_idea(ideas):
    prompt = f"""
    Based on the following five solutions, select the one with the highest innovation, feasibility, and impact.
    Provide a more refined version with additional technical details and a potential roadmap for development.

    Solutions: {ideas}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a business and tech expert refining innovation strategies."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message['content']

# ✅ Button to Generate Solutions
if st.button("Generate Solutions"):
    if problem_description and target_audience:
        try:
            with st.spinner("Analyzing problem..."):
                problem_analysis = analyze_problem(problem_description, target_audience)
            st.subheader("Problem Analysis")
            st.write(problem_analysis)

            with st.spinner("Retrieving real-world solutions..."):
                google_search_results = fetch_from_google(problem_description, target_audience)

            st.subheader("Existing Solutions & Research")
            st.write("### 🔍 Web 
