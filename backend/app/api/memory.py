from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import get_db
from app.schemas.memory import MemoryResponse
from app.services.memory_service import get_user_memories

router = APIRouter()

@router.get("/memory/{user_id}", response_model=List[MemoryResponse])
def get_memories(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the history of memories (past issues and interactions) for a specific user.
    """
    return get_user_memories(db, user_id)
