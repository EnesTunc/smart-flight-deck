"""
Tests for flight context and safety checks.
"""

import pytest
from logic.context import ContextEngine
from logic.flight_phase import FlightPhase


# Baseline state so every test provides a complete snapshot. Phase detection
# reads engine and ground speed data, so partial state resolves to UNKNOWN.
BASE_STATE = {
    "altitude": 0.0,
    "altitude_agl": 0.0,
    "speed": 0.0,
    "ground_speed": 0.0,
    "vertical_speed": 0.0,
    "on_ground": True,
    "gear_down": True,
    "flaps_index": 0,
    "engine1_running": False,
    "engine2_running": False,
    "parking_brake": False,
}


class TestFlightContext:
    """Test flight context functionality."""

    @pytest.fixture
    def context(self):
        engine = ContextEngine()
        # The detector applies hysteresis (PHASE_CHANGE_DELAY seconds) so the
        # phase cannot flicker in flight. Drop the delay so tests do not have
        # to wait in real time.
        engine._phase_detector.PHASE_CHANGE_DELAY = 0
        return engine

    @staticmethod
    def settle(context, **overrides):
        """
        Feed one state to the context until the phase transition is confirmed.

        Even with a zero delay, the detector needs one update to register the
        pending phase and a second one to commit the transition.
        """
        state = {**BASE_STATE, **overrides}
        context.update_from_simconnect(**state)
        context.update_from_simconnect(**state)

    # Phase detection
    def test_preflight_phase(self, context):
        self.settle(
            context,
            on_ground=True,
            parking_brake=True,
        )
        assert context.phase == FlightPhase.PREFLIGHT

    def test_taxi_phase(self, context):
        self.settle(
            context,
            speed=15,
            ground_speed=15,
            on_ground=True,
            engine1_running=True,
            engine2_running=True,
        )
        assert context.phase == FlightPhase.TAXI

    def test_climb_phase(self, context):
        self.settle(
            context,
            altitude=5000,
            altitude_agl=5000,
            speed=250,
            ground_speed=260,
            vertical_speed=2000,
            on_ground=False,
            gear_down=False,
            engine1_running=True,
            engine2_running=True,
        )
        assert context.phase == FlightPhase.CLIMB

    def test_cruise_phase(self, context):
        self.settle(
            context,
            altitude=35000,
            altitude_agl=35000,
            speed=450,
            ground_speed=470,
            vertical_speed=0,
            on_ground=False,
            gear_down=False,
            engine1_running=True,
            engine2_running=True,
        )
        assert context.phase == FlightPhase.CRUISE

    def test_approach_phase(self, context):
        self.settle(
            context,
            altitude=2000,
            altitude_agl=2000,
            speed=140,
            ground_speed=145,
            vertical_speed=-700,
            on_ground=False,
            gear_down=True,
            flaps_index=3,
            engine1_running=True,
            engine2_running=True,
        )
        assert context.phase == FlightPhase.APPROACH

    # Safety checks
    def test_gear_extend_allowed_low_speed(self, context):
        self.settle(
            context,
            altitude=3000,
            altitude_agl=3000,
            speed=200,
            ground_speed=210,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
            engine1_running=True,
            engine2_running=True,
        )
        result = context.check_gear_extend()
        assert result.allowed is True

    def test_gear_extend_blocked_high_speed(self, context):
        self.settle(
            context,
            altitude=10000,
            altitude_agl=10000,
            speed=300,
            ground_speed=320,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
            engine1_running=True,
            engine2_running=True,
        )
        result = context.check_gear_extend()
        assert result.allowed is False
        assert "Speed too high" in result.reason

    def test_gear_extend_warning_high_altitude(self, context):
        self.settle(
            context,
            altitude=20000,
            altitude_agl=20000,
            speed=200,
            ground_speed=220,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
            engine1_running=True,
            engine2_running=True,
        )
        result = context.check_gear_extend()
        assert result.allowed is True
        assert result.warning is not None

    def test_flaps_extend_allowed(self, context):
        self.settle(
            context,
            altitude=3000,
            altitude_agl=3000,
            speed=150,
            ground_speed=160,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
            engine1_running=True,
            engine2_running=True,
        )
        result = context.check_flaps_extend(position=2)
        assert result.allowed is True

    def test_flaps_extend_blocked_high_speed(self, context):
        self.settle(
            context,
            altitude=3000,
            altitude_agl=3000,
            speed=220,
            ground_speed=230,
            vertical_speed=-500,
            on_ground=False,
            gear_down=False,
            engine1_running=True,
            engine2_running=True,
        )
        result = context.check_flaps_extend(position=2)
        assert result.allowed is False

    # Properties
    def test_is_on_ground(self, context):
        self.settle(
            context,
            on_ground=True,
            parking_brake=True,
        )
        assert context.is_on_ground is True

    def test_current_speed(self, context):
        self.settle(
            context,
            altitude=10000,
            altitude_agl=10000,
            speed=250,
            ground_speed=260,
            vertical_speed=0,
            on_ground=False,
            gear_down=False,
            engine1_running=True,
            engine2_running=True,
        )
        assert context.current_speed == 250
