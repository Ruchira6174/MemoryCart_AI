import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.memory_service import get_user_memories

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/memory/{user_id}", tags=["Memory"])
def get_memories(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the stored memory history for a specific user.
    Returns up to the last 5 memory entries.
    Returns an empty list (not 404) when no memories exist yet — important for first-time users.
    """
    try:
        memories = get_user_memories(db, user_id)

        # Serialize memories into list of dicts
        mem_list = []
        for m in memories:
            mem_list.append({
                "memory_id": m.memory_id,
                "summary": m.summary,
                "issue_type": m.issue_type,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            })

        return JSONResponse(status_code=200, content={
            "response": "Memories retrieved.",
            "data": mem_list,
            "status": "success",
        })
    except Exception as e:
        logger.exception(f"Error fetching memories for user {user_id}: {e}")
        return JSONResponse(status_code=200, content={
            "response": "An error occurred while fetching memories.",
            "data": [],
            "status": "error",
        })
