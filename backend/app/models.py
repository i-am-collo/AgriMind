from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# --- Resource Adjustments Schema ---
class ResourceAdjustments(BaseModel):
    feed_recommendation: str = Field(description="Actionable feed adjustment advice")
    water_recommendation: str = Field(description="Actionable water adjustment advice")

# --- Structured AI Diagnostic Response Schema ---
class DiagnosticResult(BaseModel):
    detected_issue: str = Field(description="Identified disease, pest, deficiency, or anatomical issue")
    severity: str = Field(description="One of: Low, Medium, High, Critical")
    confidence_score: float = Field(description="Confidence percentage from 0.0 to 100.0")
    symptom_analysis: List[str] = Field(description="Key visual symptoms identified in the photo")
    immediate_actions: List[str] = Field(description="Immediate containment or urgent steps")
    medication_or_inputs: List[str] = Field(description="Recommended treatments, remedies, or nutritional inputs")
    preventative_measures: List[str] = Field(description="Steps to prevent recurrence or flock spread")
    isolation_required: bool = Field(description="Whether affected specimen must be quarantined immediately")
    resource_adjustments: ResourceAdjustments = Field(description="Feed and water telemetry adjustments")

# --- DB Models & Payloads ---
class BatchBase(BaseModel):
    name: str
    batch_type: str # Poultry, Crops, Livestock
    initial_quantity: int
    current_quantity: Optional[int] = None
    status: Optional[str] = "Active"

class BatchCreate(BatchBase):
    pass

class BatchResponse(BatchBase):
    id: str
    current_quantity: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DailyLogBase(BaseModel):
    batch_id: str
    log_date: Optional[date] = None
    mortality_count: int = 0
    feed_consumed_kg: float = 0.0
    water_consumed_l: float = 0.0
    notes: Optional[str] = None

class DailyLogCreate(DailyLogBase):
    pass

class DailyLogResponse(DailyLogBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DiagnosticResponse(BaseModel):
    id: str
    batch_id: Optional[str]
    image_url: Optional[str]
    detected_issue: str
    severity: str
    confidence_score: float
    treatment_plan: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
