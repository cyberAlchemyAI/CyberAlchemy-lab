#!/usr/bin/env python3
"""Check candidate design closure, without claiming runtime execution."""
import hashlib,json
from pathlib import Path
from jsonschema import Draft202012Validator
from referencing import Registry,Resource
ROOT=Path(__file__).resolve().parents[5]; PACKAGE=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text())
def verify(b): assert hashlib.sha256((ROOT/b['path']).read_bytes()).hexdigest()==b['sha256'],b['path']
d=load(PACKAGE/'design/transition-contracts.json'); impact=load(ROOT/d['exact_pair_source_binding']['path']); verify(d['exact_pair_source_binding'])
pairs={(p['relation_kind_ref'],p['source_kind'],p['target_kind']):p for p in impact['exact_pairs']}
common=load(PACKAGE/'schemas/common.schema.json'); schema=load(PACKAGE/'schemas/workflow-run.schema.json')
reg=Registry().with_resource(common['$id'],Resource.from_contents(common))
Draft202012Validator.check_schema(common); Draft202012Validator.check_schema(schema)
assert len(d['workflows'])==10 and sum(len(w['transitions']) for w in d['workflows'])==28
for w in d['workflows']:
 verify(w['source_binding']); src=load(ROOT/w['source_binding']['path'])
 assert w['states']==src['states'] and w['single_goal_coordination'] is True and w['executable'] is False
 assert len(w['transitions'])==len(src['transitions'])
 for t,st in zip(w['transitions'],src['transitions']):
  assert all(t[k]==v for k,v in st.items())
  for b in t['input_bindings_required']+t['output_bindings_required']: verify(b['schema_binding'])
  assert t['actor_contract']['assignment'] and t['authority_contract']['operation'] and t['failure_contract']['uncertain_effect']
  assert t['satisfaction_evidence_contract']['predicate'] and len(t['gaps'])==2
  for p in t['selected_relation_signatures']:
   actual=pairs[(p['relation_kind_ref'],p['source_kind'],p['target_kind'])]
   assert all(actual[k]==v for k,v in p.items()); verify(p['relation_binding'])
 # Isolate discriminator/state constraints, preserving the complete referenced schema above.
 conditional={'type':'object','properties':{'workflow_type_ref':schema['properties']['workflow_type_ref']},'allOf':schema['allOf']}
 v=Draft202012Validator(conditional)
 for state in w['states']: v.validate({'workflow_type_ref':w['workflow_type_ref'],'state':state})
 assert list(v.iter_errors({'workflow_type_ref':w['workflow_type_ref'],'state':'invented-completion'}))
assert list(Draft202012Validator(schema,registry=reg).iter_errors({})), 'required obligations disappeared'
coord=load(ROOT/'authority/artifact-types/coordination-context/v2/schema.json')
assert 'goal_ref' in coord['required'] and 'goal_refs' not in coord['properties']
checks=['ten-workflows-and-28-transitions','source-byte-bindings','unchanged-source-transitions','exact-input-output-schemas','single-goal-coordination','independent-status-axes','explicit-actor-and-operation-authority','28-satisfaction-predicates','56-named-execution-gaps','exact-ordered-existing-pairs','workflow-specific-state-negatives','offline-schema-dependencies']
paths=[p for folder in ['design','schemas'] for p in (PACKAGE/folder).glob('*') if p.is_file()]
receipt={'schema_version':'lab-workflow-design-check/v1-candidate','task':'W01','result':'PASS','authority_effect':'none','authoring_checks':checks,'workflows':10,'transitions':28,'runtime_transitions_executed':0,'actual_owner_outcome':None,'scope':'Candidate design criterion only; named per-run actor/check/relation/lifecycle gaps reject runtime use until closure.','files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]}
out=PACKAGE/'receipts/W01-0001.json'; assert not out.exists();out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps({'result':'PASS','checks':len(checks),'workflows':10,'transitions':28,'receipt':out.relative_to(ROOT).as_posix(),'runtime_transitions_executed':0}))
