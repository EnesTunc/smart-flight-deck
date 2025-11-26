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
from sim.connection import SimConnection

router = APIRouter()

# Global SimConnect instance
_sim_connection: SimConnection = None


def get_sim_connection() -> SimConnection:
    """Get or create SimConnect connection."""
    global _sim_connection
    if _sim_connection is None:
        _sim_connection = SimConnection()
    return _sim_connection


def try_connect_sim():
    """Try to connect to MSFS (called on startup and on-demand)."""
    sim = get_sim_connection()
    if not sim.is_connected:
        sim.connect()
    return sim.is_connected


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
    on_ground: bool = True

    # Position
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0
    altitude_agl: float = 0.0
    heading: float = 0.0
    track: float = 0.0

    # Speed
    indicated_speed: float = 0.0
    true_speed: float = 0.0
    ground_speed: float = 0.0
    mach: float = 0.0
    vertical_speed: float = 0.0

    # Aircraft systems
    gear_position: int = 0
    flaps_position: int = 0
    spoilers_armed: bool = False

    # Fuel
    fuel_total_kg: float = 0.0
    fuel_flow_kg_h: float = 0.0
    fuel_percent: float = 0.0
    fuel_endurance_min: int = 0

    # Navigation
    nav1_freq: float = 0.0
    nav1_ident: Optional[str] = None
    nav1_dme: float = 0.0
    nav2_freq: float = 0.0
    nav2_ident: Optional[str] = None
    nav2_dme: float = 0.0

    # Environment
    wind_direction: float = 0.0
    wind_speed: float = 0.0
    oat: float = 0.0
    qnh: float = 1013.0


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

    sim = get_sim_connection()

    # Try to connect if not connected
    if not sim.is_connected:
        try_connect_sim()

    # Get current state
    if sim.is_connected:
        state = sim.update_state()

        # Calculate fuel endurance (minutes)
        fuel_endurance_min = 0
        if state.fuel_flow_kg_h > 0:
            fuel_endurance_min = int((state.fuel_total_kg / state.fuel_flow_kg_h) * 60)

        return SimStatus(
            connected=True,
            aircraft=state.aircraft_title or None,
            flight_phase=None,  # TODO: Get from context engine
            on_ground=state.on_ground,

            # Position
            latitude=state.latitude,
            longitude=state.longitude,
            altitude=state.altitude,
            altitude_agl=state.altitude_agl,
            heading=state.heading,
            track=state.track,

            # Speed
            indicated_speed=state.indicated_airspeed,
            true_speed=state.true_airspeed,
            ground_speed=state.ground_speed,
            mach=state.mach,
            vertical_speed=state.vertical_speed,

            # Aircraft systems
            gear_position=state.gear_handle_position,
            flaps_position=state.flaps_handle_index,
            spoilers_armed=state.spoilers_armed,

            # Fuel
            fuel_total_kg=state.fuel_total_kg,
            fuel_flow_kg_h=state.fuel_flow_kg_h,
            fuel_percent=state.fuel_percent,
            fuel_endurance_min=fuel_endurance_min,

            # Navigation
            nav1_freq=state.nav1_freq,
            nav1_ident=state.nav1_ident or None,
            nav1_dme=state.nav1_dme,
            nav2_freq=state.nav2_freq,
            nav2_ident=state.nav2_ident or None,
            nav2_dme=state.nav2_dme,

            # Environment
            wind_direction=state.wind_direction,
            wind_speed=state.wind_speed,
            oat=state.oat,
            qnh=state.qnh,
        )

    return SimStatus(connected=False)


