import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.points import PointsPackage, PointsTransaction
from app.models.subscription import PaymentOrder, SubscriptionPlan
from app.services.subscription_service import activate_subscription


async def create_order(
    db: AsyncSession,
    user_id: uuid.UUID,
    order_type: str,  # "subscription" or "points"
    item_id: uuid.UUID,
) -> PaymentOrder:
    amount = 0
    plan_id = None
    package_id = None

    if order_type == "subscription":
        plan = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == item_id))
        plan = plan.scalar_one()
        amount = plan.price_yuan
        plan_id = plan.id
    else:
        pkg = await db.execute(select(PointsPackage).where(PointsPackage.id == item_id))
        pkg = pkg.scalar_one()
        amount = pkg.price_yuan
        package_id = pkg.id

    order = PaymentOrder(
        id=uuid.uuid4(),
        user_id=user_id,
        order_type=order_type,
        plan_id=plan_id,
        package_id=package_id,
        amount_yuan=amount,
        payment_status="pending",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def get_orders(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(
        select(PaymentOrder)
        .where(PaymentOrder.user_id == user_id)
        .order_by(PaymentOrder.created_at.desc())
        .limit(20)
    )
    return result.scalars().all()


async def get_order(db: AsyncSession, order_id: uuid.UUID) -> PaymentOrder | None:
    result = await db.execute(select(PaymentOrder).where(PaymentOrder.id == order_id))
    return result.scalar_one_or_none()


async def confirm_payment(db: AsyncSession, order_id: uuid.UUID) -> bool:
    """Mock payment confirmation for MVP."""
    order = await get_order(db, order_id)
    if not order or order.payment_status != "pending":
        return False

    now = datetime.now(timezone.utc)
    order.payment_status = "paid"
    order.trade_no = f"MOCK_{uuid.uuid4().hex[:12]}"
    order.paid_at = now

    # Fulfill the order
    if order.order_type == "subscription" and order.plan_id:
        await activate_subscription(db, order.user_id, order.plan_id)
    elif order.order_type == "points" and order.package_id:
        pkg = await db.execute(select(PointsPackage).where(PointsPackage.id == order.package_id))
        pkg = pkg.scalar_one()
        txn = PointsTransaction(
            id=uuid.uuid4(),
            user_id=order.user_id,
            amount=pkg.points_amount,
            transaction_type="earn_purchase",
            description=f"购买 {pkg.name}",
        )
        db.add(txn)

    await db.commit()
    return True
