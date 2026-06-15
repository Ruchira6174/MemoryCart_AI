from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.memory import User, Memory
import logging

logger = logging.getLogger(__name__)


def get_user_memories(db: Session, user_id: int):
    """
    Fetch the latest memories for a specific user, limited to the last 5.
    Returns an empty list if no memories exist — never raises.
    """
    try:
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.created_at.desc())
            .limit(5)
        )
        return db.execute(stmt).scalars().all()
    except Exception as e:
        logger.error(f"Error fetching memories for user {user_id}: {e}")
        return []


def store_memory(db: Session, user_id: int, summary: str, issue_type: str):
    """
    Store a new memory entry for a user.

    If the user does not exist yet, creates them automatically to maintain
    referential integrity. Includes rollback protection on DB errors.
    """
    try:
        # Ensure user exists
        user_stmt = select(User).where(User.user_id == user_id)
        user = db.execute(user_stmt).scalar_one_or_none()

        if not user:
            user = User(user_id=user_id, name=f"User {user_id}")
            db.add(user)
            db.commit()
            db.refresh(user)

        memory = Memory(user_id=user_id, summary=summary, issue_type=issue_type)
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory

    except Exception as e:
        logger.error(f"Failed to store memory for user {user_id}: {e}")
        try:
            db.rollback()
        except Exception as rollback_err:
            logger.error(f"Rollback also failed: {rollback_err}")
        return None


def generate_memory_context(db: Session, user_id: int) -> str:
    """
    Retrieve latest 5 memories and format them into a readable text block.
    Returns an empty string if no memory exists — never raises.
    """
    memories = get_user_memories(db, user_id)
    if not memories:
        return ""

    context_lines = []
    for m in memories:
        try:
            timestamp_str = m.created_at.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            timestamp_str = "unknown"
        context_lines.append(
            f"[{timestamp_str}] Issue Type: {m.issue_type} - Summary: {m.summary}"
        )

    return "\n".join(context_lines)
