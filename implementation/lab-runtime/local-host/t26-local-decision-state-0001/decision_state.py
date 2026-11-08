"""Pure local decision-state projection over exact candidate bytes.

This component has no authority, signature, publication, or persistence side
effects. A caller must authenticate the human and authorize any later effect.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal


Choice = Literal["approve", "reject", "revise", "defer"]
Status = Literal["pending", "approved", "rejected", "revision_requested", "deferred"]


class DecisionError(ValueError):
    pass


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _required(value: str, name: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise DecisionError(f"invalid {name}")
    return value


@dataclass(frozen=True)
class Target:
    member: str
    scope: str
    base_digest: str
    bundle_digest: str
    body_digest: str

    def __post_init__(self) -> None:
        for name in ("member", "scope"):
            _required(getattr(self, name), name)
        for name in ("base_digest", "bundle_digest", "body_digest"):
            value = getattr(self, name)
            if (not isinstance(value, str) or len(value) != 64
                    or any(c not in "0123456789abcdef" for c in value)):
                raise DecisionError(f"invalid {name}")

    @classmethod
    def from_bytes(
        cls, *, member: str, scope: str, base_digest: str,
        bundle_digest: str, body: bytes,
    ) -> "Target":
        if not isinstance(body, bytes):
            raise DecisionError("target body must be exact bytes")
        return cls(member, scope, base_digest, bundle_digest, digest(body))

    def verify_body(self, body: bytes) -> None:
        if not isinstance(body, bytes) or digest(body) != self.body_digest:
            raise DecisionError("target bytes changed")


@dataclass(frozen=True)
class Event:
    event_id: str
    target: Target
    choice: Choice
    successor_digest: str | None = None

    def __post_init__(self) -> None:
        _required(self.event_id, "event_id")
        if not isinstance(self.target, Target):
            raise DecisionError("invalid target")
        if self.choice not in ("approve", "reject", "revise", "defer"):
            raise DecisionError("invalid choice")
        if self.choice == "revise":
            if (not isinstance(self.successor_digest, str)
                    or len(self.successor_digest) != 64
                    or any(c not in "0123456789abcdef" for c in self.successor_digest)
                    or self.successor_digest == self.target.body_digest):
                raise DecisionError("revise requires a distinct exact successor digest")
        elif self.successor_digest is not None:
            raise DecisionError("successor digest only applies to revise")


class DecisionState:
    def __init__(self) -> None:
        self._events: dict[str, Event] = {}
        self._event_results: dict[str, Status] = {}
        self._states: dict[Target, Status] = {}
        self._revisions: dict[Target, str] = {}

    def status(self, target: Target) -> Status:
        return self._states.get(target, "pending")

    def successor(self, target: Target) -> str | None:
        return self._revisions.get(target)

    def apply(self, event: Event, *, body: bytes) -> Status:
        """Project an exact event; return state or refuse a conflicting replay."""
        if not isinstance(event, Event):
            raise DecisionError("invalid event")
        event.target.verify_body(body)
        previous_event = self._events.get(event.event_id)
        if previous_event is not None:
            if previous_event != event:
                raise DecisionError("event id reused with different decision")
            return self._event_results[event.event_id]
        state = self.status(event.target)
        if state in ("approved", "rejected", "revision_requested"):
            raise DecisionError("target already has a final disposition")
        new_state: Status = {
            "approve": "approved", "reject": "rejected",
            "revise": "revision_requested", "defer": "deferred",
        }[event.choice]
        self._events[event.event_id] = event
        self._event_results[event.event_id] = new_state
        self._states[event.target] = new_state
        if event.choice == "revise":
            if event.successor_digest is None:
                raise DecisionError("missing successor digest")
            self._revisions[event.target] = event.successor_digest
        return new_state

    def can_import(self, target: Target, *, body: bytes) -> bool:
        target.verify_body(body)
        return self.status(target) == "approved"
