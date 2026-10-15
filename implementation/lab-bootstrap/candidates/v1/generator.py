"""Deterministic Method projection. JSON remains the canonical representation."""
import json


def method_markdown(record):
    lines = [f"# {record['name']}", '', 'Candidate Method; no admission or execution authority.', '',
             f"Identity: `{record['method_id']}`", f"Version: `{record['version']}`", '',
             '## Scope', '', record['scope'], '']
    for name in ['inputs', 'actions', 'roles', 'gates', 'outputs', 'evidence_requirements', 'boundary']:
        lines += ['## ' + name.replace('_', ' ').title(), ''] + ['- ' + x for x in record[name]] + ['']
    for name in ['residue_rule', 'validation_rule', 'recomposition_rule']:
        lines += ['## ' + name.replace('_', ' ').title(), '', record[name], '']
    lines += ['## Exact canonical body', '', '```json', json.dumps(record, indent=2, sort_keys=True), '```', '']
    return '\n'.join(lines).encode('utf-8')
