from pydantic import BaseModel

class RefundResponse(BaseModel):
    refund_id: int
    order_id: int
    status: str
    amount: float

    model_config = {
        "from_attributes": True
    }
