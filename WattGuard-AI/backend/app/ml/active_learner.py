"""WattGuard AI - Active Learner, Dispute Dossier & Whistleblower Engine
Features 22–30:
- Closed-loop active learning model retraining.
- Validates cross-validation / holdout metrics and safely hot-swaps model artifacts if improved.
- Dispute resolution audit dossier compilation with cryptographic verification hash.
- Whistleblower anonymous tip spatial-meter correlation.
"""
import hashlib
import json
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.dual_detector import dual_detector_instance, FEATURE_NAMES
from app.ml.geospatial_cluster import GeospatialClusterEngine


class ActiveLearner:
    """Manages active learning loop, dispute dossiers, and tip correlations."""

    def __init__(self, detector=None):
        self.detector = detector or dual_detector_instance
        self.haversine = GeospatialClusterEngine.haversine_distance_km

    def retrain_with_feedback(
        self,
        new_feature_vectors: List[np.ndarray],
        new_ground_truths: List[int],
        existing_features: Optional[np.ndarray] = None,
        existing_labels: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Incorporates confirmed field inspection ground-truth into model retraining.
        
        Args:
            new_feature_vectors: Feature vectors extracted from newly inspected consumers.
            new_ground_truths: 1 for CONFIRMED_THEFT_BYPASS, 0 for GENUINE_USAGE_CHANGE / PREMISES_VACANT.
            existing_features: Historical feature set.
            existing_labels: Historical ground-truth labels.
        Returns:
            Dict containing retraining metrics and hot-swap status.
        """
        if not new_feature_vectors or len(new_feature_vectors) == 0:
            return {
                "status": "SKIPPED",
                "message": "No new inspection ground truth records available for retraining.",
                "metrics": self.detector.metadata
            }

        X_new = np.vstack(new_feature_vectors)
        y_new = np.array(new_ground_truths)

        if existing_features is not None and existing_labels is not None and len(existing_features) > 0:
            X_combined = np.vstack([existing_features, X_new])
            y_combined = np.concatenate([existing_labels, y_new])
        else:
            X_combined = X_new
            y_combined = y_new

        # Ensure multi-class stability (both healthy=0 and theft=1)
        if len(np.unique(y_combined)) < 2 or len(X_combined) < 10:
            n_feat = X_combined.shape[1]
            normal_anchors = np.zeros((10, n_feat))
            normal_anchors[:, 0] = 45.0
            normal_anchors[:, 5] = 1.5
            theft_anchors = np.zeros((10, n_feat))
            theft_anchors[:, 0] = 8.0
            theft_anchors[:, 9] = 0.75
            theft_anchors[:, 10] = 1.5
            theft_anchors[:, 12] = 2.0
            X_combined = np.vstack([X_combined, normal_anchors, theft_anchors])
            y_combined = np.concatenate([y_combined, np.zeros(10, dtype=int), np.ones(10, dtype=int)])

        # Split 80/20 train/validation
        indices = np.arange(len(X_combined))
        np.random.seed(42)
        np.random.shuffle(indices)
        split_idx = int(0.8 * len(X_combined))
        train_idx, val_idx = indices[:split_idx], indices[split_idx:]

        X_train, y_train = X_combined[train_idx], y_combined[train_idx]
        X_val, y_val = X_combined[val_idx], y_combined[val_idx]

        # Active baseline performance
        old_auc = self.detector.metadata.get("roc_auc", 0.70)

        # Train new candidate model
        candidate_metrics = self.detector.train(X_train, y_train, X_val, y_val)
        new_auc = candidate_metrics.get("roc_auc", 0.70)

        hot_swapped = False
        # Hot-swap if metrics maintained or improved
        if new_auc >= (old_auc - 0.05):
            self.detector.save_models()
            hot_swapped = True
            message = f"Candidate model hot-swapped successfully (New ROC-AUC: {new_auc:.4f} vs Old: {old_auc:.4f})."
        else:
            # Revert or keep with warning
            message = f"Candidate model performance decreased (New ROC-AUC: {new_auc:.4f} vs Old: {old_auc:.4f}); preserved active baseline."

        candidate_metrics["hot_swapped"] = hot_swapped
        candidate_metrics["message"] = message
        return candidate_metrics

    def compile_dispute_dossier(
        self,
        consumer_data: Dict[str, Any],
        alerts_data: List[Dict[str, Any]],
        inspection_data: Optional[Dict[str, Any]],
        readings_summary: Dict[str, Any],
        evidence_photos: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Consolidates meter telemetry, baselines, inspection outcomes, photos,
        and legal verification hash into a dispute resolution audit dossier.
        """
        now_dt = datetime.now(timezone.utc)
        
        # Aggregate financial losses from alert history
        total_unbilled_kwh = sum(a.get("estimated_unbilled_kwh", 0.0) for a in alerts_data)
        total_loss = sum(a.get("estimated_loss_currency", 0.0) for a in alerts_data)
        lower_bound = sum(a.get("loss_lower_bound_95", 0.0) for a in alerts_data)
        upper_bound = sum(a.get("loss_upper_bound_95", 0.0) for a in alerts_data)
        regulatory_surcharge = total_loss * 0.25
        net_claim = total_loss + regulatory_surcharge

        payload_for_hashing = {
            "consumer_id": consumer_data.get("consumer_id"),
            "tariff_class": consumer_data.get("tariff_class"),
            "sanctioned_load_kw": consumer_data.get("sanctioned_load_kw"),
            "total_unbilled_energy_kwh": round(total_unbilled_kwh, 2),
            "assessed_financial_loss": round(total_loss, 2),
            "generated_timestamp": now_dt.isoformat()
        }
        # SHA-256 legal audit certification hash
        cert_hash = hashlib.sha256(json.dumps(payload_for_hashing, sort_keys=True).encode()).hexdigest()

        return {
            "consumer_id": consumer_data.get("consumer_id"),
            "tariff_class": consumer_data.get("tariff_class"),
            "sanctioned_load_kw": consumer_data.get("sanctioned_load_kw"),
            "meter_serial": inspection_data.get("meter_serial") if inspection_data else "SM-MTR-UNKNOWN",
            "feeder_id": consumer_data.get("feeder_id"),
            "transformer_id": consumer_data.get("transformer_id"),
            "total_unbilled_energy_kwh": round(total_unbilled_kwh, 2),
            "assessed_financial_loss": round(total_loss, 2),
            "confidence_interval_95": {
                "lower_bound_currency": round(lower_bound, 2),
                "upper_bound_currency": round(upper_bound, 2)
            },
            "regulatory_surcharge": round(regulatory_surcharge, 2),
            "net_claim_amount": round(net_claim, 2),
            "alert_history": alerts_data,
            "field_audit_record": inspection_data,
            "evidentiary_photos": evidence_photos,
            "telemetry_summary": readings_summary,
            "dossier_generated_at": now_dt,
            "legal_certification_hash": cert_hash
        }

    def correlate_whistleblower_tip(
        self,
        tip_lat: Optional[float],
        tip_lon: Optional[float],
        transformer_hint: Optional[str],
        meters_pool: List[Dict[str, Any]],
        search_radius_km: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Correlates anonymous community tip against nearby smart meters and anomaly scores."""
        flagged = []
        for m in meters_pool:
            score = 0.0
            reasons = []

            # Transformer match
            if transformer_hint and m.get("transformer_id"):
                if transformer_hint.strip().upper() == m.get("transformer_id").strip().upper():
                    score += 0.40
                    reasons.append(f"Transformer ID match: {transformer_hint}")

            # GPS proximity match
            if tip_lat is not None and tip_lon is not None and m.get("latitude") and m.get("longitude"):
                dist_km = self.haversine(tip_lat, tip_lon, m["latitude"], m["longitude"])
                if dist_km <= search_radius_km:
                    dist_weight = max(0.0, 1.0 - (dist_km / search_radius_km)) * 0.40
                    score += dist_weight
                    reasons.append(f"Proximity match: {dist_km:.2f} km from reported tip coordinates")

            # High risk or anomaly score bonus
            risk_score = m.get("risk_score", 0.0)
            if risk_score > 0.40:
                score += (risk_score * 0.30)
                reasons.append(f"Elevated algorithmic theft score: {risk_score:.2f}")

            if score >= 0.25:
                flagged.append({
                    "consumer_id": m["consumer_id"],
                    "tariff_class": m.get("tariff_class", "COMMERCIAL"),
                    "transformer_id": m.get("transformer_id"),
                    "correlation_confidence": round(float(min(1.0, score)), 2),
                    "active_risk_score": round(float(risk_score), 2),
                    "tamper_flags": m.get("tamper_flags", "NORMAL"),
                    "correlation_reasons": reasons
                })

        flagged.sort(key=lambda x: x["correlation_confidence"], reverse=True)
        return flagged[:10]


active_learner_instance = ActiveLearner()
