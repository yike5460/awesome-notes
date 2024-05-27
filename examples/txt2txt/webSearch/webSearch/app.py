# Import necessary libraries
import logging
# import os

import requests
import spacy
from bs4 import BeautifulSoup
from docx import Document
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from flask import Flask, jsonify, render_template, request
from googleapiclient.discovery import build
from PyPDF2 import PdfReader
from transformers import GPT2LMHeadModel, GPT2Tokenizer

load_dotenv()

# Read from local env file
# API_KEY = os.getenv("GOOGLE_API_KEY")
# CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Initialize Flask app
app = Flask(__name__)

# Initialize logging
logger = logging.getLogger(__name__)

# Set the logging level
logger.setLevel(logging.DEBUG)

# Create console handler and set level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)

app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)

# Initialize NLP models
nlp = spacy.load("en_core_web_sm")
# Load the tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer.pad_token_id = tokenizer.eos_token_id

# Initialize Elasticsearch with local instance
# Before that you need to have Elasticsearch running locally
"""
Initialization"
$ docker stop $(docker ps -a -q)
$ docker rm $(docker ps -a -q)

Launch without SSL:
docker run -d -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.4
$ curl -X GET "http://localhost:9200/"

Launch with SSL:
$ docker run --name temp-elasticsearch -it docker.elastic.co/elasticsearch/elasticsearch:8.13.4 bash
<inside container instance>
$ elasticsearch-certutil ca
$ elasticsearch-certutil cert --ca elastic-stack-ca.p12
<inside container instance>
$ openssl pkcs12 -in elastic-certificates.p12 -clcerts -nokeys -out elastic.crt
$ openssl pkcs12 -in elastic-certificates.p12 -nocerts -nodes -out elastic.key
$ openssl pkcs12 -in  elastic-certificates.p12 -out ca.crt -cacerts -nokeys
$ docker run -d -p 9200:9200 -p 9300:9300 \
  -v /home/ubuntu/justNotes/examples/txt2txt/webSearch/webSearch/ca:/usr/share/elasticsearch/config/certs \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=true" \
  -e "ELASTIC_PASSWORD=YourStrongPasswordHere" \
  -e "xpack.security.http.ssl.enabled=true" \
  -e "xpack.security.http.ssl.key=/usr/share/elasticsearch/config/certs/elastic.key" \
  -e "xpack.security.http.ssl.certificate=/usr/share/elasticsearch/config/certs/elastic.crt" \
  -e "xpack.security.http.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca.crt" \
  -e "xpack.security.transport.ssl.enabled=true" \
  -e "xpack.security.transport.ssl.verification_mode=certificate" \
  -e "xpack.security.transport.ssl.key=/usr/share/elasticsearch/config/certs/elastic.key" \
  -e "xpack.security.transport.ssl.certificate=/usr/share/elasticsearch/config/certs/elastic.crt" \
  -e "xpack.security.transport.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca.crt" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.4

curl -k -u elastic:YourStrongPasswordHere -X GET "https://localhost:9200/"
"""
# disable the SSL verification for local testing
# es = Elasticsearch(hosts=["http://localhost:9200"], verify_certs=False)

# enable the SSL verification for production
es = Elasticsearch(
    hosts=["https://127.0.0.1:9200"],
    basic_auth=('elastic', 'YourStrongPasswordHere'),  # Use basic_auth instead of http_auth
    verify_certs=True,
    # disable hostname verification for debugging purposes
    ssl_assert_hostname=False,
    ca_certs="/home/ubuntu/justNotes/examples/txt2txt/webSearch/webSearch/ca/ca.crt"  # Path to your CA certificate
)

@app.route("/")
def home():
    return render_template("main_page.html")


# User Interface Route
@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]
    document = request.files.get("document", None)
    # Allows user to specify options like 'web', 'document', or 'all' with default as 'all'
    search_options = request.form.get("options", "all")

    logger.debug("Received search request")
    logger.debug(f"Query: {query}")
    logger.debug(f"Search options: {search_options}")

    try:
        # Step 1: Query Understanding
        intent = understand_query(query)
        logger.debug(f"Intent of the query: {intent}")
        if not intent:
            return jsonify(
                {
                    "message": "Unable to determine intent of the query. Please refine your query."
                }
            ), 400

        web_results = []
        doc_results = []

        # Step 2: Web Search
        if search_options in ["all", "web"]:
            web_results = search_web(query)
            web_results.extend(web_results)

        # Step 3: Knowledge Base Integration
        if search_options in ["all", "document"]:
            doc_results = search_document(query, top_k=3)
            doc_results.extend(doc_results)

        # Step 4: Result Aggregation and Reranking
        aggregated_results = aggregate_and_rerank(web_results, doc_results)

        # Step 5: Response Generation
        # Assembe the final response with original query and aggregated results
        query_results = [query] + [result["content"] for result in aggregated_results]

        # Trunk the query length to 1024 tokens in case error occurs: Token indices sequence length is longer than the specified maximum sequence length for this model (10541 > 1024)
        query_results = " ".join(query_results)[:1024]
        final_response = generate_response(query_results)

        return jsonify({"response": final_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])
