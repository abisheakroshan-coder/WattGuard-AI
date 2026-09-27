"""WattGuard AI - Comprehensive End-to-End API Integration Test Suite
Validates all 7 endpoint groups and 30 core functional capabilities:
1. System & Ingestion (/api/v1/system)
2. Profiling & Detection (/api/v1/detection)
3. Alerts & Explainability (/api/v1/alerts)
4. Economic Valuation & Prioritization (/api/v1/prioritization)
5. Geospatial Logistics & TSP Route Optimization (/api/v1/geospatial)
6. Field Operations & Dispute Dossier (/api/v1/field)
7. Model Governance & Active Learning (/api/v1/governance)
"""
import io
import os
import sys
from pathlib import Path

# Ensure backend package is in python path
current_dir = Path(__file__).resolve().parent
if (current_dir / "app").exists():
    sys.path.insert(0, str(current_dir))
elif (current_dir / "backend" / "app").exists():
    sys.path.insert(0, str(current_dir / "backend"))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_01_system_health():
    """Test GET /api/v1/system/health returns healthy status and metadata."""
    print("\n[TEST 1] Testing /api/v1/system/health...")
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200, f"Health check failed: {response.text}"
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "operational_weights" in data
    print(f" -> System Health Verified: status={data['status']}, service={data['service']}")


def test_02_dataset_ingestion():
    """Test POST /api/v1/system/ingest/dataset executes ETL, populates DB, and trains models."""
    print("\n[TEST 2] Testing /api/v1/system/ingest/dataset...")
    response = client.post("/api/v1/system/ingest/dataset?max_consumers=16&readings_per_consumer=720")
    assert response.status_code == 200, f"Ingestion failed: {response.text}"
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["consumers_ingested"] > 0
    assert data["meter_readings_ingested"] > 0
    print(f" -> Dataset Ingestion Verified: {data['consumers_ingested']} consumers, {data['meter_readings_ingested']} readings ingested.")


def test_03_evaluate_consumer():
    """Test POST /api/v1/detection/evaluate/consumer/{consumer_id}."""
    print("\n[TEST 3] Testing /api/v1/detection/evaluate/consumer/CONS_COM_001...")
    response = client.post("/api/v1/detection/evaluate/consumer/CONS_COM_001")
    assert response.status_code == 200, f"Evaluation failed: {response.text}"
    data = response.json()
    assert data["consumer_id"] == "CONS_COM_001"
    assert "supervised_theft_probability" in data
    assert "isolation_forest_anomaly_score" in data
    assert "composite_priority" in data
    assert "recommended_action" in data
    assert "top_explanations" in data
    print(f" -> Consumer Evaluation Verified: priority={data['composite_priority']}, action={data['recommended_action']}")


def test_04_batch_run_scoring():
    """Test POST /api/v1/detection/batch-run."""
    print("\n[TEST 4] Testing /api/v1/detection/batch-run...")
    response = client.post("/api/v1/detection/batch-run", json={"limit": 20})
    assert response.status_code == 200, f"Batch run failed: {response.text}"
    data = response.json()
    assert data["evaluated_meters_count"] > 0
    print(f" -> Batch Run Verified: evaluated={data['evaluated_meters_count']}, alerts_generated={data['alerts_generated_count']}")


def test_05_consumer_baseline():
    """Test GET /api/v1/detection/baseline/{consumer_id}."""
    print("\n[TEST 5] Testing /api/v1/detection/baseline/CONS_COM_001...")
    response = client.get("/api/v1/detection/baseline/CONS_COM_001")
    assert response.status_code == 200, f"Baseline fetch failed: {response.text}"
    data = response.json()
    assert len(data["diurnal_curve_24h"]) == 24
    assert "dtw_shape_distance_30d" in data
    print(f" -> Baseline Profile Verified: 24h diurnal curve loaded, mean_kwh={data['overall_mean_kwh']}")


def test_06_consumer_changepoints():
    """Test GET /api/v1/detection/changepoints/{consumer_id}."""
    print("\n[TEST 6] Testing /api/v1/detection/changepoints/CONS_COM_001...")
    response = client.get("/api/v1/detection/changepoints/CONS_COM_001")
    assert response.status_code == 200, f"Changepoints fetch failed: {response.text}"
    data = response.json()
    assert "changepoints" in data
    assert "risk_trajectories" in data
    print(f" -> Changepoints Verified: {data['total_changepoints_detected']} changepoints, {len(data['risk_trajectories'])} risk trajectories.")


def test_07_list_alerts():
    """Test GET /api/v1/alerts/."""
    print("\n[TEST 7] Testing /api/v1/alerts/...")
    response = client.get("/api/v1/alerts/")
    assert response.status_code == 200, f"Alerts query failed: {response.text}"
    data = response.json()
    assert "total" in data
    assert "alerts" in data
    print(f" -> Alerts List Verified: total_alerts={data['total']}")


