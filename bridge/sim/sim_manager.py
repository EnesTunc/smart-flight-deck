"""
Smart Flight Deck Companion - Unified Simulator Manager
Coordinates SimConnect, MobiFlight WASM, and aircraft profiles.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass

from .connection import SimConnection, AircraftState
from .mobiflight import MobiFlightClient
from .aircraft_detector import AircraftDetector, CommandResolver, AircraftProfile
from .wasm_installer import WASMManager, WASMStatus

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of executing a command."""

    success: bool
    message: str
    response_text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class SimManager:
    """
    Unified simulator manager.

    Provides high-level interface for:
    - SimConnect connection management
    - MobiFlight WASM integration
    - Aircraft detection and profile loading
    - Command execution (SimConnect + LVAR)
    - WASM installation management
    """

    def __init__(self):
        # Core components
        self._sim_connection = SimConnection()
        self._mobiflight = MobiFlightClient()
        self._aircraft_detector = AircraftDetector()
        self._command_resolver = CommandResolver(self._aircraft_detector)
        self._wasm_manager = WASMManager()

        # State
        self._connected = False
        self._mobiflight_available = False
        self._current_aircraft: str = ""
        self._current_profile: Optional[AircraftProfile] = None

        # Callbacks
        self._on_connection_change: Optional[Callable[[bool], None]] = None
        self._on_aircraft_change: Optional[Callable[[str, AircraftProfile], None]] = None
        self._on_state_update: Optional[Callable[[AircraftState], None]] = None

    async def initialize(
        self,
        auto_install_wasm: bool = False,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Initialize the simulator manager.

        Args:
            auto_install_wasm: Automatically install WASM if not found
            progress_callback: Progress update callback (message, percent)

        Returns:
            Dict with initialization status
        """
        result = {
            "simconnect": False,
            "mobiflight": False,
            "wasm_installed": False,
            "aircraft_detected": False,
            "profile_loaded": False,
            "errors": [],
        }

        # Step 1: Check WASM status
        if progress_callback:
            progress_callback("Checking MobiFlight WASM...", 10)

        wasm_status = self._wasm_manager.check_wasm_status()
        result["wasm_installed"] = wasm_status.installed

        if not wasm_status.installed:
            if auto_install_wasm:
                if progress_callback:
                    progress_callback("Installing MobiFlight WASM...", 20)

                success, msg = await self._wasm_manager.install_wasm(
                    progress_callback=lambda m, p: progress_callback(m, 20 + int(p * 0.3))
                    if progress_callback
                    else None
                )
                result["wasm_installed"] = success
                if not success:
                    result["errors"].append(f"WASM install failed: {msg}")
            else:
                result["errors"].append(
                    "MobiFlight WASM not installed. Some features will be limited."
                )

        # Step 2: Connect to SimConnect
        if progress_callback:
            progress_callback("Connecting to MSFS...", 50)

        try:
            sim_connected = self._sim_connection.connect()
            result["simconnect"] = sim_connected
            self._connected = sim_connected

            if not sim_connected:
                result["errors"].append("Could not connect to MSFS. Is the simulator running?")

        except Exception as e:
            result["errors"].append(f"SimConnect error: {str(e)}")

        # Step 3: Initialize MobiFlight
        if self._connected and result["wasm_installed"]:
            if progress_callback:
                progress_callback("Initializing MobiFlight...", 70)

            try:
                mf_available = self._mobiflight.initialize(self._sim_connection._sim)
                result["mobiflight"] = mf_available
                self._mobiflight_available = mf_available

                if not mf_available:
                    result["errors"].append(
                        "MobiFlight WASM module not responding. "
                        "Please restart MSFS after installing WASM."
                    )

            except Exception as e:
                result["errors"].append(f"MobiFlight error: {str(e)}")

        # Step 4: Detect aircraft
        if self._connected:
            if progress_callback:
                progress_callback("Detecting aircraft...", 85)

            try:
                state = self._sim_connection.update_state()
                aircraft_title = state.aircraft_title

                if aircraft_title:
                    self._current_aircraft = aircraft_title
                    self._current_profile = self._aircraft_detector.detect(aircraft_title)
                    result["aircraft_detected"] = True
                    result["profile_loaded"] = self._current_profile is not None

                    logger.info(
                        f"Aircraft: {aircraft_title}, "
                        f"Profile: {self._current_profile.name if self._current_profile else 'None'}"
                    )

            except Exception as e:
                result["errors"].append(f"Aircraft detection error: {str(e)}")

        if progress_callback:
            progress_callback("Ready!", 100)

        return result

    def connect(self) -> bool:
        """
        Connect to MSFS.

        Returns:
            True if connected successfully
        """
        self._connected = self._sim_connection.connect()

        if self._connected and self._on_connection_change:
            self._on_connection_change(True)

        return self._connected

    def disconnect(self):
        """Disconnect from MSFS."""
        self._sim_connection.disconnect()
        self._mobiflight.close()
        self._connected = False
        self._mobiflight_available = False

        if self._on_connection_change:
            self._on_connection_change(False)

    async def execute_command(
        self,
        command_id: str,
        value: Any = None
    ) -> CommandResult:
        """
        Execute a command using the appropriate method.

        Automatically selects between SimConnect and LVAR based on
        current aircraft profile.

        Args:
            command_id: Command identifier (e.g., 'gear_down', 'fcu_heading_set')
            value: Optional value for the command

        Returns:
            CommandResult with execution status
        """
        if not self._connected:
            return CommandResult(
                success=False,
                message="Not connected to MSFS"
            )

        # Resolve command using current profile
        resolved = self._command_resolver.resolve(command_id, value)

        if not resolved:
            return CommandResult(
                success=False,
                message=f"Command not found: {command_id}"
            )

        cmd_type = resolved.get("type")

        try:
            success = False

            if cmd_type == "simconnect":
                # Standard SimConnect event
                event = resolved.get("event")
                event_value = resolved.get("value", 0)
                success = self._sim_connection.send_event(event, event_value)

            elif cmd_type == "lvar":
                # LVAR via MobiFlight
                if not self._mobiflight_available:
                    return CommandResult(
                        success=False,
                        message="LVAR commands require MobiFlight WASM module"
                    )

                lvar = resolved.get("lvar")
                action = resolved.get("action", "set")
                lvar_value = resolved.get("value")

                if action == "set":
                    success = await self._mobiflight.write_lvar(lvar, lvar_value)
                elif action == "toggle":
                    # Read current value and toggle
                    current = await self._mobiflight.read_lvar(lvar)
                    new_value = 0 if current.value > 0 else 1
                    success = await self._mobiflight.write_lvar(lvar, new_value)

            elif cmd_type == "hevent":
                # H:Event via MobiFlight
                if not self._mobiflight_available:
                    return CommandResult(
                        success=False,
                        message="H:Event commands require MobiFlight WASM module"
                    )

                event = resolved.get("event")
                success = await self._mobiflight.execute_html_event(event)

            elif cmd_type == "calculator":
                # Calculator code via MobiFlight
                if not self._mobiflight_available:
                    return CommandResult(
                        success=False,
                        message="Calculator commands require MobiFlight WASM module"
                    )

                code = resolved.get("code")
                result = await self._mobiflight.execute_calculator_code(code)
                success = result is not None

            # Get response text
            response_text = None
            template = self._aircraft_detector.get_response_template(command_id)
            if template:
                response_text = template.format(value=value, state="engaged")

            return CommandResult(
                success=success,
                message="Command executed" if success else "Command failed",
                response_text=response_text,
                data=resolved
            )

        except Exception as e:
            logger.error(f"Error executing command {command_id}: {e}")
            return CommandResult(
                success=False,
                message=f"Error: {str(e)}"
            )

    def get_state(self) -> AircraftState:
        """Get current aircraft state."""
        if not self._connected:
            return AircraftState(connected=False)
        return self._sim_connection.update_state()

    async def get_lvar(self, lvar_name: str) -> Optional[float]:
        """
        Read an LVAR value.

        Args:
            lvar_name: LVAR name

        Returns:
            Value or None if not available
        """
        if not self._mobiflight_available:
            return None

        result = await self._mobiflight.read_lvar(lvar_name)
        return result.value if result.success else None

    def update_aircraft(self) -> Optional[AircraftProfile]:
        """
        Update aircraft detection.

        Call this when aircraft might have changed.

        Returns:
            New aircraft profile or None
        """
        if not self._connected:
            return None

        state = self._sim_connection.update_state()
        aircraft_title = state.aircraft_title

        if aircraft_title != self._current_aircraft:
            self._current_aircraft = aircraft_title
            self._current_profile = self._aircraft_detector.detect(aircraft_title)

            if self._on_aircraft_change:
                self._on_aircraft_change(aircraft_title, self._current_profile)

            logger.info(f"Aircraft changed to: {aircraft_title}")

        return self._current_profile

    def get_available_commands(self) -> list:
        """Get list of available commands for current aircraft."""
        return self._command_resolver.get_available_commands()

    def check_wasm_status(self) -> WASMStatus:
        """Check MobiFlight WASM installation status."""
        return self._wasm_manager.check_wasm_status()

    async def install_wasm(
        self,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> tuple:
        """
        Install MobiFlight WASM module.

        Args:
            progress_callback: Progress callback (message, percent)

        Returns:
            Tuple of (success, message)
        """
        return await self._wasm_manager.install_wasm(progress_callback)

    # Properties

    @property
    def is_connected(self) -> bool:
        """Check if connected to MSFS."""
        return self._connected

    @property
    def has_lvar_support(self) -> bool:
        """Check if LVAR support is available."""
        return self._mobiflight_available

    @property
    def current_aircraft(self) -> str:
        """Get current aircraft title."""
        return self._current_aircraft

    @property
    def current_profile(self) -> Optional[AircraftProfile]:
        """Get current aircraft profile."""
        return self._current_profile

    @property
    def community_folder(self) -> Optional[str]:
        """Get MSFS Community folder path."""
        path = self._wasm_manager.community_folder
        return str(path) if path else None

    # Callbacks

    def on_connection_change(self, callback: Callable[[bool], None]):
        """Register callback for connection state changes."""
        self._on_connection_change = callback

    def on_aircraft_change(
        self, callback: Callable[[str, AircraftProfile], None]
    ):
        """Register callback for aircraft changes."""
        self._on_aircraft_change = callback

    def on_state_update(self, callback: Callable[[AircraftState], None]):
        """Register callback for state updates."""
        self._on_state_update = callback
        self._sim_connection.on_state_change(callback)
