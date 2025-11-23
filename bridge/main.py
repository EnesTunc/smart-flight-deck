"""
Smart Flight Deck Companion - PC Bridge
Main entry point for the FastAPI server.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings, get_local_ip
from api.routes import router as api_router
from api.websocket import router as ws_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("=" * 50)
    logger.info("Smart Flight Deck Companion - PC Bridge")
    logger.info("=" * 50)
    logger.info(f"Local IP: {get_local_ip()}")
    logger.info(f"Server: http://{get_local_ip()}:{settings.port}")
    logger.info(f"Whisper Model: {settings.whisper_model}")
    logger.info("=" * 50)

    # TODO: Initialize SimConnect
    # TODO: Load Whisper model
    # TODO: Load Piper TTS

    yield

    # Shutdown
    logger.info("Shutting down...")
    # TODO: Cleanup SimConnect connection


app = FastAPI(
    title="Smart Flight Deck Companion",
    description="MSFS Voice Assistant - PC Bridge API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for mobile app communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to mobile app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")


@app.get("/")
async def root():
    """Root endpoint - basic info."""
    return {
        "name": "Smart Flight Deck Companion",
        "version": "0.1.0",
        "status": "running",
        "ip": get_local_ip(),
        "port": settings.port,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "simconnect": False,  # TODO: Check actual connection
        "whisper_loaded": False,  # TODO: Check model status
        "piper_loaded": False,  # TODO: Check model status
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
