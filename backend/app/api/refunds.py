import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.refund_service import get_refund_status

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/refunds/{refund_id}", tags=["Refunds"])
def get_refund(refund_id: int, db: Session = Depends(get_db)):
    """
    Retrieve refund details by refund_id.
    Returns refund status, linked order_id, and refund amount.
    """
    try:
        refund = get_refund_status(db, refund_id)
        if not refund:
            return JSONResponse(status_code=200, content={
                "response": f"Refund with ID {refund_id} not found.",
                "data": {},
                "status": "error",
            })

        refund_data = {
            "refund_id": refund.refund_id,
            "order_id": refund.order_id,
            "status": refund.status,
            "amount": float(refund.amount),
        }
        return JSONResponse(status_code=200, content={
            "response": "Refund found.",
            "data": refund_data,
            "status": "success",
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error fetching refund {refund_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while fetching the refund."
        )
