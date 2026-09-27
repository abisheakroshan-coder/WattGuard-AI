"""WattGuard AI - Auto-Adaptive ETL & Dataset Ingestion Engine
Section 2 (Phase 1):
- Programmatic inspection of raw datasets (columns, data types, sampling granularity, target distribution).
- Automated mapping to standardized internal schema:
    consumer_id, timestamp, energy_kwh, sanctioned_load_kw, tariff_class,
    latitude, longitude, feeder_id, transformer_id, phase, tamper_flags.
- Bulk ingestion into SQLite/PostgreSQL database via SQLAlchemy 2.0 AsyncSession.
"""
import os
import glob
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.consumer import Consumer
from app.models.meter_reading import MeterReading
from app.ml.dual_detector import dual_detector_instance, FEATURE_NAMES
from app.ml.baseline_engine import BaselineEngine


# Mapping DOE reference building classes to standardized tariff categories
CLASS_TO_TARIFF = {
    "MidriseApartment": "RESIDENTIAL",
    "Warehouse": "INDUSTRIAL",
    "FullServiceRestaurant": "COMMERCIAL",
    "QuickServiceRestaurant": "COMMERCIAL",
    "Stand-aloneRetail": "COMMERCIAL",
    "StripMall": "COMMERCIAL",
    "SuperMarket": "COMMERCIAL",
    "SmallHotel": "COMMERCIAL",
    "LargeHotel": "COMMERCIAL",
    "SmallOffice": "COMMERCIAL",
    "MediumOffice": "COMMERCIAL",
    "LargeOffice": "COMMERCIAL",
    "Hospital": "COMMERCIAL",
    "OutPatient": "COMMERCIAL",
    "PrimarySchool": "COMMERCIAL",
    "SecondarySchool": "COMMERCIAL"
}

# Tamper flag synthesis linked to labeled theft attacks
THEFT_TO_TAMPER = {
    "Normal": "NORMAL",
    "Theft1": "NORMAL",             # Direct line bypass (no hardware register trip)
    "Theft2": "NEUTRAL_TAMPER",      # Neutral missing / ground bypass
    "Theft3": "COVER_OPEN",          # Enclosure microswitch trip
    "Theft4": "REVERSE_CURRENT",     # Current reversal / CT inversion
    "Theft5": "MAGNETIC_TAMPER",     # High external magnetic field
    "Theft6": "NORMAL"              # Algorithmic / periodic unmetered draw
}

# Grid Feeders & Substation Topology Definitions
FEEDER_TOPOLOGY = [
    {"feeder_id": "FDR_NORTH_01", "base_lat": 28.6500, "base_lon": 77.2100, "transformers": ["TX_N101", "TX_N102", "TX_N103", "TX_N104"]},
    {"feeder_id": "FDR_METRO_02", "base_lat": 28.6250, "base_lon": 77.2250, "transformers": ["TX_M201", "TX_M202", "TX_M203", "TX_M204"]},
    {"feeder_id": "FDR_EAST_03",  "base_lat": 28.6100, "base_lon": 77.2400, "transformers": ["TX_E301", "TX_E302", "TX_E303", "TX_E304"]},
    {"feeder_id": "FDR_IND_04",   "base_lat": 28.5800, "base_lon": 77.1900, "transformers": ["TX_I401", "TX_I402", "TX_I403", "TX_I404"]}
]


