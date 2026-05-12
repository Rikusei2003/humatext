import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card_key import CardKey


async def verify_card(db: AsyncSession, card_key: str) -> dict:
    result = await db.execute(
        select(CardKey).where(CardKey.card_key == card_key)
    )
    card = result.scalar_one_or_none()
    if not card:
        return {"valid": False}
    return {
        "valid": True,
        "card_key": card.card_key,
        "usage_limit": card.usage_limit,
        "usage_count": card.usage_count,
        "remaining": max(0, card.usage_limit - card.usage_count),
        "is_active": card.is_active,
    }


async def get_card(db: AsyncSession, card_key: str) -> CardKey | None:
    result = await db.execute(
        select(CardKey).where(CardKey.card_key == card_key)
    )
    return result.scalar_one_or_none()


async def consume(db: AsyncSession, card_key_id: uuid.UUID) -> bool:
    """Increment usage_count. Returns True if within limit."""
    result = await db.execute(select(CardKey).where(CardKey.id == card_key_id))
    card = result.scalar_one_or_none()
    if not card or not card.is_active or card.usage_count >= card.usage_limit:
        return False
    card.usage_count += 1
    card.last_used_at = datetime.now(timezone.utc)
    await db.commit()
    return True
