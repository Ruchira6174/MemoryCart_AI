"""
retriever.py — ChromaDB vector store loader and policy retrieval.

Loads the persisted ChromaDB created by ingest.py and performs
similarity search to retrieve relevant policy context chunks.

EMBEDDING_MODEL is imported from the shared config.py — this guarantees
that retrieval always uses the exact same model that was used during
ingestion. To change the model, update config.py only.
"""
import logging
from pathlib import Path

from app.rag.config import EMBEDDING_MODEL, RAG_TOP_K

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Robust LangChain imports with version-independent fallbacks
# ---------------------------------------------------------------------------
try:
    from langchain_chroma import Chroma
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma
    except ImportError:
        from langchain.vectorstores import Chroma  # type: ignore

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        from langchain.embeddings import HuggingFaceEmbeddings  # type: ignore

# ---------------------------------------------------------------------------
# Path configuration — must match ingest.py
# retriever.py lives at: backend/app/rag/retriever.py
# chroma_db/    lives at: backend/app/rag/chroma_db/
# ---------------------------------------------------------------------------
PERSIST_DIR = Path(__file__).resolve().parent / "chroma_db"


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Return a HuggingFaceEmbeddings instance using the shared EMBEDDING_MODEL.
    Sourced from config.py to guarantee ingest ↔ retrieval model consistency.
    """
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


# Singleton — initialised once, reused across requests
_vector_store = None


def get_vector_store():
    """
    Load ChromaDB from disk. Returns None (not raises) if unavailable.
    Uses singleton pattern — only loaded once per server lifetime.
    """
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    if not PERSIST_DIR.exists():
        logger.warning(
            "ChromaDB not found at %s. "
            "Run: python -m app.rag.ingest  (or python app/rag/ingest.py)",
            PERSIST_DIR,
        )
        return None

    try:
        embeddings = get_embeddings()
        _vector_store = Chroma(
            persist_directory=str(PERSIST_DIR),
            embedding_function=embeddings,
        )
        logger.info("ChromaDB loaded successfully from %s.", PERSIST_DIR)
        return _vector_store
    except Exception as e:
        logger.error("Failed to load ChromaDB: %s", e)
        return None


def get_policy_answer(question: str) -> str:
    """
    Retrieve the top-k most relevant policy chunks for a given question.
    Returns a formatted string, or an empty string when nothing is found.
    Never raises — all errors are caught and logged.
    """
    try:
        db = get_vector_store()
        if db is None:
            return (
                "The policy knowledge base is not available right now. "
                "Please contact support directly for policy questions."
            )

        retriever = db.as_retriever(search_kwargs={"k": RAG_TOP_K})
        docs = retriever.invoke(question)

        if not docs:
            return ""

        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "")
            source_name = Path(source).name if source else "Policy Document"
            context_parts.append(
                f"--- Context Source {i}: {source_name} ---\n{doc.page_content}"
            )

        return "\n\n".join(context_parts)

    except Exception as e:
        logger.error("RAG retrieval error for question '%s': %s", question, e)
        return ""
