"""
main.py — MemoryCart AI FastAPI application entrypoint.

Startup lifecycle:
  1. Register SQLAlchemy models
  2. Create database tables
  3. Validate all required configuration (with warnings, not crashes)
  4. Pre-warm ChromaDB vector store
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.database.connection import engine, Base
from app.api.chat import router as chat_router
from app.api.memory import router as memory_router
from app.api.orders import router as orders_router
from app.api.refunds import router as refunds_router

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("memorycart")


# ---------------------------------------------------------------------------
# Phase 9 — Startup validation helpers
# ---------------------------------------------------------------------------

def _validate_groq() -> None:
    """Warn if GROQ_API_KEY is missing. Agent will return mock responses."""
    if not os.getenv("GROQ_API_KEY"):
        logger.warning(
            "⚠️  GROQ_API_KEY is not set. "
            "The agent will return limited mock responses until this is configured."
        )
    else:
        logger.info("✅ GROQ_API_KEY detected.")


def _validate_hindsight() -> None:
    """Warn if Hindsight credentials are missing."""
    api_key = os.getenv("HINDSIGHT_API_KEY")
    base_url = os.getenv("HINDSIGHT_API_URL") or os.getenv("HINDSIGHT_BASE_URL")
    if not api_key or not base_url:
        logger.warning(
            "⚠️  HINDSIGHT_API_KEY / HINDSIGHT_API_URL not fully set. "
            "Long-term memory will use database-backed fallback store."
        )
    else:
        logger.info("✅ Hindsight credentials detected.")


def _validate_chromadb() -> None:
    """Warn if ChromaDB has not been initialised yet."""
    chroma_path = Path(__file__).resolve().parent / "rag" / "chroma_db"
    if not chroma_path.exists():
        logger.warning(
            "⚠️  ChromaDB not found at %s. "
            "Policy (RAG) questions will return a fallback message. "
            "To enable RAG, run: python -m app.rag.ingest",
            chroma_path,
        )
    else:
        logger.info("✅ ChromaDB directory found at %s.", chroma_path)
        # Pre-warm the vector store so the first request is fast
        try:
            from app.rag.retriever import get_vector_store
            get_vector_store()
            logger.info("✅ ChromaDB vector store pre-loaded successfully.")
        except Exception as e:
            logger.warning("⚠️  ChromaDB pre-load failed: %s", e)


def _validate_database() -> None:
    """Attempt a live DB connection and warn if it fails."""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified.")
    except Exception as e:
        # Read configured DB settings for clearer diagnostics (do not log raw password)
        db_host = os.getenv("DB_HOST", "<not-set>")
        db_port = os.getenv("DB_PORT", "<not-set>")
        db_name = os.getenv("DB_NAME", "<not-set>")
        db_user = os.getenv("DB_USER", "<not-set>")

        logger.error("❌ Database connection failed.")
        logger.error("Configured database: %s", db_name)
        logger.error("Host: %s:%s", db_host, db_port)
        logger.error("User: %s", db_user)
        logger.error("Reason: %s", e)
        logger.error("Check DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD in .env")


# ---------------------------------------------------------------------------
# Startup / Shutdown lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register all models so metadata is available before table creation
    import app.models.memory   # noqa: F401
    import app.models.order    # noqa: F401
    import app.models.refund   # noqa: F401

    # Database setup
    logger.info("Creating database tables if they do not exist...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables ready.")
    except Exception as e:
        logger.error("❌ Could not create database tables: %s", e)

    # Phase 9 — Configuration validation (warns, never crashes)
    logger.info("--- MemoryCart AI Startup Validation ---")
    _validate_database()
    _validate_groq()
    _validate_hindsight()
    _validate_chromadb()
    logger.info("--- Startup validation complete ---")

    yield  # Application runs here

    logger.info("MemoryCart AI shutting down.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="MemoryCart AI",
    description=(
        "AI-powered e-commerce assistant with persistent memory, "
        "policy retrieval (RAG), order tracking, and refund tracking."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow all origins for development / hackathon demo
# In production, replace allow_origins=["*"] with specific domains.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # credentials=True is incompatible with allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers — all PRD-required endpoints
# ---------------------------------------------------------------------------
app.include_router(chat_router)    # POST /chat
app.include_router(memory_router)  # GET  /memory/{user_id}
app.include_router(orders_router)  # GET  /orders/{order_id}
app.include_router(refunds_router) # GET  /refunds/{refund_id}

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    """Health check — returns service running status."""
    return {"status": "running", "service": "MemoryCart AI"}
