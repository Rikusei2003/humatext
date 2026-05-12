from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.rewrite import RewriteRequest
from app.services.rewrite_service import rewrite_stream

router = APIRouter(prefix="/rewrite", tags=["rewrite"])


@router.post("/stream")
async def stream_rewrite(
    req: RewriteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return StreamingResponse(
        rewrite_stream(db, current_user.id, req.mode, req.source_language, req.input_text, req.use_points),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
