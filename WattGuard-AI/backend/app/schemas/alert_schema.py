"""Pydantic v2 schemas for alerts, explainability, and manifest prioritization."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class EnergyPoint(BaseModel):
    """Timestamped actual vs expected energy point."""
    timestamp: datetime
    actual_kwh: float
    expected_kwh: float
    lower_95: float
    upper_95: float


class AlertSummary(BaseModel):
    """Summary schema for alert list items."""
    alert_id: str
    consumer_id: str
    tariff_class: str
    feeder_id: str
    transformer_id: str
    risk_score: float
    anomaly_score: float
    composite_priority: float
    risk_tier: str
    estimated_unbilled_kwh: float
    estimated_loss_currency: float
    loss_lower_bound_95: float
    loss_upper_bound_95: float
    net_roi_yield: float
    recommended_action: str
    security_escort_required: bool
    hardware_tamper_evidence: str
    status: str
    created_at: datetime
    monthly_pattern_analysis: Optional[Dict[str, Any]] = None


class AlertListResponse(BaseModel):
    """Paginated list of alerts."""
    total: int
    page: int
    page_size: int
    alerts: List[AlertSummary]


class AlertEvidenceResponse(BaseModel):
    """Deep explainability and evidentiary payload for an alert."""
    alert_id: str
    consumer_id: str
    tariff_class: str
    sanctioned_load_kw: float
    risk_tier: str
    composite_priority: float
    recommended_action: str
    security_escort_required: bool
    plain_language_explanations: List[str]
    shap_feature_importance: List[Dict[str, Any]]
    hardware_tamper_flags: str
    tamper_flag_interpreted: str
    feeder_mass_balance_loss_pct: float
    loss_summary: Dict[str, float]
    energy_curves: List[EnergyPoint]
    monthly_pattern_analysis: Optional[Dict[str, Any]] = None


class ManifestItem(BaseModel):
    """Daily prioritized inspection dispatch manifest item."""
    rank: int
    alert_id: str
    consumer_id: str
    tariff_class: str
    feeder_id: str
    transformer_id: str
    latitude: float
    longitude: float
    composite_priority: float
    risk_tier: str
    estimated_unbilled_kwh: float
    estimated_loss_currency: float
    loss_lower_bound_95: float
    loss_upper_bound_95: float
    net_roi_yield: float
    recommended_action: str
    security_escort_required: bool
    tamper_flags: str
    primary_reason: str
    monthly_pattern_analysis: Optional[Dict[str, Any]] = None


class ManifestResponse(BaseModel):
    """Daily manifest response."""
    manifest_date: datetime
    total_dispatches: int
    aggregate_unbilled_kwh: float
    aggregate_expected_revenue_recovery: float
    total_estimated_dispatch_cost: float
    aggregate_net_yield: float
    high_priority_raids_count: int
    security_escorts_required_count: int
    items: List[ManifestItem]


class WeightAdjustmentRequest(BaseModel):
    """Operational weighting factor update request."""
    weight_risk: float = Field(..., ge=0.0, le=1.0)
    weight_anomaly: float = Field(..., ge=0.0, le=1.0)
    weight_loss: float = Field(..., ge=0.0, le=1.0)
    weight_confidence: float = Field(..., ge=0.0, le=1.0)


class WeightAdjustmentResponse(BaseModel):
    """Operational weighting factor update confirmation."""
    message: str
    updated_weights: Dict[str, float]
    weights_sum: float
