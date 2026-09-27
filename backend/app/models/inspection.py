"""Inspection DB Model."""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.consumer import Consumer
    from app.models.alert import Alert


class Inspection(Base):
    """Field investigation report submitted by power utility inspector."""
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inspection_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    alert_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("alerts.alert_id", ondelete="SET NULL"), nullable=True, index=True)
    consumer_id: Mapped[str] = mapped_column(String(64), ForeignKey("consumers.consumer_id", ondelete="CASCADE"), index=True)
    inspector_id: Mapped[str] = mapped_column(String(64), nullable=False)
    
    # Outcomes: CONFIRMED_THEFT_BYPASS, METER_FAULT, GENUINE_USAGE_CHANGE, PREMISES_VACANT, REINSPECTION_REQUIRED
    audit_status: Mapped[str] = mapped_column(String(64), nullable=False)
    meter_serial: Mapped[str] = mapped_column(String(64), nullable=False)
    seal_number: Mapped[str] = mapped_column(String(64), nullable=False)
    observed_load: Mapped[float] = mapped_column(Float, default=0.0)
    inspector_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Evidence photo paths & metadata (stored as JSON string)
    photo_evidence_paths: Mapped[str] = mapped_column(Text, default="[]")
    photo_metadata: Mapped[str] = mapped_column(Text, default="[]")
    
    inspection_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    consumer: Mapped["Consumer"] = relationship("Consumer", back_populates="inspections")
    alert: Mapped[Optional["Alert"]] = relationship("Alert", back_populates="inspection")
