"""Pure typed values shared by the host-side canary implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Outcome = Literal["passed", "failed", "invalid", "inconclusive", "blocked"]
Decision = Literal["rollback", "continue", "safety-rollback"]


@dataclass(frozen=True)
class WorkloadProfile:
    requests_per_second: int = 10
    request_timeout_ms: int = 1000
    max_inflight: int = 10
    hard_inflight: int = 20
    max_scheduled: int = 900
    minimum_completion_ratio: float = 0.99
    maximum_p99_issue_lateness_ms: int = 100


@dataclass(frozen=True)
class WorkloadSummary:
    scheduled: int
    completed: int
    classified: int
    max_inflight: int
    p99_issue_lateness_ms: float
    clock_reversed: bool = False


@dataclass(frozen=True)
class TelemetryWindow:
    candidate_good: int
    candidate_bad: int
    stable_good: int
    stable_bad: int
    target_up: bool
    fault_active_all_samples: bool
    candidate_reference_present: bool
    samples_in_phase: bool
    duplicate_series: bool = False
    stale_samples: bool = False
    nan_present: bool = False
    counter_reset: bool = False
    query_error: bool = False


@dataclass(frozen=True)
class EvaluationResult:
    outcome: Outcome
    candidate_assessment: Literal["unacceptable", "acceptable", "inconclusive", "invalid"]
    decision: Decision
    candidate_total: int
    stable_total: int
    candidate_bad_rate: float
    stable_bad_rate: float
    telemetry_completeness: Literal["complete", "incomplete", "invalid"]
    reasons: tuple[str, ...]
    authority_effect: Literal["none"] = "none"
