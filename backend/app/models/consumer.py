"""Consumer DB Model."""
from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.meter_reading import MeterReading
    from app.models.alert import Alert
    from app.models.inspection import Inspection


class Consumer(Base):
    """Consumer entity representing an electricity customer connection and meter."""
    __tablename__ = "consumers"

    consumer_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    sanctioned_load_kw: Mapped[float] = mapped_column(Float, nullable=False)
    tariff_class: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # RESIDENTIAL, COMMERCIAL, INDUSTRIAL, AGRICULTURAL
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    feeder_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    transformer_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    phase: Mapped[str] = mapped_column(String(8), nullable=False)  # R, Y, B or A, B, C
    has_solar: Mapped[bool] = mapped_column(Boolean, default=False)
    safety_hazard_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    security_escort_required: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    readings: Mapped[List["MeterReading"]] = relationship("MeterReading", back_populates="consumer", cascade="all, delete-orphan")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="consumer", cascade="all, delete-orphan")
    inspections: Mapped[List["Inspection"]] = relationship("Inspection", back_populates="consumer", cascade="all, delete-orphan")