@router.post("/sim/command/{command}")
async def execute_sim_command(
    command: str,
    x_session_token: str = Header(...),
):
    """Execute a simulator command directly."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    # Map command names to SimConnect events
    command_events = {
        "gear_toggle": "GEAR_TOGGLE",
        "gear_up": "GEAR_UP",
        "gear_down": "GEAR_DOWN",
        "flaps_up": "FLAPS_DECR",
        "flaps_down": "FLAPS_INCR",
        "flaps_1": "FLAPS_1",
        "flaps_2": "FLAPS_2",
        "flaps_3": "FLAPS_3",
        "flaps_full": "FLAPS_DOWN",
        "parking_brake": "PARKING_BRAKES",
        "spoilers_arm": "SPOILERS_ARM_TOGGLE",
        "spoilers_on": "SPOILERS_ON",
        "spoilers_off": "SPOILERS_OFF",
        "landing_lights": "LANDING_LIGHTS_TOGGLE",
        "nav_lights": "NAV_LIGHTS_TOGGLE",
        "beacon": "BEACON_LIGHTS_TOGGLE",
        "strobe": "STROBES_TOGGLE",
    }

    if command not in command_events:
        raise HTTPException(status_code=400, detail=f"Unknown command: {command}")

    sim = get_sim_connection()

    if not sim.is_connected:
        try_connect_sim()

    if not sim.is_connected:
        raise HTTPException(status_code=503, detail="MSFS not connected")

    # Execute the event
    event_name = command_events[command]
    success = sim.send_event(event_name)

    if success:
        return {
            "success": True,
            "command": command,
            "event": event_name,
            "message": f"Command '{command}' executed",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute command: {command}"
        )


# ===========================
# WASM Management Endpoints
# ===========================


class WASMStatusResponse(BaseModel):
    """WASM installation status."""

    installed: bool
    path: Optional[str] = None
    version: Optional[str] = None
    needs_update: bool = False
    msfs_found: bool = False
    community_folder: Optional[str] = None
    error_message: str = ""


class WASMInstallRequest(BaseModel):
    """WASM installation request."""

    auto_install: bool = True


class AircraftProfileInfo(BaseModel):
    """Aircraft profile information."""

    name: str
    has_lvar_support: bool
    has_fcu_control: bool
    has_mcp_control: bool
    available_commands: list[str] = []


@router.get("/wasm/status", response_model=WASMStatusResponse)
async def get_wasm_status():
    """
    Check MobiFlight WASM installation status.

    No authentication required - this is used during initial setup.
    """
    from sim import WASMManager, MSFSDetector

    wasm_manager = WASMManager()
    detector = MSFSDetector()

    # Check MSFS installation
    installations = detector.detect_all()
    msfs_found = len(installations) > 0
    community_folder = None

    if installations:
        community_folder = str(installations[0].community_path)

    # Check WASM status
    status = wasm_manager.check_wasm_status()

    return WASMStatusResponse(
        installed=status.installed,
        path=str(status.path) if status.path else None,
        version=status.version,
        needs_update=status.needs_update,
        msfs_found=msfs_found,
        community_folder=community_folder,
        error_message=status.error_message,
    )


@router.post("/wasm/install")
async def install_wasm(request: WASMInstallRequest = None):
    """
    Install MobiFlight WASM module.

    Downloads from GitHub and installs to MSFS Community folder.
    No authentication required - this is used during initial setup.
    """
    from sim import WASMManager

    wasm_manager = WASMManager()

    # Check current status
    status = wasm_manager.check_wasm_status()

    if status.installed and not status.needs_update:
        return {
            "success": True,
            "message": "MobiFlight WASM is already installed",
            "path": str(status.path),
        }

    # Install WASM
    success, message = await wasm_manager.install_wasm()

    if success:
        new_status = wasm_manager.check_wasm_status()
        return {
            "success": True,
            "message": message,
            "path": str(new_status.path) if new_status.path else None,
            "note": "Please restart MSFS for changes to take effect",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"WASM installation failed: {message}"
        )


@router.delete("/wasm/uninstall")
async def uninstall_wasm():
    """
    Uninstall MobiFlight WASM module.

    Removes from MSFS Community folder.
    """
    from sim import WASMManager

    wasm_manager = WASMManager()

    success, message = wasm_manager.uninstall_wasm()

    if success:
        return {
            "success": True,
            "message": message,
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"WASM uninstallation failed: {message}"
        )


@router.get("/wasm/msfs-paths")
async def get_msfs_paths():
    """
    Get detected MSFS installation paths.

    Useful for troubleshooting installation issues.
    """
    from sim import MSFSDetector

    detector = MSFSDetector()
    installations = detector.detect_all()

    return {
        "found": len(installations),
        "installations": [
            {
                "edition": inst.edition.value,
                "packages_path": str(inst.packages_path),
                "community_path": str(inst.community_path),
            }
            for inst in installations
        ],
    }


# ===========================
# Aircraft Profile Endpoints
# ===========================


@router.get("/aircraft/profile", response_model=AircraftProfileInfo)
async def get_current_aircraft_profile(x_session_token: str = Header(...)):
    """Get current aircraft's profile information."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    from sim import AircraftDetector

    # TODO: Get actual aircraft from SimConnect
    detector = AircraftDetector()

    # For now, return default profile info
    profile = detector._loader.get_default_profile()

    if profile:
        return AircraftProfileInfo(
            name=profile.name,
            has_lvar_support=profile.has_lvar_support,
            has_fcu_control=profile.has_fcu_control,
            has_mcp_control=profile.has_mcp_control,
            available_commands=list(profile.commands.keys()),
        )

    return AircraftProfileInfo(
        name="Unknown",
        has_lvar_support=False,
        has_fcu_control=False,
        has_mcp_control=False,
        available_commands=[],
    )


