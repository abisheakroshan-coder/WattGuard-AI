"""WattGuard AI - Behavioral Profiling & Baselining Engine
Features 1–3, 7–9:
- Dynamic Time Warping (DTW) shape comparisons against historical windows.
- Peer cohort clustering and rolling z-scores against immediate neighbors.
- Vacancy fingerprinting filter (<0.2 kWh flat standby).
- Changepoint detection (rolling two-sample Student's t-test).
- Solar disaggregation filter (diurnal bell-curve drop during 11:00 AM - 3:00 PM).
- Multi-week Risk Trajectory Tracker (4 sliding windows).
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from scipy import stats
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from sklearn.cluster import KMeans


class BaselineEngine:
    """Computes dynamic consumer baselines, DTW shape distances, peer cohort deviations,
    vacancy fingerprints, changepoints, and solar disaggregation."""

    def __init__(self):
        pass

    @staticmethod
    def compute_diurnal_baseline(readings: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Calculates 24-hour diurnal mean, std, and 95% confidence bounds (mu +/- 1.96*sigma).
        
        Args:
            readings: DataFrame with 'timestamp' and 'energy_kwh'.
        Returns:
            Tuple of (hours, mean_curve, std_curve, lower_95, upper_95)
        """
        if readings.empty:
            zeros = np.zeros(24)
            return np.arange(24), zeros, zeros, zeros, zeros

        df = readings.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        df["hour"] = df["timestamp"].dt.hour
        hourly_stats = df.groupby("hour")["energy_kwh"].agg(["mean", "std"]).reindex(range(24)).fillna(0.0)

        mean_curve = hourly_stats["mean"].to_numpy()
        std_curve = hourly_stats["std"].to_numpy()
        # Fallback std if 0
        std_curve = np.where(std_curve < 1e-4, 0.05 * np.maximum(mean_curve, 0.1), std_curve)

        lower_95 = np.maximum(0.0, mean_curve - 1.96 * std_curve)
        upper_95 = mean_curve + 1.96 * std_curve

        return np.arange(24), mean_curve, std_curve, lower_95, upper_95

    @staticmethod
    def compute_dtw_distance(series_a: np.ndarray, series_b: np.ndarray) -> float:
        """Computes FastDTW normalized shape distance between two time-series windows."""
        if len(series_a) == 0 or len(series_b) == 0:
            return 0.0

        # Subsample or interpolate to comparable lengths if long (for performance)
        target_len = min(720, max(len(series_a), len(series_b)))  # max 30 days of hourly points
        if len(series_a) > target_len:
            indices = np.linspace(0, len(series_a) - 1, target_len).astype(int)
            series_a = series_a[indices]
        if len(series_b) > target_len:
            indices = np.linspace(0, len(series_b) - 1, target_len).astype(int)
            series_b = series_b[indices]

        # Normalize amplitudes to compare pure shape
        norm_a = series_a - np.mean(series_a)
        std_a = np.std(series_a)
        if std_a > 1e-5:
            norm_a = norm_a / std_a

        norm_b = series_b - np.mean(series_b)
        std_b = np.std(series_b)
        if std_b > 1e-5:
            norm_b = norm_b / std_b

        distance, _ = fastdtw(norm_a, norm_b, dist=lambda x, y: abs(float(x) - float(y)))
        normalized_distance = float(distance / max(len(norm_a), 1))
        return float(normalized_distance)

    @staticmethod
    def is_vacancy_profile(recent_readings: pd.DataFrame, standby_threshold: float = 0.20) -> bool:
        """Identifies genuine vacant property by detecting flat, low-variance baseline.
        
        A vacant property exhibits:
        - Mean consumption < 0.20 kWh (phantom/standby load only)
        - Very low standard deviation (< 0.05 kWh)
        - Zero morning or evening peak fluctuations
        """
        if recent_readings.empty or len(recent_readings) < 24:
            return False

        vals = recent_readings["energy_kwh"].to_numpy()
        mean_val = float(np.mean(vals))
        std_val = float(np.std(vals))
        peak_val = float(np.max(vals))

        if mean_val < standby_threshold and std_val < 0.06 and peak_val < (standby_threshold * 1.8):
            return True
        return False

    @staticmethod
    def check_solar_signature(recent_readings: pd.DataFrame) -> Tuple[bool, float]:
        """Detects whether day-time consumption dip is caused by rooftop solar generation.
        
        Solar profile shows a characteristic bell-curve dip between 11:00 AM and 3:00 PM (hours 11-15),
        while evening hours (18:00 - 22:00) remain normal/high.
        Returns:
            Tuple of (is_solar_suppressed, solar_confidence)
        """
        if recent_readings.empty or len(recent_readings) < 48:
            return False, 0.0

        df = recent_readings.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour

        solar_hours_mean = float(df[df["hour"].between(11, 15)]["energy_kwh"].mean())
        evening_hours_mean = float(df[df["hour"].between(18, 22)]["energy_kwh"].mean())
        night_hours_mean = float(df[df["hour"].between(1, 5)]["energy_kwh"].mean())

        # If evening is active and solar hours dip below 50% of evening
        if evening_hours_mean > 0.5:
            dip_ratio = (evening_hours_mean - solar_hours_mean) / max(evening_hours_mean, 1e-4)
            if dip_ratio > 0.40 and solar_hours_mean <= night_hours_mean * 1.2:
                confidence = float(min(1.0, dip_ratio))
                return True, confidence

        return False, 0.0

    @staticmethod
    def compute_peer_cohort_zscore(
        target_consumption: float,
        cohort_consumptions: List[float]
    ) -> float:
        """Computes rolling normalized consumption z-score against immediate peer cohort."""
        if not cohort_consumptions or len(cohort_consumptions) < 2:
            return 0.0

        arr = np.array(cohort_consumptions)
        mean_cohort = np.mean(arr)
        std_cohort = np.std(arr)

        if std_cohort < 1e-4:
            return 0.0

        z_score = float((target_consumption - mean_cohort) / std_cohort)
        return z_score

    @staticmethod
    def detect_changepoints(
        readings: pd.DataFrame,
        window_size_hours: int = 168,  # 7 days
        significance_level: float = 0.01
    ) -> List[Dict[str, Any]]:
        """Offline changepoint detection using rolling two-sample Student's t-test
        to pinpoint the exact datetime of persistent consumption step-downs.
        """
        if readings.empty or len(readings) < window_size_hours * 2:
            return []

        df = readings.sort_values("timestamp").reset_index(drop=True)
        vals = df["energy_kwh"].to_numpy()
        times = df["timestamp"].to_numpy()
        n = len(vals)

        detected = []
        step = max(24, window_size_hours // 7)  # Check daily steps
        min_drop_pct = 25.0  # At least 25% persistent drop

        i = window_size_hours
        while i < (n - window_size_hours):
            pre_window = vals[i - window_size_hours : i]
            post_window = vals[i : i + window_size_hours]

            pre_mean = float(np.mean(pre_window))
            post_mean = float(np.mean(post_window))

            if pre_mean > 0.1:
                drop_pct = float(((pre_mean - post_mean) / pre_mean) * 100.0)
                if drop_pct >= min_drop_pct:
                    # Run two-sample t-test
                    t_stat, p_val = stats.ttest_ind(pre_window, post_window, equal_var=False)
                    if p_val < significance_level and t_stat > 0:
                        severity = "CRITICAL" if drop_pct > 60 else ("HIGH" if drop_pct > 40 else "MEDIUM")
                        detected.append({
                            "timestamp": pd.to_datetime(times[i]),
                            "p_value": float(p_val),
                            "drop_percentage": round(drop_pct, 2),
                            "pre_mean_kwh": round(pre_mean, 3),
                            "post_mean_kwh": round(post_mean, 3),
                            "severity": severity
                        })
                        # Skip forward to avoid duplicate detections on same transition
                        i += window_size_hours
                        continue
            i += step

        return detected

    @staticmethod
    def track_risk_trajectory(
        readings: pd.DataFrame,
        baseline_mean: float,
        num_windows: int = 4,
        window_days: int = 7
    ) -> List[Dict[str, Any]]:
        """Computes multi-week risk progression over sliding windows (e.g. LOW -> MEDIUM -> HIGH -> CRITICAL)."""
        if readings.empty or baseline_mean <= 1e-4:
            return []

        df = readings.sort_values("timestamp").reset_index(drop=True)
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        max_time = df["timestamp"].max()
        trajectories = []

        for w in range(num_windows - 1, -1, -1):
            w_end = max_time - timedelta(days=w * window_days)
            w_start = w_end - timedelta(days=window_days)
            window_slice = df[(df["timestamp"] >= w_start) & (df["timestamp"] < w_end)]

            if not window_slice.empty:
                w_mean = float(window_slice["energy_kwh"].mean())
                drop_pct = max(0.0, float(((baseline_mean - w_mean) / baseline_mean) * 100.0))
            else:
                w_mean = 0.0
                drop_pct = 0.0

            if drop_pct > 65.0:
                state = "CRITICAL"
            elif drop_pct > 40.0:
                state = "HIGH"
            elif drop_pct > 20.0:
                state = "MEDIUM"
            else:
                state = "LOW"

            trajectories.append({
                "window_name": f"W-{num_windows - w}",
                "start_time": w_start,
                "end_time": w_end,
                "mean_consumption": round(w_mean, 3),
                "drop_from_baseline_pct": round(drop_pct, 2),
                "risk_state": state
            })

        return trajectories