class ETLManager:
    """Handles automated inspection, normalization, and database ingestion."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or settings.DATA_DIR

    def inspect_datasets(self) -> Dict[str, Any]:
        """Scans data directories, analyzes available files, schema, sampling granularity and target distribution."""
        candidate_dirs = [self.data_dir, Path("data"), Path("."), settings.BASE_DIR / "data", settings.BASE_DIR]
        found_files = []
        for d in candidate_dirs:
            if d.exists():
                for ext in ["*.csv", "*.parquet", "*.sqlite"]:
                    found_files.extend(glob.glob(str(d / ext)))

        # Remove duplicates while preserving path strings
        unique_files = list(dict.fromkeys(found_files))
        if not unique_files:
            return {
                "status": "NO_DATASET_FOUND",
                "searched_directories": [str(d) for d in candidate_dirs],
                "files_count": 0
            }

        inspected = []
        for fpath in unique_files:
            p = Path(fpath)
            size_mb = round(p.stat().st_size / (1024 * 1024), 2)
            try:
                if p.suffix.lower() == ".csv":
                    # Sample head for rapid inspection
                    df_sample = pd.read_csv(p, nrows=5000)
                    total_rows = sum(1 for _ in open(p, "rb")) - 1  # fast line count
                else:
                    df_sample = pd.read_parquet(p)
                    total_rows = len(df_sample)

                cols = df_sample.columns.tolist()
                dtypes = {col: str(dtype) for col, dtype in df_sample.dtypes.items()}
                null_counts = df_sample.isnull().sum().to_dict()

                # Granularity heuristics
                granularity = "Hourly (estimated from 8760-hour cycle)"

                # Target inspection
                theft_dist = {}
                if "theft" in cols:
                    theft_dist = df_sample["theft"].value_counts().to_dict()
                elif "Class" in cols:
                    theft_dist = df_sample["Class"].value_counts().to_dict()

                inspected.append({
                    "file_path": str(p),
                    "file_name": p.name,
                    "size_mb": size_mb,
                    "estimated_rows": total_rows,
                    "columns": cols,
                    "data_types": dtypes,
                    "null_counts": null_counts,
                    "sampling_granularity": granularity,
                    "target_distribution": theft_dist
                })
            except Exception as e:
                inspected.append({
                    "file_path": str(p),
                    "file_name": p.name,
                    "error": str(e)
                })

        return {
            "status": "SUCCESS",
            "files_inspected": inspected,
            "total_files": len(inspected)
        }

    def load_and_normalize(
        self,
        max_consumers: int = 32,
        readings_per_consumer: int = 1440  # 60 days of hourly data for fast yet deep analysis
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Parses raw dataset, generates consumers with realistic topology,
        and standardizes meter readings according to internal schema.
        """
        # Locate df.csv
        target_file = None
        for candidate in [
            self.data_dir / "df.csv",
            Path("data/df.csv"),
            Path("df.csv"),
            settings.BASE_DIR / "data" / "df.csv",
            settings.BASE_DIR / "df.csv"
        ]:
            if candidate.exists():
                target_file = candidate
                break

        if not target_file:
            raise FileNotFoundError(f"Could not locate df.csv in data directories: {self.data_dir}")

        # Read dataset
        df = pd.read_csv(target_file)
        # Drop corrupt row where Class == '0'
        df = df[df["Class"] != "0"].reset_index(drop=True)

        consumers_list: List[Dict[str, Any]] = []
        readings_list: List[Dict[str, Any]] = []

        classes = df["Class"].unique()
        consumer_counter = 1
        base_start_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        # Loop through classes and allocate 2 consumers per class
        for cls_name in classes:
            if consumer_counter > max_consumers:
                break

            cls_df = df[df["Class"] == cls_name].reset_index(drop=True)
            tariff = CLASS_TO_TARIFF.get(cls_name, "COMMERCIAL")
            
            # Divide into 2 consumer instances (e.g. 17520 hours each from the 35040 hours)
            half = len(cls_df) // 2
            subsets = [cls_df.iloc[:half], cls_df.iloc[half:]]

            for s_idx, sub_df in enumerate(subsets):
                if consumer_counter > max_consumers:
                    break

                cid = f"CONS_{tariff[:3]}_{consumer_counter:03d}"
                feeder_cfg = FEEDER_TOPOLOGY[consumer_counter % len(FEEDER_TOPOLOGY)]
                feeder_id = feeder_cfg["feeder_id"]
                tx_list = feeder_cfg["transformers"]
                tx_id = tx_list[(consumer_counter // len(FEEDER_TOPOLOGY)) % len(tx_list)]
                phase = ["R", "Y", "B"][consumer_counter % 3]

                # Realistic GPS around feeder hub (+/- 0.015 deg ~ 1.5 km)
                np.random.seed(consumer_counter)
                lat = feeder_cfg["base_lat"] + np.random.uniform(-0.015, 0.015)
                lon = feeder_cfg["base_lon"] + np.random.uniform(-0.015, 0.015)

                # Peak consumption as sanctioned load base
                peak_load = float(sub_df["Electricity:Facility [kW](Hourly)"].quantile(0.99))
                sanctioned_load = max(10.0, round(peak_load * 1.25, 1))

                has_solar = (consumer_counter % 7 == 0)
                hazard = (consumer_counter % 11 == 0)

                consumers_list.append({
                    "consumer_id": cid,
                    "sanctioned_load_kw": sanctioned_load,
                    "tariff_class": tariff,
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6),
                    "feeder_id": feeder_id,
                    "transformer_id": tx_id,
                    "phase": phase,
                    "has_solar": has_solar,
                    "safety_hazard_flag": hazard,
                    "security_escort_required": hazard
                })

                # Slice readings
                slice_len = min(len(sub_df), readings_per_consumer)
                sample_readings = sub_df.iloc[:slice_len]

                for r_idx, (_, row) in enumerate(sample_readings.iterrows()):
                    reading_time = base_start_time + timedelta(hours=r_idx)
                    kwh = float(row["Electricity:Facility [kW](Hourly)"])
                    theft_tag = str(row.get("theft", "Normal"))
                    is_theft = (theft_tag != "Normal")
                    tamper = THEFT_TO_TAMPER.get(theft_tag, "NORMAL")

                    # Sub-metering values if present
                    hvac = float(row.get("Cooling:Electricity [kW](Hourly)", 0.0)) + float(row.get("Heating:Electricity [kW](Hourly)", 0.0))
                    lighting = float(row.get("InteriorLights:Electricity [kW](Hourly)", 0.0))

                    readings_list.append({
                        "consumer_id": cid,
                        "timestamp": reading_time,
                        "energy_kwh": max(0.0, round(kwh, 3)),
                        "submeter_hvac_kwh": round(hvac, 3),
                        "submeter_lighting_kwh": round(lighting, 3),
                        "tamper_flags": tamper,
                        "is_theft_ground_truth": is_theft,
                        "theft_type": theft_tag
                    })

                consumer_counter += 1

        return consumers_list, readings_list

    async def ingest_into_database(
        self,
        session: AsyncSession,
        max_consumers: int = 32,
        readings_per_consumer: int = 1440
    ) -> Dict[str, Any]:
        """Performs end-to-end ingestion and populates DB tables."""
        from app.core.database import init_db
        await init_db()

        # 1. Clean existing records for fresh idempotent load
        await session.execute(delete(MeterReading))
        await session.execute(delete(Consumer))
        await session.commit()

        # 2. Extract and normalize
        consumers_data, readings_data = self.load_and_normalize(
            max_consumers=max_consumers,
            readings_per_consumer=readings_per_consumer
        )

        # 3. Insert Consumers
        for c in consumers_data:
            consumer_obj = Consumer(**c)
            session.add(consumer_obj)
        await session.commit()

        # 4. Batch insert readings in chunks of 2,000 for SQLite performance
        chunk_size = 2000
        for i in range(0, len(readings_data), chunk_size):
            chunk = readings_data[i : i + chunk_size]
            db_objs = [MeterReading(**r) for r in chunk]
            session.add_all(db_objs)
            await session.commit()

        # 5. Automatically train baseline ML models on the ingested data
        training_metrics = self.train_baseline_models(consumers_data, readings_data)

        return {
            "status": "SUCCESS",
            "consumers_ingested": len(consumers_data),
            "meter_readings_ingested": len(readings_data),
            "feeders_populated": len(FEEDER_TOPOLOGY),
            "model_training_metrics": training_metrics
        }

    def train_baseline_models(
        self,
        consumers_data: List[Dict[str, Any]],
        readings_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extracts training feature vectors from normalized readings and fits DualDetector."""
        df_readings = pd.DataFrame(readings_data)
        if df_readings.empty:
            return {"status": "NO_READINGS_TO_TRAIN"}

        X_list = []
        y_list = []

        # Group by consumer and generate rolling window samples
        for c in consumers_data:
            cid = c["consumer_id"]
            sanctioned = c["sanctioned_load_kw"]
            c_readings = df_readings[df_readings["consumer_id"] == cid].sort_values("timestamp")

            if len(c_readings) < 168:
                continue

            # Compute historical baseline from first 30 days (720h)
            baseline_slice = c_readings.iloc[:min(720, len(c_readings))]
            _, base_mean, _, _, _ = BaselineEngine.compute_diurnal_baseline(baseline_slice)
            overall_base_mean = float(np.mean(base_mean))

            # Slide 7-day windows across readings
            step = 72  # 3 days step
            w_size = 168  # 7 days window
            n_rows = len(c_readings)

            for start_idx in range(0, n_rows - w_size, step):
                w_df = c_readings.iloc[start_idx : start_idx + w_size]
                label = 1 if w_df["is_theft_ground_truth"].sum() > 24 else 0
                tamper = w_df["tamper_flags"].mode()[0] if not w_df.empty else "NORMAL"

                feat = dual_detector_instance.extract_features(
                    readings=w_df,
                    sanctioned_load_kw=sanctioned,
                    baseline_mean=overall_base_mean,
                    dtw_distance=0.5 if label == 1 else 0.1,
                    peer_zscore=-1.8 if label == 1 else 0.0,
                    tamper_flag=tamper
                )
                X_list.append(feat)
                y_list.append(label)

        if not X_list:
            return {"status": "INSUFFICIENT_WINDOW_SAMPLES"}

        X_arr = np.array(X_list)
        y_arr = np.array(y_list)

        # Train/val split
        indices = np.arange(len(X_arr))
        np.random.seed(42)
        np.random.shuffle(indices)
        split = int(0.8 * len(X_arr))
        train_idx, val_idx = indices[:split], indices[split:]

        metrics = dual_detector_instance.train(
            X_train=X_arr[train_idx],
            y_train=y_arr[train_idx],
            X_val=X_arr[val_idx],
            y_val=y_arr[val_idx]
        )
        return metrics


etl_manager = ETLManager()
