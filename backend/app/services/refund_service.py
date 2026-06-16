import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.refund import Refund

# Configure logging
logger = logging.getLogger(__name__)

def get_refund_by_id(db: Session, refund_id: int) -> Optional[Refund]:
    """
    Fetch a refund from the database by its refund_id.
    
    Args:
        db (Session): The SQLAlchemy database session.
        refund_id (int): The ID of the refund to retrieve.
        
    Returns:
        Optional[Refund]: The Refund object if found, else None.
        
    Raises:
        Exception: If a database error occurs during the query.
    """
    try:
        refund = db.query(Refund).filter(Refund.refund_id == refund_id).first()
        return refund
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching refund_id={refund_id}: {str(e)}")
        raise Exception(f"An error occurred while reading refund {refund_id} from the database.") from e
    except Exception as e:
        logger.error(f"Unexpected error while fetching refund_id={refund_id}: {str(e)}")
        raise Exception("An unexpected error occurred.") from e
