from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.order import Order

def get_order_status(db: Session, order_id: int):
    """
    Query the orders table by order_id.
    Return the Order instance or None if not found.
    """
    stmt = select(Order).where(Order.order_id == order_id)
    return db.execute(stmt).scalar_one_or_none()
