import uuid

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateCardRequest(BaseModel):
    usage_limit: int = 10
    count: int = 1
    note: str | None = None


async def get_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        payload = admin_service.decode_admin_token(credentials.credentials)
        if payload.get("type") != "admin":
            raise HTTPException(401)
    except JWTError:
        raise HTTPException(401, "Invalid token")


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    admin = await admin_service.authenticate_admin(db, req.username, req.password)
    if not admin:
        raise HTTPException(401, "用户名或密码错误")
    token = admin_service.create_admin_token(str(admin.id))
    return {"token": token, "token_type": "bearer"}


@router.post("/cards")
async def create_cards(
    req: CreateCardRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin),
):
    cards = []
    for _ in range(req.count):
        card = await admin_service.create_card(db, req.usage_limit, req.note)
        cards.append(card)
    return {"cards": cards}


@router.get("/cards")
async def list_cards(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin),
):
    return await admin_service.list_cards(db, page, per_page)


@router.patch("/cards/{card_id}")
async def update_card(
    card_id: uuid.UUID,
    usage_limit: int | None = Query(None, ge=1),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin),
):
    result = await admin_service.update_card(db, card_id, usage_limit, is_active)
    if not result:
        raise HTTPException(404, "兑换码不存在")
    return result


@router.delete("/cards/{card_id}")
async def delete_card(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin),
):
    ok = await admin_service.delete_card(db, card_id)
    if not ok:
        raise HTTPException(404, "兑换码不存在")
    return {"status": "deleted"}


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin),
):
    return await admin_service.get_stats(db)
