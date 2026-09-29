"""WattGuard AI - Core Configuration Module
Defines settings, database connection URLs, operational weights, and tariff definitions.
"""
from pathlib import Path
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application runtime settings and configuration."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project metadata
    PROJECT_NAME: str = "WattGuard AI - AI-Assisted Power Theft & Unbilled Energy Decision-Support System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Paths (relative to backend root or workspace)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = BASE_DIR / "uploads" / "evidence"
    ARTIFACT_DIR: Path = BASE_DIR / "app" / "artifacts"

    # Database
    DATABASE_PATH: Path = BASE_DIR / "wattguard.db"
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR.as_posix()}/wattguard.db"
    SYNC_DATABASE_URL: str = f"sqlite:///{BASE_DIR.as_posix()}/wattguard.db"

    # Operational Weights for Composite Priority Index:
    # Priority = w1(RiskScore) + w2(AnomalyScore) + w3(NormalizedLoss) + w4(Confidence)
    WEIGHT_RISK: float = Field(default=0.35, ge=0.0, le=1.0)
    WEIGHT_ANOMALY: float = Field(default=0.25, ge=0.0, le=1.0)
    WEIGHT_LOSS: float = Field(default=0.25, ge=0.0, le=1.0)
    WEIGHT_CONFIDENCE: float = Field(default=0.15, ge=0.0, le=1.0)

    # Dispatch & Financial Parameters
    ESTIMATED_DISPATCH_COST: float = 50.0  # USD / dispatch
    REGULATORY_PENALTY_RATE: float = 0.25  # 25% surcharge on unbilled energy
    STANDARD_TECHNICAL_LOSS_RATE: float = 0.05  # 5% standard technical line loss

    # Tariff Rates per Class ($/kWh)
    TARIFF_RATES: Dict[str, float] = {
        "RESIDENTIAL": 0.14,
        "COMMERCIAL": 0.22,
        "INDUSTRIAL": 0.18,
        "AGRICULTURAL": 0.08
    }

    # Dynamic Tariff Rate Slabs (Residential tiered pricing)
    RESIDENTIAL_SLABS: List[Dict[str, float]] = [
        {"max_kwh": 100.0, "rate": 0.10},
        {"max_kwh": 300.0, "rate": 0.14},
        {"max_kwh": float("inf"), "rate": 0.20}
    ]

    # Security & Evidence
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    MAX_IMAGE_SIZE_MB: int = 15


settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
