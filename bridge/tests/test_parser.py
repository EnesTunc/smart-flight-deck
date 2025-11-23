"""
Tests for command parser.
"""

import pytest
from logic.parser import CommandParser, ParsedCommand


class TestCommandParser:
    """Test command parsing functionality."""

    @pytest.fixture
    def parser(self):
        return CommandParser()

    # Gear commands
    def test_gear_down_basic(self, parser):
        result = parser.parse("gear down")
        assert result is not None
        assert result.intent == "gear_down"

    def test_gear_down_extend(self, parser):
        result = parser.parse("gear extend")
        assert result is not None
        assert result.intent == "gear_down"

    def test_gear_up_basic(self, parser):
        result = parser.parse("gear up")
        assert result is not None
        assert result.intent == "gear_up"

    def test_lower_the_gear(self, parser):
        result = parser.parse("lower the gear")
        assert result is not None
        assert result.intent == "gear_down"

    # Flaps commands
    def test_flaps_with_number(self, parser):
        result = parser.parse("flaps 2")
        assert result is not None
        assert result.intent == "flaps_set"

    def test_flaps_full(self, parser):
        result = parser.parse("flaps full")
        assert result is not None
        assert result.intent == "flaps_set"
        assert result.parameters.get("position") == 4

    def test_flaps_up(self, parser):
        result = parser.parse("flaps up")
        assert result is not None
        assert result.intent == "flaps_up"

    # Lights
    def test_landing_lights_on(self, parser):
        result = parser.parse("landing lights on")
        assert result is not None
        assert result.intent == "landing_lights_toggle"

    def test_lights_off(self, parser):
        result = parser.parse("lights off")
        assert result is not None
        assert result.intent == "landing_lights_toggle"

    # Parking brake
    def test_parking_brake(self, parser):
        result = parser.parse("parking brake")
        assert result is not None
        assert result.intent == "parking_brake_toggle"

    def test_set_brake(self, parser):
        result = parser.parse("set parking brake")
        assert result is not None
        assert result.intent == "parking_brake_toggle"

    # Queries
    def test_query_speed(self, parser):
        result = parser.parse("what's the speed")
        assert result is not None
        assert result.intent == "query_speed"

    def test_query_altitude(self, parser):
        result = parser.parse("current altitude")
        assert result is not None
        assert result.intent == "query_altitude"

    # Edge cases
    def test_empty_string(self, parser):
        result = parser.parse("")
        assert result is None

    def test_unknown_command(self, parser):
        result = parser.parse("make me a sandwich")
        assert result is None

    def test_case_insensitive(self, parser):
        result = parser.parse("GEAR DOWN")
        assert result is not None
        assert result.intent == "gear_down"

    def test_with_extra_words(self, parser):
        result = parser.parse("please put the gear down now")
        assert result is not None
        assert result.intent == "gear_down"
