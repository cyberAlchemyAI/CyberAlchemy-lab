"""Check candidate policy source, clauses, retention schedule and Lab Policy/v2 shape."""
from pathlib import Path
import hashlib
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'CyberAlchemy-lab'
BASE = ROOT / 'model/policies'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


index = load(BASE / 'index.json')
clause_source = BASE / 'clauses.json'
policy_source = BASE / 'policy-set.json'
retention_source = BASE / 'retention-source.json'
assistance_source = BASE / 'assistance-source.json'
clauses = load(clause_source)['clauses']
policies = load(policy_source)['policies']
retention = load(retention_source)
assistance = load(assistance_source)
assert index['clause_count'] == len(clauses) == 46
assert index['policy_count'] == len(policies) == 14
assert len(retention['entries']) == 10
assert len(assistance['rows']) == 24
for key, path in [('clause', clause_source), ('policy', policy_source), ('retention', retention_source), ('assistance', assistance_source)]:
    assert index[f'{key}_source_sha256'] == digest(path.read_bytes())
clause_schema = load(ROOT / 'model/carriers/policy-clause/v1/schema.json')
retention_schema = load(ROOT / 'model/carriers/retention-schedule/v1/schema.json')
assistance_schema = load(ROOT / 'model/carriers/assistance-matrix/v1/schema.json')
policy_schema = load(LAB / 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/policy/v2/schema.json')
registry = load(LAB / 'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json')
assert registry['current_by_identity']['cal.artifact-type.policy'] == 'cal.artifact-type.policy/v2'
policy_descriptor = next(x for x in registry['descriptors'] if x['artifact_type_ref'] == 'cal.artifact-type.policy/v2')
assert policy_descriptor['schema_sha256'] == digest((LAB / policy_descriptor['schema_path']).read_bytes())
for schema in (clause_schema, retention_schema, assistance_schema, policy_schema):
    Draft202012Validator.check_schema(schema)
for family, schema_path in [('policy-clause', ROOT / 'model/carriers/policy-clause/v1/schema.json'),
                            ('retention-schedule', ROOT / 'model/carriers/retention-schedule/v1/schema.json'),
                            ('assistance-matrix', ROOT / 'model/carriers/assistance-matrix/v1/schema.json')]:
    base = schema_path.parent
    descriptor, request = load(base / 'artifact.json'), load(base / 'request.json')
    assert descriptor['status'] == request['status'] == 'candidate-unadmitted'
    assert descriptor['instance_contract']['schema_sha256'] == digest(schema_path.read_bytes())
    assert descriptor['semantic_definition_sha256'] == digest((ROOT / 'model/definition-records' / family / 'definition.json').read_bytes())
    assert request['semantic_definition_refs'] == [f'ea.{family}@0.1.0-candidate.1']
expected_clauses = []
policy_ids = {x['id'] for x in policies}
for i, row in enumerate(clauses):
    path = BASE / 'clauses' / row['id'] / 'record.json'
    record = load(path)
    errors = list(Draft202012Validator(clause_schema).iter_errors(record))
    assert not errors, (path, [e.message for e in errors])
    assert record['record_id'] == row['id'] and record['source_index'] == i
    assert record['source_sha256'] == index['clause_source_sha256']
    assert record['source_excerpt_sha256'] == digest(json.dumps(row, ensure_ascii=False, sort_keys=True).encode())
    assert row['policy_id'] in policy_ids
    assert record['policy_ref'] == f'model/policies/records/{row["policy_id"]}/policy.json'
    for field in ('condition', 'effect', 'statement', 'enforcement_point', 'required_evidence', 'exception_route', 'owner_role', 'source_refs', 'open_parameters'):
        assert record[field] == row[field]
    for ref in record['source_refs'] + [record['policy_ref']]:
        assert (ROOT / ref).is_file(), (path, ref)
    expected_clauses.append(str(path.relative_to(ROOT)))
assert index['clause_refs'] == expected_clauses
expected_policies = []
for row in policies:
    path = BASE / 'records' / row['id'] / 'policy.json'
    record = load(path)
    errors = list(Draft202012Validator(policy_schema).iter_errors(record))
    assert not errors, (path, [e.message for e in errors])
    assert record['lifecycle_state'] == 'candidate' and record['authority_effect'] == 'none'
    assert record['name'] == row['title'] and record['payload']['effective_period'] == 'not-effective-candidate'
    assert record['payload']['rule_refs'] == [f'model/policies/clauses/{rid}/record.json' for rid in row['clause_ids']]
    assert record['owner_ref'] == record['payload']['issuer_ref']
    assert row['approval_ref'] is None and row['status'] == 'candidate-unissued'
    for ref in record['payload']['rule_refs'] + row['source_refs']:
        assert (ROOT / ref).is_file(), (path, ref)
    expected_policies.append(str(path.relative_to(ROOT)))
assert index['policy_refs'] == expected_policies
retention_path = ROOT / index['retention_ref']
schedule = load(retention_path)
errors = list(Draft202012Validator(retention_schema).iter_errors(schedule))
assert not errors, (retention_path, [e.message for e in errors])
assert schedule['record_id'] == retention['schedule_id']
assert schedule['source_sha256'] == index['retention_source_sha256']
assert schedule['source_excerpt_sha256'] == digest(json.dumps(retention, ensure_ascii=False, sort_keys=True).encode())
assert schedule['entries'] == retention['entries']
assert schedule['jurisdiction'] is schedule['controller_ref'] is schedule['approval_ref'] is None
assert all(x['duration_value'] is x['duration_unit'] is None for x in schedule['entries'])
assert schedule['policy_ref'] == 'model/policies/records/POL-02/policy.json'
matrix_path = ROOT / index['assistance_ref']
matrix = load(matrix_path)
errors = list(Draft202012Validator(assistance_schema).iter_errors(matrix))
assert not errors, (matrix_path, [e.message for e in errors])
assert matrix['record_id'] == assistance['matrix_id']
assert matrix['source_sha256'] == index['assistance_source_sha256']
assert matrix['source_excerpt_sha256'] == digest(json.dumps(assistance, ensure_ascii=False, sort_keys=True).encode())
assert matrix['rows'] == assistance['rows'] and matrix['approval_ref'] is None
assert matrix['policy_ref'] == 'model/policies/records/POL-03/policy.json'
assert (ROOT / matrix['administration_policy_ref']).is_file()
assert {r['session'] for r in matrix['rows']} == {1, 2, 3}
assert len({(r['session'], r['resource']) for r in matrix['rows']}) == 24
for session in (1, 2, 3):
    assert next(r for r in matrix['rows'] if r['session'] == session and r['resource'] == 'accessibility-tools')['baseline_state'] == 'candidate-permit'
    assert next(r for r in matrix['rows'] if r['session'] == session and r['resource'] == 'live-generative-ai')['baseline_state'] == 'candidate-prohibit'
print('PASS: 14 candidate Lab Policy/v2 records, 46 source-bound clauses, ten-class retention schedule and 24-row assistance matrix')