@router.get("/aircraft/profiles")
async def list_aircraft_profiles():
    """List all available aircraft profiles."""
    from sim import ProfileLoader

    loader = ProfileLoader()
    profiles = []

    for profile_id in loader.list_profiles():
        profile = loader.get_profile(profile_id)
        if profile:
            profiles.append({
                "id": profile_id,
                "name": profile.name,
                "has_lvar_support": profile.has_lvar_support,
                "features": profile.features,
            })

    # Add default profile
    default = loader.get_default_profile()
    if default:
        profiles.append({
            "id": "default",
            "name": default.name,
            "has_lvar_support": default.has_lvar_support,
            "features": default.features,
            "is_default": True,
        })

    return {"profiles": profiles}


# ===========================
# Context Engine Endpoints
# ===========================


class ContextStatus(BaseModel):
    """Flight context status."""

    phase: str
    phase_display: str
    on_ground: bool
    speed: float
    altitude: float
    altitude_agl: float
    is_critical: bool
    aircraft: str
    limits: Optional[dict] = None


class PhaseInfo(BaseModel):
    """Detailed flight phase information."""

    current: str
    previous: str
    is_ground_phase: bool
    is_critical_phase: bool
    duration_seconds: float


class SafetyEvaluationRequest(BaseModel):
    """Request to evaluate command safety."""

    command_id: str
    value: Optional[float] = None
    override: bool = False


class SafetyEvaluationResponse(BaseModel):
    """Safety evaluation result."""

    allowed: bool
    action: str
    message: Optional[str] = None
    warning: Optional[str] = None
    details: dict = {}


# Global context engine instance
_context_engine = None


def get_context_engine():
    """Get or create context engine instance."""
    global _context_engine
    if _context_engine is None:
        from logic import ContextEngine
        _context_engine = ContextEngine()
    return _context_engine


@router.get("/context/status", response_model=ContextStatus)
async def get_context_status(x_session_token: str = Header(...)):
    """
    Get current flight context status.

    Returns flight phase, aircraft state, and active limits.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    ctx = get_context_engine()

    return ContextStatus(
        phase=ctx.phase.name,
        phase_display=ctx.phase.display_name,
        on_ground=ctx.is_on_ground,
        speed=ctx.current_speed,
        altitude=ctx.current_altitude,
        altitude_agl=ctx.current_altitude_agl,
        is_critical=ctx.is_critical_phase,
        aircraft=ctx.aircraft_title,
        limits=ctx.speed_limits.to_dict() if ctx.speed_limits else None,
    )


@router.get("/context/phase", response_model=PhaseInfo)
async def get_flight_phase(x_session_token: str = Header(...)):
    """
    Get detailed flight phase information.

    Includes current/previous phase, duration, and phase characteristics.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    ctx = get_context_engine()
    phase_info = ctx.get_phase_info()

    return PhaseInfo(
        current=phase_info["current"],
        previous=phase_info["previous"],
        is_ground_phase=phase_info["is_ground"],
        is_critical_phase=phase_info["is_critical"],
        duration_seconds=phase_info["duration"],
    )


