"""
Smart Flight Deck Companion - Safety Rules Engine
Evaluates commands against safety rules before execution.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
import logging

from .flight_phase import FlightPhase, PhaseDetectionState, get_phase_restriction
from .v_speeds import SpeedLimits, SpeedLimitProvider

logger = logging.getLogger(__name__)


class SafetyAction(Enum):
    """Action to take based on safety evaluation."""

    ALLOW = auto()      # Safe to execute
    REMIND = auto()     # Execute with reminder
    WARN = auto()       # Execute with warning
    CONFIRM = auto()    # Requires user confirmation
    BLOCK = auto()      # Do not execute

    @property
    def should_execute(self) -> bool:
        """Check if command should be executed."""
        return self in [SafetyAction.ALLOW, SafetyAction.REMIND, SafetyAction.WARN]

    @property
    def needs_confirmation(self) -> bool:
        """Check if confirmation is needed."""
        return self == SafetyAction.CONFIRM


@dataclass
class SafetyEvaluation:
    """Result of safety rule evaluation."""

    action: SafetyAction
    rule_id: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    can_override: bool = True

    @property
    def is_safe(self) -> bool:
        """Check if evaluation indicates safe."""
        return self.action in [SafetyAction.ALLOW, SafetyAction.REMIND]


@dataclass
class SafetyContext:
    """Context for safety evaluation."""

    # Aircraft state
    state: PhaseDetectionState

    # Current phase
    flight_phase: FlightPhase

    # Speed limits
    limits: SpeedLimits

    # Command info
    command_id: str
    command_value: Any = None

    # Override requested
    override_requested: bool = False


# =============================================================================
# Safety Rules Definition
# =============================================================================

@dataclass
class SafetyRule:
    """Definition of a safety rule."""

    rule_id: str
    description: str
    applicable_commands: List[str]
    evaluator: Callable[[SafetyContext], Optional[SafetyEvaluation]]
    priority: int = 100  # Lower = higher priority
    can_override: bool = True


class SafetyRulesEngine:
    """
    Evaluates commands against safety rules.

    Rules are evaluated in priority order. First blocking rule wins.
    """

    def __init__(self):
        self._rules: List[SafetyRule] = []
        self._speed_provider = SpeedLimitProvider()
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Set up default safety rules."""

        # =====================================================================
        # GEAR RULES
        # =====================================================================

        self.add_rule(SafetyRule(
            rule_id="GEAR_001",
            description="Speed too high for gear extension",
            applicable_commands=["gear_down", "gear_toggle"],
            evaluator=self._check_gear_speed_high,
            priority=10,
            can_override=True,
        ))

        self.add_rule(SafetyRule(
            rule_id="GEAR_002",
            description="Gear extended speed exceeded",
            applicable_commands=["gear_down"],  # Warning when already down
            evaluator=self._check_gear_extended_speed,
            priority=20,
        ))

        self.add_rule(SafetyRule(
            rule_id="GEAR_003",
            description="Low altitude gear retraction",
            applicable_commands=["gear_up", "gear_toggle"],
            evaluator=self._check_gear_low_altitude,
            priority=30,
        ))

        self.add_rule(SafetyRule(
            rule_id="GEAR_004",
            description="Gear retraction during approach",
            applicable_commands=["gear_up"],
            evaluator=self._check_gear_approach,
            priority=10,
            can_override=False,
        ))

        self.add_rule(SafetyRule(
            rule_id="GEAR_005",
            description="Gear retraction on ground",
            applicable_commands=["gear_up", "gear_toggle"],
            evaluator=self._check_gear_on_ground,
            priority=5,
            can_override=False,
        ))

        # =====================================================================
        # FLAP RULES
        # =====================================================================

        self.add_rule(SafetyRule(
            rule_id="FLAP_001",
            description="Speed too high for flap extension",
            applicable_commands=["flaps_down", "flaps_set", "flaps_extend"],
            evaluator=self._check_flap_speed,
            priority=10,
            can_override=True,
        ))

        self.add_rule(SafetyRule(
            rule_id="FLAP_002",
            description="Early flap retraction after takeoff",
            applicable_commands=["flaps_up", "flaps_retract"],
            evaluator=self._check_flap_early_retract,
            priority=30,
        ))

        self.add_rule(SafetyRule(
            rule_id="FLAP_003",
            description="Flap retraction during approach",
            applicable_commands=["flaps_up", "flaps_retract"],
            evaluator=self._check_flap_approach,
            priority=15,
        ))

        # =====================================================================
        # AUTOPILOT RULES
        # =====================================================================

        self.add_rule(SafetyRule(
            rule_id="AP_001",
            description="Low altitude autopilot engagement",
            applicable_commands=["ap_engage", "ap1_push", "ap2_push", "autopilot_toggle"],
            evaluator=self._check_ap_low_altitude,
            priority=30,
        ))

        self.add_rule(SafetyRule(
            rule_id="AP_002",
            description="Autopilot during takeoff",
            applicable_commands=["ap_engage", "ap1_push", "ap2_push", "autopilot_toggle"],
            evaluator=self._check_ap_takeoff,
            priority=10,
        ))

        # =====================================================================
        # SPOILER RULES
        # =====================================================================

        self.add_rule(SafetyRule(
            rule_id="SPD_001",
            description="Spoilers during takeoff",
            applicable_commands=["spoilers_deploy", "spoilers_on"],
            evaluator=self._check_spoilers_takeoff,
            priority=5,
            can_override=False,
        ))

        self.add_rule(SafetyRule(
            rule_id="SPD_002",
            description="Spoilers not armed for landing",
            applicable_commands=[],  # Proactive check
            evaluator=self._check_spoilers_not_armed,
            priority=50,
        ))

        # =====================================================================
        # ENGINE RULES
        # =====================================================================

        self.add_rule(SafetyRule(
            rule_id="ENG_001",
            description="Engine shutdown while airborne",
            applicable_commands=["engine_shutdown", "engine1_off", "engine2_off"],
            evaluator=self._check_engine_shutdown_airborne,
            priority=1,
            can_override=False,
        ))

        self.add_rule(SafetyRule(
            rule_id="ENG_002",
            description="Engine shutdown while moving",
            applicable_commands=["engine_shutdown", "engine1_off", "engine2_off"],
            evaluator=self._check_engine_shutdown_moving,
            priority=20,
        ))

        # =====================================================================
        # LIGHT REMINDERS
        # =====================================================================

        self.add_rule(SafetyRule(
            rule_id="LGT_001",
            description="Landing lights for takeoff",
            applicable_commands=["takeoff_config_check"],
            evaluator=self._check_landing_lights_takeoff,
            priority=100,
        ))

        # Sort by priority
        self._rules.sort(key=lambda r: r.priority)

    def add_rule(self, rule: SafetyRule):
        """Add a safety rule."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority)

    def evaluate(self, context: SafetyContext) -> SafetyEvaluation:
        """
        Evaluate a command against all applicable rules.

        Args:
            context: Safety evaluation context

        Returns:
            SafetyEvaluation with action and message
        """
        command = context.command_id

        # Check phase restrictions first
        phase_restriction = get_phase_restriction(context.flight_phase, command)
        if phase_restriction:
            if not context.override_requested:
                return SafetyEvaluation(
                    action=SafetyAction.BLOCK,
                    rule_id="PHASE_RESTRICT",
                    message=phase_restriction,
                    can_override=False,
                )

        # Evaluate all applicable rules
        evaluations: List[SafetyEvaluation] = []

        for rule in self._rules:
            if command in rule.applicable_commands or not rule.applicable_commands:
                result = rule.evaluator(context)
                if result:
                    result.can_override = rule.can_override
                    evaluations.append(result)

        # Find most severe evaluation
        if not evaluations:
            return SafetyEvaluation(
                action=SafetyAction.ALLOW,
                rule_id="NONE",
                message="Command is safe to execute",
            )

        # Sort by severity (BLOCK > CONFIRM > WARN > REMIND > ALLOW)
        severity_order = {
            SafetyAction.BLOCK: 0,
            SafetyAction.CONFIRM: 1,
            SafetyAction.WARN: 2,
            SafetyAction.REMIND: 3,
            SafetyAction.ALLOW: 4,
        }
        evaluations.sort(key=lambda e: severity_order[e.action])

        result = evaluations[0]

        # Handle override
        if context.override_requested and result.can_override:
            if result.action in [SafetyAction.BLOCK, SafetyAction.CONFIRM]:
                return SafetyEvaluation(
                    action=SafetyAction.WARN,
                    rule_id=result.rule_id + "_OVERRIDE",
                    message=f"Override accepted. {result.message}",
                    details=result.details,
                )

        return result

    # =========================================================================
    # Rule Evaluators - Gear
    # =========================================================================

    def _check_gear_speed_high(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check if speed is too high for gear extension."""
        ias = ctx.state.indicated_airspeed
        vlo = ctx.limits.vlo

        if ias > vlo:
            return SafetyEvaluation(
                action=SafetyAction.BLOCK,
                rule_id="GEAR_001",
                message=f"Speed too high for gear. Current {int(ias)} kts, max {vlo} kts.",
                details={"current_speed": ias, "limit": vlo},
            )

        # Warning if close to limit
        if ias > vlo * 0.9:
            return SafetyEvaluation(
                action=SafetyAction.WARN,
                rule_id="GEAR_001_MARGIN",
                message=f"Speed near gear limit. Current {int(ias)} kts, max {vlo} kts.",
                details={"current_speed": ias, "limit": vlo},
            )

        return None

    def _check_gear_extended_speed(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check if exceeding gear extended speed."""
        if ctx.state.gear_handle_position != 1:
            return None

        ias = ctx.state.indicated_airspeed
        vle = ctx.limits.vle

        if ias > vle:
            return SafetyEvaluation(
                action=SafetyAction.WARN,
                rule_id="GEAR_002",
                message=f"Exceeding gear extended speed. Current {int(ias)} kts, max {vle} kts.",
                details={"current_speed": ias, "limit": vle},
            )

        return None

    def _check_gear_low_altitude(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for low altitude gear retraction."""
        if ctx.state.on_ground:
            return None

        agl = ctx.state.altitude_agl

        if agl < 500:
            return SafetyEvaluation(
                action=SafetyAction.WARN,
                rule_id="GEAR_003",
                message=f"Low altitude gear retraction. Altitude {int(agl)} feet AGL.",
                details={"altitude_agl": agl},
            )

        return None

    def _check_gear_approach(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for gear retraction during approach."""
        if ctx.flight_phase == FlightPhase.APPROACH:
            return SafetyEvaluation(
                action=SafetyAction.BLOCK,
                rule_id="GEAR_004",
                message="Cannot retract gear during approach.",
            )

        return None

    def _check_gear_on_ground(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for gear retraction on ground."""
        if ctx.state.on_ground and ctx.command_id in ["gear_up", "gear_toggle"]:
            return SafetyEvaluation(
                action=SafetyAction.BLOCK,
                rule_id="GEAR_005",
                message="Cannot retract gear while on ground.",
            )

        return None

    # =========================================================================
    # Rule Evaluators - Flaps
    # =========================================================================

    def _check_flap_speed(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check if speed is too high for flap extension."""
        ias = ctx.state.indicated_airspeed
        target_position = ctx.command_value or ctx.state.flaps_handle_index + 1

        vfe = ctx.limits.vfe.get_limit(target_position)
        if vfe is None:
            return None

        if ias > vfe:
            return SafetyEvaluation(
                action=SafetyAction.BLOCK,
                rule_id="FLAP_001",
                message=f"Speed too high for flaps {target_position}. Current {int(ias)} kts, max {vfe} kts.",
                details={"current_speed": ias, "limit": vfe, "position": target_position},
            )

        if ias > vfe * 0.9:
            return SafetyEvaluation(
                action=SafetyAction.WARN,
                rule_id="FLAP_001_MARGIN",
                message=f"Speed near flap limit. Current {int(ias)} kts, max {vfe} kts.",
                details={"current_speed": ias, "limit": vfe},
            )

        return None

    def _check_flap_early_retract(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for early flap retraction after takeoff."""
        if ctx.flight_phase != FlightPhase.TAKEOFF:
            return None

        agl = ctx.state.altitude_agl
        ias = ctx.state.indicated_airspeed

        if agl < 1000 or ias < 180:
            return SafetyEvaluation(
                action=SafetyAction.WARN,
                rule_id="FLAP_002",
                message=f"Early flap retraction. Altitude {int(agl)} ft, speed {int(ias)} kts.",
                details={"altitude_agl": agl, "speed": ias},
            )

        return None

    def _check_flap_approach(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for flap retraction during approach."""
        if ctx.flight_phase == FlightPhase.APPROACH:
            return SafetyEvaluation(
                action=SafetyAction.CONFIRM,
                rule_id="FLAP_003",
                message="Flap retraction during approach. Are you going around?",
            )

        return None

    # =========================================================================
    # Rule Evaluators - Autopilot
    # =========================================================================

    def _check_ap_low_altitude(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for low altitude autopilot engagement."""
        if ctx.state.on_ground:
            return None

        agl = ctx.state.altitude_agl

        if agl < 500:
            return SafetyEvaluation(
                action=SafetyAction.WARN,
                rule_id="AP_001",
                message=f"Low altitude autopilot engagement. Altitude {int(agl)} feet AGL.",
                details={"altitude_agl": agl},
            )

        return None

    def _check_ap_takeoff(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for autopilot during takeoff."""
        if ctx.flight_phase == FlightPhase.TAKEOFF and ctx.state.on_ground:
            return SafetyEvaluation(
                action=SafetyAction.BLOCK,
                rule_id="AP_002",
                message="Cannot engage autopilot during takeoff roll.",
            )

        return None

    # =========================================================================
    # Rule Evaluators - Spoilers
    # =========================================================================

    def _check_spoilers_takeoff(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for spoiler deployment during takeoff."""
        if ctx.flight_phase == FlightPhase.TAKEOFF:
            return SafetyEvaluation(
                action=SafetyAction.BLOCK,
                rule_id="SPD_001",
                message="Cannot deploy spoilers during takeoff.",
            )

        return None

    def _check_spoilers_not_armed(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check if spoilers are armed for landing."""
        if ctx.flight_phase == FlightPhase.APPROACH and not ctx.state.spoilers_armed:
            return SafetyEvaluation(
                action=SafetyAction.REMIND,
                rule_id="SPD_002",
                message="Reminder: Spoilers not armed for landing.",
            )

        return None

    # =========================================================================
    # Rule Evaluators - Engine
    # =========================================================================

    def _check_engine_shutdown_airborne(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for engine shutdown while airborne."""
        if not ctx.state.on_ground:
            return SafetyEvaluation(
                action=SafetyAction.BLOCK,
                rule_id="ENG_001",
                message="Cannot shutdown engines while airborne!",
            )

        return None

    def _check_engine_shutdown_moving(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check for engine shutdown while moving."""
        if ctx.state.ground_speed > 5:
            return SafetyEvaluation(
                action=SafetyAction.CONFIRM,
                rule_id="ENG_002",
                message=f"Aircraft is moving at {int(ctx.state.ground_speed)} kts. Confirm engine shutdown?",
                details={"ground_speed": ctx.state.ground_speed},
            )

        return None

    # =========================================================================
    # Rule Evaluators - Lights
    # =========================================================================

    def _check_landing_lights_takeoff(self, ctx: SafetyContext) -> Optional[SafetyEvaluation]:
        """Check landing lights for takeoff."""
        # This would need landing light state from SimConnect
        # For now, just a placeholder
        return None


# =============================================================================
# Response Templates
# =============================================================================

RESPONSE_TEMPLATES = {
    "en": {
        "GEAR_001": "Unable. Speed {current_speed} knots exceeds gear limit of {limit} knots.",
        "GEAR_003": "Warning. Retracting gear at {altitude_agl} feet. Positive rate, gear up.",
        "GEAR_004": "Unable. Cannot retract gear during approach.",
        "GEAR_005": "Unable. Cannot retract gear while on ground.",
        "FLAP_001": "Unable. Speed {current_speed} knots exceeds flap {position} limit of {limit} knots.",
        "FLAP_002": "Caution. Early flap retraction at {altitude_agl} feet.",
        "AP_001": "Caution. Low altitude autopilot engagement at {altitude_agl} feet.",
        "AP_002": "Unable. Cannot engage autopilot during takeoff roll.",
        "SPD_001": "Unable. Cannot deploy spoilers during takeoff.",
        "ENG_001": "Unable. Cannot shutdown engines while airborne.",
        "ENG_002": "Aircraft is moving. Say confirm to shutdown engines.",
    },
    "tr": {
        "GEAR_001": "Yapılamıyor. Hız {current_speed} knot, gear limiti {limit} knot.",
        "GEAR_003": "Uyarı. {altitude_agl} feet'te gear kaldırılıyor.",
        "GEAR_004": "Yapılamıyor. Approach sırasında gear kaldırılamaz.",
        "GEAR_005": "Yapılamıyor. Yerdeyken gear kaldırılamaz.",
        "FLAP_001": "Yapılamıyor. Hız {current_speed} knot, flap {position} limiti {limit} knot.",
        "ENG_001": "Yapılamıyor. Havadayken motor kapatılamaz.",
    },
}


def get_response_text(
    rule_id: str,
    language: str = "en",
    **kwargs
) -> str:
    """
    Get formatted response text for a rule.

    Args:
        rule_id: Rule identifier
        language: Language code
        **kwargs: Format parameters

    Returns:
        Formatted response string
    """
    templates = RESPONSE_TEMPLATES.get(language, RESPONSE_TEMPLATES["en"])
    template = templates.get(rule_id, f"Safety check: {rule_id}")

    try:
        return template.format(**kwargs)
    except KeyError:
        return template
