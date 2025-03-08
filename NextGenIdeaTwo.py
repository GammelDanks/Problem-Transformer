import openai
import requests
import streamlit as st
import datetime  # Ensure datetime is imported

# 🔹 Add your Google Search API credentials here
GOOGLE_API_KEY = "AIzaSyDAdbb_xnGRsbI77-ZfnlhMc-6iLDTVxiE"  # 🔴 Replace with your actual Google API Key
SEARCH_ENGINE_ID = "94d30f152c43a48a7"  # 🔴 Replace with your Custom Search Engine ID

import datetime

# 🔹 Function to fetch high-quality, industry-specific search results with a fallback mechanism
def fetch_from_google(problem_description, target_audience):
    """Fetches search results from Google Custom Search API, prioritizing authoritative sources but allowing a fallback search."""
    
    # Get the current year
    current_year = datetime.datetime.now().year

    # List of high-quality, industry-specific sources
    trusted_sources = [
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

    # Construct the search query prioritizing authoritative sources
    trusted_query = (
        f'{problem_description} {target_audience} '
        f'("report" OR "study" OR "data analysis" OR "white paper") '
        f'({" OR ".join([f"site:{site}" for site in trusted_sources])}) '
        f'-site:pinterest.com -site:quora.com -site:reddit.com after:{current_year - 3}'
    )
    
    url_trusted = f"https://www.googleapis.com/customsearch/v1?q={trusted_query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"

    try:
        # First attempt: Search within trusted sources
        response = requests.get(url_trusted)
        data = response.json()
        
        results = []
        for item in data.get("items", [])[:8]:  # Get top 8 results
            title = item.get("title", "No Title")
            link = item.get("link", "#")
            snippet = item.get("snippet", "No description available")

            # Check for publication date and filter old articles if available
            article_year = None
            if "pagemap" in item and "metatags" in item["pagemap"]:
                meta_tags = item["pagemap"]["metatags"][0]
                if "article:published_time" in meta_tags:
                    article_year = int(meta_tags["article:published_time"][:4])

            if article_year and article_year < current_year - 3:
                continue  # Skip articles older than 3 years
            
            results.append(f"🔗 [{title}]({link}) - {snippet}")

        # If results are found from trusted sources, return them
        if results:
            return "\n\n".join(results)

        # If no relevant results, perform a broader search
        fallback_query = (
            f'{problem_description} {target_audience} '
            f'("report" OR "study" OR "data analysis" OR "white paper") '
            f'-site:pinterest.com -site:quora.com -site:reddit.com after:{current_year - 3}'
        )
        url_fallback = f"https://www.googleapis.com/customsearch/v1?q={fallback_query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"

        response = requests.get(url_fallback)
        data = response.json()
        
        results = []
        for item in data.get("items", [])[:8]:  # Get top 8 results
            title = item.get("title", "No Title")
            link = item.get("link", "#")
            snippet = item.get("snippet", "No description available")

            # Check for publication date and filter old articles if available
            article_year = None
            if "pagemap" in item and "metatags" in item["pagemap"]:
                meta_tags = item["pagemap"]["metatags"][0]
                if "article:published_time" in meta_tags:
                    article_year = int(meta_tags["article:published_time"][:4])

            if article_year and article_year < current_year - 3:
                continue  # Skip articles older than 3 years
            
            results.append(f"🔗 [{title}]({link}) - {snippet}")

        return "\n\n".join(results) if results else "No relevant search results found. Try adjusting your input."

    except Exception as e:
        return f"Error fetching from Google: {e}"

# 🔹 Streamlit App UI
st.title("Advanced Innovation Generator")
st.write("Generate deep, tech-driven, and broad solutions using AI-powered frameworks.")

# Set the OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 🔹 Step 1: Analyze the problem
def analyze_problem(problem_description, target_audience):
    prompt = f"""
    You are an expert problem analyst. Given the following problem and audience, provide:
    1. A deeper breakdown of the root causes of the problem.
    2. Key obstacles to solving this problem. This analyis should be related to the root causes and the internet sources that you found via Google search before.
    
    Problem: {problem_description}
    Target Audience: {target_audience}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a problem analysis expert."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message['content']

# 🔹 Step 2: Generate new technology-based ideas
def generate_new_ideas(problem_description, target_audience, existing_solutions):
    prompt = f"""
    Generate five **unique, technology-based** solutions to the problem. The ideas should be both original and feasible and make use of the newest technologies. Do not focus on AI-related solutions only. Do not only focus on digital platforms, or apps. Each idea should include:
    - A product/service name
    - A detailed description of how it works
    - The key technology behind it
    - Possible challenges of the solution (technology, capital intensity, regulation and laws, the market accpetance, compettion) and how to overcome them
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

# 🔹 Step 3: Evaluate and refine the best idea
def refine_best_idea(ideas):
    prompt = f"""
    Based on the following five solutions, select the one with the highest innovation, feasibility, and impact.Explain in one or two sentences why this is the most promising idea. Focus on feasibility which includes (1) the high newness and uniqueness (2) the acceptable technical complexity and risk and development costs,
 (3) the high effectiveness to solve the problem. Provide a more refined version with some additional technical details.
    
    Solutions: {ideas}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a business and tech expert refining innovation strategies."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message['content']

# 🔹 Streamlit UI Inputs
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

# 🔹 Button to generate solutions
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
            st.write("### 🔍 Web Search Results (Google API)")
            st.write(google_search_results)

            with st.spinner("Generating new innovative ideas..."):
                new_ideas = generate_new_ideas(problem_description, target_audience, google_search_results)
            st.subheader("Innovative Solutions")
            st.write(new_ideas)

            with st.spinner("Refining best idea..."):
                best_idea = refine_best_idea(new_ideas)
            st.subheader("Refined Best Idea")
            st.write(best_idea)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter both the problem description and target audience to generate solutions.")
