"""
HyDE is an approach for precise zero-shot dense retrieval that does not require any relevance labels or supervision. The key idea is to use a language model to generate a hypothetical document based on the user's query, and then convert this into an embedding vector to retrieve the most similar real documents from a corpus.
The steps of HyDE retrieval are:
- Hypothetical Document Generation: Given a user query, a large language model like GPT-3 is used to generate a hypothetical document that tries to capture the relevant information to answer the query. This generated text may not be fully accurate, but aims to include key terms and concepts.
- Unsupervised Encoding: The generated hypothetical document is passed through an unsupervised encoder model to convert it into a dense embedding vector. The encoder is typically trained using contrastive learning to map semantically similar texts to nearby embedding vectors.
- Corpus Retrieval: The hypothetical document embedding is used to search the corpus embedding space and retrieve the real documents that are most similar to it based on vector similarity (e.g. inner product).

Pesudo code below is an example of how HyDE retrieval can be implemented using LangChain library in Python, note the retriever is not implemented in the library yet, however, sample code are offered in https://github.com/langchain-ai/rag-from-scratch/blob/main/rag_from_scratch_5_to_9.ipynb
"""

from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.retrievers.hyde import HyDERetriever

# Load embeddings model and vector database 
embeddings = OpenAIEmbeddings()
db = VectorStoreIndexWrapper(embedding=embeddings)

# Load question generation chain
llm = OpenAI(temperature=0)
prompt_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(prompt_template)
question_chain = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)

# Load HyDE retriever
retriever = HyDERetriever(
    llm_chain=question_chain, 
    base_retriever=db.as_retriever()
)

# Run retrieval on a query
query = "What are the health risks of fast food?"
docs = retriever.get_relevant_documents(query)
print(docs)
