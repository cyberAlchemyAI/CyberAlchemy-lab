#!/usr/bin/env python3
"""Materialize transition design from pinned existing workflow templates."""
import copy
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
PACKAGE=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text())
def put(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def binding(p): return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
impact=load(ROOT/'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json')
pairs={(p['relation_kind_ref'],p['source_kind'],p['target_kind']):p for p in impact['exact_pairs']}
carriers={p['carrier_ref']:p for p in impact['carriers']}
# Selected semantic requirements. Other template connections require named closure;
# permitted signatures are never automatically instantiated as edges.
selected={
 'engineering': [('relation.evaluates','work-outcome-assessment','work')],
 'research': [('relation.engages-inquiry','experiment-design','research-inquiry'),('relation.tests-hypothesis','experiment-design','hypothesis'),('relation.realizes','experiment-run','experiment-design'),('relation.engages-inquiry','finding','research-inquiry')],
 'operational-learning': [('relation.applies-lesson','lesson-application','operational-lesson'),('relation.evaluates','lesson-outcome-assessment','lesson-application')],
}
checks={
 'intent-framing':['Intent Resolution resolves every claimed subject to its exact revision and records unresolved subjects; no completion is inferred.','Work references the resolved Intent and declared Goal; the Coordination Context has exactly one goal_ref.'],
 'agent-context':['Assignment and Delegation resolve a current principal, represented scope and revocation status; Context and Ontology Views share the selected Project State cut.','Session context is bounded, binds its source/head/configuration, and is rejected when stale; short memory starts empty and is erased on close or expiry.'],
 'engineering':['Design output binds the exact resolved Intent, Work, implementation revision and acceptance obligations; declared dependencies resolve.','Implementation output binds original bytes, generator identity, source references and executed checks; proposal/admission status is separate.','Work Outcome Assessment evaluates each declared satisfaction obligation with evidence and limitations; acceptance is independent of admission.'],
 'research':['Experiment Design declares hypothesis, protocol, variables, controls, measurements, resource bounds and intended interpretation before execution.','Experiment Run and Measurement Results bind the design revision, real executor, actual inputs and observations; planned observations cannot become evidence.','Finding and Evaluation retain uncertainty, negative results and evidence lineage; evaluation does not prove Product adoption.'],
 'failure-assessment':['Occurrence evidence is immutable; Classification Assignment binds a selected classification rule and its version rather than inventing free text authority.','Failure Assessment distinguishes observed occurrence, hypothesized failure mode and causal confidence; scope and evidence are explicit.','Failure Control Binding and assessment record actual control application and observed response; recommendations are not effective controls.'],
 'challenge-handling':['Challenge Event resolves the challenged claim and the exact Challenge Contract eligibility, owner and response route.','Response binds current authority, source evidence and outcome scope; a pending contest is not silently closed.','Resolution records the responsible owner outcome, remaining contests and any exact required Decision; no implied admission.'],
 'operational-learning':['Lesson references actual observation and outcome evidence, describes applicability and limitations; a pattern is not an instruction grant.','Lesson Application binds one lesson revision to actual selected Work/context and records why it applies; selection alone is not application.','Lesson Outcome Assessment binds actual application results; Improvement Signal is a candidate proposal, never automatic memory or governance mutation.'],
 'review-admission':['Review closure binds exact members, postimages, source cuts, validation evidence, principal roles and per-member effect scope.','Checkpoint resolution preserves actual human member outcomes, including reject/revise/defer, against the unchanged exact bundle; no simulated owner outcome.','Admission applies only members with current positive exact authority; compare-and-swap preconditions and transaction journal bind the poststate; uncertain effects require inspection.'],
 'ontology-migration':['Mapping binds node meaning, original admitted source references and exact existing relation signatures; no carrier/instance or concept/source collapse.','Candidate validation checks all node/edge identities, evidence lineage, selected policy and local/global scope; a local edge never extends global coupling.','Migration Manifest compares declared scope with actual selected records and preserves exclusions, byte evidence and recoverability; selection assessment is not complete migration.'],
 'product-adoption-release':['Candidate assessment binds Product identity, capability realization, exact implementation revision and relevant acceptance results; Project scope remains distinct.','Pilot assessment records actual human observations and limitations from a real run; automated fixtures cannot prove usefulness.','Release review binds exact capability adoption and operational evidence under actual owner authority; no stable release from candidate status alone.']
}
contracts=[]
for src in sorted((ROOT/'docs/proposals/0007-lab-integrated-schema-package/workflows').glob('*.json')):
 d=load(src); name=src.stem; ts=[]
 for index,t in enumerate(d['transitions']):
  rows=[]
  kinds={carriers[c]['semantic_kind'] for c in t['input_carriers']+t['output_carriers']}
  for key in selected.get(name,[]):
   if key[1] in kinds and key[2] in kinds:
    pair=pairs[key]
    rows.append({k:copy.deepcopy(pair[k]) for k in ['relation_kind_ref','source_kind','target_kind','axis_id','relation_binding','qualifier_contract']})
  ts.append({**copy.deepcopy(t),'input_bindings_required':[{'carrier_ref':c,'schema_binding':{'path':carriers[c]['schema_path'],'sha256':carriers[c]['schema_sha256']}} for c in t['input_carriers']],
    'output_bindings_required':[{'carrier_ref':c,'schema_binding':{'path':carriers[c]['schema_path'],'sha256':carriers[c]['schema_sha256']}} for c in t['output_carriers']],
    'actor_contract':{'assignment':'Exact authenticated principal and active Agent Assignment/Delegation where delegated; machine Agent session is ephemeral.','scope':'Current operation, represented Project scope, selected cut, expiry and revocation; no authority from caller body.','binding_status':'required-per-run; not assigned by design'},
    'authority_contract':{'candidate_preparation':'Explicit current execution authorization; grants no canonical semantic state.','semantic_member':'R08 exact member outcome, verified independently, before effective admission.','operation':'Exact current action authorization, preconditions and effect scope; semantic admission alone is insufficient.'},
    'selected_relation_signatures':rows,'relation_rule':'Every actual connection must choose one exact ordered pair and its closed qualifier values, bind admitted endpoints and one writable authority; no Cartesian expansion or automatic edge.',
    'satisfaction_evidence_contract':{'predicate':checks[name][index],'required':['Exact input/output byte bindings','Actual check implementation and execution result','Source cut and transaction head','Named unresolved obligations and limitations'],'state_rule':'Transition state and admission/carrier lifecycle/commitment/outcome satisfaction are independent.'},
    'gaps':[{'gap_id':'W01-ACTOR-'+t['transition_ref'],'disposition':'W02/W03 bind real per-run actors and checks; absent bindings reject execution.'},{'gap_id':'W01-RELATIONS-'+t['transition_ref'],'disposition':'W02/W03 bind every actual selected relation, endpoint, closed qualifier domain and lifecycle role; absent or new signature routes to C14 and R08.'}],
    'failure_contract':{'known_invalid':'Reject before mutation and record blocked with violated predicate.','uncertain_effect':'Record indeterminate, inspect exact journal and current cut; reconcile under a bound recovery contract before retry.','cancellation':'Explicit scoped cancellation preserves evidence; never infers semantic rejection.'}})
 contracts.append({'name':name,'workflow_type_ref':d['workflow_type_ref'],'source_binding':binding(src),'states':d['states'],'initial_state':d['initial_state'],'terminal_states':d['terminal_states'],'transitions':ts,'single_goal_coordination':True,'authority_effect':'none','executable':False})
put(PACKAGE/'design/transition-contracts.json',{'schema_version':'lab-workflow-transition-design/v1-candidate','authority_effect':'none','status':'candidate-design-not-executable','workflows':contracts,'exact_pair_source_binding':binding(ROOT/'implementation/lab-runtime/candidates/repeatable-operation/design/contract-impact.json')})
common=ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/common.schema.json'
(PACKAGE/'schemas/common.schema.json').write_bytes(common.read_bytes())
schema=load(ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/workflow-run.schema.json')
schema['$id']='urn:cyberalchemy-lab:workflow-design:run:v1-candidate'
schema['properties']['schema_version']['const']='lab-workflow-design-run/v1-candidate'
schema['properties']['workflow_type_ref']={'enum':[w['workflow_type_ref'] for w in contracts]}
schema['properties']['status_axes']={'type':'object','additionalProperties':False,'required':['carrier_lifecycle','commitment','admission','outcome_satisfaction'],'properties':{k:{'type':['string','null']} for k in ['carrier_lifecycle','commitment','admission','outcome_satisfaction']}}
schema['required']+=['workflow_type_ref','status_axes']
schema['allOf']=[{'if':{'properties':{'workflow_type_ref':{'const':w['workflow_type_ref']}},'required':['workflow_type_ref']},'then':{'properties':{'state':{'enum':w['states']}}}} for w in contracts]
put(PACKAGE/'schemas/workflow-run.schema.json',schema)
lines=['# Integrated workflow transition contracts','', 'Status: candidate design. Ten workflows, exact input/output schema bindings and independently declared workflow states. Actual principal assignments, implemented checks, relation instances and lifecycle mappings are required before execution.','', '## State and authority','', 'Intent states express requested direction. Intent Resolution binds exact target subjects. Work goals retain their admitted shape. Coordination Context/v2 has one goal_ref. Product describes durable value and capabilities; Project bounds coordinated work. Workflow phase is separate from carrier lifecycle, commitment, admission and outcome satisfaction.','', 'Machine Agents are ephemeral. Durable knowledge comes from exact Project State, Context View and Ontology View; short memory belongs to one session and is erased on closure. Lessons require evidenced application and outcome assessment.','', 'Each transition requires authenticated assignment, bounded authority, original-byte input/output bindings, independently executed satisfaction evidence, exact ordered relation signatures and explicit failure disposition. Owner checkpoint and operation authority are evaluated separately.','', '## Workflows','']
for w in contracts:
 lines += ['### '+w['name'],'','| Transition | Satisfaction predicate | Selected exact signatures |','| --- | --- | --- |']
 for t in w['transitions']:
  signatures='; '.join(p['source_kind']+' — '+p['relation_kind_ref']+' → '+p['target_kind'] for p in t['selected_relation_signatures']) or 'Per-run closure required; no inferred connection'
  lines.append('| '+t['from_state']+' → '+t['to_state']+' | '+t['satisfaction_evidence_contract']['predicate']+' | '+signatures+' |')
 lines+=['']
lines+=['## Extension and recovery gaps','','Project/Product representation and Method carrier closure remain exact semantic members for R08. W02/W03 bind runtime actor, check, qualifier and domain lifecycle evidence. C14 handles new exact pairs or semantic questions; existing pairs never grant an edge or permission. Known invalid transitions are rejected before mutation. Uncertain effects are recorded as indeterminate and inspected before scoped reconciliation.','','## Schema boundary','','workflow-run.schema.json preserves original reference contracts through the exact vendored common.schema.json dependency. It adds a workflow discriminator with workflow-specific closed state domains and explicit independent status axes. It is a protocol record, not a newly admitted domain artifact. Transition-contracts.json carries semantic predicates requiring runtime checks; JSON shape validation alone cannot prove them.','']
(PACKAGE/'design/workflow-contracts.md').write_text('\n'.join(lines))
put(PACKAGE/'design/schema-dependencies.json',{'authority_effect':'none','dependencies':[{'source_binding':binding(common),'local_path':'schemas/common.schema.json','status':'exact-vendored-dependency'}]})
print(json.dumps({'workflows':len(contracts),'transitions':sum(len(w['transitions']) for w in contracts),'authority_effect':'none'}))
