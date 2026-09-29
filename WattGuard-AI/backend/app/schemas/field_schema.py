"""Pydantic v2 schemas for field operations, geospatial logistics, tips, and governance."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# --- Field Inspections ---
class InspectionSubmitRequest(BaseModel):
    """Field investigation submission from inspector."""
    consumer_id: str
    alert_id: Optional[str] = None
    inspector_id: str
    audit_status: str = Field(
        ...,
        description="CONFIRMED_THEFT_BYPASS, METER_FAULT, GENUINE_USAGE_CHANGE, PREMISES_VACANT, REINSPECTION_REQUIRED"
    )
    meter_serial: str
    seal_number: str
    observed_load: float = Field(default=0.0, ge=0.0)
    inspector_notes: Optional[str] = None
    inspection_timestamp: Optional[datetime] = None


class InspectionSubmitResponse(BaseModel):
    """Inspection submission confirmation."""
    inspection_id: str
    consumer_id: str
    alert_id: Optional[str]
    audit_status: str
    status: str
    message: str
    timestamp: datetime


class EvidenceUploadResponse(BaseModel):
    """File evidence upload confirmation."""
    inspection_id: str
    file_id: str
    file_path: str
    file_size_bytes: int
    content_type: str
    captured_metadata: Dict[str, Any]
    message: str


class DisputeDossierResponse(BaseModel):
    """Complete structured machine-readable dispute dossier."""
    consumer_id: str
    tariff_class: str
    sanctioned_load_kw: float
    meter_serial: Optional[str]
    feeder_id: str
    transformer_id: str
    total_unbilled_energy_kwh: float
    assessed_financial_loss: float
    confidence_interval_95: Dict[str, float]
    regulatory_surcharge: float
    net_claim_amount: float
    alert_history: List[Dict[str, Any]]
    field_audit_record: Optional[Dict[str, Any]]
    evidentiary_photos: List[Dict[str, Any]]
    telemetry_summary: Dict[str, Any]
    dossier_generated_at: datetime
    legal_certification_hash: str


# --- Geospatial Logistics ---
class HotspotCluster(BaseModel):
    """Geographic cluster of high-theft meters."""
    cluster_id: int
    centroid_latitude: float
    centroid_longitude: float
    radius_meters: float
    consumer_count: int
    total_unbilled_kwh: float
    total_revenue_loss: float
    feeder_id: str
    vulnerability_rating: str  # EXTREME, HIGH, ELEVATED, MODERATE
    consumer_ids: List[str]


class HotspotsResponse(BaseModel):
    """Hotspot detection response."""
    total_hotspots_detected: int
    total_clustered_consumers: int
    aggregate_unbilled_kwh: float
    hotspots: List[HotspotCluster]


class RouteOptimizeRequest(BaseModel):
    """Inspector routing TSP request."""
    inspector_start_latitude: float
    inspector_start_longitude: float
    alert_ids: List[str]


class RouteWaypoint(BaseModel):
    """Ordered stop in inspection route."""
    sequence: int
    alert_id: Optional[str]
    consumer_id: Optional[str]
    latitude: float
    longitude: float
    address_or_tag: str
    recommended_action: str
    distance_from_prev_km: float
    cumulative_distance_km: float
    estimated_arrival_minutes: float


class RouteOptimizeResponse(BaseModel):
    """Optimal TSP inspection route."""
    total_stops: int
    total_distance_km: float
    estimated_transit_minutes: float
    estimated_inspection_minutes: float
    estimated_total_tour_minutes: float
    ordered_waypoints: List[RouteWaypoint]


class FeederVulnerabilityItem(BaseModel):
    """Feeder / Transformer zone vulnerability metrics."""
    feeder_id: str
    transformer_count: int
    active_meter_count: int
    high_risk_meter_count: int
    unaccounted_feeder_loss_kwh: float
    unaccounted_feeder_loss_pct: float
    vulnerability_index_score: float  # 0.0 - 100.0
    vulnerability_tier: str  # CRITICAL, HIGH, MODERATE, LOW


class FeederVulnerabilityResponse(BaseModel):
    """Feeder vulnerability ranking response."""
    feeders: List[FeederVulnerabilityItem]


# --- Governance & Whistleblower Tips ---
class WhistleblowerTipRequest(BaseModel):
    """Tip intake request."""
    description: str
    approximate_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    transformer_hint: Optional[str] = None


class WhistleblowerTipResponse(BaseModel):
    """Tip intake response with spatial correlation."""
    tip_id: str
    message: str
    correlated_meter_count: int
    flagged_candidates: List[Dict[str, Any]]
    created_at: datetime


class ModelRetrainResponse(BaseModel):
    """Asynchronous retraining job dispatch response."""
    job_id: str
    status: str
    message: str
    timestamp: datetime


class ModelMetricsResponse(BaseModel):
    """Model governance metrics and drift curves."""
    model_version: str
    active_model_type: str
    training_sample_count: int
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    confusion_matrix: Dict[str, int]
    feature_importances: Dict[str, float]
    drift_status: str
    last_retrained_at: Optional[datetime]
