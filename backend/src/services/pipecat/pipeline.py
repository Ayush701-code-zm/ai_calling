import logging
from fastapi import WebSocket
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketTransport, FastAPIWebsocketParams
from pipecat.services.google import GoogleLLMService
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.frames.frames import EndFrame
from pipecat.serializers.exotel import ExotelFrameSerializer

from src.config.settings import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a professional AI voice assistant. 
Speak naturally in Hindi and English. 
Keep responses short, conversational, and human-like."""

async def run_pipecat_pipeline(websocket: WebSocket, stream_sid: str):
    # For Exotel, we use the ExotelFrameSerializer
    transport = FastAPIWebsocketTransport(
        websocket=websocket,
        params=FastAPIWebsocketParams(
            serializer=ExotelFrameSerializer(stream_sid),
            audio_out_enabled=True,
            add_wav_header=False # Exotel expects raw mu-law usually
        )
    )


    from pipecat.services.google import GoogleLLMService
    
    llm = GoogleLLMService(
        api_key=settings.GOOGLE_API_KEY,
        model="gemini-2.0-flash-exp", # Or relevant live model
        system_instruction=SYSTEM_PROMPT
    )

    # We need a pipeline that handles the flow
    pipeline = Pipeline([
        transport.input(),   # Audio from Exotel
        llm,                 # Gemini processing (STT + LLM + TTS)
        transport.output()   # Audio back to Exotel
    ])

    task = PipelineTask(pipeline)

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info(f"Exotel stream connected: {stream_sid}")
        # Initial greeting if needed
        # await task.queue_frames([TextFrame("Hello, how can I help you today?")])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info(f"Exotel stream disconnected: {stream_sid}")
        await task.queue_frames([EndFrame()])

    runner = PipelineRunner()
    await runner.run(task)
