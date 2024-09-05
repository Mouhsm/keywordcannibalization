import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from statistics import mean
import io

# Function to fetch and parse webpage
def fetch_and_parse(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException as e:
        st.error(f"Error fetching {url}: {e}")
        return None

# Function to extract keywords using TF-IDF
def extract_keywords(content, num_keywords=10):
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))  # Unigrams and bigrams
    X = vectorizer.fit_transform([content])
    scores = X.sum(axis=0).A1
    features = vectorizer.get_feature_names_out()
    keywords = sorted(zip(features, scores), key=lambda x: x[1], reverse=True)
    return [keyword for keyword, score in keywords[:num_keywords]]

# Function to get internal links from a page
def get_internal_links(soup, base_url):
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/'):
            href = base_url + href
        if href.startswith(base_url):
            links.append(href.split('#')[0])  # Remove fragments
    return list(set(links))  # Remove duplicates

# Function to analyze keyword cannibalization between two URLs
def analyze_cannibalization(url1, url2):
    base_url1 = url1.split('/')[0] + '//' + url1.split('/')[2]
    base_url2 = url2.split('/')[0] + '//' + url2.split('/')[2]
    
    results = []
    
    for url in [url1, url2]:
        soup = fetch_and_parse(url)
        if not soup:
            continue
        internal_links = get_internal_links(soup, base_url1 if url == url1 else base_url2)
        keywords_dict = defaultdict(lambda: {'count': 0, 'pages': defaultdict(lambda: {'count': 0, 'total_words': 0})})
        
        for link in internal_links:
            page_soup = fetch_and_parse(link)
            if not page_soup:
                continue
            page_content = page_soup.get_text()
            words = re.findall(r'\b\w+\b', page_content.lower())
            total_words = len(words)
            page_keywords = extract_keywords(page_content)
            
            for keyword in page_keywords:
                if keyword in keywords_dict:
                    keywords_dict[keyword]['count'] += 1
                    keywords_dict[keyword]['pages'][link]['count'] += page_keywords.count(keyword)
                    keywords_dict[keyword]['pages'][link]['total_words'] = total_words
                else:
                    keywords_dict[keyword]['count'] = 1
                    keywords_dict[keyword]['pages'][link] = {'count': page_keywords.count(keyword), 'total_words': total_words}
        
        # Filter out keywords that appear on only one page
        filtered_keywords = {
            keyword: data for keyword, data in keywords_dict.items()
            if len(data['pages']) > 1
        }
        
        # Calculate keyword density and sort keywords by frequency
        for keyword, data in filtered
        # Calculate keyword density and sort keywords by frequency
        for keyword, data in filtered_keywords.items():
            densities = [
                (page_data['count'] / page_data['total_words']) * 100
                for page_data in data['pages'].values()
            ]
            data['density'] = mean(densities) if densities else 0
        sorted_keywords = sorted(filtered_keywords.items(), key=lambda x: x[1]['count'], reverse=True)
        
        # Append results to the list
        for keyword, data in sorted_keywords:
            results.append({
                'Keyword': keyword,
                'Frequency': data['count'],
                'Pages': ', '.join(data['pages'].keys()),
                'Keyword Density': f"{data['density']:.2f}%",
                'URL': url
            })
    
    return results

# Streamlit app
st.title('Keyword Cannibalization Tool')

# Input fields for two URLs
url1 = st.text_input('Enter the first URL here:')
url2 = st.text_input('Enter the second URL here:')

# Button to check cannibalization
if st.button('Check Cannibalization'):
    if url1 and url2:
        with st.spinner('Analyzing...'):
            cannibalization_data = analyze_cannibalization(url1, url2)
            
            # Convert data to DataFrame
            if cannibalization_data:
                df = pd.DataFrame(cannibalization_data)
                st.dataframe(df)
                
                # Button to download results as CSV file
                def to_csv(df):
                    csv = df.to_csv(index=False)
                    return csv

                st.download_button(
                    label="Download results as CSV",
                    data=to_csv(df),
                    file_name='cannibalization_results.csv',
                    mime='text/csv'
                )
            else:
                st.write("No cannibalization issues found.")
    else:
        st.error("Please enter both URLs.")