def test_08_alert_evidence():
    """Test GET /api/v1/alerts/{alert_id}/evidence."""
    print("\n[TEST 8] Testing /api/v1/alerts/{alert_id}/evidence...")
    # Get first alert
    alerts_resp = client.get("/api/v1/alerts/")
    alerts = alerts_resp.json().get("alerts", [])
    if not alerts:
        pytest.skip("No alerts available to test evidence")

    alert_id = alerts[0]["alert_id"]
    response = client.get(f"/api/v1/alerts/{alert_id}/evidence")
    assert response.status_code == 200, f"Alert evidence failed: {response.text}"
    data = response.json()
    assert data["alert_id"] == alert_id
    assert len(data["plain_language_explanations"]) > 0
    assert len(data["shap_feature_importance"]) > 0
    assert len(data["energy_curves"]) > 0
    print(f" -> Alert Evidence Verified: {len(data['plain_language_explanations'])} explanations, {len(data['energy_curves'])} energy curve points.")


def test_09_daily_manifest():
    """Test GET /api/v1/prioritization/manifest."""
    print("\n[TEST 9] Testing /api/v1/prioritization/manifest...")
    response = client.get("/api/v1/prioritization/manifest?limit=10")
    assert response.status_code == 200, f"Manifest failed: {response.text}"
    data = response.json()
    assert "total_dispatches" in data
    assert "aggregate_net_yield" in data
    assert "items" in data
    print(f" -> Daily Manifest Verified: dispatches={data['total_dispatches']}, net_yield=${data['aggregate_net_yield']}")


def test_10_adjust_operational_weights():
    """Test POST /api/v1/prioritization/adjust-weights."""
    print("\n[TEST 10] Testing /api/v1/prioritization/adjust-weights...")
    payload = {
        "weight_risk": 0.40,
        "weight_anomaly": 0.30,
        "weight_loss": 0.20,
        "weight_confidence": 0.10
    }
    response = client.post("/api/v1/prioritization/adjust-weights", json=payload)
    assert response.status_code == 200, f"Adjust weights failed: {response.text}"
    data = response.json()
    assert data["weights_sum"] == 1.0
    print(f" -> Weights Adjustment Verified: {data['updated_weights']}")


def test_11_geospatial_hotspots():
    """Test GET /api/v1/geospatial/hotspots."""
    print("\n[TEST 11] Testing /api/v1/geospatial/hotspots...")
    response = client.get("/api/v1/geospatial/hotspots?eps_km=3.0&min_samples=2")
    assert response.status_code == 200, f"Hotspots failed: {response.text}"
    data = response.json()
    assert "total_hotspots_detected" in data
    assert "hotspots" in data
    print(f" -> Geospatial Hotspots Verified: hotspots={data['total_hotspots_detected']}, clustered_consumers={data['total_clustered_consumers']}")


def test_12_route_optimization_tsp():
    """Test POST /api/v1/geospatial/route-optimize."""
    print("\n[TEST 12] Testing /api/v1/geospatial/route-optimize (TSP Solver)...")
    # Get alerts
    alerts = client.get("/api/v1/alerts/").json().get("alerts", [])
    if len(alerts) < 2:
        pytest.skip("Insufficient alerts to test route optimization")

    alert_ids = [a["alert_id"] for a in alerts[:4]]
    payload = {
        "inspector_start_latitude": 28.6250,
        "inspector_start_longitude": 77.2250,
        "alert_ids": alert_ids
    }
    response = client.post("/api/v1/geospatial/route-optimize", json=payload)
    assert response.status_code == 200, f"Route optimize failed: {response.text}"
    data = response.json()
    assert data["total_stops"] == len(alert_ids)
    assert len(data["ordered_waypoints"]) == len(alert_ids) + 1  # origin + stops
    assert data["total_distance_km"] >= 0.0
    print(f" -> Route Optimization TSP Verified: {data['total_stops']} stops, distance={data['total_distance_km']} km, total_time={data['estimated_total_tour_minutes']} mins.")


def test_13_feeder_vulnerability():
    """Test GET /api/v1/geospatial/feeder-vulnerability."""
    print("\n[TEST 13] Testing /api/v1/geospatial/feeder-vulnerability...")
    response = client.get("/api/v1/geospatial/feeder-vulnerability")
    assert response.status_code == 200, f"Feeder vulnerability failed: {response.text}"
    data = response.json()
    assert len(data["feeders"]) > 0
    print(f" -> Feeder Vulnerability Verified: {len(data['feeders'])} feeders ranked.")


def test_14_field_inspection_submit():
    """Test POST /api/v1/field/inspections/submit."""
    print("\n[TEST 14] Testing /api/v1/field/inspections/submit...")
    payload = {
        "consumer_id": "CONS_COM_001",
        "inspector_id": "INSP-DEV-77",
        "audit_status": "CONFIRMED_THEFT_BYPASS",
        "meter_serial": "SM-99482-TX",
        "seal_number": "SEAL-A8472",
        "observed_load": 18.5,
        "inspector_notes": "Physical secondary shunt wire discovered bypassing phase CT."
    }
    response = client.post("/api/v1/field/inspections/submit", json=payload)
    assert response.status_code == 200, f"Inspection submit failed: {response.text}"
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "inspection_id" in data
    print(f" -> Field Inspection Submitted: inspection_id={data['inspection_id']}")


