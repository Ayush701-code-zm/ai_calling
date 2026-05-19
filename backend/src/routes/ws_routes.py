from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted from Exotel")
    
    stream_sid = None
    
    try:
        message = await websocket.receive_text()
        data = json.loads(message)
        
        if data.get("event") == "start":
            stream_sid = data.get("start", {}).get("streamSid")
            logger.info(f"Starting Pipecat pipeline for StreamSid: {stream_sid}")

            from src.services.pipecat.pipeline import run_pipecat_pipeline
            await run_pipecat_pipeline(websocket, stream_sid)
            
        else:
            logger.warning(f"Unexpected initial message: {data}")
            await websocket.close()

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for StreamSid: {stream_sid}")
    except Exception as e:
        logger.error(f"Error in voice websocket: {e}")
        if not websocket.client_state.name == "DISCONNECTED":
            await websocket.close()
