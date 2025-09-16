# comp_new.py
# ------------------------------------------------------------
# Simplified Competitor Analysis Tool
# - UI unverändert
# - OpenAI bleibt Hauptquelle
# - Zusätzliche Websuche via You.com (u.com) API
# - Robustes Secret-Handling (kein Crash bei fehlenden Keys)
# ------------------------------------------------------------

import os
import requests
import streamlit as st
import openai

# -------------------- Secret-Helper -------------------------

def _get_openai_key():
    """
    Holt den OpenAI-Key aus ENV (OPENAI_API_KEY) oder Streamlit-Secrets [openai].openai_api_key.
    Bricht mit klarer Fehlermeldung ab, wenn nicht vorhanden.
    """
    key = os.getenv("OPENAI_API_KEY") or st.secrets.get("openai", {}).get("openai_api_key")
    if not key:
        st.error("Missing OpenAI API key. Setze OPENAI_API_KEY (Env) oder [openai].openai_api_key in den Secrets.")
        st.stop()
    return key

def _get_youcom_key():
    """
    Holt den You.com-Key aus ENV (YOUCOM_API_KEY) oder Streamlit-Secrets [youcom].api_key.
    Fehlt der Key, wird die You.com-Suche übersprungen (App läuft ohne Crash weiter).
    """
    return os.getenv("YOUCOM_API_KEY") or st.secrets.get("youcom", {}).get("api_key")

# OpenAI initialisieren
openai.api_key = _get_openai_key()

# -------------------- You.com Websuche ----------------------

def you_search_competitors(solution_description: str,
                           count: int = 8,
                           freshness: str = "year",
                           country: str = "DE") -> list[dict]:
    """
    Ruft You.com (u.com) Web Search API auf, um potenzielle Wettbewerberseiten zu finden.
    Gibt Liste von Dicts zurück: {title, url, description}
    """
    api_key = _get_youcom_key()
    if not api_key:
        # Kein Crash: freundlich informieren und mit OpenAI-only weitermachen
        st.info("You.com API key not found. Continuing without web search (OpenAI-only).")
        return []

    endpoint = "https://api.ydc-index.io/v1/search"

    # Query zielt auf Wettbewerber-/Alternativen-Listen + vermeidet Jobseiten
    query = (
        f'("{solution_description}") '
        f'(competitors OR alternatives OR "similar tools" OR "top companies") '
        f'-(job OR careers OR hiring)'
    )

    params = {
        "query": query,
        "count": count,          # Anzahl Treffer
        "freshness": freshness,  # day|week|month|year
        "country": country,      # z.B. DE, US
        "safesearch": "moderate"
    }
    headers = {"X-API-Key": api_key}

    try:
        r = requests.get(endpoint, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        web_results = data.get("results", {}).get("web", []) or []

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
        # Robust bleiben: nicht crashen, sondern Info ausgeben
        st.info(f"You.com search unavailable ({e}). Continuing with AI results only.")
        return []

# -------------------- OpenAI-Funktionen ---------------------

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

    # You.com Ergebnisse als Addendum anhängen (gleiches Text-Panel)
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

# -------------------- Streamlit App (UI unverändert) --------

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
