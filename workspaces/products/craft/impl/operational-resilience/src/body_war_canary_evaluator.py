"""Fail-closed pure evaluation of frozen canary telemetry."""

from __future__ import annotations

from .body_war_canary_contracts import EvaluationResult, TelemetryWindow, WorkloadSummary
from .body_war_canary_workload import validate_workload


def evaluate_canary(window: TelemetryWindow, workload: WorkloadSummary) -> EvaluationResult:
    candidate_total = window.candidate_good + window.candidate_bad
    stable_total = window.stable_good + window.stable_bad
    candidate_rate = window.candidate_bad / candidate_total if candidate_total else 0.0
    stable_rate = window.stable_bad / stable_total if stable_total else 0.0
    workload_valid, workload_reasons = validate_workload(workload)
    if not workload_valid:
        return EvaluationResult("invalid", "invalid", "safety-rollback", candidate_total, stable_total, candidate_rate, stable_rate, "invalid", workload_reasons)
    invalid_counts = any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in (window.candidate_good, window.candidate_bad, window.stable_good, window.stable_bad))
    if invalid_counts or window.counter_reset:
        return EvaluationResult("invalid", "invalid", "safety-rollback", candidate_total, stable_total, candidate_rate, stable_rate, "invalid", ("TELEMETRY_COUNTER_INVALID",))
    incomplete: list[str] = []
    if candidate_total < 20: incomplete.append("CANDIDATE_DENOMINATOR_INSUFFICIENT")
    if stable_total < 180: incomplete.append("STABLE_DENOMINATOR_INSUFFICIENT")
    if not window.target_up: incomplete.append("PROMETHEUS_TARGET_DOWN")
    if not window.fault_active_all_samples: incomplete.append("FAULT_GAUGE_INCOMPLETE")
    if not window.candidate_reference_present: incomplete.append("CANDIDATE_REFERENCE_GAUGE_MISSING")
    if not window.samples_in_phase: incomplete.append("SAMPLE_OUTSIDE_PHASE")
    if window.duplicate_series: incomplete.append("DUPLICATE_SERIES")
    if window.stale_samples: incomplete.append("STALE_SAMPLES")
    if window.nan_present: incomplete.append("NON_FINITE_SAMPLE")
    if window.query_error: incomplete.append("PROMETHEUS_QUERY_ERROR")
    if incomplete:
        return EvaluationResult("inconclusive", "inconclusive", "safety-rollback", candidate_total, stable_total, candidate_rate, stable_rate, "incomplete", tuple(sorted(incomplete)))
    if stable_rate > 0.01:
        return EvaluationResult("failed", "unacceptable", "safety-rollback", candidate_total, stable_total, candidate_rate, stable_rate, "complete", ("STABLE_HARM",))
    if candidate_rate >= 0.20:
        return EvaluationResult("passed", "unacceptable", "rollback", candidate_total, stable_total, candidate_rate, stable_rate, "complete", ())
    return EvaluationResult("passed", "acceptable", "continue", candidate_total, stable_total, candidate_rate, stable_rate, "complete", ())
