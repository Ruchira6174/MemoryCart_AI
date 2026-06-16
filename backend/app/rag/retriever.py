import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

def similarity_search(query: str, k: int = 3):
    """
    Performs a similarity search using ChromaDB and LangChain.
    Returns the top 'k' most similar document chunks.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load existing Chroma database
    vectorstore = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )
    
    # Perform similarity search and return top k chunks
    return vectorstore.similarity_search(query, k=k)
