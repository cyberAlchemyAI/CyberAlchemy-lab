"""Qualified history hypotheses,finite append frames and actual generic/project/native boundary observations."""
import ast,copy,hashlib,json,types
from pathlib import Path
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['history','subject','stream','semantic_event_id','semantic_event_digest','semantic_cursor','upstream_evidence','complete_state','owner','source_epoch','registry_epoch']
SUPPORT=['canonical_selection','complete_state_validation','semantic_lookup','exact_event_join','hash_verification','upstream_evidence_authentication','append_only_storage','prior_entry_retention','scope_use','authority_separation']
def profiles():
 context={n:'hyp:'+n for n in AXES};base={'context':context,'query':dict(context),'supports':{n:True for n in SUPPORT},'is_policy':False,'is_decision':False,'is_semantic_history':False,'infers_authority':False,'infers_source_truth':False,'infers_external_effect':False,'actual_claim':False,'history_current':True,'bindings_current':True};rows=[]
 def add(id,change,reject=False,use=True):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['context']!=x['query']:errors.append('exact-history-observation-mismatch')
  if not all(x['supports'].values()):errors.append('missing-qualified-support')
  if any(x[n] for n in ['is_policy','is_decision','is_semantic_history','infers_authority','infers_source_truth','infers_external_effect','actual_claim']):errors.append('unverified-inferred-role-or-outcome')
  allowed=not errors and x['history_current'] and x['bindings_current'];assert bool(errors)==reject and allowed==use,(id,errors)
  rows.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'observations':{'actual_history_state_join_evidence_append_retention_verified':False,'source_fidelity_accepted':False,'use_allowed_under_hypotheses':allowed},'actual_runtime_execution':False})
 add('qualified-complete-observation-with-upstream-authority-separate',lambda x:None)
 for n in AXES:add('mismatched-'+n,lambda x,n=n:x['query'].update({n:'hyp:other'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in ['is_policy','is_decision','is_semantic_history','infers_authority','infers_source_truth','infers_external_effect','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-history-no-reuse',lambda x:x.update(history_current=False),False,False);add('changed-bindings-no-reuse',lambda x:x.update(bindings_current=False),False,False)
 return rows
def frames():
 event={'id':'hyp:e1','state':{'confidence':'hyp:c','challenge':'hyp:contract'},'semantic_ref':{'id':'hyp:s1','digest':'hyp:d','cursor':1},'evidence':['hyp:decision']};base={'before':[event],'after':[copy.deepcopy(event)],'append_authorized':False,'history_writes_decision':False,'history_patches_semantic_state':False,'actual_claim':False};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['after'][:len(x['before'])]!=x['before']:errors.append('prior-complete-entry-prefix-changed')
  if len(x['after'])>len(x['before']) and not x['append_authorized']:errors.append('append-without-separate-authorization')
  if x['history_writes_decision'] or x['history_patches_semantic_state']:errors.append('observation-originates-upstream-or-semantic-change')
  if x['actual_claim']:errors.append('actual-temporal-proof-unverified')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'universal_temporal_proof':False,'actual_runtime_execution':False})
 add('unchanged-history-prefix-retained',lambda x:None)
 add('authorized-hypothetical-observation-append',lambda x:(x['after'].append({**copy.deepcopy(event),'id':'hyp:e2'}),x.update(append_authorized=True)))
 add('append-without-authorization',lambda x:x['after'].append({**copy.deepcopy(event),'id':'hyp:e2'}),True)
 add('prior-entry-deleted',lambda x:x.update(after=[]),True)
 for n in ['id','evidence']:add('prior-entry-mutated-'+n,lambda x,n=n:x['after'][0].update({n:'hyp:changed'}),True)
 for n in ['confidence','challenge']:add('prior-complete-state-mutated-'+n,lambda x,n=n:x['after'][0]['state'].update({n:'hyp:changed'}),True)
 for n in ['id','digest','cursor']:add('prior-exact-semantic-join-mutated-'+n,lambda x,n=n:x['after'][0]['semantic_ref'].update({n:'hyp:changed'}),True)
 add('new-observation-may-use-same-semantic-event',lambda x:(x['after'].append({**copy.deepcopy(event),'id':'hyp:e2'}),x.update(append_authorized=True)))
 add('history-originates-decision',lambda x:x.update(history_writes_decision=True),True)
 add('history-patches-semantic-state',lambda x:x.update(history_patches_semantic_state=True),True)
 add('actual-history-compliance-claim',lambda x:x.update(actual_claim=True),True)
 return rows
def extracted(raw,path,names,namespace):
 tree=ast.parse(raw,filename=str(path));selected=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names]
 if {x.name for x in selected}!=set(names):raise ValueError('Missing pure bound functions')
 exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace);return namespace
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];row=next(x for x in current if x['semantic_kind']=='governance-event-history');pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes());paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/record.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/RECORD.md','generator':b.ROOT/artifact['source_direction']['generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/'authority/ontology-integration/candidates/0002-carrier-materialization/validate.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','native_runtime':b.ROOT/'ontology-lifecycle/runtime/src/lib.rs','project_validator':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/sources.py','project_common':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/common.py','project_semantic':b.ROOT/'authority/admissions/governance-transaction-surface/v1/instances/project-semantic-event-history.json','project_governance':b.ROOT/'authority/admissions/governance-transaction-surface/v1/instances/project-governance-event-history.json'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-governance-event-history-v1-binding',[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']]==['cal.artifact-type.governance-event-history/v1'] and len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]))
 ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('root-descriptor-binding',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 renderer=extracted(raw['generator'],paths['generator'],['render_record'],{'json':json})['render_record'];before=copy.deepcopy(fixture);ck('two-fixture-renders-exact',renderer(fixture).encode()==renderer(fixture).encode()==raw['fixture_projection']);ck('render-input-preserved',fixture==before)
 expected='\n'.join(['<!-- GENERATED FILE: canonical data is artifact.json. -->','',f"# {artifact['name']}/v1",'',artifact['distinct_validation_purpose'],'','## Claim ceiling','',artifact['claim_ceiling'],'']).encode();ck('actual-generator-artifact-template-projection-exact',expected==raw['artifact_projection'] and 'item["distinct_validation_purpose"]' in raw['generator'].decode())
 ck('closed-top-payload-event-and-exact-join-shapes',all(x['additionalProperties'] is False for x in [schema,schema['properties']['payload'],schema['properties']['payload']['properties']['events']['items'],schema['properties']['payload']['properties']['events']['items']['properties']['semantic_event_ref']]))
 ck('manifest-external-event-record-index-without-inline-full-state','record_ref' in schema['properties']['payload']['properties']['events']['items']['required'] and 'complete_resulting_governance_state' not in schema['properties']['payload']['properties']['events']['items']['properties'])
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('four-hostile-fixtures-rejected',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles))
 tree=ast.parse(raw['validator']);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');code=ast.get_source_segment(raw['validator'].decode(),fn)
 ck('package-validator-generic-no-state-hash-chain-join-resolution',all(n not in code for n in ['semantic_event_ref','event_digest','previous_event_digest','governance_cursor','complete_resulting_governance_state','upstream_governance_evidence_refs']) and 'dump(package/' in code)
 native=raw['native_runtime'].decode();ck('native-distinct-complete-state-event-structure-inspected','pub struct GovernanceEvent {' in native and 'pub complete_resulting_governance_state: OntologyGovernanceState' in native and 'pub struct ExactSemanticEventReference {' in native)
 ck('native-governance-validation-and-append-boundaries-inspected',all(n in native for n in ['GOVERNANCE_CURSOR_NOT_CONTIGUOUS','GOVERNANCE_EVENT_ID_DUPLICATE','GOVERNANCE_REFERENCE_MISMATCH','GOVERNANCE_EVENT_CHAIN_BROKEN','EXPECTED_STREAM_VERSION_MISMATCH','validate_governance_history(&self.semantic_events, &proposed)?;','persist_batch(directory, &writes)?;']))
 derr=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not derr,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in derr],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not errors)==accept,(id,errors);probes.append({'case_id':id,'record':x,'schema_accepted':not errors,'expected_schema_acceptance':accept,'errors':errors,'actual_state_event_hash_join_evidence_append_or_retention_verified':False})
 def event(x):return x['payload']['events'][0]
 probe('unresolved-event-record-and-upstream-evidence-accepted',lambda x:(event(x).update(record_ref='absent:record',upstream_governance_evidence_refs=['absent:evidence'])),True)
 probe('no-inline-complete-governance-state-required',lambda x:None,True)
 probe('semantic-id-digest-cursor-unrelated-accepted',lambda x:event(x).update(semantic_event_ref={'semantic_event_id':'other:event','semantic_event_digest':'0'*64,'semantic_cursor':1}),True)
 probe('wrong-event-and-chain-digests-accepted',lambda x:(event(x).update(event_digest='0'*64),x['payload'].update(chain_digest='0'*64)),True)
 probe('duplicate-identical-events-accepted',lambda x:x['payload']['events'].append(copy.deepcopy(event(x))),True)
 probe('nongenesic-null-previous-digest-accepted',lambda x:x['payload']['events'].append({**copy.deepcopy(event(x)),'event_id':'other:event','governance_cursor':2}),True)
 probe('noncontiguous-cursor-accepted',lambda x:event(x).update(governance_cursor=99),True)
 probe('latest-cursor-event-list-mismatch-accepted',lambda x:x['payload'].update(latest_governance_cursor=999),True)
 probe('unmatched-previous-event-digest-accepted',lambda x:event(x).update(previous_event_digest='f'*64),True)
 probe('out-of-order-events-accepted',lambda x:x['payload']['events'].insert(0,{**copy.deepcopy(event(x)),'event_id':'other:event','governance_cursor':2}),True)
 probe('same-history-id-changed-semantic-state-ref-accepted',lambda x:event(x).update(record_ref='other:state'),True)
 probe('whitespace-subject-stream-owner-scope-and-event-id-accepted',lambda x:(x.update(owner_ref=' ',scope_ref=' '),x['payload'].update(subject_ref=' ',stream_id=' '),event(x).update(event_id=' ',record_ref=' ')),True)
 probe('empty-top-level-evidence-and-successor-sets-accepted',lambda x:x.update(evidence_refs=[],successor_refs=[]),True)
 probe('record-state-admitted-text-accepted-with-no-authority-effect',lambda x:x.update(record_state='admitted'),True)
 probe('permission-sounding-claim-accepted-with-no-effect',lambda x:x.update(claim_ceiling='This history originates and authorizes all admissions.'),True)
 probe('unbounded-positive-integer-cursors-accepted',lambda x:(event(x).update(governance_cursor=10**100),x['payload'].update(latest_governance_cursor=10**100)),True)
 probe('empty-events-rejected',lambda x:x['payload'].update(events=[]),False)
 probe('empty-upstream-evidence-rejected',lambda x:event(x).update(upstream_governance_evidence_refs=[]),False)
 probe('duplicate-upstream-evidence-rejected',lambda x:event(x)['upstream_governance_evidence_refs'].append(event(x)['upstream_governance_evidence_refs'][0]),False)
 for n in ['append_only','semantic_patch_forbidden','event_records_are_replay_source','history_manifest_is_event_index']:probe('false-'+n+'-rejected',lambda x,n=n:x['payload'].update({n:False}),False)
 for id,val in [('zero',0),('negative',-1),('fraction',1.5),('boolean',True)]:probe('invalid-governance-cursor-'+id+'-rejected',lambda x,val=val:event(x).update(governance_cursor=val),False)
 for id,val in [('short','a'),('uppercase','A'*64),('nonhex','z'*64)]:probe('invalid-event-digest-'+id+'-rejected',lambda x,val=val:event(x).update(event_digest=val),False)
 probe('missing-semantic-event-digest-rejected',lambda x:event(x)['semantic_event_ref'].pop('semantic_event_digest'),False)
 probe('missing-event-record-ref-rejected',lambda x:event(x).pop('record_ref'),False)
 probe('inline-full-state-extra-field-rejected',lambda x:event(x).update(complete_resulting_governance_state={'confidence':'high'}),False)
 for n in ['implicit_admission','derived_authority','runtime_activation']:probe('extra-'+n+'-rejected',lambda x,n=n:x.update({n:True}),False)
 probe('authority-effect-admitted-rejected',lambda x:x.update(authority_effect='admitted'),False)
 # Execute only the existing pure project function and its exact bound helpers on captured in-memory bytes.
 ns=extracted(raw['project_common'],paths['project_common'],['RuntimeFault','require','digest'],{'hashlib':hashlib,'json':json});extracted(raw['project_validator'],paths['project_validator'],['validate_histories'],ns);histories={'project-semantic-event-history':docs['project_semantic'],'project-governance-event-history':docs['project_governance']};project=[]
 def gov(x):return x['project-governance-event-history']['payload']
 def reseal(x):
  previous=None
  for e in gov(x)['events']:
   e['previous_event_digest']=previous;e['event_digest']=ns['digest']({k:z for k,z in e.items() if k!='event_digest'});previous=e['event_digest']
  gov(x)['chain_digest']=ns['digest']([e['event_digest'] for e in gov(x)['events']])
 def project_case(id,change,accepted):
  x=copy.deepcopy(histories);change(x);before=copy.deepcopy(x);error=None
  try:ns['validate_histories'](x)
  except ns['RuntimeFault'] as err:error=str(err)
  assert (error is None)==accepted and x==before,(id,error)
  project.append({'case_id':id,'input_sha256':ns['digest'](x),'pure_checker_accepted':error is None,'expected_acceptance':accepted,'error':error,'input_preserved':True,'actual_runtime_execution':False,'whole_definition_or_append_transition_proof':False})
 project_case('captured-four-event-project-history-integrity-and-joins',lambda x:None,True)
 project_case('cursor-mismatch-rejected',lambda x:gov(x)['events'][0].update(governance_cursor=2),False)
 project_case('previous-chain-mismatch-rejected',lambda x:gov(x)['events'][1].update(previous_event_digest='0'*64),False)
 project_case('unsealed-summary-change-rejected',lambda x:gov(x)['events'][0].update(governance_summary='changed'),False)
 project_case('chain-digest-mismatch-rejected',lambda x:gov(x).update(chain_digest='0'*64),False)
 project_case('latest-watermark-mismatch-rejected',lambda x:gov(x).update(latest_governance_cursor=99),False)
 for n,val in [('semantic_event_id','absent:event'),('semantic_event_digest','0'*64),('semantic_cursor',999)]:project_case('resealed-exact-join-mismatch-'+n+'-rejected',lambda x,n=n,val=val:(gov(x)['events'][0]['semantic_event_ref'].update({n:val}),reseal(x)),False)
 project_case('resealed-upstream-evidence-empty-not-checked-by-this-function',lambda x:(gov(x)['events'][0].update(upstream_governance_evidence_refs=[]),reseal(x)),True)
 project_case('resealed-complete-state-summary-truth-not-checked',lambda x:(gov(x)['events'][0].update(governance_summary='All claims are true.'),reseal(x)),True)
 project_case('resealed-duplicate-governance-event-id-not-checked',lambda x:(gov(x)['events'][1].update(event_id=gov(x)['events'][0]['event_id']),reseal(x)),True)
 project_case('append-only-flag-not-checked-by-this-function',lambda x:gov(x).update(append_only=False),True)
 ck('pure-project-history-function-accepted-selected-bytes',project[0]['pure_checker_accepted'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-GovernanceEventHistory-profile/v1-candidate','status':'PASS-for-hypothetical-history-qualification-and-selected-generic-project-native-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'dedicated_current_carrier_selection':{'direct_definition_binding_types':['cal.artifact-type.governance-event-history/v1'],'dedicated_current_carrier_established':True,'exact_definition_binding':binding[0]},'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'descriptor_version':artifact['version'],'carrier_schema_ref':artifact['schema_ref'],'fixture_kind':fixture['kind'],'fixture_status':fixture['record_state'],'carrier_manifest_not_inline_state':True,'generic_project_native_common_carrier_map_accepted':False,'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_history_frames':frames(),'project_pure_function_controls':project,'project_pure_function_executed_on_captured_in_memory_records':True,'project_events_selected':{k:len(x['payload']['events']) for k,x in histories.items()},'native_runtime_source_inspected':True,'native_runtime_executed':False,'bound_package_validator_executed':False,'bound_package_validator_static_source_inspected':True,'generator_module_or_materialization_writer_executed':False,'historical_source_current_definition_shape':shape,'fixture_claim_authentication_or_authority_verified':False,'actual_history_state_append_replay_or_external_effect_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Current generic index/schema/pure projections and captured project integrity/join function;native complete-state/hash/join/append code statically inspected. No universal runtime proof,accepted generic/project/native maps,actual append/storage/decision/authority,source-owner fidelity or shared closure.'}
 b.unchanged(list(refs.values())+context['sources']+report['checker_bindings']+report['input_refs']);b.external_current(context);assert runtime==v.f.current_bindings()
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh history carrier/profiles differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'frames':len(x['finite_history_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_history_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(z['schema_accepted'] for z in x['schema_probes']),'catalog_checks':x['actual_check_count'],'project_pure_function_controls':len(x['project_pure_function_controls'])},indent=2))
if __name__=='__main__':main()
