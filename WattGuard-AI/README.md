# WattGuard AI: AI-Assisted Power Theft & Unbilled Energy Decision-Support System

A production-grade Python FastAPI backend, machine learning pipeline, spatial-fleet optimizer, and decision-support system designed to detect non-technical electricity losses (NTL / power theft), estimate uncertainty-aware revenue recovery, and dispatch inspection operations.

---

## 1. System Architecture

```text
                               +--------------------------------------------+
                               |     Raw Smart Meter Telemetry (df.csv)    |
                               +--------------------------------------------+
                                                     |
                                                     v
                               +--------------------------------------------+
                               |  Auto-Adaptive Ingestion & ETL (etl.py)   |
                               +--------------------------------------------+
                                                     |
                    +--------------------------------+--------------------------------+
                    |                                                                 |
                    v                                                                 v
+---------------------------------------+                 +---------------------------------------+
|  Module 1: Profiling & Baselining    |                 |   Module 2: Dual Detection Engine     |
|  - FastDTW Shape Distance             |                 |   - Engine A: Supervised RF / GBDT    |
|  - Peer Cohort Clustering (z-score)   |                 |   - Engine B: Unsupervised IsoForest  |
|  - Vacancy Standby Filter (<0.20 kWh) |                 |   - Feeder Mass-Balance Residual Loss |
|  - Diurnal Confidence Curves (95%)    |                 +---------------------------------------+
+---------------------------------------+                                     |
                    |                                                         |
                    +--------------------------------+------------------------+
                                                     v
                    +---------------------------------------------------------+
                    |        Module 3: Time-Series Anomalies & Trends         |
                    |        - Two-Sample Student's t-test Changepoints       |
                    |        - 4-Window Risk Trajectory (LOW->CRITICAL)       |
                    |        - Diurnal Solar Signature Disaggregation         |
                    +---------------------------------------------------------+
                                                     |
                    +--------------------------------+------------------------+
                    |                                                         |
                    v                                                         v
+---------------------------------------+                 +---------------------------------------+
| Module 4: Explainability & SHAP       |                 | Module 5 & 6: Valuation & Priority    |
| - TreeExplainer Attributions          |                 | - Delta E with 95% Confidence Bounds  |
| - Plain-Language Operator Diagnostics |                 | - Tiered Tariff Slabs & 25% Penalties |
| - Hardware Tamper Register Mapping    |                 | - Net Yield ROI = Loss - DispatchCost |
+---------------------------------------+                 | - Composite Priority Index (0-100)    |
                                                          | - Directives (RAID, AUDIT, CALIBRATE) |
                                                          +---------------------------------------+
                                                                      |
                                                                      v
                    +---------------------------------------------------------+
                    |         Module 7: Geospatial & Route Optimization       |
                    |         - Haversine DBSCAN Hotspot Clustering           |
                    |         - TSP Inspector Vehicle Routing (2-opt)         |
                    |         - Feeder Vulnerability Index (FVI)              |
                    +---------------------------------------------------------+
                                                     |
                    +--------------------------------+------------------------+
                    |                                                         |
                    v                                                         v
+---------------------------------------+                 +---------------------------------------+
| Module 8: Field Operations & Audit    |                 | Module 8: Closed-Loop Active Learning |
| - Standardized Inspection Audit Status|                 | - Asynchronous Retraining Worker      |
| - Geo-Tagged Multipart Photo Evidence |                 | - Validation Holdout Gate             |
| - Dispute Dossier (SHA-256 Hash)      |                 | - Model Governance & Drift Tracking   |
+---------------------------------------+                 | - Whistleblower Spatial Correlation   |
                                                          +---------------------------------------+
```

---

