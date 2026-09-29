"""WattGuard AI - Uncertainty-Aware Loss & Inspection Prioritization Engine
Features 13–15, 16–18:
- Expected vs. Actual Delta E = max(0, E_expected - E_actual).
- 95% confidence bounds (mu +/- 1.96 * sigma).
- Financial loss using dynamic tariff rate slabs and regulatory penalties (25%).
- Inspection Net Yield ROI = Financial_Loss - Dispatch_Cost.
- Composite Priority Index (0–100) with operational weights (w1, w2, w3, w4).
- Deterministic action directives:
    PRIORITY_PHYSICAL_RAID, METER_CALIBRATION_TEST, REMOTE_FIRMWARE_AUDIT, WATCHLIST_7_DAY_MONITOR.
- Hazard safety evaluation (SECURITY_ESCORT_REQUIRED).
"""
import numpy as np
from typing import Dict, Tuple, Any, Optional
from app.core.config import settings


class LossEstimator:
    """Calculates uncertainty-aware unbilled energy, financial loss, net yield,
    composite priority index, and operational directives."""

    def __init__(self):
        pass

    @staticmethod
    def calculate_unbilled_energy(
        actual_kwh: float,
        baseline_mean_kwh: float,
        baseline_std_kwh: float
    ) -> Tuple[float, float, float]:
        """Calculates expected vs actual unbilled energy delta and 95% confidence interval bounds.
        
        Returns:
            Tuple of (delta_e_kwh, lower_bound_95_kwh, upper_bound_95_kwh)
        """
        delta_e = max(0.0, baseline_mean_kwh - actual_kwh)

        # 95% bounds on the delta based on baseline standard deviation
        margin = 1.96 * max(baseline_std_kwh, 0.05 * baseline_mean_kwh)
        lower_bound = max(0.0, delta_e - margin)
        upper_bound = delta_e + margin

        return round(delta_e, 3), round(lower_bound, 3), round(upper_bound, 3)

    @staticmethod
    def calculate_financial_loss(
        delta_e_kwh: float,
        lower_bound_kwh: float,
        upper_bound_kwh: float,
        tariff_class: str
    ) -> Tuple[float, float, float, float]:
        """Calculates financial loss across dynamic tariff slabs and applies regulatory penalties.
        
        Returns:
            Tuple of (base_loss, penalty_loss, total_loss, lower_bound_loss, upper_bound_loss)
        """
        rate = settings.TARIFF_RATES.get(tariff_class.upper(), 0.18)

        # Apply residential tiered slabs if applicable
        if tariff_class.upper() == "RESIDENTIAL":
            base_loss = 0.0
            remaining = delta_e_kwh
            prev_tier = 0.0
            for slab in settings.RESIDENTIAL_SLABS:
                tier_cap = slab["max_kwh"] - prev_tier
                slab_rate = slab["rate"]
                if remaining <= 0:
                    break
                kwh_in_slab = min(remaining, tier_cap)
                base_loss += kwh_in_slab * slab_rate
                remaining -= kwh_in_slab
                prev_tier = slab["max_kwh"]
        else:
            base_loss = delta_e_kwh * rate

        # 25% regulatory surcharge penalty for unauthorized extraction
        penalty_loss = base_loss * settings.REGULATORY_PENALTY_RATE
        total_loss = base_loss + penalty_loss

        # Bound calculations
        lower_loss = lower_bound_kwh * rate * (1.0 + settings.REGULATORY_PENALTY_RATE)
        upper_loss = upper_bound_kwh * rate * (1.0 + settings.REGULATORY_PENALTY_RATE)

        return (
            round(total_loss, 2),
            round(lower_loss, 2),
            round(upper_loss, 2),
            round(penalty_loss, 2)
        )

    @staticmethod
    def calculate_inspection_roi(
        total_loss_currency: float,
        dispatch_cost: Optional[float] = None
    ) -> float:
        """Calculates expected net yield from dispatch:
        Net Yield = Loss_financial - EstimatedDispatchCost
        """
        cost = dispatch_cost if dispatch_cost is not None else settings.ESTIMATED_DISPATCH_COST
        net_yield = total_loss_currency - cost
        return round(net_yield, 2)

    @staticmethod
    def compute_composite_priority(
        risk_score: float,
        anomaly_score: float,
        normalized_loss: float,
        confidence: float = 0.90,
        weights: Optional[Dict[str, float]] = None
    ) -> float:
        """Calculates composite Priority Index (0–100):
        Priority = 100 * [ w1(RiskScore) + w2(AnomalyScore) + w3(NormalizedLoss) + w4(Confidence) ]
        """
        w = weights or {
            "w1": settings.WEIGHT_RISK,
            "w2": settings.WEIGHT_ANOMALY,
            "w3": settings.WEIGHT_LOSS,
            "w4": settings.WEIGHT_CONFIDENCE
        }
        total_w = sum(w.values())
        if total_w <= 0:
            total_w = 1.0

        w1 = w.get("w1", 0.35) / total_w
        w2 = w.get("w2", 0.25) / total_w
        w3 = w.get("w3", 0.25) / total_w
        w4 = w.get("w4", 0.15) / total_w

        # Ensure bounded [0, 1] inputs
        r = float(np.clip(risk_score, 0.0, 1.0))
        a = float(np.clip(anomaly_score, 0.0, 1.0))
        l = float(np.clip(normalized_loss, 0.0, 1.0))
        c = float(np.clip(confidence, 0.0, 1.0))

        priority_0_1 = (w1 * r) + (w2 * a) + (w3 * l) + (w4 * c)
        priority_index = float(np.clip(priority_0_1 * 100.0, 0.0, 100.0))
        return round(priority_index, 2)

    @staticmethod
    def determine_action_directive(
        composite_priority: float,
        risk_score: float,
        anomaly_score: float,
        tamper_flags: str,
        total_loss: float,
        safety_hazard_history: bool = False
    ) -> Tuple[str, str, bool]:
        """Deterministic rule-engine mapping outputs to actionable recommendations:
        - PRIORITY_PHYSICAL_RAID
        - METER_CALIBRATION_TEST
        - REMOTE_FIRMWARE_AUDIT
        - WATCHLIST_7_DAY_MONITOR
        
        Returns:
            Tuple of (recommended_action, risk_tier, security_escort_required)
        """
        flags = tamper_flags.upper()
        escort_required = safety_hazard_history or (composite_priority > 85.0 and total_loss > 500.0)

        # Risk tier determination
        if composite_priority >= 75.0:
            risk_tier = "CRITICAL"
        elif composite_priority >= 50.0:
            risk_tier = "HIGH"
        elif composite_priority >= 25.0:
            risk_tier = "MEDIUM"
        else:
            risk_tier = "LOW"

        # Directive rules
        if (
            composite_priority >= 65.0
            or "REVERSE_CURRENT" in flags
            or "MAGNETIC_TAMPER" in flags
            or "NEUTRAL_TAMPER" in flags
            or total_loss >= 350.0
        ):
            action = "PRIORITY_PHYSICAL_RAID"
        elif "COVER_OPEN" in flags or (anomaly_score >= 0.65 and risk_score < 0.40):
            action = "REMOTE_FIRMWARE_AUDIT"
        elif composite_priority >= 40.0 or (risk_score >= 0.45 and total_loss >= 100.0):
            action = "METER_CALIBRATION_TEST"
        else:
            action = "WATCHLIST_7_DAY_MONITOR"

        return action, risk_tier, escort_required


loss_estimator_instance = LossEstimator()
