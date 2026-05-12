from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.points import PointsBalanceResponse, PointsRedeemResponse
from app.services import points_service

router = APIRouter(prefix="/points", tags=["points"])


@router.get("/balance", response_model=PointsBalanceResponse)
async def get_balance(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    balance = await points_service.get_balance(db, current_user.id)
    return PointsBalanceResponse(balance=balance)


@router.post("/daily-login")
async def daily_login(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    earned = await points_service.earn_daily_login(db, current_user.id)
    balance = await points_service.get_balance(db, current_user.id)
    return {"earned": earned, "balance": balance}


@router.get("/transactions")
async def get_transactions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    txns = await points_service.get_transactions(db, current_user.id)
    return [
        {
            "id": str(t.id),
            "amount": t.amount,
            "transaction_type": t.transaction_type,
            "description": t.description,
            "created_at": t.created_at.isoformat(),
        }
        for t in txns
    ]


@router.post("/redeem", response_model=PointsRedeemResponse)
async def redeem(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await points_service.spend_rewrite(db, current_user.id)
    balance = await points_service.get_balance(db, current_user.id)
    if success:
        return PointsRedeemResponse(success=True, message="兑换成功，获得 1 次额外改写", balance=balance)
    return PointsRedeemResponse(success=False, message="积分不足", balance=balance)


@router.get("/packages")
async def get_packages(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    packages = await points_service.get_packages(db)
    return [
        {"id": str(p.id), "name": p.name, "points_amount": p.points_amount, "price_yuan": p.price_yuan}
        for p in packages
    ]
