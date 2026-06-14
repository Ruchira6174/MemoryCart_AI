from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class OrderResponse(BaseModel):
    order_id: int
    product_name: str
    status: str
    delivery_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
