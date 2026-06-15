"""
config.py — Shared configuration constants for MemoryCart AI.

Single source of truth for values that must be identical across
multiple modules (e.g. embedding model used by both ingest.py and
retriever.py). Import from here instead of duplicating constants.
"""

# ---------------------------------------------------------------------------
# RAG / Embedding
# ---------------------------------------------------------------------------

#: Full HuggingFace model identifier.
#: MUST be identical in ingest.py and retriever.py to prevent
#: embedding-dimension mismatches between ingestion and retrieval.
EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------

#: Number of relevant document chunks to retrieve per query.
RAG_TOP_K: int = 3

#: Text splitter parameters
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 200
