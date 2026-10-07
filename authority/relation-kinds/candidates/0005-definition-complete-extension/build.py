#!/usr/bin/env python3
"""Build the definition-complete closed relation surface for Lab review."""
from __future__ import annotations
import hashlib,json
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent; LAB=ROOT.parents[3]
BASE=LAB/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json'
COVERAGE=LAB/'authority/artifact-types/candidates/0011-definition-carrier-coverage-audit/audit.json'
ADMISSION=LAB/'authority/artifact-types/candidates/0010-step5-postimage-registry/admission-manifest.json'
STEP7=LAB/'authority/ontology-integration/candidates/0002-carrier-materialization/carrier-postimages.json'
DEFREG=LAB/'authority/definitions/registry.json'
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def pairs(*xs): return [{'source_kind':a,'target_kind':b} for a,b in xs]

NEW_AXES={
 'relation.addresses-intent':('axis.intent-addressing','Which exact Intent is this governed subject intended to address?',
  [('product','intent'),('project','intent'),('goal','intent'),('research-inquiry','intent'),('product-capability','intent'),('agent-assignment','intent')],
  ['intent_resolution_ref','addressing_role'],['satisfaction','completion','authority','membership']),
 'relation.acts-for':('axis.bounded-representation','Which Principal is this Agent Instance acting for under one exact Delegation?',
  [('agent-instance','principal')],['delegation_ref','scope_ref','effective_period','revocation_state'],['identity-equivalence','ownership-transfer','unrestricted-authority']),
 'relation.has-capability':('axis.agent-capability-declaration','Which Agent Capability is declared for this Agent Profile or Agent Instance?',
  [('agent-profile','agent-capability'),('agent-instance','agent-capability')],['capability_version_ref','declaration_basis'],['authority','successful-performance','product-value']),
 'relation.performs':('axis.agent-performance-attribution','Which attributable activity is performed or attempted by this Agent Instance?',
  [('agent-instance',x) for x in ('agent-action','work','research-run','experiment-run','review')],['session_ref','participation_role','action_posture'],['ownership','approval','admission','successful-effect']),
 'relation.uses-tool':('axis.tool-use','Which Tool or Implementation does this Agent Session or Agent Action use?',
  [(s,t) for s in ('agent-session','agent-action') for t in ('tool','implementation')],['tool_version_ref','invocation_contract_ref','use_role'],['realization','conformance','ownership','authority']),
 'relation.produces':('axis.attributable-production','Which governed output was produced by this Agent Action?',
  [('agent-action',t) for t in ('generated-output','observation','operational-observation','measurement-result','evidence-set','finding','definition','typed-relation','agent-reflection','operational-lesson','lesson-application','classification-assignment','failure-occurrence','failure-assessment','feedback-record','drift-assessment','improvement-signal','work-outcome-assessment','challenge-event')],
  ['action_receipt_ref','production_role','output_posture'],['acceptance','correctness','admission','authority-effect']),
 'relation.applies-lesson':('axis.lesson-application','Which exact Operational Lesson revision was used or deliberately not used by this Lesson Application?',
  [('lesson-application','operational-lesson')],['lesson_revision_ref','application_posture','applicability_assessment_ref','instruction_precedence'],['compliance','benefit','authority','method-use']),
 'relation.occurs-during':('axis.occurrence-envelope','In which exact execution envelope did this Failure Occurrence happen?',
  [('failure-occurrence',t) for t in ('agent-action','agent-session','work','research-run','experiment-run')],['envelope_version_ref','temporal_scope'],['cause','blame','severity','recovery']),
 'relation.violates':('axis.boundary-violation','Which exact expected boundary does evidence indicate was not satisfied?',
  [('failure-occurrence',t) for t in ('contract','policy','schema','challenge-contract')],['boundary_version_ref','evidence_posture'],['cause','severity','authority','automatic-failure-confirmation']),
 'relation.affects':('axis.scoped-impact','Which exact subject was affected, under what declared scope?',
  [(s,t) for s in ('failure-occurrence','incident') for t in ('agent-session','project','product','product-capability','agent-capability','implementation','person-reference','work','generated-output','artifact-type','ontology')],['impact_scope','evidence_posture'],['cause','severity','blame','ownership']),
 'relation.responds-to':('axis.operational-response','Which Failure Occurrence or Incident is this Agent Action intended to address?',
  [('agent-action','failure-occurrence'),('agent-action','incident')],['response_role','intended_outcome'],['recovery-success','cause','closure','authority']),
 'relation.controls':('axis.failure-control','Which Failure Mode is this Failure Control Binding intended to control?',
  [('failure-control-binding','failure-mode')],['control_role','control_version_ref','installation_posture'],['installation','execution','effectiveness','authority']),
 'relation.challenges':('axis.contestability-target','Which exact governed subject revision does this Challenge Event challenge?',None,
  ['challenge_contract_ref','challenge_mode','challenged_version_ref'],['suspension','reversal','contradiction-proof','authority']),
 'relation.addresses-improvement-target':('axis.improvement-target-addressing','Which Improvement Target is this Research Inquiry intended to address?',
  [('research-inquiry','improvement-target')],['target_version_ref','addressing_role'],['resolution','improvement','priority','authority']),
 'relation.tests-hypothesis':('axis.hypothesis-testing','Which exact Hypothesis is this Experiment Design constructed to test?',
  [('experiment-design','hypothesis')],['hypothesis_version_ref','test_role'],['support','contradiction','truth','successful-execution']),
 'relation.consumes-view':('axis.view-consumption','Which immutable Context View or Ontology View did this Agent Session actually consume?',
  [('agent-session','context-view'),('agent-session','ontology-view')],['view_digest','cursor','consumption_purpose'],['currentness','source-authority','memory-ownership','request-fulfillment']),
 'relation.profiled-by':('axis.agent-profile-binding','Which exact Agent Profile revision configures this Agent Instance?',
  [('agent-instance','agent-profile')],['profile_version_ref','binding_ref'],['conformance','capability','authority','identity-continuity']),
}

