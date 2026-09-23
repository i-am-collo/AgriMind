import os
import json
import uuid
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, JSON, DateTime, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from app.config import settings

# Handle SQLite vs Postgres engine options
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBBatch(Base):
    __tablename__ = "batches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    batch_type = Column(String(50), nullable=False) # Poultry, Crops, Livestock
    initial_quantity = Column(Integer, nullable=False)
    current_quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="Active") # Active, Harvested, Quarantined
    created_at = Column(DateTime, default=datetime.utcnow)
    
    logs = relationship("DBDailyLog", back_populates="batch", cascade="all, delete-orphan")
    diagnostics = relationship("DBDiagnostic", back_populates="batch", cascade="all, delete-orphan")

class DBDailyLog(Base):
    __tablename__ = "daily_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String, ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, default=date.today)
    mortality_count = Column(Integer, default=0)
    feed_consumed_kg = Column(Float, default=0.0)
    water_consumed_l = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    batch = relationship("DBBatch", back_populates="logs")

class DBDiagnostic(Base):
    __tablename__ = "diagnostics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String, ForeignKey("batches.id", ondelete="CASCADE"), nullable=True)
    image_url = Column(Text, nullable=True)
    detected_issue = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False) # Low, Medium, High, Critical
    confidence_score = Column(Float, nullable=False)
    treatment_plan = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    batch = relationship("DBBatch", back_populates="diagnostics")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed initial data if batches table is empty
        if db.query(DBBatch).count() == 0:
            b1_id = "b1111111-1111-1111-1111-111111111111"
            b2_id = "b2222222-2222-2222-2222-222222222222"
            b3_id = "b3333333-3333-3333-3333-333333333333"

            b1 = DBBatch(
                id=b1_id,
                name="Cobb 500 Broiler Flock A",
                batch_type="Poultry",
                initial_quantity=500,
                current_quantity=488,
                status="Active"
            )
            b2 = DBBatch(
                id=b2_id,
                name="Maize Plot #3 (North Field)",
                batch_type="Crops",
                initial_quantity=1200,
                current_quantity=1180,
                status="Active"
            )
            b3 = DBBatch(
                id=b3_id,
                name="Dairy Holstein Herd B",
                batch_type="Livestock",
                initial_quantity=45,
                current_quantity=45,
                status="Active"
            )
            db.add_all([b1, b2, b3])

            # Logs for b1
            today = date.today()
            l1 = DBDailyLog(
                batch_id=b1_id,
                log_date=today - timedelta(days=2),
                mortality_count=2,
                feed_consumed_kg=85.5,
                water_consumed_l=190.0,
                notes="Normal behavior, appetite consistent."
            )
            l2 = DBDailyLog(
                batch_id=b1_id,
                log_date=today - timedelta(days=1),
                mortality_count=4,
                feed_consumed_kg=82.0,
                water_consumed_l=185.0,
                notes="Slightly reduced feed intake in northern coop section."
            )
            l3 = DBDailyLog(
                batch_id=b1_id,
                log_date=today,
                mortality_count=6,
                feed_consumed_kg=76.0,
                water_consumed_l=175.0,
                notes="Observed lethargy in 8 birds. Submitted image for AI inspection."
            )
            # Logs for b2
            l4 = DBDailyLog(
                batch_id=b2_id,
                log_date=today - timedelta(days=1),
                mortality_count=10,
                feed_consumed_kg=0.0,
                water_consumed_l=450.0,
                notes="Irrigation cycle complete. Spotted yellowing on lower leaves."
            )
            l5 = DBDailyLog(
                batch_id=b2_id,
                log_date=today,
                mortality_count=10,
                feed_consumed_kg=0.0,
                water_consumed_l=450.0,
                notes="Nitrogen foliar spray applied."
            )
            db.add_all([l1, l2, l3, l4, l5])

            # Initial Diagnostic
            d1 = DBDiagnostic(
                id="d1111111-1111-1111-1111-111111111111",
                batch_id=b1_id,
                image_url="/uploads/poultry_sample.jpg",
                detected_issue="Coccidiosis (Eimeria infection)",
                severity="High",
                confidence_score=94.50,
                treatment_plan={
                    "symptom_analysis": ["Ruffled feathers", "Lethargy", "Pale wattles", "Diarrhea"],
                    "immediate_actions": [
                        "Isolate affected birds immediately to containment pen 2.",
                        "Sanitize all drinking troughs with chlorine dioxide (2 ppm).",
                        "Increase coop ventilation by 15%."
                    ],
                    "medication_or_inputs": [
                        "Administer Amprolium 9.6% solution via drinking water for 5 consecutive days (10 ml per gallon).",
                        "Provide vitamin K3 supplement to reduce intestinal hemorrhaging."
                    ],
                    "preventative_measures": [
                        "Replace damp litter with dry pine shavings.",
                        "Keep litter moisture below 25%."
                    ],
                    "isolation_required": True,
                    "resource_adjustments": {
                        "feed_recommendation": "Switch to pre-starter crumb with probiotic additives; reduce high-fat protein intake by 10%.",
                        "water_recommendation": "Increase clean electrolyte water availability by 20% to prevent dehydration."
                    }
                }
            )
            db.add(d1)
            db.commit()
    finally:
        db.close()
