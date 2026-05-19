from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.routes.call_routes import router as call_router
from src.routes.ws_routes import router as ws_router
from src.routes.auth_routes import router as auth_router
from src.utils.db import connect_to_mongo, close_mongo_connection
from src.config.settings import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(title="AI Voice Caller Backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup():
        await connect_to_mongo()

    @app.on_event("shutdown")
    async def shutdown():
        await close_mongo_connection()

    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "An internal server error occurred."}
        )

    app.include_router(call_router, prefix="/api/v1/calls", tags=["calls"])
    app.include_router(ws_router, tags=["websocket"])
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()
