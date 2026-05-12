import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CardKey(Base):
    __tablename__ = "card_keys"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    card_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    access_link: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    usage_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("1"))
    note: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
