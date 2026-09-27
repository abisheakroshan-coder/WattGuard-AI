"""WattGuard AI - Geospatial Hotspot & Feeder Vulnerability Engine
Features 19, 21:
- Spatial Hotspot Detector: DBSCAN on (latitude, longitude) of active alerts.
- Cluster centroids, radius, aggregate unbilled load, consumer counts.
- Feeder Vulnerability Index per transformer/substation zone.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.cluster import DBSCAN


class GeospatialClusterEngine:
    """Detects geographical theft clusters and computes feeder vulnerability indices."""

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance between two GPS coordinates in kilometers."""
        r = 6371.0  # Earth radius in km
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        delta_phi = np.radians(lat2 - lat1)
        delta_lambda = np.radians(lon2 - lon1)

        a = (
            np.sin(delta_phi / 2.0) ** 2
            + np.cos(phi1) * np.cos(phi2) * (np.sin(delta_lambda / 2.0) ** 2)
        )
        c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
        return float(r * c)

    def detect_hotspots(
        self,
        alert_records: List[Dict[str, Any]],
        eps_km: float = 1.5,  # 1.5 km neighborhood
        min_samples: int = 2
    ) -> List[Dict[str, Any]]:
        """Applies DBSCAN clustering on GPS coordinates of active alerts.
        
        Args:
            alert_records: List of dicts with:
                latitude, longitude, consumer_id, unbilled_kwh, loss_currency, feeder_id
        Returns:
            List of detected spatial clusters.
        """
        if not alert_records or len(alert_records) < min_samples:
            return []

        # Convert lat/lon to radians for Haversine metric in scikit-learn
        coords = np.array([
            [r["latitude"], r["longitude"]] for r in alert_records
        ])
        coords_rad = np.radians(coords)
        kms_per_radian = 6371.0088
        epsilon_radians = eps_km / kms_per_radian

        db = DBSCAN(eps=epsilon_radians, min_samples=min_samples, metric="haversine")
        labels = db.fit_predict(coords_rad)

        clusters = []
        unique_labels = set(labels)
        if -1 in unique_labels:
            unique_labels.remove(-1)  # Ignore noise points

        for cid in sorted(unique_labels):
            indices = np.where(labels == cid)[0]
            cluster_members = [alert_records[i] for i in indices]

            cluster_lats = [r["latitude"] for r in cluster_members]
            cluster_lons = [r["longitude"] for r in cluster_members]
            centroid_lat = float(np.mean(cluster_lats))
            centroid_lon = float(np.mean(cluster_lons))

            # Compute radius as max distance to centroid
            max_dist_m = 0.0
            for r in cluster_members:
                d_km = self.haversine_distance_km(centroid_lat, centroid_lon, r["latitude"], r["longitude"])
                max_dist_m = max(max_dist_m, d_km * 1000.0)

            total_unbilled = sum(r.get("unbilled_kwh", 0.0) for r in cluster_members)
            total_loss = sum(r.get("loss_currency", 0.0) for r in cluster_members)
            feeders = [r.get("feeder_id", "FDR-MAIN") for r in cluster_members]
            primary_feeder = max(set(feeders), key=feeders.count) if feeders else "FDR-MAIN"

            # Determine vulnerability rating
            if total_loss > 1500.0 or len(cluster_members) >= 6:
                rating = "EXTREME"
            elif total_loss > 800.0 or len(cluster_members) >= 4:
                rating = "HIGH"
            elif total_loss > 300.0:
                rating = "ELEVATED"
            else:
                rating = "MODERATE"

            clusters.append({
                "cluster_id": int(cid + 1),
                "centroid_latitude": round(centroid_lat, 6),
                "centroid_longitude": round(centroid_lon, 6),
                "radius_meters": round(max(max_dist_m, 100.0), 1),
                "consumer_count": len(cluster_members),
                "total_unbilled_kwh": round(total_unbilled, 2),
                "total_revenue_loss": round(total_loss, 2),
                "feeder_id": primary_feeder,
                "vulnerability_rating": rating,
                "consumer_ids": [r["consumer_id"] for r in cluster_members]
            })

        # Sort clusters by total revenue loss descending
        clusters.sort(key=lambda c: c["total_revenue_loss"], reverse=True)
        return clusters

    @staticmethod
    def compute_feeder_vulnerabilities(
        feeders_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculates Feeder Vulnerability Index (FVI) per transformer/substation zone:
        FVI = 0.40 * (High_Risk_Fraction) + 0.35 * (Unaccounted_Loss_Fraction) + 0.25 * (Loss_Density)
        """
        results = []
        for f in feeders_data:
            feeder_id = f["feeder_id"]
            tx_count = f.get("transformer_count", 1)
            active_meters = max(1, f.get("active_meter_count", 1))
            high_risk_meters = f.get("high_risk_meter_count", 0)
            unaccounted_kwh = f.get("unaccounted_feeder_loss_kwh", 0.0)
            total_feeder_kwh = max(1.0, f.get("total_feeder_kwh", 1000.0))

            risk_fraction = min(1.0, high_risk_meters / active_meters)
            loss_fraction = min(1.0, unaccounted_kwh / total_feeder_kwh)
            loss_density = min(1.0, (unaccounted_kwh / active_meters) / 50.0)

            fvi = (0.40 * risk_fraction + 0.35 * loss_fraction + 0.25 * loss_density) * 100.0
            fvi = round(float(np.clip(fvi, 0.0, 100.0)), 2)

            if fvi >= 65.0:
                tier = "CRITICAL"
            elif fvi >= 45.0:
                tier = "HIGH"
            elif fvi >= 25.0:
                tier = "MODERATE"
            else:
                tier = "LOW"

            results.append({
                "feeder_id": feeder_id,
                "transformer_count": tx_count,
                "active_meter_count": active_meters,
                "high_risk_meter_count": high_risk_meters,
                "unaccounted_feeder_loss_kwh": round(unaccounted_kwh, 2),
                "unaccounted_feeder_loss_pct": round(loss_fraction * 100.0, 2),
                "vulnerability_index_score": fvi,
                "vulnerability_tier": tier
            })

        results.sort(key=lambda x: x["vulnerability_index_score"], reverse=True)
        return results


geospatial_cluster_engine = GeospatialClusterEngine()