@router.post("/context/evaluate", response_model=SafetyEvaluationResponse)
async def evaluate_command_safety(
    request: SafetyEvaluationRequest,
    x_session_token: str = Header(...),
):
    """
    Evaluate if a command is safe to execute.

    Checks speed limits, flight phase restrictions, and safety rules.
    Returns action recommendation: ALLOW, REMIND, WARN, CONFIRM, or BLOCK.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    ctx = get_context_engine()

    result = ctx.evaluate_command(
        command_id=request.command_id,
        value=request.value,
        override=request.override,
    )

    return SafetyEvaluationResponse(
        allowed=result.allowed,
        action=result.action.name,
        message=result.reason,
        warning=result.warning,
        details=result.details,
    )


@router.post("/context/update")
async def update_context(
    on_ground: bool,
    altitude: float,
    altitude_agl: float,
    speed: float,
    ground_speed: float,
    vertical_speed: float,
    gear_down: bool = True,
    flaps_index: int = 0,
    engine1_running: bool = False,
    engine2_running: bool = False,
    parking_brake: bool = False,
    aircraft_title: str = "",
    x_session_token: str = Header(...),
):
    """
    Update flight context with current aircraft state.

    Called periodically by SimConnect data handler.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    ctx = get_context_engine()

    ctx.update_from_simconnect(
        altitude=altitude,
        altitude_agl=altitude_agl,
        speed=speed,
        ground_speed=ground_speed,
        vertical_speed=vertical_speed,
        on_ground=on_ground,
        gear_down=gear_down,
        flaps_index=flaps_index,
        engine1_running=engine1_running,
        engine2_running=engine2_running,
        parking_brake=parking_brake,
        aircraft_title=aircraft_title,
    )

    return {
        "success": True,
        "phase": ctx.phase.display_name,
        "is_critical": ctx.is_critical_phase,
    }


@router.get("/context/limits")
async def get_speed_limits(x_session_token: str = Header(...)):
    """
    Get current aircraft speed limits.

    Returns Vmo, Mmo, Vlo, Vle, Vfe for current aircraft.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    ctx = get_context_engine()

    if ctx.speed_limits:
        return {
            "aircraft": ctx.aircraft_title,
            "limits": ctx.speed_limits.to_dict(),
        }

    return {
        "aircraft": ctx.aircraft_title or "Unknown",
        "limits": None,
        "message": "No aircraft loaded or limits not available",
    }


# ===========================
# Checklist Endpoints
# ===========================


class ChecklistInfo(BaseModel):
    """Checklist information."""
    id: str
    name: str
    name_tr: str
    phase: str
    items_count: int


class ChecklistItemInfo(BaseModel):
    """Checklist item information."""
    id: str
    challenge: str
    expected: str
    critical: bool = False
    notes: Optional[str] = None


class ChecklistStatusResponse(BaseModel):
    """Checklist status response."""
    active: bool
    state: str
    checklist_name: Optional[str] = None
    current_item: Optional[ChecklistItemInfo] = None
    progress: float = 0.0
    items_remaining: int = 0


class ChecklistActionResponse(BaseModel):
    """Response from checklist actions."""
    success: bool
    state: str
    message: str
    tts_text: str
    current_item: Optional[ChecklistItemInfo] = None
    verified: Optional[bool] = None
    verification_message: Optional[str] = None
    progress: float = 0.0
    items_remaining: int = 0


class ChecklistResponseRequest(BaseModel):
    """Request for checklist response."""
    response: str  # "check", "skip", "override", "repeat"


# Global checklist manager instance
_checklist_manager = None


def get_checklist_manager():
    """Get or create checklist manager instance."""
    global _checklist_manager
    if _checklist_manager is None:
        from logic import ChecklistManager
        _checklist_manager = ChecklistManager()
    return _checklist_manager


@router.get("/checklist/list")
async def list_checklists(x_session_token: str = Header(...)):
    """
    List available checklists for current aircraft.

    Returns all checklists that can be started.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    manager = get_checklist_manager()
    checklists = manager.list_available()

    return {
        "aircraft": manager._current_aircraft or "Default",
        "checklists": checklists,
    }