## 2. Directory Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── system.py          # /ingest/dataset, /health
│   │   │   │   ├── detection.py       # /evaluate/consumer, /batch-run, /baseline, /changepoints
│   │   │   │   ├── alerts.py          # /, /{alert_id}/evidence
│   │   │   │   ├── prioritization.py  # /manifest, /adjust-weights
│   │   │   │   ├── geospatial.py      # /hotspots, /route-optimize, /feeder-vulnerability
│   │   │   │   ├── field.py           # /inspections/submit, /evidence-upload, /dispute-dossier
│   │   │   │   └── governance.py      # /model/retrain, /model/metrics, /whistleblower-tip
│   │   │   └── api_router.py          # Master v1 router aggregator
│   ├── core/
│   │   ├── config.py                  # Pydantic Settings, tariff slabs, operational weights
│   │   ├── database.py                # SQLAlchemy 2.0 async engine & sessionmaker
│   │   └── etl.py                     # Auto-adaptive inspection, normalization & ingestion
│   ├── models/                        # SQLAlchemy DB entities
│   │   ├── consumer.py                # Customer profiles, connection capacity, feeder topology
│   │   ├── meter_reading.py           # Hourly time-series consumption & tamper flags
│   │   ├── alert.py                   # Anomaly scores, priority, loss bounds & directives
│   │   ├── inspection.py              # Field outcomes, seal numbers, photo metadata
│   │   └── tip.py                     # Anonymous community whistleblower tips
│   ├── schemas/                       # Pydantic v2 validation models
│   │   ├── detection_schema.py        # Evaluation, baseline, changepoints, batch scoring
│   │   ├── alert_schema.py            # Alert manifests, evidence, weight adjustments
│   │   └── field_schema.py            # Inspections, uploads, dossiers, hotspots, TSP, governance
│   ├── ml/                            # Machine learning, math & spatial engines
│   │   ├── baseline_engine.py         # FastDTW, peer cohort z-scores, vacancy & solar filters
│   │   ├── dual_detector.py           # Supervised classifier + IsolationForest + Feeder balance
│   │   ├── explainability.py          # Tree SHAP attribution & plain-language translation
│   │   ├── loss_estimator.py          # 95% loss bounds, tariff slabs, net yield & action rules
│   │   ├── geospatial_cluster.py      # Haversine DBSCAN clustering & Feeder Vulnerability Index
│   │   ├── route_optimizer.py         # Nearest Neighbor + 2-opt TSP route optimizer
│   │   └── active_learner.py          # Closed-loop retraining, dispute dossier with SHA-256 hash
│   ├── artifacts/                     # Serialized .joblib models, scalers, and metadata
│   └── main.py                        # FastAPI entrypoint with lifespan DB & model initialization
├── data/                              # Local dataset directory containing df.csv
├── uploads/                           # Structured storage for evidence photos
│   └── evidence/
├── alembic/                           # Alembic database schema migrations
├── requirements.txt                   # Production Python package dependencies
├── test_api.py                        # End-to-end integration test runner
└── README.md
```

---

## 3. Dataset Characteristics & Auto-Adaptive ETL

The system operates on smart meter telemetry from commercial and residential facilities (`df.csv`):
- **Scale**: 560,655 hourly time-series readings across 16 building facility classes (each having 35,040 hourly records = 4 years of continuous 8,760-hour annual cycles).
- **Target Distribution**: Healthy baselines (`Normal`: 59.2%) and 6 labeled synthetic theft attacks (`Theft1` to `Theft6`: 40.8% total) simulating percentage reduction, constant offset, random reduction, peak reduction, and phase bypassing.
- **Normalization**: The ETL pipeline (`app/core/etl.py`) maps arbitrary column headers into standard internal entities:
  - `consumer_id`: Unique alphanumeric ID (`CONS_COM_001`, `CONS_RES_002`, etc.)
  - `timestamp`: UTC datetime index
  - `energy_kwh`: Active power draw derived from `Electricity:Facility [kW](Hourly)`
  - `sanctioned_load_kw`: Peak connection load capacity with 25% safety margin
  - `tariff_class`: `RESIDENTIAL`, `COMMERCIAL`, `INDUSTRIAL`, `AGRICULTURAL`
  - `latitude`, `longitude`: Realistic geospatial coordinates clustered around feeder substation hubs
  - `feeder_id`, `transformer_id`, `phase`: Grid topological identifiers
  - `tamper_flags`: Smart meter status registers (`NORMAL`, `REVERSE_CURRENT`, `NEUTRAL_TAMPER`, `COVER_OPEN`, `MAGNETIC_TAMPER`)

---

## 4. Core Algorithmic Capabilities

### Module 1: Behavioral Profiling & Baselining
- **Dynamic Time Warping (DTW)**: Normalized shape distance comparison between recent consumption windows and historical diurnal curves using FastDTW.
- **Peer Cohort Clustering**: Groups consumers dynamically by `(transformer_id, tariff_class)` to compute normalized rolling z-scores against immediate neighbors.
- **Vacancy Fingerprinting Filter**: Suppresses false positives by detecting prolonged standby baselines (< 0.20 kWh flat draw with $\sigma < 0.05$).
- **Diurnal Confidence Intervals**: Hourly 95% confidence bands ($\mu \pm 1.96\sigma$) for normal consumption.

### Module 2: Dual Detection Engine
- **Engine A (Supervised)**: `RandomForestClassifier` with `class_weight='balanced_subsample'` trained on 13 engineered time-series features (mean, std, median, min, max, peak-to-avg ratio, night-to-day ratio, zero-reading fraction, load factor, drop ratio, DTW distance, peer z-score, tamper severity).
- **Engine B (Unsupervised Novelty)**: `IsolationForest` fitted strictly on healthy profiles ($\text{theft} = 0$) to calculate an anomaly score ($0.0 \to 1.0$) for novel/zero-day bypass techniques.
- **Feeder Mass-Balance Residual Engine**:
  $$\text{Loss}_{\text{unaccounted}} = E_{\text{feeder}} - (\sum E_{\text{meters}} + \text{Technical Loss}_{\text{standard}})$$
  Injects feeder-level leakage into the consumer risk weights.

### Module 3: Time-Series Anomalies & Risk Trends
- **Changepoint Detection**: Rolling two-sample Student's t-test ($p < 0.01$) identifying the precise datetime of persistent step-down drops.
- **Risk Trajectory Tracker**: 4-window sliding progression tracker (`LOW` $\to$ `MEDIUM` $\to$ `HIGH` $\to$ `CRITICAL`).
- **Solar Disaggregation Filter**: Identifies characteristic diurnal solar bell-curve generation dips (11:00 AM–3:00 PM) to eliminate false alarms on net-metered solar roofs.

### Module 4: Explainability & Alert Engine
- **TreeExplainer SHAP Values**: Calculates feature attributions for predictions.
- **Deterministic Plain-Language Translation**: Translates top 3 contributing factors into actionable audit strings (e.g. *"Sharp consumption drop of 62.4% below historical baseline"*, *"Severe peer cohort divergence: consumer consumes 2.45 standard deviations below neighbors"*).
- **Hardware Register Correlation**: Directly correlates physical tamper registers (`REVERSE_CURRENT`, `NEUTRAL_TAMPER`, `MAGNETIC_TAMPER`).

### Module 5 & 6: Valuation, Prioritization & Action Directives
- **Uncertainty-Aware Loss Bounds**: $\Delta E = \max(0, E_{\text{expected}} - E_{\text{actual}})$ with 95% confidence interval ($\mu \pm 1.96\sigma$).
- **Dynamic Tariff Slabs**: Applies class-specific tariffs (Residential tiers, Commercial, Industrial, Agricultural) and 25% regulatory unauthorized extraction surcharges.
- **Net Yield ROI**: $\text{Net Yield} = \text{Loss}_{\text{financial}} - \text{EstimatedDispatchCost}$ (Default dispatch cost: $50.00).
- **Composite Priority Index (0–100)**:
  $$\text{Priority} = 100 \times [w_1(\text{Risk}) + w_2(\text{Anomaly}) + w_3(\text{NormalizedLoss}) + w_4(\text{Confidence})]$$
- **Action Directives Rule Engine**:
  - `PRIORITY_PHYSICAL_RAID`: High theft probability ($> 0.65$), critical tamper flag, or loss $\ge \$350$.
  - `METER_CALIBRATION_TEST`: Moderate risk ($0.40 - 0.65$) or suspected CT drift.
  - `REMOTE_FIRMWARE_AUDIT`: Cover open or anomalous zero-reading patterns.
  - `WATCHLIST_7_DAY_MONITOR`: Low-medium score with early changepoint trajectory.
- **Safety Hazards**: Flags `SECURITY_ESCORT_REQUIRED` based on customer hazard history and raid thresholds.

### Module 7: Geospatial Hotspots & Route Optimization
- **Spatial Hotspot Detector**: Haversine metric DBSCAN clustering on GPS coordinates of active alerts to identify geographic theft clusters.
- **Vehicle Route Optimizer (TSP Solver)**: Heuristic Travelling Salesperson Problem solver combining Greedy Nearest Neighbor with 2-opt local search optimization, outputting an ordered waypoint sequence, leg distances in km, transit times at 30 km/h urban speed, and estimated tour duration.
- **Feeder Vulnerability Index (FVI)**:
  $$\text{FVI} = 0.40(\text{HighRiskFraction}) + 0.35(\text{UnaccountedLossFraction}) + 0.25(\text{LossDensity})$$

### Module 8: Field Operations & Closed-Loop Retraining
- **Standardized Field Classifications**:
  - `CONFIRMED_THEFT_BYPASS`
  - `METER_FAULT`
  - `GENUINE_USAGE_CHANGE`
  - `PREMISES_VACANT`
  - `REINSPECTION_REQUIRED`
- **Geo-Tagged Evidence Storage**: Validated multipart file upload storing site photos securely under `/uploads/evidence/` with timestamp, GPS coordinates, and photo type.
- **Legal Dispute Dossier**: Exports structured machine-readable JSON case files certifying telemetry, baseline curves, inspection notes, photos, and a legal SHA-256 cryptographic verification hash.
- **Active Learning Pipeline**: Asynchronous background endpoint pulling confirmed field inspection ground truth, appending to training data, retraining models, validating holdout metrics, and hot-swapping model artifacts safely.
- **Whistleblower Tip Intake**: Correlates anonymous community tips with nearby smart meters and anomaly scores.

---

## 5. RESTful API Specification

### A. System & Ingestion (`/api/v1/system`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/system/ingest/dataset` | Inspects schema, normalizes time-series, populates DB, trains baseline ML models |
| `GET` | `/api/v1/system/health` | System health, database connection, model version, operational weights |

