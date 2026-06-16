from pydantic import BaseModel
from datetime import datetime


class MemoryResponse(BaseModel):
    memory_id: int
    user_id: int
    issue_type: str
    summary: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }