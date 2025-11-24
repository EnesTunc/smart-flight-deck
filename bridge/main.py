"""
Smart Flight Deck Companion - PC Bridge
Main entry point for the FastAPI server.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - QR code page for mobile connection."""
    ip = get_local_ip()
    port = settings.port

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Flight Deck - Connect</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #fff;
            }}
            .container {{
                text-align: center;
                padding: 40px;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }}
            h1 {{
                font-size: 28px;
                margin-bottom: 10px;
                color: #4ade80;
            }}
            .subtitle {{
                color: #94a3b8;
                margin-bottom: 30px;
            }}
            #qr-container {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                display: inline-block;
                margin-bottom: 20px;
            }}
            #qr-image {{
                width: 250px;
                height: 250px;
            }}
            .info {{
                background: rgba(74, 222, 128, 0.1);
                border: 1px solid #4ade80;
                border-radius: 8px;
                padding: 15px;
                margin-top: 20px;
            }}
            .info p {{
                margin: 5px 0;
                font-family: monospace;
                font-size: 14px;
            }}
            .status {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                margin-top: 20px;
                color: #4ade80;
            }}
            .status-dot {{
                width: 10px;
                height: 10px;
                background: #4ade80;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            .loading {{
                color: #94a3b8;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✈️ Smart Flight Deck</h1>
            <p class="subtitle">Scan QR code with mobile app to connect</p>

            <div id="qr-container">
                <img id="qr-image" src="" alt="QR Code">
                <p class="loading" id="loading">Loading QR code...</p>
            </div>

            <div class="info">
                <p><strong>Server:</strong> http://{ip}:{port}</p>
                <p><strong>API Docs:</strong> <a href="/docs" style="color:#4ade80">/docs</a></p>
            </div>

            <div class="status">
                <div class="status-dot"></div>
                <span>Bridge Running</span>
            </div>
        </div>

        <script>
            async function loadQR() {{
                try {{
                    const response = await fetch('/api/connect/qr');
                    const data = await response.json();
                    document.getElementById('qr-image').src = data.qr_image;
                    document.getElementById('loading').style.display = 'none';
                }} catch (error) {{
                    document.getElementById('loading').textContent = 'Error loading QR code';
                    console.error('Error:', error);
                }}
            }}
            loadQR();
            // Refresh QR every 5 minutes (token expires)
            setInterval(loadQR, 5 * 60 * 1000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api-info")
async def api_info():
    """API info endpoint - basic JSON info."""
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
