import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.card_key import CardKey
from app.models.rewrite import RewriteJob

router = APIRouter(prefix="/rewrite", tags=["history"])


@router.get("/history")
async def get_history(
    card_key: str = Query(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CardKey).where(CardKey.card_key == card_key))
    card = result.scalar_one_or_none()
    if not card:
        return {"items": [], "total": 0}

    offset = (page - 1) * per_page
    result = await db.execute(
        select(RewriteJob)
        .where(RewriteJob.card_key_id == card.id)
        .order_by(RewriteJob.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    jobs = result.scalars().all()

    count_result = await db.execute(
        select(func.count(RewriteJob.id)).where(RewriteJob.card_key_id == card.id)
    )
    total = count_result.scalar() or 0

    return {
        "items": [
            {
                "id": str(j.id), "mode": j.mode, "source_language": j.source_language,
                "input_text": j.input_text[:200], "output_text": (j.output_text or "")[:200],
                "word_count": j.word_count, "status": j.status,
                "created_at": j.created_at.isoformat(),
            }
            for j in jobs
        ],
        "total": total, "page": page, "per_page": per_page,
    }


@router.get("/history/{job_id}")
async def get_history_detail(
    job_id: uuid.UUID,
    card_key: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CardKey).where(CardKey.card_key == card_key))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(404, "记录不存在")

    result = await db.execute(
        select(RewriteJob).where(RewriteJob.id == job_id, RewriteJob.card_key_id == card.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "记录不存在")
    return {
        "id": str(job.id), "mode": job.mode, "source_language": job.source_language,
        "input_text": job.input_text, "output_text": job.output_text,
        "word_count": job.word_count, "status": job.status,
        "created_at": job.created_at.isoformat(),
    }
