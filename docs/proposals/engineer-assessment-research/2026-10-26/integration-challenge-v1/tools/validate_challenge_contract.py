"""Validate the candidate Lab Challenge Contract and trigger-policy closure."""
from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'CyberAlchemy-lab'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


record = load(ROOT / 'model/lab-records/integration-choice-challenge-contract.json')
schema = load(LAB / 'authority/artifact-types/challenge-contract/v1/schema.json')
errors = list(Draft202012Validator(schema).iter_errors(record))
assert not errors, [e.message for e in errors]
assert record['lifecycle_state'] == 'candidate' and record['authority_effect'] == 'none'
policy_ref = record['payload']['policy_ref']
assert policy_ref == 'model/integration/RECONSIDERATION-POLICY.md'
policy = (ROOT / policy_ref).read_text(encoding='utf-8')
assert 'Status: **candidate policy source only**' in policy
assert record['relation_refs'][0]['counterpart_ref'] == policy_ref
assert record['evidence_refs'] == []
triggers = load(ROOT / 'model/integration/challenge-triggers.json')
assert triggers['contract_ref'] == 'model/lab-records/integration-choice-challenge-contract.json'
ids = {t['id'] for t in triggers['triggers']}
assert len(ids) == len(triggers['triggers']) == 7
assert ids == {ground.split()[0] for ground in record['payload']['grounds']}
reviews = load(ROOT / 'model/integration/choices.json')['choices']
assert len(reviews) == 6
for row in reviews:
    assert row['challenge_contract_ref'] == triggers['contract_ref']
    assert set(row['revisit_triggers']).issubset(ids) and row['revisit_triggers']
for trigger in triggers['triggers']:
    assert set(trigger['boundary_refs']) == {r['id'] for r in reviews}
    for field in ('trigger_condition', 'required_evidence', 'reassessment_gate', 'interim_disposition'):
        assert trigger[field]
    assert trigger['id'] in policy
assert '## Resolution gate' in policy
print('PASS: candidate Lab Challenge Contract shape, seven grounds, six linked reviews and draft-policy closure')
