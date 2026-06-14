import os
from pathlib import Path

# Robust LangChain imports with version-independent fallbacks
try:
    from langchain_community.document_loaders import PyPDFLoader
except ImportError:
    from langchain.document_loaders import PyPDFLoader

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    try:
        from langchain_chroma import Chroma
    except ImportError:
        from langchain.vectorstores import Chroma

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError:
        from langchain.embeddings import HuggingFaceEmbeddings

# Define paths relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "documents"
PERSIST_DIR = Path(__file__).resolve().parent / "chroma_db"

def get_embeddings():
    # Local lightweight HuggingFace Embeddings
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def ingest_docs():
    # Make sure documents directory exists
    if not DOCUMENTS_DIR.exists():
        print(f"Documents directory {DOCUMENTS_DIR} does not exist. Creating it.")
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        return

    # Look for PDF files
    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {DOCUMENTS_DIR}. Please add faq.pdf, shipping_policy.pdf, or return_policy.pdf.")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")
    documents = []

    for pdf_path in pdf_files:
        print(f"Loading {pdf_path.name}...")
        try:
            loader = PyPDFLoader(str(pdf_path))
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {pdf_path.name}: {e}")

    if not documents:
        print("No documents loaded.")
        return

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # Initialize embeddings
    embeddings = get_embeddings()

    # Store in ChromaDB
    print(f"Creating/updating ChromaDB at {PERSIST_DIR}...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(PERSIST_DIR)
    )
    
    # In newer langchain-community versions, persist is handled automatically, 
    # but we call it explicitly for compatibility.
    if hasattr(vector_store, "persist"):
        vector_store.persist()
        
    print("Ingestion completed successfully.")

if __name__ == "__main__":
    ingest_docs()
