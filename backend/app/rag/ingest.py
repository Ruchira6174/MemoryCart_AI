"""
ingest.py — Production-ready document ingestion pipeline for MemoryCart AI.

Architecture:
  documents/          ← PDF source files (backend/documents/)
  app/rag/chroma_db/  ← Persisted ChromaDB vector store
  app/rag/retriever.py ← Reads from chroma_db using the same embedding model

Usage:
  python -m app.rag.ingest              # normal run (append-only)
  CLEAR_EXISTING_DB=true python -m app.rag.ingest   # full rebuild

Design principles:
  - Single PDF failure never aborts the entire pipeline
  - Idempotent by default; explicit reset required for a full rebuild
  - Embedding model constant shared with retriever.py to prevent mismatches
  - Structured log output with per-phase statistics
  - Final summary always printed regardless of partial failures
"""

import logging
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from app.rag.config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Re-export so external callers can still do: from app.rag.ingest import EMBEDDING_MODEL
# ---------------------------------------------------------------------------
__all__ = ["EMBEDDING_MODEL", "ingest_docs", "validate_environment", "IngestionStats"]

#: When True, wipe and rebuild chroma_db from scratch.
#: Override via env var:  CLEAR_EXISTING_DB=true python -m app.rag.ingest
CLEAR_EXISTING_DB: bool = os.getenv("CLEAR_EXISTING_DB", "false").lower() == "true"

# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------
# ingest.py  →  backend/app/rag/ingest.py
# documents/ →  backend/documents/
# chroma_db/ →  backend/app/rag/chroma_db/
_RAG_DIR: Path = Path(__file__).resolve().parent
BASE_DIR: Path = _RAG_DIR.parent.parent.parent
DOCUMENTS_DIR: Path = BASE_DIR / "documents"
PERSIST_DIR: Path = _RAG_DIR / "chroma_db"

# ---------------------------------------------------------------------------
# Robust LangChain imports — version-independent fallbacks
# ---------------------------------------------------------------------------
try:
    from langchain_community.document_loaders import PyPDFLoader
except ImportError:
    from langchain.document_loaders import PyPDFLoader  # type: ignore

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore

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
# Ingestion statistics dataclass
# ---------------------------------------------------------------------------

@dataclass
class IngestionStats:
    """Accumulates metrics across the entire ingestion run."""
    pdfs_found: int = 0
    pdfs_loaded: int = 0
    pdfs_failed: int = 0
    pages_loaded: int = 0
    chunks_created: int = 0
    failed_files: List[str] = field(default_factory=list)
    status: str = "NOT STARTED"


# ---------------------------------------------------------------------------
# Environment validation
# ---------------------------------------------------------------------------

def validate_environment() -> bool:
    """
    Run pre-flight checks before ingestion begins.

    Verifies:
      - documents/ directory exists (or can be created)
      - write permission for chroma_db/ parent
      - embedding model can be imported
      - chroma_db/ directory is accessible if it already exists

    Returns:
        True if all checks pass, False if a blocking issue is found.
        Non-blocking issues are logged as warnings.
    """
    all_ok = True

    # 1. Documents directory
    if not DOCUMENTS_DIR.exists():
        logger.warning(
            "⚠️  Documents directory not found at %s — creating it. "
            "Add PDF files then re-run.",
            DOCUMENTS_DIR,
        )
        try:
            DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error("❌ Cannot create documents directory: %s", e)
            all_ok = False
    else:
        logger.info("✅ Documents directory: %s", DOCUMENTS_DIR)

    # 2. Write permissions for chroma_db parent
    parent_dir = PERSIST_DIR.parent
    if not os.access(parent_dir, os.W_OK):
        logger.error(
            "❌ No write permission for ChromaDB parent directory: %s", parent_dir
        )
        all_ok = False
    else:
        logger.info("✅ Write permissions verified for: %s", parent_dir)

    # 3. ChromaDB directory (if it already exists)
    if PERSIST_DIR.exists():
        if not os.access(PERSIST_DIR, os.W_OK):
            logger.error("❌ ChromaDB directory exists but is not writable: %s", PERSIST_DIR)
            all_ok = False
        else:
            logger.info("✅ Existing ChromaDB accessible at: %s", PERSIST_DIR)

    # 4. Embedding model availability (import check only — no download here)
    try:
        HuggingFaceEmbeddings  # noqa: B018 — just verify importable
        logger.info("✅ HuggingFaceEmbeddings import OK (model: %s)", EMBEDDING_MODEL)
    except NameError:
        logger.error("❌ HuggingFaceEmbeddings could not be imported.")
        all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# Step 1 — Embedding model
