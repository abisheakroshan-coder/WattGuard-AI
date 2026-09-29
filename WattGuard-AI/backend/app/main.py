from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api_router import api_router
from app.ml.dual_detector import dual_detector_instance

# Resolve web/dist directory (single-application unified deployment)
WEB_DIST_DIR = settings.BASE_DIR.parent / "web" / "dist"


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

# 1. Include master API router first (preserved under /api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)

# 2. Serve secure uploaded evidence photos locally
if settings.UPLOAD_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR.parent)), name="uploads")

# 3. Mount Vite compiled static assets (/assets)
if (WEB_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(WEB_DIST_DIR / "assets")), name="static_assets")


@app.get("/", include_in_schema=False)
async def root():
    """Serves the compiled React HUD frontend single-page application at root."""
    index_file = WEB_DIST_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(str(index_file))
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "api_documentation": "/docs",
        "redoc_documentation": "/redoc",
        "v1_endpoints": f"{settings.API_V1_STR}"
    }


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    """SPA fallback routing: serves index.html on deep links / page refreshes for client-side routing."""
    # Never intercept API or documentation routes
    if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
        raise HTTPException(status_code=404, detail="Not Found")

    # Check if a static file in web/dist exists (e.g. favicon.ico, vite.svg)
    requested_file = WEB_DIST_DIR / full_path
    if requested_file.is_file():
        return FileResponse(str(requested_file))

    # SPA Fallback: return index.html for client-side navigation
    index_file = WEB_DIST_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(str(index_file))

    raise HTTPException(status_code=404, detail="Frontend dist not found. Run 'npm run build' in /web.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

