"""
Logic module - Command parsing, context management, safety rules, and checklists.

Components:
- CommandParser: Voice command parsing and intent recognition
- FlightPhase: Flight phase detection and tracking
- SpeedLimits: Aircraft V-speed limits and calculations
- SafetyRules: Safety rules evaluation engine
- ContextEngine: Integrated flight context and safety system
- Checklist: Challenge-response checklist system with verification
"""

from .parser import CommandParser
from .commands import Command, CommandRegistry

# Flight Phase Detection
from .flight_phase import (
    FlightPhase,
    FlightPhaseDetector,
    PhaseDetectionState,
    is_command_allowed_in_phase,
    get_phase_restriction,
)

# V-Speeds and Limits
from .v_speeds import (
    SpeedLimits,
    FlapSpeedLimits,
    SpeedLimitProvider,
    AircraftCategory,
    calculate_vref,
    calculate_approach_speed,
    check_speed_margin,
)

# Safety Rules Engine
from .safety_rules import (
    SafetyAction,
    SafetyRule,
    SafetyContext,
    SafetyEvaluation,
    SafetyRulesEngine,
    get_response_text,
)

# Context Engine (Main Integration)
from .context import (
    ContextEngine,
    AircraftStateSnapshot,
    SafetyCheckResult,
    FlightContext,  # Legacy compatibility
)

# Checklist System
from .checklist import (
    ChecklistEngine,
    ChecklistState,
    ItemState,
    UserResponse,
    Checklist,
    ChecklistItem,
    ChecklistResponse,
    VerificationResult,
    parse_user_response,
)

from .checklist_loader import (
    ChecklistLoader,
    ChecklistManager,
)

from .checklist_verifier import (
    ChecklistVerifier,
    create_verifier_from_sim_manager,
)

__all__ = [
    # Command System
    "CommandParser",
    "Command",
    "CommandRegistry",
    # Flight Phase
    "FlightPhase",
    "FlightPhaseDetector",
    "PhaseDetectionState",
    "is_command_allowed_in_phase",
    "get_phase_restriction",
    # V-Speeds
    "SpeedLimits",
    "FlapSpeedLimits",
    "SpeedLimitProvider",
    "AircraftCategory",
    "calculate_vref",
    "calculate_approach_speed",
    "check_speed_margin",
    # Safety Rules
    "SafetyAction",
    "SafetyRule",
    "SafetyContext",
    "SafetyEvaluation",
    "SafetyRulesEngine",
    "get_response_text",
    # Context Engine
    "ContextEngine",
    "AircraftStateSnapshot",
    "SafetyCheckResult",
    "FlightContext",
    # Checklist System
    "ChecklistEngine",
    "ChecklistState",
    "ItemState",
    "UserResponse",
    "Checklist",
    "ChecklistItem",
    "ChecklistResponse",
    "VerificationResult",
    "parse_user_response",
    "ChecklistLoader",
    "ChecklistManager",
    "ChecklistVerifier",
    "create_verifier_from_sim_manager",
]
