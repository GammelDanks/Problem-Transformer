import openai
import requests
import streamlit as st
import datetime

# 🔹 Add your Google Search API credentials here
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"  # 🔴 Replace with your actual Google API Key
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID"  # 🔴 Replace with your Custom Search Engine ID

# 🔹 Trusted sources for targeted searches
TRUSTED_SOURCES = [
    "reuters.com", "spglobal.com", "industryweek.com", "manufacturing.net",
    "cleantechnica.com", "iea.org", "materialstoday.com", "azom.com",
    "medtechdive.com", "healthcareitnews.com", "automotivenews.com",
    "motortrend.com", "caranddriver.com", "autoweek.com", "topgear.com",
    "themanufacturer.com", "plantengineering.com", "modernmachineshop.com",
    "greentechmedia.com", "canarymedia.com", "energystoragejournal.com",
    "materialsworld.com", "advancedmaterials.com", "jmateralscience.com",
    "massdevice.com", "fiercebiotech.com", "medicaldesignandoutsourcing.com",
    "techcrunch.com", "wired.com", "theverge.com", "cnet.com", "gizmodo.com",
    "biopharmadive.com", "constructiondive.com", "utilitydive.com",
    "transportdive.com", "retaildive.com", "treehugger.com", "ecowatch.com",
    "greenbiz.com", "insideclimatenews.org", "climatecentral.org",
    "bloomberg.com", "forbes.com", "fortune.com", "wsj.com",
    "frost.com", "gartner.com", "mckinsey.com", "deloitte.com",
    "strategyand.pwc.com", "iea.org", "who.int"
]

# 🔹 Function to fetch search results from Google Custom Search API
def fetch_from_google(query, num_results=10, trusted_only=True):
    """Fetches search results from Google Custom Search API. If trusted_only=True, prioritizes authoritative sources."""
    
    current_year = datetime.datetime.now().year
    trusted_query = (
        f'{query} ("report" OR "study" OR "data analysis" OR "white paper") '
        f'({" OR ".join([f"site:{site}" for site in TRUSTED_SOURCES])}) '
        f'-site:pinterest.com -site:quora.com -site:reddit.com after:{current_year - 3}'
    )

    url = f"https://www.googleapis.com/customsearch/v1?q={trusted_query if trusted_only else query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&num={num_results}"

    try:
        response = requests.get(url)
        data = response.json()
        
        results = []
        for item in data.get("items", []):  # Get up to 'num_results' results
            title = item.get("title", "No Title")
            link = item.get("link", "#")
            snippet = item.get("snippet", "No description available")
            results.append(f"🔗 [{title}]({link}) - {snippet}")
        
        return results if results else []

    except Exception as e:
        return [f"Error fetching from Google: {e}"]

# 🔹 Function to perform internet search for deeper root causes
def search_root_causes(problem_description, target_audience):
    """Searches the internet for deeper root causes of the problem, prioritizing authoritative sources first."""
    query = f"root causes of {problem_description} in {target_audience}"
    
    # Try trusted sources first
    results = fetch_from_google(query, num_results=5, trusted_only=True)
    
    # If no relevant results, fall back to a broader search
    if not results:
        results = fetch_from_google(query, num_results=5, trusted_only=False)

    return results

# 🔹 Streamlit App UI
st.title("Advanced Innovation Generator")
st.write("Generate deep, tech-driven, and broad solutions using AI-powered frameworks.")

# Set the OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 🔹 Step 1: Analyze the problem
def analyze_problem(problem_description, target_audience):
    # Fetch root cause information from the internet
    root_cause_info = search_root_causes(problem_description, target_audience)
    
    root_cause_text = "\n\n".join(root_cause_info) if root_cause_info else "No relevant sources found."
    
    # Combine problem description, target audience, and fetched information
    prompt = f"""
    You are an expert problem analyst. Given the following problem and audience, provide:
    1. A deeper breakdown of the root causes of the problem.
    2. A summary of similar problems in different industries.
    3. Key obstacles to solving this problem.
    4. Relevant references from recent studies and data.
    
    Problem: {problem_description}
    Target Audience: {target_audience}
    Additional Information: {root_cause_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a problem analysis expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message['content']

# 🔹 Streamlit UI Inputs
problem_description = st.text_area("Describe the problem:", placeholder="What is the problem?")
target_audience = st.text_area("Who has the problem?", placeholder="Who is affected?")

# 🔹 Button to generate solutions
if st.button("Generate Solutions"):
    if problem_description and target_audience:
        try:
            with st.spinner("Analyzing problem..."):
                problem_analysis = analyze_problem(problem_description, target_audience)
            st.subheader("Problem Analysis")
            st.write(problem_analysis)

            with st.spinner("Retrieving real-world solutions..."):
                google_search_results = fetch_from_google(problem_description, num_results=10, trusted_only=True)

            if not google_search_results:  # Fallback if no trusted sources found
                google_search_results = fetch_from_google(problem_description, num_results=10, trusted_only=False)

            st.subheader("Existing Solutions & Research")
            st.write("### 🔍 Web Search Results (Google API)")
            st.write("\n\n".join(google_search_results) if google_search_results else "No relevant search results found.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter both the problem description and target audience to generate solutions.")
