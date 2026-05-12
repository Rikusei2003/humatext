import uuid
from datetime import date

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.usage import DailyUsage


async def get_today_usage(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Return today's rewrite count for the user."""
    today = date.today()
    result = await db.execute(
        select(DailyUsage).where(
            DailyUsage.user_id == user_id,
            DailyUsage.usage_date == today,
        )
    )
    record = result.scalar_one_or_none()
    return record.rewrite_count if record else 0


async def increment_usage(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Increment today's rewrite count. Creates record if first use today."""
    today = date.today()
    result = await db.execute(
        select(DailyUsage).where(
            DailyUsage.user_id == user_id,
            DailyUsage.usage_date == today,
        )
    )
    record = result.scalar_one_or_none()
    if record:
        record.rewrite_count += 1
    else:
        record = DailyUsage(
            id=uuid.uuid4(),
            user_id=user_id,
            usage_date=today,
            rewrite_count=1,
        )
        db.add(record)
    await db.commit()


def check_limits(daily_count: int, is_member: bool, word_count: int) -> tuple[bool, str | None]:
    """Return (allowed, error_message)."""
    if is_member:
        if word_count > settings.MEMBER_MAX_WORDS:
            return False, f"会员单次最多 {settings.MEMBER_MAX_WORDS} 字"
        return True, None
    if daily_count >= settings.FREE_DAILY_LIMIT:
        return False, "今日免费次数已用完，请使用积分兑换或升级会员"
    if word_count > settings.FREE_MAX_WORDS:
        return False, f"免费用户单次最多 {settings.FREE_MAX_WORDS} 字"
    return True, None
