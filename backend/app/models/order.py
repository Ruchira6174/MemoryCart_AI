from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    # Using Integer instead of ForeignKey("users.id") to avoid NoReferencedTableError 
    # if the 'users' table is not yet created. Update this if you have a User model.
    user_id = Column(Integer, index=True, nullable=False) 
    product_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    delivery_date = Column(Date, nullable=True)

    # Relationship to refunds
    refunds = relationship("Refund", back_populates="order", cascade="all, delete-orphan")
