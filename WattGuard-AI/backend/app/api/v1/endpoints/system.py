"""WattGuard AI - System & Dataset Ingestion Endpoints
/api/v1/system:
- POST /ingest/dataset: Triggers dataset inspection and database ingestion.
- GET /health: System health, DB connection, model versions, and loaded artifacts.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any

from app.core.database import get_db
from app.core.config import settings
from app.core.etl import etl_manager
from app.ml.dual_detector import dual_detector_instance

router = APIRouter()


@router.post("/ingest/dataset", summary="Trigger Automated Dataset Ingestion & Validation")
async def trigger_dataset_ingestion(
    max_consumers: int = 32,
    readings_per_consumer: int = 1440,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Scans `./data/`, inspects schema, normalizes time-series readings,
    populates consumers and meter readings into the database, and trains baseline ML models.
    """
    try:
        # Run inspection
        inspection_report = etl_manager.inspect_datasets()

        # Run ingestion
        result = await etl_manager.ingest_into_database(
            session=db,
            max_consumers=max_consumers,
            readings_per_consumer=readings_per_consumer
        )
        result["inspection_report"] = inspection_report
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/health", summary="System Health & Model Status")
async def get_system_health(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Returns database connection status, active model versions, and artifact metadata."""
    # Test DB connection
    db_connected = False
    try:
        res = await db.execute(text("SELECT 1"))
        db_connected = bool(res.scalar() == 1)
    except Exception:
        db_connected = False

    model_loaded = (
        dual_detector_instance.supervised_model is not None
        and dual_detector_instance.isolation_forest is not None
    )

    return {
        "status": "HEALTHY" if db_connected else "DEGRADED",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_connected": db_connected,
        "model_artifacts_loaded": model_loaded,
        "active_model_metadata": dual_detector_instance.metadata,
        "operational_weights": {
            "w1_risk": settings.WEIGHT_RISK,
            "w2_anomaly": settings.WEIGHT_ANOMALY,
            "w3_loss": settings.WEIGHT_LOSS,
            "w4_confidence": settings.WEIGHT_CONFIDENCE
        }
    }
