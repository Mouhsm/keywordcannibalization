import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict

# Function to fetch and parse webpage
def fetch_and_parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# Function to extract keywords from content
def extract_keywords(content):
    # Simple keyword extraction by splitting words (can be enhanced)
    words = content.lower().split()
    keywords = [word.strip('.,!?()[]{}"\'') for word in words if len(word) > 3]
    return keywords

# Function to get internal links from a page
def get_internal_links(soup, base_url):
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/'):
            href = base_url + href
        if href.startswith(base_url):
            links.append(href)
    return links

# Function to analyze keyword cannibalization
def analyze_cannibalization(url):
    base_url = url.split('/')[0] + '//' + url.split('/')[2]
    soup = fetch_and_parse(url)
    internal_links = get_internal_links(soup, base_url)
    keywords_dict = defaultdict(list)
    
    for link in internal_links:
        page_soup = fetch_and_parse(link)
        page_content = page_soup.get_text()
        keywords = extract_keywords(page_content)
        
        for keyword in keywords:
            keywords_dict[keyword].append(link)
    
    return keywords_dict

# Streamlit app
st.title('Keyword Cannibalization Tool')

url = st.text_input('Enter the URL of your website:')

if url:
    with st.spinner('Analyzing...'):
        cannibalization_data = analyze_cannibalization(url)
        # Convert data to DataFrame
        data = [(keyword, ', '.join(links)) for keyword, links in cannibalization_data.items()]
        df = pd.DataFrame(data, columns=['Keyword', 'Pages'])
        st.dataframe(df)
