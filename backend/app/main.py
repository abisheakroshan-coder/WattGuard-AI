"""WattGuard AI - Master FastAPI Application Entrypoint
AI-Assisted Power Theft & Unbilled Energy Decision-Support System
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api_router import api_router
from app.ml.dual_detector import dual_detector_instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager: runs DB schema creation and loads ML models on startup."""
    print("[WattGuard AI] Initializing database schema...")
    await init_db()
    print("[WattGuard AI] Loading ML model artifacts...")
    loaded = dual_detector_instance.load_models()
    if loaded:
        print("[WattGuard AI] Model artifacts successfully loaded from disk.")
    else:
        print("[WattGuard AI] Model artifacts not found; models will train upon first dataset ingestion.")
    yield
    print("[WattGuard AI] Shutting down application gracefully.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI decision-support system for smart meter power theft detection, "
                "economic valuation, geospatial fleet dispatch optimization, and closed-loop active learning.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include master API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve secure uploaded evidence photos locally
if settings.UPLOAD_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR.parent)), name="uploads")


@app.get("/", tags=["Root"])
async def root():
    """Root metadata and system information endpoint."""
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "api_documentation": "/docs",
        "redoc_documentation": "/redoc",
        "v1_endpoints": f"{settings.API_V1_STR}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
