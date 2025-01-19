from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import google.generativeai as genai
import os 
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv('GEMINI_KEY')

template = (
  "You are tasked with extracting specific information from the following text content: {dom_content}. "
  "Please follow these instructions carefully: \n\n"
  "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
  "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
  "3. **Empty Response:** If no information matches the description, return an empty string ('')."
  "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

model = OllamaLLM(model="llama3.2")

def parse_with_ollama(html_content):
  prompt = ChatPromptTemplate.from_template(template) 
  chain = prompt | model 
  parse_description = "suggest improvement for website or is there any issue with it"
  # response = chain.invoke({"dom_content": html_content, "parse_description": parse_description}) 
  ollama_suggestions = []
  for i, chunk in enumerate(html_content, start=1): 
    response = chain.invoke({"dom_content": chunk, "parse_description": parse_description}) 
    print(f"Parsed batch {i} of {len(html_content)}") 
    ollama_suggestions.append(response)
  # ollama_suggestions = response.strip().split('\n') 
  return ollama_suggestions  
  # parsed_results = [] 
  # for i, chunk in enumerate(dom_chunks, start=1): 
  #   response = chain.invoke({"dom_content": chunk, "parse_description": parse_description}) 
  #   print(f"Parsed batch {i} of {len(dom_chunks)}") 
  #   parsed_results.append(response) 
  # return "\n".join(parsed_results)

def parse_with_gemini(html_content): 
  genai.configure(api_key=gemini_api_key) 
  prompt = ( "suggest improvement for website or is there any issue with it {html_content} is providen to you" ) 
  model = genai.GenerativeModel("gemini-1.5-flash")
  response = model.generate_content( prompt.format(html_content=html_content, parse_description="suggest improvement for website or is there any issue with it") ) 
  gemini_suggestions = response.text.strip().split('\n') 
  print("\n\n\n",response , "\n\n\n")
  return gemini_suggestions

# def parse_with_ollama(dom_chunks,parse_description):
#   prompt = ChatPromptTemplate.from_template(template)
#   chain  = prompt | model
#   parsed_results = []

#   for i, chunk in enumerate(dom_chunks,start= 1):
#     response = chain.invoke({"dom_content" : chunk,"parse_description" : parse_description})
#     print(f"Parsed batch {i} of {len(dom_chunks)}")
#     parsed_results.append(response)

#   return "\n".join(parsed_results)
