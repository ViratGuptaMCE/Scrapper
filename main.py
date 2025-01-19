import streamlit as st
from scrap import scrape_website, split_dom_content , clean_body_cont,extract_body_content , get_website_improvement_suggestions
from parse import parse_with_ollama
import requests
import json
import time

import os 
from dotenv import load_dotenv

load_dotenv()
user_key = os.getenv('XCB_USER_KEY')

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
    "limit": 5
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-cb-user-key": user_key
}

response = requests.post(url, json=payload, headers=headers)



def extract_fields(json_content, fields):
    data = json.loads(json_content)
    extracted_data = {field: [] for field in fields}

    for item in data:
        for field in fields:
            extracted_data[field].append(item.get(field))
    return extracted_data


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

extInfo = []
if st.button("Scrape Site"):
    st.write("Scraping the website")
    result = response.text
    st.session_state.dom_content = result

    extInfo = extractInfos(st.session_state.dom_content)
    info_str = '\n'.join([f"Name: {info['name']}\nID: {info['uuid']}\nRank: {info['rank']}\nWebsite URL: {info['website_url']}\n\n" for info in extInfo])
    # while True:
    st.text_area("Extracted Info", info_str, height=300) 
    # time.sleep(50)


for info in extInfo:
    url = info['website_url']
    suggestions = get_website_improvement_suggestions(url)
    if len(suggestions)>0:
        suggestions = f"{info['name']} : \n\n"+'\n'.join([f"{suggest}" for suggest in suggestions])
        st.write(suggestions)
    

if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe What you want to parse (e.g., name, rank, website_url)")

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content")
            dom_chunks = split_dom_content(st.session_state.dom_content)
            result = parse_with_ollama(dom_chunks, parse_description)
            st.write(result)



# def parse_with_ollama(dom_chunks, parse_description):
#     # Example function to send data to Ollama and get the response
#     url = "https://api.ollama.com/parse"
#     headers = {
#         "accept": "application/json",
#         "content-type": "application/json"
#     }
#     results = []
#     for chunk in dom_chunks:
#         payload = {
#             "content": chunk,
#             "description": parse_description
#         }
#         response = requests.post(url, json=payload, headers=headers)
#         results.append(response.json())
#     return results



# st.title("Data Scraper")
# url = st.text_input("Enter WebLink : ")

# if st.button("Scrape Site"):
#   st.write("Scraping the website")
#   result = response.text
#   # print(result)
#   body_cont = extract_body_content(result)
#   cleaned_cont = clean_body_cont(body_cont)
#   st.session_state.dom_content = cleaned_cont

#   with st.expander("View DOM Content"):
#     st.text_area("DOM Content",cleaned_cont,height=300)

# if "dom_content" in st.session_state:
#   parse_description = st.text_area("Describe What you want to parse")

#   if st.button("Parse Content"):
#     if parse_description:
#       st.write("Parsing the content")
#       dom_chunks = split_dom_content(st.session_state.dom_content)
#       result = parse_with_ollama(dom_chunks , parse_description)
#       st.write(result)


# import requests
# from bs4 import BeautifulSoup
# import json

# def scrape_website(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.text
#     else:
#         return None

# def analyze_website(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')
    
#     # Example analysis: Check for broken links
#     broken_links = []
#     for link in soup.find_all('a', href=True):
#         href = link['href']
#         if not href.startswith('http'):
#             href = f"{urlparse(url).scheme}://{urlparse(url).netloc}{href}"
#         try:
#             link_response = requests.head(href)
#             if link_response.status_code >= 400:
#                 broken_links.append(href)
#         except requests.RequestException:
#             broken_links.append(href)
    
#     # Example analysis: Check for missing meta description
#     meta_description = soup.find('meta', attrs={'name': 'description'})
#     if not meta_description or not meta_description.get('content'):
#         meta_description_issue = "Missing meta description"
#     else:
#         meta_description_issue = None
    
#     # Example analysis: Check for mobile-friendliness (simplified)
#     viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
#     if not viewport_meta:
#         mobile_friendly_issue = "Missing viewport meta tag"
#     else:
#         mobile_friendly_issue = None
    
#     # Generate suggestions
#     suggestions = []
#     if broken_links:
#         suggestions.append(f"Broken links found: {', '.join(broken_links)}")
#     if meta_description_issue:
#         suggestions.append(meta_description_issue)
#     if mobile_friendly_issue:
#         suggestions.append(mobile_friendly_issue)
    
#     return suggestions

# def get_website_improvement_suggestions(url):
#     html_content = scrape_website(url)
#     if html_content:
#         suggestions = analyze_website(html_content)
#         return suggestions
#     else:
#         return ["Failed to scrape the website"]

# # Example usage
# url = "https://example.com"
# suggestions = get_website_improvement_suggestions(url)
# for suggestion in suggestions:
#     print(suggestion)
