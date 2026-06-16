import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
DOCUMENTS = ["faq.pdf", "shipping_policy.pdf", "return_policy.pdf"]

def ingest_documents():
    """
    Loads PDF documents, splits them into chunks, and ingests them into ChromaDB.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    all_documents = []
    
    # Path to backend/documents
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "documents")
    
    for doc_name in DOCUMENTS:
        doc_path = os.path.join(docs_dir, doc_name)
        
        if os.path.exists(doc_path):
            print(f"Loading {doc_path}...")
            loader = PyPDFLoader(doc_path)
            documents = loader.load()
            all_documents.extend(documents)
        else:
            print(f"Warning: Document {doc_name} not found at {doc_path}")

    if not all_documents:
        print("No documents were loaded. Exiting ingestion.")
        return

    # Split documents into smaller chunks for similarity search
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(all_documents)
    
    print(f"Split documents into {len(chunks)} chunks. Creating Chroma vectorstore...")
    
    # Ingest into Chroma vectorstore
    Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    print("Ingestion completed successfully.")

if __name__ == "__main__":
    ingest_documents()