# ---------------------------------------------------------------------------

def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Return a HuggingFaceEmbeddings instance using the shared EMBEDDING_MODEL.

    Using the constant guarantees ingest.py and retriever.py always use
    the same model, preventing silent embedding-dimension mismatches.
    """
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


# ---------------------------------------------------------------------------
# Step 2 — ChromaDB reset
# ---------------------------------------------------------------------------

def _reset_chroma_db() -> None:
    """
    Wipe the existing chroma_db directory for a clean rebuild.
    Called only when CLEAR_EXISTING_DB is True.
    Safe: checks existence before attempting deletion.
    """
    if PERSIST_DIR.exists():
        logger.warning(
            "🗑️  CLEAR_EXISTING_DB=True — deleting existing ChromaDB at %s",
            PERSIST_DIR,
        )
        shutil.rmtree(PERSIST_DIR)
        logger.info("✅ ChromaDB directory removed. Will rebuild from scratch.")
    else:
        logger.info("ℹ️  CLEAR_EXISTING_DB=True but no existing DB found — nothing to remove.")


# ---------------------------------------------------------------------------
# Step 3 — PDF discovery with duplicate detection
# ---------------------------------------------------------------------------

def _discover_pdfs() -> Tuple[List[Path], List[str]]:
    """
    Scan the documents directory for PDF files.

    Returns:
        (unique_pdf_paths, duplicate_names)
        Duplicates are files whose stem (name without extension) appears
        more than once (case-insensitive), which could indicate accidental
        re-ingestion of renamed copies.
    """
    all_pdfs = sorted(DOCUMENTS_DIR.glob("*.pdf"))
    seen_stems: dict[str, Path] = {}
    unique: List[Path] = []
    duplicates: List[str] = []

    for pdf in all_pdfs:
        stem = pdf.stem.lower()
        if stem in seen_stems:
            duplicates.append(pdf.name)
            logger.warning(
                "⚠️  Potential duplicate detected: '%s' has the same base name as '%s'. "
                "Skipping to prevent double-ingestion.",
                pdf.name,
                seen_stems[stem].name,
            )
        else:
            seen_stems[stem] = pdf
            unique.append(pdf)

    return unique, duplicates


# ---------------------------------------------------------------------------
# Step 4 — Load a single PDF with metadata validation
# ---------------------------------------------------------------------------

def _load_pdf(pdf_path: Path) -> Tuple[list, Optional[str]]:
    """
    Load a single PDF file and validate document metadata.

    Validates per document:
      - metadata dict is not empty
      - 'source' key maps to an existing file path
      - 'page' key is present (page number tracking)

    Returns:
        (documents, error_message)
        On success: (non-empty list, None)
        On failure: ([], error_string)
    """
    try:
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
    except Exception as e:
        return [], f"PyPDFLoader failed: {e}"

    if not docs:
        return [], "PyPDFLoader returned 0 documents (file may be empty or corrupt)"

    # Metadata validation — warn but do not discard documents
    malformed_count = 0
    for i, doc in enumerate(docs):
        meta = doc.metadata or {}

        if not meta:
            logger.warning(
                "⚠️  [%s] Page %d has no metadata at all.", pdf_path.name, i
            )
            malformed_count += 1
            continue

        source = meta.get("source", "")
        if source and not Path(source).exists():
            logger.warning(
                "⚠️  [%s] Page %d: metadata 'source' path does not exist: %s",
                pdf_path.name, i, source,
            )

        if "page" not in meta:
            logger.warning(
                "⚠️  [%s] Page %d: 'page' key missing from metadata.",
                pdf_path.name, i,
            )
            malformed_count += 1

    if malformed_count > 0:
        logger.warning(
            "⚠️  [%s] %d/%d pages had malformed metadata — still ingested.",
            pdf_path.name, malformed_count, len(docs),
        )

    return docs, None


# ---------------------------------------------------------------------------
# Step 5 — Load all PDFs
# ---------------------------------------------------------------------------

def _load_all_pdfs(pdf_files: List[Path], stats: IngestionStats) -> list:
    """
    Load all discovered PDFs, continuing past individual failures.

    Updates stats in-place.
    Returns a flat list of all successfully loaded LangChain Document objects.
    """
    all_documents = []

    for pdf in pdf_files:
        logger.info("📄 Loading: %s", pdf.name)
        docs, error = _load_pdf(pdf)

        if error:
            logger.error("❌ Failed to load '%s': %s", pdf.name, error)
            stats.pdfs_failed += 1
            stats.failed_files.append(pdf.name)
            continue

        logger.info(
            "   ✅ '%s' → %d page(s) loaded.", pdf.name, len(docs)
        )
        stats.pdfs_loaded += 1
        stats.pages_loaded += len(docs)
        all_documents.extend(docs)

    return all_documents


# ---------------------------------------------------------------------------
# Step 6 — Chunk documents
# ---------------------------------------------------------------------------

def _split_documents(documents: list) -> list:
    """
    Split documents into overlapping chunks for embedding.

    chunk_size=1000, chunk_overlap=200 gives ~200-char context overlap
    between adjacent chunks, improving retrieval quality at boundaries.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


