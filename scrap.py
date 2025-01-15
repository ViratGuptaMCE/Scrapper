# import selenium.webdriver as webdriver
# from selenium.webdriver.chrome.service import Service
# import time
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

AUTH = 'brd-customer-hl_74fc088c-zone-first_scrap:ea13gt7ollpt'
SBR_WEBDRIVER = f'https://{AUTH}@brd.superproxy.io:9515'
def scrape_website(website):
  print("Launching browser...")
  # chrome_driver_path = "./chromedriver.exe"
  # options = webdriver.ChromeOptions()
  # driver = webdriver.Chrome(service=Service(chrome_driver_path),options = options)

  # try :
  #   driver.get(website)
  #   print("Page loaded...")
  #   html = driver.page_source
  #   time.sleep(10)
  #   return html
  # finally:
  #   driver.quit()
  sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'google', 'chrome')
  with Remote(sbr_connection, options=ChromeOptions()) as driver:
    print('Connected! Navigating...')
    driver.get(website)
    print('Taking page screenshot to file page.png')
    driver.get_screenshot_as_file('./page.png')
    print('Navigated! Scraping page content...')
    html = driver.page_source
    return html
# if __name__ == '__main__':
#   main()  
  


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
