from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base

class Memory(Base):
    __tablename__ = "memories"

    memory_id = Column(Integer, primary_key=True, index=True)
    # Using Integer instead of ForeignKey("users.id") to avoid NoReferencedTableError 
    # if the 'users' table is not yet created. Update this if you have a User model.
    user_id = Column(Integer, index=True, nullable=False)
    issue_type = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
