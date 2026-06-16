from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Refund(Base):
    __tablename__ = "refunds"

    refund_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    status = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)

    # Relationship to order
    order = relationship("Order", back_populates="refunds")
