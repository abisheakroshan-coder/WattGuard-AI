import urllib.request
import json

BASE = "http://127.0.0.1:8001"

print("=" * 70)
print("  WATTGUARD AI - UNIFIED FASTAPI INTEGRATION VERIFICATION")
print(f"  Target: {BASE}")
print("=" * 70)

# 1. Frontend & SPA
print("\n[CHECK 1] Frontend Root & SPA Routing Verification:")
for path in ["/", "/radar", "/feed", "/inspector", "/governance"]:
    res = urllib.request.urlopen(f"{BASE}{path}")
    print(f"  GET {path:15} -> Status: {res.status} | Content-Type: {res.headers.get('Content-Type')}")

# 2. Assets
html = urllib.request.urlopen(f"{BASE}/").read().decode("utf-8")
import re
assets = re.findall(r'/assets/[a-zA-Z0-9_\-\.]+', html)
print(f"\n[CHECK 2] Frontend Static Bundles ({len(assets)} assets):")
for a in assets:
    res = urllib.request.urlopen(f"{BASE}{a}")
    print(f"  GET {a:30} -> Status: {res.status} | Size: {len(res.read())} bytes")

# 3. Dashboard Metrics
print("\n[CHECK 3] Real Dashboard Metrics from Backend /api/v1/prioritization/manifest:")
manifest = json.loads(urllib.request.urlopen(f"{BASE}/api/v1/prioritization/manifest").read().decode())
print(f"  Total Dispatches:       {manifest['total_dispatches']}")
print(f"  Aggregate Unbilled kWh: {manifest['aggregate_unbilled_kwh']} kWh")
print(f"  Expected Recovery:      ${manifest['aggregate_expected_revenue_recovery']}")
print(f"  Aggregate Net Yield:    ${manifest['aggregate_net_yield']}")

# 4. Consumers, Alerts & Scores
print("\n[CHECK 4] Real Consumers & ML Scores from Backend /api/v1/alerts/:")
alerts_res = json.loads(urllib.request.urlopen(f"{BASE}/api/v1/alerts/?page_size=6").read().decode())
print(f"  Total Alerts in DB: {alerts_res['total']}")
for a in alerts_res['alerts']:
    print(f"  {a['consumer_id']:15} | Risk: {a['risk_score']:.4f} | AnomalyScore: {a['anomaly_score']:.4f} | Priority: {a['composite_priority']:.2f} | Loss: ${a['estimated_loss_currency']:.2f}")

# 5. SHAP Evidence
first_alert = alerts_res['alerts'][0]
print(f"\n[CHECK 5] Real SHAP Evidence for {first_alert['alert_id']} ({first_alert['consumer_id']}):")
ev = json.loads(urllib.request.urlopen(f"{BASE}/api/v1/alerts/{first_alert['alert_id']}/evidence").read().decode())
print(f"  Explanations: {ev.get('plain_language_explanations')}")
print(f"  SHAP Features ({len(ev.get('shap_feature_importance', []))}): {ev.get('shap_feature_importance')[:2]}")
print(f"  Energy Curve Points: {len(ev.get('energy_curves', []))} hourly records")

# 6. Field Inspection Submit
print(f"\n[CHECK 6] Submitting Real Field Inspection to Backend Database:")
post_payload = json.dumps({
    "consumer_id": first_alert["consumer_id"],
    "alert_id": first_alert["alert_id"],
    "inspector_id": "INSP-8410",
    "audit_status": "CONFIRMED_THEFT_BYPASS",
    "meter_serial": "SM-99482-TX",
    "seal_number": "WG-SEAL-882104-SEC",
    "observed_load": 14.5,
    "inspector_notes": "Live integration verification: direct bypass confirmed and re-sealed."
}).encode("utf-8")
req = urllib.request.Request(f"{BASE}/api/v1/field/inspections/submit", data=post_payload, headers={"Content-Type": "application/json"})
ins_res = json.loads(urllib.request.urlopen(req).read().decode())
print(f"  Inspection ID: {ins_res.get('inspection_id')}")
print(f"  Outcome:       {ins_res.get('audit_status')}")
print(f"  Message:       {ins_res.get('message')}")

print("\n" + "=" * 70)
print("  ALL VERIFICATION CHECKS COMPLETED SUCCESSFULLY!")
print("=" * 70)
