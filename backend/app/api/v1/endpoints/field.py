"""WattGuard AI - Field Inspector Operations & Dispute Dossier Endpoints
/api/v1/field:
- POST /inspections/submit: Submit structured field inspection outcome.
- POST /inspections/{inspection_id}/evidence-upload: Secure multipart upload of geo-tagged evidence photos.
- GET /dispute-dossier/{consumer_id}: Export full dispute resolution case dossier.
"""
import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.models.inspection import Inspection
from app.models.alert import Alert
from app.models.consumer import Consumer
from app.models.meter_reading import MeterReading
from app.schemas.field_schema import (
    InspectionSubmitRequest,
    InspectionSubmitResponse,
    EvidenceUploadResponse,
    DisputeDossierResponse
)
from app.ml.active_learner import active_learner_instance

router = APIRouter()

VALID_AUDIT_STATUSES = {
    "CONFIRMED_THEFT_BYPASS",
    "METER_FAULT",
    "GENUINE_USAGE_CHANGE",
    "PREMISES_VACANT",
    "REINSPECTION_REQUIRED"
}


@router.post("/inspections/submit", response_model=InspectionSubmitResponse, summary="Submit Field Inspection Result")
async def submit_inspection(
    req: InspectionSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    """Submits a structured field inspection result with standardized audit status."""
    status_upper = req.audit_status.strip().upper()
    if status_upper not in VALID_AUDIT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audit_status '{req.audit_status}'. Must be one of: {sorted(list(VALID_AUDIT_STATUSES))}"
        )

    consumer = await db.scalar(select(Consumer).where(Consumer.consumer_id == req.consumer_id))
    if not consumer:
        raise HTTPException(status_code=404, detail=f"Consumer {req.consumer_id} not found.")

    inspection_id = f"INS-{uuid.uuid4().hex[:8].upper()}"
    inspection_obj = Inspection(
        inspection_id=inspection_id,
        alert_id=req.alert_id,
        consumer_id=req.consumer_id,
        inspector_id=req.inspector_id,
        audit_status=status_upper,
        meter_serial=req.meter_serial,
        seal_number=req.seal_number,
        observed_load=req.observed_load,
        inspector_notes=req.inspector_notes,
        photo_evidence_paths="[]",
        photo_metadata="[]",
        inspection_timestamp=req.inspection_timestamp or datetime.now(timezone.utc)
    )
    db.add(inspection_obj)

    # If linked to an alert, update alert status to INSPECTED
    if req.alert_id:
        alert = await db.scalar(select(Alert).where(Alert.alert_id == req.alert_id))
        if alert:
            alert.status = "INSPECTED"

    await db.commit()

    return InspectionSubmitResponse(
        inspection_id=inspection_id,
        consumer_id=req.consumer_id,
        alert_id=req.alert_id,
        audit_status=status_upper,
        status="SUCCESS",
        message="Field inspection submitted successfully.",
        timestamp=datetime.now(timezone.utc)
    )


@router.post("/inspections/{inspection_id}/evidence-upload", response_model=EvidenceUploadResponse, summary="Upload Site Evidence Image")
async def upload_inspection_evidence(
    inspection_id: str,
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    photo_type: str = Form("METER_SEAL_CLOSEUP", description="METER_SEAL_CLOSEUP, BYPASS_TAP_PANEL, TERMINAL_BOX, SITE_OVERVIEW"),
    db: AsyncSession = Depends(get_db)
):
    """Manages secure multipart upload of evidence images, verifying file format,
    capturing GPS coordinate and timestamp metadata, and saving to encrypted/local storage.
    """
    inspection = await db.scalar(select(Inspection).where(Inspection.inspection_id == inspection_id))
    if not inspection:
        raise HTTPException(status_code=404, detail=f"Inspection record '{inspection_id}' not found.")

    # Validate file extension
    file_ext = Path(file.filename or "evidence.jpg").suffix.lower()
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format '{file_ext}'. Allowed formats: {settings.ALLOWED_IMAGE_EXTENSIONS}"
        )

    # Read content and validate size
    content = await file.read()
    if len(content) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size limit of {settings.MAX_IMAGE_SIZE_MB} MB."
        )

    # Generate secure storage path
    file_id = f"EVD-{uuid.uuid4().hex[:12].upper()}{file_ext}"
    dest_path = settings.UPLOAD_DIR / file_id
    with open(dest_path, "wb") as f:
        f.write(content)

    # Update inspection record metadata
    existing_paths = json.loads(inspection.photo_evidence_paths or "[]")
    existing_meta = json.loads(inspection.photo_metadata or "[]")

    metadata_entry = {
        "file_id": file_id,
        "file_path": str(dest_path),
        "photo_type": photo_type,
        "latitude": latitude,
        "longitude": longitude,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "size_bytes": len(content)
    }

    existing_paths.append(str(dest_path))
    existing_meta.append(metadata_entry)

    inspection.photo_evidence_paths = json.dumps(existing_paths)
    inspection.photo_metadata = json.dumps(existing_meta)
    await db.commit()

    return EvidenceUploadResponse(
        inspection_id=inspection_id,
        file_id=file_id,
        file_path=str(dest_path),
        file_size_bytes=len(content),
        content_type=file.content_type or "image/jpeg",
        captured_metadata=metadata_entry,
        message="Evidence photo securely stored and linked to inspection record."
    )


