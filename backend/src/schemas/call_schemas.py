from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class OutboundCallRequest(BaseModel):
    phone_number: str = Field(..., description="Customer phone number with country code")
    customer_name: str = Field(..., description="Customer name for personalization")

class CallStatusUpdate(BaseModel):
    CallSid: str
    Status: str
    EventType: Optional[str] = None

class TranscriptCreate(BaseModel):
    call_id: str
    transcript: str
    duration: float
    call_status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