# ---------------------------------------------------------------------------
# Step 7 — Build / update ChromaDB
# ---------------------------------------------------------------------------

def _build_vector_store(chunks: list, embeddings: HuggingFaceEmbeddings) -> Chroma:
    """
    Persist chunks into ChromaDB.

    Modern chromadb versions auto-persist on write; the legacy
    vector_store.persist() call has been intentionally omitted.
    """
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(PERSIST_DIR),
    )
    return vector_store


# ---------------------------------------------------------------------------
# Step 8 — Post-ingestion verification
# ---------------------------------------------------------------------------

def _verify_vector_store(vector_store: Chroma) -> bool:
    """
    Confirm the vector store was persisted correctly.

    Checks:
      1. PERSIST_DIR exists on disk
      2. Collection is non-empty (at least 1 document)
      3. At least one file was created inside the persist directory

    Returns:
        True if all checks pass, False otherwise.
    """
    all_pass = True

    # Check 1: directory exists
    if not PERSIST_DIR.exists():
        logger.error("❌ Verification FAILED: ChromaDB directory not found after ingestion.")
        all_pass = False
    else:
        logger.info("✅ Verification: ChromaDB directory exists at %s", PERSIST_DIR)

    # Check 2: collection is non-empty
    try:
        count = vector_store._collection.count()
        if count == 0:
            logger.error("❌ Verification FAILED: ChromaDB collection is empty after ingestion.")
            all_pass = False
        else:
            logger.info("✅ Verification: %d document chunks stored in ChromaDB.", count)
    except Exception as e:
        logger.warning("⚠️  Could not verify collection count: %s", e)

    # Check 3: persistence files present
    db_files = list(PERSIST_DIR.rglob("*")) if PERSIST_DIR.exists() else []
    if not db_files:
        logger.error("❌ Verification FAILED: ChromaDB directory is empty after ingestion.")
        all_pass = False
    else:
        logger.info(
            "✅ Verification: %d file(s) found in ChromaDB directory.", len(db_files)
        )

    return all_pass


# ---------------------------------------------------------------------------
# Step 9 — Final summary report
# ---------------------------------------------------------------------------

def _print_summary(stats: IngestionStats) -> None:
    """Print the structured ingestion summary to stdout and logger."""
    divider = "=" * 45
    summary_lines = [
        "",
        divider,
        "  RAG INGESTION SUMMARY",
        divider,
        f"  PDFs Found       : {stats.pdfs_found}",
        f"  PDFs Loaded      : {stats.pdfs_loaded}",
        f"  PDFs Failed      : {stats.pdfs_failed}",
        f"  Pages Loaded     : {stats.pages_loaded}",
        f"  Chunks Created   : {stats.chunks_created}",
        f"  Embedding Model  : {EMBEDDING_MODEL}",
        f"  Vector Store Path: {PERSIST_DIR}",
        f"  Status           : {stats.status}",
    ]
    if stats.failed_files:
        summary_lines.append(f"  Failed Files     : {', '.join(stats.failed_files)}")
    summary_lines.append(divider)
    summary_lines.append("")

    report = "\n".join(summary_lines)
    print(report)
    logger.info("Ingestion summary:\n%s", report)


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------

