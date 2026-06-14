from pydantic import BaseModel, ConfigDict

class ChatRequest(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    response: str

    model_config = ConfigDict(from_attributes=True)