@router.post("/checklist/start/{checklist_id}", response_model=ChecklistActionResponse)
async def start_checklist(
    checklist_id: str,
    x_session_token: str = Header(...),
):
    """
    Start a checklist by ID.

    Begins the challenge-response sequence.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    manager = get_checklist_manager()

    # Try to find checklist by ID or name
    actual_id = manager.find_checklist_by_name(checklist_id)
    if not actual_id:
        actual_id = checklist_id

    result = manager.start_checklist(actual_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Checklist '{checklist_id}' not found"
        )

    current_item = None
    if result.current_item:
        current_item = ChecklistItemInfo(
            id=result.current_item.get("id", ""),
            challenge=result.current_item.get("challenge", ""),
            expected=result.current_item.get("expected", ""),
            critical=result.current_item.get("critical", False),
            notes=result.current_item.get("notes"),
        )

    return ChecklistActionResponse(
        success=result.success,
        state=result.state.name,
        message=result.message,
        tts_text=result.tts_text,
        current_item=current_item,
        progress=result.progress,
        items_remaining=result.items_remaining,
    )


@router.get("/checklist/status", response_model=ChecklistStatusResponse)
async def get_checklist_status(x_session_token: str = Header(...)):
    """
    Get current checklist status.

    Returns active checklist info and current item.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    manager = get_checklist_manager()
    engine = manager.engine

    current_item = None
    if engine.current_item:
        item = engine.current_item
        current_item = ChecklistItemInfo(
            id=item.id,
            challenge=item.challenge,
            expected=item.expected_response,
            critical=item.critical,
            notes=item.notes,
        )

    return ChecklistStatusResponse(
        active=engine.is_active,
        state=engine.state.name,
        checklist_name=engine.active_checklist.name if engine.active_checklist else None,
        current_item=current_item,
        progress=engine.progress,
        items_remaining=engine.items_remaining,
    )


@router.post("/checklist/response", response_model=ChecklistActionResponse)
async def send_checklist_response(
    request: ChecklistResponseRequest,
    x_session_token: str = Header(...),
):
    """
    Send a response to the current checklist item.

    Valid responses: "check", "skip", "override", "repeat"
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    from logic import UserResponse, parse_user_response

    manager = get_checklist_manager()
    engine = manager.engine

    if not engine.is_active:
        raise HTTPException(
            status_code=400,
            detail="No active checklist"
        )

    # Parse response
    user_response = parse_user_response(request.response)
    if not user_response:
        # Try direct mapping
        response_map = {
            "check": UserResponse.CHECK,
            "skip": UserResponse.SKIP,
            "override": UserResponse.OVERRIDE,
            "repeat": UserResponse.REPEAT,
        }
        user_response = response_map.get(request.response.lower())

    if not user_response:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid response: {request.response}. Use: check, skip, override, repeat"
        )

    result = engine.respond(user_response)

    current_item = None
    if result.current_item:
        current_item = ChecklistItemInfo(
            id=result.current_item.get("id", ""),
            challenge=result.current_item.get("challenge", ""),
            expected=result.current_item.get("expected", ""),
            critical=result.current_item.get("critical", False),
        )

    return ChecklistActionResponse(
        success=result.success,
        state=result.state.name,
        message=result.message,
        tts_text=result.tts_text,
        current_item=current_item,
        verified=result.verified,
        verification_message=result.verification_message,
        progress=result.progress,
        items_remaining=result.items_remaining,
    )


@router.post("/checklist/pause", response_model=ChecklistActionResponse)
async def pause_checklist(x_session_token: str = Header(...)):
    """Pause the active checklist."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    manager = get_checklist_manager()
    result = manager.engine.pause()

    return ChecklistActionResponse(
        success=result.success,
        state=result.state.name,
        message=result.message,
        tts_text=result.tts_text,
        progress=result.progress,
        items_remaining=result.items_remaining,
    )


