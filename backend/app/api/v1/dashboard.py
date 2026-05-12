from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.rewrite import RewriteJob
from app.models.usage import DailyUsage
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Total rewrites
    total_result = await db.execute(
        select(func.count(RewriteJob.id)).where(RewriteJob.user_id == current_user.id)
    )
    total_rewrites = total_result.scalar() or 0

    # Total words
    words_result = await db.execute(
        select(func.coalesce(func.sum(RewriteJob.word_count), 0)).where(
            RewriteJob.user_id == current_user.id
        )
    )
    total_words = words_result.scalar() or 0

    # This month rewrites
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_result = await db.execute(
        select(func.count(RewriteJob.id)).where(
            RewriteJob.user_id == current_user.id,
            RewriteJob.created_at >= month_start,
        )
    )
    month_rewrites = month_result.scalar() or 0

    # Recent activity (last 7 days)
    from datetime import timedelta
    week_ago = now - timedelta(days=7)
    daily_result = await db.execute(
        select(DailyUsage.usage_date, func.sum(DailyUsage.rewrite_count))
        .where(DailyUsage.user_id == current_user.id, DailyUsage.usage_date >= week_ago.date())
        .group_by(DailyUsage.usage_date)
        .order_by(DailyUsage.usage_date)
    )
    daily_data = [{"date": str(row[0]), "count": row[1]} for row in daily_result.all()]

    return {
        "total_rewrites": total_rewrites,
        "total_words": total_words,
        "month_rewrites": month_rewrites,
        "daily_activity": daily_data,
    }
