import streamlit as st
import openai
import requests
from urllib.parse import urlencode

# Set the OpenAI API key
openai.api_key = st.secrets["openai"]["openai_api_key"]

# -------- NEW: lightweight You.com Search helper --------
def you_search_competitors(solution_description: str,
                           count: int = 8,
                           freshness: str = "year",
                           country: str = "DE") -> list[dict]:
    """
    Calls You.com (u.com) Web Search API to find potential competitor pages.
    Returns a list of dicts with keys: title, url, description.
    """
    api_key = st.secrets["youcom"]["api_key"]
    endpoint = "https://api.ydc-index.io/v1/search"
    # Query engineered to surface company/alternative lists & directories
    query = (
        f'("{solution_description}") '
        f'(competitors OR alternatives OR "similar tools" OR "top companies") '
        f'-(job OR careers OR hiring)'
    )

    params = {
        "query": query,
        "count": count,
        "freshness": freshness,   # day|week|month|year
        "country": country,       # e.g. DE for Germany
        "safesearch": "moderate"
    }

    headers = {"X-API-Key": api_key}

    try:
        r = requests.get(endpoint, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        web_results = data.get("results", {}).get("web", []) or []

        # Normalize minimal subset
        cleaned = []
        seen_urls = set()
        for hit in web_results:
            url = hit.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            cleaned.append({
                "title": hit.get("title") or url,
                "url": url,
                "description": hit.get("description") or ""
            })
        return cleaned

    except Exception as e:
        # Keep app robust: fail silently but inform in logs/UX.
        st.info(f"Note: You.com search unavailable ({e}). Continuing with AI results only.")
        return []

# Function to retrieve competitors using OpenAI (+ appended You.com findings)
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
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a market analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        temperature=0.7,
    )
    ai_block = response.choices[0].message['content'].strip()

    # --- NEW: append a compact addendum from You.com search (same section) ---
    web_hits = you_search_competitors(solution_description)
    if web_hits:
        addendum_lines = ["", "**Additional competitors found via web search (You.com):**"]
        for h in web_hits:
            title = h["title"]
            url = h["url"]
            desc = f" — {h['description']}" if h["description"] else ""
            addendum_lines.append(f"- [{title}]({url}){desc}")
        ai_block += "\n" + "\n".join(addendum_lines)

    return ai_block

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
