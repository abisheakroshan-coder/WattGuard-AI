"""WattGuard AI - Dual Detection Engine (Supervised & Unsupervised)
Features 4–6:
- Engine A (Supervised): GradientBoosting / RandomForest Classifier with class-imbalance weighting.
- Engine B (Unsupervised Novelty): IsolationForest fitted on healthy baseline patterns (Anomaly Score 0.0 to 1.0).
- Feeder Mass-Balance Engine: Computes residual transformer/feeder losses:
    Loss_unaccounted = E_feeder - (sum(E_meters) + Technical_Loss_standard)
"""
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional, Any, List
from sklearn.ensemble import RandomForestClassifier, IsolationForest, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from app.core.config import settings

FEATURE_NAMES = [
    "mean_kwh",
    "std_kwh",
    "median_kwh",
    "max_kwh",
    "min_kwh",
    "peak_to_avg_ratio",
    "night_to_day_ratio",
    "zero_reading_fraction",
    "load_factor",
    "drop_ratio_baseline",
    "dtw_shape_distance",
    "peer_zscore",
    "tamper_flag_severity"
]


class DualDetector:
    """Combines supervised classifier (Engine A) and Isolation Forest (Engine B)
    with grid feeder mass-balance residual factors."""

    def __init__(self, artifact_dir: Optional[Path] = None):
        self.artifact_dir = artifact_dir or settings.ARTIFACT_DIR
        self.supervised_model_path = self.artifact_dir / "supervised_detector.joblib"
        self.unsupervised_model_path = self.artifact_dir / "isolation_forest.joblib"
        self.scaler_path = self.artifact_dir / "feature_scaler.joblib"
        self.metadata_path = self.artifact_dir / "model_metadata.joblib"

        self.supervised_model: Optional[Any] = None
        self.isolation_forest: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.metadata: Dict[str, Any] = {}

        # Attempt to load existing artifacts if present
        self.load_models()

    def load_models(self) -> bool:
        """Loads serialized model artifacts from disk if available."""
        if (
            self.supervised_model_path.exists()
            and self.unsupervised_model_path.exists()
            and self.scaler_path.exists()
        ):
            try:
                self.supervised_model = joblib.load(self.supervised_model_path)
                self.isolation_forest = joblib.load(self.unsupervised_model_path)
                self.scaler = joblib.load(self.scaler_path)
                if self.metadata_path.exists():
                    self.metadata = joblib.load(self.metadata_path)
                return True
            except Exception as e:
                print(f"[DualDetector] Error loading models: {e}")
                return False
        return False

    def save_models(self) -> None:
        """Persists model artifacts and scaler to disk."""
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        if self.supervised_model is not None:
            joblib.dump(self.supervised_model, self.supervised_model_path)
        if self.isolation_forest is not None:
            joblib.dump(self.isolation_forest, self.unsupervised_model_path)
        if self.scaler is not None:
            joblib.dump(self.scaler, self.scaler_path)
        if self.metadata:
            joblib.dump(self.metadata, self.metadata_path)

    @staticmethod
    def extract_features(
        readings: pd.DataFrame,
        sanctioned_load_kw: float,
        baseline_mean: float,
        dtw_distance: float = 0.0,
        peer_zscore: float = 0.0,
        tamper_flag: str = "NORMAL"
    ) -> np.ndarray:
        """Extracts fixed 13-dimensional feature vector from consumer time-series window."""
        if readings.empty:
            return np.zeros(len(FEATURE_NAMES))

        vals = readings["energy_kwh"].to_numpy().astype(float)
        mean_val = float(np.mean(vals))
        std_val = float(np.std(vals))
        med_val = float(np.median(vals))
        max_val = float(np.max(vals))
        min_val = float(np.min(vals))

        par = float(max_val / max(mean_val, 1e-4))

        # Night vs Day ratio (night: 00-06, day: 09-17)
        if "timestamp" in readings.columns:
            ts = pd.to_datetime(readings["timestamp"])
            hours = ts.dt.hour
            night_mask = hours.isin([0, 1, 2, 3, 4, 5])
            day_mask = hours.isin([9, 10, 11, 12, 13, 14, 15, 16, 17])
            night_mean = float(vals[night_mask].mean()) if night_mask.any() else mean_val
            day_mean = float(vals[day_mask].mean()) if day_mask.any() else mean_val
            night_to_day = float(night_mean / max(day_mean, 1e-4))
        else:
            night_to_day = 0.5

        zero_fraction = float(np.mean(vals <= 0.01))
        load_factor = float(mean_val / max(sanctioned_load_kw, 0.5))

        # Drop ratio relative to historical baseline
        drop_ratio = float((baseline_mean - mean_val) / max(baseline_mean, 1e-4)) if baseline_mean > 0 else 0.0
        drop_ratio = float(np.clip(drop_ratio, -1.0, 1.0))

        # Tamper severity mapping
        severity_map = {
            "NORMAL": 0.0,
            "COVER_OPEN": 1.0,
            "REVERSE_CURRENT": 1.5,
            "NEUTRAL_TAMPER": 2.0,
            "MAGNETIC_TAMPER": 2.5
        }
        tamper_severity = severity_map.get(tamper_flag.upper(), 0.0)

        feature_vector = np.array([
            mean_val,
            std_val,
            med_val,
            max_val,
            min_val,
            par,
            night_to_day,
            zero_fraction,
            load_factor,
            drop_ratio,
            dtw_distance,
            peer_zscore,
            tamper_severity
        ], dtype=float)

        return feature_vector

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Fits both supervised RandomForest/GradientBoosting and unsupervised IsolationForest."""
        # 1. Fit scaler
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        # 2. Train Engine A (Supervised Classifier with class weighting)
        self.supervised_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1
        )
        self.supervised_model.fit(X_train_scaled, y_train)

        # 3. Train Engine B (Isolation Forest on healthy samples only: y_train == 0)
        healthy_mask = (y_train == 0)
        X_healthy_scaled = X_train_scaled[healthy_mask] if np.any(healthy_mask) else X_train_scaled

        self.isolation_forest = IsolationForest(
            n_estimators=100,
            contamination=0.10,
            random_state=42,
            n_jobs=-1
        )
        self.isolation_forest.fit(X_healthy_scaled)

        # Evaluate metrics if validation data provided
        metrics: Dict[str, Any] = {}
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            y_pred = self.supervised_model.predict(X_val_scaled)
            proba_mat = self.supervised_model.predict_proba(X_val_scaled)
            if proba_mat.shape[1] > 1:
                y_proba = proba_mat[:, 1]
            else:
                cls_val = self.supervised_model.classes_[0]
                y_proba = np.ones(len(X_val)) if cls_val == 1 else np.zeros(len(X_val))

            prec = float(precision_score(y_val, y_pred, zero_division=0))
            rec = float(recall_score(y_val, y_pred, zero_division=0))
            f1 = float(f1_score(y_val, y_pred, zero_division=0))
            auc = float(roc_auc_score(y_val, y_proba)) if len(np.unique(y_val)) > 1 else 0.5
            cm = confusion_matrix(y_val, y_pred).tolist()

            # Feature importances
            importances = dict(zip(FEATURE_NAMES, [float(v) for v in self.supervised_model.feature_importances_]))

            metrics = {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "roc_auc": round(auc, 4),
                "confusion_matrix": {
                    "tn": cm[0][0] if len(cm) > 1 else 0,
                    "fp": cm[0][1] if len(cm) > 1 else 0,
                    "fn": cm[1][0] if len(cm) > 1 else 0,
                    "tp": cm[1][1] if len(cm) > 1 else 0
                },
                "feature_importances": importances,
                "training_sample_count": int(len(X_train)),
                "model_version": "v1.0.0",
                "active_model_type": "RandomForestClassifier(balanced_subsample) + IsolationForest"
            }
            self.metadata = metrics

        self.save_models()
        return metrics

    def predict(
        self,
        features: np.ndarray,
        feeder_loss_factor: float = 0.0
    ) -> Dict[str, float]:
        """Runs dual inference for a consumer feature vector:
        - Engine A: Supervised probability of theft
        - Engine B: Unsupervised Isolation Forest novelty/anomaly score (0.0 to 1.0)
        - Injects Feeder Mass-Balance residual loss factor
        """
        if self.supervised_model is None or self.scaler is None:
            # Fallback if models not yet initialized
            return {
                "supervised_risk_score": 0.15,
                "anomaly_score": 0.15,
                "feeder_loss_factor": feeder_loss_factor,
                "raw_features": features.tolist()
            }

        feat_2d = features.reshape(1, -1)
        scaled_feat = self.scaler.transform(feat_2d)

        # Supervised probability
        proba_mat = self.supervised_model.predict_proba(scaled_feat)
        if proba_mat.shape[1] > 1:
            proba = float(proba_mat[0, 1])
        else:
            cls_val = self.supervised_model.classes_[0]
            proba = 1.0 if cls_val == 1 else 0.0

        # Isolation forest anomaly score
        # decision_function gives negative for anomalies, positive for inliers
        # Map to 0.0 (normal) to 1.0 (severe outlier)
        if self.isolation_forest is not None:
            raw_score = float(self.isolation_forest.decision_function(scaled_feat)[0])
            # raw_score is typically between -0.3 and +0.3
            anomaly_score = float(np.clip(0.5 - (raw_score / 0.5), 0.0, 1.0))
        else:
            anomaly_score = proba

        return {
            "supervised_risk_score": round(proba, 4),
            "anomaly_score": round(anomaly_score, 4),
            "feeder_loss_factor": round(float(feeder_loss_factor), 4),
            "raw_features": features.tolist()
        }

    @staticmethod
    def compute_feeder_mass_balance(
        feeder_total_kwh: float,
        sum_consumer_kwh: float,
        technical_loss_rate: float = 0.05
    ) -> Tuple[float, float]:
        """Computes feeder residual unaccounted energy loss:
        Loss_unaccounted = E_feeder - (sum(E_meters) + Technical_Loss_standard)
        
        Returns:
            Tuple of (unaccounted_loss_kwh, unaccounted_loss_fraction)
        """
        technical_loss_kwh = feeder_total_kwh * technical_loss_rate
        unaccounted_kwh = max(0.0, feeder_total_kwh - (sum_consumer_kwh + technical_loss_kwh))
        unaccounted_fraction = float(unaccounted_kwh / max(feeder_total_kwh, 1e-4))
        return float(unaccounted_kwh), float(min(1.0, unaccounted_fraction))


dual_detector_instance = DualDetector()
