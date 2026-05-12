from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import subscription_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans")
async def get_plans(db: AsyncSession = Depends(get_db)):
    plans = await subscription_service.get_plans(db)
    return [
        {"id": str(p.id), "name": p.name, "price_yuan": p.price_yuan,
         "duration_days": p.duration_days, "max_word_count": p.max_word_count,
         "daily_limit": p.daily_limit}
        for p in plans
    ]


@router.get("/current")
async def current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await subscription_service.get_active_subscription(db, current_user.id)
    if not sub:
        return {"has_subscription": False}
    return {
        "has_subscription": True,
        "id": str(sub.id),
        "start_date": sub.start_date.isoformat(),
        "end_date": sub.end_date.isoformat(),
        "is_active": sub.is_active,
    }
