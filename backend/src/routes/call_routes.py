from fastapi import APIRouter, HTTPException, Request, Response
from src.schemas.call_schemas import OutboundCallRequest, CallStatusUpdate
from src.services.exotel.service import exotel_service
from src.utils.db import db
import logging
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/outbound")
async def trigger_call(request: OutboundCallRequest):
    try:
        result = await exotel_service.trigger_outbound_call(
            phone_number=request.phone_number,
            customer_name=request.customer_name
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Failed to trigger call: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhooks/exotel")
async def exotel_webhook(request: Request):
    form_data = await request.form()
    data = dict(form_data)
    
    call_sid = data.get("CallSid")
    status = data.get("Status")
    
    logger.info(f"Exotel Webhook received: CallSid={call_sid}, Status={status}")
    
    if call_sid:
        await db.db.calls.update_one(
            {"call_sid": call_sid},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow(),
                    "metadata": data
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
    
    return Response(status_code=200)
