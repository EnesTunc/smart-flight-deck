"""
Simulator module - SimConnect interface for MSFS.

Includes:
- SimConnect basic connection and events
- MobiFlight WASM integration for LVAR access
- Aircraft profile system for third-party aircraft support
- Automatic WASM installation
"""

from .connection import SimConnection
from .events import SimEvents
from .variables import SimVariables
from .mobiflight import MobiFlightClient, MobiFlightSimConnectBridge
from .aircraft_detector import (
    AircraftDetector,
    AircraftProfile,
    ProfileLoader,
    CommandResolver,
)
from .wasm_installer import (
    WASMManager,
    WASMInstaller,
    MSFSDetector,
    WASMStatus,
    MSFSInstallation,
)
from .sim_manager import SimManager, CommandResult

__all__ = [
    # Core SimConnect
    "SimConnection",
    "SimEvents",
    "SimVariables",
    # MobiFlight WASM
    "MobiFlightClient",
    "MobiFlightSimConnectBridge",
    # Aircraft Profiles
    "AircraftDetector",
    "AircraftProfile",
    "ProfileLoader",
    "CommandResolver",
    # WASM Installation
    "WASMManager",
    "WASMInstaller",
    "MSFSDetector",
    "WASMStatus",
    "MSFSInstallation",
    # Unified Manager
    "SimManager",
    "CommandResult",
]
