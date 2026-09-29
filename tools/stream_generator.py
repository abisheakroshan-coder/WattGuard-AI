"""WattGuard AI - Live Grid Telemetry & Anomaly Stream Generator
Simulates real-time IoT smart meter readings, random grid frequency drift,
and periodically injects simulated power theft anomalies into the FastAPI backend.
"""
import sys
import os
import time
import random
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_BASE = os.environ.get("WATTGUARD_API_URL", "http://localhost:8001/api/v1")

FEEDERS = ["FDR_NORTH_01", "FDR_METRO_02", "FDR_EAST_03", "FDR_IND_05"]
CONSUMERS = [
    {"id": "CONS_COM_013", "feeder": "FDR_METRO_02", "base_kw": 85.0, "sanctioned": 371.6, "tariff": "COMMERCIAL"},
    {"id": "CONS_IND_007", "feeder": "FDR_IND_05", "base_kw": 240.0, "sanctioned": 620.0, "tariff": "INDUSTRIAL"},
    {"id": "CONS_RES_042", "feeder": "FDR_EAST_03", "base_kw": 12.0, "sanctioned": 45.0, "tariff": "RESIDENTIAL"},
    {"id": "CONS_COM_003", "feeder": "FDR_NORTH_01", "base_kw": 55.0, "sanctioned": 210.0, "tariff": "COMMERCIAL"},
    {"id": "CONS_RES_019", "feeder": "FDR_EAST_03", "base_kw": 9.5, "sanctioned": 30.0, "tariff": "RESIDENTIAL"},
    {"id": "CONS_IND_011", "feeder": "FDR_IND_05", "base_kw": 180.0, "sanctioned": 450.0, "tariff": "INDUSTRIAL"},
]

TAMPER_TYPES = [
    ("Direct Tap", "PHYSICAL_TAP_DETECTED", 0.75),
    ("Meter Shunt", "NEUTRAL_DISTURBANCE", 0.65),
    ("Phase Inversion", "REVERSE_CURRENT_DETECTED", 0.85),
    ("Unmetered Load", "CT_SATURATION_WARNING", 0.70),
    ("Neodymium Magnet", "MAGNETIC_INTERFERENCE", 0.80),
]


def post_json(endpoint: str, payload: dict) -> dict:
    url = f"{API_BASE}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": str(e)}


def generate_meter_reading(consumer: dict, inject_theft: bool = False):
    base = consumer["base_kw"]
    # Diurnal variation
    now = datetime.now(timezone.utc)
    hour = now.hour
    diurnal_mult = 0.6 + 0.5 * (1 + 0.8 * (1 if 8 <= hour <= 20 else 0.4))
    nominal_draw = base * diurnal_mult * (1 + (random.random() - 0.5) * 0.1)

    if inject_theft:
        theft_type, tamper_flag, drop_rate = random.choice(TAMPER_TYPES)
        metered_draw = nominal_draw * (1 - drop_rate)
        return {
            "consumer_id": consumer["id"],
            "timestamp": now.isoformat(),
            "expected_kw": round(nominal_draw, 2),
            "metered_kw": round(metered_draw, 2),
            "unmetered_delta_kw": round(nominal_draw - metered_draw, 2),
            "tamper_flag": tamper_flag,
            "theft_class": theft_type,
            "feeder_id": consumer["feeder"],
            "frequency_hz": round(50.0 + (random.random() - 0.5) * 0.08, 3),
            "is_anomaly": True
        }
    else:
        return {
            "consumer_id": consumer["id"],
            "timestamp": now.isoformat(),
            "expected_kw": round(nominal_draw, 2),
            "metered_kw": round(nominal_draw * 0.98, 2),
            "unmetered_delta_kw": 0.0,
            "tamper_flag": "NONE",
            "theft_class": "NOMINAL",
            "feeder_id": consumer["feeder"],
            "frequency_hz": round(50.0 + (random.random() - 0.5) * 0.04, 3),
            "is_anomaly": False
        }


def run_stream(interval_sec: float = 2.0, anomaly_rate: float = 0.25):
    print("=" * 70)
    print("  WATTGUARD AI - LIVE GRID TELEMETRY STREAM GENERATOR")
    print(f"  Target API:     {API_BASE}")
    print(f"  Tick Frequency: {interval_sec}s | Anomaly Probability: {anomaly_rate * 100}%")
    print("=" * 70)

    tick = 0
    anomalies_injected = 0

    try:
        while True:
            tick += 1
            consumer = random.choice(CONSUMERS)
            inject_theft = random.random() < anomaly_rate
            packet = generate_meter_reading(consumer, inject_theft=inject_theft)

            time_str = datetime.now().strftime("%H:%M:%S")

            if packet["is_anomaly"]:
                anomalies_injected += 1
                print(f"[{time_str}] [TICK #{tick:04d}] \033[91mCRITICAL ANOMALY\033[0m: {packet['consumer_id']} ({packet['feeder_id']})")
                print(f"       Tamper: {packet['theft_class']} | Flag: {packet['tamper_flag']}")
                print(f"       Draw: {packet['metered_kw']} kW (Expected {packet['expected_kw']} kW) -> Leak: -{packet['unmetered_delta_kw']} kW")
                
                # Attempt to notify backend
                try:
                    res = post_json(f"/detection/evaluate/consumer/{consumer['id']}", {
                        "force_evaluate": True,
                        "tamper_flag": packet["tamper_flag"]
                    })
                    if "error" not in res:
                        print(f"       -> Backend Evaluated: Risk={res.get('risk_score', 'N/A')}, Directive={res.get('recommended_action', 'N/A')}")
                except Exception:
                    pass
            else:
                print(f"[{time_str}] [TICK #{tick:04d}] \033[92mNOMINAL TICK\033[0m:    {packet['consumer_id']} | Draw: {packet['metered_kw']} kW | Freq: {packet['frequency_hz']} Hz")

            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print(f"Stream stopped. Total ticks: {tick}, Anomalies injected: {anomalies_injected}")
        print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WattGuard AI Telemetry Generator")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval between ticks (seconds)")
    parser.add_argument("--anomaly-rate", type=float, default=0.25, help="Probability of theft anomaly (0.0 to 1.0)")
    args = parser.parse_args()

    run_stream(interval_sec=args.interval, anomaly_rate=args.anomaly_rate)
