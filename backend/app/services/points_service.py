import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.points import PointsPackage, PointsTransaction


async def get_balance(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.coalesce(func.sum(PointsTransaction.amount), 0)).where(
            PointsTransaction.user_id == user_id
        )
    )
    return result.scalar() or 0


async def get_transactions(db: AsyncSession, user_id: uuid.UUID, limit: int = 20):
    result = await db.execute(
        select(PointsTransaction)
        .where(PointsTransaction.user_id == user_id)
        .order_by(PointsTransaction.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def earn_daily_login(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Award daily login points. Returns 0 if already claimed today."""
    from datetime import date, datetime, timezone

    today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)
    result = await db.execute(
        select(PointsTransaction).where(
            PointsTransaction.user_id == user_id,
            PointsTransaction.transaction_type == "earn_daily",
            PointsTransaction.created_at >= today_start,
        )
    )
    if result.scalar_one_or_none():
        return 0  # already claimed today

    txn = PointsTransaction(
        id=uuid.uuid4(),
        user_id=user_id,
        amount=settings.DAILY_LOGIN_POINTS,
        transaction_type="earn_daily",
        description="每日签到",
    )
    db.add(txn)
    await db.commit()
    return settings.DAILY_LOGIN_POINTS


async def spend_rewrite(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Spend points for one extra rewrite. Returns True if successful."""
    balance = await get_balance(db, user_id)
    if balance < settings.POINTS_PER_REWRITE:
        return False
    txn = PointsTransaction(
        id=uuid.uuid4(),
        user_id=user_id,
        amount=-settings.POINTS_PER_REWRITE,
        transaction_type="spend_rewrite",
        description="积分兑换改写次数",
    )
    db.add(txn)
    await db.commit()
    return True


async def get_packages(db: AsyncSession):
    result = await db.execute(
        select(PointsPackage).where(PointsPackage.is_active == True)
    )
    return result.scalars().all()