EXISTING_ADDITIONS={
 'relation.member-of':[('agent-assignment','project'),('project-state','project'),('failure-occurrence','incident'),('classification-value','classification-scheme'),('agent-instance','agent-session'),('agent-action','agent-session')],
 'relation.contributes-to':[('agent-action','goal'),('agent-action','product')],
 'relation.uses-method':[('agent-action','method')],
 'relation.evaluates':[('failure-assessment','failure-occurrence'),('lesson-outcome-assessment','lesson-application'),('work-outcome-assessment','work'),('work-outcome-assessment','agent-action'),('preference-application-assessment','communication-preference')],
 'relation.originates-from':[('operational-observation','source'),('feedback-record','source'),('drift-assessment','source')],
 'relation.derives-from':[
  ('agent-reflection','agent-session'),('agent-reflection','agent-action'),('agent-reflection','observation'),('agent-reflection','operational-observation'),('agent-reflection','finding'),('agent-reflection','evidence-set'),('agent-reflection','feedback-record'),('agent-reflection','failure-assessment'),('agent-reflection','work-outcome-assessment'),
  ('operational-lesson','agent-reflection'),('operational-lesson','failure-assessment'),('operational-lesson','finding'),('operational-lesson','evidence-set'),('operational-lesson','lesson-outcome-assessment'),('operational-lesson','feedback-record'),
  ('improvement-target','operational-lesson'),('improvement-target','lesson-outcome-assessment'),('improvement-target','improvement-signal'),
  ('classification-assignment','evidence-set'),('classification-assignment','observation'),('classification-assignment','operational-observation'),('classification-assignment','finding'),('classification-assignment','measurement-result'),('classification-assignment','source'),('classification-assignment','feedback-record'),
  ('improvement-signal','operational-observation'),('improvement-signal','failure-assessment'),('improvement-signal','work-outcome-assessment'),('improvement-signal','drift-assessment')],
 'relation.governed-by':[(s,'policy') for s in ('agent-profile','agent-instance','agent-session','agent-action','operational-lesson','classification-assignment','failure-mode','failure-occurrence','failure-assessment','failure-control-binding','incident','challenge-contract','feedback-record','communication-preference','ontology-node','ontology-edge')]+[('classification-assignment','classification-scheme'),('challenge-event','challenge-contract')],
 'relation.declares-effect-on':[('decision',t) for t in ('operational-lesson','improvement-target','classification-assignment','failure-mode','failure-occurrence','failure-assessment','failure-control-binding','incident','challenge-event','intent-resolution','agent-profile','agent-capability','delegation','communication-preference')],
 'relation.instance-of':[(s,'classification-value') for s in ('agent-instance','agent-action','operational-lesson','failure-mode','failure-occurrence','improvement-target')]+[('failure-occurrence','failure-mode')],
 'relation.assigned-to':[('agent-instance','role'),('agent-instance','responsibility')],
 'relation.asserts-identity-of':[('principal-reference','principal')],
}

