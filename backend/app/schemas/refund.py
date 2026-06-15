from pydantic import BaseModel, ConfigDict


class RefundResponse(BaseModel):
    refund_id: int
    order_id: int
    status: str
    amount: float

    model_config = ConfigDict(from_attributes=True)
