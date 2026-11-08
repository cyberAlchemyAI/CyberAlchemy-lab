"""Independent restoration predicates that never consume actuator success."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestorationFacts:
    gateway_candidate_target_present: bool
    gateway_candidate_weight: int
    candidate_reference_gauge: int
    candidate_containers: int
    candidate_endpoints: int
    gateway_probe_statuses: tuple[int, ...]
    direct_stable_probe_statuses: tuple[int, ...]
    stable_image_unchanged: bool
    elapsed_ms: int


@dataclass(frozen=True)
class RestorationResult:
    outcome: str
    candidate_reference_absent: bool
    probes_passed: bool
    deadline_met: bool
    findings: tuple[str, ...]
    authority_effect: str = "none"


def observe_restoration(facts: RestorationFacts) -> RestorationResult:
    findings: list[str] = []
    denominator = (
        not facts.gateway_candidate_target_present,
        facts.gateway_candidate_weight == 0,
        facts.candidate_reference_gauge == 0,
        facts.candidate_containers == 0,
        facts.candidate_endpoints == 0,
    )
    labels = ("GATEWAY_TARGET_PRESENT", "GATEWAY_WEIGHT_NONZERO", "REFERENCE_GAUGE_NONZERO", "CANDIDATE_CONTAINER_PRESENT", "CANDIDATE_ENDPOINT_PRESENT")
    findings.extend(label for passed, label in zip(denominator, labels) if not passed)
    probes = len(facts.gateway_probe_statuses) == 20 and len(facts.direct_stable_probe_statuses) == 5 and all(200 <= code < 400 for code in facts.gateway_probe_statuses + facts.direct_stable_probe_statuses)
    if not probes: findings.append("RESTORATION_PROBES_INCOMPLETE")
    if not facts.stable_image_unchanged: findings.append("STABLE_IMAGE_CHANGED")
    deadline = 0 <= facts.elapsed_ms <= 20000
    if not deadline: findings.append("ROLLBACK_DEADLINE_EXCEEDED")
    return RestorationResult("passed" if not findings else "failed", all(denominator), probes, deadline, tuple(sorted(findings)))