EVIDENCE_SOURCES=('evidence-set','observation','measurement-result','operational-observation','finding','feedback-record')
EVIDENCE_TARGETS=('failure-occurrence','failure-assessment','classification-assignment','operational-lesson','lesson-outcome-assessment','work-outcome-assessment','preference-application-assessment','drift-assessment','improvement-signal','challenge-event')
EXISTING_ADDITIONS['relation.evidence-bears-on']=[(s,t) for s in EVIDENCE_SOURCES for t in EVIDENCE_TARGETS]

def main():
 base=load(BASE); coverage=load(COVERAGE); admission=load(ADMISSION); step7=load(STEP7); reg=load(DEFREG)
 kinds={x['semantic_kind'] for x in admission['entries']}
 kinds|={load(LAB/x['artifact_path'])['classification']['semantic_kind'] for x in step7['entries']}
 kinds|={x['artifact_type_ref'].removeprefix('cal.artifact-type.').split('/')[0] for x in coverage['required_actions']}
 base_kinds={k for e in base['entries'] for k in e['source_kinds']+e['target_kinds']}
 kinds|=base_kinds
 NEW_AXES['relation.challenges']=(*NEW_AXES['relation.challenges'][:2],[('challenge-event',k) for k in sorted(kinds)],*NEW_AXES['relation.challenges'][3:])
 additions=deepcopy(EXISTING_ADDITIONS); additions['relation.successor-of']=[(k,k) for k in sorted(kinds)]
 entries=[]; extension_groups=[]
 for old in base['entries']:
  e=deepcopy(old); existing={(p['source_kind'],p['target_kind']) for p in e['allowed_endpoint_pairs']}; requested=additions.get(e['relation_kind_id'],[])
  added=sorted(set(requested)-existing)
  e['allowed_endpoint_pairs']=pairs(*sorted(existing|set(requested))); e['source_kinds']=sorted({p['source_kind'] for p in e['allowed_endpoint_pairs']}); e['target_kinds']=sorted({p['target_kind'] for p in e['allowed_endpoint_pairs']})
  entries.append(e)
  if added: extension_groups.append({'relation_kind_id':e['relation_kind_id'],'extension_kind':'exact-pair-extension','added_pairs':pairs(*added),'unique_question':e['unique_question'],'required_qualifier_axes':e['required_qualifier_axes'],'forbidden_inferences':e['forbidden_inferences'],'lifecycle_rule':'Each Typed Relation binds exact endpoint revisions and has its own lifecycle; endpoint or carrier lifecycle never silently creates, rewrites, or retires the relation.'})
 for rid,(axis,question,ps,quals,forbids) in NEW_AXES.items():
  e={'relation_kind_id':rid,'axis_id':axis,'group':'definition-complete-extension','unique_question':question,'operational_effect':'Records only the named semantic connection with exact endpoints, qualifiers, evidence, owner, lifecycle, and claim ceiling.','required_qualifier_axes':quals,'forbidden_inferences':forbids,'allowed_endpoint_pairs':pairs(*sorted(set(ps))),'source_kinds':sorted({a for a,b in ps}),'target_kinds':sorted({b for a,b in ps}),'absorbed_relation_kinds':[rid],'status':'candidate-axis-orthogonal','authority_effect':'none'}
  entries.append(e); extension_groups.append({'relation_kind_id':rid,'extension_kind':'new-axis','added_pairs':e['allowed_endpoint_pairs'],'unique_question':question,'required_qualifier_axes':quals,'forbidden_inferences':forbids,'lifecycle_rule':'Each relation instance binds exact endpoint revisions and retains independent create, challenge, supersede, and retire state.'})
 entries=sorted(entries,key=lambda x:x['relation_kind_id'])
 defentry=next(x for x in reg['entries'] if x['definition_id']=='cal.definition.typed-connection-extension-rule' and x['lifecycle_state']=='admitted')
 examples={}
 for e in entries:
  p=e['allowed_endpoint_pairs'][0]; examples[e['relation_kind_id']]={'relation_id':f"typed-relation:example-{e['relation_kind_id'].removeprefix('relation.')}",'relation_kind_ref':e['relation_kind_id'],'source_ref':f"{p['source_kind']}:example-001",'target_ref':f"{p['target_kind']}:example-001",'qualifiers':{q:f"example-{q}" for q in e['required_qualifier_axes']},'owner_ref':'role:relation-owner','evidence_refs':['evidence:definition-complete-relation-review'],'lifecycle_state':'candidate','authority_effect':'none','claim_ceiling':'Example demonstrates the exact pair and qualifiers only.'}
 model={'schema_version':'cyberalchemy-lab-definition-complete-relation-model/v1','model_id':'CAL-DEFINITION-COMPLETE-RELATION-MODEL-0005','status':'candidate-complete-awaiting-owner-review','authority_effect':'none','predecessor':{'path':str(BASE.relative_to(LAB)),'sha256':sha(BASE),'relation_kind_count':23},'typed_connection_extension_rule':{'definition_ref':f"{defentry['definition_id']}@{defentry['version']}",'path':defentry['path'],'sha256':defentry['sha256'],'admission_decision_ref':defentry['admission_decision_ref']},'carrier_inputs':{'decision_0069_manifest':{'path':str(ADMISSION.relative_to(LAB)),'sha256':sha(ADMISSION)},'step7_carriers':{'path':str(STEP7.relative_to(LAB)),'sha256':sha(STEP7)},'definition_coverage':{'path':str(COVERAGE.relative_to(LAB)),'sha256':sha(COVERAGE)}},'entries':entries,'connection_extensions':extension_groups,'deferred_axes':[{'relation_kind_id':'relation.subclass-of','reason':'No reviewed hierarchical Classification Scheme instance currently requires a global hierarchy edge. Add only with exact Scheme, value endpoints, qualifiers, and migration rules.'}],'scope_decisions':[{'candidate':'ontology-node-represents-subject','decision':'ontology-local-binding','reason':'Ontology Node/v2 already carries the exact subject revision binding; no global represents axis is created, avoiding identity collapse and wildcard endpoints.'},{'candidate':'agent-instance-profile-binding','decision':'new-global-axis','relation_kind_id':'relation.profiled-by','reason':'Profile binding is neither classification nor demonstrated conformance.'}],'canonical_instance_rule':{'allowed_modes':['projects-as','represented-by'],'dual_writable_copies_forbidden':True},'counts':{'base_relation_kinds':23,'active_relation_kinds':len(entries),'new_relation_kinds':len(NEW_AXES),'deferred_relation_kinds':1,'endpoint_kinds':len(kinds),'declared_endpoint_pairs':sum(len(e['allowed_endpoint_pairs']) for e in entries),'extension_groups':len(extension_groups),'added_endpoint_pairs':sum(len(x['added_pairs']) for x in extension_groups)},'claim_ceiling':'This candidate closes the reviewed global relation surface for the definition-complete Artifact Type model. It admits no Relation Kind, Typed Relation, Artifact Type, instance, ontology assertion, consumer, or runtime.'}
 dump(ROOT/'model.json',model); dump(ROOT/'examples.json',examples)
 lines=['<!-- GENERATED FILE: canonical data is model.json and examples.json. -->','','# Definition-complete relation model','',f"- Active Relation Kinds: `{model['counts']['active_relation_kinds']}`",f"- New Relation Kinds: `{model['counts']['new_relation_kinds']}`",f"- Endpoint kinds: `{model['counts']['endpoint_kinds']}`",f"- Exact ordered pairs: `{model['counts']['declared_endpoint_pairs']}`",'- Wildcards: `0`','- Authority effect: `none`','','## Complete axes','','| Relation Kind | Unique question | Exact pairs |','| --- | --- | ---: |']
 for e in entries: lines.append(f"| `{e['relation_kind_id']}` | {e['unique_question']} | {len(e['allowed_endpoint_pairs'])} |")
 lines += ['','## Deferred and local decisions','','- `relation.subclass-of` is deferred until a reviewed hierarchical Classification Scheme requires it.','- Ontology Node subject representation remains an ontology-local exact binding.','- Agent Instance to Agent Profile uses the independent `relation.profiled-by` axis.','','## Realistic examples','']
 for rid in sorted(examples): lines += [f"### `{rid}`",'', '```json',json.dumps(examples[rid],indent=2,sort_keys=True),'```','']
 lines += ['## Claim ceiling','',model['claim_ceiling'],'']; (ROOT/'MODEL.md').write_text('\n'.join(lines),encoding='utf-8')

if __name__=='__main__': main()
