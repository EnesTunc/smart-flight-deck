"""
Smart Flight Deck Companion - SimConnect Connection
Manages connection to Microsoft Flight Simulator.
"""

import logging
import math
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
    heading: float = 0.0  # degrees magnetic
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
        self._aircraft_requests = None
        self._last_aircraft_title = ""
        self._aircraft_state = AircraftState()
        self._last_valid_state = None  # Keep last good state for pause/menu
        self._on_state_change: Optional[Callable] = None

    def connect(self) -> bool:
        """
        Establish connection to MSFS.

        Returns:
            True if connection successful
        """
        try:
            from SimConnect import SimConnect

            logger.info("Connecting to MSFS...")
            self._sim = SimConnect()
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
                self._aircraft_requests = None
                self._last_aircraft_title = ""
                self._last_valid_state = None
                self._connected = False
                logger.info("Disconnected from MSFS")

    def _calculate_fuel_percent(self, fuel_kg: float) -> float:
        """
        Calculate fuel percentage from fuel quantity and capacity.

        Args:
            fuel_kg: Current fuel quantity in kg

        Returns:
            Fuel percentage (0-100)
        """
        try:
            if not self._sim or not self._aircraft_requests:
                return 0.0

            # Use cached AircraftRequests to avoid object overflow
            ar = self._aircraft_requests

            # Try to get fuel capacity (different SimVars for different aircraft)
            fuel_capacity_gallons = None

            # Method 1: Try FUEL_TOTAL_CAPACITY (works for most aircraft)
            try:
                fuel_capacity_gallons = ar.get("FUEL_TOTAL_CAPACITY")
            except:
                pass

            # Method 2: Try FUEL_TANK_*_CAPACITY and sum them
            if not fuel_capacity_gallons or fuel_capacity_gallons <= 0:
                try:
                    center = ar.get("FUEL_TANK_CENTER_CAPACITY") or 0
                    left = ar.get("FUEL_TANK_LEFT_MAIN_CAPACITY") or 0
                    right = ar.get("FUEL_TANK_RIGHT_MAIN_CAPACITY") or 0
                    fuel_capacity_gallons = center + left + right
                except:
                    pass

            if not fuel_capacity_gallons or fuel_capacity_gallons <= 0:
                logger.debug("Could not get fuel capacity, returning 0%")
                return 0.0

            # Convert capacity to kg (1 gallon jet fuel ≈ 3.02 kg)
            fuel_capacity_kg = fuel_capacity_gallons * 3.02

            # Calculate percentage
            percent = (fuel_kg / fuel_capacity_kg) * 100.0
            return min(100.0, max(0.0, percent))  # Clamp to 0-100

        except Exception as e:
            logger.debug(f"Error calculating fuel percent: {e}")
            return 0.0

    def update_state(self) -> AircraftState:
        """
        Poll current aircraft state.

        Returns:
            Updated AircraftState
        """
        if not self._connected or not self._sim:
            return AircraftState(connected=False)

        try:
            from SimConnect import AircraftRequests

            # Create or reuse AircraftRequests with caching
            if self._aircraft_requests is None:
                self._aircraft_requests = AircraftRequests(self._sim, _time=200)

            ar = self._aircraft_requests

            # Get current aircraft title to detect flight changes
            current_title = ar.get("TITLE") or "Unknown"
            if isinstance(current_title, bytes):
                current_title = current_title.decode('utf-8', errors='ignore')

            # If aircraft changed, recreate AircraftRequests
            if current_title != self._last_aircraft_title and self._last_aircraft_title != "":
                logger.info(f"Aircraft changed: {self._last_aircraft_title} -> {current_title}")
                self._aircraft_requests = AircraftRequests(self._sim, _time=200)
                ar = self._aircraft_requests

            self._last_aircraft_title = current_title
            title = current_title

            # Helper function to safely decode string values
            def decode_str(value, default=""):
                if value is None:
                    return default
                if isinstance(value, bytes):
                    return value.decode('utf-8', errors='ignore')
                return str(value)

            # Helper function to safely get float values
            def get_float(name, default=0.0, unit=None):
                try:
                    # If unit specified, use it (important for angles!)
                    if unit:
                        val = ar.get((name, unit))
                    else:
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
                heading=math.degrees(get_float("PLANE_HEADING_DEGREES_MAGNETIC")),  # Convert radians to degrees
                track=math.degrees(get_float("GPS_GROUND_TRUE_TRACK")),  # Convert radians to degrees

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
                fuel_percent=self._calculate_fuel_percent(fuel_kg),

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

            # Save as last valid state (for pause/menu scenarios)
            self._last_valid_state = self._aircraft_state
            return self._aircraft_state

        except Exception as e:
            logger.error(f"Error updating state: {e}")

            # If we have a valid last state, return it (MSFS paused or in menu)
            if self._last_valid_state is not None:
                logger.debug("Returning last valid state (MSFS paused or in menu)")
                return self._last_valid_state

            # No valid state - connection truly lost
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
