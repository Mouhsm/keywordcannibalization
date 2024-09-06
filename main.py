import streamlit as st
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from collections import Counter
import nltk
import pandas as pd

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
    
    common_keywords = []
    for keyword in keywords1_dict:
        if keyword in keywords2_dict:
            common_keywords.append({
                "Keyword": keyword,
                "Count in URL 1": keywords1_dict[keyword],
                "Count in URL 2": keywords2_dict[keyword]
            })
    
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
                
                # Extract keywords
                keywords1 = extract_keywords(content1)
                keywords2 = extract_keywords(content2)
                
                # Analyze cannibalization
                common_keywords = analyze_cannibalization(keywords1, keywords2)
                
                # Display results
                if common_keywords:
                    df = pd.DataFrame(common_keywords)
                    st.dataframe(df)
                    
                    # Button to copy results to clipboard
                    st.download_button(
                        label="Download Results",
                        data=df.to_csv(index=False),
                        file_name="results.csv",
                        mime="text/csv"
                    )
                else:
                    st.write("No common keywords found.")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter both URLs.")

if __name__ == "__main__":
    main()
