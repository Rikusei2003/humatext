import uuid
from datetime import datetime

from pydantic import BaseModel


class CreateOrderRequest(BaseModel):
    order_type: str  # "subscription" or "points"
    item_id: uuid.UUID


class PlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    price_yuan: int
    duration_days: int
    max_word_count: int
    daily_limit: int

    model_config = {"from_attributes": True}


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    plan_name: str | None = None
    start_date: datetime
    end_date: datetime
    is_active: bool


class OrderResponse(BaseModel):
    id: uuid.UUID
    order_type: str
    amount_yuan: int
    payment_status: str
    trade_no: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