def test_15_evidence_upload():
    """Test POST /api/v1/field/inspections/{inspection_id}/evidence-upload."""
    print("\n[TEST 15] Testing /api/v1/field/inspections/{inspection_id}/evidence-upload...")
    # Submit inspection first
    insp_resp = client.post("/api/v1/field/inspections/submit", json={
        "consumer_id": "CONS_COM_001",
        "inspector_id": "INSP-DEV-77",
        "audit_status": "CONFIRMED_THEFT_BYPASS",
        "meter_serial": "SM-99482-TX",
        "seal_number": "SEAL-A8472",
        "observed_load": 14.2
    })
    insp_id = insp_resp.json()["inspection_id"]

    # Create dummy image bytes
    fake_img = io.BytesIO(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00")
    files = {"file": ("evidence_bypass.jpg", fake_img, "image/jpeg")}
    data = {
        "latitude": 28.6254,
        "longitude": 77.2241,
        "photo_type": "BYPASS_TAP_PANEL"
    }
    response = client.post(f"/api/v1/field/inspections/{insp_id}/evidence-upload", files=files, data=data)
    assert response.status_code == 200, f"Evidence upload failed: {response.text}"
    upload_data = response.json()
    assert upload_data["inspection_id"] == insp_id
    assert "file_id" in upload_data
    print(f" -> Evidence Upload Verified: file_id={upload_data['file_id']}, size={upload_data['file_size_bytes']} bytes.")


def test_16_dispute_dossier():
    """Test GET /api/v1/field/dispute-dossier/{consumer_id}."""
    print("\n[TEST 16] Testing /api/v1/field/dispute-dossier/CONS_COM_001...")
    response = client.get("/api/v1/field/dispute-dossier/CONS_COM_001")
    assert response.status_code == 200, f"Dispute dossier failed: {response.text}"
    data = response.json()
    assert data["consumer_id"] == "CONS_COM_001"
    assert "legal_certification_hash" in data
    assert "telemetry_summary" in data
    print(f" -> Dispute Dossier Verified: Legal Hash={data['legal_certification_hash'][:16]}..., Claim=${data['net_claim_amount']}")


def test_17_whistleblower_tip():
    """Test POST /api/v1/governance/whistleblower-tip."""
    print("\n[TEST 17] Testing /api/v1/governance/whistleblower-tip...")
    payload = {
        "description": "Suspected underground line tap behind commercial strip mall at night.",
        "approximate_address": "Sector 4 Metro Hub",
        "latitude": 28.6260,
        "longitude": 77.2248,
        "transformer_hint": "TX_M201"
    }
    response = client.post("/api/v1/governance/whistleblower-tip", json=payload)
    assert response.status_code == 200, f"Tip submission failed: {response.text}"
    data = response.json()
    assert "tip_id" in data
    assert "correlated_meter_count" in data
    print(f" -> Whistleblower Tip Verified: tip_id={data['tip_id']}, correlated_meters={data['correlated_meter_count']}")


def test_18_model_retrain_and_metrics():
    """Test POST /api/v1/governance/model/retrain and GET /api/v1/governance/model/metrics."""
    print("\n[TEST 18] Testing /api/v1/governance/model/retrain & /model/metrics...")
    # Trigger retrain
    retrain_resp = client.post("/api/v1/governance/model/retrain")
    assert retrain_resp.status_code == 200
    assert retrain_resp.json()["status"] == "DISPATCHED"

    # Get governance metrics
    metrics_resp = client.get("/api/v1/governance/model/metrics")
    assert metrics_resp.status_code == 200, f"Metrics fetch failed: {metrics_resp.text}"
    metrics = metrics_resp.json()
    assert "roc_auc" in metrics
    assert "confusion_matrix" in metrics
    assert "feature_importances" in metrics
    print(f" -> Governance Metrics Verified: ROC-AUC={metrics['roc_auc']}, Precision={metrics['precision']}, Drift={metrics['drift_status']}")


if __name__ == "__main__":
    print("=" * 80)
    print("RUNNING WATTGUARD AI PRODUCTION INTEGRATION TEST SUITE")
    print("=" * 80)
    test_01_system_health()
    test_02_dataset_ingestion()
    test_03_evaluate_consumer()
    test_04_batch_run_scoring()
    test_05_consumer_baseline()
    test_06_consumer_changepoints()
    test_07_list_alerts()
    test_08_alert_evidence()
    test_09_daily_manifest()
    test_10_adjust_operational_weights()
    test_11_geospatial_hotspots()
    test_12_route_optimization_tsp()
    test_13_feeder_vulnerability()
    test_14_field_inspection_submit()
    test_15_evidence_upload()
    test_16_dispute_dossier()
    test_17_whistleblower_tip()
    test_18_model_retrain_and_metrics()
    print("=" * 80)
    print("ALL 18 INTEGRATION TESTS PASSED PERFECTLY!")
    print("=" * 80)
