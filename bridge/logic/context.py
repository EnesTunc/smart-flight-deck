"""
Smart Flight Deck Companion - Flight Context
Situational awareness and safety checks.
"""

import logging
from enum import Enum
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class FlightPhase(Enum):
    """Current phase of flight."""

    PREFLIGHT = "preflight"
    TAXI = "taxi"
    TAKEOFF = "takeoff"
    CLIMB = "climb"
    CRUISE = "cruise"
    DESCENT = "descent"
    APPROACH = "approach"
    LANDING = "landing"
    ROLLOUT = "rollout"


@dataclass
class SafetyCheckResult:
    """Result of a safety check."""

    allowed: bool
    reason: Optional[str] = None
    warning: Optional[str] = None


class FlightContext:
    """
    Maintains awareness of current flight situation.

    Used for:
    - Safety checks (don't extend gear at high speed)
    - Context-aware responses
    - Flight phase detection
    """

    # Safety thresholds
    MAX_GEAR_EXTEND_SPEED = 250  # knots
    MAX_FLAPS_SPEED = {
        1: 250,  # Flaps 1
        2: 200,  # Flaps 2
        3: 180,  # Flaps 3
        4: 160,  # Flaps full
    }

    def __init__(self):
        self._phase = FlightPhase.PREFLIGHT
        self._last_altitude = 0.0
        self._last_speed = 0.0
        self._on_ground = True

    def update(
        self,
        altitude: float,
        speed: float,
        vertical_speed: float,
        on_ground: bool,
        gear_down: bool,
    ):
        """
        Update flight context with current data.

        Args:
            altitude: Current altitude in feet
            speed: Indicated airspeed in knots
            vertical_speed: Vertical speed in fpm
            on_ground: Whether aircraft is on ground
            gear_down: Whether gear is extended
        """
        self._last_altitude = altitude
        self._last_speed = speed
        self._on_ground = on_ground

        # Detect flight phase
        self._phase = self._detect_phase(
            altitude, speed, vertical_speed, on_ground, gear_down
        )

    def _detect_phase(
        self,
        altitude: float,
        speed: float,
        vertical_speed: float,
        on_ground: bool,
        gear_down: bool,
    ) -> FlightPhase:
        """Detect current flight phase."""
        if on_ground:
            if speed < 30:
                return FlightPhase.PREFLIGHT if speed < 5 else FlightPhase.TAXI
            elif speed > 50:
                return FlightPhase.ROLLOUT if vertical_speed < 100 else FlightPhase.TAKEOFF

        # Airborne
        if altitude < 1000 and vertical_speed > 500:
            return FlightPhase.TAKEOFF
        elif altitude < 10000 and vertical_speed > 300:
            return FlightPhase.CLIMB
        elif altitude > 20000 and abs(vertical_speed) < 300:
            return FlightPhase.CRUISE
        elif vertical_speed < -300 and altitude > 3000:
            return FlightPhase.DESCENT
        elif altitude < 3000 and vertical_speed < -200:
            return FlightPhase.APPROACH
        elif altitude < 500 and gear_down:
            return FlightPhase.LANDING

        return FlightPhase.CRUISE  # Default

    def check_gear_extend(self) -> SafetyCheckResult:
        """Check if gear extension is safe."""
        if self._last_speed > self.MAX_GEAR_EXTEND_SPEED:
            return SafetyCheckResult(
                allowed=False,
                reason=f"Speed too high for gear extension. Current: {self._last_speed:.0f} kts, Max: {self.MAX_GEAR_EXTEND_SPEED} kts",
                warning="Reduce speed below 250 knots before extending gear",
            )

        if self._last_altitude > 15000:
            return SafetyCheckResult(
                allowed=True,
                warning="Unusual: Extending gear above 15000 feet",
            )

        return SafetyCheckResult(allowed=True)

    def check_flaps_extend(self, position: int) -> SafetyCheckResult:
        """Check if flaps extension is safe."""
        max_speed = self.MAX_FLAPS_SPEED.get(position, 200)

        if self._last_speed > max_speed:
            return SafetyCheckResult(
                allowed=False,
                reason=f"Speed too high for Flaps {position}. Current: {self._last_speed:.0f} kts, Max: {max_speed} kts",
            )

        return SafetyCheckResult(allowed=True)

    def check_takeoff_config(self) -> SafetyCheckResult:
        """Check takeoff configuration."""
        warnings = []

        # Add checks as needed
        # This would check flaps position, trim, etc.

        if warnings:
            return SafetyCheckResult(
                allowed=True,
                warning="; ".join(warnings),
            )

        return SafetyCheckResult(allowed=True)

    @property
    def phase(self) -> FlightPhase:
        """Current flight phase."""
        return self._phase

    @property
    def is_on_ground(self) -> bool:
        """Whether aircraft is on ground."""
        return self._on_ground

    @property
    def current_speed(self) -> float:
        """Last known speed."""
        return self._last_speed

    @property
    def current_altitude(self) -> float:
        """Last known altitude."""
        return self._last_altitude
