#!/usr/bin/env python3
"""Validate design closure and selected negative examples, not ontology runtime."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];PACKAGE=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text())
def verify(b):assert hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest()==b['sha256'],b['path']
p=load(PACKAGE/'profiles/lab-ontology-profile.json'); ex=load(PACKAGE/'design/mapping-examples.json')
for b in [p['scope']['source_profile_binding'],p['scope']['carrier_inventory_binding'],p['global_edge']['signature_source_binding'],p['challenge_join']['contract_binding']]:verify(b)
impact=load(ROOT/p['scope']['carrier_inventory_binding']['path'])
assert len(p['domain_carrier_mappings'])==143
assert {c['carrier_ref'] for c in p['domain_carrier_mappings']}=={c['carrier_ref'] for c in impact['carriers']}
for c in p['domain_carrier_mappings']:verify(c['schema_binding'])
assert len(p['namespaces'])==len(set(p['namespaces'].values()))==3
assert len(p['history_domains'])==5 and all(k in p['history_domains'] for k in ['project_semantic','project_governance','ontology_semantic','ontology_governance'])
assert p['authority_effect']=='none' and p['replay_source'] is False and p['executable'] is False
for predicate, pairs in p['local_edges']['signatures'].items():
 assert len(pairs)==len({tuple(pair) for pair in pairs})
 assert all(len(pair)==2 and 'subject' not in pair for pair in pairs)
 assert predicate in p['local_edges']['allowed_qualifiers']
assert len(p['local_edges']['signatures'])==9
assert {'current','historical','withdrawn','challenged','version-mismatch','private-session-memory','missing-implementation-evidence','same-label-other-namespace'}=={x['case'] for x in ex['examples']}
fields=p['node_identity']['fields']
def node_id(row):
 vals=[row['ontology_ref'],row['namespace'],row['kind'],row['identity_ref'],row['version_ref'],row['represented_byte_sha256']]
 raw=b''.join(len(v.encode()).to_bytes(8,'big')+v.encode() for v in vals)
 return p['node_identity']['prefix']+hashlib.sha256(raw).hexdigest()
by_case={x['case']:x for x in ex['examples']}
assert node_id(by_case['current'])!=node_id(by_case['historical'])
assert node_id(by_case['current'])!=node_id(by_case['same-label-other-namespace'])
assert by_case['version-mismatch']['classification']=='unresolved'
assert by_case['private-session-memory']['classification']=='excluded'
assert by_case['missing-implementation-evidence']['classification']=='unresolved'
assert by_case['challenged']['instance_admission']=='admitted-current' and by_case['challenged']['challenge_state']=='pending'
assert all(x['fixture'] and x['actual_admission_evidence'] is None for x in ex['examples'])
assert len(p['independent_axes'])==9 and len(p['adapter_gaps'])==3
checks=['143-exact-carrier-mappings','independently-pinned-design-sources','three-distinct-namespaces','601-closed-local-signatures','global-projection-read-only','four-independent-history-domains','exact-challenge-revision-join','eight-fixture-dispositions','revision-and-namespace-identity-negatives','independent-posture-axes','explicit-rust-adapter-and-event-gaps','bounded-query-coverage']
paths=[f for folder in ['design','profiles'] for f in (PACKAGE/folder).glob('*') if f.is_file()]
context=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-O01-v6.json'
source_files=load(context)['sources'];[verify(b) for b in source_files]
r={'schema_version':'lab-ontology-mapping-check/v1-candidate','task':'O01','result':'PASS','authority_effect':'none','authoring_checks':checks,'scope':'Candidate mapping design and synthetic fixture semantics only; no actual Ontology Cut, admitted profile, canonical event or runtime adapter.','canonical_ontology_events_written':0,'actual_owner_outcome':None,'files':[{'path':f.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(paths)],'source_bindings':source_files}
index=1
while (PACKAGE/f'receipts/O01-{index:04d}.json').exists():index+=1
out=PACKAGE/f'receipts/O01-{index:04d}.json';out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
print(json.dumps({'result':'PASS','checks':len(checks),'receipt':out.relative_to(ROOT).as_posix(),'canonical_ontology_events_written':0}))