@router.post("/checklist/resume", response_model=ChecklistActionResponse)
async def resume_checklist(x_session_token: str = Header(...)):
    """Resume a paused checklist."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    manager = get_checklist_manager()
    result = manager.engine.resume()

    current_item = None
    if result.current_item:
        current_item = ChecklistItemInfo(
            id=result.current_item.get("id", ""),
            challenge=result.current_item.get("challenge", ""),
            expected=result.current_item.get("expected", ""),
            critical=result.current_item.get("critical", False),
        )

    return ChecklistActionResponse(
        success=result.success,
        state=result.state.name,
        message=result.message,
        tts_text=result.tts_text,
        current_item=current_item,
        progress=result.progress,
        items_remaining=result.items_remaining,
    )


@router.post("/checklist/cancel", response_model=ChecklistActionResponse)
async def cancel_checklist(x_session_token: str = Header(...)):
    """Cancel the active checklist."""
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    manager = get_checklist_manager()
    result = manager.engine.cancel()

    return ChecklistActionResponse(
        success=result.success,
        state=result.state.name,
        message=result.message,
        tts_text=result.tts_text,
    )


@router.post("/checklist/set-aircraft")
async def set_checklist_aircraft(
    aircraft_title: str,
    x_session_token: str = Header(...),
):
    """
    Set the current aircraft for checklist selection.

    This determines which checklist profile is used.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    manager = get_checklist_manager()
    manager.set_aircraft(aircraft_title)

    checklists = manager.list_available()

    return {
        "success": True,
        "aircraft": aircraft_title,
        "available_checklists": len(checklists),
        "checklists": checklists,
    }


# ===========================
# TTS & SETTINGS
# ===========================

# Global TTS instance
_tts_instance = None


def get_tts():
    """Get or create TTS instance."""
    global _tts_instance
    if _tts_instance is None:
        from audio.tts import PiperTTS
        _tts_instance = PiperTTS(voice=settings.piper_voice)
        _tts_instance.load()
    return _tts_instance


class SettingsUpdate(BaseModel):
    """Settings update request."""
    tts_enabled: Optional[bool] = None
    tts_voice: Optional[str] = None
    verification_enabled: Optional[bool] = None


@router.get("/api/tts/voices")
async def get_tts_voices():
    """
    Get list of available TTS voices with installation status.

    All voices are Public Domain - safe for commercial use.
    """
    from audio.tts import PiperTTS

    voices = PiperTTS.get_available_voices()
    current_voice = settings.piper_voice

    # Check which voices are installed
    models_dir = Path(settings.models_dir) / "piper"
    for voice in voices:
        voice_dir = models_dir / voice['id']
        onnx_file = voice_dir / f"{voice['file_prefix']}.onnx"
        voice['installed'] = onnx_file.exists()
        if voice['installed']:
            voice['size_mb'] = round(onnx_file.stat().st_size / (1024 * 1024), 1)
        else:
            voice['size_mb'] = 0

    return {
        "current_voice": current_voice,
        "voices": voices,
        "total": len(voices),
        "installed": sum(1 for v in voices if v['installed']),
    }


@router.post("/api/tts/preview")
async def preview_tts_voice(
    voice_id: str,
    text: Optional[str] = "Welcome to Smart Flight Deck Companion",
    x_session_token: str = Header(...),
):
    """
    Preview a TTS voice with sample text.

    Returns audio data as base64 encoded WAV.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    from audio.tts import PiperTTS, AVAILABLE_VOICES

    if voice_id not in AVAILABLE_VOICES:
        raise HTTPException(status_code=400, detail=f"Unknown voice: {voice_id}")

    # Create temporary TTS instance with requested voice
    tts = PiperTTS(voice=voice_id)
    if not tts.load():
        raise HTTPException(status_code=500, detail="Failed to load TTS voice")

    # Synthesize preview
    audio_data = tts.synthesize(text)
    audio_base64 = base64.b64encode(audio_data).decode()

    voice_info = AVAILABLE_VOICES[voice_id]

    return {
        "voice": voice_id,
        "voice_info": voice_info,
        "text": text,
        "audio": audio_base64,
        "format": "wav",
        "sample_rate": 22050,
    }


@router.get("/api/settings")
async def get_settings(x_session_token: str = Header(...)):
    """
    Get current Bridge settings.

    Includes TTS voice, Whisper model, and feature flags.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    from audio.tts import PiperTTS

    tts = get_tts()

    return {
        "version": "1.0.0",
        "tts_enabled": settings.tts_enabled,
        "tts_voice": settings.piper_voice,
        "tts_voice_info": tts.get_voice_info(),
        "verification_enabled": True,  # From checklist system
        "whisper_model": settings.whisper_model,
        "language": "en",
    }


