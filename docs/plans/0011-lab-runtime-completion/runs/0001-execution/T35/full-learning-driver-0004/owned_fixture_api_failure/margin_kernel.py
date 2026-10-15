"""Pure, qualification-only timing reserve evaluator. No empirical defaults."""
from datetime import datetime, timezone

IDENTITY_FIELDS = {'source_sha256', 'profile_sha256', 'code_closure_sha256',
                   'dependency_selection_sha256', 'load_identity_sha256',
                   'instrumentation_identity_sha256', 'source_cut_sha256'}
POLICY_FIELDS = {'schema_version', 'authority_effect', 'status', 'execution_identity',
                 'evidence_bindings', 'uncertainty_method', 'sample_count',
                 'phase_upper_bounds_us', 'uncertainty_reserve_us',
                 'gate_overhead_upper_bound_us', 'valid_until'}
CHECKPOINTS = {'lesson.apply': 'application-preclaim',
               'lesson.assess': 'assessment-preclaim'}
REMAINING = {
    'application-preclaim': ('application-call', 'exact-application-retry',
        'operation-inspection', 'assessment-operator-preparation', 'assessment-call',
        'attached-close', 'parent-inspection', 'parent-close', 'original-cleanup'),
    'assessment-preclaim': ('assessment-call', 'attached-close', 'parent-inspection',
        'parent-close', 'original-cleanup'),
}
DEADLINE_FIELDS = {'effective_call', 'Session', 'Context_delivery', 'Source_period',
                   'parent_reader', 'operator_reader'}


class MarginRefusal(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def require(value, reason):
    if not value:
        raise MarginRefusal(reason)


def instant(value):
    require(type(value) is str, 'missing-real-deadline')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise MarginRefusal('invalid-real-deadline') from None
    require(result.tzinfo is not None and result.utcoffset() is not None,
            'timezone-required')
    return result.astimezone(timezone.utc)


def positive_integer(value):
    return type(value) is int and value > 0


def decide(policy, identity, deadlines, observed_at, checkpoint, *, load_current):
    """Use exact accepted empirical bounds; this function performs no effects.

    observed_at and deadlines are direct real-runtime observations supplied by
    the separately selected production adapter. Synthetic tests may supply
    inert timestamps but cannot qualify a real lease or empirical policy.
    """
    require(type(policy) is dict and set(policy) == POLICY_FIELDS,
            'empirical-policy-missing-or-open')
    require(policy['schema_version'] == 'lab-observed-lifetime-margin/v1-candidate'
            and policy['authority_effect'] == 'none'
            and policy['status'] == 'empirically-qualified', 'empirical-policy-unqualified')
    require(type(identity) is dict and set(identity) == IDENTITY_FIELDS
            and identity == policy['execution_identity'], 'empirical-execution-identity-differs')
    import re
    require(all(type(v) is str and re.fullmatch('[a-f0-9]{64}', v)
                for v in identity.values()), 'empirical-identity-incomplete')
    require(load_current is True, 'actual-load-unknown-or-outside-calibration')
    require(policy['uncertainty_method'] == 'observed-maximum-plus-reviewed-uncertainty',
            'uncertainty-method-unqualified')
    require(positive_integer(policy['sample_count']) and type(policy['evidence_bindings']) is list
            and len(policy['evidence_bindings']) > 0, 'empirical-evidence-missing')
    for row in policy['evidence_bindings']:
        require(type(row) is dict and set(row) == {'path', 'sha256'}
                and type(row['path']) is str and type(row['sha256']) is str
                and re.fullmatch('[a-f0-9]{64}', row['sha256']), 'empirical-evidence-binding-open')
        from pathlib import PurePosixPath
        path = PurePosixPath(row['path'])
        require(bool(row['path']) and not path.is_absolute() and path.as_posix() == row['path']
                and '..' not in path.parts and '\\' not in row['path'] and '\0' not in row['path']
                and row['path'] != '.', 'empirical-evidence-path-unsafe')
    require(type(checkpoint) is str and checkpoint in REMAINING, 'unknown-effect-checkpoint')
    require(type(deadlines) is dict and set(deadlines) == DEADLINE_FIELDS,
            'real-lifetime-bound-missing')
    current = instant(observed_at)
    require(current < instant(policy['valid_until']), 'empirical-policy-expired')
    bound = min(instant(value) for value in deadlines.values())
    delta = bound - current
    remaining_us = delta.days * 86400000000 + delta.seconds * 1000000 + delta.microseconds
    phases = policy['phase_upper_bounds_us']
    require(type(phases) is dict and set(phases) == set(REMAINING['application-preclaim'])
            and all(positive_integer(v) for v in phases.values()), 'empirical-phase-bound-unknown')
    uncertainty = policy['uncertainty_reserve_us']
    overhead = policy['gate_overhead_upper_bound_us']
    require(positive_integer(uncertainty) and positive_integer(overhead),
            'empirical-uncertainty-or-gate-overhead-unknown')
    required_us = sum(phases[name] for name in REMAINING[checkpoint]) + uncertainty + overhead
    require(remaining_us > required_us, 'real-lease-cannot-fit-observed-tail')
    return {'checkpoint': checkpoint, 'strictest_real_deadline': bound.isoformat(),
            'observed_at': current.isoformat(), 'remaining_real_lease_us': remaining_us,
            'required_observed_tail_us': required_us, 'remaining_margin_us': remaining_us-required_us,
            'policy_grants_permission': False, 'prediction_guarantees_future_load': False,
            'authority_effect': 'none'}

raise ValueError('owned inert helper initialization failure')
