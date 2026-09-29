"""Whistleblower Community Tip DB Model."""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.core.database import Base


class WhistleblowerTip(Base):
    """Anonymous community tip reporting suspected power theft."""
    __tablename__ = "whistleblower_tips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tip_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    approximate_address: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transformer_hint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    correlated_consumer_ids: Mapped[str] = mapped_column(Text, default="[]")  # JSON list
    status: Mapped[str] = mapped_column(String(32), default="PENDING_REVIEW")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
