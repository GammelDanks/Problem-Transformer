import requests
import datetime
import re

GOOGLE_API_KEY = "AIzaSyDAdbb_xnGRsbI77-ZfnlhMc-6iLDTVxiE"  # 🔴 Replace with your Google API Key
SEARCH_ENGINE_ID = "94d30f152c43a48a7"  # 🔴 Replace with your Custom Search Engine ID

def extract_keywords(text):
    """Extracts important keywords from user input using simple regex-based filtering."""
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text)  # Get words of at least 4 letters
    keywords = " ".join(words[:5])  # Limit to first 5 meaningful words
    return keywords

def fetch_from_google(problem_description, target_audience):
    """Fetches search results from Google Custom Search API with intelligent queries and a 3-year time filter."""
    
    # Extract important keywords from both user inputs
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
