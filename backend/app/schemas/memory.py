from datetime import datetime
from pydantic import BaseModel, ConfigDict

class MemoryResponse(BaseModel):
    memory_id: int
    summary: str
    issue_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
