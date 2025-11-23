"""
Smart Flight Deck Companion - Command Definitions
Command registry and execution.
"""

import logging
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Types of commands."""

    ACTION = "action"  # Executes a SimConnect event
    QUERY = "query"  # Returns information
    CHECKLIST = "checklist"  # Checklist operations


@dataclass
class Command:
    """Definition of an executable command."""

    id: str
    name: str
    type: CommandType
    description: str
    sim_event: Optional[str] = None  # SimConnect event name
    response_template: str = ""  # TTS response template
    aliases: list = field(default_factory=list)
    requires_confirmation: bool = False
    safety_check: Optional[Callable] = None  # Validation function


class CommandRegistry:
    """
    Registry of all available commands.
    """

    _commands: Dict[str, Command] = {}

    @classmethod
    def register(cls, command: Command):
        """Register a command."""
        cls._commands[command.id] = command
        logger.debug(f"Registered command: {command.id}")

    @classmethod
    def get(cls, command_id: str) -> Optional[Command]:
        """Get command by ID."""
        return cls._commands.get(command_id)

    @classmethod
    def all(cls) -> Dict[str, Command]:
        """Get all registered commands."""
        return cls._commands.copy()

    @classmethod
    def by_type(cls, command_type: CommandType) -> Dict[str, Command]:
        """Get commands by type."""
        return {
            cid: cmd
            for cid, cmd in cls._commands.items()
            if cmd.type == command_type
        }


# ===========================
# Register Default Commands
# ===========================

# Gear commands
CommandRegistry.register(
    Command(
        id="gear_down",
        name="Gear Down",
        type=CommandType.ACTION,
        description="Extend landing gear",
        sim_event="GEAR_DOWN",
        response_template="Gear down",
        aliases=["lower gear", "extend gear"],
    )
)

CommandRegistry.register(
    Command(
        id="gear_up",
        name="Gear Up",
        type=CommandType.ACTION,
        description="Retract landing gear",
        sim_event="GEAR_UP",
        response_template="Gear up",
        aliases=["raise gear", "retract gear"],
    )
)

# Flaps commands
CommandRegistry.register(
    Command(
        id="flaps_up",
        name="Flaps Up",
        type=CommandType.ACTION,
        description="Retract flaps one notch",
        sim_event="FLAPS_UP",
        response_template="Flaps up",
    )
)

CommandRegistry.register(
    Command(
        id="flaps_down",
        name="Flaps Down",
        type=CommandType.ACTION,
        description="Extend flaps one notch",
        sim_event="FLAPS_DOWN",
        response_template="Flaps down",
    )
)

CommandRegistry.register(
    Command(
        id="flaps_set",
        name="Flaps Set",
        type=CommandType.ACTION,
        description="Set flaps to specific position",
        sim_event="FLAPS_SET",
        response_template="Flaps {position}",
    )
)

# Lights
CommandRegistry.register(
    Command(
        id="landing_lights_toggle",
        name="Landing Lights",
        type=CommandType.ACTION,
        description="Toggle landing lights",
        sim_event="LANDING_LIGHTS_TOGGLE",
        response_template="Landing lights",
    )
)

CommandRegistry.register(
    Command(
        id="beacon_lights_toggle",
        name="Beacon Lights",
        type=CommandType.ACTION,
        description="Toggle beacon lights",
        sim_event="TOGGLE_BEACON_LIGHTS",
        response_template="Beacon",
    )
)

CommandRegistry.register(
    Command(
        id="strobe_lights_toggle",
        name="Strobe Lights",
        type=CommandType.ACTION,
        description="Toggle strobe lights",
        sim_event="STROBES_TOGGLE",
        response_template="Strobes",
    )
)

CommandRegistry.register(
    Command(
        id="nav_lights_toggle",
        name="Navigation Lights",
        type=CommandType.ACTION,
        description="Toggle navigation lights",
        sim_event="TOGGLE_NAV_LIGHTS",
        response_template="Nav lights",
    )
)

CommandRegistry.register(
    Command(
        id="taxi_lights_toggle",
        name="Taxi Lights",
        type=CommandType.ACTION,
        description="Toggle taxi lights",
        sim_event="TOGGLE_TAXI_LIGHTS",
        response_template="Taxi lights",
    )
)

# Parking brake
CommandRegistry.register(
    Command(
        id="parking_brake_toggle",
        name="Parking Brake",
        type=CommandType.ACTION,
        description="Toggle parking brake",
        sim_event="PARKING_BRAKES",
        response_template="Parking brake",
    )
)

# Spoilers / Speedbrake
CommandRegistry.register(
    Command(
        id="spoilers_arm",
        name="Arm Spoilers",
        type=CommandType.ACTION,
        description="Arm ground spoilers",
        sim_event="SPOILERS_ARM_TOGGLE",
        response_template="Spoilers armed",
    )
)

CommandRegistry.register(
    Command(
        id="spoilers_on",
        name="Spoilers On",
        type=CommandType.ACTION,
        description="Deploy spoilers",
        sim_event="SPOILERS_ON",
        response_template="Speedbrake deployed",
    )
)

CommandRegistry.register(
    Command(
        id="spoilers_off",
        name="Spoilers Off",
        type=CommandType.ACTION,
        description="Retract spoilers",
        sim_event="SPOILERS_OFF",
        response_template="Speedbrake retracted",
    )
)

# Autobrake
CommandRegistry.register(
    Command(
        id="autobrake_off",
        name="Autobrake Off",
        type=CommandType.ACTION,
        description="Disable autobrake",
        sim_event="AUTO_BRAKE_DISARM",
        response_template="Autobrake off",
    )
)

CommandRegistry.register(
    Command(
        id="autobrake_lo",
        name="Autobrake Low",
        type=CommandType.ACTION,
        description="Set autobrake to low",
        sim_event="AUTO_BRAKE_LO_SET",
        response_template="Autobrake low",
    )
)

CommandRegistry.register(
    Command(
        id="autobrake_med",
        name="Autobrake Medium",
        type=CommandType.ACTION,
        description="Set autobrake to medium",
        sim_event="AUTO_BRAKE_MED_SET",
        response_template="Autobrake medium",
    )
)

CommandRegistry.register(
    Command(
        id="autobrake_hi",
        name="Autobrake High",
        type=CommandType.ACTION,
        description="Set autobrake to high",
        sim_event="AUTO_BRAKE_HI_SET",
        response_template="Autobrake high",
    )
)

CommandRegistry.register(
    Command(
        id="autobrake_max",
        name="Autobrake Max",
        type=CommandType.ACTION,
        description="Set autobrake to maximum",
        sim_event="AUTO_BRAKE_MAX_SET",
        response_template="Autobrake maximum",
    )
)

CommandRegistry.register(
    Command(
        id="autobrake_rto",
        name="Autobrake RTO",
        type=CommandType.ACTION,
        description="Set autobrake to rejected takeoff mode",
        sim_event="AUTO_BRAKE_RTO_SET",
        response_template="Autobrake RTO",
    )
)

# Trim
CommandRegistry.register(
    Command(
        id="elevator_trim_up",
        name="Trim Up",
        type=CommandType.ACTION,
        description="Trim nose up",
        sim_event="ELEV_TRIM_UP",
        response_template="Trim up",
    )
)

CommandRegistry.register(
    Command(
        id="elevator_trim_down",
        name="Trim Down",
        type=CommandType.ACTION,
        description="Trim nose down",
        sim_event="ELEV_TRIM_DN",
        response_template="Trim down",
    )
)

CommandRegistry.register(
    Command(
        id="aileron_trim_left",
        name="Aileron Trim Left",
        type=CommandType.ACTION,
        description="Trim ailerons left",
        sim_event="AILERON_TRIM_LEFT",
        response_template="Aileron trim left",
    )
)

CommandRegistry.register(
    Command(
        id="aileron_trim_right",
        name="Aileron Trim Right",
        type=CommandType.ACTION,
        description="Trim ailerons right",
        sim_event="AILERON_TRIM_RIGHT",
        response_template="Aileron trim right",
    )
)

CommandRegistry.register(
    Command(
        id="rudder_trim_left",
        name="Rudder Trim Left",
        type=CommandType.ACTION,
        description="Trim rudder left",
        sim_event="RUDDER_TRIM_LEFT",
        response_template="Rudder trim left",
    )
)

CommandRegistry.register(
    Command(
        id="rudder_trim_right",
        name="Rudder Trim Right",
        type=CommandType.ACTION,
        description="Trim rudder right",
        sim_event="RUDDER_TRIM_RIGHT",
        response_template="Rudder trim right",
    )
)

# APU
CommandRegistry.register(
    Command(
        id="apu_start",
        name="APU Start",
        type=CommandType.ACTION,
        description="Start the APU",
        sim_event="APU_STARTER",
        response_template="APU starting",
    )
)

CommandRegistry.register(
    Command(
        id="apu_off",
        name="APU Off",
        type=CommandType.ACTION,
        description="Shutdown the APU",
        sim_event="APU_OFF_SWITCH",
        response_template="APU shutdown",
    )
)

# Engines
CommandRegistry.register(
    Command(
        id="engines_start",
        name="Engines Start",
        type=CommandType.ACTION,
        description="Start all engines",
        sim_event="ENGINE_AUTO_START",
        response_template="Engines starting",
    )
)

CommandRegistry.register(
    Command(
        id="engines_off",
        name="Engines Off",
        type=CommandType.ACTION,
        description="Shutdown all engines",
        sim_event="ENGINE_AUTO_SHUTDOWN",
        response_template="Engines shutdown",
    )
)

CommandRegistry.register(
    Command(
        id="engine1_start",
        name="Engine 1 Start",
        type=CommandType.ACTION,
        description="Start engine 1",
        sim_event="SET_STARTER1_HELD",
        response_template="Engine 1 starting",
    )
)

CommandRegistry.register(
    Command(
        id="engine2_start",
        name="Engine 2 Start",
        type=CommandType.ACTION,
        description="Start engine 2",
        sim_event="SET_STARTER2_HELD",
        response_template="Engine 2 starting",
    )
)

# Transponder
CommandRegistry.register(
    Command(
        id="xpndr_standby",
        name="Transponder Standby",
        type=CommandType.ACTION,
        description="Set transponder to standby",
        sim_event="XPNDR_SET",
        response_template="Transponder standby",
    )
)

CommandRegistry.register(
    Command(
        id="xpndr_on",
        name="Transponder On",
        type=CommandType.ACTION,
        description="Set transponder to altitude mode",
        sim_event="XPNDR_SET",
        response_template="Transponder on",
    )
)

CommandRegistry.register(
    Command(
        id="xpndr_ident",
        name="Transponder Ident",
        type=CommandType.ACTION,
        description="Squawk ident",
        sim_event="XPNDR_IDENT_ON",
        response_template="Squawk ident",
    )
)

CommandRegistry.register(
    Command(
        id="xpndr_set",
        name="Set Squawk Code",
        type=CommandType.ACTION,
        description="Set transponder code",
        sim_event="XPNDR_SET",
        response_template="Squawk {code}",
    )
)

# Autopilot
CommandRegistry.register(
    Command(
        id="ap_master",
        name="Autopilot Master",
        type=CommandType.ACTION,
        description="Toggle autopilot",
        sim_event="AP_MASTER",
        response_template="Autopilot",
    )
)

CommandRegistry.register(
    Command(
        id="ap_heading_hold",
        name="Heading Hold",
        type=CommandType.ACTION,
        description="Toggle heading hold",
        sim_event="AP_PANEL_HEADING_HOLD",
        response_template="Heading hold",
    )
)

CommandRegistry.register(
    Command(
        id="ap_altitude_hold",
        name="Altitude Hold",
        type=CommandType.ACTION,
        description="Toggle altitude hold",
        sim_event="AP_PANEL_ALTITUDE_HOLD",
        response_template="Altitude hold",
    )
)

CommandRegistry.register(
    Command(
        id="ap_nav_hold",
        name="NAV Hold",
        type=CommandType.ACTION,
        description="Toggle NAV hold",
        sim_event="AP_NAV1_HOLD",
        response_template="Nav hold",
    )
)

CommandRegistry.register(
    Command(
        id="ap_approach",
        name="Approach Mode",
        type=CommandType.ACTION,
        description="Toggle approach mode",
        sim_event="AP_APR_HOLD",
        response_template="Approach mode",
    )
)

CommandRegistry.register(
    Command(
        id="ap_vs_hold",
        name="Vertical Speed",
        type=CommandType.ACTION,
        description="Toggle vertical speed hold",
        sim_event="AP_VS_HOLD",
        response_template="Vertical speed",
    )
)

CommandRegistry.register(
    Command(
        id="ap_flc",
        name="Flight Level Change",
        type=CommandType.ACTION,
        description="Toggle flight level change",
        sim_event="FLIGHT_LEVEL_CHANGE",
        response_template="Flight level change",
    )
)

CommandRegistry.register(
    Command(
        id="ap_speed_hold",
        name="Speed Hold",
        type=CommandType.ACTION,
        description="Toggle autothrottle/speed hold",
        sim_event="AP_PANEL_SPEED_HOLD",
        response_template="Speed hold",
    )
)

# Radio/Comms
CommandRegistry.register(
    Command(
        id="com1_swap",
        name="COM1 Swap",
        type=CommandType.ACTION,
        description="Swap COM1 frequencies",
        sim_event="COM_STBY_RADIO_SWAP",
        response_template="COM 1 swapped",
    )
)

CommandRegistry.register(
    Command(
        id="com2_swap",
        name="COM2 Swap",
        type=CommandType.ACTION,
        description="Swap COM2 frequencies",
        sim_event="COM2_RADIO_SWAP",
        response_template="COM 2 swapped",
    )
)

CommandRegistry.register(
    Command(
        id="nav1_swap",
        name="NAV1 Swap",
        type=CommandType.ACTION,
        description="Swap NAV1 frequencies",
        sim_event="NAV1_RADIO_SWAP",
        response_template="NAV 1 swapped",
    )
)

CommandRegistry.register(
    Command(
        id="nav2_swap",
        name="NAV2 Swap",
        type=CommandType.ACTION,
        description="Swap NAV2 frequencies",
        sim_event="NAV2_RADIO_SWAP",
        response_template="NAV 2 swapped",
    )
)

# Cabin/Doors
CommandRegistry.register(
    Command(
        id="toggle_door",
        name="Toggle Door",
        type=CommandType.ACTION,
        description="Toggle main door",
        sim_event="TOGGLE_AIRCRAFT_EXIT",
        response_template="Door toggled",
    )
)

CommandRegistry.register(
    Command(
        id="toggle_door1",
        name="Toggle Door 1",
        type=CommandType.ACTION,
        description="Toggle exit 1",
        sim_event="TOGGLE_AIRCRAFT_EXIT_FAST",
        response_template="Door 1 toggled",
    )
)

CommandRegistry.register(
    Command(
        id="toggle_door2",
        name="Toggle Door 2",
        type=CommandType.ACTION,
        description="Toggle exit 2",
        sim_event="TOGGLE_AIRCRAFT_EXIT_FAST",
        response_template="Door 2 toggled",
    )
)

CommandRegistry.register(
    Command(
        id="seatbelt_sign",
        name="Seatbelt Sign",
        type=CommandType.ACTION,
        description="Toggle seatbelt sign",
        sim_event="CABIN_SEATBELTS_ALERT_SWITCH_TOGGLE",
        response_template="Seatbelt sign",
    )
)

CommandRegistry.register(
    Command(
        id="no_smoking_sign",
        name="No Smoking Sign",
        type=CommandType.ACTION,
        description="Toggle no smoking sign",
        sim_event="CABIN_NO_SMOKING_ALERT_SWITCH_TOGGLE",
        response_template="No smoking sign",
    )
)

# Query commands
CommandRegistry.register(
    Command(
        id="query_speed",
        name="Check Speed",
        type=CommandType.QUERY,
        description="Report current speed",
        response_template="Current speed is {speed} knots",
    )
)

CommandRegistry.register(
    Command(
        id="query_altitude",
        name="Check Altitude",
        type=CommandType.QUERY,
        description="Report current altitude",
        response_template="Altitude is {altitude} feet",
    )
)

CommandRegistry.register(
    Command(
        id="query_heading",
        name="Check Heading",
        type=CommandType.QUERY,
        description="Report current heading",
        response_template="Heading is {heading} degrees",
    )
)

CommandRegistry.register(
    Command(
        id="query_fuel",
        name="Check Fuel",
        type=CommandType.QUERY,
        description="Report fuel remaining",
        response_template="Fuel remaining {fuel_percent} percent",
    )
)
