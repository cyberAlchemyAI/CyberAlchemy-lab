"""Ordered rollback plans over injected argv runners."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class RollbackAction:
    action_id: str
    argv: tuple[str, ...]
    effect: bool


def rollback_plan(project_name: str, expected_generation: int) -> tuple[RollbackAction, ...]:
    if not project_name.startswith("orodi-bw-") or expected_generation < 0:
        raise ValueError("ROLLBACK_IDENTITY_INVALID")
    return (
        RollbackAction("remove-gateway-candidate-reference", ("gateway-control", "rollback", "--expected-generation", str(expected_generation)), True),
        RollbackAction("reconcile-gateway-state", ("gateway-control", "state"), False),
        RollbackAction("remove-candidate-container", ("docker", "compose", "--project-name", project_name, "rm", "--stop", "--force", "candidate"), True),
    )


def validate_rollback_order(actions: tuple[RollbackAction, ...]) -> None:
    ids = [action.action_id for action in actions]
    if ids != ["remove-gateway-candidate-reference", "reconcile-gateway-state", "remove-candidate-container"]:
        raise ValueError("ROLLBACK_ACTION_ORDER_INVALID")
    if any(isinstance(action.argv, str) for action in actions):
        raise ValueError("ROLLBACK_SHELL_TEXT_FORBIDDEN")


def execute_rollback(actions: tuple[RollbackAction, ...], runner: Callable[[tuple[str, ...]], int]) -> tuple[tuple[str, int], ...]:
    validate_rollback_order(actions)
    results: list[tuple[str, int]] = []
    for action in actions:
        code = runner(action.argv)
        results.append((action.action_id, code))
        if code != 0:
            break
    return tuple(results)
