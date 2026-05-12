import uuid
from datetime import datetime

from pydantic import BaseModel


class PointsBalanceResponse(BaseModel):
    balance: int

    model_config = {"from_attributes": True}


class PointsTransactionResponse(BaseModel):
    id: uuid.UUID
    amount: int
    transaction_type: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PointsPackageResponse(BaseModel):
    id: uuid.UUID
    name: str
    points_amount: int
    price_yuan: int

    model_config = {"from_attributes": True}


class PointsRedeemResponse(BaseModel):
    success: bool
    message: str
    balance: int
