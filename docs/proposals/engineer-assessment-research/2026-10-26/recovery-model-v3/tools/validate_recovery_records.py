"""Check recovery source parity, three carrier requests and synthetic shapes."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
LAB = Path(os.environ.get('CYBERALCHEMY_LAB_ROOT', str(ROOT.parent / 'CyberAlchemy-lab')))
load = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda data: hashlib.sha256(data).hexdigest()
source_path = ROOT / 'model/recovery/rule-source.json'
source = load(source_path)
index = load(ROOT / 'model/recovery/index.json')
assert source['authority_effect'] == index['authority_effect'] == 'none'
assert index['count'] == len(index['record_refs']) == len(source['rules']) == 21
assert index['source_sha256'] == sha(source_path.read_bytes())
assert [r['rule_id'] for r in source['rules']] == [f'RR-{n:02d}' for n in range(1, 22)]

registry = LAB / 'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
current = load(registry)['current_by_identity']
request_schema = load(LAB / 'authority/artifact-types/artifact-type-request/v1/schema.json')
spec = importlib.util.spec_from_file_location('ea_artifact_surface_recovery', LAB / 'tooling/generators/artifact_surface.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
request_type = load(LAB / 'authority/artifact-types/artifact-type-request/v1/artifact.json')

for family in ('administration-policy', 'recovery-rule', 'recovery-decision', 'upload-attempt'):
    base = ROOT / 'model/carriers' / family / 'v1'
    request = load(base / 'request.json')
    assert not list(Draft202012Validator(request_schema).iter_errors(request))
    assert request['resolution_evidence'] == {'registry_ref': str(registry.relative_to(LAB)) + '#sha256=' + sha(registry.read_bytes()), 'matches': []}
    assert 'cal.artifact-type.' + family not in current
    assert all(current.get(c['existing_type_ref'].split('/')[0]) == c['existing_type_ref'] for c in request['compatibility_analysis'])
    assert (base / 'REQUEST.md').read_text(encoding='utf-8') == module.render_instance(request_type, request)
    descriptor = load(base / 'artifact.json')
    schema = load(base / 'schema.json')
    Draft202012Validator.check_schema(schema)
    assert descriptor['authority_effect'] == 'none' and descriptor['lab_v3_conformance'].startswith('not-claimed')
    assert descriptor['instance_contract']['schema_sha256'] == sha((base / 'schema.json').read_bytes())
    assert descriptor['semantic_definition_sha256'] == sha((ROOT / 'model/definition-records' / family / 'definition.json').read_bytes())
    fixture_path = ROOT / 'model/recovery/synthetic' / (family + '.json')
    if fixture_path.exists():
        fixture = load(fixture_path)
        assert fixture['status'] == 'synthetic-fixture' and fixture['authority_effect'] == 'none'
        assert not list(Draft202012Validator(schema).iter_errors(fixture))
        bad = dict(fixture)
        if family == 'recovery-decision':
            bad.update(outcome='replace_same_slot', successor_assignment_ref=None)
        else:
            bad.update(state='verified', verified_media_ref=None)
        assert list(Draft202012Validator(schema).iter_errors(bad)), family

rule_schema = load(ROOT / 'model/carriers/recovery-rule/v1/schema.json')
policy = load(ROOT / 'model/recovery/administration-policy-candidate.json')
policy_schema = load(ROOT / 'model/carriers/administration-policy/v1/schema.json')
assert not list(Draft202012Validator(policy_schema).iter_errors(policy))
assert policy['source_sha256'] == sha((ROOT / policy['source_ref']).read_bytes())
assert policy['rule_refs'] == [r['rule_id'] for r in source['rules']]
assert policy['release_decision_ref'] is None and policy['status'] == 'candidate-unadmitted'
for i, ref in enumerate(index['record_refs']):
    row = source['rules'][i]
    record = load(ROOT / ref)
    assert record['rule_id'] == row['rule_id'] and record['source_index'] == i
    assert record['source_sha256'] == index['source_sha256']
    assert record['source_excerpt_sha256'] == sha(json.dumps(row, sort_keys=True, ensure_ascii=False).encode())
    assert not list(Draft202012Validator(rule_schema).iter_errors(record)), ref
    assert record['status'] == 'candidate-unadmitted' and record['authority_effect'] == 'none'
assert all(r['default_disposition'] != 'replace_same_slot' for r in source['rules'])
print('PASS: 21 source-bound recovery rules, 1 draft Administration Policy, 4 Lab-shaped type requests, 4 candidate schemas and 2 synthetic witnesses; invalid replacement/verification rejected')
