"""Pure structural fixtures only; no genuine Work, Tool, Workflow or Session effects."""
import ast,copy,hashlib,importlib.util,json,sys
from pathlib import Path
from jsonschema import ValidationError
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');HERE=Path(__file__).absolute().parent
EXPECTED='bd9814929bd91c7093a3d0628077e7331f7865c7dc3fd2b1d1ca469f0052257f'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def guard():
 p=HERE/'input-selection.json';assert sha(p.read_bytes())==EXPECTED
 for row in json.loads(p.read_bytes())['files']:
  q=ROOT/row['path'];assert not any(t.is_symlink() for t in [q,*q.parents]);assert sha(q.read_bytes())==row['sha256']
 return len(json.loads(p.read_bytes())['files'])
def package(name,p):
 spec=importlib.util.spec_from_file_location(name,p/'__init__.py',submodule_search_locations=[str(p)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
entry=guard();package('_T31_output_controls',HERE);O=__import__('_T31_output_controls.output_contracts',fromlist=['*']);P=__import__('_T31_output_controls.producer_outputs',fromlist=['*']);L=__import__('_T31_output_controls.lesson_consumer',fromlist=['*'])
original=ROOT/'product/lab/release-candidates/v1/interface/workflow-transition-v1';package('_T31_original_kernel_controls',original);K=__import__('_T31_original_kernel_controls.kernel',fromlist=['*']);F=__import__('_T31_original_kernel_controls.fixtures',fromlist=['*'])
catalog_raw=(HERE/'carrier-catalog.json').read_bytes();catalog=json.loads(catalog_raw);docs={row[key]:(ROOT/row[key]).read_bytes() for row in catalog['rows'] for key in ['schema_path','artifact_path']};carriers=O.OriginalCarriers(catalog_raw,'b2709686d7a34ff704ebaa4c7dc78c18281208adfe2daeedf84fc5a0705e6ed8',docs)
cases=[]
def refused(label,fn):
 try:fn()
 except (O.OutputRefusal,ValueError,ValidationError):cases.append({'case':label,'result':'PASS-refused'})
 else:raise AssertionError(label+' unexpectedly accepted')
# One actual original engineering definition, using explicitly synthetic current/authority facts.
message,facts=F.build();definition_raw=(ROOT/'docs/proposals/0007-lab-integrated-schema-package/workflows/engineering.json').read_bytes();definition=json.loads(definition_raw);transition=next(t for t in definition['transitions'] if t['transition_ref']=='transition:engineering:assessed');run=json.loads(facts['run_raw']);scope=facts['host_grant']['scope_ref'];actor=facts['authenticated_actor']
def binding(ref,raw):return {'ref':ref,'sha256':sha(raw)}
def header(identity,carrier,rawsha='c'*64):return {'scope_ref':scope,'identity_ref':identity,'version_ref':identity+'@candidate.1','carrier_ref':carrier,'byte_sha256':rawsha}
run['definition_binding']=binding('original-definition:engineering',definition_raw);run['state']=transition['from_state'];run_raw=K.encoded(run)
message.update(definition_binding=run['definition_binding'],run_binding=binding('isolated-run:engineering',run_raw),transition_ref=transition['transition_ref'],expected_state=run['state'],input_artifacts=[header('isolated-input:'+str(i),c) for i,c in enumerate(transition['input_carriers'])])
obligations={ref:[{'ref':'isolated-evidence:'+ref,'sha256':'d'*64}] for ref in [*transition['authority_requirement_refs'],*transition['precondition_refs'],*transition['satisfaction_check_refs'],*transition['relation_requirement_refs']]}
def check(ref):return {'check_ref':'isolated-check:'+ref,'obligation_ref':ref,'result':'pass','evidence_bindings':obligations[ref],'claim_ceiling':'Structural fixture only; no native original or authority claim.'}
authority=json.loads(facts['authority_raw']);authority['checks']=[check(ref) for ref in transition['authority_requirement_refs']];authority['evidence_bindings']=next(iter(obligations.values()))
satisfaction=json.loads(facts['satisfaction_raw']);satisfaction['subject_binding']=message['run_binding'];satisfaction['checks']=[check(ref) for ref in [*transition['precondition_refs'],*transition['satisfaction_check_refs'],*transition['relation_requirement_refs']]]
message['authority_evaluation_binding']=binding('isolated-authority:engineering',K.encoded(authority));message['satisfaction_report_binding']=binding('isolated-satisfaction:engineering',K.encoded(satisfaction));grant=facts['host_grant'];grant.update(actor_role_refs=transition['actor_role_refs'],permitted_transitions=[transition['transition_ref']],obligation_bindings=obligations,**{k:message[k] for k in ['run_binding','definition_binding','authority_evaluation_binding','satisfaction_report_binding','action_receipt_bindings']})
headers={h['version_ref']:{'artifact':h,'posture':'local-admitted-current','semantic_kind':'isolated-schema-fixture'} for h in [run[k] for k in ['intent','intent_resolution','work','coordination_context']]+message['input_artifacts']};facts.update(definition_raw=definition_raw,run_raw=run_raw,authority_raw=K.encoded(authority),satisfaction_raw=K.encoded(satisfaction),selected_headers=headers,selected_obligations=obligations)
plan=K.plan(message,**facts)
body=json.loads((ROOT/'authority/artifact-types/work-outcome-assessment/v1/fixtures/valid/record.json').read_bytes());body['scope_ref']=scope;body['payload']['subject_ref']=run['work']['version_ref'];raw=K.encoded(body);artifact=header(body['node_id'],'cal.artifact-type.work-outcome-assessment/v1',sha(raw));outputs=[artifact];raws={artifact['version_ref']:raw}
attached=O.attach_outputs(K,plan,outputs=outputs,raw_by_ref=raws,carriers=carriers,scope_ref=scope,work_ref=run['work']['version_ref'])
assert attached['event']['output_artifact_refs']==outputs and attached['next_run']['outcome_assessment']==artifact
assert set(attached['next_run'])==set(run) and 'output_artifact_refs' not in attached['next_run']
assert attached['event']['canonical_admission_granted'] is False and attached['work_satisfaction_asserted'] is False
assert attached['next_run']['event_bindings'][-1]['sha256']==K.digest(attached['event']) and attached['next_run_structural_sha256']==K.digest(attached['next_run'])
K.validate_shapes(message,definition,attached['next_run'],authority,satisfaction)
cases.append({'case':'real original engineering:assessed definition plus synthetic original-carrier output linked through existing fields','result':'PASS-structural-fixture-only'})
refused('missing required output',lambda:O.attach_outputs(K,plan,outputs=[],raw_by_ref={},carriers=carriers,scope_ref=scope,work_ref=run['work']['version_ref']))
refused('duplicate output revision',lambda:O.attach_outputs(K,plan,outputs=outputs*2,raw_by_ref=raws,carriers=carriers,scope_ref=scope,work_ref=run['work']['version_ref']))
refused('missing original bytes',lambda:O.attach_outputs(K,plan,outputs=outputs,raw_by_ref={},carriers=carriers,scope_ref=scope,work_ref=run['work']['version_ref']))
refused('wrong independently selected scope',lambda:O.attach_outputs(K,plan,outputs=outputs,raw_by_ref=raws,carriers=carriers,scope_ref='project:foreign',work_ref=run['work']['version_ref']))
refused('unrelated exact Work outcome lineage',lambda:O.attach_outputs(K,plan,outputs=outputs,raw_by_ref=raws,carriers=carriers,scope_ref=scope,work_ref='work:foreign@1'))
refused('wrong carrier version',lambda:carriers.output({**artifact,'carrier_ref':'cal.artifact-type.work-outcome-assessment/v999'},raw,scope_ref=scope))
refused('wrong original byte hash',lambda:carriers.output({**artifact,'byte_sha256':'0'*64},raw,scope_ref=scope))
refused('unselected extra schema document',lambda:O.OriginalCarriers(catalog_raw,sha(catalog_raw),{**docs,'foreign.json':b'{}'}))
refused('wrong independent carrier catalog',lambda:O.OriginalCarriers(catalog_raw,'0'*64,docs))
# The actual original W03 materialization review structure, instantiated as a labelled fixture only.
review={'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,'work_effect':{'from_version_ref':run['work']['version_ref'],'applied':False},'member_records':[{'version_ref':artifact['version_ref'],'identity_ref':artifact['identity_ref'],'record_sha256':artifact['byte_sha256']}]}
P.verify_original_materialization('engineering',K.encoded(review),outputs=outputs,work_ref=run['work']['version_ref']);cases.append({'case':'original W03 member/Work linkage shape','result':'PASS-structural-fixture-only'})
refused('foreign producer Work',lambda:P.verify_original_materialization('engineering',K.encoded(review),outputs=outputs,work_ref='work:foreign@1'))
refused('unindexed producer output',lambda:P.verify_original_materialization('engineering',K.encoded({**review,'member_records':[]}),outputs=outputs,work_ref=run['work']['version_ref']))
refused('review is not admission authority',lambda:P.verify_original_materialization('engineering',K.encoded({**review,'canonical_effects_applied':1}),outputs=outputs,work_ref=run['work']['version_ref']))
# Concrete W06 consumer gate refuses current attribution-only metadata.
application={'kind':'lesson-application','authority_effect':'none','payload':{'application_posture':'candidate-attributed-no-tool-dispatch','lesson_revision_ref':'lesson:isolated@1','session_ref':'session:isolated'}};ar=K.encoded(application)
refused('current attribution-only lesson application cannot supply observed producer input',lambda:L.observed_research_builder_input(application_raw=ar,manifest_raw=b'{}',repaired_raw=b'pass',expected_application_sha256=sha(ar),expected_manifest_sha256=sha(b'{}'),lesson_ref='lesson:isolated@1',selected_source_head='isolated',session_ref='session:isolated'))
for q in HERE.glob('*.py'):ast.parse(q.read_bytes())
report={'schema_version':'lab-T31-pure-output-contract-controls/v1-candidate','result':'PASS-structural-only','authority_effect':'none','actual_owner_outcome':None,'cases':cases,'case_count':len(cases),'original_definition_binding':binding(str((ROOT/'docs/proposals/0007-lab-integrated-schema-package/workflows/engineering.json').relative_to(ROOT)),definition_raw),'exact_input_entry_rows':entry,'exact_input_exit_rows':guard(),'original_output_carriers':len(carriers.rows),'original_workflow_run_fields_preserved':True,'new_candidate_event_and_run_digest_rebound':True,'actual_output_producer_or_Work_Tool_WorkflowRun_Session_native_or_journal_constructor_executed':False,'current_native_source_or_owner_permission_or_work_satisfaction_qualified':False,'current_shared_API_or_capture3_modified':False}
p=HERE/'pure-controls-result.json'
with p.open('x') as stream:json.dump(report,stream,sort_keys=True,indent=2);stream.write('\n')
print(json.dumps({'result':report['result'],'cases':len(cases),'input_rows':entry,'sha256':sha(p.read_bytes())}))
