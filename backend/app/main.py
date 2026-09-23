import os
import uuid
import shutil
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db, DBBatch, DBDailyLog, DBDiagnostic
from app.models import (
    BatchCreate, BatchResponse,
    DailyLogCreate, DailyLogResponse,
    DiagnosticResponse, DiagnosticResult
)
from app.ai_engine import run_ai_diagnosis

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AgriMind - AI-Powered Smart Agricultural Resource Engine API",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure database tables and initial seed data exist
@app.on_event("startup")
def startup_event():
    init_db()

# Mount uploads directory for serving uploaded diagnostic images
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# --- Health Check ---
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "ai_engine": "Gemini 2.5 Flash Multimodal Pipeline",
        "api_key_configured": bool(settings.GEMINI_API_KEY)
    }

# --- System Overview & Stats ---
@app.get("/api/v1/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_batches = db.query(DBBatch).count()
    active_batches = db.query(DBBatch).filter(DBBatch.status == "Active").count()
    
    batches = db.query(DBBatch).all()
    total_initial = sum(b.initial_quantity for b in batches)
    total_current = sum(b.current_quantity for b in batches)
    total_mortality = max(0, total_initial - total_current)
    
    logs = db.query(DBDailyLog).all()
    total_feed = sum(l.feed_consumed_kg for l in logs)
    total_water = sum(l.water_consumed_l for l in logs)
    
    critical_diagnostics = db.query(DBDiagnostic).filter(DBDiagnostic.severity.in_(["High", "Critical"])).count()
    recent_diagnostics = db.query(DBDiagnostic).order_by(DBDiagnostic.created_at.desc()).limit(5).all()

    return {
        "active_batches": active_batches,
        "total_batches": total_batches,
        "total_mortality": total_mortality,
        "total_feed_consumed_kg": round(total_feed, 2),
        "total_water_consumed_l": round(total_water, 2),
        "critical_alerts": critical_diagnostics,
        "recent_diagnostics_count": len(recent_diagnostics)
    }

# --- Batches API ---
@app.get("/api/v1/batches", response_model=List[BatchResponse])
def list_batches(db: Session = Depends(get_db)):
    return db.query(DBBatch).order_by(DBBatch.created_at.desc()).all()

@app.post("/api/v1/batches", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(payload: BatchCreate, db: Session = Depends(get_db)):
    batch = DBBatch(
        id=str(uuid.uuid4()),
        name=payload.name,
        batch_type=payload.batch_type,
        initial_quantity=payload.initial_quantity,
        current_quantity=payload.current_quantity if payload.current_quantity is not None else payload.initial_quantity,
        status=payload.status or "Active"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch

@app.get("/api/v1/batches/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(DBBatch).filter(DBBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

# --- Daily Telemetry Logs API ---
@app.get("/api/v1/batches/{batch_id}/logs", response_model=List[DailyLogResponse])
def get_batch_logs(batch_id: str, db: Session = Depends(get_db)):
    return db.query(DBDailyLog).filter(DBDailyLog.batch_id == batch_id).order_by(DBDailyLog.log_date.desc()).all()

@app.post("/api/v1/batches/{batch_id}/logs", response_model=DailyLogResponse, status_code=status.HTTP_201_CREATED)
def add_daily_log(batch_id: str, payload: DailyLogCreate, db: Session = Depends(get_db)):
    batch = db.query(DBBatch).filter(DBBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    log = DBDailyLog(
        id=str(uuid.uuid4()),
        batch_id=batch_id,
        log_date=payload.log_date,
        mortality_count=payload.mortality_count,
        feed_consumed_kg=payload.feed_consumed_kg,
        water_consumed_l=payload.water_consumed_l,
        notes=payload.notes
    )
    db.add(log)
    
    # Update batch current quantity if mortality count is added
    if payload.mortality_count > 0:
        batch.current_quantity = max(0, batch.current_quantity - payload.mortality_count)
        db.add(batch)

    db.commit()
    db.refresh(log)
    return log

# --- AI Diagnostics API ---
@app.post("/api/v1/diagnose")
async def diagnose_health(
    file: UploadFile = File(...),
    batch_type: str = Form("Poultry"),
    batch_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(""),
    db: Session = Depends(get_db)
):
    """
    Multimodal visual diagnostic endpoint.
    Accepts file upload + batch_type, queries Gemini 2.5 Flash, returns structured JSON diagnostic & saves to database.
    """
    # Read image contents
    contents = await file.read()
    
    # Save image to upload folder
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    image_url = f"/uploads/{filename}"

    # Execute AI visual inspection pipeline
    diagnostic_result: DiagnosticResult = run_ai_diagnosis(
        image_bytes=contents,
        batch_type=batch_type,
        notes=notes or ""
    )

    # Convert Pydantic result to dict for JSON DB storage
    treatment_plan_json = {
        "symptom_analysis": diagnostic_result.symptom_analysis,
        "immediate_actions": diagnostic_result.immediate_actions,
        "medication_or_inputs": diagnostic_result.medication_or_inputs,
        "preventative_measures": diagnostic_result.preventative_measures,
        "isolation_required": diagnostic_result.isolation_required,
        "resource_adjustments": diagnostic_result.resource_adjustments.dict()
    }

    # Save diagnostic to DB
    diag_record = DBDiagnostic(
        id=str(uuid.uuid4()),
        batch_id=batch_id if batch_id and batch_id != "undefined" else None,
        image_url=image_url,
        detected_issue=diagnostic_result.detected_issue,
        severity=diagnostic_result.severity,
        confidence_score=diagnostic_result.confidence_score,
        treatment_plan=treatment_plan_json
    )
    
    db.add(diag_record)
    db.commit()
    db.refresh(diag_record)

    return {
        "id": diag_record.id,
        "batch_id": diag_record.batch_id,
        "image_url": image_url,
        "detected_issue": diagnostic_result.detected_issue,
        "severity": diagnostic_result.severity,
        "confidence_score": diagnostic_result.confidence_score,
        "treatment_plan": treatment_plan_json,
        "created_at": diag_record.created_at
    }

@app.get("/api/v1/diagnostics")
def list_diagnostics(db: Session = Depends(get_db)):
    return db.query(DBDiagnostic).order_by(DBDiagnostic.created_at.desc()).all()

@app.get("/api/v1/diagnostics/{diag_id}")
def get_diagnostic(diag_id: str, db: Session = Depends(get_db)):
    diag = db.query(DBDiagnostic).filter(DBDiagnostic.id == diag_id).first()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnostic report not found")
    return diag