### B. Profiling & Detection (`/api/v1/detection`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/detection/evaluate/consumer/{consumer_id}` | Dual-engine inference, baseline profiling, and loss estimation for a consumer |
| `POST` | `/api/v1/detection/batch-run` | Batch scoring across meters on a feeder/zone, generating alerts |
| `GET` | `/api/v1/detection/baseline/{consumer_id}` | 24h diurnal curve, std, 95% confidence bounds, DTW distance |
| `GET` | `/api/v1/detection/changepoints/{consumer_id}` | Detected changepoints (rolling t-test) and 4-window risk trajectory |

### C. Alerts & Explainability (`/api/v1/alerts`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/alerts/` | Query active alerts with filtering (risk level, tariff class, feeder, status) |
| `GET` | `/api/v1/alerts/{alert_id}/evidence` | Deep SHAP attributions, plain-language text, hardware tamper registers, energy curves |

### D. Economic Valuation & Prioritization (`/api/v1/prioritization`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/prioritization/manifest` | Daily prioritized inspection dispatch manifest ranked by composite score |
| `POST` | `/api/v1/prioritization/adjust-weights` | Update operational weighting factors ($w_1, w_2, w_3, w_4$) |

### E. Geospatial & Fleet Logistics (`/api/v1/geospatial`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/geospatial/hotspots` | DBSCAN geo-clustered theft hotspots, aggregate unbilled kWh, vulnerability tiers |
| `POST` | `/api/v1/geospatial/route-optimize` | Inspector TSP route optimization from start GPS coordinates through alert stops |
| `GET` | `/api/v1/geospatial/feeder-vulnerability` | Feeder Vulnerability Index rankings |

