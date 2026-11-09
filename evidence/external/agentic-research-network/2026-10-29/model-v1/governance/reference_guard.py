"""Non-authorizing, deterministic decision-rights assessment for synthetic inputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STAGES = ("proposer", "reviewers", "approvers", "executors")


@dataclass(frozen=True)
class Assessment:
    ok: bool
    reasons: tuple[str, ...]
    authority_effect: str = "none"


class Guard:
    def __init__(self, actors: dict, profile: dict):
        self.actors = actors
        self.profile = profile
        self.roles = {role["role_id"]: role for role in actors["roles"]}
        self.actions = {action["action_id"]: action for action in profile["actions"]}

    @classmethod
    def load(cls) -> "Guard":
        return cls(json.loads((ROOT / "actors.json").read_text()),
                   json.loads((ROOT / "decision-rights.json").read_text()))

    def assess(self, request: dict, assignments: list[dict]) -> Assessment:
        if not isinstance(request, dict) or not isinstance(assignments, list) or not all(
                isinstance(item, dict) for item in assignments):
            return Assessment(False, ("invalid-request",))
        errors: list[str] = []

        def deny(condition: bool, code: str) -> None:
            if not condition:
                errors.append(code)

        action = self.actions.get(request.get("action_id"))
        if not action:
            return Assessment(False, ("unknown-action",))
        deny(request.get("profile_version") == self.profile["version"], "profile-version-mismatch")
        deny(request.get("scope_ref") == self.profile["project_ref"], "scope-mismatch")
        now = request.get("now")
        proposed_at = request.get("proposed_at")
        if type(now) is not int or type(proposed_at) is not int:
            return Assessment(False, ("invalid-time",))
        deny(now >= proposed_at + action["min_delay_seconds"], "decision-delay-open")
        if action["prospective_only"]:
            deny(type(request.get("effective_at")) is int and
                 request["effective_at"] >= now, "retrospective-effect")
        if action["requires_challenge_close"]:
            deny(request.get("challenge_closed") is True, "challenge-open")
        if action["max_duration_seconds"] is not None:
            duration = request.get("duration_seconds")
            deny(type(duration) is int and 0 < duration <= action["max_duration_seconds"],
                 "invalid-pause-duration")

        evidence = request.get("evidence", {})
        if not isinstance(evidence, dict):
            return Assessment(False, ("invalid-evidence",))
        for key in action["required_evidence"]:
            value = evidence.get(key)
            deny(isinstance(value, str) and bool(value) and not value.startswith("open:"),
                 f"missing-evidence:{key}")

        participants = {"proposer": [request.get("proposer")],
                        "reviewers": request.get("reviewers", []),
                        "approvers": request.get("approvers", []),
                        "executors": request.get("executors", [])}
        for stage, people in participants.items():
            valid = isinstance(people, list) and all(isinstance(x, str) and x for x in people)
            deny(valid, f"invalid-{stage}")
            if valid:
                deny(len(people) == len(set(people)), f"duplicate-{stage}")
        if any(code.startswith("invalid-") for code in errors):
            return Assessment(False, tuple(dict.fromkeys(errors)))

        active: dict[str, set[str]] = {}
        controllers: dict[str, str] = {}
        for item in assignments:
            principal, role, scope = item.get("principal_ref"), item.get("role_ref"), item.get("scope_ref")
            if not principal or not role or role not in self.roles:
                errors.append("invalid-assignment")
                continue
            if (scope != request.get("scope_ref") or item.get("state") != "active" or
                    type(item.get("valid_from")) is not int or type(item.get("valid_until")) is not int or
                    not (item["valid_from"] <= now < item["valid_until"])):
                continue
            kind = item.get("actor_kind")
            if kind not in self.roles[role]["eligible_actor_kinds"]:
                errors.append("ineligible-actor-kind")
                continue
            if kind == "agent-operated" and not item.get("delegation_ref"):
                errors.append("missing-agent-delegation")
                continue
            controller = item.get("controller_ref")
            if not controller:
                errors.append("missing-controller")
                continue
            if principal in controllers and controllers[principal] != controller:
                errors.append("inconsistent-controller")
                continue
            controllers[principal] = controller
            active.setdefault(principal, set()).add(role)

        for stage, people in participants.items():
            for principal in people:
                deny(principal in active, f"unassigned-or-expired:{stage}")
                if stage in ("reviewers", "approvers", "executors"):
                    kinds = {item.get("actor_kind") for item in assignments
                             if item.get("principal_ref") == principal and
                             item.get("role_ref") in active.get(principal, set())}
                    deny("agent-operated" not in kinds, f"agent-decision-seat:{stage}")
            stage_controllers = [controllers.get(x) for x in people if x in controllers]
            deny(len(stage_controllers) == len(set(stage_controllers)), f"common-control:{stage}")

        proposer = request.get("proposer")
        deny(bool(active.get(proposer, set()) & set(action["proposer_roles"])),
             "proposer-role-missing")

        for stage, field in (("reviewers", "reviewer_quorum"),
                             ("approvers", "approver_quorum"),
                             ("executors", "executor_quorum")):
            slots = [entry["role_ref"] for entry in action[field]
                     for _ in range(entry["count"])]
            people = participants[stage]
            deny(len(people) == len(slots), f"quorum-size:{stage}")
            if len(people) == len(slots):
                deny(self._match_roles(people, slots, active), f"quorum-role:{stage}")

        conflicted_refs = request.get("conflicted_principals", [])
        original_refs = request.get("original_decision_principals", [])
        if not all(isinstance(refs, list) and all(isinstance(x, str) for x in refs)
                   for refs in (conflicted_refs, original_refs)):
            return Assessment(False, ("invalid-conflict-or-panel-refs",))
        conflicted = set(conflicted_refs)
        original = set(original_refs)
        for stage in ("reviewers", "approvers", "executors"):
            deny(not (set(participants[stage]) & conflicted), f"conflict:{stage}")
        if request["action_id"] == "appeal.resolve":
            for stage in STAGES:
                deny(not (set(participants[stage]) & original), f"original-panel:{stage}")

        subject = request.get("subject_principal")
        for stage in action["subject_excluded_stages"]:
            deny(subject not in participants[stage], f"subject-in-{stage}")
            subject_controller = controllers.get(subject)
            if subject_controller:
                deny(subject_controller not in {controllers.get(x) for x in participants[stage]},
                     f"subject-control-in-{stage}")
        for left, right in action["separation_pairs"]:
            left_controllers = {controllers.get(x) for x in participants[left]}
            right_controllers = {controllers.get(x) for x in participants[right]}
            deny(not (left_controllers & right_controllers), f"separation:{left}:{right}")

        return Assessment(not errors, tuple(dict.fromkeys(errors)))

    @staticmethod
    def _match_roles(people: list[str], slots: list[str], active: dict[str, set[str]]) -> bool:
        if not slots:
            return not people
        role = slots[0]
        for index, principal in enumerate(people):
            if role in active.get(principal, set()) and Guard._match_roles(
                    people[:index] + people[index + 1:], slots[1:], active):
                return True
        return False


if __name__ == "__main__":
    guard = Guard.load()
    print(f"Loaded {len(guard.roles)} candidate roles and {len(guard.actions)} action routes; no authority granted.")
