import openai
import requests
import streamlit as st

# 🔹 Add your Google Search API credentials here
GOOGLE_API_KEY = "AIzaSyDAdbb_xnGRsbI77-ZfnlhMc-6iLDTVxiE"  # 🔴 Replace with your actual Google API Key
SEARCH_ENGINE_ID = "94d30f152c43a48a7"  # 🔴 Replace with your Custom Search Engine ID

# 🔹 Function to fetch search results from Google Custom Search API
def fetch_from_google(query):
    """Fetches search results from Google Custom Search API."""
    
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        results = []
        for item in data.get("items", [])[:5]:  # Get top 5 results
            title = item.get("title", "No Title")
            link = item.get("link", "#")
            snippet = item.get("snippet", "No description available")
            results.append(f"🔗 [{title}]({link}) - {snippet}")
        
        return "\n\n".join(results) if results else "No relevant search results found."
    
    except Exception as e:
        return f"Error fetching from Google: {e}"

# Set the OpenAI API key
openai.api_key = openai_api_key

# Function to make API calls with retry handling
def make_api_call(prompt, system_message):
    retries = 3
    delay = 5
    for i in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
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
                return "⚠️ Rate limit exceeded. Please try again later."
        except Exception as e:
            return f"❌ An error occurred: {e}"

# ✅ IMPROVED: Function to perform Google Custom Search with better relevance & time filter
def google_search(problem, barrier, affected, wish, num_results=5):
    """ Performs a Google search with more intelligent queries and limits results to the last 3 years. """
    
    # Generate a smarter search query using key input elements
    query = f"{problem} AND {barrier} AND {affected} AND {wish} latest research trends"
    
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": google_api_key,
        "cx": google_cse_id,
        "num": num_results,
        "dateRestrict": "y3",  # Limits results to the last 3 years
        "sort": "date"  # Prioritizes newer results
    }

    try:
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            return []
    except Exception as e:
        return [f"❌ Google Search Error: {e}"]

# Streamlit App UI
st.title("💡 Idea Search Transformer")

st.write("🚀 AI-powered insights for business & market opportunities.")

# User Input Fields
problem = st.text_area("📌 Describe the problem:", placeholder="Enter a brief problem description.")
barrier = st.text_area("🚧 What barriers exist?", placeholder="Describe the challenges.")
affected = st.text_area("👥 Who is affected?", placeholder="List the affected parties.")
wish = st.text_area("🎯 Ideal situation?", placeholder="Describe the desired outcome.")

# Generate Analysis and Web Search
if st.button("🔍 Generate Analysis and Ideas"):
    if problem and barrier and affected and wish:
        try:
            # AI-Generated Insights
            st.subheader("📌 Problem Summary & Insights")
            problem_summary = make_api_call(
                f"Summarize this problem and provide insights:\nProblem: {problem}\nBarriers: {barrier}\nAffected: {affected}\nIdeal Outcome: {wish}",
                "You are an expert in problem analysis."
            )
            st.write(problem_summary)

            st.subheader("📊 Data-Driven Evidence")
            empirical_evidence = make_api_call(
                f"Provide data and research on the impact of this problem:\nProblem: {problem}\nBarriers: {barrier}\nAffected: {affected}",
                "You are an expert researcher who provides empirical evidence."
            )
            st.write(empirical_evidence)

            st.subheader("🌍 Market Potential Analysis")
            market_potential = make_api_call(
                f"Analyze the market potential for this problem:\nProblem: {problem}\nBarriers: {barrier}\nAffected: {affected}\nIdeal Outcome: {wish}",
                "You are an expert in business analysis and market potential estimation."
            )
            st.write(market_potential)

            st.subheader("🚧 Major Challenges to Solve")
            challenges_analysis = make_api_call(
                f"Identify key challenges in solving this problem:\nProblem: {problem}\nImmediate Effects: {barrier}\nAffected: {affected}",
                "You are an expert in business and technical challenges."
            )
            st.write(challenges_analysis)

            # ✅ IMPROVED Web Search Integration
            st.subheader("🔍 Web Search Results (Last 3 Years)")
            search_results = google_search(problem, barrier, affected, wish)

            if search_results:
                for result in search_results:
                    if isinstance(result, str):  # Error Handling
                        st.write(result)
                    else:
                        st.write(f"🔗 [{result['title']}]({result['link']})")
                        st.write(f"*{result['snippet']}*")
            else:
                st.write("⚠️ No relevant search results found.")

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
    else:
        st.warning("⚠️ Please fill in all fields before generating the analysis.")
