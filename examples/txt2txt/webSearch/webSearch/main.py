# Import necessary libraries
import os
from flask import Flask, request, jsonify
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import requests
from bs4 import BeautifulSoup
import elasticsearch
from elasticsearch import Elasticsearch
import spacy
import logging
from googleapiclient.discovery import build

from dotenv import load_dotenv
load_dotenv()

# Read from local env file
API_KEY = os.getenv('GOOGLE_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')

# Initialize Flask app
app = Flask(__name__)

# Initialize logging
logger = logging.getLogger(__name__)

# Set the logging level
logger.setLevel(logging.DEBUG)

# Create console handler and set level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)

app.logger.addHandler(console_handler)
app.logger.setLevel(logging.DEBUG)

# Initialize NLP models
nlp = spacy.load("en_core_web_sm")
# Load the tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer.pad_token_id = tokenizer.eos_token_id

# Initialize Elasticsearch with local instance
es = Elasticsearch(hosts=["https://localhost:9200"])

# User Interface Route
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    document = request.files.get('document', None)
    search_options = request.form.get('options', 'all')  # Allows user to specify options like 'web', 'document', or 'all'

    logger.debug("Received search request")
    logger.debug(f"Query: {query}")
    logger.debug(f"Search options: {search_options}")

    try:
        # Step 1: Query Understanding
        intent = understand_query(query)
        logger.debug(f"Intent of the query: {intent}")
        if not intent:
            return jsonify({"message": "Unable to determine intent of the query. Please refine your query."}), 400
        
        results = []
        
        # Step 2: Web Search
        if search_options in ['all', 'web']:
            web_results = search_web(query)
            results.extend(web_results)
        
        # Step 3: Knowledge Base Integration
        if document and search_options in ['all', 'document']:
            doc_results = search_document(document, query)
            results.extend(doc_results)
        
        # Step 4: Result Aggregation and Reranking
        aggregated_results = aggregate_and_rerank(results)
        
        # Step 5: Response Generation
        final_response = generate_response(aggregated_results)
        
        return jsonify({"response": final_response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def understand_query(query):
    logger.debug("****Understanding the query****")
    # Ensure pad_token_id is set
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    # Use NLP to understand the intent of the query
    inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True)
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    logger.debug(f"Input IDs: {input_ids}, query: {query}")
    logger.debug(f"Attention mask: {attention_mask}")

    # Create the attention mask
    attention_mask = input_ids.ne(tokenizer.pad_token_id).long()
    logger.debug(f"Attention mask: {attention_mask}")

    # Generate text
    try:
        output = model.generate(
            input_ids=input_ids, 
            attention_mask=attention_mask, 
            pad_token_id=tokenizer.eos_token_id, 
            max_length=50
        )
        logger.debug(f"Output: {output}")
    except Exception as e:
        logger.error(f"Error during text generation: {e}", exc_info=True)
        return None

    # Decode the generated text
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    logger.debug(f"Generated text: {generated_text}")
    return generated_text

def search_web(query):
    logger.debug("****Searching the web****")
    logger.debug(f"Query: {query}")
    final_results = []
    # Search Google
    google_results = search_google(query)
    final_results.extend(google_results)
    # Search Reddit
    # reddit_results = search_reddit(query)
    reddit_results = []
    final_results.extend(reddit_results)
    # Search StackOverflow
    # stackoverflow_results = search_stackoverflow(query)
    stackoverflow_results = []
    final_results.extend(stackoverflow_results)
    return final_results

# Function to peform google custom search and return the text results
def search_google(query):
    # Use Google API to search for now, custom search API is not used
    try:
        response = requests.get(f"https://www.google.com/search?q={query}")
        soup = BeautifulSoup(response.text, 'html.parser')
        logger.debug(f"Google raw search results: {soup.get_text()}")
        clean_results = []
        # TODO, update the parsing logic
        for g in soup.find_all('div', class_='g'):
            title = g.find('h3')
            if title:
                title_text = title.get_text()
            else:
                title_text = "No title found"
            
            snippet_div = g.find_next_sibling('div')
            if snippet_div:
                snippet_text = snippet_div.get_text()
            else:
                snippet_text = "No snippet found"
            
            clean_results.append({'title': title_text, 'snippet': snippet_text})

        logger.debug(f"Google cleaned search results: {clean_results}")
        return clean_results

    except Exception as e:
        logger.error(f"Error searching Google: {e}", exc_info=True)
        return []

def search_reddit(query):
    # Use Reddit API to search
    try:
        response = requests.get(f"https://www.reddit.com/search.json?q={query}")
        return response.json()
    except Exception as e:
        logger.error(f"Error searching Reddit: {e}", exc_info=True)
        return []

def search_stackoverflow(query):
    # Use StackExchange API to search
    response = requests.get(f"https://api.stackexchange.com/2.2/search?order=desc&sort=activity&intitle={query}&site=stackoverflow")
    return response.json()

def search_document(document, query):
    es.index(index="documents", body={"content": document.read().decode('utf-8')})
    response = es.search(index="documents", body={"query": {"match": {"content": query}}})
    return response['hits']['hits']    

def aggregate_and_rerank(web_results, doc_results):
    # Use BERT to rerank results
    all_results = web_results + doc_results
    ranked_results = rank_results(all_results)
    return ranked_results

def rank_results(results):
    return sorted(results, key=lambda x: x['_score'], reverse=True)

def generate_response(results):
    inputs = tokenizer(results, return_tensors="pt")
    outputs = model(**inputs)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == '__main__':
    app.run(debug=True)
    """
    curl -X POST http://localhost:5000/search \
    -F 'query=How to start with Flask?' \
    -F 'options=all'
    """