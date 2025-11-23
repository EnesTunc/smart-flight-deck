"""
Smart Flight Deck Companion - Command Parser
Natural language to command conversion.
"""

import re
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedCommand:
    """Result of parsing a voice command."""

    intent: str  # Command intent (e.g., "gear_down")
    confidence: float  # Match confidence 0-1
    parameters: dict  # Extracted parameters
    raw_text: str  # Original text
    matched_pattern: Optional[str] = None


class CommandParser:
    """
    Parse natural language commands into structured intents.

    Uses pattern matching with fuzzy matching support.
    """

    # Command patterns: (pattern, intent, parameter_extractors)
    PATTERNS: List[Tuple[str, str, dict]] = [
        # Gear commands
        (r"gear (down|extend)", "gear_down", {}),
        (r"gear (up|retract)", "gear_up", {}),
        (r"(lower|drop) (the )?gear", "gear_down", {}),
        (r"(raise|retract) (the )?gear", "gear_up", {}),
        # Flaps commands
        (r"flaps? (up|zero|0)", "flaps_up", {"position": 0}),
        (r"flaps? (down|extend)", "flaps_down", {}),
        (r"flaps? (\d+)", "flaps_set", {"position": "group1"}),
        (r"flaps? (one|1)", "flaps_set", {"position": 1}),
        (r"flaps? (two|2|ten|10)", "flaps_set", {"position": 2}),
        (r"flaps? (three|3|fifteen|15)", "flaps_set", {"position": 3}),
        (r"flaps? (four|4|full|twenty|20|25)", "flaps_set", {"position": 4}),
        # Lights
        (r"(landing )?lights? (on|off)", "landing_lights_toggle", {}),
        (r"(turn )?(on|off) (the )?(landing )?lights?", "landing_lights_toggle", {}),
        (r"strobes? (on|off)", "strobe_lights_toggle", {}),
        (r"beacon (on|off)", "beacon_lights_toggle", {}),
        (r"nav(igation)? lights? (on|off)", "nav_lights_toggle", {}),
        # Parking brake
        (r"parking brake", "parking_brake_toggle", {}),
        (r"(set|release) (parking )?brake", "parking_brake_toggle", {}),
        # Spoilers
        (r"spoilers? arm(ed)?", "spoilers_arm", {}),
        (r"arm (the )?spoilers?", "spoilers_arm", {}),
        (r"spoilers? (on|extend|deploy)", "spoilers_on", {}),
        (r"spoilers? (off|retract)", "spoilers_off", {}),
        # Autopilot
        (r"autopilot (on|off|engage|disengage)", "ap_master", {}),
        (r"(engage|disengage) autopilot", "ap_master", {}),
        (r"heading (hold|mode)", "ap_heading_hold", {}),
        (r"altitude (hold|mode)", "ap_altitude_hold", {}),
        (r"nav (hold|mode)", "ap_nav_hold", {}),
        (r"approach (mode)?", "ap_approach", {}),
        # Status queries
        (r"(what('?s| is) (the |my |our )?)?(current )?speed", "query_speed", {}),
        (r"(what('?s| is) (the |my |our )?)?(current )?altitude", "query_altitude", {}),
        (r"(what('?s| is) (the |my |our )?)?(current )?heading", "query_heading", {}),
        (r"(how much )?fuel (remaining|left)?", "query_fuel", {}),
    ]

    def __init__(self):
        # Compile patterns for efficiency
        self._compiled = [
            (re.compile(pattern, re.IGNORECASE), intent, params)
            for pattern, intent, params in self.PATTERNS
        ]

    def parse(self, text: str) -> Optional[ParsedCommand]:
        """
        Parse text into a command.

        Args:
            text: Raw text from speech recognition

        Returns:
            ParsedCommand if matched, None otherwise
        """
        text = text.strip().lower()

        if not text:
            return None

        for pattern, intent, param_template in self._compiled:
            match = pattern.search(text)

            if match:
                # Extract parameters
                parameters = {}
                for key, value in param_template.items():
                    if isinstance(value, str) and value.startswith("group"):
                        group_num = int(value.replace("group", ""))
                        try:
                            parameters[key] = match.group(group_num)
                        except IndexError:
                            parameters[key] = None
                    else:
                        parameters[key] = value

                logger.debug(f"Matched: '{text}' -> {intent} (params: {parameters})")

                return ParsedCommand(
                    intent=intent,
                    confidence=0.9,  # Pattern match = high confidence
                    parameters=parameters,
                    raw_text=text,
                    matched_pattern=pattern.pattern,
                )

        logger.debug(f"No match for: '{text}'")
        return None

    def get_suggestions(self, partial_text: str) -> List[str]:
        """
        Get command suggestions based on partial input.

        Args:
            partial_text: Partial command text

        Returns:
            List of suggested commands
        """
        suggestions = [
            "gear down",
            "gear up",
            "flaps 1",
            "flaps 2",
            "flaps full",
            "landing lights on",
            "parking brake",
            "spoilers arm",
        ]

        partial_lower = partial_text.lower()
        return [s for s in suggestions if partial_lower in s or s.startswith(partial_lower)]
