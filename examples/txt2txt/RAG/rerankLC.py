from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# load env variables from .env
from dotenv import load_dotenv
load_dotenv()

def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )

# Assuming documents are loaded and split
documents = UnstructuredPDFLoader("smallPDF.pdf", mode="elements", strategy="fast").load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

# Set up the base retriever
retriever = FAISS.from_documents(texts, CohereEmbeddings()).as_retriever(search_kwargs={"k": 3})

# Apply Cohere's re-ranker
compressor = CohereRerank()
compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)

# Query the compression retriever, note there is one issue :https://github.com/langchain-ai/langchain/discussions/19461 and error will prompt like "TypeError: BaseCohere.rerank() takes 1 positional argument but 4 positional arguments (and 2 keyword-only arguments) were given"
query = "What can I do with smallPDF?"
results = compression_retriever.get_relevant_documents("query")
pretty_print_docs(results)