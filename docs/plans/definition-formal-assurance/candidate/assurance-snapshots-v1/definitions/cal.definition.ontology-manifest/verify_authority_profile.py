"""Candidate Manifest hypotheses and exact carrier/static binding observations; no runtime activation."""
import ast,copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['manifest','ontology','definition_version','owner','state_model','relation_registry','policy_set','runtime_binding','projection_set','challenge_route','configuration_version','source_epoch','registry_epoch']
SUPPORT=['canonical_selection','stable_identity','typed_configuration_bindings','nonempty_policy_projection','exact_reference_closure','configuration_digest','authorized_revision','separate_subject_state','scope_use','separate_runtime_authority']
FORBIDDEN=['subject_replay_source','writes_subject_state','activates_runtime','grants_authority','admits_configuration','actual_claim']
def profiles():
 ctx={n:'hyp:'+n for n in AXES};base={'context':ctx,'query':dict(ctx),'supports':{n:True for n in SUPPORT},**{n:False for n in FORBIDDEN},'manifest_current':True,'bindings_current':True};rows=[]
 def add(id,change,reject=False,use=True):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['context']!=x['query']:errors.append('exact-configuration-context-mismatch')
  if not all(x['supports'].values()):errors.append('missing-hypothetical-support')
  if any(x[n] for n in FORBIDDEN):errors.append('forbidden-state-runtime-authority-claim')
  allowed=not errors and x['manifest_current'] and x['bindings_current'];assert bool(errors)==reject and allowed==use,(id,errors)
  rows.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'use_allowed_under_hypotheses':allowed,'actual_runtime_execution':False,'actual_configuration_or_authority_verified':False,'source_fidelity_accepted':False})
 add('qualified-stable-configuration-under-hypotheses',lambda x:None)
 for n in AXES:add('mismatched-'+n,lambda x,n=n:x['query'].update({n:'hyp:other'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in FORBIDDEN:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-manifest-no-reuse',lambda x:x.update(manifest_current=False),False,False)
 add('changed-binding-no-reuse',lambda x:x.update(bindings_current=False),False,False)
 return rows

def frames():
 source={'identity':'hyp:id','ontology':'hyp:o','runtime':'hyp:r','policy':'hyp:p','projection':'hyp:v'};base={'before':source,'after':copy.deepcopy(source),'successor':dict(source),'revision_authorized_hypothesis':True,'subject_state_before':'hyp:state','subject_state_after':'hyp:state',**{n:False for n in FORBIDDEN}};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['before']!=x['after']:errors.append('retained-record-mutation')
  if any(x['successor'][n]!=x['before'][n] for n in ['identity','ontology']):errors.append('stable-successor-identity-or-ontology-change')
  if x['successor']!=x['before'] and not x['revision_authorized_hypothesis']:errors.append('changed-configuration-without-hypothetical-authorization')
  if x['subject_state_before']!=x['subject_state_after']:errors.append('manifest-writes-represented-state')
  if any(x[n] for n in FORBIDDEN):errors.append('unverified-state-runtime-authority-role')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'universal_temporal_or_authority_proof':False,'actual_runtime_execution':False,'authorization_rule_is_primary_T_axiom':False})
 add('retained-stable-configuration',lambda x:None)
 for n in ['runtime','policy','projection']:add('authorized-hypothetical-successor-changes-'+n,lambda x,n=n:x['successor'].update({n:'hyp:new'}))
 for n in source:add('mutates-retained-'+n,lambda x,n=n:x['after'].update({n:'hyp:new'}),True)
 for n in ['identity','ontology']:add('successor-changes-'+n,lambda x,n=n:x['successor'].update({n:'hyp:new'}),True)
 add('changed-runtime-without-hypothetical-authorization',lambda x:(x['successor'].update(runtime='hyp:new'),x.update(revision_authorized_hypothesis=False)),True)
 add('manifest-changes-subject-state',lambda x:x.update(subject_state_after='hyp:new'),True)
 for n in FORBIDDEN:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 return rows

def extracted(raw,path,names,namespace):
 tree=ast.parse(raw,filename=str(path));selected=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names];assert {x.name for x in selected}==set(names)
 exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace);return namespace

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert [x['artifact_type_ref'] for x in direct]==['cal.artifact-type.ontology-manifest/v1'];row=direct[0];pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes())
 paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/record.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/RECORD.md','generator':b.ROOT/artifact['source_direction']['generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/'authority/ontology-integration/candidates/0002-carrier-materialization/validate.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','native_runtime':b.ROOT/'ontology-lifecycle/runtime/src/lib.rs','project_session':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/session.py','runtime_binding':b.ROOT/'implementation/bindings/ontology-product-event-runtime/v2/binding.json','binding_implementation':b.ROOT/'implementation/bindings/ontology-product-event-runtime/v2/src/lib.rs','binding_admission':b.ROOT/'docs/decisions/0047-ontology-event-runtime-binding-admission/decision.json','runtime_adoption':b.ROOT/'docs/decisions/0048-ontology-event-runtime-adoption/decision.json','versioned_graph_manifest':b.ROOT/'ontology-lifecycle/system-ontology/versions/cal-ontology-runtime-integration-v1/manifest.json','node_fixture':b.ROOT/'authority/artifact-types/ontology-node/v2/fixtures/valid/record.json','semantic_history_fixture':b.ROOT/'authority/artifact-types/semantic-event-history/v1/fixtures/valid/record.json','governance_history_fixture':b.ROOT/'authority/artifact-types/governance-event-history/v1/fixtures/valid/record.json'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-manifest-binding',len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]) and binding[0]['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
 ck('current-registry-records-C70-type-admission',row['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and row['lifecycle_state']=='admitted-current')
 ck('retained-descriptor-and-fixture-candidate-posture',artifact['status']=='candidate-unadmitted' and fixture['record_state']=='candidate' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256'])
 ck('root-descriptor-binding',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 renderer=extracted(raw['generator'],paths['generator'],['render_record'],{'json':json})['render_record'];before=copy.deepcopy(fixture);ck('two-pure-fixture-renders-exact',renderer(fixture).encode()==renderer(fixture).encode()==raw['fixture_projection']);ck('render-input-preserved',fixture==before)
 expected='\n'.join(['<!-- GENERATED FILE: canonical data is artifact.json. -->','',f"# {artifact['name']}/v1",'',artifact['distinct_validation_purpose'],'','## Claim ceiling','',artifact['claim_ceiling'],'']).encode();ck('generator-artifact-template-projection-exact',expected==raw['artifact_projection'] and 'item["distinct_validation_purpose"]' in raw['generator'].decode())
 payload=schema['properties']['payload'];ck('closed-top-and-payload',schema['additionalProperties'] is payload['additionalProperties'] is False)
 ck('fifteen-required-configuration-fields',len(payload['required'])==15 and set(payload['required'])==set(payload['properties']))
 ck('Policy-projection-arrays-unique-but-no-minItems',all(payload['properties'][n]['uniqueItems'] is True and 'minItems' not in payload['properties'][n] for n in ['policy_refs','projection_contract_refs']))
 ck('digest-shape-and-nonreplay-constant',payload['properties']['configuration_digest']=={'pattern':'^[0-9a-f]{64}$','type':'string'} and payload['properties']['subject_replay_source']=={'const':False})
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('four-hostiles-rejected',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles))
 tree=ast.parse(raw['validator']);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');code=ast.get_source_segment(raw['validator'].decode(),fn)
 ck('generic-validator-does-not-resolve-manifest-config',all(n not in code for n in ['ontology_definition_ref','configuration_digest','runtime_binding_ref','policy_refs','projection_contract_refs']) and 'dump(package/' in code)
 native=raw['native_runtime'].decode();event= native.split('pub struct EventStore {',1)[1].split('pub fn subject_ids',1)[0]
 ck('native-EventStore-separate-event-directories-and-cursors-inspected',all(n in event for n in ['semantic_directory','governance_directory','semantic_cursor','governance_cursor','validate_semantic_history','validate_governance_history']))
 ck('no-OntologyManifest-struct-in-selected-native-lib','pub struct OntologyManifest' not in native)
 rejection=native.split('fn reject_noncanonical_source(',1)[1].split('\nfn ',1)[0];ck('native-replay-requires-canonical-event-source-inspected','Some("canonical_event")' in rejection and 'NONCANONICAL_REPLAY_SOURCE' in rejection)
 implementation=raw['binding_implementation'].decode();ck('binding-realization-loads-event-store-not-Manifest-carrier-inspected',all(n in implementation for n in ['pub fn realize_navigation(','pub fn load_realized_runtime(','EventStore::load(root.join("semantic-events"), root.join("governance-events"))']) and 'OntologyManifest' not in implementation)
 sessiontree=ast.parse(raw['project_session']);cls=next(x for x in sessiontree.body if isinstance(x,ast.ClassDef) and x.name=='Session');method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_build');session=ast.get_source_segment(raw['project_session'].decode(),method);ck('Project-session-runtime-head-manifest-marker-inspected','ontology_manifest_ref="runtime-head:" + self.head' in session)
 rb=docs['runtime_binding'];adm=docs['binding_admission'];adopt=docs['runtime_adoption'];fp=fixture['payload']
 ck('fixture-runtime-binding-exact-id-selected',fp['runtime_binding_ref']==rb['binding_id']=='cal.binding.ontology-product-event-runtime/v2')
 ck('recorded-C47-exact-byte-binding-admission-only',adm['status']=='admitted' and adm['authority_effect']=='implementation-binding-admission-only' and adm['subject']['binding_id']==rb['binding_id'] and adm['subject']['path']==refs['runtime_binding']['path'] and adm['subject']['sha256']==refs['runtime_binding']['sha256'])
 ck('recorded-C48-exact-native-byte-runtime-adoption-only',adopt['status']=='adopted' and adopt['authority_effect']=='runtime-adoption-only' and adopt['subject']['binding_id']==rb['binding_id'] and adopt['subject']['runtime_id']==rb['runtime_source']['runtime_id'] and adopt['subject']['path']==refs['native_runtime']['path'] and adopt['subject']['sha256']==refs['native_runtime']['sha256']==rb['runtime_source']['source_sha256'])
 ck('retained-frozen-binding-candidate-not-adopted-field',rb['status']=='test-candidate' and rb['authority_effect']=='none' and rb['runtime_source']['adopted'] is False)
 ck('binding-implementation-material-exact-selected-lib',next(x for x in rb['implementation_material'] if x['path']==refs['binding_implementation']['path'])['sha256']==refs['binding_implementation']['sha256'])
 ck('recorded-admission-and-adoption-exclude-runtime-activation','runtime-activation' in adm['excluded_effects'] and {'runtime-activation','service-start'}<=set(adopt['excluded_effects']))
 mismatches={'node_manifest_ref':docs['node_fixture']['payload']['ontology_manifest_ref'],'manifest_node_id':fixture['node_id'],'semantic_history_ref':fp['semantic_history_ref'],'selected_semantic_history_fixture_id':docs['semantic_history_fixture']['node_id'],'governance_history_ref':fp['governance_history_ref'],'selected_governance_history_fixture_id':docs['governance_history_fixture']['node_id'],'alias_or_global_history_map_accepted':False}
 ck('selected-node-Manifest-exact-ref-gap-observed',mismatches['node_manifest_ref']==fixture['node_id']+'/v1')
 ck('selected-history-fixtures-not-exact-global-history-ref-targets',mismatches['semantic_history_ref']!=mismatches['selected_semantic_history_fixture_id'] and mismatches['governance_history_ref']!=mismatches['selected_governance_history_fixture_id'])
 legacy=docs['versioned_graph_manifest'];legacyerrors=[e.message for e in validator.iter_errors(legacy)];ck('separate-versioned-graph-read-model-manifest',legacy['schema_version']=='cal.system-ontology-graph-version/v1' and legacy['status']=='admitted-versioned-read-model' and legacy['canonical_replay_source'] is False and bool(legacyerrors))
 derr=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not derr,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in derr],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not errors)==accept,(id,errors);probes.append({'case_id':id,'record':x,'schema_accepted':not errors,'expected_schema_acceptance':accept,'errors':errors,'actual_configuration_referent_digest_revision_or_authority_verified':False})
 for n in ['policy_refs','projection_contract_refs']:probe('empty-'+n+'-accepted',lambda x,n=n:x['payload'].update({n:[]}),True)
 scalar=[n for n in payload['required'] if payload['properties'][n].get('minLength')==1]
 for n in scalar:probe('unresolved-cross-kind-'+n+'-accepted',lambda x,n=n:x['payload'].update({n:'absent:wrong-kind'}),True)
 probe('wrong-plausible-configuration-digest-accepted',lambda x:x['payload'].update(configuration_digest='0'*64),True)
 probe('same-ID-changed-configuration-accepted',lambda x:x['payload'].update(runtime_binding_ref='other:runtime',ontology_owner_ref='other:owner',ontology_version='other:version'),True)
 probe('different-record-and-ontology-owners-accepted',lambda x:x.update(owner_ref='other:record-owner'),True)
 probe('whitespace-ref-accepted',lambda x:x['payload'].update(ontology_definition_ref=' '),True)
 probe('multiple-Policy-projection-bindings-accepted',lambda x:x['payload'].update(policy_refs=['hyp:p','hyp:q'],projection_contract_refs=['hyp:v','hyp:w']),True)
 probe('same-semantic-governance-history-ref-accepted',lambda x:x['payload'].update(semantic_history_ref='hyp:history',governance_history_ref='hyp:history'),True)
 probe('admitted-state-with-none-effect-accepted',lambda x:x.update(record_state='admitted'),True)
 probe('permission-sounding-claim-accepted',lambda x:x.update(claim_ceiling='This record activates runtime and admits subjects.'),True)
 for n in payload['required']:probe('missing-'+n+'-rejected',lambda x,n=n:x['payload'].pop(n),False)
 for n in scalar:probe('empty-'+n+'-rejected',lambda x,n=n:x['payload'].update({n:''}),False)
 for n in ['policy_refs','projection_contract_refs']:
  probe('duplicate-'+n+'-rejected',lambda x,n=n:x['payload'].update({n:['hyp:x','hyp:x']}),False)
  probe('wrong-type-'+n+'-rejected',lambda x,n=n:x['payload'].update({n:'hyp:x'}),False)
  probe('empty-item-'+n+'-rejected',lambda x,n=n:x['payload'].update({n:['']}),False)
 probe('malformed-digest-rejected',lambda x:x['payload'].update(configuration_digest='G'*64),False)
 probe('subject-replay-source-true-rejected',lambda x:x['payload'].update(subject_replay_source=True),False)
 probe('authority-effect-admitted-rejected',lambda x:x.update(authority_effect='admitted'),False)
 probe('inline-snapshot-rejected',lambda x:x['payload'].update(subject_snapshot={'state':'hyp'}),False)
 probe('canonical-marker-extra-top-field-rejected',lambda x:x.update(canonical=True),False)
 probe('activation-field-rejected',lambda x:x['payload'].update(runtime_activated=True),False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-OntologyManifest-profile/v1-candidate','status':'PASS-for-configuration-hypotheses-and-selected-carrier-static-binding-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'exact_definition_binding':binding[0],'current_registry_selection':row,'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'fixture_status':fixture['record_state'],'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_configuration_frames':frames(),'selected_fixture_reference_gaps':mismatches,'recorded_binding_admission':{'decision_id':adm['decision_id'],'subject':adm['subject'],'authority_effect':adm['authority_effect'],'excluded_effects':adm['excluded_effects']},'recorded_runtime_adoption':{'decision_id':adopt['decision_id'],'subject':adopt['subject'],'authority_effect':adopt['authority_effect'],'excluded_effects':adopt['excluded_effects']},'versioned_graph_manifest_shape':{'schema_version':legacy['schema_version'],'canonical_replay_source':legacy['canonical_replay_source'],'current_Manifest_schema_errors':legacyerrors,'historical_admission_invalidated':False,'common_manifest_map_accepted':False},'historical_source_current_definition_shape':shape,'native_runtime_executed':False,'project_session_executed':False,'binding_materialization_executed':False,'bound_package_validator_executed':False,'generator_module_or_materialization_writer_executed':False,'existing_pure_projection_function_executed':True,'generic_native_project_common_manifest_map_accepted':False,'actual_configuration_authority_or_runtime_activation_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Actual schema/catalog/projection and exact recorded C47/C48 subject-byte observations plus selected static native/binding/Project code. Hypothetical configuration qualification and frames do not prove actual referent closure,identity/cardinality,digest/revision authorization,runtime activation,owner fidelity or joint closure.'}
 b.unchanged(list(refs.values())+context['sources']+report['checker_bindings']+report['input_refs']);assert runtime==v.f.current_bindings()
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Manifest observations differ')
 return report

def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'frames':len(x['finite_configuration_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_configuration_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(z['schema_accepted'] for z in x['schema_probes']),'catalog_checks':x['actual_check_count']},indent=2))
if __name__=='__main__':main()
