"""Finite host-controller transitions with no full-trial retry."""

from __future__ import annotations

STATES = ("not-started", "preflight-valid", "stable-proved", "workload-valid", "candidate-exposed", "fault-active", "canary-decided", "rollback-triggered", "rollback-actuated", "stable-restored", "teardown-verified", "evidence-projected", "completed")


def transition(current: str, requested: str) -> str:
    if current not in STATES or requested not in STATES:
        raise ValueError("CONTROLLER_STATE_UNKNOWN")
    if STATES.index(requested) != STATES.index(current) + 1:
        raise ValueError("CONTROLLER_TRANSITION_NON_SEQUENTIAL")
    return requested


def safety_route(current: str) -> tuple[str, ...]:
    if current in ("not-started", "preflight-valid"):
        return ("blocked-no-effect",)
    if current in ("teardown-verified", "evidence-projected", "completed"):
        return ("stop",)
    return ("rollback-triggered", "rollback-actuated", "stable-restored", "teardown-verified")


def retry_allowed(operation: str, intended_effect_absent: bool, attempts: int) -> bool:
    if operation in ("full-trial", "fault-activation"):
        return False
    if operation == "observation":
        return attempts < 1
    if operation == "cleanup":
        return attempts < 1
    return intended_effect_absent and attempts < 1
