"""WattGuard AI - Operator & DevOps CLI Tool
Provides convenient terminal commands for dataset ingestion, consumer evaluation,
daily dispatch manifest generation, hotspot detection, and latency benchmarking.
"""
import sys
import os
import argparse
import asyncio
import time
from pathlib import Path

# Ensure backend package is in python path
current_dir = Path(__file__).resolve().parent
if (current_dir / "app").exists():
    sys.path.insert(0, str(current_dir))
elif (current_dir / "backend" / "app").exists():
    sys.path.insert(0, str(current_dir / "backend"))

from app.core.config import settings
from app.core.database import async_session_factory, init_db
from app.core.etl import etl_manager
from app.ml.dual_detector import dual_detector_instance
from app.ml.geospatial_cluster import geospatial_cluster_engine
from app.models.consumer import Consumer
from app.models.alert import Alert
from sqlalchemy import select, func


async def cmd_health():
    """Checks database connectivity and model status."""
    print("=" * 60)
    print("WATTGUARD AI - SYSTEM HEALTH STATUS")
    print("=" * 60)
    await init_db()
    print(f"Service Name: {settings.PROJECT_NAME}")
    print(f"API Version:  {settings.VERSION}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Models Ready: {dual_detector_instance.supervised_model is not None}")
    if dual_detector_instance.metadata:
        meta = dual_detector_instance.metadata
        print(f"ROC-AUC:      {meta.get('roc_auc', 'N/A')}")
        print(f"Precision:    {meta.get('precision', 'N/A')}")
        print(f"Recall:       {meta.get('recall', 'N/A')}")
    print("=" * 60)


async def cmd_ingest(max_consumers: int, readings: int):
    """Executes dataset inspection and populates database."""
    print("=" * 60)
    print("WATTGUARD AI - INGESTION & MODEL TRAINING")
    print("=" * 60)
    await init_db()
    async with async_session_factory() as session:
        t0 = time.time()
        print(f"Starting ingestion (max_consumers={max_consumers}, readings={readings})...")
        res = await etl_manager.ingest_into_database(
            session=session,
            max_consumers=max_consumers,
            readings_per_consumer=readings
        )
        elapsed = time.time() - t0
        print(f"Status:             {res['status']}")
        print(f"Consumers Ingested: {res['consumers_ingested']}")
        print(f"Readings Ingested:  {res['meter_readings_ingested']}")
        print(f"Feeders Populated:  {res['feeders_populated']}")
        print(f"Elapsed Time:       {elapsed:.2f} seconds")
    print("=" * 60)


async def cmd_manifest(limit: int):
    """Displays prioritized inspection dispatch manifest."""
    await init_db()
    async with async_session_factory() as session:
        rows = (await session.execute(
            select(Alert, Consumer)
            .join(Consumer, Alert.consumer_id == Consumer.consumer_id)
            .where(Alert.status == "ACTIVE")
            .order_by(Alert.composite_priority.desc())
            .limit(limit)
        )).all()

        print("=" * 90)
        print(f"WATTGUARD AI - DAILY DISPATCH MANIFEST (TOP {limit})")
        print("=" * 90)
        print(f"{'Rank':<5} {'Consumer ID':<15} {'Priority':<10} {'Tier':<10} {'Action':<26} {'Net Yield ($)':<12}")
        print("-" * 90)
        for idx, (alert, consumer) in enumerate(rows, start=1):
            print(
                f"{idx:<5} {consumer.consumer_id:<15} {alert.composite_priority:<10.1f} "
                f"{alert.risk_tier:<10} {alert.recommended_action:<26} ${alert.net_roi_yield:<12.2f}"
            )
        print("=" * 90)


async def cmd_hotspots():
    """Displays active geospatial theft hotspots."""
    await init_db()
    async with async_session_factory() as session:
        rows = (await session.execute(
            select(Alert, Consumer)
            .join(Consumer, Alert.consumer_id == Consumer.consumer_id)
            .where(Alert.status == "ACTIVE")
        )).all()

        records = [{
            "alert_id": a.alert_id,
            "consumer_id": c.consumer_id,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "unbilled_kwh": a.estimated_unbilled_kwh,
            "loss_currency": a.estimated_loss_currency,
            "feeder_id": c.feeder_id
        } for a, c in rows]

        clusters = geospatial_cluster_engine.detect_hotspots(records, eps_km=3.0, min_samples=2)

        print("=" * 80)
        print("WATTGUARD AI - GEOGRAPHIC THEFT HOTSPOTS (DBSCAN)")
        print("=" * 80)
        print(f"{'ID':<4} {'Feeder':<14} {'Rating':<10} {'Meters':<8} {'Unbilled kWh':<14} {'Revenue Loss ($)':<16}")
        print("-" * 80)
        for c in clusters:
            print(
                f"{c['cluster_id']:<4} {c['feeder_id']:<14} {c['vulnerability_rating']:<10} "
                f"{c['consumer_count']:<8} {c['total_unbilled_kwh']:<14.1f} ${c['total_revenue_loss']:<16.2f}"
            )
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="WattGuard AI Command Line Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # health
    subparsers.add_parser("health", help="Check system and database health")

    # ingest
    p_ingest = subparsers.add_parser("ingest", help="Trigger dataset ingestion and model training")
    p_ingest.add_argument("--max-consumers", type=int, default=16, help="Number of consumers to ingest")
    p_ingest.add_argument("--readings", type=int, default=720, help="Readings per consumer (hours)")

    # manifest
    p_manifest = subparsers.add_parser("manifest", help="View prioritized inspection manifest")
    p_manifest.add_argument("--limit", type=int, default=10, help="Max manifest items")

    # hotspots
    subparsers.add_parser("hotspots", help="Detect geospatial theft clusters")

    args = parser.parse_args()

    if args.command == "health":
        asyncio.run(cmd_health())
    elif args.command == "ingest":
        asyncio.run(cmd_ingest(args.max_consumers, args.readings))
    elif args.command == "manifest":
        asyncio.run(cmd_manifest(args.limit))
    elif args.command == "hotspots":
        asyncio.run(cmd_hotspots())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