@router.put("/api/settings")
async def update_settings(
    updates: SettingsUpdate,
    x_session_token: str = Header(...),
):
    """
    Update Bridge settings.

    Supported settings:
    - tts_enabled: Enable/disable TTS
    - tts_voice: Change active voice
    - verification_enabled: Enable/disable checklist verification
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    changed = []

    # Update TTS voice
    if updates.tts_voice is not None:
        from audio.tts import AVAILABLE_VOICES

        if updates.tts_voice not in AVAILABLE_VOICES:
            raise HTTPException(status_code=400, detail=f"Unknown voice: {updates.tts_voice}")

        tts = get_tts()
        if tts.set_voice(updates.tts_voice):
            settings.piper_voice = updates.tts_voice
            changed.append("tts_voice")
        else:
            raise HTTPException(status_code=500, detail="Failed to change voice")

    # Update TTS enabled
    if updates.tts_enabled is not None:
        settings.tts_enabled = updates.tts_enabled
        changed.append("tts_enabled")

    # TODO: Update verification_enabled when implemented

    return {
        "success": True,
        "message": f"Updated: {', '.join(changed)}" if changed else "No changes",
        "settings": {
            "tts_enabled": settings.tts_enabled,
            "tts_voice": settings.piper_voice,
            "verification_enabled": True,
        },
    }


@router.post("/api/tts/download")
async def download_tts_voice(
    voice_id: str,
    x_session_token: str = Header(...),
):
    """
    Download a TTS voice on demand.

    This allows mobile app to request additional voices to be downloaded.
    Bridge downloads the voice files and returns status.
    """
    if not validate_session(x_session_token):
        raise HTTPException(status_code=401, detail="Invalid session")

    from audio.tts import AVAILABLE_VOICES
    import requests

    if voice_id not in AVAILABLE_VOICES:
        raise HTTPException(status_code=400, detail=f"Unknown voice: {voice_id}")

    voice_info = AVAILABLE_VOICES[voice_id]

    # Check if already downloaded
    models_dir = Path(settings.models_dir) / "piper"
    voice_dir = models_dir / voice_id
    onnx_file = voice_dir / f"{voice_info['file_prefix']}.onnx"

    if onnx_file.exists():
        return {
            "success": True,
            "message": "Voice already installed",
            "voice": voice_id,
            "voice_info": voice_info,
            "size_mb": onnx_file.stat().st_size / (1024 * 1024),
        }

    # Download voice
    try:
        voice_dir.mkdir(parents=True, exist_ok=True)

        # Download .onnx model
        onnx_url = f"https://sfo3.digitaloceanspaces.com/bkmdls/{voice_info['file_prefix']}.onnx"
        response = requests.get(onnx_url, stream=True, timeout=60)
        response.raise_for_status()

        with open(onnx_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:
                    f.write(chunk)

        # Download .onnx.json config
        json_file = voice_dir / f"{voice_info['file_prefix']}.onnx.json"
        json_url = f"https://sfo3.digitaloceanspaces.com/bkmdls/{voice_info['file_prefix']}.onnx.json"
        response = requests.get(json_url, timeout=30)
        response.raise_for_status()
        json_file.write_bytes(response.content)

        size_mb = onnx_file.stat().st_size / (1024 * 1024)

        return {
            "success": True,
            "message": "Voice downloaded successfully",
            "voice": voice_id,
            "voice_info": voice_info,
            "size_mb": size_mb,
        }

    except Exception as e:
        # Cleanup on failure
        if voice_dir.exists():
            import shutil
            shutil.rmtree(voice_dir)

        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/api/version")
async def get_version():
    """
    Get Bridge version information.

    No authentication required.
    """
    import sys
    import platform

    return {
        "version": "1.0.0",
        "build": "20251125",
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
    }