def index_document():
    # TODO, The document should pass into embedding model to convert into vector before indexing into Elasticsearch
    document = request.files.get("document", None)
    if document:
        filename = document.filename.lower()
        content = ""

        try:
            if filename.endswith(".pdf"):
                # Handle PDF files
                reader = PdfReader(document)
                for page in reader.pages:
                    content += (page.extract_text() or "") + " "
                # logging the first 1000 characters of the content
                logger.debug(f"PDF content (first 1000 characters): {content[:1000]}")
            elif filename.endswith(".docx"):
                # Handle DOCX files
                doc = Document(document)
                for para in doc.paragraphs:
                    content += para.text + " "
            elif filename.endswith(".doc"):
                # Handle older DOC files (requires additional handling)
                # This is a placeholder, as python-docx does not read .doc files
                content = (
                    "Error: .doc files are not supported. Please convert to .docx."
                )
                return jsonify({"error": content}), 400
            elif filename.endswith(".txt"):
                # Handle text files
                content = document.read().decode("utf-8")
            else:
                return jsonify({"error": "Unsupported file type"}), 400

            # Index document into Elasticsearch
            try:
                response = es.index(index="documents", body={"content": content})
                logger.debug(f"Document indexed successfully: {response}")
                return jsonify({"message": "Document indexed successfully", "id": response["_id"]})
            except Exception as e:
                logger.error(f"Error indexing document: {e}", exc_info=True)
                if isinstance(e, ConnectionError):
                    return jsonify({"error": "Failed to connect to Elasticsearch. Please check the service and network configuration."}), 503
                return jsonify({"error": str(e)}), 500
        except Exception as e:
            logger.error(f"Error processing or indexing document: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    return jsonify({"message": "No document provided"}), 400


def understand_query(query):
    logger.debug("****Understanding the query****")
    # Ensure pad_token_id is set
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    # Use NLP to understand the intent of the query
    inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
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
            max_length=50,
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
        soup = BeautifulSoup(response.text, "html.parser")
        logger.debug(f"Google raw search results: {soup.get_text()}")
        clean_results = []
        # TODO, update the parsing logic
        clean_results = soup.get_text().split("\n")
        # strip the tailing ' - Google Search' from the title

        # for g in soup.find_all('div', class_='g'):
        #     title = g.find('h3')
        #     if title:
        #         title_text = title.get_text()
        #     else:
        #         title_text = "No title found"

        #     snippet_div = g.find_next_sibling('div')
        #     if snippet_div:
        #         snippet_text = snippet_div.get_text()
        #     else:
        #         snippet_text = "No snippet found"

        #     clean_results.append({'title': title_text, 'snippet': snippet_text})
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
    response = requests.get(
        f"https://api.stackexchange.com/2.2/search?order=desc&sort=activity&intitle={query}&site=stackoverflow"
    )
    return response.json()


def search_document(query, top_k=10):
    """
    Search for documents in the Elasticsearch index that match the given query.

    :param query: Search query string
    :param top_k: Number of top documents to retrieve
    :return: List of top K documents matching the query
    """
    logger.debug("****Searching the document****")
    logger.debug(f"Query: {query}")

    response = es.search(
        index="documents",
        body={
            "size": top_k,  # Limit the number of results to top_k
            "query": {
                "match": {
                    "content": query
                }
            },
            "sort": [
                "_score"  # Sort by score descending (highest scores first)
            ]
        }
    )

    logger.debug(f"Document search results: {response}")
    return response["hits"]["hits"]


def aggregate_and_rerank(web_results, doc_results):
    # TODO Use BERT to rerank results
    """
    Transform both result into a common format:
    original web result:
    [
        'content'
    ]
    original doc result:
    [
        {
        '_index': 'documents', 
        '_id': '8ijOuI8BxhHDdfbBYvZM', 
        '_score': 2.3219662, 
        '_ignored': ['content.keyword'], 
        '_source': 
            {
            'content': 'content'
            }
        }
    ]
    common format:
    [
        {
        'content': 'content',
        '_score': 2.3219662
        }
    ]
    """
    all_results = []
    for result in web_results:
        # Give all web results a score of 1.0
        all_results.append({"content": result, "_score": 1.0})
    for result in doc_results:
        all_results.append({"content": result["_source"]["content"], "_score": result["_score"]})
    ranked_results = rank_results(all_results)
    return ranked_results


def rank_results(results):
    logger.debug("****Ranking the results****")
    return sorted(results, key=lambda x: x["_score"], reverse=True)


def generate_response(results):
    logger.debug("****Generating the response****")
    inputs = tokenizer(results, return_tensors="pt")
    outputs = model(**inputs)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == "__main__":
    app.run(debug=True)
    """
    curl -X POST http://localhost:5000/search \
    -F 'query=How to start with Flask?' \
    -F 'options=all'
    """
