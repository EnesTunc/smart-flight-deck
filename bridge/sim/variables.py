"""
Smart Flight Deck Companion - SimConnect Variables
SimVar definitions for reading aircraft data.
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass


class VarUnit(Enum):
    """Units for simulator variables."""

    BOOL = "Bool"
    NUMBER = "Number"
    FEET = "Feet"
    KNOTS = "Knots"
    DEGREES = "Degrees"
    PERCENT = "Percent"
    FEET_PER_MINUTE = "Feet per minute"
    POUNDS = "Pounds"
    GALLONS = "Gallons"
    CELSIUS = "Celsius"
    INHG = "inHg"
    MBAR = "Millibars"
    ENUM = "Enum"
    POSITION = "Position"
    MASK = "Mask"


@dataclass
class SimVariable:
    """Definition of a simulator variable."""

    name: str  # SimConnect variable name
    unit: VarUnit
    description: str
    settable: bool = False


class SimVariables:
    """
    SimConnect variable definitions.

    Used for reading aircraft state.
    """

    # Core flight data
    FLIGHT_DATA: Dict[str, SimVariable] = {
        "altitude": SimVariable(
            "PLANE_ALTITUDE", VarUnit.FEET, "Current altitude MSL"
        ),
        "altitude_agl": SimVariable(
            "PLANE_ALT_ABOVE_GROUND", VarUnit.FEET, "Altitude above ground"
        ),
        "indicated_airspeed": SimVariable(
            "AIRSPEED_INDICATED", VarUnit.KNOTS, "Indicated airspeed"
        ),
        "true_airspeed": SimVariable(
            "AIRSPEED_TRUE", VarUnit.KNOTS, "True airspeed"
        ),
        "ground_speed": SimVariable(
            "GROUND_VELOCITY", VarUnit.KNOTS, "Ground speed"
        ),
        "vertical_speed": SimVariable(
            "VERTICAL_SPEED", VarUnit.FEET_PER_MINUTE, "Vertical speed"
        ),
        "heading": SimVariable(
            "PLANE_HEADING_DEGREES_TRUE", VarUnit.DEGREES, "True heading"
        ),
        "heading_magnetic": SimVariable(
            "PLANE_HEADING_DEGREES_MAGNETIC", VarUnit.DEGREES, "Magnetic heading"
        ),
        "pitch": SimVariable(
            "PLANE_PITCH_DEGREES", VarUnit.DEGREES, "Pitch angle"
        ),
        "bank": SimVariable(
            "PLANE_BANK_DEGREES", VarUnit.DEGREES, "Bank angle"
        ),
    }

    # Aircraft systems
    SYSTEMS: Dict[str, SimVariable] = {
        "gear_handle": SimVariable(
            "GEAR_HANDLE_POSITION", VarUnit.BOOL, "Gear handle position"
        ),
        "gear_center": SimVariable(
            "GEAR_CENTER_POSITION", VarUnit.PERCENT, "Center gear position"
        ),
        "gear_left": SimVariable(
            "GEAR_LEFT_POSITION", VarUnit.PERCENT, "Left gear position"
        ),
        "gear_right": SimVariable(
            "GEAR_RIGHT_POSITION", VarUnit.PERCENT, "Right gear position"
        ),
        "flaps_handle": SimVariable(
            "FLAPS_HANDLE_INDEX", VarUnit.NUMBER, "Flaps handle index"
        ),
        "flaps_position": SimVariable(
            "FLAPS_HANDLE_PERCENT", VarUnit.PERCENT, "Flaps position percent"
        ),
        "spoilers_armed": SimVariable(
            "SPOILERS_ARMED", VarUnit.BOOL, "Spoilers armed"
        ),
        "spoilers_position": SimVariable(
            "SPOILERS_HANDLE_POSITION", VarUnit.PERCENT, "Spoilers position"
        ),
        "parking_brake": SimVariable(
            "BRAKE_PARKING_INDICATOR", VarUnit.BOOL, "Parking brake set"
        ),
    }

    # Environment
    ENVIRONMENT: Dict[str, SimVariable] = {
        "on_ground": SimVariable(
            "SIM_ON_GROUND", VarUnit.BOOL, "Aircraft on ground"
        ),
        "ambient_temperature": SimVariable(
            "AMBIENT_TEMPERATURE", VarUnit.CELSIUS, "Outside air temperature"
        ),
        "barometer": SimVariable(
            "KOHLSMAN_SETTING_HG", VarUnit.INHG, "Altimeter setting"
        ),
    }

    # Engine
    ENGINE: Dict[str, SimVariable] = {
        "engine1_running": SimVariable(
            "ENG_COMBUSTION:1", VarUnit.BOOL, "Engine 1 running"
        ),
        "engine2_running": SimVariable(
            "ENG_COMBUSTION:2", VarUnit.BOOL, "Engine 2 running"
        ),
        "throttle1": SimVariable(
            "GENERAL_ENG_THROTTLE_LEVER_POSITION:1",
            VarUnit.PERCENT,
            "Engine 1 throttle",
        ),
        "throttle2": SimVariable(
            "GENERAL_ENG_THROTTLE_LEVER_POSITION:2",
            VarUnit.PERCENT,
            "Engine 2 throttle",
        ),
    }

    # Fuel
    FUEL: Dict[str, SimVariable] = {
        "fuel_total": SimVariable(
            "FUEL_TOTAL_QUANTITY", VarUnit.GALLONS, "Total fuel quantity"
        ),
        "fuel_percent": SimVariable(
            "FUEL_TOTAL_CAPACITY_PERCENT", VarUnit.PERCENT, "Fuel percentage"
        ),
    }

    # Navigation
    NAVIGATION: Dict[str, SimVariable] = {
        "nav1_freq": SimVariable(
            "NAV_ACTIVE_FREQUENCY:1", VarUnit.NUMBER, "NAV1 frequency"
        ),
        "nav1_ident": SimVariable(
            "NAV_IDENT:1", VarUnit.ENUM, "NAV1 ident"
        ),
        "nav1_dme": SimVariable(
            "NAV_DME:1", VarUnit.NUMBER, "NAV1 DME distance"
        ),
        "nav2_freq": SimVariable(
            "NAV_ACTIVE_FREQUENCY:2", VarUnit.NUMBER, "NAV2 frequency"
        ),
        "nav2_ident": SimVariable(
            "NAV_IDENT:2", VarUnit.ENUM, "NAV2 ident"
        ),
        "nav2_dme": SimVariable(
            "NAV_DME:2", VarUnit.NUMBER, "NAV2 DME distance"
        ),
        "gps_ground_track": SimVariable(
            "GPS_GROUND_TRUE_TRACK", VarUnit.DEGREES, "GPS ground track"
        ),
    }

    # Wind
    WIND: Dict[str, SimVariable] = {
        "wind_direction": SimVariable(
            "AMBIENT_WIND_DIRECTION", VarUnit.DEGREES, "Wind direction"
        ),
        "wind_speed": SimVariable(
            "AMBIENT_WIND_VELOCITY", VarUnit.KNOTS, "Wind speed"
        ),
    }

    # Position
    POSITION: Dict[str, SimVariable] = {
        "latitude": SimVariable(
            "PLANE_LATITUDE", VarUnit.DEGREES, "Aircraft latitude"
        ),
        "longitude": SimVariable(
            "PLANE_LONGITUDE", VarUnit.DEGREES, "Aircraft longitude"
        ),
        "mach": SimVariable(
            "AIRSPEED_MACH", VarUnit.NUMBER, "Mach number"
        ),
    }

    # Aircraft info
    AIRCRAFT: Dict[str, SimVariable] = {
        "title": SimVariable("TITLE", VarUnit.ENUM, "Aircraft title"),
        "atc_id": SimVariable("ATC_ID", VarUnit.ENUM, "ATC callsign"),
    }

    @classmethod
    def get_all_variables(cls) -> Dict[str, SimVariable]:
        """Get all variable definitions."""
        all_vars = {}
        all_vars.update(cls.FLIGHT_DATA)
        all_vars.update(cls.SYSTEMS)
        all_vars.update(cls.ENVIRONMENT)
        all_vars.update(cls.ENGINE)
        all_vars.update(cls.FUEL)
        all_vars.update(cls.NAVIGATION)
        all_vars.update(cls.WIND)
        all_vars.update(cls.POSITION)
        all_vars.update(cls.AIRCRAFT)
        return all_vars

    @classmethod
    def get_simconnect_name(cls, var_id: str) -> Optional[str]:
        """Get SimConnect variable name by ID."""
        all_vars = cls.get_all_variables()
        var = all_vars.get(var_id)
        return var.name if var else None
