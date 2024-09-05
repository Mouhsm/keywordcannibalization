import streamlit as st
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import nltk

# Download NLTK stopwords if not already downloaded
nltk.download('punkt')
nltk.download('stopwords')

def fetch_content(url):
    """Fetch the content of a web page and return the text."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

def extract_keywords(text, num_keywords=10):
    """Extract keywords from text, ignoring common stop words."""
    # Tokenize and remove stop words
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Calculate word frequencies
    word_freq = Counter(filtered_words)
    
    # Get the most common keywords
    return word_freq.most_common(num_keywords)

def analyze_cannibalization(keywords1, keywords2):
    """Check for keyword cannibalization between two sets of keywords."""
    keywords1_set = set(keyword for keyword, _ in keywords1)
    keywords2_set = set(keyword for keyword, _ in keywords2)
    
    common_keywords = keywords1_set.intersection(keywords2_set)
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
                result_text = "Common Keywords:\n" + "\n".join(common_keywords)
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
