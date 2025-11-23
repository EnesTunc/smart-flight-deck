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

# Spoilers
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
