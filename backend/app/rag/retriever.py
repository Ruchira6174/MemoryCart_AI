from pathlib import Path

# Robust LangChain imports with version-independent fallbacks
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

# Define path to ChromaDB
PERSIST_DIR = Path(__file__).resolve().parent / "chroma_db"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = get_embeddings()
        if PERSIST_DIR.exists():
            _vector_store = Chroma(
                persist_directory=str(PERSIST_DIR),
                embedding_function=embeddings
            )
        else:
            _vector_store = None
    return _vector_store

def get_policy_answer(question: str) -> str:
    """
    Retrieve relevant policy context from ChromaDB for the given question.
    """
    db = get_vector_store()
    if not db:
        return "No policy database found. Please run ingest.py first."

    # Retrieve relevant documents (top 3 matches)
    retriever = db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)

    if not docs:
        return ""

    # Format the retrieved chunks into a single readable context block
    context_parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        source_name = Path(source).name if source else "Policy Document"
        context_parts.append(
            f"--- Context Source {i}: {source_name} ---\n{doc.page_content}"
        )

    return "\n\n".join(context_parts)