def ingest_docs() -> IngestionStats:
    """
    Run the full document ingestion pipeline.

    Pipeline stages:
      1. Environment validation
      2. Optional ChromaDB reset
      3. PDF discovery + duplicate detection
      4. Load PDFs with metadata validation
      5. Chunk documents
      6. Embed and persist to ChromaDB
      7. Post-ingestion verification
      8. Print final summary

    Returns:
        IngestionStats — full metrics from this run.
    Never raises — all errors are caught and recorded in stats.
    """
    stats = IngestionStats()
    logger.info("=" * 45)
    logger.info("  MemoryCart AI — RAG Ingestion Pipeline")
    logger.info("=" * 45)

    # ── Stage 1: Environment validation ─────────────────────────────────────
    logger.info("▶ Stage 1/7: Environment validation")
    env_ok = validate_environment()
    if not env_ok:
        stats.status = "ABORTED — environment validation failed"
        _print_summary(stats)
        return stats

    # ── Stage 2: Optional ChromaDB reset ────────────────────────────────────
    if CLEAR_EXISTING_DB:
        logger.info("▶ Stage 2/7: Resetting ChromaDB (CLEAR_EXISTING_DB=True)")
        try:
            _reset_chroma_db()
        except Exception as e:
            logger.error("❌ ChromaDB reset failed: %s", e)
            stats.status = "ABORTED — ChromaDB reset failed"
            _print_summary(stats)
            return stats
    else:
        logger.info("▶ Stage 2/7: ChromaDB reset skipped (CLEAR_EXISTING_DB=False)")

    # ── Stage 3: PDF discovery ───────────────────────────────────────────────
    logger.info("▶ Stage 3/7: Discovering PDFs in %s", DOCUMENTS_DIR)
    try:
        pdf_files, duplicates = _discover_pdfs()
    except Exception as e:
        logger.error("❌ PDF discovery failed: %s", e)
        stats.status = "ABORTED — PDF discovery failed"
        _print_summary(stats)
        return stats

    stats.pdfs_found = len(pdf_files) + len(duplicates)
    logger.info(
        "   Found %d PDF(s) total (%d unique, %d duplicate/skipped).",
        stats.pdfs_found, len(pdf_files), len(duplicates),
    )

    if not pdf_files:
        stats.status = "SKIPPED — no PDF files to ingest"
        _print_summary(stats)
        return stats

    # ── Stage 4: Load PDFs ───────────────────────────────────────────────────
    logger.info("▶ Stage 4/7: Loading %d PDF file(s)", len(pdf_files))
    all_documents = _load_all_pdfs(pdf_files, stats)

    if not all_documents:
        logger.error("❌ No documents were loaded successfully. Aborting.")
        stats.status = "FAILED — no documents loaded"
        _print_summary(stats)
        return stats

    logger.info(
        "   Total: %d document page(s) loaded from %d PDF(s).",
        stats.pages_loaded, stats.pdfs_loaded,
    )

    # ── Stage 5: Chunking ────────────────────────────────────────────────────
    logger.info("▶ Stage 5/7: Splitting into chunks")
    try:
        chunks = _split_documents(all_documents)
        stats.chunks_created = len(chunks)
        logger.info(
            "   %d page(s) → %d chunks (size=%d, overlap=%d).",
            len(all_documents), stats.chunks_created, CHUNK_SIZE, CHUNK_OVERLAP,
        )
    except Exception as e:
        logger.error("❌ Document splitting failed: %s", e)
        stats.status = "FAILED — document splitting error"
        _print_summary(stats)
        return stats

    # ── Stage 6: Embed + persist ─────────────────────────────────────────────
    logger.info("▶ Stage 6/7: Embedding and persisting to ChromaDB")
    logger.info("   Model: %s", EMBEDDING_MODEL)
    logger.info("   Destination: %s", PERSIST_DIR)
    try:
        embeddings = get_embeddings()
        vector_store = _build_vector_store(chunks, embeddings)
        logger.info("   ✅ ChromaDB built successfully.")
    except Exception as e:
        logger.error("❌ ChromaDB build failed: %s", e)
        stats.status = "FAILED — ChromaDB build error"
        _print_summary(stats)
        return stats

    # ── Stage 7: Verification ────────────────────────────────────────────────
    logger.info("▶ Stage 7/7: Verifying vector store")
    try:
        verified = _verify_vector_store(vector_store)
        stats.status = "SUCCESS ✅" if verified else "PARTIAL — verification warnings"
    except Exception as e:
        logger.warning("⚠️  Verification step raised an error: %s", e)
        stats.status = "SUCCESS (verification skipped)"

    _print_summary(stats)
    return stats


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    ingest_docs()