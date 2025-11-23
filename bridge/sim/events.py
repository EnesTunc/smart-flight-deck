"""
Smart Flight Deck Companion - SimConnect Events
Event definitions and mappings.
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass


class EventCategory(Enum):
    """Categories of simulator events."""

    GEAR = "gear"
    FLAPS = "flaps"
    LIGHTS = "lights"
    AUTOPILOT = "autopilot"
    ENGINES = "engines"
    CONTROLS = "controls"
    SYSTEMS = "systems"


@dataclass
class SimEvent:
    """Definition of a simulator event."""

    name: str  # SimConnect event name
    category: EventCategory
    description: str
    requires_value: bool = False
    min_value: Optional[int] = None
    max_value: Optional[int] = None


class SimEvents:
    """
    SimConnect event definitions.

    Maps voice commands to simulator events.
    """

    # Event definitions
    EVENTS: Dict[str, SimEvent] = {
        # Gear
        "gear_toggle": SimEvent(
            "GEAR_TOGGLE", EventCategory.GEAR, "Toggle landing gear"
        ),
        "gear_up": SimEvent("GEAR_UP", EventCategory.GEAR, "Retract landing gear"),
        "gear_down": SimEvent("GEAR_DOWN", EventCategory.GEAR, "Extend landing gear"),
        # Flaps
        "flaps_up": SimEvent("FLAPS_UP", EventCategory.FLAPS, "Retract flaps one notch"),
        "flaps_down": SimEvent(
            "FLAPS_DOWN", EventCategory.FLAPS, "Extend flaps one notch"
        ),
        "flaps_set": SimEvent(
            "FLAPS_SET",
            EventCategory.FLAPS,
            "Set flaps position",
            requires_value=True,
            min_value=0,
            max_value=16383,
        ),
        # Lights
        "landing_lights_toggle": SimEvent(
            "LANDING_LIGHTS_TOGGLE", EventCategory.LIGHTS, "Toggle landing lights"
        ),
        "landing_lights_on": SimEvent(
            "LANDING_LIGHTS_ON", EventCategory.LIGHTS, "Turn on landing lights"
        ),
        "landing_lights_off": SimEvent(
            "LANDING_LIGHTS_OFF", EventCategory.LIGHTS, "Turn off landing lights"
        ),
        "strobe_lights_toggle": SimEvent(
            "STROBES_TOGGLE", EventCategory.LIGHTS, "Toggle strobe lights"
        ),
        "nav_lights_toggle": SimEvent(
            "TOGGLE_NAV_LIGHTS", EventCategory.LIGHTS, "Toggle navigation lights"
        ),
        "beacon_lights_toggle": SimEvent(
            "TOGGLE_BEACON_LIGHTS", EventCategory.LIGHTS, "Toggle beacon lights"
        ),
        "taxi_lights_toggle": SimEvent(
            "TOGGLE_TAXI_LIGHTS", EventCategory.LIGHTS, "Toggle taxi lights"
        ),
        # Parking Brake
        "parking_brake_toggle": SimEvent(
            "PARKING_BRAKES", EventCategory.CONTROLS, "Toggle parking brake"
        ),
        # Spoilers
        "spoilers_arm": SimEvent(
            "SPOILERS_ARM_TOGGLE", EventCategory.CONTROLS, "Arm/disarm spoilers"
        ),
        "spoilers_on": SimEvent(
            "SPOILERS_ON", EventCategory.CONTROLS, "Deploy spoilers"
        ),
        "spoilers_off": SimEvent(
            "SPOILERS_OFF", EventCategory.CONTROLS, "Retract spoilers"
        ),
        # Autopilot
        "ap_master": SimEvent(
            "AP_MASTER", EventCategory.AUTOPILOT, "Toggle autopilot master"
        ),
        "ap_heading_hold": SimEvent(
            "AP_PANEL_HEADING_HOLD", EventCategory.AUTOPILOT, "Toggle heading hold"
        ),
        "ap_altitude_hold": SimEvent(
            "AP_PANEL_ALTITUDE_HOLD", EventCategory.AUTOPILOT, "Toggle altitude hold"
        ),
        "ap_nav_hold": SimEvent(
            "AP_NAV1_HOLD", EventCategory.AUTOPILOT, "Toggle NAV hold"
        ),
        "ap_approach": SimEvent(
            "AP_APR_HOLD", EventCategory.AUTOPILOT, "Toggle approach mode"
        ),
    }

    @classmethod
    def get_event(cls, event_id: str) -> Optional[SimEvent]:
        """Get event definition by ID."""
        return cls.EVENTS.get(event_id)

    @classmethod
    def get_simconnect_name(cls, event_id: str) -> Optional[str]:
        """Get SimConnect event name by ID."""
        event = cls.EVENTS.get(event_id)
        return event.name if event else None

    @classmethod
    def list_by_category(cls, category: EventCategory) -> Dict[str, SimEvent]:
        """Get all events in a category."""
        return {
            eid: event
            for eid, event in cls.EVENTS.items()
            if event.category == category
        }

    @classmethod
    def all_event_ids(cls) -> list:
        """Get all event IDs."""
        return list(cls.EVENTS.keys())
