"""
Smart Flight Deck Companion - Flight Phase Detection
Automatically detects current flight phase based on aircraft state.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, Callable
import logging
import time

logger = logging.getLogger(__name__)


class FlightPhase(Enum):
    """Flight phases throughout a flight."""

    UNKNOWN = auto()
    PREFLIGHT = auto()      # On ground, engines off, parking brake set
    ENGINE_START = auto()   # Starting engines
    TAXI = auto()           # On ground, moving slowly
    TAKEOFF = auto()        # Takeoff roll and initial climb
    CLIMB = auto()          # Climbing to cruise altitude
    CRUISE = auto()         # Level flight at altitude
    DESCENT = auto()        # Descending from cruise
    APPROACH = auto()       # Final approach, configured for landing
    LANDING = auto()        # Touchdown and rollout
    GO_AROUND = auto()      # Missed approach, climbing away
    SHUTDOWN = auto()       # Engines shutting down

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        names = {
            FlightPhase.UNKNOWN: "Unknown",
            FlightPhase.PREFLIGHT: "Preflight",
            FlightPhase.ENGINE_START: "Engine Start",
            FlightPhase.TAXI: "Taxi",
            FlightPhase.TAKEOFF: "Takeoff",
            FlightPhase.CLIMB: "Climb",
            FlightPhase.CRUISE: "Cruise",
            FlightPhase.DESCENT: "Descent",
            FlightPhase.APPROACH: "Approach",
            FlightPhase.LANDING: "Landing",
            FlightPhase.GO_AROUND: "Go Around",
            FlightPhase.SHUTDOWN: "Shutdown",
        }
        return names.get(self, "Unknown")

    @property
    def is_ground_phase(self) -> bool:
        """Check if this is a ground phase."""
        return self in [
            FlightPhase.PREFLIGHT,
            FlightPhase.ENGINE_START,
            FlightPhase.TAXI,
            FlightPhase.LANDING,
            FlightPhase.SHUTDOWN,
        ]

    @property
    def is_critical_phase(self) -> bool:
        """Check if this is a critical phase of flight."""
        return self in [
            FlightPhase.TAKEOFF,
            FlightPhase.APPROACH,
            FlightPhase.LANDING,
            FlightPhase.GO_AROUND,
        ]


@dataclass
class PhaseDetectionState:
    """State used for phase detection."""

    # Position
    on_ground: bool = True
    altitude_msl: float = 0.0  # feet
    altitude_agl: float = 0.0  # feet

    # Speed
    indicated_airspeed: float = 0.0  # knots
    ground_speed: float = 0.0  # knots
    vertical_speed: float = 0.0  # feet per minute

    # Configuration
    gear_handle_position: int = 1  # 0=up, 1=down
    flaps_handle_index: int = 0  # 0-4 typically
    spoilers_armed: bool = False
    parking_brake: bool = True

    # Engines
    engine1_running: bool = False
    engine2_running: bool = False
    engine1_n2: float = 0.0  # N2 percentage
    engine2_n2: float = 0.0

    # Throttle
    throttle_percent: float = 0.0

    @property
    def any_engine_running(self) -> bool:
        """Check if any engine is running."""
        return self.engine1_running or self.engine2_running

    @property
    def all_engines_running(self) -> bool:
        """Check if all engines are running."""
        return self.engine1_running and self.engine2_running

    @property
    def is_configured_for_landing(self) -> bool:
        """Check if aircraft is configured for landing."""
        return self.gear_handle_position == 1 and self.flaps_handle_index > 0


class FlightPhaseDetector:
    """
    Detects the current flight phase based on aircraft state.

    Uses a combination of criteria to determine the most likely phase.
    Implements hysteresis to prevent rapid phase switching.
    """

    # Thresholds
    TAXI_MAX_SPEED = 30  # knots
    TAKEOFF_SPEED_THRESHOLD = 50  # knots
    CLIMB_VS_THRESHOLD = 500  # fpm
    LEVEL_VS_THRESHOLD = 300  # fpm (±)
    DESCENT_VS_THRESHOLD = -500  # fpm
    APPROACH_MAX_ALTITUDE_AGL = 3000  # feet
    LANDING_MAX_ALTITUDE_AGL = 50  # feet
    GO_AROUND_VS_THRESHOLD = 1000  # fpm

    # Hysteresis
    PHASE_CHANGE_DELAY = 2.0  # seconds before confirming phase change

    def __init__(self):
        self._current_phase = FlightPhase.UNKNOWN
        self._previous_phase = FlightPhase.UNKNOWN
        self._phase_start_time = time.time()
        self._pending_phase: Optional[FlightPhase] = None
        self._pending_phase_time: float = 0.0
        self._was_airborne = False

        # Callbacks
        self._on_phase_change: Optional[Callable[[FlightPhase, FlightPhase], None]] = None

    def detect(self, state: PhaseDetectionState) -> FlightPhase:
        """
        Detect current flight phase.

        Args:
            state: Current aircraft state

        Returns:
            Detected flight phase
        """
        detected = self._evaluate_phase(state)

        # Apply hysteresis
        if detected != self._current_phase:
            if detected != self._pending_phase:
                # New potential phase change
                self._pending_phase = detected
                self._pending_phase_time = time.time()
            elif time.time() - self._pending_phase_time >= self.PHASE_CHANGE_DELAY:
                # Phase change confirmed after delay
                self._transition_to(detected)
        else:
            # Reset pending change
            self._pending_phase = None

        # Track airborne state for landing detection
        if not state.on_ground:
            self._was_airborne = True
        elif state.on_ground and state.ground_speed < 10:
            self._was_airborne = False

        return self._current_phase

    def _evaluate_phase(self, state: PhaseDetectionState) -> FlightPhase:
        """
        Evaluate all criteria and return most likely phase.

        Order matters - more specific conditions first.
        """

        # =====================================================================
        # GROUND PHASES
        # =====================================================================

        if state.on_ground:
            # PREFLIGHT: Parked, engines off
            if (not state.any_engine_running and
                state.parking_brake and
                state.ground_speed < 1):
                return FlightPhase.PREFLIGHT

            # ENGINE_START: N2 rising but not yet running
            if (not state.any_engine_running and
                (state.engine1_n2 > 5 or state.engine2_n2 > 5)):
                return FlightPhase.ENGINE_START

            # SHUTDOWN: Was running, now shutting down
            if (self._current_phase not in [FlightPhase.PREFLIGHT, FlightPhase.UNKNOWN] and
                not state.any_engine_running and
                state.ground_speed < 1):
                return FlightPhase.SHUTDOWN

            # LANDING: Just touched down, still fast
            if (self._was_airborne and
                state.ground_speed > self.TAXI_MAX_SPEED):
                return FlightPhase.LANDING

            # TAKEOFF: Accelerating on runway
            if (state.any_engine_running and
                state.ground_speed > self.TAXI_MAX_SPEED and
                state.throttle_percent > 50):
                return FlightPhase.TAKEOFF

            # TAXI: Moving slowly on ground
            if (state.any_engine_running and
                not state.parking_brake and
                state.ground_speed < self.TAXI_MAX_SPEED):
                return FlightPhase.TAXI

            # Still on ground but not matching other criteria
            if state.any_engine_running:
                return FlightPhase.TAXI

            return FlightPhase.PREFLIGHT

        # =====================================================================
        # AIRBORNE PHASES
        # =====================================================================

        # GO_AROUND: Climbing away from approach
        if (self._current_phase == FlightPhase.APPROACH and
            state.vertical_speed > self.GO_AROUND_VS_THRESHOLD and
            state.throttle_percent > 70):
            return FlightPhase.GO_AROUND

        # Continue GO_AROUND until established in climb
        if (self._current_phase == FlightPhase.GO_AROUND and
            state.altitude_agl < 1500):
            return FlightPhase.GO_AROUND

        # TAKEOFF: Initial climb after liftoff
        if (state.altitude_agl < 1500 and
            state.vertical_speed > 0 and
            self._current_phase in [FlightPhase.TAKEOFF, FlightPhase.TAXI, FlightPhase.UNKNOWN]):
            return FlightPhase.TAKEOFF

        # APPROACH: Low altitude, descending, configured
        if (state.altitude_agl < self.APPROACH_MAX_ALTITUDE_AGL and
            state.vertical_speed < 0 and
            state.is_configured_for_landing):
            return FlightPhase.APPROACH

        # Also APPROACH if low and slow, even if not fully configured
        if (state.altitude_agl < 1500 and
            state.indicated_airspeed < 180 and
            state.vertical_speed < 0):
            return FlightPhase.APPROACH

        # DESCENT: Descending at altitude
        if state.vertical_speed < self.DESCENT_VS_THRESHOLD:
            return FlightPhase.DESCENT

        # CLIMB: Climbing
        if state.vertical_speed > self.CLIMB_VS_THRESHOLD:
            return FlightPhase.CLIMB

        # CRUISE: Level flight
        if abs(state.vertical_speed) < self.LEVEL_VS_THRESHOLD:
            return FlightPhase.CRUISE

        # Default: maintain current or UNKNOWN
        return self._current_phase if self._current_phase != FlightPhase.UNKNOWN else FlightPhase.CRUISE

    def _transition_to(self, new_phase: FlightPhase):
        """Handle phase transition."""
        old_phase = self._current_phase
        self._previous_phase = old_phase
        self._current_phase = new_phase
        self._phase_start_time = time.time()
        self._pending_phase = None

        logger.info(f"Flight phase: {old_phase.display_name} → {new_phase.display_name}")

        if self._on_phase_change:
            self._on_phase_change(old_phase, new_phase)

    def force_phase(self, phase: FlightPhase):
        """Force a specific phase (for testing/override)."""
        self._transition_to(phase)

    @property
    def current_phase(self) -> FlightPhase:
        """Get current flight phase."""
        return self._current_phase

    @property
    def previous_phase(self) -> FlightPhase:
        """Get previous flight phase."""
        return self._previous_phase

    @property
    def phase_duration(self) -> float:
        """Get time in current phase (seconds)."""
        return time.time() - self._phase_start_time

    @property
    def is_critical_phase(self) -> bool:
        """Check if currently in critical phase."""
        return self._current_phase.is_critical_phase

    def on_phase_change(self, callback: Callable[[FlightPhase, FlightPhase], None]):
        """Register callback for phase changes."""
        self._on_phase_change = callback

    def reset(self):
        """Reset detector to initial state."""
        self._current_phase = FlightPhase.UNKNOWN
        self._previous_phase = FlightPhase.UNKNOWN
        self._phase_start_time = time.time()
        self._pending_phase = None
        self._was_airborne = False


# =============================================================================
# Phase-Aware Command Validation
# =============================================================================

# Commands that are restricted in certain phases
PHASE_RESTRICTIONS: Dict[FlightPhase, Dict[str, str]] = {
    FlightPhase.PREFLIGHT: {
        # Most commands allowed during preflight
    },

    FlightPhase.TAXI: {
        "gear_up": "Cannot retract gear while on ground",
        "flaps_retract": "Check flap setting for taxi",
    },

    FlightPhase.TAKEOFF: {
        "gear_up": None,  # Allowed after positive climb
        "spoilers_deploy": "Cannot deploy spoilers during takeoff",
        "ap_engage": "Cannot engage autopilot during takeoff roll",
        "engine_shutdown": "Cannot shutdown engines during takeoff",
    },

    FlightPhase.CLIMB: {
        # Most commands allowed
    },

    FlightPhase.CRUISE: {
        # Most commands allowed
    },

    FlightPhase.DESCENT: {
        # Most commands allowed
    },

    FlightPhase.APPROACH: {
        "gear_up": "Cannot retract gear during approach",
        "flaps_retract": "Cannot retract flaps during approach",
    },

    FlightPhase.LANDING: {
        "gear_up": "Cannot retract gear during landing roll",
        "engine_shutdown": "Wait until taxi to shutdown",
    },

    FlightPhase.GO_AROUND: {
        # Gear up is explicitly ALLOWED during go-around
        "spoilers_deploy": "Cannot deploy spoilers during go-around",
    },
}


def get_phase_restriction(phase: FlightPhase, command: str) -> Optional[str]:
    """
    Get restriction message for command in phase.

    Args:
        phase: Current flight phase
        command: Command identifier

    Returns:
        Restriction message or None if allowed
    """
    restrictions = PHASE_RESTRICTIONS.get(phase, {})
    return restrictions.get(command)


def is_command_allowed_in_phase(phase: FlightPhase, command: str) -> bool:
    """
    Check if command is allowed in current phase.

    Args:
        phase: Current flight phase
        command: Command identifier

    Returns:
        True if allowed
    """
    restriction = get_phase_restriction(phase, command)
    return restriction is None
