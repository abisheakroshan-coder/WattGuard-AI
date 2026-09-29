"""Pydantic v2 schemas for detection, baseline profiling, and changepoints."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class EvaluationRequest(BaseModel):
    """Request schema for evaluating a single consumer."""
    model_config = ConfigDict(extra="ignore")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    inject_feeder_loss: bool = True


class ChangepointRecord(BaseModel):
    """Detected step-down or changepoint event."""
    timestamp: datetime
    p_value: float
    drop_percentage: float
    pre_mean_kwh: float
    post_mean_kwh: float
    severity: str


class RiskTrajectoryRecord(BaseModel):
    """Multi-week risk progression tracking."""
    window_name: str
    start_time: datetime
    end_time: datetime
    mean_consumption: float
    drop_from_baseline_pct: float
    risk_state: str  # LOW, MEDIUM, HIGH, CRITICAL


class ConsumerEvaluationResponse(BaseModel):
    """Dual-model evaluation result for a consumer."""
    consumer_id: str
    tariff_class: str
    sanctioned_load_kw: float
    feeder_id: str
    transformer_id: str
    phase: str
    evaluation_window_hours: int
    mean_actual_kwh: float
    mean_baseline_kwh: float
    dtw_distance: float
    peer_cohort_zscore: float
    is_vacant_flag: bool
    solar_suppressed: bool
    
    # Dual Model Scores
    supervised_theft_probability: float = Field(..., ge=0.0, le=1.0)
    isolation_forest_anomaly_score: float = Field(..., ge=0.0, le=1.0)
    feeder_unaccounted_loss_factor: float = Field(..., ge=0.0, le=1.0)
    composite_priority: float = Field(..., ge=0.0, le=100.0)
    risk_tier: str  # LOW, MEDIUM, HIGH, CRITICAL

    # Financial & Loss Estimation
    estimated_unbilled_kwh: float
    estimated_revenue_loss: float
    loss_lower_bound_95: float
    loss_upper_bound_95: float
    net_roi_yield: float

    # Directives & Explanations
    recommended_action: str
    security_escort_required: bool
    hardware_tamper_flags: str
    top_explanations: List[str]
    alert_generated: bool
    alert_id: Optional[str] = None
    monthly_pattern_analysis: Optional[Dict[str, Any]] = None


class BatchRunRequest(BaseModel):
    """Batch run scoring request across feeder or zone."""
    feeder_id: Optional[str] = None
    transformer_id: Optional[str] = None
    tariff_class: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)


class BatchRunResponse(BaseModel):
    """Batch run execution summary."""
    evaluated_meters_count: int
    alerts_generated_count: int
    total_unbilled_kwh: float
    total_estimated_loss_currency: float
    critical_alerts_count: int
    high_alerts_count: int
    medium_alerts_count: int
    low_alerts_count: int
    execution_time_seconds: float


class BaselinePoint(BaseModel):
    """Baseline diurnal profile point."""
    hour_of_day: int
    mean_kwh: float
    std_kwh: float
    lower_95: float
    upper_95: float


class BaselineProfileResponse(BaseModel):
    """Detailed consumer historical baseline profile."""
    consumer_id: str
    tariff_class: str
    sanctioned_load_kw: float
    total_readings: int
    baseline_window_days: int
    diurnal_curve_24h: List[BaselinePoint]
    overall_mean_kwh: float
    overall_variance: float
    dtw_shape_distance_30d: float
    dtw_shape_distance_90d: float
    is_vacant_profile: bool


class ChangepointsResponse(BaseModel):
    """Historical changepoints and step-down timestamps."""
    consumer_id: str
    total_changepoints_detected: int
    changepoints: List[ChangepointRecord]
    risk_trajectories: List[RiskTrajectoryRecord]
