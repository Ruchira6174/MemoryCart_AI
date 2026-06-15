"""
hindsight_memory.py — Unified memory layer for MemoryCart AI.

Priority order:
  1. Hindsight SDK (cloud, long-term, semantic recall)
  2. Database-backed fallback (persistent across restarts via memories table)

The server must NEVER crash if Hindsight is unavailable.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Hindsight SDK initialisation — safe, non-crashing
# ---------------------------------------------------------------------------
_hindsight_client = None
_hindsight_available = False


def _init_hindsight():
    """
    Attempt to initialise the Hindsight client from environment variables.
    Returns (client, True) on success, (None, False) on any failure.
    """
    api_key = os.getenv("HINDSIGHT_API_KEY")
    base_url = os.getenv("HINDSIGHT_API_URL") or os.getenv("HINDSIGHT_BASE_URL")

    if not api_key or not base_url:
        logger.warning(
            "HINDSIGHT_API_KEY or HINDSIGHT_API_URL not set. "
            "Using database-backed fallback store."
        )
        return None, False

    try:
        from hindsight_client import Hindsight  # type: ignore
        # hindsight-client 0.8.2: constructor takes base_url; api_key is sent
        # via the Authorization header through the underlying aiohttp session.
        client = Hindsight(base_url=base_url, api_key=api_key)
        logger.info("Hindsight SDK initialised successfully (hindsight-client 0.8.2).")
        return client, True
    except TypeError:
        # Older/newer builds may not accept api_key in the constructor —
        # fall back to base_url-only init and rely on server-side key validation.
        try:
            from hindsight_client import Hindsight  # type: ignore
            client = Hindsight(base_url=base_url)
            logger.info(
                "Hindsight SDK initialised (base_url only — "
                "api_key will be validated server-side)."
            )
            return client, True
        except Exception as inner_e:
            logger.error(
                f"Failed to initialise Hindsight client (base_url only): {inner_e}. "
                "Falling back to database-backed store."
            )
    except ImportError:
        logger.warning(
            "hindsight_client package not found. "
            "Run: pip install hindsight-client==0.8.2  "
            "Falling back to database-backed store."
        )
    except Exception as e:
        logger.error(
            f"Failed to initialise Hindsight client: {e}. "
            "Falling back to database-backed store."
        )

    return None, False


_hindsight_client, _hindsight_available = _init_hindsight()


# ---------------------------------------------------------------------------
# Database-backed fallback helpers
# (Import lazily to avoid circular imports at module load time)
# ---------------------------------------------------------------------------

def _db_store_memory(user_id: int, message: str, response: str) -> None:
    """
    Persist a conversation exchange to the memories table.
    Structured storage: summary + issue_type + timestamp + user_id.
    """
    try:
        from app.database.connection import SessionLocal
        from app.services.memory_service import store_memory

        summary = f"User: {message[:120]} | Assistant: {response[:120]}"
        db = SessionLocal()
        try:
            store_memory(db, user_id, summary=summary, issue_type="GENERAL")
        finally:
            db.close()
    except Exception as e:
        # Absolute last resort — log and continue, never raise
        logger.error(f"DB fallback memory write failed for user {user_id}: {e}")


def _db_retrieve_memory(user_id: int) -> str:
    """
    Retrieve the last 5 memory entries from the database for a user.
    Returns a formatted string or '' if none exist.
    """
    try:
        from app.database.connection import SessionLocal
        from app.services.memory_service import get_user_memories

        db = SessionLocal()
        try:
            memories = get_user_memories(db, user_id)
        finally:
            db.close()

        if not memories:
            return ""

        lines = []
        for m in memories:
            ts = m.created_at.strftime("%Y-%m-%d %H:%M") if m.created_at else "unknown"
            lines.append(f"[{ts}] {m.issue_type}: {m.summary}")
        return "Past conversation history:\n" + "\n".join(lines)

    except Exception as e:
        logger.error(f"DB fallback memory read failed for user {user_id}: {e}")
        return ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_memory(user_id: int, message: str, response: str) -> bool:
    """
    Store a conversation exchange for a user.

    Uses Hindsight SDK when available.
    Falls back to database-backed persistence (survives restarts).
    Never raises — always returns True/False.
    """
    content = f"User: {message}\nAssistant: {response}"
    bank_id = f"user_{user_id}"

    if _hindsight_available and _hindsight_client is not None:
        try:
            _hindsight_client.retain(bank_id=bank_id, content=content)
            logger.debug(f"Memory saved to Hindsight for user {user_id}.")
            return True
        except Exception as e:
            logger.error(
                f"Hindsight retain failed for user {user_id}: {e}. "
                "Falling back to database store."
            )

    # DB-backed fallback — persistent across restarts
    _db_store_memory(user_id, message, response)
    return True


def retrieve_memory(user_id: int) -> str:
    """
    Retrieve synthesised memory context for a user.

    Uses Hindsight reflect/recall when available.
    Falls back to database-backed retrieval.
    Always returns a string — never raises.
    """
    bank_id = f"user_{user_id}"

    if _hindsight_available and _hindsight_client is not None:
        # Try reflect (synthesised summary)
        try:
            summary = _hindsight_client.reflect(
                bank_id=bank_id,
                query=(
                    "Provide a concise summary of the past conversations "
                    "and what the user has asked or experienced."
                ),
            )
            if summary:
                logger.debug(f"Hindsight reflect succeeded for user {user_id}.")
                return str(summary).strip()
        except Exception as e:
            logger.error(f"Hindsight reflect failed for user {user_id}: {e}.")

        # Fallback: recall (raw results)
        try:
            results = _hindsight_client.recall(
                bank_id=bank_id,
                query="What did the user ask or experience in past conversations?",
            )
            if results:
                return "\n".join(str(r).strip() for r in results)
        except Exception as e:
            logger.error(f"Hindsight recall failed for user {user_id}: {e}.")

    # DB-backed fallback — persistent across restarts
    return _db_retrieve_memory(user_id)
