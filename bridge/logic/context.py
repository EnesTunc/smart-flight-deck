"""
Smart Flight Deck Companion - Flight Context Engine
Situational awareness, safety checks, and command validation.

This module integrates:
- Flight phase detection
- V-speed limits
- Safety rules evaluation
- Context-aware command validation
"""

import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field

from .flight_phase import (
    FlightPhase,
    FlightPhaseDetector,
    PhaseDetectionState,
    is_command_allowed_in_phase,
)
from .v_speeds import SpeedLimits, SpeedLimitProvider
from .safety_rules import (
    SafetyRulesEngine,
    SafetyContext,
    SafetyEvaluation,
    SafetyAction,
    get_response_text,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Legacy Compatibility
# =============================================================================

@dataclass
class SafetyCheckResult:
    """
    Result of a safety check.

    Legacy compatibility class - maps to SafetyEvaluation internally.
    """

    allowed: bool
    reason: Optional[str] = None
    warning: Optional[str] = None
    action: SafetyAction = SafetyAction.ALLOW
    details: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_evaluation(cls, evaluation: SafetyEvaluation) -> "SafetyCheckResult":
        """Create from SafetyEvaluation."""
        return cls(
            allowed=evaluation.action.should_execute,
            reason=evaluation.message if evaluation.action == SafetyAction.BLOCK else None,
            warning=evaluation.message if evaluation.action in [SafetyAction.WARN, SafetyAction.REMIND] else None,
            action=evaluation.action,
            details=evaluation.details,
        )


# =============================================================================
# Context Engine
# =============================================================================

@dataclass
class AircraftStateSnapshot:
    """Complete aircraft state snapshot for context evaluation."""

    # Position
    on_ground: bool = True
    altitude_msl: float = 0.0
    altitude_agl: float = 0.0

    # Speed
    indicated_airspeed: float = 0.0
    ground_speed: float = 0.0
    vertical_speed: float = 0.0

    # Configuration
    gear_handle_position: int = 1
    flaps_handle_index: int = 0
    spoilers_armed: bool = False
    parking_brake: bool = True

    # Engines
    engine1_running: bool = False
    engine2_running: bool = False
    engine1_n2: float = 0.0
    engine2_n2: float = 0.0
    throttle_percent: float = 0.0

    # Aircraft info
    aircraft_title: str = ""

    def to_phase_state(self) -> PhaseDetectionState:
        """Convert to PhaseDetectionState."""
        return PhaseDetectionState(
            on_ground=self.on_ground,
            altitude_msl=self.altitude_msl,
            altitude_agl=self.altitude_agl,
            indicated_airspeed=self.indicated_airspeed,
            ground_speed=self.ground_speed,
            vertical_speed=self.vertical_speed,
            gear_handle_position=self.gear_handle_position,
            flaps_handle_index=self.flaps_handle_index,
            spoilers_armed=self.spoilers_armed,
            parking_brake=self.parking_brake,
            engine1_running=self.engine1_running,
            engine2_running=self.engine2_running,
            engine1_n2=self.engine1_n2,
            engine2_n2=self.engine2_n2,
            throttle_percent=self.throttle_percent,
        )


class ContextEngine:
    """
    Main context engine for flight awareness and safety.

    Integrates flight phase detection, speed limits, and safety rules
    to provide intelligent command validation.
    """

    def __init__(self):
        # Components
        self._phase_detector = FlightPhaseDetector()
        self._speed_provider = SpeedLimitProvider()
        self._safety_engine = SafetyRulesEngine()

        # State
        self._current_state: Optional[AircraftStateSnapshot] = None
        self._current_limits: Optional[SpeedLimits] = None
        self._aircraft_title: str = ""

        # Callbacks
        self._on_phase_change: Optional[Callable[[FlightPhase, FlightPhase], None]] = None
        self._on_safety_warning: Optional[Callable[[SafetyEvaluation], None]] = None

        # Set up phase change callback
        self._phase_detector.on_phase_change(self._handle_phase_change)

    def update(self, state: AircraftStateSnapshot):
        """
        Update context with current aircraft state.

        Args:
            state: Current aircraft state
        """
        self._current_state = state

        # Update aircraft limits if aircraft changed
        if state.aircraft_title != self._aircraft_title:
            self._aircraft_title = state.aircraft_title
            self._current_limits = self._speed_provider.get_limits(state.aircraft_title)
            logger.info(f"Loaded limits for: {state.aircraft_title}")

        # Update flight phase
        phase_state = state.to_phase_state()
        self._phase_detector.detect(phase_state)

    def update_from_simconnect(
        self,
        altitude: float,
        altitude_agl: float,
        speed: float,
        ground_speed: float,
        vertical_speed: float,
        on_ground: bool,
        gear_down: bool,
        flaps_index: int = 0,
        engine1_running: bool = False,
        engine2_running: bool = False,
        parking_brake: bool = False,
        aircraft_title: str = "",
    ):
        """
        Update context from SimConnect data.

        Convenience method for direct SimConnect integration.
        """
        state = AircraftStateSnapshot(
            on_ground=on_ground,
            altitude_msl=altitude,
            altitude_agl=altitude_agl if altitude_agl > 0 else altitude,
            indicated_airspeed=speed,
            ground_speed=ground_speed,
            vertical_speed=vertical_speed,
            gear_handle_position=1 if gear_down else 0,
            flaps_handle_index=flaps_index,
            parking_brake=parking_brake,
            engine1_running=engine1_running,
            engine2_running=engine2_running,
            aircraft_title=aircraft_title,
        )
        self.update(state)

    def evaluate_command(
        self,
        command_id: str,
        value: Any = None,
        override: bool = False,
    ) -> SafetyCheckResult:
        """
        Evaluate if a command is safe to execute.

        Args:
            command_id: Command identifier (e.g., "gear_down", "flaps_set")
            value: Optional command value
            override: Whether user requested override

        Returns:
            SafetyCheckResult with action and messages
        """
        if self._current_state is None:
            return SafetyCheckResult(
                allowed=True,
                warning="No aircraft state available - proceeding without safety checks",
            )

        if self._current_limits is None:
            self._current_limits = self._speed_provider.get_limits(self._aircraft_title)

        # Build safety context
        context = SafetyContext(
            state=self._current_state.to_phase_state(),
            flight_phase=self._phase_detector.current_phase,
            limits=self._current_limits,
            command_id=command_id,
            command_value=value,
            override_requested=override,
        )

        # Evaluate safety rules
        evaluation = self._safety_engine.evaluate(context)

        # Trigger warning callback if needed
        if evaluation.action in [SafetyAction.WARN, SafetyAction.BLOCK]:
            if self._on_safety_warning:
                self._on_safety_warning(evaluation)

        return SafetyCheckResult.from_evaluation(evaluation)

    def _handle_phase_change(self, old_phase: FlightPhase, new_phase: FlightPhase):
        """Handle flight phase change."""
        logger.info(f"Flight phase changed: {old_phase.display_name} → {new_phase.display_name}")

        if self._on_phase_change:
            self._on_phase_change(old_phase, new_phase)

    # =========================================================================
    # Legacy API (Backward Compatibility)
    # =========================================================================

    def check_gear_extend(self) -> SafetyCheckResult:
        """Check if gear extension is safe. (Legacy API)"""
        return self.evaluate_command("gear_down")

    def check_gear_retract(self) -> SafetyCheckResult:
        """Check if gear retraction is safe."""
        return self.evaluate_command("gear_up")

    def check_flaps_extend(self, position: int) -> SafetyCheckResult:
        """Check if flaps extension is safe. (Legacy API)"""
        return self.evaluate_command("flaps_set", value=position)

    def check_takeoff_config(self) -> SafetyCheckResult:
        """Check takeoff configuration. (Legacy API)"""
        return self.evaluate_command("takeoff_config_check")

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def phase(self) -> FlightPhase:
        """Current flight phase."""
        return self._phase_detector.current_phase

    @property
    def previous_phase(self) -> FlightPhase:
        """Previous flight phase."""
        return self._phase_detector.previous_phase

    @property
    def is_on_ground(self) -> bool:
        """Whether aircraft is on ground."""
        return self._current_state.on_ground if self._current_state else True

    @property
    def current_speed(self) -> float:
        """Current indicated airspeed."""
        return self._current_state.indicated_airspeed if self._current_state else 0.0

    @property
    def current_altitude(self) -> float:
        """Current altitude MSL."""
        return self._current_state.altitude_msl if self._current_state else 0.0

    @property
    def current_altitude_agl(self) -> float:
        """Current altitude AGL."""
        return self._current_state.altitude_agl if self._current_state else 0.0

    @property
    def is_critical_phase(self) -> bool:
        """Whether in critical phase of flight."""
        return self._phase_detector.is_critical_phase

    @property
    def speed_limits(self) -> Optional[SpeedLimits]:
        """Current aircraft speed limits."""
        return self._current_limits

    @property
    def aircraft_title(self) -> str:
        """Current aircraft title."""
        return self._aircraft_title

    # =========================================================================
    # Callbacks
    # =========================================================================

    def on_phase_change(self, callback: Callable[[FlightPhase, FlightPhase], None]):
        """Register callback for phase changes."""
        self._on_phase_change = callback

    def on_safety_warning(self, callback: Callable[[SafetyEvaluation], None]):
        """Register callback for safety warnings."""
        self._on_safety_warning = callback

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_status_summary(self) -> Dict[str, Any]:
        """Get current context status summary."""
        return {
            "phase": self.phase.display_name,
            "on_ground": self.is_on_ground,
            "speed": round(self.current_speed),
            "altitude": round(self.current_altitude),
            "altitude_agl": round(self.current_altitude_agl),
            "is_critical": self.is_critical_phase,
            "aircraft": self.aircraft_title,
            "limits": self._current_limits.to_dict() if self._current_limits else None,
        }

    def get_phase_info(self) -> Dict[str, Any]:
        """Get detailed phase information."""
        return {
            "current": self.phase.display_name,
            "previous": self.previous_phase.display_name,
            "is_ground": self.phase.is_ground_phase,
            "is_critical": self.phase.is_critical_phase,
            "duration": round(self._phase_detector.phase_duration, 1),
        }

    def reset(self):
        """Reset context to initial state."""
        self._phase_detector.reset()
        self._current_state = None
        self._aircraft_title = ""
        self._current_limits = None


# =============================================================================
# Legacy FlightContext Class (Backward Compatibility)
# =============================================================================

class FlightContext(ContextEngine):
    """
    Legacy FlightContext class.

    Maintained for backward compatibility. Use ContextEngine for new code.
    """

    # Legacy thresholds (now handled by SpeedLimits)
    MAX_GEAR_EXTEND_SPEED = 250
    MAX_FLAPS_SPEED = {
        1: 250,
        2: 200,
        3: 180,
        4: 160,
    }

    def __init__(self):
        super().__init__()
        self._last_altitude = 0.0
        self._last_speed = 0.0
        self._on_ground = True

    def update(
        self,
        altitude: float = None,
        speed: float = None,
        vertical_speed: float = None,
        on_ground: bool = None,
        gear_down: bool = None,
        **kwargs
    ):
        """
        Update flight context with current data. (Legacy API)

        Accepts both old positional style and new keyword style.
        """
        # Handle legacy positional arguments
        if isinstance(altitude, AircraftStateSnapshot):
            # New style call
            super().update(altitude)
            return

        # Legacy style call
        if altitude is not None:
            self._last_altitude = altitude
        if speed is not None:
            self._last_speed = speed
        if on_ground is not None:
            self._on_ground = on_ground

        # Create state snapshot for new engine
        state = AircraftStateSnapshot(
            on_ground=self._on_ground,
            altitude_msl=self._last_altitude,
            altitude_agl=self._last_altitude,  # Legacy doesn't distinguish
            indicated_airspeed=self._last_speed,
            ground_speed=self._last_speed if self._on_ground else 0,
            vertical_speed=vertical_speed or 0,
            gear_handle_position=1 if gear_down else 0,
        )

        super().update(state)

    @property
    def _phase(self) -> FlightPhase:
        """Legacy phase property."""
        return self.phase

    @_phase.setter
    def _phase(self, value: FlightPhase):
        """Legacy phase setter (no-op, phase is auto-detected)."""
        pass
