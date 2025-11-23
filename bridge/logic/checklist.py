"""
Smart Flight Deck Companion - Checklist System
Hybrid challenge-response checklist with SimConnect/WASM verification.
"""

import logging
import time
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class ChecklistState(Enum):
    """Checklist execution states."""
    IDLE = auto()       # No checklist active
    RUNNING = auto()    # Checklist active, reading item
    WAITING = auto()    # Waiting for user response
    PAUSED = auto()     # Temporarily paused
    COMPLETE = auto()   # Checklist finished
    FAILED = auto()     # Critical item failed


class ItemState(Enum):
    """Individual checklist item states."""
    PENDING = auto()    # Not yet read
    ACTIVE = auto()     # Currently active item
    VERIFIED = auto()   # Verification passed
    FAILED = auto()     # Verification failed
    SKIPPED = auto()    # User skipped
    OVERRIDE = auto()   # User overrode warning


class VerificationType(Enum):
    """Types of verification."""
    SIMVAR = "simvar"       # SimConnect variable
    LVAR = "lvar"           # WASM LVAR
    MANUAL = "manual"       # No automatic verification
    COMBINED = "combined"   # Multiple conditions


class ConditionType(Enum):
    """Verification condition types."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN_RANGE = "in_range"
    CONTAINS = "contains"


class ActionType(Enum):
    """Action types for checklist items."""
    NONE = "none"
    SIMCONNECT = "simconnect"
    LVAR = "lvar"
    KEY = "key"


class UserResponse(Enum):
    """User response types."""
    CHECK = "check"
    SKIP = "skip"
    OVERRIDE = "override"
    REPEAT = "repeat"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class VerificationConfig:
    """Configuration for item verification."""
    type: VerificationType = VerificationType.MANUAL
    variable: Optional[str] = None
    condition: ConditionType = ConditionType.EQUALS
    value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    conditions: List['VerificationConfig'] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> 'VerificationConfig':
        """Create from dictionary."""
        if not data:
            return cls(type=VerificationType.MANUAL)

        return cls(
            type=VerificationType(data.get("type", "manual")),
            variable=data.get("variable"),
            condition=ConditionType(data.get("condition", "equals")),
            value=data.get("value"),
            min_value=data.get("min"),
            max_value=data.get("max"),
            conditions=[cls.from_dict(c) for c in data.get("conditions", [])],
        )


@dataclass
class ActionConfig:
    """Configuration for item action."""
    type: ActionType = ActionType.NONE
    event: Optional[str] = None
    variable: Optional[str] = None
    value: Any = None
    key: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'ActionConfig':
        """Create from dictionary."""
        if not data:
            return cls()

        return cls(
            type=ActionType(data.get("type", "none")),
            event=data.get("event"),
            variable=data.get("variable"),
            value=data.get("value"),
            key=data.get("key"),
        )


@dataclass
class ChecklistItem:
    """Single checklist item."""
    id: str
    challenge: str
    expected_response: str
    verification: VerificationConfig
    action: ActionConfig
    critical: bool = False
    warning_if_fail: Optional[str] = None
    notes: Optional[str] = None

    # Runtime state
    state: ItemState = ItemState.PENDING
    actual_value: Any = None
    verification_message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'ChecklistItem':
        """Create from dictionary."""
        return cls(
            id=data["id"],
            challenge=data["challenge"],
            expected_response=data["expected_response"],
            verification=VerificationConfig.from_dict(data.get("verification", {})),
            action=ActionConfig.from_dict(data.get("action", {})),
            critical=data.get("critical", False),
            warning_if_fail=data.get("warning_if_fail"),
            notes=data.get("notes"),
        )

    def reset(self):
        """Reset item to pending state."""
        self.state = ItemState.PENDING
        self.actual_value = None
        self.verification_message = None


@dataclass
class Checklist:
    """Complete checklist definition."""
    id: str
    name: str
    phase: str
    items: List[ChecklistItem]

    # Metadata
    aircraft: str = ""
    version: str = "1.0"

    @classmethod
    def from_dict(cls, checklist_id: str, data: Dict, aircraft: str = "") -> 'Checklist':
        """Create from dictionary."""
        return cls(
            id=checklist_id,
            name=data["name"],
            phase=data.get("phase", "UNKNOWN"),
            items=[ChecklistItem.from_dict(item) for item in data.get("items", [])],
            aircraft=aircraft,
        )

    def reset(self):
        """Reset all items to pending."""
        for item in self.items:
            item.reset()

    @property
    def total_items(self) -> int:
        """Total number of items."""
        return len(self.items)

    @property
    def completed_items(self) -> int:
        """Number of completed items."""
        return sum(1 for item in self.items
                   if item.state in [ItemState.VERIFIED, ItemState.SKIPPED, ItemState.OVERRIDE])

    @property
    def progress_percent(self) -> float:
        """Completion percentage."""
        if self.total_items == 0:
            return 100.0
        return (self.completed_items / self.total_items) * 100


@dataclass
class VerificationResult:
    """Result of item verification."""
    success: bool
    actual_value: Any = None
    expected_value: Any = None
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChecklistResponse:
    """Response from checklist operations."""
    success: bool
    state: ChecklistState
    message: str
    tts_text: str

    # Current item info
    current_item: Optional[Dict] = None

    # Verification info
    verified: Optional[bool] = None
    verification_message: Optional[str] = None

    # Progress
    progress: float = 0.0
    items_remaining: int = 0


# =============================================================================
# Checklist Engine
# =============================================================================

class ChecklistEngine:
    """
    Main checklist execution engine.

    Handles state machine, item progression, and verification coordination.
    """

    # Timeout settings (seconds)
    RESPONSE_TIMEOUT = 10.0
    MAX_RETRIES = 3

    def __init__(self):
        self._state = ChecklistState.IDLE
        self._active_checklist: Optional[Checklist] = None
        self._current_index: int = 0
        self._retry_count: int = 0
        self._last_challenge_time: float = 0.0

        # Callbacks
        self._on_state_change: Optional[Callable[[ChecklistState, ChecklistState], None]] = None
        self._on_item_complete: Optional[Callable[[ChecklistItem, ItemState], None]] = None
        self._verifier: Optional[Callable[[ChecklistItem], VerificationResult]] = None

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def state(self) -> ChecklistState:
        """Current checklist state."""
        return self._state

    @property
    def is_active(self) -> bool:
        """Whether a checklist is currently active."""
        return self._state in [ChecklistState.RUNNING, ChecklistState.WAITING, ChecklistState.PAUSED]

    @property
    def active_checklist(self) -> Optional[Checklist]:
        """Currently active checklist."""
        return self._active_checklist

    @property
    def current_item(self) -> Optional[ChecklistItem]:
        """Current checklist item."""
        if not self._active_checklist or self._current_index >= len(self._active_checklist.items):
            return None
        return self._active_checklist.items[self._current_index]

    @property
    def progress(self) -> float:
        """Current progress percentage."""
        if not self._active_checklist:
            return 0.0
        return self._active_checklist.progress_percent

    @property
    def items_remaining(self) -> int:
        """Number of items remaining."""
        if not self._active_checklist:
            return 0
        return self._active_checklist.total_items - self._active_checklist.completed_items

    # =========================================================================
    # Configuration
    # =========================================================================

    def set_verifier(self, verifier: Callable[[ChecklistItem], VerificationResult]):
        """Set verification callback."""
        self._verifier = verifier

    def on_state_change(self, callback: Callable[[ChecklistState, ChecklistState], None]):
        """Register state change callback."""
        self._on_state_change = callback

    def on_item_complete(self, callback: Callable[[ChecklistItem, ItemState], None]):
        """Register item completion callback."""
        self._on_item_complete = callback

    # =========================================================================
    # Checklist Operations
    # =========================================================================

    def start(self, checklist: Checklist) -> ChecklistResponse:
        """
        Start a new checklist.

        Args:
            checklist: Checklist to start

        Returns:
            ChecklistResponse with first item
        """
        if self.is_active:
            return ChecklistResponse(
                success=False,
                state=self._state,
                message="A checklist is already active. Cancel it first.",
                tts_text="A checklist is already running. Say cancel checklist to stop it.",
            )

        # Reset and activate
        checklist.reset()
        self._active_checklist = checklist
        self._current_index = 0
        self._retry_count = 0
        self._transition_to(ChecklistState.RUNNING)

        logger.info(f"Started checklist: {checklist.name}")

        # Read first item
        return self._read_current_item(is_first=True)

    def respond(self, response: UserResponse) -> ChecklistResponse:
        """
        Process user response to current item.

        Args:
            response: User response type

        Returns:
            ChecklistResponse with result and next item
        """
        if not self.is_active:
            return ChecklistResponse(
                success=False,
                state=self._state,
                message="No active checklist",
                tts_text="No checklist is running.",
            )

        if self._state == ChecklistState.PAUSED:
            return ChecklistResponse(
                success=False,
                state=self._state,
                message="Checklist is paused",
                tts_text="Checklist is paused. Say resume to continue.",
            )

        item = self.current_item
        if not item:
            return self._complete_checklist()

        # Handle response type
        if response == UserResponse.REPEAT:
            return self._read_current_item()
        elif response == UserResponse.SKIP:
            return self._skip_item()
        elif response == UserResponse.OVERRIDE:
            return self._override_item()
        elif response == UserResponse.CHECK:
            return self._verify_and_advance()

        return ChecklistResponse(
            success=False,
            state=self._state,
            message="Unknown response",
            tts_text="I didn't understand. Say check, skip, or repeat.",
        )

    def pause(self) -> ChecklistResponse:
        """Pause the active checklist."""
        if not self.is_active:
            return ChecklistResponse(
                success=False,
                state=self._state,
                message="No active checklist",
                tts_text="No checklist to pause.",
            )

        self._transition_to(ChecklistState.PAUSED)

        return ChecklistResponse(
            success=True,
            state=self._state,
            message="Checklist paused",
            tts_text=f"{self._active_checklist.name} checklist paused.",
            progress=self.progress,
            items_remaining=self.items_remaining,
        )

    def resume(self) -> ChecklistResponse:
        """Resume a paused checklist."""
        if self._state != ChecklistState.PAUSED:
            return ChecklistResponse(
                success=False,
                state=self._state,
                message="Checklist is not paused",
                tts_text="Checklist is not paused.",
            )

        self._transition_to(ChecklistState.WAITING)
        return self._read_current_item()

    def cancel(self) -> ChecklistResponse:
        """Cancel the active checklist."""
        if not self.is_active and self._state != ChecklistState.PAUSED:
            return ChecklistResponse(
                success=False,
                state=self._state,
                message="No active checklist",
                tts_text="No checklist to cancel.",
            )

        checklist_name = self._active_checklist.name if self._active_checklist else "Checklist"

        self._reset()

        return ChecklistResponse(
            success=True,
            state=self._state,
            message="Checklist cancelled",
            tts_text=f"{checklist_name} checklist cancelled.",
        )

    def get_status(self) -> ChecklistResponse:
        """Get current checklist status."""
        if not self._active_checklist:
            return ChecklistResponse(
                success=True,
                state=self._state,
                message="No active checklist",
                tts_text="No checklist is running.",
            )

        item = self.current_item
        item_info = None
        if item:
            item_info = {
                "id": item.id,
                "challenge": item.challenge,
                "expected": item.expected_response,
                "critical": item.critical,
            }

        return ChecklistResponse(
            success=True,
            state=self._state,
            message=f"{self._active_checklist.name}: {self._active_checklist.completed_items}/{self._active_checklist.total_items}",
            tts_text=f"{self._active_checklist.name} checklist. {self.items_remaining} items remaining.",
            current_item=item_info,
            progress=self.progress,
            items_remaining=self.items_remaining,
        )

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _transition_to(self, new_state: ChecklistState):
        """Transition to new state."""
        old_state = self._state
        self._state = new_state

        if self._on_state_change and old_state != new_state:
            self._on_state_change(old_state, new_state)

    def _reset(self):
        """Reset engine to idle state."""
        self._active_checklist = None
        self._current_index = 0
        self._retry_count = 0
        self._transition_to(ChecklistState.IDLE)

    def _read_current_item(self, is_first: bool = False) -> ChecklistResponse:
        """Read the current checklist item."""
        item = self.current_item
        if not item:
            return self._complete_checklist()

        item.state = ItemState.ACTIVE
        self._last_challenge_time = time.time()
        self._transition_to(ChecklistState.WAITING)

        # Build TTS text
        if is_first:
            tts_text = f"{self._active_checklist.name} checklist. {item.challenge}."
        else:
            tts_text = f"{item.challenge}."

        return ChecklistResponse(
            success=True,
            state=self._state,
            message=f"Current item: {item.challenge}",
            tts_text=tts_text,
            current_item={
                "id": item.id,
                "challenge": item.challenge,
                "expected": item.expected_response,
                "critical": item.critical,
                "notes": item.notes,
            },
            progress=self.progress,
            items_remaining=self.items_remaining,
        )

    def _verify_and_advance(self) -> ChecklistResponse:
        """Verify current item and advance to next."""
        item = self.current_item
        if not item:
            return self._complete_checklist()

        # Perform verification
        result = self._verify_item(item)

        if result.success:
            item.state = ItemState.VERIFIED
            item.actual_value = result.actual_value

            if self._on_item_complete:
                self._on_item_complete(item, ItemState.VERIFIED)

            return self._advance_to_next(
                prefix_tts=f"{item.expected_response}.",
            )
        else:
            # Verification failed
            item.state = ItemState.FAILED
            item.actual_value = result.actual_value
            item.verification_message = result.message
            self._retry_count += 1

            if item.critical:
                # Critical item - don't auto-advance
                warning = item.warning_if_fail or result.message or "Verification failed"
                return ChecklistResponse(
                    success=True,
                    state=self._state,
                    message=f"Verification failed: {warning}",
                    tts_text=f"{item.challenge} not verified. {warning}. Say override to continue or check to retry.",
                    current_item={
                        "id": item.id,
                        "challenge": item.challenge,
                        "expected": item.expected_response,
                        "critical": True,
                    },
                    verified=False,
                    verification_message=warning,
                    progress=self.progress,
                    items_remaining=self.items_remaining,
                )
            else:
                # Non-critical - warn and continue
                return self._advance_to_next(
                    prefix_tts=f"{item.challenge} not verified, but continuing. {result.message or ''}",
                    verified=False,
                    verification_message=result.message,
                )

    def _verify_item(self, item: ChecklistItem) -> VerificationResult:
        """Verify a single item."""
        if item.verification.type == VerificationType.MANUAL:
            # Manual verification always succeeds
            return VerificationResult(success=True, message="Manual verification")

        if self._verifier:
            return self._verifier(item)

        # No verifier set - assume success
        return VerificationResult(success=True, message="No verifier configured")

    def _skip_item(self) -> ChecklistResponse:
        """Skip current item."""
        item = self.current_item
        if not item:
            return self._complete_checklist()

        item.state = ItemState.SKIPPED

        if self._on_item_complete:
            self._on_item_complete(item, ItemState.SKIPPED)

        return self._advance_to_next(
            prefix_tts=f"{item.challenge} skipped.",
        )

    def _override_item(self) -> ChecklistResponse:
        """Override failed item verification."""
        item = self.current_item
        if not item:
            return self._complete_checklist()

        if item.state != ItemState.FAILED:
            return ChecklistResponse(
                success=False,
                state=self._state,
                message="Nothing to override",
                tts_text="Nothing to override.",
            )

        item.state = ItemState.OVERRIDE

        if self._on_item_complete:
            self._on_item_complete(item, ItemState.OVERRIDE)

        return self._advance_to_next(
            prefix_tts=f"{item.challenge} override accepted.",
        )

    def _advance_to_next(
        self,
        prefix_tts: str,
        verified: Optional[bool] = None,
        verification_message: Optional[str] = None,
    ) -> ChecklistResponse:
        """Advance to next item."""
        self._current_index += 1
        self._retry_count = 0

        next_item = self.current_item
        if not next_item:
            return self._complete_checklist(prefix_tts=prefix_tts)

        next_item.state = ItemState.ACTIVE
        self._last_challenge_time = time.time()

        return ChecklistResponse(
            success=True,
            state=self._state,
            message=f"Next: {next_item.challenge}",
            tts_text=f"{prefix_tts} {next_item.challenge}.",
            current_item={
                "id": next_item.id,
                "challenge": next_item.challenge,
                "expected": next_item.expected_response,
                "critical": next_item.critical,
            },
            verified=verified,
            verification_message=verification_message,
            progress=self.progress,
            items_remaining=self.items_remaining,
        )

    def _complete_checklist(
        self,
        prefix_tts: str = "",
    ) -> ChecklistResponse:
        """Complete the checklist."""
        checklist = self._active_checklist
        name = checklist.name if checklist else "Checklist"

        self._transition_to(ChecklistState.COMPLETE)

        # Count results
        verified_count = sum(1 for item in checklist.items if item.state == ItemState.VERIFIED)
        skipped_count = sum(1 for item in checklist.items if item.state == ItemState.SKIPPED)
        overridden_count = sum(1 for item in checklist.items if item.state == ItemState.OVERRIDE)

        logger.info(f"Checklist complete: {name} - {verified_count} verified, {skipped_count} skipped, {overridden_count} overridden")

        # Reset for next use
        self._active_checklist = None
        self._current_index = 0
        self._transition_to(ChecklistState.IDLE)

        tts_text = f"{prefix_tts} {name} checklist complete.".strip()

        return ChecklistResponse(
            success=True,
            state=ChecklistState.COMPLETE,
            message=f"{name} complete",
            tts_text=tts_text,
            progress=100.0,
            items_remaining=0,
        )


# =============================================================================
# Convenience Functions
# =============================================================================

def parse_user_response(text: str) -> Optional[UserResponse]:
    """
    Parse user text into a UserResponse.

    Args:
        text: User's spoken/typed response

    Returns:
        UserResponse or None if not recognized
    """
    text_lower = text.lower().strip()

    # Check responses
    check_words = ["check", "checked", "set", "on", "off", "confirm", "confirmed"]
    if any(word in text_lower for word in check_words):
        return UserResponse.CHECK

    # Skip responses
    skip_words = ["skip", "next"]
    if any(word in text_lower for word in skip_words):
        return UserResponse.SKIP

    # Override responses
    override_words = ["override"]
    if any(word in text_lower for word in override_words):
        return UserResponse.OVERRIDE

    # Repeat responses
    repeat_words = ["repeat", "again", "what"]
    if any(word in text_lower for word in repeat_words):
        return UserResponse.REPEAT

    return None