### F. Field Operations & Audit (`/api/v1/field`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/field/inspections/submit` | Submit structured field inspection results with standard audit statuses |
| `POST` | `/api/v1/field/inspections/{inspection_id}/evidence-upload` | Geo-tagged evidence photo upload with GPS coordinates & metadata |
| `GET` | `/api/v1/field/dispute-dossier/{consumer_id}` | Export complete dispute audit dossier with SHA-256 cryptographic verification hash |

### G. Model Governance & Active Learning (`/api/v1/governance`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/governance/model/retrain` | Triggers background active learning retraining incorporating field ground truth |
| `GET` | `/api/v1/governance/model/metrics` | Precision, recall, ROC-AUC, confusion matrix, drift tracking |
| `POST` | `/api/v1/governance/whistleblower-tip` | Anonymous community tip intake with spatial-meter correlation |

---

## 6. Installation & Execution

### 1. Requirements
Ensure Python 3.10+ is installed:
```bash
python --version
```

### 2. Install Dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

### 3. Run Automated Integration Test Suite
Verify that all 18 test cases across all modules pass cleanly:
```bash
python test_api.py
```

### 4. Start the Production Dev Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI documentation will be available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 7. Interactive React Frontend (Antigravity Sci-Fi HUD)

The frontend is an interactive mission-control HUD built with React 18, Tailwind CSS, Lucide icons, and Web Audio API synthesis:

