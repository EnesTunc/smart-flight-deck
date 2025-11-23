"""
Smart Flight Deck Companion - HTTP API Routes
"""

import secrets
import io
import base64
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from pydantic import BaseModel

import qrcode
from config import settings, get_local_ip

router = APIRouter()


# ===========================
# Models
# ===========================


class ConnectionInfo(BaseModel):
    """QR code connection information."""

    ip: str
    port: int
    session_token: str
    expires_at: str


class TranscriptionResult(BaseModel):
    """Speech-to-text result."""

    text: str
    confidence: float
    language: str
    duration: float


class CommandResult(BaseModel):
    """Command execution result."""

    success: bool
    command: str
    action: Optional[str] = None
    message: str
    tts_audio: Optional[str] = None  # Base64 encoded audio


class SimStatus(BaseModel):
    """Simulator connection status."""

    connected: bool
    aircraft: Optional[str] = None
    flight_phase: Optional[str] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    gear_position: Optional[int] = None


# ===========================
# Session Management
# ===========================

# In-memory session store (use Redis in production)
_sessions: dict[str, dict] = {}


def create_session() -> tuple[str, datetime]:
    """Create a new session token."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(seconds=settings.session_token_expiry)
    _sessions[token] = {
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "authenticated": False,
    }
    return token, expires_at


def validate_session(token: str) -> bool:
    """Validate a session token."""
    if token not in _sessions:
        return False
    session = _sessions[token]
    if datetime.utcnow() > session["expires_at"]:
        del _sessions[token]
        return False
    return True


# ===========================
# Connection Endpoints
# ===========================


@router.get("/connect/qr")
async def get_connection_qr():
    """Generate QR code for mobile app connection."""
    token, expires_at = create_session()

    connection_info = ConnectionInfo(
        ip=get_local_ip(),
        port=settings.port,
        session_token=token,
        expires_at=expires_at.isoformat(),
    )

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(connection_info.model_dump_json())
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "qr_image": f"data:image/png;base64,{qr_base64}",
        "connection_info": connection_info,
    }


@router.post("/connect/verify")
async def verify_connection(x_session_token: str = Header(...)):
    """Verify mobile app connection."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    _sessions[x_session_token]["authenticated"] = True

    return {
        "status": "connected",
        "message": "Mobile app connected successfully",
    }


# ===========================
# Audio Endpoints
# ===========================


@router.post("/audio/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(
    audio: UploadFile = File(...),
    x_session_token: str = Header(...),
):
    """Transcribe audio to text using Whisper."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    # TODO: Implement actual Whisper transcription
    # For now, return placeholder
    return TranscriptionResult(
        text="gear down",  # Placeholder
        confidence=0.95,
        language="en",
        duration=1.5,
    )


@router.post("/audio/command", response_model=CommandResult)
async def process_command(
    audio: UploadFile = File(...),
    x_session_token: str = Header(...),
):
    """Process audio command: transcribe -> parse -> execute -> TTS response."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    # TODO: Full pipeline implementation
    # 1. Transcribe audio
    # 2. Parse command
    # 3. Execute SimConnect action
    # 4. Generate TTS response

    return CommandResult(
        success=True,
        command="gear down",
        action="GEAR_DOWN",
        message="Gear is down",
        tts_audio=None,  # TODO: Base64 TTS audio
    )


# ===========================
# Simulator Endpoints
# ===========================


@router.get("/sim/status", response_model=SimStatus)
async def get_sim_status(x_session_token: str = Header(...)):
    """Get current simulator status."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    # TODO: Get actual SimConnect data
    return SimStatus(
        connected=False,
        aircraft=None,
        flight_phase=None,
        altitude=None,
        speed=None,
        gear_position=None,
    )


@router.post("/sim/command/{command}")
async def execute_sim_command(
    command: str,
    x_session_token: str = Header(...),
):
    """Execute a simulator command directly."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    valid_commands = [
        "gear_toggle",
        "gear_up",
        "gear_down",
        "flaps_up",
        "flaps_down",
        "parking_brake",
    ]

    if command not in valid_commands:
        raise HTTPException(status_code=400, detail=f"Unknown command: {command}")

    # TODO: Execute via SimConnect
    return {
        "success": True,
        "command": command,
        "message": f"Command '{command}' executed",
    }
