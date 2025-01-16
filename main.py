import streamlit as st
from scrap import scrape_website, split_dom_content , clean_body_cont,extract_body_content
from parse import parse_with_ollama

st.title("Data Scraper")
url = st.text_input("Enter WebLink : ")

if st.button("Scrape Site"):
  st.write("Scraping the website")
  result = scrape_website(url)
  # print(result)
  body_cont = extract_body_content(result)
  cleaned_cont = clean_body_cont(body_cont)
  st.session_state.dom_content = cleaned_cont

  with st.expander("View DOM Content"):
    st.text_area("DOM Content",cleaned_cont,height=300)

if "dom_content" in st.session_state:
  parse_description = st.text_area("Describe What you want to parse")

  if st.button("Parse Content"):
    if parse_description:
      st.write("Parsing the content")

      dom_chunks = split_dom_content(st.session_state.dom_content)
      result = parse_with_ollama(dom_chunks , parse_description)
      st.write(result)