### Features
- **Top Orbit HUD**: Live telemetry beacon (`SYS_ONLINE // 8001_ACTIVE` with automatic fallback), Power Injected vs Metered, Net Divergence (`-18.4%`), Revenue Recovered, simulation play/pause toggle, and procedural Web Audio SFX synthesizer.
- **View A: Grid Surveillance & Real-Time Divergence**: 24-hour SVG load divergence curves (baseline vs metered), Feeder filters, Tamper class tags (`Direct Tap`, `Phase Inversion`, `Meter Shunt`, etc.), Quick Raid dispatch, and one-click Section 135 Search Warrant generation.
- **View B: Anomaly Diagnostic & SHAP Explainability**: Flyout modal with directional SHAP attribution bars, hourly load forensics, AI plain-language brief, Field Unit dispatch, Dispute recording, and Cryptographic SHA-256 JSON Forensic Dossier export.
- **View C: Geospatial Surveillance (Dual-Mode)**:
  - **360° Circular Hologram Sweep**: Canvas radar with phosphor decay trail, sweep beam, range rings (5 km, 10 km, 25 km), and moving patrol blips.
  - **CartoDB Dark Matter Vector Tile Map**: Interactive SVG geospatial satellite map displaying high-voltage substations, glowing feeder transmission lines with moving current particles, pulsating hotspot theft halos, interactive zoom controls (1X, 1.5X, 2X), and layer toggles.
- **Mobile Field Inspector PWA Cockpit (`FIELD INSPECTOR`)**:
  - Tablet/mobile inspection cockpit for raid crews and technical squads.
  - Dispatched target queue with distance calculations (`0.4 km`, `1.1 km`).
  - 4-Step forensic inspection workflow: Physical seal check (Intact / Broken / Missing / Cloned), optical port diagnostics, neutral shunt resistance toggle, and evidence photo snapshot simulator with SHA-256 seal badges.
  - High-security cryptographic re-sealing barcode generator (`WG-SEAL-XXXXXX-SEC`).
  - Statutory enforcement actions with digital officer signature certification under Section 135(1A).
- **Statutory Section 135 Search & Seizure Warrant Modal**:
  - Official legal warrant conforming to Sections 135 & 126 of the Electricity Act 2003.
  - Complete with order serial number, subject consumer premises, feeder line, GPS coordinates, and SHAP evidence annexure.
  - Conferred statutory search and seizure powers, penalty assessment calculations, digital magistrate seal, and squad leader sign-offs.
  - Fully formatted with `@media print` CSS for instant clean white-paper court submission or PDF export (`Ctrl + P`).
- **View D: Model Governance & Active Learning**: Confusion matrix benchmark, global feature importance distribution, drift monitoring, and active retraining trigger.
- **Encrypted Citizen Whistleblower Portal**: Confidential lead intake form for community reports.

### Running the Frontend Locally
```bash
cd web
npm install
npm run dev
```
Open **[http://localhost:5174](http://localhost:5174)** (or active port shown in terminal).

### Production Frontend Build
```bash
cd web
npm run build
```

---

## 8. Live Grid Telemetry & Anomaly Stream Generator

To simulate continuous smart meter readings, random grid frequency fluctuations, and inject realistic power theft anomalies directly into the FastAPI backend:

```bash
python tools/stream_generator.py --interval 2.0 --anomaly-rate 0.25
```

Options:
- `--interval`: Frequency in seconds between meter ticks (default: `2.0s`).
- `--anomaly-rate`: Probability of generating a theft anomaly tick (`0.0` to `1.0`, default: `0.25`).

---

## 9. Docker Compose Full-Stack Deployment

To run the complete platform (FastAPI backend + React Sci-Fi HUD frontend) in synchronized containers:

```bash
docker-compose up --build
```

- **HUD Frontend**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **API Health Check**: [http://localhost:8000/api/v1/system/health](http://localhost:8000/api/v1/system/health)
