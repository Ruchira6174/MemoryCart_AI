import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.order import Order

# Configure logging
logger = logging.getLogger(__name__)

def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    """
    Fetch an order from the database by its order_id.
    
    Args:
        db (Session): The SQLAlchemy database session.
        order_id (int): The ID of the order to retrieve.
        
    Returns:
        Optional[Order]: The Order object if found, else None.
        
    Raises:
        Exception: If a database error occurs during the query.
    """
    try:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        return order
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching order_id={order_id}: {str(e)}")
        raise Exception(f"An error occurred while reading order {order_id} from the database.") from e
    except Exception as e:
        logger.error(f"Unexpected error while fetching order_id={order_id}: {str(e)}")
        raise Exception("An unexpected error occurred.") from e
