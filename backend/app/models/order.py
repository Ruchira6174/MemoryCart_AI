from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base
from app.models.memory import User  # Ensure User is registered in metadata

class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), 
        nullable=False
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    delivery_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    refund: Mapped[Optional["Refund"]] = relationship(
        "Refund", 
        back_populates="order", 
        uselist=False, 
        cascade="all, delete-orphan"
    )