@router.get("/dispute-dossier/{consumer_id}", response_model=DisputeDossierResponse, summary="Export Legal Dispute Audit Dossier")
async def get_dispute_dossier(consumer_id: str, db: AsyncSession = Depends(get_db)):
    """Exports full case dossier combining meter telemetry, baseline anomalies,
    inspection outcomes, and evidentiary timestamps into structured machine-readable JSON exports.
    """
    consumer = await db.scalar(select(Consumer).where(Consumer.consumer_id == consumer_id))
    if not consumer:
        raise HTTPException(status_code=404, detail="Consumer not found")

    # Fetch alerts history
    alerts_rows = (await db.scalars(
        select(Alert).where(Alert.consumer_id == consumer_id).order_by(Alert.created_at.desc())
    )).all()
    alerts_data = [{
        "alert_id": a.alert_id,
        "risk_tier": a.risk_tier,
        "composite_priority": a.composite_priority,
        "estimated_unbilled_kwh": a.estimated_unbilled_kwh,
        "estimated_loss_currency": a.estimated_loss_currency,
        "loss_lower_bound_95": a.loss_lower_bound_95,
        "loss_upper_bound_95": a.loss_upper_bound_95,
        "recommended_action": a.recommended_action,
        "tamper_evidence": a.hardware_tamper_evidence,
        "created_at": a.created_at.isoformat()
    } for a in alerts_rows]

    # Fetch inspection record if any
    inspection = await db.scalar(
        select(Inspection).where(Inspection.consumer_id == consumer_id).order_by(Inspection.created_at.desc())
    )
    inspection_data = None
    photos_data = []
    if inspection:
        inspection_data = {
            "inspection_id": inspection.inspection_id,
            "inspector_id": inspection.inspector_id,
            "audit_status": inspection.audit_status,
            "meter_serial": inspection.meter_serial,
            "seal_number": inspection.seal_number,
            "observed_load_kw": inspection.observed_load,
            "inspector_notes": inspection.inspector_notes,
            "inspection_timestamp": inspection.inspection_timestamp.isoformat()
        }
        photos_data = json.loads(inspection.photo_metadata or "[]")

    # Readings summary
    readings = (await db.scalars(
        select(MeterReading).where(MeterReading.consumer_id == consumer_id).order_by(MeterReading.timestamp)
    )).all()
    
    total_consumed = sum(r.energy_kwh for r in readings) if readings else 0.0
    mean_consumed = total_consumed / max(1, len(readings))

    telemetry_summary = {
        "total_recorded_hours": len(readings),
        "total_billed_kwh": round(total_consumed, 2),
        "mean_hourly_kwh": round(mean_consumed, 3),
        "start_timestamp": readings[0].timestamp.isoformat() if readings else None,
        "end_timestamp": readings[-1].timestamp.isoformat() if readings else None
    }

    consumer_dict = {
        "consumer_id": consumer.consumer_id,
        "tariff_class": consumer.tariff_class,
        "sanctioned_load_kw": consumer.sanctioned_load_kw,
        "feeder_id": consumer.feeder_id,
        "transformer_id": consumer.transformer_id
    }

    dossier = active_learner_instance.compile_dispute_dossier(
        consumer_data=consumer_dict,
        alerts_data=alerts_data,
        inspection_data=inspection_data,
        readings_summary=telemetry_summary,
        evidence_photos=photos_data
    )

    return DisputeDossierResponse(**dossier)
