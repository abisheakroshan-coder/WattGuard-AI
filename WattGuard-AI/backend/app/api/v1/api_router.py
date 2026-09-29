"""WattGuard AI - Master API Router for v1 Endpoints."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    system,
    detection,
    alerts,
    prioritization,
    geospatial,
    field,
    governance
)

api_router = APIRouter()

api_router.include_router(system.router, prefix="/system", tags=["System & Ingestion"])
api_router.include_router(detection.router, prefix="/detection", tags=["Profiling & Anomaly Engine"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts & Explainability"])
api_router.include_router(prioritization.router, prefix="/prioritization", tags=["Economic Valuation & Prioritization"])
api_router.include_router(geospatial.router, prefix="/geospatial", tags=["Geospatial & Fleet Logistics"])
api_router.include_router(field.router, prefix="/field", tags=["Field Operations & Audit"])
api_router.include_router(governance.router, prefix="/governance", tags=["Model Governance & Active Learning"])
