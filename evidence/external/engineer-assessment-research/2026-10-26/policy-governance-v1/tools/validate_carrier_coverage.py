"""Check carrier coverage of authored records, source views and explicit gaps."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
coverage=load(ROOT/'model/carriers/coverage.json');gaps=load(ROOT/'model/carriers/gaps.json')
assert coverage['authority_effect']==gaps['authority_effect']=='none'
selected=coverage['selected_lab_instance_records']
expected_product={'product/product.json'}
expected_research={str(p.relative_to(ROOT)) for p in (ROOT/'model/lab-records').glob('*.json') if p.name not in ('relation-proposals.json','integration-choice-challenge-contract.json')}
expected_governance={'model/lab-records/integration-choice-challenge-contract.json'}
expected_policies={str(p.relative_to(ROOT)) for p in (ROOT/'model/policies/records').glob('*/policy.json')}
expected_roles={str(p.relative_to(ROOT)) for p in (ROOT/'model/lab-records/roles').glob('*.json')}
expected_defs={str(p.relative_to(ROOT)) for p in (ROOT/'model/definition-records').glob('*/definition.json')}
for key,expected in [('product',expected_product),('research',expected_research),('governance',expected_governance),('policies',expected_policies),('roles',expected_roles),('definitions',expected_defs)]:
 assert set(selected[key])==expected,key
assert selected['count']==sum(len(selected[k]) for k in ('product','research','governance','policies','roles','definitions'))==167
index=load(ROOT/'model/concrete-records/index.json')
local={p for f in index['families'] if f['carrier_status']=='candidate-requested' for p in f['record_refs']}
local.update(load(ROOT/'model/recovery/index.json')['record_refs'])
local.add('model/recovery/administration-policy-candidate.json')
local.update(load(ROOT/'model/integration/index.json')['record_refs'])
local.update(load(ROOT/'model/integration/component-index.json')['record_refs'])
local.update(load(ROOT/'model/integration/boundary-index.json')['record_refs'])
policy_index=load(ROOT/'model/policies/index.json')
local.update(policy_index['clause_refs'])
local.update([policy_index['retention_ref'],policy_index['assistance_ref']])
assert set(coverage['local_candidate_instance_records']['records'])==local
assert coverage['local_candidate_instance_records']['count']==len(local)==208
requests={str(p.relative_to(ROOT)) for p in (ROOT/'model/carriers').glob('*/v1/request.json')}
assert set(coverage['artifact_type_requests']['records'])==requests
assert coverage['artifact_type_requests']['count']==len(requests)==22
for group in ('product','research','governance','policies','roles','definitions'):
 for ref in selected[group]:assert (ROOT/ref).is_file(),ref
for ref in local|requests:assert (ROOT/ref).is_file(),ref
ids={g['gap_id'] for g in gaps['gaps']};assert len(ids)==len(gaps['gaps'])==17
for g in gaps['gaps']:assert (ROOT/g['source_ref']).is_file(),g['gap_id']
for row in coverage['embedded_or_source_controls']:
 assert (ROOT/row['source_ref']).is_file(),row
 assert row['gap_ref'] is None or row['gap_ref'] in ids
for row in coverage['embedded_subjects']:
 assert (ROOT/row['source_ref']).is_file(),row
 assert row['gap_ref'] is None or row['gap_ref'] in ids
crosswalk=load(ROOT/'model/concrete-records/study-design-crosswalk.json')
assert crosswalk['count']==len(crosswalk['entries'])==3
study={s['experiment_id']:s for s in load(ROOT/'research/session-studies.json')['studies']}
for row in crosswalk['entries']:
 assert row['study_id'] in study and row['run_count']==len(study[row['study_id']]['run_refs'])==0
 design=load(ROOT/row['design_ref']);assert design['protocol_ref']==row['protocol_ref']==study[row['study_id']]['protocol']
assert len(load(ROOT/'model/lab-records/relation-proposals.json')['proposals'])==114
print('PASS: 167 selected-carrier and 208 local-carrier candidate records, 22 type requests, 17 explicit gaps, 3 study crosswalks and 114 unapplied links accounted for')
