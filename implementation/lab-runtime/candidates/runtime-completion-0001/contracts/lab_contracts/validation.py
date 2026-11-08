"""Closed schemas and semantic invariants; no permission is inferred."""
from datetime import datetime
from .codec import Refusal, _check, need
from .schema_catalog import schema


def instant(text):
    try:
        value = datetime.fromisoformat(text.replace('Z', '+00:00'))
        need(value.tzinfo is not None and value.utcoffset().total_seconds() == 0, 'UTC_REQUIRED')
        return value
    except (ValueError, TypeError, AttributeError):
        raise Refusal('INVALID_UTC') from None


def validate(name, value):
    from jsonschema import Draft202012Validator, FormatChecker
    _check(value)
    try:
        validator = Draft202012Validator(schema(name), format_checker=FormatChecker())
        need(validator.is_valid(value), 'SCHEMA_' + name)
    except (KeyError, RecursionError):
        raise Refusal('UNKNOWN_SCHEMA') from None
    if type(value) is dict and 'not_before' in value:
        need(instant(value['not_before']) < instant(value['expires_at']), 'EMPTY_INTERVAL')
    if name == 'CommandResult' and value['result'] == 'PASS':
        need(value['checks'] > 0, 'EMPTY_PASS')
        need(value['effect_state'] != 'unknown' and value['cleanup'] != 'unknown', 'UNKNOWN_EFFECT_OR_CLEANUP_PASS')
    if name == 'PhasePermit':
        diagnostic = value['mode'] == 'diagnostic'
        need((value['diagnostic_bounds_binding'] is not None) == diagnostic
             and (value['measured_budget_binding'] is None) == diagnostic, 'BUDGET_MODE')
    if name == 'SlotReceipt':
        need((value['terminal_binding'] is not None) ==
             (value['state'] in ('closed', 'quarantined')), 'SLOT_TERMINAL')
    if name in ('DiagnosticBounds', 'MeasuredBudget'):
        ids = [p['phase_id'] for p in value['phase_caps']]
        need(len(ids) == len(set(ids)), 'DUPLICATE_PHASE')
        need(value['cleanup_reserve_ms'] < value['total_cap_ms'], 'CLEANUP_CAP')
        need(all(p['hard_cap_ms'] <= value['total_cap_ms'] for p in value['phase_caps']), 'PHASE_CAP')
    if name == 'NamespaceCore':
        ids = [r['root_id'] for r in value['roots']]
        need(len(ids) == len(set(ids)), 'DUPLICATE_ROOT')
        need(value['broker_uid'] != value['workload_uid'], 'WRITER_ISOLATION')
        need(value['limits']['max_frame_bytes'] <= 65536, 'BROKER_FRAME_LIMIT')
    return value
