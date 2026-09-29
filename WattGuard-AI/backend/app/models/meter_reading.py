"""Meter Reading DB Model."""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.consumer import Consumer


class MeterReading(Base):
    """Time-series smart meter consumption record."""
    __tablename__ = "meter_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    consumer_id: Mapped[str] = mapped_column(String(64), ForeignKey("consumers.consumer_id", ondelete="CASCADE"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    energy_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    submeter_hvac_kwh: Mapped[float] = mapped_column(Float, default=0.0)
    submeter_lighting_kwh: Mapped[float] = mapped_column(Float, default=0.0)
    tamper_flags: Mapped[str] = mapped_column(String(64), default="NORMAL")  # NORMAL, REVERSE_CURRENT, COVER_OPEN, NEUTRAL_TAMPER, MAGNETIC_TAMPER
    is_theft_ground_truth: Mapped[bool] = mapped_column(Boolean, default=False)
    theft_type: Mapped[str] = mapped_column(String(32), default="Normal")

    consumer: Mapped["Consumer"] = relationship("Consumer", back_populates="readings")
