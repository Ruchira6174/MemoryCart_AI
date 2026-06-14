from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.memory import User, Memory

def get_user_memories(db: Session, user_id: int):
    """
    Fetch the latest memories for a specific user, limited to the last 5.
    """
    stmt = (
        select(Memory)
        .where(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .limit(5)
    )
    return db.execute(stmt).scalars().all()

def store_memory(db: Session, user_id: int, summary: str, issue_type: str):
    """
    Store a new memory for a user. If the user doesn't exist, ensures
    they are created first to maintain database referential integrity.
    """
    # Check if user exists
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

def generate_memory_context(db: Session, user_id: int) -> str:
    """
    Retrieve latest 5 memories and format them into a readable text block.
    Returns an empty string if no memory exists.
    """
    memories = get_user_memories(db, user_id)
    if not memories:
        return ""

    context_lines = []
    for m in memories:
        timestamp_str = m.created_at.strftime("%Y-%m-%d %H:%M:%S")
        context_lines.append(
            f"[{timestamp_str}] Issue Type: {m.issue_type} - Summary: {m.summary}"
        )
    
    return "\n".join(context_lines)
