# import selenium.webdriver as webdriver
# from selenium.webdriver.chrome.service import Service
# import time
import requests
from urllib.parse import urlparse
import json
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from parse import parse_with_gemini

# AUTH = 'brd-customer-hl_74fc088c-zone-first_scrap:ea13gt7ollpt'
# SBR_WEBDRIVER = f'https://{AUTH}@brd.superproxy.io:9515'
# def scrape_website(website):
#   print("Launching browser...")
#   # chrome_driver_path = "./chromedriver.exe"
#   # options = webdriver.ChromeOptions()
#   # driver = webdriver.Chrome(service=Service(chrome_driver_path),options = options)

#   # try :
#   #   driver.get(website)
#   #   print("Page loaded...")
#   #   html = driver.page_source
#   #   time.sleep(10)
#   #   return html
#   # finally:
#   #   driver.quit()
#   sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'google', 'chrome')
#   with Remote(sbr_connection, options=ChromeOptions()) as driver:
#     print('Connected! Navigating...')
#     driver.get(website)
#     print('Taking page screenshot to file page.png')
#     driver.get_screenshot_as_file('./page.png')
#     print('Navigated! Scraping page content...')
#     html = driver.page_source
#     return html
# # if __name__ == '__main__':
# #   main()  
def scrape_website(website): 
  print("Launching browser...") 
  try: 
    response = requests.get(website) 
    response.raise_for_status() 
    # Check if the request was successful 
    print('Connected! Navigating...') 
    # Save the screenshot (if needed, you can use a different method to capture screenshots) 
    with open('page.png', 'wb') as f: 
      f.write(response.content) 
      print('Taking page screenshot to file page.png') 
      print('Navigated! Scraping page content...') 
      html = response.text 
      return html 
  except requests.RequestException as e: 
    print(f"Error: {e}") 
    return None


# AUTH = 'brd-customer-hl_74fc088c-zone-first_scrap:ea13gt7ollpt'
# SBR_WEBDRIVER = f'https://{AUTH}@brd.superproxy.io:9515'
# def main():
#     print('Connecting to Scraping Browser...')
#     sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
#     with Remote(sbr_connection, options=ChromeOptions()) as driver:
#         print('Connected! Navigating...')
#         driver.get('https://example.com')
#         print('Taking page screenshot to file page.png')
#         driver.get_screenshot_as_file('./page.png')
#         print('Navigated! Scraping page content...')
#         html = driver.page_source
#         print(html)
# if __name__ == '__main__':
#   main()

def extract_body_content(html_content):
  soup = BeautifulSoup(html_content,"html.parser")
  body_content = soup.body
  if body_content : 
    return str(body_content)
  return ""

def clean_body_cont(body_content):
  soup = BeautifulSoup(body_content,"html.parser")

  for script_or_style in soup(["script","style"]):
    script_or_style.extract()

  cleaned_content = soup.get_text(separator="\n")
  cleaned_content = "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())

  return cleaned_content

def split_dom_content(dom_content,max_length = 6000):
  return [
    dom_content[i: i+ max_length] for i in range(0,len(dom_content),max_length)
  ]


def analyze_website(html_content,url):
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
    mobile_friendly_issue = ''
    meta_description_issue = ''

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

    dom_chunks = split_dom_content(html_content)
    # result = parse_with_gemini(dom_chunks , parse_description)
    
    ollama_suggestions = parse_with_gemini(dom_chunks)
    suggestions.extend(ollama_suggestions)
    return suggestions

def get_website_improvement_suggestions(url):
    html_content = scrape_website(url)
    if html_content:
        suggestions = analyze_website(html_content,url)
        return suggestions
    else:
        return ["Failed to scrape the website"]