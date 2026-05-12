import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.admin import Admin
from app.models.card_key import CardKey
from app.models.usage import DailyUsage
from app.models.rewrite import RewriteJob


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_admin_token(admin_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=8)
    payload = {"sub": admin_id, "exp": expire, "type": "admin"}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_admin_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


async def create_default_admin(db: AsyncSession):
    result = await db.execute(select(Admin).limit(1))
    if not result.scalar_one_or_none():
        admin = Admin(
            id=uuid.uuid4(),
            username="admin",
            password_hash=hash_password("admin123"),
        )
        db.add(admin)
        await db.commit()


async def authenticate_admin(db: AsyncSession, username: str, password: str) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.username == username))
    admin = result.scalar_one_or_none()
    if not admin or not verify_password(password, admin.password_hash):
        return None
    return admin


async def create_card(db: AsyncSession, usage_limit: int = 10, note: str | None = None) -> dict:
    card = CardKey(
        id=uuid.uuid4(),
        card_key=secrets.token_hex(6),
        usage_limit=usage_limit,
        note=note,
        access_link="",  # will be set below
    )
    card.access_link = f"/access/{card.card_key}"
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return {
        "id": str(card.id),
        "card_key": card.card_key,
        "access_link": card.access_link,
        "usage_limit": card.usage_limit,
        "usage_count": card.usage_count,
        "is_active": card.is_active,
        "note": card.note,
        "created_at": card.created_at.isoformat(),
    }


async def list_cards(db: AsyncSession, page: int = 1, per_page: int = 50):
    offset = (page - 1) * per_page
    result = await db.execute(
        select(CardKey).order_by(CardKey.created_at.desc()).offset(offset).limit(per_page)
    )
    cards = result.scalars().all()
    total = (await db.execute(select(func.count(CardKey.id)))).scalar() or 0
    return {
        "items": [
            {
                "id": str(c.id), "card_key": c.card_key, "access_link": c.access_link,
                "usage_limit": c.usage_limit, "usage_count": c.usage_count,
                "remaining": max(0, c.usage_limit - c.usage_count),
                "is_active": c.is_active, "note": c.note,
                "created_at": c.created_at.isoformat(),
                "last_used_at": c.last_used_at.isoformat() if c.last_used_at else None,
            }
            for c in cards
        ],
        "total": total, "page": page, "per_page": per_page,
    }


async def update_card(db: AsyncSession, card_id: uuid.UUID, usage_limit: int | None = None, is_active: bool | None = None):
    result = await db.execute(select(CardKey).where(CardKey.id == card_id))
    card = result.scalar_one_or_none()
    if not card:
        return None
    if usage_limit is not None:
        card.usage_limit = usage_limit
    if is_active is not None:
        card.is_active = is_active
    await db.commit()
    return {"id": str(card.id), "card_key": card.card_key, "usage_limit": card.usage_limit, "is_active": card.is_active}


async def delete_card(db: AsyncSession, card_id: uuid.UUID) -> bool:
    result = await db.execute(select(CardKey).where(CardKey.id == card_id))
    card = result.scalar_one_or_none()
    if not card:
        return False
    await db.delete(card)
    await db.commit()
    return True


async def get_stats(db: AsyncSession):
    total_cards = (await db.execute(select(func.count(CardKey.id)))).scalar() or 0
    active_cards = (await db.execute(
        select(func.count(CardKey.id)).where(CardKey.is_active == True)
    )).scalar() or 0
    total_rewrites = (await db.execute(select(func.count(RewriteJob.id)))).scalar() or 0
    today = datetime.now(timezone.utc).date()
    today_result = await db.execute(
        select(func.count(RewriteJob.id)).where(func.date(RewriteJob.created_at) == today)
    )
    today_rewrites = today_result.scalar() or 0
    return {
        "total_cards": total_cards,
        "active_cards": active_cards,
        "total_rewrites": total_rewrites,
        "today_rewrites": today_rewrites,
    }
