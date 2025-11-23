"""
Smart Flight Deck Companion - Aircraft Detector
Automatically detects current aircraft and loads appropriate profile.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AircraftProfile:
    """Loaded aircraft profile data."""

    name: str
    file_path: Path
    data: Dict[str, Any]
    has_lvar_support: bool = False
    has_fcu_control: bool = False
    has_mcp_control: bool = False

    @property
    def features(self) -> Dict[str, bool]:
        """Get feature flags from profile."""
        return self.data.get("features", {})

    @property
    def commands(self) -> Dict[str, Any]:
        """Get command definitions."""
        return self.data.get("commands", {})

    @property
    def variables(self) -> Dict[str, Any]:
        """Get variable definitions."""
        return self.data.get("variables", {})

    @property
    def responses(self) -> Dict[str, str]:
        """Get response templates."""
        return self.data.get("responses", {})


class ProfileLoader:
    """
    Loads and manages aircraft profiles.
    """

    def __init__(self, profiles_dir: Optional[Path] = None):
        """
        Initialize profile loader.

        Args:
            profiles_dir: Directory containing profile JSON files
        """
        if profiles_dir is None:
            # Default to aircraft_profiles folder in same directory
            profiles_dir = Path(__file__).parent / "aircraft_profiles"

        self._profiles_dir = profiles_dir
        self._profiles: Dict[str, AircraftProfile] = {}
        self._default_profile: Optional[AircraftProfile] = None

        self._load_all_profiles()

    def _load_all_profiles(self):
        """Load all profile JSON files from profiles directory."""
        if not self._profiles_dir.exists():
            logger.warning(f"Profiles directory not found: {self._profiles_dir}")
            return

        for json_file in self._profiles_dir.glob("*.json"):
            try:
                profile = self._load_profile(json_file)
                if profile:
                    profile_id = json_file.stem  # filename without extension

                    # Check if this is the default/fallback profile
                    detection = profile.data.get("detection", {})
                    if detection.get("fallback", False):
                        self._default_profile = profile
                        logger.info(f"Default profile loaded: {profile.name}")
                    else:
                        self._profiles[profile_id] = profile
                        logger.info(f"Profile loaded: {profile.name} ({profile_id})")

            except Exception as e:
                logger.error(f"Error loading profile {json_file}: {e}")

        logger.info(f"Loaded {len(self._profiles)} aircraft profiles")

    def _load_profile(self, file_path: Path) -> Optional[AircraftProfile]:
        """
        Load a single profile from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            AircraftProfile or None
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            features = data.get("features", {})

            return AircraftProfile(
                name=data.get("name", file_path.stem),
                file_path=file_path,
                data=data,
                has_lvar_support=features.get("lvar_support", False),
                has_fcu_control=features.get("fcu_control", False),
                has_mcp_control=features.get("mcp_control", False),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            return None

    def get_profile(self, profile_id: str) -> Optional[AircraftProfile]:
        """Get profile by ID."""
        return self._profiles.get(profile_id)

    def get_default_profile(self) -> Optional[AircraftProfile]:
        """Get the default/fallback profile."""
        return self._default_profile

    def list_profiles(self) -> List[str]:
        """List all available profile IDs."""
        return list(self._profiles.keys())

    def reload_profiles(self):
        """Reload all profiles from disk."""
        self._profiles.clear()
        self._default_profile = None
        self._load_all_profiles()


class AircraftDetector:
    """
    Detects current aircraft and selects appropriate profile.

    Uses aircraft title from SimConnect to match against profile detection rules.
    """

    def __init__(self, profile_loader: Optional[ProfileLoader] = None):
        """
        Initialize aircraft detector.

        Args:
            profile_loader: ProfileLoader instance
        """
        self._loader = profile_loader or ProfileLoader()
        self._current_profile: Optional[AircraftProfile] = None
        self._current_aircraft_title: str = ""

    def detect(self, aircraft_title: str) -> AircraftProfile:
        """
        Detect aircraft and return matching profile.

        Args:
            aircraft_title: Aircraft title from SimConnect

        Returns:
            Matching AircraftProfile (or default if no match)
        """
        # Normalize title for comparison
        title_lower = aircraft_title.lower()
        self._current_aircraft_title = aircraft_title

        # Try to match against profiles
        for profile_id, profile in self._loader._profiles.items():
            if self._matches_profile(title_lower, profile):
                logger.info(f"Aircraft '{aircraft_title}' matched profile: {profile.name}")
                self._current_profile = profile
                return profile

        # No match - use default profile
        default = self._loader.get_default_profile()
        if default:
            logger.info(f"Aircraft '{aircraft_title}' using default profile")
            self._current_profile = default
            return default

        # Create empty profile as last resort
        logger.warning(f"No profile found for aircraft: {aircraft_title}")
        self._current_profile = AircraftProfile(
            name="Unknown",
            file_path=Path("unknown"),
            data={},
        )
        return self._current_profile

    def _matches_profile(self, title_lower: str, profile: AircraftProfile) -> bool:
        """
        Check if aircraft title matches a profile's detection rules.

        Args:
            title_lower: Lowercase aircraft title
            profile: Profile to check

        Returns:
            True if matches
        """
        detection = profile.data.get("detection", {})

        # Check title_contains rules
        title_rules = detection.get("title_contains", [])
        if title_rules:
            for rule in title_rules:
                if rule.lower() in title_lower:
                    return True

        # Check livery_contains rules
        livery_rules = detection.get("livery_contains", [])
        if livery_rules:
            for rule in livery_rules:
                if rule.lower() in title_lower:
                    return True

        return False

    @property
    def current_profile(self) -> Optional[AircraftProfile]:
        """Get currently active profile."""
        return self._current_profile

    @property
    def current_aircraft(self) -> str:
        """Get current aircraft title."""
        return self._current_aircraft_title

    def get_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        """
        Get command definition from current profile.

        Args:
            command_id: Command identifier

        Returns:
            Command definition dict or None
        """
        if not self._current_profile:
            return None
        return self._current_profile.commands.get(command_id)

    def get_variable(self, var_id: str) -> Optional[Dict[str, Any]]:
        """
        Get variable definition from current profile.

        Args:
            var_id: Variable identifier

        Returns:
            Variable definition dict or None
        """
        if not self._current_profile:
            return None
        return self._current_profile.variables.get(var_id)

    def get_response_template(self, command_id: str) -> Optional[str]:
        """
        Get response template for a command.

        Args:
            command_id: Command identifier

        Returns:
            Response template string or None
        """
        if not self._current_profile:
            return None
        return self._current_profile.responses.get(command_id)

    def supports_feature(self, feature: str) -> bool:
        """
        Check if current profile supports a feature.

        Args:
            feature: Feature name (e.g., 'lvar_support', 'fcu_control')

        Returns:
            True if feature is supported
        """
        if not self._current_profile:
            return False
        return self._current_profile.features.get(feature, False)


class CommandResolver:
    """
    Resolves voice commands to aircraft-specific actions.

    Uses aircraft profile to determine correct command implementation.
    """

    def __init__(self, detector: AircraftDetector):
        """
        Initialize command resolver.

        Args:
            detector: AircraftDetector instance
        """
        self._detector = detector

    def resolve(self, command_id: str, value: Any = None) -> Optional[Dict[str, Any]]:
        """
        Resolve a command to its implementation.

        Args:
            command_id: Generic command identifier (e.g., 'fcu_heading_set')
            value: Optional value for the command

        Returns:
            Dict with command implementation details:
            {
                'type': 'simconnect' | 'lvar' | 'hevent' | 'calculator',
                'action': specific action data,
                'value': resolved value
            }
        """
        command_def = self._detector.get_command(command_id)

        if not command_def:
            logger.warning(f"Command not found in profile: {command_id}")
            return None

        cmd_type = command_def.get("type")

        if cmd_type == "simconnect":
            return self._resolve_simconnect(command_def, value)
        elif cmd_type == "lvar":
            return self._resolve_lvar(command_def, value)
        elif cmd_type == "hevent":
            return self._resolve_hevent(command_def)
        elif cmd_type == "calculator":
            return self._resolve_calculator(command_def, value)
        else:
            logger.warning(f"Unknown command type: {cmd_type}")
            return None

    def _resolve_simconnect(
        self, command_def: Dict[str, Any], value: Any
    ) -> Dict[str, Any]:
        """Resolve SimConnect event command."""
        event_name = command_def.get("event")
        requires_value = command_def.get("value_required", False)

        # Map value if value_map is provided
        if value is not None and "value_map" in command_def:
            value_map = command_def["value_map"]
            value = value_map.get(str(value), value)

        return {
            "type": "simconnect",
            "event": event_name,
            "value": value if requires_value else 0,
        }

    def _resolve_lvar(self, command_def: Dict[str, Any], value: Any) -> Dict[str, Any]:
        """Resolve LVAR command."""
        lvar_name = command_def.get("lvar")
        action = command_def.get("action", "set")

        # Handle value mapping
        if value is not None and "value_map" in command_def:
            value_map = command_def["value_map"]
            value = value_map.get(str(value), value)
        elif value is None:
            # Use default value from definition
            value = command_def.get("value")

        return {
            "type": "lvar",
            "lvar": lvar_name,
            "action": action,
            "value": value,
        }

    def _resolve_hevent(self, command_def: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve H:Event command."""
        event_name = command_def.get("event")

        return {
            "type": "hevent",
            "event": event_name,
        }

    def _resolve_calculator(
        self, command_def: Dict[str, Any], value: Any
    ) -> Dict[str, Any]:
        """Resolve calculator code command."""
        code = command_def.get("code", "")

        # Replace placeholders in code
        if value is not None:
            code = code.replace("{value}", str(value))

        return {
            "type": "calculator",
            "code": code,
        }

    def get_available_commands(self) -> List[str]:
        """Get list of available commands for current aircraft."""
        profile = self._detector.current_profile
        if not profile:
            return []
        return list(profile.commands.keys())

    def get_command_description(self, command_id: str) -> Optional[str]:
        """Get description for a command."""
        command_def = self._detector.get_command(command_id)
        if command_def:
            return command_def.get("description")
        return None
