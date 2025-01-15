import streamlit as st
from scrap import scrape_website

st.title("Data Scraper")
url = st.text_input("Enter WebLink : ")

if st.button("Scrape Site"):
  st.write("Scraping the website")
  result = scrape_website(url)
  print(result)