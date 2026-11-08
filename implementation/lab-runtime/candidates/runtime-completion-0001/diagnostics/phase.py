"""C03/R05 phase budget decisions and observations for an already guarded caller.

This module never starts a worker or substitutes a clock, verifier, or callback.
The caller must still perform its original currentness, containment, entry,
exit, and effect guards at every required boundary. A selected budget is only
an upper limit; it is not a measurement or an authority grant.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import time

from lab_contracts.codec import need
from lab_contracts.validation import instant, validate
from lab_selectors.chains import phase_remaining, selected


@dataclass(frozen=True)
class PhaseStart:
    phase_id: str
    mode: str
    selected_budget_binding: dict
    hard_cap_ms: int
    strictest_deadline_utc: str
    started_at_utc: str
    started_monotonic_ns: int
    load_binding: dict
    execution_selection_binding: dict


def _utc_now():
    return datetime.now(timezone.utc)


def _cutoff(value):
    need(type(value) is str, 'MISSING_DEADLINE')
    return instant(value)


def begin_phase(reader, permit, expected_budget_binding, *,
                source_deadline, permission_deadline, session_deadline=None,
                request_deadline=None, elapsed_attempt_ms=0, current_guard=None):
    """Refuse before effect if any selected finite cap or real cutoff cannot fit.

    ``current_guard`` is the original caller's guard, invoked as-is. Its
    successful return is not accepted as a replacement for subsequent guards.
    The independently expected binding must come from the selected review.
    """
    validate('PhasePermit', permit)
    need(callable(current_guard), 'CURRENT_GUARD_REQUIRED')
    need(current_guard() is not False, 'CURRENT_GUARD_REFUSED')
    now = _utc_now()
    lower = _cutoff(permit['not_before'])
    upper = _cutoff(permit['expires_at'])
    need(lower <= now < upper, 'PERMIT_NOT_CURRENT')
    deadlines = [upper, _cutoff(source_deadline), _cutoff(permission_deadline)]
    if session_deadline is not None:
        deadlines.append(_cutoff(session_deadline))
    if request_deadline is not None:
        deadlines.append(_cutoff(request_deadline))
    strictest = min(deadlines)
    remaining_ns = (strictest - now).days * 86400_000_000_000 + (strictest - now).seconds * 1_000_000_000 + (strictest - now).microseconds * 1000
    need(remaining_ns > 0, 'DEADLINE_EXPIRED')
    # Round remaining time down. Never gain scheduling margin from sub-ms time.
    remaining_ms = remaining_ns // 1_000_000
    need(type(elapsed_attempt_ms) is int and elapsed_attempt_ms >= 0,
         'TIMING_INPUT')
    cap = phase_remaining(permit, reader, expected_budget_binding,
                          elapsed_attempt_ms, permit['phase_id'], remaining_ms)
    selected_binding = (permit['diagnostic_bounds_binding'] if permit['mode'] == 'diagnostic'
                        else permit['measured_budget_binding'])
    budget = selected(reader, selected_binding,
                      'DiagnosticBounds' if permit['mode'] == 'diagnostic' else 'MeasuredBudget',
                      expected_budget_binding)
    if permit['mode'] == 'diagnostic':
        need(budget['no_extra_effects'] is True and budget['review_binding']
             and budget['justification_binding'] and budget['kill_reap_policy_binding'],
             'MISSING_DIAGNOSTIC_CAP_REVIEW')
    else:
        need(bool(budget['sample_bindings']) and budget['complete_path_binding'],
             'MISSING_MEASURED_PATH')
    # A final wall-clock read can only reduce authority; it is not a renewal.
    final_now = _utc_now()
    need(final_now >= now, 'UTC_CLOCK_MOVED_BACKWARD')
    need(final_now < strictest and final_now >= lower, 'DEADLINE_EXPIRED')
    need((strictest - final_now).total_seconds() * 1000 >
         cap + max(budget['cleanup_reserve_ms'], permit['cleanup_reserve_seconds'] * 1000),
         'INSUFFICIENT_WHOLE_ATTEMPT_BUDGET')
    return PhaseStart(permit['phase_id'], permit['mode'], selected_binding, cap,
                      strictest.isoformat(), final_now.isoformat(), time.monotonic_ns(),
                      budget['load_binding'], permit['execution_selection_binding'])


def finish_phase(start, *, outcome, effect_state, containment_terminal,
                 cleanup_state, response_received=True):
    """Record observed elapsed time; timeout/lost reply never proves no effect.

    The caller supplies actual containment and cleanup observations. A
    diagnostic or censored sample can never be marked timing qualified.
    """
    need(type(start) is PhaseStart, 'PHASE_START_REQUIRED')
    need(outcome in ('success', 'refused', 'timeout', 'interrupted'), 'PHASE_OUTCOME')
    need(effect_state in ('none', 'observed', 'unknown'), 'EFFECT_STATE')
    need(cleanup_state in ('complete', 'incomplete', 'unknown'), 'CLEANUP_STATE')
    need(type(containment_terminal) is bool and type(response_received) is bool,
         'CONTAINMENT_OBSERVATION')
    ended_ns = time.monotonic_ns()
    need(ended_ns >= start.started_monotonic_ns, 'MONOTONIC_DISCONTINUITY')
    elapsed_ns = ended_ns - start.started_monotonic_ns
    ended = _utc_now()
    wall_elapsed_ns = int((ended - _cutoff(start.started_at_utc)).total_seconds() * 1_000_000_000)
    clock_discontinuity = abs(wall_elapsed_ns - elapsed_ns) > 1_000_000_000
    deadline_passed = ended >= _cutoff(start.strictest_deadline_utc)
    censored = (outcome in ('timeout', 'interrupted') or not response_received
                or elapsed_ns >= start.hard_cap_ms * 1_000_000 or deadline_passed
                or clock_discontinuity or effect_state == 'unknown'
                or not containment_terminal or cleanup_state != 'complete')
    observed_partial_effect = effect_state == 'observed' and censored
    if censored:
        outcome = 'censored'
        effect_state = 'unknown'
    return {
        'schema_version': 'lab-phase-observation/v1',
        'phase_id': start.phase_id, 'mode': start.mode,
        'selected_budget_binding': start.selected_budget_binding,
        'execution_selection_binding': start.execution_selection_binding,
        'load_binding': start.load_binding,
        'started_at_utc': start.started_at_utc, 'ended_at_utc': ended.isoformat(),
        'monotonic_elapsed_ns': elapsed_ns, 'hard_cap_ms': start.hard_cap_ms,
        'outcome': outcome, 'censored': censored, 'effect_state': effect_state,
        'observed_partial_effect': observed_partial_effect,
        'deadline_passed_after_start': deadline_passed,
        'clock_discontinuity': clock_discontinuity,
        'containment_terminal': containment_terminal, 'cleanup_state': cleanup_state,
        'response_received': response_received,
        'retry_allowed': False,
        'continue_positive': outcome == 'success' and not censored,
        # A caller must prove original exit/effect guards and full path separately.
        'timing_qualified': False,
        'authority_effect': 'none',
    }
