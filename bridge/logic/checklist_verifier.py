"""
Smart Flight Deck Companion - Checklist Verifier
SimConnect and WASM-based checklist item verification.
"""

import logging
from typing import Optional, Any, Callable

from .checklist import (
    ChecklistItem,
    VerificationResult,
    VerificationType,
    ConditionType,
)

logger = logging.getLogger(__name__)


class ChecklistVerifier:
    """
    Verifies checklist items using SimConnect and WASM (MobiFlight).

    Connects to the simulator to read variables and validate
    checklist item conditions.
    """

    def __init__(self):
        self._simvar_reader: Optional[Callable[[str], Any]] = None
        self._lvar_reader: Optional[Callable[[str], Any]] = None

    def set_simvar_reader(self, reader: Callable[[str], Any]):
        """
        Set SimConnect variable reader function.

        Args:
            reader: Function that takes variable name and returns value
        """
        self._simvar_reader = reader

    def set_lvar_reader(self, reader: Callable[[str], Any]):
        """
        Set LVAR reader function (MobiFlight WASM).

        Args:
            reader: Function that takes LVAR name and returns value
        """
        self._lvar_reader = reader

    def verify(self, item: ChecklistItem) -> VerificationResult:
        """
        Verify a checklist item.

        Args:
            item: Checklist item to verify

        Returns:
            VerificationResult with success status and details
        """
        verification = item.verification

        # Manual verification always succeeds
        if verification.type == VerificationType.MANUAL:
            return VerificationResult(
                success=True,
                message="Manual verification - user confirmed",
            )

        # SimVar verification
        if verification.type == VerificationType.SIMVAR:
            return self._verify_simvar(item)

        # LVAR verification
        if verification.type == VerificationType.LVAR:
            return self._verify_lvar(item)

        # Combined verification
        if verification.type == VerificationType.COMBINED:
            return self._verify_combined(item)

        # Unknown type
        return VerificationResult(
            success=True,
            message=f"Unknown verification type: {verification.type}",
        )

    def _verify_simvar(self, item: ChecklistItem) -> VerificationResult:
        """Verify using SimConnect variable."""
        if not self._simvar_reader:
            logger.warning("SimVar reader not configured, assuming success")
            return VerificationResult(
                success=True,
                message="SimVar reader not available",
            )

        verification = item.verification
        variable = verification.variable

        try:
            actual_value = self._simvar_reader(variable)
            return self._check_condition(
                item, actual_value, verification.condition,
                verification.value, verification.min_value, verification.max_value
            )
        except Exception as e:
            logger.error(f"Failed to read SimVar {variable}: {e}")
            return VerificationResult(
                success=False,
                message=f"Failed to read {variable}: {e}",
            )

    def _verify_lvar(self, item: ChecklistItem) -> VerificationResult:
        """Verify using LVAR (WASM)."""
        if not self._lvar_reader:
            logger.warning("LVAR reader not configured, assuming success")
            return VerificationResult(
                success=True,
                message="LVAR reader not available",
            )

        verification = item.verification
        variable = verification.variable

        try:
            actual_value = self._lvar_reader(variable)
            return self._check_condition(
                item, actual_value, verification.condition,
                verification.value, verification.min_value, verification.max_value
            )
        except Exception as e:
            logger.error(f"Failed to read LVAR {variable}: {e}")
            return VerificationResult(
                success=False,
                message=f"Failed to read {variable}: {e}",
            )

    def _verify_combined(self, item: ChecklistItem) -> VerificationResult:
        """Verify multiple conditions (all must pass)."""
        verification = item.verification

        for i, sub_config in enumerate(verification.conditions):
            # Create a temporary item for each sub-verification
            temp_item = ChecklistItem(
                id=f"{item.id}_sub_{i}",
                challenge=item.challenge,
                challenge_tr=item.challenge_tr,
                expected_response=item.expected_response,
                expected_response_tr=item.expected_response_tr,
                verification=sub_config,
                action=item.action,
            )

            result = self.verify(temp_item)
            if not result.success:
                return result

        return VerificationResult(
            success=True,
            message="All conditions verified",
        )

    def _check_condition(
        self,
        item: ChecklistItem,
        actual_value: Any,
        condition: ConditionType,
        expected_value: Any,
        min_value: Optional[float],
        max_value: Optional[float],
    ) -> VerificationResult:
        """Check if actual value meets condition."""

        success = False
        message = ""

        try:
            if condition == ConditionType.EQUALS:
                success = self._values_equal(actual_value, expected_value)
                if not success:
                    message = f"Expected {expected_value}, got {actual_value}"

            elif condition == ConditionType.NOT_EQUALS:
                success = not self._values_equal(actual_value, expected_value)
                if not success:
                    message = f"Should not be {expected_value}"

            elif condition == ConditionType.GREATER_THAN:
                success = float(actual_value) > float(expected_value)
                if not success:
                    message = f"Should be greater than {expected_value}, got {actual_value}"

            elif condition == ConditionType.LESS_THAN:
                success = float(actual_value) < float(expected_value)
                if not success:
                    message = f"Should be less than {expected_value}, got {actual_value}"

            elif condition == ConditionType.IN_RANGE:
                val = float(actual_value)
                success = min_value <= val <= max_value
                if not success:
                    message = f"Should be between {min_value} and {max_value}, got {actual_value}"

            elif condition == ConditionType.CONTAINS:
                success = str(expected_value).lower() in str(actual_value).lower()
                if not success:
                    message = f"Should contain '{expected_value}'"

            else:
                success = True
                message = f"Unknown condition type: {condition}"

        except (ValueError, TypeError) as e:
            success = False
            message = f"Comparison error: {e}"

        return VerificationResult(
            success=success,
            actual_value=actual_value,
            expected_value=expected_value,
            message=message if not success else None,
            details={
                "condition": condition.value if hasattr(condition, "value") else str(condition),
                "variable": item.verification.variable,
            },
        )

    def _values_equal(self, actual: Any, expected: Any) -> bool:
        """Check equality with type flexibility."""
        # Direct equality
        if actual == expected:
            return True

        # Numeric comparison
        try:
            return float(actual) == float(expected)
        except (ValueError, TypeError):
            pass

        # String comparison (case-insensitive)
        try:
            return str(actual).lower() == str(expected).lower()
        except:
            pass

        # Boolean comparison
        if isinstance(expected, bool):
            if actual in [1, "1", "true", "True", "on", "On"]:
                return expected is True
            if actual in [0, "0", "false", "False", "off", "Off"]:
                return expected is False

        return False


