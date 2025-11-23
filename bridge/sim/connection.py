"""
Smart Flight Deck Companion - SimConnect Connection
Manages connection to Microsoft Flight Simulator.
"""

import logging
from typing import Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AircraftState:
    """Current aircraft state data."""

    connected: bool = False
    aircraft_title: str = ""
    on_ground: bool = True
    altitude: float = 0.0  # feet
    indicated_airspeed: float = 0.0  # knots
    ground_speed: float = 0.0  # knots
    heading: float = 0.0  # degrees
    vertical_speed: float = 0.0  # feet per minute
    gear_handle_position: int = 0  # 0=up, 1=down
    flaps_handle_index: int = 0  # 0-4 typically
    parking_brake: bool = False
    engine_running: bool = False


class SimConnection:
    """
    SimConnect connection manager.

    Handles connection lifecycle and data polling.
    """

    def __init__(self):
        self._connected = False
        self._sim = None
        self._aircraft_state = AircraftState()
        self._on_state_change: Optional[Callable] = None

    def connect(self) -> bool:
        """
        Establish connection to MSFS.

        Returns:
            True if connection successful
        """
        try:
            from SimConnect import SimConnect, AircraftRequests

            logger.info("Connecting to MSFS...")
            self._sim = SimConnect()
            self._aircraft_requests = AircraftRequests(self._sim, _time=200)
            self._connected = True
            logger.info("Connected to MSFS successfully")
            return True

        except Exception as e:
            logger.warning(f"Could not connect to MSFS: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Disconnect from MSFS."""
        if self._sim:
            try:
                self._sim.exit()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            finally:
                self._sim = None
                self._connected = False
                logger.info("Disconnected from MSFS")

    def update_state(self) -> AircraftState:
        """
        Poll current aircraft state.

        Returns:
            Updated AircraftState
        """
        if not self._connected or not self._sim:
            return AircraftState(connected=False)

        try:
            ar = self._aircraft_requests

            self._aircraft_state = AircraftState(
                connected=True,
                aircraft_title=str(ar.get("TITLE") or "Unknown"),
                on_ground=bool(ar.get("SIM_ON_GROUND")),
                altitude=float(ar.get("PLANE_ALTITUDE") or 0),
                indicated_airspeed=float(ar.get("AIRSPEED_INDICATED") or 0),
                ground_speed=float(ar.get("GROUND_VELOCITY") or 0),
                heading=float(ar.get("PLANE_HEADING_DEGREES_TRUE") or 0),
                vertical_speed=float(ar.get("VERTICAL_SPEED") or 0),
                gear_handle_position=int(ar.get("GEAR_HANDLE_POSITION") or 0),
                flaps_handle_index=int(ar.get("FLAPS_HANDLE_INDEX") or 0),
                parking_brake=bool(ar.get("BRAKE_PARKING_INDICATOR")),
                engine_running=bool(ar.get("ENG_COMBUSTION:1")),
            )

            return self._aircraft_state

        except Exception as e:
            logger.error(f"Error updating state: {e}")
            return self._aircraft_state

    def send_event(self, event_name: str, value: int = 0) -> bool:
        """
        Send an event to the simulator.

        Args:
            event_name: SimConnect event name (e.g., "GEAR_DOWN")
            value: Event value (if applicable)

        Returns:
            True if event sent successfully
        """
        if not self._connected or not self._sim:
            logger.warning("Cannot send event: not connected")
            return False

        try:
            from SimConnect import AircraftEvents

            ae = AircraftEvents(self._sim)
            event = ae.find(event_name)

            if event:
                event(value)
                logger.debug(f"Event sent: {event_name} = {value}")
                return True
            else:
                logger.warning(f"Event not found: {event_name}")
                return False

        except Exception as e:
            logger.error(f"Error sending event {event_name}: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        """Check if connected to MSFS."""
        return self._connected

    @property
    def state(self) -> AircraftState:
        """Get last known aircraft state."""
        return self._aircraft_state

    def on_state_change(self, callback: Callable[[AircraftState], None]):
        """Register callback for state changes."""
        self._on_state_change = callback
