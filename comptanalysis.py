import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import spacy
import spacy
from spacy.cli import download

# Ensure the spacy model is downloaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
import openai

# Load the spaCy model for English
nlp = spacy.load("en_core_web_sm")

# Access the API keys from Streamlit secrets with correct keys
openai_api_key = st.secrets["openai"]["openai_api_key"]
serpapi_key = st.secrets["serpapi"]["api_key"]

# Set the OpenAI API key
openai.api_key = openai_api_key

# Function to identify competitors and find relevant links using OpenAI
def find_competitors_with_openai(solution_description):
    try:
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
                {"role": "system", "content": "You are a market analyst providing a list of competitors and relevant articles for a given solution."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            n=1,
            stop=None,
            temperature=0.7,
        )
        
        openai_competitors = response.choices[0].message['content'].strip()
        return openai_competitors

    except openai.error.OpenAIError as e:
        st.error(f"An error occurred while retrieving competitors with OpenAI: {str(e)}")
        return "No competitors found."

# Function to find a competitor's website using a direct API request to SerpAPI
def find_website_url(competitor_name):
    try:
        params = {
            "q": f"{competitor_name} official website",
            "api_key": serpapi_key,
            "engine": "google",
        }
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        results = response.json()
        if 'organic_results' in results and len(results['organic_results']) > 0:
            return results['organic_results'][0]['link']
        else:
            return None
    except Exception as e:
        st.error(f"An error occurred while searching for {competitor_name}: {str(e)}")
        return None

# Updated function to scrape a competitor's website for features and benefits with headers
def scrape_competitor_website(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        list_items = soup.find_all('li')
        text_content = " ".join([p.get_text() for p in paragraphs + list_items])
        return text_content
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while scraping {url}: {str(e)}")
        return ""

# Function to extract key features and benefits using NLP
def extract_features_from_text(text):
    doc = nlp(text.lower())
    features = []
    for sentence in doc.sents:
        if "feature" in sentence.text or "benefit" in sentence.text or "functionality" in sentence.text:
            features.append(sentence.text.strip())
    return features

# Function to aggregate features across competitors
def aggregate_features(all_features):
    feature_counter = Counter([feature for features in all_features for feature in features])
    top_features = [feature for feature, count in feature_counter.most_common(6)]
    return top_features

# Function to create a comparison table
def create_comparison_table(competitors, top_features, competitor_features):
    comparison_data = {"Feature": top_features}
    for competitor in competitors:
        comparison_data[competitor] = [feature in competitor_features.get(competitor, []) for feature in top_features]
    df = pd.DataFrame(comparison_data)
    df = df.replace({True: '✅', False: '❌'})
    return df

# Streamlit App UI for Competitor Analysis
st.title("Competitor Analysis Tool")

st.write("This tool helps you analyze the competitive landscape for the solutions generated and provides strategic recommendations.")

# Input: Solutions
solutions = st.text_area(
    "Enter the solutions generated:",
    placeholder="Describe the solution you are working on. Example: A mobile app that helps users track their fitness goals."
)

if st.button("Analyze Competitors"):
    if solutions:
        for solution in solutions.split('\n'):
            solution = solution.strip()
            if solution:
                st.subheader(f"Competitor Analysis for: {solution}")
                
                # Step 1: Find competitors and relevant links using OpenAI
                competitors_list = find_competitors_with_openai(solution)
                st.write(competitors_list)
                
                # Parse competitor names from OpenAI output for comparison table
                competitors = [line.split(":")[0].strip() for line in competitors_list.split("\n") if line]

                # Step 2: Scrape websites for features/benefits
                competitor_features = {}
                for competitor in competitors:
                    competitor_url = find_website_url(competitor)
                    if competitor_url:
                        text_content = scrape_competitor_website(competitor_url)
                        features = extract_features_from_text(text_content)
                        competitor_features[competitor] = features

                # Step 3: Aggregate features across competitors
                top_features = aggregate_features(competitor_features.values())

                # Step 4: Create and display comparison table
                st.subheader("Competitor Comparison Table")
                comparison_table = create_comparison_table(competitors, top_features, competitor_features)
                st.write(comparison_table)

                # Step 5: Identify and display gaps in competitor offerings
                st.subheader("Identified Gaps in Competitor Offerings")
                for feature in top_features:
                    competitors_with_feature = [
                        comp for comp, feats in competitor_features.items() if feature in feats
                    ]
                    if len(competitors_with_feature) < len(competitor_features):
                        missing_competitors = set(competitor_features.keys()) - set(competitors_with_feature)
                        st.write(f"Feature '{feature}' is missing in: {', '.join(missing_competitors)}")
                
    else:
        st.warning("Please enter the solutions to analyze competitors.")
