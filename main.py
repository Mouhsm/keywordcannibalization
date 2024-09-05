import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
from datetime import datetime
import re

# Function to fetch and parse webpage
def fetch_and_parse(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

# Function to extract keywords from content
def extract_keywords(content):
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

# Function to get page title
def get_page_title(soup):
    title_tag = soup.find('title')
    return title_tag.get_text() if title_tag else 'No Title'

# Function to get content summary
def get_content_summary(soup):
    text = soup.get_text()
    sentences = text.split('. ')
    return '. '.join(sentences[:2])  # Summary of the first 2 sentences

# Function to estimate content type (basic example)
def get_content_type(soup):
    if soup.find('meta', {'name': 'description'}):
        return 'Blog Post'  # Simple heuristic for content type
    if soup.find('h1'):
        return 'Landing Page'
    return 'Other'

# Function to estimate keyword density
def get_keyword_density(content, keyword):
    words = content.lower().split()
    keyword_count = words.count(keyword.lower())
    return keyword_count / len(words) * 100 if words else 0

# Function to analyze keyword cannibalization
def analyze_cannibalization(url):
    base_url = url.split('/')[0] + '//' + url.split('/')[2]
    soup = fetch_and_parse(url)
    internal_links = get_internal_links(soup, base_url)
    
    results = []
    for link in internal_links:
        page_soup = fetch_and_parse(link)
        page_content = page_soup.get_text()
        keywords = extract_keywords(page_content)
        
        page_title = get_page_title(page_soup)
        content_summary = get_content_summary(page_soup)
        content_type = get_content_type(page_soup)
        last_updated = datetime.now().strftime("%Y-%m-%d")  # Placeholder for actual date
        for keyword in keywords:
            density = get_keyword_density(page_content, keyword)
            results.append((keyword, link, page_title, content_summary, content_type, last_updated, density))
    
    return results

# Streamlit app
st.title('Keyword Cannibalization Tool')

url = st.text_input('Enter the URL of your website:')

if url:
    with st.spinner('Analyzing...'):
        cannibalization_data = analyze_cannibalization(url)
        # Convert data to DataFrame
        df = pd.DataFrame(cannibalization_data, columns=[
            'Keyword', 'Page URL', 'Page Title', 'Content Summary', 'Content Type', 'Last Updated', 'Keyword Density'
        ])
        st.dataframe(df)

