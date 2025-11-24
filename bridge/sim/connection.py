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

    # Connection status
    connected: bool = False

    # Aircraft info
    aircraft_title: str = ""

    # Position
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: float = 0.0  # feet MSL
    altitude_agl: float = 0.0  # feet AGL
    heading: float = 0.0  # degrees true
    track: float = 0.0  # degrees GPS ground track

    # Speed
    indicated_airspeed: float = 0.0  # knots
    true_airspeed: float = 0.0  # knots
    ground_speed: float = 0.0  # knots
    mach: float = 0.0
    vertical_speed: float = 0.0  # feet per minute

    # Aircraft systems
    on_ground: bool = True
    gear_handle_position: int = 0  # 0=up, 1=down
    flaps_handle_index: int = 0  # 0-4 typically
    spoilers_armed: bool = False
    parking_brake: bool = False
    engine_running: bool = False

    # Fuel
    fuel_total_kg: float = 0.0
    fuel_flow_kg_h: float = 0.0
    fuel_percent: float = 0.0

    # Navigation
    nav1_freq: float = 0.0
    nav1_ident: str = ""
    nav1_dme: float = 0.0
    nav2_freq: float = 0.0
    nav2_ident: str = ""
    nav2_dme: float = 0.0

    # Environment
    wind_direction: float = 0.0  # degrees
    wind_speed: float = 0.0  # knots
    oat: float = 0.0  # celsius
    qnh: float = 1013.0  # millibars


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

            # Get aircraft title and decode if bytes
            title = ar.get("TITLE") or "Unknown"
            if isinstance(title, bytes):
                title = title.decode('utf-8', errors='ignore')

            # Helper function to safely decode string values
            def decode_str(value, default=""):
                if value is None:
                    return default
                if isinstance(value, bytes):
                    return value.decode('utf-8', errors='ignore')
                return str(value)

            # Helper function to safely get float values
            def get_float(name, default=0.0):
                try:
                    val = ar.get(name)
                    return float(val) if val is not None else default
                except (TypeError, ValueError):
                    return default

            # Helper function to safely get int values
            def get_int(name, default=0):
                try:
                    val = ar.get(name)
                    return int(val) if val is not None else default
                except (TypeError, ValueError):
                    return default

            # Convert fuel from gallons to kg (approximate with Jet-A density 3.0 kg/gal)
            fuel_gallons = get_float("FUEL_TOTAL_QUANTITY")
            fuel_kg = fuel_gallons * 3.0

            # Convert fuel flow from gallons/hour to kg/hour
            # Sum both engines if available
            fuel_flow_gph = get_float("ENG_FUEL_FLOW_GPH:1") + get_float("ENG_FUEL_FLOW_GPH:2")
            fuel_flow_kg_h = fuel_flow_gph * 3.0

            # Convert barometer from inHg to millibars
            baro_inhg = get_float("KOHLSMAN_SETTING_HG", 29.92)
            qnh_mbar = baro_inhg * 33.8639

            self._aircraft_state = AircraftState(
                connected=True,
                aircraft_title=str(title),

                # Position
                latitude=get_float("PLANE_LATITUDE"),
                longitude=get_float("PLANE_LONGITUDE"),
                altitude=get_float("PLANE_ALTITUDE"),
                altitude_agl=get_float("PLANE_ALT_ABOVE_GROUND"),
                heading=get_float("PLANE_HEADING_DEGREES_TRUE"),
                track=get_float("GPS_GROUND_TRUE_TRACK"),

                # Speed
                indicated_airspeed=get_float("AIRSPEED_INDICATED"),
                true_airspeed=get_float("AIRSPEED_TRUE"),
                ground_speed=get_float("GROUND_VELOCITY"),
                mach=get_float("AIRSPEED_MACH"),
                vertical_speed=get_float("VERTICAL_SPEED"),

                # Aircraft systems
                on_ground=bool(ar.get("SIM_ON_GROUND")),
                gear_handle_position=get_int("GEAR_HANDLE_POSITION"),
                flaps_handle_index=get_int("FLAPS_HANDLE_INDEX"),
                spoilers_armed=bool(ar.get("SPOILERS_ARMED")),
                parking_brake=bool(ar.get("BRAKE_PARKING_INDICATOR")),
                engine_running=bool(ar.get("ENG_COMBUSTION:1")),

                # Fuel
                fuel_total_kg=fuel_kg,
                fuel_flow_kg_h=fuel_flow_kg_h,
                fuel_percent=get_float("FUEL_TOTAL_CAPACITY_PERCENT"),

                # Navigation
                nav1_freq=get_float("NAV_ACTIVE_FREQUENCY:1"),
                nav1_ident=decode_str(ar.get("NAV_IDENT:1")),
                nav1_dme=get_float("NAV_DME:1"),
                nav2_freq=get_float("NAV_ACTIVE_FREQUENCY:2"),
                nav2_ident=decode_str(ar.get("NAV_IDENT:2")),
                nav2_dme=get_float("NAV_DME:2"),

                # Environment
                wind_direction=get_float("AMBIENT_WIND_DIRECTION"),
                wind_speed=get_float("AMBIENT_WIND_VELOCITY"),
                oat=get_float("AMBIENT_TEMPERATURE"),
                qnh=qnh_mbar,
            )

            return self._aircraft_state

        except Exception as e:
            logger.error(f"Error updating state: {e}")
            # Connection lost - reset state
            self._connected = False
            self._aircraft_state = AircraftState(connected=False)
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
