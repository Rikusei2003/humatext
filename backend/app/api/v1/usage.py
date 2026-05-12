from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.usage_service import get_today_usage
from app.config import settings

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/today")
async def today_usage(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    count = await get_today_usage(db, current_user.id)
    return {
        "used": count,
        "limit": settings.FREE_DAILY_LIMIT,
        "remaining": max(0, settings.FREE_DAILY_LIMIT - count),
    }
