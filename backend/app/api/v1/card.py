from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.rewrite import RewriteRequest
from app.services.rewrite_service import rewrite_stream
from app.services.card_service import verify_card

router = APIRouter(prefix="/card", tags=["card"])


@router.get("/verify/{card_key}")
async def verify(card_key: str, db: AsyncSession = Depends(get_db)):
    return await verify_card(db, card_key)


@router.post("/rewrite/stream")
async def stream_rewrite(
    req: RewriteRequest,
    db: AsyncSession = Depends(get_db),
):
    return StreamingResponse(
        rewrite_stream(db, req.card_key or "", req.mode, req.source_language, req.input_text),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
