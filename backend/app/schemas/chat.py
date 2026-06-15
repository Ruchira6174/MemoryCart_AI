from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    user_id: int
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    response: str
    data: Dict[str, Any] = {}
    status: str = "success"

    model_config = ConfigDict(from_attributes=True)
