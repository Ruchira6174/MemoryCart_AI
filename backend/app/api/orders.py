import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.order_service import get_order_status

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/orders/{order_id}", tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Retrieve order details by order_id.
    Returns order status, product name, and expected delivery date.
    """
    try:
        order = get_order_status(db, order_id)
        if not order:
            return JSONResponse(status_code=200, content={
                "response": f"Order with ID {order_id} not found.",
                "data": {},
                "status": "error",
            })

        # Serialize order into plain dict
        order_data = {
            "order_id": order.order_id,
            "user_id": order.user_id,
            "product_name": order.product_name,
            "status": order.status,
            "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
        }
        return JSONResponse(status_code=200, content={
            "response": "Order found.",
            "data": order_data,
            "status": "success",
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error fetching order {order_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while fetching the order."
        )
