"""
Tests for flight context and safety checks.
"""

import pytest
from logic.context import FlightContext, FlightPhase


class TestFlightContext:
    """Test flight context functionality."""

    @pytest.fixture
    def context(self):
        return FlightContext()

    # Phase detection
    def test_preflight_phase(self, context):
        context.update(
            altitude=0,
            speed=0,
            vertical_speed=0,
            on_ground=True,
            gear_down=True,
        )
        assert context.phase == FlightPhase.PREFLIGHT

    def test_taxi_phase(self, context):
        context.update(
            altitude=0,
            speed=15,
            vertical_speed=0,
            on_ground=True,
            gear_down=True,
        )
        assert context.phase == FlightPhase.TAXI

    def test_climb_phase(self, context):
        context.update(
            altitude=5000,
            speed=250,
            vertical_speed=2000,
            on_ground=False,
            gear_down=False,
        )
        assert context.phase == FlightPhase.CLIMB

    def test_cruise_phase(self, context):
        context.update(
            altitude=35000,
            speed=450,
            vertical_speed=0,
            on_ground=False,
            gear_down=False,
        )
        assert context.phase == FlightPhase.CRUISE

    def test_approach_phase(self, context):
        context.update(
            altitude=2000,
            speed=140,
            vertical_speed=-700,
            on_ground=False,
            gear_down=True,
        )
        assert context.phase == FlightPhase.APPROACH

    # Safety checks
    def test_gear_extend_allowed_low_speed(self, context):
        context.update(
            altitude=3000,
            speed=200,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
        )
        result = context.check_gear_extend()
        assert result.allowed is True

    def test_gear_extend_blocked_high_speed(self, context):
        context.update(
            altitude=10000,
            speed=300,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
        )
        result = context.check_gear_extend()
        assert result.allowed is False
        assert "Speed too high" in result.reason

    def test_gear_extend_warning_high_altitude(self, context):
        context.update(
            altitude=20000,
            speed=200,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
        )
        result = context.check_gear_extend()
        assert result.allowed is True
        assert result.warning is not None

    def test_flaps_extend_allowed(self, context):
        context.update(
            altitude=3000,
            speed=180,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
        )
        result = context.check_flaps_extend(position=2)
        assert result.allowed is True

    def test_flaps_extend_blocked_high_speed(self, context):
        context.update(
            altitude=3000,
            speed=220,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
        )
        result = context.check_flaps_extend(position=2)
        assert result.allowed is False

    # Properties
    def test_is_on_ground(self, context):
        context.update(
            altitude=0,
            speed=0,
            vertical_speed=0,
            on_ground=True,
            gear_down=True,
        )
        assert context.is_on_ground is True

    def test_current_speed(self, context):
        context.update(
            altitude=10000,
            speed=250,
            vertical_speed=0,
            on_ground=False,
            gear_down=False,
        )
        assert context.current_speed == 250
