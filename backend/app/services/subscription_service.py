import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import SubscriptionPlan, UserSubscription


async def get_plans(db: AsyncSession):
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.is_active == True)
    )
    return result.scalars().all()


async def get_active_subscription(db: AsyncSession, user_id: uuid.UUID) -> UserSubscription | None:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UserSubscription).where(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True,
            UserSubscription.end_date > now,
        )
    )
    return result.scalar_one_or_none()


async def is_member(db: AsyncSession, user_id: uuid.UUID) -> bool:
    sub = await get_active_subscription(db, user_id)
    return sub is not None


async def activate_subscription(db: AsyncSession, user_id: uuid.UUID, plan_id: uuid.UUID) -> UserSubscription:
    from datetime import timedelta

    # Deactivate old subscriptions
    old = await db.execute(
        select(UserSubscription).where(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True,
        )
    )
    for s in old.scalars().all():
        s.is_active = False

    plan = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = plan.scalar_one()

    now = datetime.now(timezone.utc)
    sub = UserSubscription(
        id=uuid.uuid4(),
        user_id=user_id,
        plan_id=plan_id,
        start_date=now,
        end_date=now + timedelta(days=plan.duration_days),
        is_active=True,
    )
    db.add(sub)
    await db.commit()
    return sub
