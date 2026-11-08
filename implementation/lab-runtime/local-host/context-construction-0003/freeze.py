"""Write one immutable review bundle; never writes into the selected family."""
import ast
import json
from collections import Counter
from pathlib import Path

import constructor as C


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def exclusive(path: Path, raw: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)


def main():
    rows = C.render()
    audit = C.historical_closure_candidates()
    require = C.require
    require(C.sha(C.raw_at(C.HERE.parent / 'CONTEXT-DOCKER-NEXT-UNIT-DESIGN-20261020-0002.md')) == C.DESIGN_SHA,
            'reviewed design changed')
    require(C.sha(C.raw_at(C.HERE.parent / 'independent-context-docker-design-review-0002/review.json')) == C.REVIEW_SHA,
            'independent design review changed')
    inventory = []
    for name, row in rows.items():
        raw = row['render_bytes']
        if name.endswith('.py'):
            tree = ast.parse(raw)
            refusals = sum(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and
                           node.func.id == '_t35_effect_refused' for node in ast.walk(tree))
        else:
            refusals = 0
        inventory.append({key: row[key] for key in ('path', 'preimage_sha256', 'render_sha256')}
                         | {'name': name, 'size': len(raw), 'effect_refusal_calls': refusals,
                            'predecessor_occurrences': row.get('predecessor_occurrences', {})})
    counts = dict(sorted(Counter(row['state'] for row in audit['rows']).items()))
    selection = {
        'schema_version': 'lab-disposable-context-provisional-selection/v1-inactive',
        'status': 'PROVISIONAL_EFFECT_DISABLED', 'authority_effect': 'none', 'actual_owner_outcome': None,
        'design_sha256': C.DESIGN_SHA, 'independent_design_review_sha256': C.REVIEW_SHA,
        'instance': C.INSTANCE, 'prospective_family': str(C.FAMILY), 'prospective_snapshot': str(C.SNAPSHOT),
        'source_manifest_status': 'REFUSED_PENDING_FRESH_MAPPER_AND_COMPLETE_CLOSURE',
        'predecessor_status': 'unselected', 'reader_adapter_source_status': 'unselected',
        'implementation_binding_status': 'unselected', 'development_authorization_status': 'unselected',
        'api_fact_schema_status': 'unselected', 'environment': {'python': '3.14.4', 'jsonschema': '4.23.0',
                                                                'cryptography': '46.0.5'},
        'role_count': 11, 'role_rows': inventory, 'historical_closure_manifest_sha256': audit['historical_manifest_sha256'],
        'historical_closure_row_count': len(audit['rows']), 'historical_closure_states': counts,
        'helpers': C.HELPER_PINS, 'source_pin_frozen': False,
        'completion_contract': C.completion_contract(),
    }
    require(len(inventory) == 11 and sum(row['effect_refusal_calls'] for row in inventory) > 0,
            'effect refusal insertion not observed')
    for name, row in rows.items():
        exclusive(C.HERE / 'rendered' / name, row['render_bytes'])
    exclusive(C.HERE / 'historical-closure-candidates.json', encoded(audit))
    exclusive(C.HERE / 'selection.json', encoded(selection))
    print(json.dumps({'status': 'FROZEN_PROVISIONAL', 'roles': 11, 'closure_rows': len(audit['rows']),
                      'closure_states': counts, 'effect_refusals': sum(r['effect_refusal_calls'] for r in inventory),
                      'source_manifest': 'REFUSED', 'effect': 'NOT_RUN'}, sort_keys=True))


if __name__ == '__main__':
    main()
