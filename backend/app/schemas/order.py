from pydantic import BaseModel
from typing import Optional

class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    product_name: str
    status: str
    delivery_date: Optional[str] = None

    model_config = {
        "from_attributes": True
    }