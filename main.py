import streamlit as st
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from collections import Counter
import nltk

# Download NLTK resources if not already downloaded
nltk.download('punkt_tab')
nltk.download('stopwords')

def fetch_content(url):
    """Fetch the content of a web page and return the text."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

def extract_keywords(text, num_keywords=10, n=3):
    """Extract n-grams as keywords from text, ignoring common stop words."""
    # Tokenize and remove stop words
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Extract n-grams
    n_grams = ngrams(filtered_words, n)
    n_gram_freq = Counter([' '.join(gram) for gram in n_grams])
    
    # Get the most common n-grams
    return n_gram_freq.most_common(num_keywords)

def analyze_cannibalization(keywords1, keywords2):
    """Check for keyword cannibalization between two sets of keywords, including frequencies."""
    keywords1_dict = dict(keywords1)
    keywords2_dict = dict(keywords2)
    
    common_keywords = {}
    for keyword in keywords1_dict:
        if keyword in keywords2_dict:
            common_keywords[keyword] = (keywords1_dict[keyword], keywords2_dict[keyword])
    
    return common_keywords

def main():
    st.title("Keyword Cannibalization Analyzer")

    # User input for URLs
    url1 = st.text_input("Enter the first URL:")
    url2 = st.text_input("Enter the second URL:")

    if st.button("Check Cannibalization"):
        if url1 and url2:
            try:
                # Fetch and process content from both URLs
                content1 = fetch_content(url1)
                content2 = fetch_content(url2)
                
                st.write("Content from URL 1 (first 500 chars):", content1[:500])
                st.write("Content from URL 2 (first 500 chars):", content2[:500])
                
                # Extract keywords
                keywords1 = extract_keywords(content1)
                keywords2 = extract_keywords(content2)
                
                st.write("Keywords from URL 1:", keywords1)
                st.write("Keywords from URL 2:", keywords2)
                
                # Analyze cannibalization
                common_keywords = analyze_cannibalization(keywords1, keywords2)
                
                # Display results
                if common_keywords:
                    result_text = "Common Keywords:\n"
                    for keyword, (count1, count2) in common_keywords.items():
                        result_text += f"{keyword}: Found {count1} times in URL 1, {count2} times in URL 2\n"
                else:
                    result_text = "No common keywords found."
                
                st.text_area("Results", result_text, height=300)
                
                # Button to copy results
                st.download_button(
                    label="Copy Results to Clipboard",
                    data=result_text,
                    file_name="results.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter both URLs.")

if __name__ == "__main__":
    main()
