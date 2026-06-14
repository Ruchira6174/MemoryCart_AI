from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_service import process_user_message

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    POST /chat endpoint to receive a user message, validate the request body,
    process it through the MemoryCart AI Agent, and return the response.
    """
    agent_response = process_user_message(
        user_id=request.user_id,
        message=request.message
    )
    return ChatResponse(response=agent_response)
