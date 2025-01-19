import os
import time
import requests
import json
import streamlit as st
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai
import schedule
import sqlite3

# Load environment variables from .env file
load_dotenv()
user_key = os.getenv('XCB_USER_KEY')
gemini_api_key = os.getenv('GEMINI_KEY')

# Configure the Gemini API
genai.configure(api_key=gemini_api_key)

conn = sqlite3.connect('website_data.db') 
c = conn.cursor() # Create table to store website data 
c.execute('''CREATE TABLE IF NOT EXISTS website_data (name TEXT, rank INTEGER, website_url TEXT, suggestions TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# Function to scrape the website content
def scrape_website(website):
    try:
        response = requests.get(website)
        response.raise_for_status()
        html = response.text
        return html
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

# Function to analyze the content using Gemini
def parse_with_gemini(html_content):
    prompt = (
        "suggest improvement for website or is there any issue with it."
        "{html_content} is provided to you"
        "Please follow these instructions carefully: \n\n"
        "1. **Identify Issues:** Identify any issues or areas for improvement in the HTML content. "
        "2. **Provide Suggestions:** Provide specific suggestions for improving the website. "
        "3. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
        "4. **Precise and Straight Points:** Your output should contain only the the suggestions in point with point number and not any html snippets"
    )
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt.format(html_content=html_content,parse_description="suggest improvement for website or is there any issue with it"))
    
    gemini_suggestions = response.text.strip().split('\n')
    print("\n\n\n\n",gemini_suggestions,"\n\n\n\n\n")
    return gemini_suggestions

# Function to analyze the website content using BeautifulSoup and Gemini
def analyze_website(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Example analysis: Check for broken links
    broken_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if not href.startswith('http'):
            href = f"{urlparse(url).scheme}://{urlparse(url).netloc}{href}"
        try:
            link_response = requests.head(href)
            if link_response.status_code >= 400:
                broken_links.append(href)
        except requests.RequestException:
            broken_links.append(href)
    
    # Example analysis: Check for missing meta description
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if not meta_description or not meta_description.get('content'):
        meta_description_issue = "Missing meta description"
    else:
        meta_description_issue = None
    
    # Example analysis: Check for mobile-friendliness (simplified)
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    if not viewport_meta:
        mobile_friendly_issue = "Missing viewport meta tag"
    else:
        mobile_friendly_issue = None
    
    # Generate suggestions
    suggestions = []
    if broken_links:
        suggestions.append(f"Broken links found: {', '.join(broken_links)}")
    if meta_description_issue:
        suggestions.append(meta_description_issue)
    if mobile_friendly_issue:
        suggestions.append(mobile_friendly_issue)

    # Use Gemini to analyze the content and provide additional suggestions
    gemini_suggestions = parse_with_gemini(html_content)
    suggestions.extend(gemini_suggestions)
    
    return suggestions



# Function to get website improvement suggestions
def get_website_improvement_suggestions(url):
    html_content = scrape_website(url)
    if html_content:
        suggestions = analyze_website(html_content, url)
        return suggestions
    else:
        return ["Failed to scrape the website"]

# Function to extract information from CrunchBase
def extractInfos(result):
    data = json.loads(result)
    entities = data.get('entities', [])
    extracted_info = [] 
    unique_ids = set()
    for entity in entities:
        entity_id = entity.get('uuid', '')
        if entity_id not in unique_ids:
            unique_ids.add(entity_id)
            properties = entity.get('properties', {}) 
            name = properties.get('name', '') 
            entity_id = entity.get('uuid', '') 
            rank = properties.get('rank', '') 
            website_url = properties.get('website_url', '') 
            extracted_info.append({ 'name': name, 'rank': rank, 'website_url': website_url,'uuid': entity_id }) 
    return extracted_info

# Function to fetch data from CrunchBase
def fetch_crunchbase_data():
    url = "https://api.crunchbase.com/v4/data/searches/organizations"
    payload = {
        "field_ids": ["name", "website_url", "rank"],
        "query": [
            {
                "operator_id": "includes",
                "type": "predicate",
                "field_id": "name"
            }
        ],
        "limit": 1000
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-cb-user-key": user_key
    }
    response = requests.post(url, json=payload, headers=headers)
    result = response.text
    st.session_state.dom_content = result

    extInfo = extractInfos(st.session_state.dom_content)
    info_str = '\n'.join([f"Name: {info['name']}\nID: {info['uuid']}\nRank: {info['rank']}\nWebsite URL: {info['website_url']}\n\n" for info in extInfo])
    st.text_area("Extracted Info", info_str, height=300)
    return result

# Function to run the script indefinitely
def run_script():
    while True:
        try:
            result = fetch_crunchbase_data()
            extInfo = extractInfos(result)
            for info in extInfo[56:]:
                url = info['website_url']
                suggestions = get_website_improvement_suggestions(url)
                if len(suggestions) > 0 and suggestions[0] != "Failed to scrape the website":
                    suggestions_str = f"{info['name']} : \n\n" + '\n'.join([f"{suggest}" for suggest in suggestions])
                    st.write(suggestions_str)
                    c.execute("INSERT INTO website_data (name, rank, website_url, suggestions) VALUES (?, ?, ?, ?)", (info['name'], info['rank'], info['website_url'], suggestions_str)) 
                    conn.commit()
            time.sleep(3600)  # Run every hour
        except Exception as e:
            st.write(f"Error: {e}")

# Function to provide updates every 4 hours
def provide_updates():
    st.write("Providing updates every 4 hours...")
    # Add your update logic here

# Function to share data daily
def share_data_daily():
    st.write("Sharing data daily...")
    # Add your data sharing logic here

# Schedule the updates and data sharing
schedule.every(4).hours.do(provide_updates)
schedule.every().day.at("00:00").do(share_data_daily)

# Run the script and schedule in Streamlit
if st.button("Start Script"):
    st.write("Starting the script...")
    run_script()

# Run the scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(100)
