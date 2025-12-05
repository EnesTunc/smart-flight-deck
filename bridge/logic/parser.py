"""
Smart Flight Deck Companion - Command Parser
Natural language to command conversion.
"""

import re
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass
from difflib import SequenceMatcher

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
        (r"(lower|drop) (the )?(landing )?gear", "gear_down", {}),  # "lower the landing gear"
        (r"(raise|retract) (the )?gear", "gear_up", {}),
        # Flaps commands
        (r"flaps? (up|zero|0)", "flaps_up", {"position": 0}),
        (r"flaps? (down|extend)", "flaps_down", {}),
        (r"set flaps? to position (\d+)", "flaps_set", {"position": "group1"}),  # "set flaps to position 1"
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
        (r"taxi lights? (on|off)", "taxi_lights_toggle", {}),
        # Parking brake
        (r"parking brake", "parking_brake_toggle", {}),
        (r"(set|release) (parking )?brake", "parking_brake_toggle", {}),
        # Spoilers / Speedbrake
        (r"spoilers? arm(ed)?", "spoilers_arm", {}),
        (r"arm (the )?spoilers?", "spoilers_arm", {}),
        (r"spoilers? (on|extend|deploy)", "spoilers_on", {}),
        (r"spoilers? (off|retract)", "spoilers_off", {}),
        (r"speed ?brake (on|extend|deploy)", "spoilers_on", {}),
        (r"speed ?brake (off|retract)", "spoilers_off", {}),
        # Autobrake
        (r"auto ?brake (off|disarm)", "autobrake_off", {}),
        (r"auto ?brake (low|lo|1|one)", "autobrake_lo", {}),
        (r"auto ?brake (med|medium|2|two)", "autobrake_med", {}),
        (r"auto ?brake (high|hi|3|three)", "autobrake_hi", {}),
        (r"auto ?brake (max|maximum|4|four)", "autobrake_max", {}),
        (r"auto ?brake (rto|rejected)", "autobrake_rto", {}),
        # Trim
        (r"trim (nose )?up", "elevator_trim_up", {}),
        (r"trim (nose )?down", "elevator_trim_down", {}),
        (r"(aileron |roll )?trim left", "aileron_trim_left", {}),
        (r"(aileron |roll )?trim right", "aileron_trim_right", {}),
        (r"rudder trim left", "rudder_trim_left", {}),
        (r"rudder trim right", "rudder_trim_right", {}),
        # APU
        (r"apu (start|on)", "apu_start", {}),
        (r"(start|turn on) (the )?apu", "apu_start", {}),
        (r"apu (stop|off|shutdown)", "apu_off", {}),
        (r"(stop|turn off|shutdown) (the )?apu", "apu_off", {}),
        # Engines
        (r"(start|ignite) engine(s)?( all)?", "engines_start", {}),
        (r"engine(s)? start", "engines_start", {}),
        (r"(shutdown|stop|cut) engine(s)?( all)?", "engines_off", {}),
        (r"engine(s)? (off|shutdown|stop|cut)", "engines_off", {}),
        (r"(start|ignite) engine (one|1|left)", "engine1_start", {}),
        (r"(start|ignite) engine (two|2|right)", "engine2_start", {}),
        # Transponder
        (r"transponder (standby|stby)", "xpndr_standby", {}),
        (r"(squawk |transponder )?(ident|id)", "xpndr_ident", {}),
        (r"transponder (on|alt|altitude)", "xpndr_on", {}),
        (r"squawk (\\d{4})", "xpndr_set", {"code": "group1"}),
        # Autopilot
        (r"autopilot (on|off|engage|disengage)", "ap_master", {}),
        (r"(engage|disengage) autopilot", "ap_master", {}),
        (r"heading (hold|mode)", "ap_heading_hold", {}),
        (r"altitude (hold|mode)", "ap_altitude_hold", {}),
        (r"nav (hold|mode)", "ap_nav_hold", {}),
        (r"approach (mode)?", "ap_approach", {}),
        (r"vertical speed (mode)?", "ap_vs_hold", {}),
        (r"v s (mode)?", "ap_vs_hold", {}),
        (r"flight level change", "ap_flc", {}),
        (r"speed (hold|mode)", "ap_speed_hold", {}),
        # Radio/Comms
        (r"(swap|flip|switch) com( ?(one|1))?", "com1_swap", {}),
        (r"(swap|flip|switch) com ?(two|2)", "com2_swap", {}),
        (r"(swap|flip|switch) nav( ?(one|1))?", "nav1_swap", {}),
        (r"(swap|flip|switch) nav ?(two|2)", "nav2_swap", {}),
        # Cabin/Doors
        (r"(open|close) (main |passenger )?door", "toggle_door", {}),
        (r"(exit|door) (one|1|left)", "toggle_door1", {}),
        (r"(exit|door) (two|2|right)", "toggle_door2", {}),
        (r"(fasten )?seat ?belt(s)? (sign )?(on|off)", "seatbelt_sign", {}),
        (r"no smoking (sign )?(on|off)", "no_smoking_sign", {}),
        # Status queries
        (r"(what('?s| is) (the |my |our )?)?(current )?speed", "query_speed", {}),
        (r"(what('?s| is) (the |my |our )?)?(current )?altitude", "query_altitude", {}),
        (r"(what('?s| is) (the |my |our )?)?(current )?heading", "query_heading", {}),
        (r"(how much )?fuel (remaining|left)?", "query_fuel", {}),
        # Checklist commands
        (r"(start |run |begin )?(before start|before engine) checklist", "checklist_start", {"checklist": "before_start"}),
        (r"(start |run |begin )?(after start) checklist", "checklist_start", {"checklist": "after_start"}),
        (r"(start |run |begin )?(before taxi) checklist", "checklist_start", {"checklist": "before_taxi"}),
        (r"(start |run |begin )?(before takeoff|takeoff) checklist", "checklist_start", {"checklist": "before_takeoff"}),
        (r"(start |run |begin )?(after takeoff) checklist", "checklist_start", {"checklist": "after_takeoff"}),
        (r"(start |run |begin )?(approach) checklist", "checklist_start", {"checklist": "approach"}),
        (r"(start |run |begin )?(before landing|landing) checklist", "checklist_start", {"checklist": "before_landing"}),
        (r"(start |run |begin )?(after landing) checklist", "checklist_start", {"checklist": "after_landing"}),
        (r"(start |run |begin )?(shutdown) checklist", "checklist_start", {"checklist": "shutdown"}),
        (r"(start |run |begin )?(cockpit prep(aration)?) checklist", "checklist_start", {"checklist": "cockpit_preparation"}),
        (r"^checklist$", "checklist_start", {}),  # "checklist" tek kelime - genel checklist
        (r"(start |run |begin )?checklist (.+)", "checklist_start", {"checklist": "group2"}),
        # Checklist responses
        (r"^check(ed)?$", "checklist_check", {}),
        (r"^set$", "checklist_check", {}),
        (r"^confirm(ed)?$", "checklist_check", {}),
        (r"^skip$", "checklist_skip", {}),
        (r"^next( item)?$", "checklist_skip", {}),
        (r"^repeat$", "checklist_repeat", {}),
        (r"^(say )?again$", "checklist_repeat", {}),
        (r"^override$", "checklist_override", {}),
        # Checklist control
        (r"(pause|hold) checklist", "checklist_pause", {}),
        (r"(resume|continue) checklist", "checklist_resume", {}),
        (r"(cancel|stop|abort) checklist", "checklist_cancel", {}),
        (r"(what('?s| is) (the )?)?(current |next )?item", "checklist_status", {}),
        (r"checklist status", "checklist_status", {}),
        (r"list checklists?", "checklist_list", {}),
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

        # No exact match - try fuzzy matching for common misrecognitions
        fuzzy_result = self._fuzzy_match(text)
        if fuzzy_result:
            logger.info(f"Fuzzy match: '{text}' -> '{fuzzy_result.intent}' (confidence: {fuzzy_result.confidence:.2f})")
            return fuzzy_result

        logger.debug(f"No match for: '{text}'")
        return None

    def _fuzzy_match(self, text: str) -> Optional[ParsedCommand]:
        """
        Attempt fuzzy matching for common STT misrecognitions.

        Common errors:
        - "parking bridge" → "parking brake"
        - "girda" → "gear down"
        - "fleps" → "flaps"
        """
        # Common word substitutions for aviation terms
        corrections = {
            "bridge": "brake",
            "break": "brake",
            "breck": "brake",
            "girda": "gear down",
            "geardown": "gear down",
            "girup": "gear up",
            "gearup": "gear up",
            "fleps": "flaps",
            "flex": "flaps",
            "spoliers": "spoilers",
            "spoiller": "spoilers",
        }

        corrected_text = text
        for wrong, correct in corrections.items():
            if wrong in text:
                corrected_text = text.replace(wrong, correct)
                logger.debug(f"Fuzzy correction: '{text}' -> '{corrected_text}'")
                break

        # Try matching with corrected text
        if corrected_text != text:
            for pattern, intent, param_template in self._compiled:
                match = pattern.search(corrected_text)
                if match:
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

                    return ParsedCommand(
                        intent=intent,
                        confidence=0.7,  # Lower confidence for fuzzy match
                        parameters=parameters,
                        raw_text=text,
                        matched_pattern=f"fuzzy:{pattern.pattern}",
                    )

        # Try similarity matching with known commands
        known_commands = [
            ("gear down", "gear_down"),
            ("gear up", "gear_up"),
            ("parking brake", "parking_brake_toggle"),
            ("flaps", "flaps_down"),
            ("spoilers", "spoilers_on"),
        ]

        best_match = None
        best_ratio = 0.6  # Minimum similarity threshold

        for command_text, intent in known_commands:
            ratio = SequenceMatcher(None, text, command_text).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = intent

        if best_match:
            logger.debug(f"Similarity match: '{text}' -> '{best_match}' (ratio: {best_ratio:.2f})")
            return ParsedCommand(
                intent=best_match,
                confidence=best_ratio * 0.8,  # Scale down confidence
                parameters={},
                raw_text=text,
                matched_pattern="similarity",
            )

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
            # Basic controls
            "gear down",
            "gear up",
            "flaps 1",
            "flaps 2",
            "flaps full",
            "landing lights on",
            "parking brake",
            "spoilers arm",
            # Checklists
            "before start checklist",
            "before takeoff checklist",
            "after takeoff checklist",
            "approach checklist",
            "before landing checklist",
            "after landing checklist",
            "shutdown checklist",
            "check",
            "skip",
            "pause checklist",
            "cancel checklist",
        ]

        partial_lower = partial_text.lower()
        return [s for s in suggestions if partial_lower in s or s.startswith(partial_lower)]
