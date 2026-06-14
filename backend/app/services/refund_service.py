from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.refund import Refund

def get_refund_status(db: Session, refund_id: int):
    """
    Query the refunds table by refund_id.
    Return the Refund instance or None if not found.
    """
    stmt = select(Refund).where(Refund.refund_id == refund_id)
    return db.execute(stmt).scalar_one_or_none()