def create_verifier_from_sim_manager(sim_manager) -> ChecklistVerifier:
    """
    Create a ChecklistVerifier connected to SimManager.

    Args:
        sim_manager: SimManager instance with SimConnect/WASM access

    Returns:
        Configured ChecklistVerifier
    """
    verifier = ChecklistVerifier()

    # Set up SimVar reader
    def read_simvar(name: str) -> Any:
        if hasattr(sim_manager, "simconnect") and sim_manager.simconnect:
            return sim_manager.simconnect.get_variable(name)
        return None

    # Set up LVAR reader
    def read_lvar(name: str) -> Any:
        if hasattr(sim_manager, "mobiflight") and sim_manager.mobiflight:
            return sim_manager.mobiflight.read_lvar(name)
        return None

    verifier.set_simvar_reader(read_simvar)
    verifier.set_lvar_reader(read_lvar)

    return verifier


# =============================================================================
# Common Variable Mappings
# =============================================================================

# SimConnect variable names for common checklist items
SIMVAR_MAPPINGS = {
    # Brakes
    "parking_brake": "BRAKE PARKING INDICATOR",

    # Gear
    "gear_handle": "GEAR HANDLE POSITION",
    "gear_center": "GEAR CENTER POSITION",
    "gear_left": "GEAR LEFT POSITION",
    "gear_right": "GEAR RIGHT POSITION",

    # Flaps
    "flaps_handle": "FLAPS HANDLE INDEX",
    "flaps_position": "FLAPS HANDLE PERCENT",

    # Spoilers
    "spoilers_armed": "SPOILERS ARMED",
    "spoilers_position": "SPOILERS HANDLE POSITION",

    # Lights
    "beacon": "LIGHT BEACON",
    "landing_lights": "LIGHT LANDING",
    "nav_lights": "LIGHT NAV",
    "strobe": "LIGHT STROBE",
    "taxi_light": "LIGHT TAXI",

    # Engines
    "engine1_running": "ENG COMBUSTION:1",
    "engine2_running": "ENG COMBUSTION:2",
    "engine1_n1": "ENG N1 RPM:1",
    "engine2_n1": "ENG N1 RPM:2",
    "engine1_n2": "ENG N2 RPM:1",
    "engine2_n2": "ENG N2 RPM:2",

    # Fuel
    "fuel_total": "FUEL TOTAL QUANTITY",
    "fuel_left": "FUEL LEFT QUANTITY",
    "fuel_right": "FUEL RIGHT QUANTITY",

    # Electrical
    "battery_master": "ELECTRICAL MASTER BATTERY",
    "avionics_master": "AVIONICS MASTER SWITCH",

    # Autopilot
    "ap_master": "AUTOPILOT MASTER",
    "ap_altitude_lock": "AUTOPILOT ALTITUDE LOCK",
    "ap_heading_lock": "AUTOPILOT HEADING LOCK",

    # Transponder
    "transponder_mode": "TRANSPONDER STATE",

    # Pitot/Static
    "pitot_heat": "PITOT HEAT",

    # Flight data
    "altitude": "PLANE ALTITUDE",
    "airspeed": "AIRSPEED INDICATED",
    "heading": "HEADING INDICATOR",
    "vertical_speed": "VERTICAL SPEED",
}


def get_simvar_name(item_id: str) -> Optional[str]:
    """Get SimConnect variable name for common item ID."""
    return SIMVAR_MAPPINGS.get(item_id)
