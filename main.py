import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords

# Download necessary NLTK data
nltk.download('stopwords')

# Function to fetch and parse content from a URL
def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from all paragraphs
        text = ' '.join(p.get_text() for p in soup.find_all('p'))
        return text
    except requests.RequestException as e:
        st.error(f"Error fetching URL: {e}")
        return ""

# Function to clean and preprocess text
def preprocess_text(text):
    # Convert to lowercase and remove non-alphabetic characters
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return text

# Function to extract keywords using TF-IDF
def extract_keywords(text):
    stop_words = set(stopwords.words('english'))
    text = preprocess_text(text)
    
    # Use TF-IDF to find important words
    vectorizer = TfidfVectorizer(stop_words=stop_words, ngram_range=(1, 3))
    X = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = X.toarray()[0]
    
    # Combine feature names with their scores
    keywords = sorted(zip(feature_names, scores), key=lambda x: -x[1])
    
    # Return top 20 keywords
    return [keyword for keyword, score in keywords[:20]]

# Function to check for keyword cannibalization
def check_cannibalization(url1, url2):
    content1 = fetch_content(url1)
    content2 = fetch_content(url2)
    
    if not content1 or not content2:
        st.error("Failed to fetch content from one or both URLs.")
        return set()
    
    keywords1 = set(extract_keywords(content1))
    keywords2 = set(extract_keywords(content2))
    cannibalized_keywords = keywords1.intersection(keywords2)
    
    return cannibalized_keywords

# Streamlit application
st.title('Keyword Cannibalization Checker')

# Input fields for URLs
url1 = st.text_input('Enter the first URL:')
url2 = st.text_input('Enter the second URL:')

if st.button('Check Cannibalization'):
    if url1 and url2:
        cannibalized_keywords = check_cannibalization(url1, url2)
        if cannibalized_keywords:
            result = f"Keywords from the first URL that exist in the second URL:\n{', '.join(cannibalized_keywords)}"
        else:
            result = "No keyword cannibalization detected or unable to fetch content."
        st.text_area('Results', value=result, height=200)
        st.download_button('Copy to Clipboard', result)
    else:
        st.error('Please enter both URLs.')

