"""Check candidate component identity records and the empty binding carrier."""
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


source = BASE / 'components.json'
rows = load(source)['components']
boundary_ids = {x['id'] for x in load(BASE / 'boundaries.json')['boundaries']}
index = load(BASE / 'component-index.json')
assert len(rows) == len({x['id'] for x in rows}) == index['count'] == 24
assert index['source_sha256'] == digest(source.read_bytes())
assert index['binding_refs'] == []
schema = load(ROOT / 'model/carriers/technology-component/v1/schema.json')
binding_schema = load(ROOT / 'model/carriers/integration-binding/v1/schema.json')
Draft202012Validator.check_schema(schema)
Draft202012Validator.check_schema(binding_schema)
assert binding_schema['properties']['owner_decision_ref']['minLength'] == 1
assert binding_schema['properties']['verification_result_refs']['minItems'] == 1
for family in ('technology-component', 'integration-binding'):
    base = ROOT / 'model/carriers' / family / 'v1'
    descriptor = load(base / 'artifact.json')
    request = load(base / 'request.json')
    definition = ROOT / 'model/definition-records' / family / 'definition.json'
    assert descriptor['semantic_definition_sha256'] == digest(definition.read_bytes())
    assert descriptor['instance_contract']['schema_sha256'] == digest((base / 'schema.json').read_bytes())
    assert descriptor['status'] == request['status'] == 'candidate-unadmitted'
    assert descriptor['authority_effect'] == request['authority_effect'] == 'none'
    assert request['semantic_definition_refs'] == [f'ea.{family}@0.1.0-candidate.1']

expected = []
for i, row in enumerate(rows):
    path = BASE / 'components' / row['id'] / 'record.json'
    record = load(path)
    errors = list(Draft202012Validator(schema).iter_errors(record))
    assert not errors, (path, [e.message for e in errors])
    assert record['record_id'] == row['id'] and record['source_index'] == i
    assert record['source_ref'] == 'model/integration/components.json'
    assert record['source_sha256'] == index['source_sha256']
    assert record['source_excerpt_sha256'] == digest(json.dumps(row, ensure_ascii=False, sort_keys=True).encode())
    assert {k: record[k] for k in row if k != 'id'} == {k: v for k, v in row.items() if k != 'id'}
    assert record['version_pin'] is record['license_or_terms_ref'] is record['legal_processor_ref'] is None
    assert record['publisher_or_maintainer_ref'] is record['upstream_identity_ref'] is None
    assert record['lifecycle_status'] == 'unverified'
    assert record['selection_posture'] == 'candidate-only'
    assert set(record['boundary_refs']).issubset(boundary_ids)
    for ref in record['source_refs']:
        assert (ROOT / ref).is_file(), (path, ref)
    expected.append(str(path.relative_to(ROOT)))
assert index['record_refs'] == expected
used = {ref for review in load(BASE / 'choices.json')['choices'] for option in review['options'] for ref in option['component_refs']}
assert used <= {row['id'] for row in rows}
print('PASS: 24 source-bound technology candidates, 2 carrier requests and an empty selected-binding index')
