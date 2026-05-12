import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import CreateOrderRequest
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create")
async def create_order(
    req: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await payment_service.create_order(db, current_user.id, req.order_type, req.item_id)
    return {
        "id": str(order.id),
        "order_type": order.order_type,
        "amount_yuan": order.amount_yuan,
        "payment_status": order.payment_status,
        "created_at": order.created_at.isoformat(),
    }


@router.get("/orders")
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    orders = await payment_service.get_orders(db, current_user.id)
    return [
        {"id": str(o.id), "order_type": o.order_type, "amount_yuan": o.amount_yuan,
         "payment_status": o.payment_status, "trade_no": o.trade_no,
         "created_at": o.created_at.isoformat()}
        for o in orders
    ]


@router.get("/orders/{order_id}")
async def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = await payment_service.get_order(db, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(404, "Order not found")
    return {
        "id": str(order.id), "order_type": order.order_type,
        "amount_yuan": order.amount_yuan, "payment_status": order.payment_status,
        "trade_no": order.trade_no, "created_at": order.created_at.isoformat(),
    }


@router.post("/orders/{order_id}/pay")
async def pay_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mock payment for MVP — instantly confirms payment."""
    order = await payment_service.get_order(db, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(404, "Order not found")
    success = await payment_service.confirm_payment(db, order_id)
    if not success:
        raise HTTPException(400, "Payment already processed")
    return {"status": "paid", "message": "支付成功"}
