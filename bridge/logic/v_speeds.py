"""
Smart Flight Deck Companion - V-Speeds Module
Aircraft speed limits and calculations.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AircraftCategory(Enum):
    """Aircraft category for default limits."""

    JET_AIRLINER = "jet_airliner"
    JET_REGIONAL = "jet_regional"
    TURBOPROP = "turboprop"
    SINGLE_PROP = "single_prop"
    UNKNOWN = "unknown"


@dataclass
class FlapSpeedLimits:
    """Flap extension speed limits (Vfe) by position."""

    # Position -> Max speed in knots
    limits: Dict[str, int] = field(default_factory=dict)

    def get_limit(self, position: int) -> Optional[int]:
        """Get speed limit for flap position."""
        # Try exact match first
        if str(position) in self.limits:
            return self.limits[str(position)]

        # Try common aliases
        aliases = {
            0: "0",
            1: "1",
            2: "2",
            3: "3",
            4: "full",
            5: "full",
        }

        alias = aliases.get(position)
        if alias and alias in self.limits:
            return self.limits[alias]

        return None

    def is_safe(self, position: int, current_speed: float) -> bool:
        """Check if current speed is safe for flap position."""
        limit = self.get_limit(position)
        if limit is None:
            return True  # No limit defined, assume safe
        return current_speed <= limit


@dataclass
class SpeedLimits:
    """Complete speed limits for an aircraft."""

    # Operating speeds
    vmo: int = 350  # Max operating speed (knots)
    mmo: float = 0.82  # Max operating Mach

    # Landing gear speeds
    vlo: int = 250  # Gear operating speed
    vle: int = 280  # Gear extended speed

    # Flap speeds
    vfe: FlapSpeedLimits = field(default_factory=FlapSpeedLimits)

    # Reference speeds (approximate)
    vref_base: int = 130  # Base Vref at reference weight
    green_dot: Optional[int] = None  # Best L/D speed (Airbus)

    # Stall speeds (approximate, clean config)
    vs_clean: int = 120  # Stall speed clean
    vs_full: int = 95  # Stall speed full flaps

    # Other limits
    max_altitude: int = 41000  # Service ceiling
    turbulence_penetration: int = 280  # Rough air speed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vmo": self.vmo,
            "mmo": self.mmo,
            "vlo": self.vlo,
            "vle": self.vle,
            "vfe": self.vfe.limits,
            "vref_base": self.vref_base,
            "green_dot": self.green_dot,
            "max_altitude": self.max_altitude,
        }


# =============================================================================
# Default Speed Limits by Aircraft Category
# =============================================================================

DEFAULT_LIMITS: Dict[AircraftCategory, SpeedLimits] = {
    AircraftCategory.JET_AIRLINER: SpeedLimits(
        vmo=350,
        mmo=0.82,
        vlo=250,
        vle=280,
        vfe=FlapSpeedLimits(limits={
            "1": 230,
            "2": 215,
            "3": 200,
            "full": 180,
        }),
        vref_base=135,
        vs_clean=130,
        vs_full=100,
        max_altitude=41000,
    ),

    AircraftCategory.JET_REGIONAL: SpeedLimits(
        vmo=320,
        mmo=0.78,
        vlo=220,
        vle=250,
        vfe=FlapSpeedLimits(limits={
            "1": 220,
            "2": 200,
            "3": 180,
            "full": 160,
        }),
        vref_base=125,
        vs_clean=115,
        vs_full=90,
        max_altitude=37000,
    ),

    AircraftCategory.TURBOPROP: SpeedLimits(
        vmo=250,
        mmo=0.55,
        vlo=180,
        vle=200,
        vfe=FlapSpeedLimits(limits={
            "1": 180,
            "2": 160,
            "3": 145,
            "full": 130,
        }),
        vref_base=100,
        vs_clean=90,
        vs_full=70,
        max_altitude=30000,
    ),

    AircraftCategory.SINGLE_PROP: SpeedLimits(
        vmo=180,
        mmo=0.40,
        vlo=120,
        vle=140,
        vfe=FlapSpeedLimits(limits={
            "1": 120,
            "2": 100,
            "full": 85,
        }),
        vref_base=65,
        vs_clean=55,
        vs_full=48,
        max_altitude=15000,
    ),

    AircraftCategory.UNKNOWN: SpeedLimits(
        vmo=250,
        mmo=0.70,
        vlo=200,
        vle=220,
        vfe=FlapSpeedLimits(limits={
            "1": 180,
            "2": 160,
            "full": 140,
        }),
        vref_base=100,
        vs_clean=100,
        vs_full=80,
        max_altitude=25000,
    ),
}


# =============================================================================
# Aircraft-Specific Speed Limits
# =============================================================================

AIRCRAFT_LIMITS: Dict[str, SpeedLimits] = {
    # Airbus A320 Family
    "a320": SpeedLimits(
        vmo=350,
        mmo=0.82,
        vlo=250,
        vle=280,
        vfe=FlapSpeedLimits(limits={
            "1": 230,
            "1+f": 215,
            "2": 200,
            "3": 185,
            "full": 177,
        }),
        vref_base=130,
        green_dot=220,
        vs_clean=130,
        vs_full=95,
        max_altitude=39100,
        turbulence_penetration=275,
    ),

    # Boeing 737 Family
    "b737": SpeedLimits(
        vmo=340,
        mmo=0.82,
        vlo=270,
        vle=320,
        vfe=FlapSpeedLimits(limits={
            "1": 250,
            "5": 250,
            "10": 210,
            "15": 200,
            "25": 190,
            "30": 175,
            "40": 162,
        }),
        vref_base=130,
        vs_clean=135,
        vs_full=100,
        max_altitude=41000,
        turbulence_penetration=280,
    ),

    # Boeing 747
    "b747": SpeedLimits(
        vmo=365,
        mmo=0.92,
        vlo=270,
        vle=320,
        vfe=FlapSpeedLimits(limits={
            "1": 280,
            "5": 260,
            "10": 240,
            "20": 220,
            "25": 205,
            "30": 180,
        }),
        vref_base=145,
        vs_clean=150,
        vs_full=115,
        max_altitude=45000,
    ),

    # Boeing 787
    "b787": SpeedLimits(
        vmo=360,
        mmo=0.90,
        vlo=270,
        vle=320,
        vfe=FlapSpeedLimits(limits={
            "1": 260,
            "5": 240,
            "15": 215,
            "20": 205,
            "25": 190,
            "30": 175,
        }),
        vref_base=135,
        vs_clean=140,
        vs_full=105,
        max_altitude=43000,
    ),

    # Cessna 172
    "c172": SpeedLimits(
        vmo=163,
        mmo=0.30,
        vlo=100,
        vle=140,
        vfe=FlapSpeedLimits(limits={
            "10": 110,
            "20": 85,
            "full": 85,
        }),
        vref_base=60,
        vs_clean=48,
        vs_full=40,
        max_altitude=14000,
    ),

    # CRJ-700/900
    "crj": SpeedLimits(
        vmo=335,
        mmo=0.85,
        vlo=250,
        vle=275,
        vfe=FlapSpeedLimits(limits={
            "8": 260,
            "20": 220,
            "30": 200,
            "45": 180,
        }),
        vref_base=130,
        vs_clean=125,
        vs_full=95,
        max_altitude=41000,
    ),

    # Embraer E-Jets
    "e190": SpeedLimits(
        vmo=320,
        mmo=0.82,
        vlo=250,
        vle=280,
        vfe=FlapSpeedLimits(limits={
            "1": 230,
            "2": 215,
            "3": 200,
            "4": 185,
            "5": 177,
            "full": 145,
        }),
        vref_base=125,
        vs_clean=120,
        vs_full=90,
        max_altitude=41000,
    ),
}


# =============================================================================
# Speed Limit Provider
# =============================================================================

class SpeedLimitProvider:
    """
    Provides speed limits for aircraft.

    Resolves limits from:
    1. Aircraft profile (JSON)
    2. Built-in aircraft limits
    3. Category defaults
    """

    def __init__(self):
        self._cache: Dict[str, SpeedLimits] = {}

    def get_limits(
        self,
        aircraft_title: str,
        profile_limits: Optional[Dict] = None
    ) -> SpeedLimits:
        """
        Get speed limits for an aircraft.

        Args:
            aircraft_title: Aircraft title from SimConnect
            profile_limits: Limits from aircraft profile JSON

        Returns:
            SpeedLimits for the aircraft
        """
        # Check cache first
        cache_key = aircraft_title.lower()
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Try profile limits first
        if profile_limits:
            limits = self._parse_profile_limits(profile_limits)
            self._cache[cache_key] = limits
            return limits

        # Try built-in aircraft limits
        limits = self._match_aircraft(aircraft_title)
        if limits:
            self._cache[cache_key] = limits
            return limits

        # Fall back to category defaults
        category = self._detect_category(aircraft_title)
        limits = DEFAULT_LIMITS[category]
        self._cache[cache_key] = limits
        return limits

    def _parse_profile_limits(self, profile_limits: Dict) -> SpeedLimits:
        """Parse limits from aircraft profile JSON."""
        vfe_data = profile_limits.get("vfe", {})
        vfe = FlapSpeedLimits(limits={str(k): v for k, v in vfe_data.items()})

        return SpeedLimits(
            vmo=profile_limits.get("vmo", 350),
            mmo=profile_limits.get("mmo", 0.82),
            vlo=profile_limits.get("vlo", 250),
            vle=profile_limits.get("vle", 280),
            vfe=vfe,
            vref_base=profile_limits.get("vref_base", 130),
            green_dot=profile_limits.get("green_dot"),
            vs_clean=profile_limits.get("vs_clean", 120),
            vs_full=profile_limits.get("vs_full", 95),
            max_altitude=profile_limits.get("max_altitude", 41000),
        )

    def _match_aircraft(self, aircraft_title: str) -> Optional[SpeedLimits]:
        """Match aircraft title to built-in limits."""
        title_lower = aircraft_title.lower()

        # A320 family
        if any(x in title_lower for x in ["a320", "a319", "a321", "a32n", "neo"]):
            if "fenix" in title_lower or "flybywire" in title_lower or "fbw" in title_lower:
                return AIRCRAFT_LIMITS["a320"]
            return AIRCRAFT_LIMITS["a320"]

        # Boeing 737
        if "737" in title_lower:
            return AIRCRAFT_LIMITS["b737"]

        # Boeing 747
        if "747" in title_lower:
            return AIRCRAFT_LIMITS["b747"]

        # Boeing 787
        if "787" in title_lower:
            return AIRCRAFT_LIMITS["b787"]

        # Cessna 172
        if "172" in title_lower or "cessna" in title_lower and "skyhawk" in title_lower:
            return AIRCRAFT_LIMITS["c172"]

        # CRJ
        if "crj" in title_lower:
            return AIRCRAFT_LIMITS["crj"]

        # E-Jets
        if any(x in title_lower for x in ["e170", "e175", "e190", "e195", "embraer"]):
            return AIRCRAFT_LIMITS["e190"]

        return None

    def _detect_category(self, aircraft_title: str) -> AircraftCategory:
        """Detect aircraft category from title."""
        title_lower = aircraft_title.lower()

        # Jet airliners
        jet_keywords = ["airbus", "boeing", "737", "747", "767", "777", "787",
                       "a320", "a330", "a340", "a350", "a380", "md-80", "md-11"]
        if any(kw in title_lower for kw in jet_keywords):
            return AircraftCategory.JET_AIRLINER

        # Regional jets
        regional_keywords = ["crj", "erj", "e170", "e175", "e190", "e195",
                           "embraer", "bombardier"]
        if any(kw in title_lower for kw in regional_keywords):
            return AircraftCategory.JET_REGIONAL

        # Turboprops
        turboprop_keywords = ["atr", "dash", "dhc", "king air", "tbm", "pc-12",
                            "caravan", "turboprop"]
        if any(kw in title_lower for kw in turboprop_keywords):
            return AircraftCategory.TURBOPROP

        # Single props
        prop_keywords = ["cessna", "piper", "beech", "172", "152", "182",
                        "bonanza", "baron", "cherokee"]
        if any(kw in title_lower for kw in prop_keywords):
            return AircraftCategory.SINGLE_PROP

        return AircraftCategory.UNKNOWN

    def clear_cache(self):
        """Clear the limits cache."""
        self._cache.clear()


# =============================================================================
# Speed Calculations
# =============================================================================

def calculate_vref(
    base_vref: int,
    actual_weight_kg: float,
    reference_weight_kg: float = 60000,
    flap_setting: str = "full"
) -> int:
    """
    Calculate reference speed (Vref) based on weight.

    Simplified formula - real aircraft use performance tables.

    Args:
        base_vref: Base Vref at reference weight
        actual_weight_kg: Actual landing weight
        reference_weight_kg: Reference weight for base Vref
        flap_setting: Flap setting for landing

    Returns:
        Calculated Vref in knots
    """
    # Weight correction: approximately 1 knot per 1000 kg difference
    weight_diff = (actual_weight_kg - reference_weight_kg) / 1000
    weight_correction = weight_diff * 1.0

    # Flap correction (if not full flaps)
    flap_corrections = {
        "full": 0,
        "3": 5,
        "30": 5,
        "2": 10,
        "25": 8,
        "1": 20,
        "15": 12,
    }
    flap_correction = flap_corrections.get(str(flap_setting), 0)

    vref = base_vref + weight_correction + flap_correction

    return max(int(round(vref)), base_vref - 10)  # Don't go below base - 10


def calculate_approach_speed(vref: int, wind_speed: int = 0, gust: int = 0) -> int:
    """
    Calculate approach speed (Vapp) with wind correction.

    Standard: Vapp = Vref + half headwind + full gust increment

    Args:
        vref: Reference speed
        wind_speed: Headwind component
        gust: Gust factor (max - sustained)

    Returns:
        Approach speed in knots
    """
    # Half the headwind, max 10 knots
    wind_additive = min(wind_speed / 2, 10)

    # Full gust factor, max 10 knots
    gust_additive = min(gust, 10)

    vapp = vref + wind_additive + gust_additive

    return int(round(vapp))


def check_speed_margin(
    current_speed: float,
    limit_speed: int,
    margin_percent: float = 0.05
) -> tuple[bool, float]:
    """
    Check speed against limit with margin.

    Args:
        current_speed: Current IAS
        limit_speed: Speed limit
        margin_percent: Warning margin (default 5%)

    Returns:
        Tuple of (is_safe, margin_remaining)
    """
    margin = limit_speed * margin_percent
    margin_remaining = limit_speed - current_speed

    is_safe = current_speed <= limit_speed

    return is_safe, margin_remaining
