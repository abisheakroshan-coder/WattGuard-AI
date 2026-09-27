"""WattGuard AI - Economic Valuation & Inspection Prioritization Endpoints
/api/v1/prioritization:
- GET /manifest: Prioritized daily inspection manifest ranked by composite score.
- POST /adjust-weights: Update operational weighting factors (w1, w2, w3, w4).
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.config import settings
from app.models.alert import Alert
from app.models.consumer import Consumer
from app.schemas.alert_schema import (
    ManifestResponse,
    ManifestItem,
    WeightAdjustmentRequest,
    WeightAdjustmentResponse
)

router = APIRouter()


@router.get("/manifest", response_model=ManifestResponse, summary="Get Prioritized Daily Inspection Manifest")
async def get_daily_manifest(
    limit: int = Query(25, ge=1, le=100),
    tariff_class: Optional[str] = Query(None),
    feeder_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Returns prioritized daily inspection manifests ranked by composite score,
    including estimated unbilled kWh, revenue loss bounds, net yield, and action directives.
    """
    query = (
        select(Alert, Consumer)
        .join(Consumer, Alert.consumer_id == Consumer.consumer_id)
        .where(Alert.status == "ACTIVE")
    )

    if tariff_class:
        query = query.where(Consumer.tariff_class == tariff_class.upper())
    if feeder_id:
        query = query.where(Consumer.feeder_id == feeder_id)

    query = query.order_by(desc(Alert.composite_priority)).limit(limit)
    rows = (await db.execute(query)).all()

    items: List[ManifestItem] = []
    agg_unbilled = 0.0
    agg_revenue = 0.0
    agg_yield = 0.0
    raids_count = 0
    escorts_count = 0

    for rank, (alert, consumer) in enumerate(rows, start=1):
        agg_unbilled += alert.estimated_unbilled_kwh
        agg_revenue += alert.estimated_loss_currency
        agg_yield += alert.net_roi_yield

        if alert.recommended_action == "PRIORITY_PHYSICAL_RAID":
            raids_count += 1
        if alert.security_escort_required:
            escorts_count += 1

        primary_reason = (alert.plain_language_explanation or "").split("\n")[0] if alert.plain_language_explanation else "High composite theft risk score"

        items.append(ManifestItem(
            rank=rank,
            alert_id=alert.alert_id,
            consumer_id=consumer.consumer_id,
            tariff_class=consumer.tariff_class,
            feeder_id=consumer.feeder_id,
            transformer_id=consumer.transformer_id,
            latitude=consumer.latitude,
            longitude=consumer.longitude,
            composite_priority=alert.composite_priority,
            risk_tier=alert.risk_tier,
            estimated_unbilled_kwh=alert.estimated_unbilled_kwh,
            estimated_loss_currency=alert.estimated_loss_currency,
            loss_lower_bound_95=alert.loss_lower_bound_95,
            loss_upper_bound_95=alert.loss_upper_bound_95,
            net_roi_yield=alert.net_roi_yield,
            recommended_action=alert.recommended_action,
            security_escort_required=alert.security_escort_required,
            tamper_flags=alert.hardware_tamper_evidence,
            primary_reason=primary_reason
        ))

    total_dispatch_cost = len(items) * settings.ESTIMATED_DISPATCH_COST

    return ManifestResponse(
        manifest_date=datetime.now(timezone.utc),
        total_dispatches=len(items),
        aggregate_unbilled_kwh=round(agg_unbilled, 2),
        aggregate_expected_revenue_recovery=round(agg_revenue, 2),
        total_estimated_dispatch_cost=round(total_dispatch_cost, 2),
        aggregate_net_yield=round(agg_yield, 2),
        high_priority_raids_count=raids_count,
        security_escorts_required_count=escorts_count,
        items=items
    )


@router.post("/adjust-weights", response_model=WeightAdjustmentResponse, summary="Adjust Operational Prioritization Weights")
async def adjust_prioritization_weights(req: WeightAdjustmentRequest):
    """Updates operational weighting factors (w1_risk, w2_anomaly, w3_loss, w4_confidence) for ranking."""
    total = req.weight_risk + req.weight_anomaly + req.weight_loss + req.weight_confidence
    if total <= 0:
        raise HTTPException(status_code=400, detail="Sum of weights must be greater than zero.")

    # Normalize weights so they sum to 1.0
    settings.WEIGHT_RISK = round(req.weight_risk / total, 3)
    settings.WEIGHT_ANOMALY = round(req.weight_anomaly / total, 3)
    settings.WEIGHT_LOSS = round(req.weight_loss / total, 3)
    settings.WEIGHT_CONFIDENCE = round(req.weight_confidence / total, 3)

    return WeightAdjustmentResponse(
        message="Operational prioritization weights updated successfully.",
        updated_weights={
            "w1_risk": settings.WEIGHT_RISK,
            "w2_anomaly": settings.WEIGHT_ANOMALY,
            "w3_loss": settings.WEIGHT_LOSS,
            "w4_confidence": settings.WEIGHT_CONFIDENCE
        },
        weights_sum=round(settings.WEIGHT_RISK + settings.WEIGHT_ANOMALY + settings.WEIGHT_LOSS + settings.WEIGHT_CONFIDENCE, 3)
    )
