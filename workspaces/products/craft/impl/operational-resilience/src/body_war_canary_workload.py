"""Deterministic no-I/O workload scheduling and validity classification."""

from __future__ import annotations

import math

from .body_war_canary_contracts import WorkloadProfile, WorkloadSummary


def build_schedule(start_monotonic: float, duration_seconds: int, profile: WorkloadProfile = WorkloadProfile()) -> tuple[float, ...]:
    if not math.isfinite(start_monotonic) or start_monotonic < 0:
        raise ValueError("WORKLOAD_MONOTONIC_START_INVALID")
    if not isinstance(duration_seconds, int) or duration_seconds <= 0:
        raise ValueError("WORKLOAD_DURATION_INVALID")
    total = duration_seconds * profile.requests_per_second
    if total > profile.max_scheduled:
        raise ValueError("WORKLOAD_SCHEDULE_CEILING_EXCEEDED")
    interval = 1.0 / profile.requests_per_second
    return tuple(start_monotonic + index * interval for index in range(total))


def validate_workload(summary: WorkloadSummary, profile: WorkloadProfile = WorkloadProfile()) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    integers = (summary.scheduled, summary.completed, summary.classified, summary.max_inflight)
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in integers):
        reasons.append("WORKLOAD_COUNTER_INVALID")
    if summary.scheduled > profile.max_scheduled:
        reasons.append("WORKLOAD_SCHEDULE_CEILING_EXCEEDED")
    if summary.max_inflight > profile.hard_inflight:
        reasons.append("WORKLOAD_HARD_INFLIGHT_CEILING_EXCEEDED")
    elif summary.max_inflight > profile.max_inflight:
        reasons.append("WORKLOAD_VALID_INFLIGHT_CEILING_EXCEEDED")
    if summary.scheduled == 0 or summary.completed / summary.scheduled < profile.minimum_completion_ratio:
        reasons.append("WORKLOAD_COMPLETION_RATIO_INSUFFICIENT")
    if summary.classified != summary.completed:
        reasons.append("WORKLOAD_CLASSIFICATION_INCOMPLETE")
    if not math.isfinite(summary.p99_issue_lateness_ms) or summary.p99_issue_lateness_ms > profile.maximum_p99_issue_lateness_ms:
        reasons.append("WORKLOAD_ISSUE_LATENESS_EXCEEDED")
    if summary.clock_reversed:
        reasons.append("WORKLOAD_CLOCK_REVERSED")
    return (not reasons, tuple(sorted(reasons)))
