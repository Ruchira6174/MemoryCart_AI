from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict

from app.database.connection import get_db
from app.services.agent_service import AgentService
from app.services.memory_service import MemoryService
from app.services.order_service import get_order_by_id
from app.services.refund_service import get_refund_by_id

# Import from schemas
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Process a user message through the AI agent workflow.
    """
    try:
        response_text = AgentService.process_message(
            db=db, 
            user_id=request.user_id, 
            message=request.message
        )
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")

@router.get("/memory/{user_id}")
def get_user_memory(user_id: int) -> Dict[str, Any]:
    """
    Retrieve the latest memories for a given user.
    """
    try:
        memories = MemoryService.get_latest_memories(user_id=user_id, limit=5)
        return {"user_id": user_id, "memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memory: {str(e)}")

@router.get("/orders/{order_id}")
def get_order_endpoint(order_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieve order details by order ID.
    """
    try:
        order = get_order_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "order_id": order.order_id,
            "user_id": order.user_id,
            "product_name": order.product_name,
            "status": order.status,
            "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve order: {str(e)}")

@router.get("/refunds/{refund_id}")
def get_refund_endpoint(refund_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Retrieve refund details by refund ID.
    """
    try:
        refund = get_refund_by_id(db, refund_id)
        if not refund:
            raise HTTPException(status_code=404, detail="Refund not found")
            
        return {
            "refund_id": refund.refund_id,
            "order_id": refund.order_id,
            "status": refund.status,
            "amount": refund.amount
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve refund: {str(e)}")
