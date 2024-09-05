import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
import re
from statistics import mean
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import download

# Ensure nltk resources are downloaded
download('punkt')
download('stopwords')

# Function to fetch and parse webpage
def fetch_and_parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# Function to extract keywords from content
def extract_keywords(content):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(content.lower())
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    return [phrase.strip() for phrase in filtered_tokens]

# Function to get internal links from a page
def get_internal_links(soup, base_url):
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/'):
            href = base_url + href
        if href.startswith(base_url) and not href in links:
            links.add(href)
    return list(links)

# Function to analyze keyword cannibalization
def analyze_cannibalization(url):
    base_url = url.split('/')[0] + '//' + url.split('/')[2]
    soup = fetch_and_parse(url)
    internal_links = get_internal_links(soup, base_url)
    keywords_dict = defaultdict(lambda: {'count': 0, 'pages': defaultdict(lambda: {'count': 0, 'total_words': 0})})

    for link in internal_links:
        page_soup = fetch_and_parse(link)
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
    for keyword, data in filtered_keywords.items():
        densities = [
            (page_data['count'] / page_data['total_words']) * 100
            for page_data in data['pages'].values()
        ]
        data['density'] = mean(densities) if densities else 0
    sorted_keywords = sorted(filtered_keywords.items(), key=lambda x: x[1]['count'], reverse=True)

    return sorted_keywords

# Streamlit app
st.title('Keyword Cannibalization Tool')

url = st.text_input('Enter the URL of your website:')

if url:
    with st.spinner('Analyzing...'):
        cannibalization_data = analyze_cannibalization(url)
        # Convert data to DataFrame
        data = [(keyword, data['count'], ', '.join(data['pages'].keys()), f"{data['density']:.2f}%") for keyword, data in cannibalization_data]
        if data:
            df = pd.DataFrame(data, columns=['Keyword', 'Frequency', 'Pages', 'Keyword Density'])
            st.dataframe(df)
        else:
            st.write("No cannibalization issues found.")
