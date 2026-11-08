"""Python State Machine candidate: a pure enum transition decision."""
from dataclasses import dataclass
from enum import Enum

class SettlementState(str, Enum):
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"

class SettlementTrigger(str, Enum):
    CONFIRM = "confirm"
    REJECT = "reject"

@dataclass(frozen=True)
class TransitionDecision:
    accepted: bool
    next_state: SettlementState | None
    guard_ids: tuple[str, ...]
    effect_intents: tuple[str, ...]

def transition_settlement_lifecycle(state: SettlementState, trigger: SettlementTrigger) -> TransitionDecision:
    if state is SettlementState.PENDING and trigger is SettlementTrigger.CONFIRM:
        return TransitionDecision(True, SettlementState.SETTLED, ("can-settle",), ("persist-settlement", "append-settlement-created"))
    if state is SettlementState.PENDING and trigger is SettlementTrigger.REJECT:
        return TransitionDecision(True, SettlementState.FAILED, ("can-settle",), ("record-rejection",))
    return TransitionDecision(False, None, (), ())

SETTLEMENT_TRANSITIONS = (
    ("pending", "confirm", "settled", ("can-settle",), ("persist-settlement", "append-settlement-created")),
    ("pending", "reject", "failed", ("can-settle",), ("record-rejection",)),
)
