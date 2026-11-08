"""Check source parity and candidate carrier shape for integration governance."""
from pathlib import Path
import hashlib
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'model/integration'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


choices = load(BASE / 'choices.json')['choices']
contracts = load(BASE / 'contracts.json')['contracts']
component_ids = {x['id'] for x in load(BASE / 'components.json')['components']}
assert len(choices) == len(contracts) == 6
assert {r['id'] for r in choices} == {r['option_review_id'] for r in contracts}
assert {r['contract_id'] for r in choices} == {r['id'] for r in contracts}
assert len({r['id'] for r in choices + contracts}) == 12

expected = []
for family, rows, source in (
    ('integration-option-review', choices, BASE / 'choices.json'),
    ('integration-verification-contract', contracts, BASE / 'contracts.json'),
):
    carrier = ROOT / 'model/carriers' / family / 'v1'
    schema = load(carrier / 'schema.json')
    Draft202012Validator.check_schema(schema)
    descriptor = load(carrier / 'artifact.json')
    request = load(carrier / 'request.json')
    assert descriptor['status'] == request['status'] == 'candidate-unadmitted'
    assert descriptor['authority_effect'] == request['authority_effect'] == 'none'
    assert descriptor['instance_contract']['schema_sha256'] == digest((carrier / 'schema.json').read_bytes())
    definition = ROOT / 'model/definition-records' / family / 'definition.json'
    assert descriptor['semantic_definition_sha256'] == digest(definition.read_bytes())
    assert request['semantic_definition_refs'] == [f'ea.{family}@0.1.0-candidate.1']
    registry_ref, registry_hash = request['resolution_evidence']['registry_ref'].split('#sha256=')
    registry = ROOT.parent / 'CyberAlchemy-lab' / registry_ref
    assert registry.is_file() and digest(registry.read_bytes()) == registry_hash
    for i, row in enumerate(rows):
        path = BASE / 'records' / row['id'] / 'record.json'
        record = load(path)
        errors = list(Draft202012Validator(schema).iter_errors(record))
        assert not errors, (path, [e.message for e in errors])
        assert record['record_id'] == row['id']
        assert record['source_ref'] == str(source.relative_to(ROOT))
        assert record['source_sha256'] == digest(source.read_bytes())
        assert record['source_index'] == i
        assert record['source_excerpt_sha256'] == digest(json.dumps(row, ensure_ascii=False, sort_keys=True).encode())
        assert record['authority_effect'] == 'none'
        if family == 'integration-option-review':
            for key in ('boundary', 'problem', 'requirement_refs', 'options', 'provisional_preference', 'rationale', 'unresolved_assumptions', 'decision_constraints', 'revisit_triggers', 'rejected_alternatives'):
                assert record[key] == row[key], (path, key)
            assert record['owner_decision_ref'] is None
            assert record['verification_contract_ref'] == f'model/integration/records/{row["contract_id"]}/record.json'
            assert len({x['id'] for x in row['options']}) == len(row['options'])
            for ref in row['requirement_refs'] + [s for option in row['options'] for s in option['source_refs']]:
                assert (ROOT / ref).is_file(), (path, ref)
            for option in row['options']:
                assert set(option['component_refs']).issubset(component_ids), (path, option['id'])
        else:
            for key in ('objective', 'environment', 'checks', 'failure_route', 'challenge_route', 'evidence_requirements', 'rejection_gates', 'threshold_registration'):
                assert record[key] == row[key], (path, key)
            assert record['option_review_ref'] == f'model/integration/records/{row["option_review_id"]}/record.json'
            assert record['run_refs'] == record['result_refs'] == []
            assert len({x['id'] for x in row['checks']}) == len(row['checks'])
        assert (ROOT / record.get('verification_contract_ref', record.get('option_review_ref'))).is_file()
        expected.append(str(path.relative_to(ROOT)))

index = load(BASE / 'index.json')
assert index['count'] == len(expected) == 12 and index['record_refs'] == expected
assert index['authority_effect'] == 'none'
assert all((ROOT / ref).is_file() for ref in index['source_refs'])
print('PASS: 12 source-bound integration records, 2 candidate carriers, 2 requests, 6 closed verification contracts; no run or owner Decision')
