import streamlit as st
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from collections import Counter
import nltk
import pandas as pd
import base64

# Download NLTK resources if not already downloaded
nltk.download('punkt')
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

    # Inject custom CSS to style and center the buttons
    st.markdown("""
        <style>
        .download-button {
            display: inline-block;
            background-color: #FFA500; /* Orange color */
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            text-align: center;
            text-decoration: none;
        }
        .download-button:hover {
            background-color: #FF8C00; /* Darker orange color on hover */
        }
        .check-button {
            background-color: #007BFF; /* Blue color */
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        .check-button:hover {
            background-color: #0056b3; /* Darker blue color on hover */
        }
        .center {
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # User input for URLs
    url1 = st.text_input("Enter the first URL:")
    url2 = st.text_input("Enter the second URL:")

    # Render the "Check Cannibalization" button with custom styling
    if st.markdown('<button class="check-button" id="check-button">Check Cannibalization</button>', unsafe_allow_html=True):
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
                    
                    # Convert DataFrame to CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    b64 = base64.b64encode(csv).decode('utf-8')
                    href = f'<a href="data:file/csv;base64,{b64}" download="results.csv" class="download-button">Download Results</a>'
                    
                    # Center the button and display it
                    st.markdown(f'<div class="center">{href}</div>', unsafe_allow_html=True)
                    
                    # Display the DataFrame
                    st.dataframe(df)
                else:
                    st.write("No common keywords found.")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter both URLs.")

if __name__ == "__main__":
    main()
