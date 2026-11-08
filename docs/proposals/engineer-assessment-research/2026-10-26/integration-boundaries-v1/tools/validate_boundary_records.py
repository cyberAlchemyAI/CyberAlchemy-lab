"""Check six candidate Integration Boundaries and their cross-record closure."""
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


source = BASE / 'boundaries.json'
rows = load(source)['boundaries']
index = load(BASE / 'boundary-index.json')
schema_path = ROOT / 'model/carriers/integration-boundary/v1/schema.json'
schema = load(schema_path)
Draft202012Validator.check_schema(schema)
assert len(rows) == len({x['id'] for x in rows}) == index['count'] == 6
assert len({x['slug'] for x in rows}) == 6
assert index['source_sha256'] == digest(source.read_bytes())
carrier = ROOT / 'model/carriers/integration-boundary/v1'
descriptor = load(carrier / 'artifact.json')
request = load(carrier / 'request.json')
assert descriptor['status'] == request['status'] == 'candidate-unadmitted'
assert descriptor['instance_contract']['schema_sha256'] == digest(schema_path.read_bytes())
assert descriptor['semantic_definition_sha256'] == digest((ROOT / 'model/definition-records/integration-boundary/definition.json').read_bytes())
assert request['semantic_definition_refs'] == ['ea.integration-boundary@0.1.0-candidate.1']
choices = {x['id']: x for x in load(BASE / 'choices.json')['choices']}
contracts = {x['id']: x for x in load(BASE / 'contracts.json')['contracts']}
expected = []
for i, row in enumerate(rows):
    path = BASE / 'boundaries' / row['id'] / 'record.json'
    record = load(path)
    errors = list(Draft202012Validator(schema).iter_errors(record))
    assert not errors, (path, [e.message for e in errors])
    assert record['record_id'] == row['id'] and record['source_index'] == i
    assert record['source_sha256'] == index['source_sha256']
    assert record['source_excerpt_sha256'] == digest(json.dumps(row, ensure_ascii=False, sort_keys=True).encode())
    for field in ('slug', 'responsibility', 'producer', 'consumer', 'inputs', 'outputs', 'data_classification', 'purpose', 'interface_contract', 'capability_ref', 'invariants', 'failure_and_recovery', 'source_refs', 'challenge_contract_ref'):
        assert record[field] == row[field], (path, field)
    assert choices[row['option_review_id']]['boundary_ref'] == contracts[row['verification_contract_id']]['boundary_ref'] == str(path.relative_to(ROOT))
    assert choices[row['option_review_id']]['boundary'] == row['slug']
    assert record['option_review_ref'] == f'model/integration/records/{row["option_review_id"]}/record.json'
    assert record['verification_contract_ref'] == f'model/integration/records/{row["verification_contract_id"]}/record.json'
    for ref in record['source_refs'] + [record['option_review_ref'], record['verification_contract_ref'], record['challenge_contract_ref']]:
        assert (ROOT / ref).is_file(), (path, ref)
    assert record['capability_ref'] in (ROOT / 'model/PRODUCT-MODEL.md').read_text(encoding='utf-8')
    expected.append(str(path.relative_to(ROOT)))
assert index['record_refs'] == expected
print('PASS: 6 source-bound Integration Boundaries, carrier request and closed review/verification/challenge links')
