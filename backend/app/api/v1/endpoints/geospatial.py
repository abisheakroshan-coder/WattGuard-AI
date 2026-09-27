"""WattGuard AI - Geospatial & Fleet Route Optimization Endpoints
/api/v1/geospatial:
- GET /hotspots: Geo-clustered theft hotspots via DBSCAN.
- POST /route-optimize: Heuristic TSP vehicle route from inspector coordinates through alerts.
- GET /feeder-vulnerability: Feeder-level vulnerability index rankings.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.alert import Alert
from app.models.consumer import Consumer
from app.models.meter_reading import MeterReading
from app.schemas.field_schema import (
    HotspotsResponse,
    HotspotCluster,
    RouteOptimizeRequest,
    RouteOptimizeResponse,
    FeederVulnerabilityResponse,
    FeederVulnerabilityItem
)
from app.ml.geospatial_cluster import geospatial_cluster_engine
from app.ml.route_optimizer import route_optimizer_instance
from app.core.etl import FEEDER_TOPOLOGY

router = APIRouter()


@router.get("/hotspots", response_model=HotspotsResponse, summary="Detect Geographic Theft Hotspots")
async def get_theft_hotspots(
    eps_km: float = Query(1.5, ge=0.2, le=10.0, description="DBSCAN neighborhood radius in km"),
    min_samples: int = Query(2, ge=2, le=20, description="Minimum alerts to form a cluster"),
    db: AsyncSession = Depends(get_db)
):
    """Runs DBSCAN clustering on GPS coordinates of active alerts to detect geographic theft clusters."""
    query = (
        select(Alert, Consumer)
        .join(Consumer, Alert.consumer_id == Consumer.consumer_id)
        .where(Alert.status == "ACTIVE")
    )
    rows = (await db.execute(query)).all()

    alert_records = []
    for alert, consumer in rows:
        alert_records.append({
            "alert_id": alert.alert_id,
            "consumer_id": consumer.consumer_id,
            "latitude": consumer.latitude,
            "longitude": consumer.longitude,
            "unbilled_kwh": alert.estimated_unbilled_kwh,
            "loss_currency": alert.estimated_loss_currency,
            "feeder_id": consumer.feeder_id
        })

    raw_clusters = geospatial_cluster_engine.detect_hotspots(
        alert_records=alert_records,
        eps_km=eps_km,
        min_samples=min_samples
    )

    clusters = [HotspotCluster(**c) for c in raw_clusters]
    total_consumers = sum(c.consumer_count for c in clusters)
    total_unbilled = sum(c.total_unbilled_kwh for c in clusters)

    return HotspotsResponse(
        total_hotspots_detected=len(clusters),
        total_clustered_consumers=total_consumers,
        aggregate_unbilled_kwh=round(total_unbilled, 2),
        hotspots=clusters
    )


@router.post("/route-optimize", response_model=RouteOptimizeResponse, summary="Optimize Inspection Fleet Route (TSP)")
async def optimize_inspection_route(
    req: RouteOptimizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Given inspector start coordinates and an array of alert_ids,
    returns the ordered TSP inspection route with distances and arrival estimates.
    """
    if not req.alert_ids:
        raise HTTPException(status_code=400, detail="Must provide at least one alert_id for route planning.")

    query = (
        select(Alert, Consumer)
        .join(Consumer, Alert.consumer_id == Consumer.consumer_id)
        .where(Alert.alert_id.in_(req.alert_ids))
    )
    rows = (await db.execute(query)).all()
    if not rows:
        raise HTTPException(status_code=404, detail="None of the specified alert_ids were found.")

    stops = []
    for alert, consumer in rows:
        stops.append({
            "alert_id": alert.alert_id,
            "consumer_id": consumer.consumer_id,
            "latitude": consumer.latitude,
            "longitude": consumer.longitude,
            "recommended_action": alert.recommended_action,
            "address_or_tag": f"Feeder {consumer.feeder_id} - Tx {consumer.transformer_id} ({consumer.consumer_id})"
        })

    result = route_optimizer_instance.optimize_route(
        inspector_start=(req.inspector_start_latitude, req.inspector_start_longitude),
        stops=stops
    )
    return RouteOptimizeResponse(**result)


@router.get("/feeder-vulnerability", response_model=FeederVulnerabilityResponse, summary="Get Feeder Vulnerability Rankings")
async def get_feeder_vulnerability(db: AsyncSession = Depends(get_db)):
    """Computes Feeder Vulnerability Index per transformer/substation zone."""
    # Group consumers by feeder
    feeders_stats = []
    for topo in FEEDER_TOPOLOGY:
        fid = topo["feeder_id"]
        tx_count = len(topo["transformers"])

        # Count active meters
        meters_count = (await db.scalar(
            select(func.count(Consumer.consumer_id)).where(Consumer.feeder_id == fid)
        )) or 0

        # Count high-risk meters
        high_risk_count = (await db.scalar(
            select(func.count(Alert.id))
            .join(Consumer, Alert.consumer_id == Consumer.consumer_id)
            .where(Consumer.feeder_id == fid, Alert.risk_tier.in_(["HIGH", "CRITICAL"]))
        )) or 0

        # Sum unbilled energy
        loss_kwh = (await db.scalar(
            select(func.sum(Alert.estimated_unbilled_kwh))
            .join(Consumer, Alert.consumer_id == Consumer.consumer_id)
            .where(Consumer.feeder_id == fid)
        )) or 0.0

        total_kwh = max(1000.0, meters_count * 350.0)

        feeders_stats.append({
            "feeder_id": fid,
            "transformer_count": tx_count,
            "active_meter_count": meters_count,
            "high_risk_meter_count": high_risk_count,
            "unaccounted_feeder_loss_kwh": float(loss_kwh),
            "total_feeder_kwh": float(total_kwh)
        })

    vuln_data = geospatial_cluster_engine.compute_feeder_vulnerabilities(feeders_stats)
    return FeederVulnerabilityResponse(feeders=[FeederVulnerabilityItem(**f) for f in vuln_data])
