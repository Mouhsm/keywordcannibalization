import streamlit as st
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re

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

# Function to extract main keywords based on density
def extract_keywords(text):
    # Convert text to lower case and remove non-alphabetic characters
    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = Counter(words)
    # Return the most common words
    return [word for word, count in word_counts.most_common(20)]

# Function to check for keyword cannibalization
def check_cannibalization(url1, url2):
    content1 = fetch_content(url1)
    content2 = fetch_content(url2)
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
            result = "No keyword cannibalization detected."
        st.text_area('Results', value=result, height=200)
        st.download_button('Copy to Clipboard', result)
    else:
        st.error('Please enter both URLs.')

