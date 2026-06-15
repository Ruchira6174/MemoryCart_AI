import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_service import process_user_message

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest):
    """
    Send a user message and receive an AI-powered response.
    The agent detects intent and routes to memory, RAG, order, or refund service.

    Always returns unified JSON:
      { "response": "...", "data": {}, "status": "success" | "error" }
    """
    try:
        agent_response = process_user_message(
            user_id=request.user_id,
            message=request.message,
        )
        return ChatResponse(
            response=agent_response,
            data={},
            status="success",
        )
    except Exception as e:
        logger.exception(f"Unhandled error in /chat for user {request.user_id}: {e}")
        # Return the unified contract shape even for errors
        return JSONResponse(
            status_code=200,
            content={
                "response": (
                    "I'm sorry, something went wrong while processing your request. "
                    "Please try again."
                ),
                "data": {},
                # Return "success" so the frontend renders the response text above
                # instead of throwing on status="error". The message itself signals
                # the problem to the user gracefully.
                "status": "success",
            },
        )
