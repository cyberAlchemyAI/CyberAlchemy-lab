"""Qualified cut hypotheses,finite immutable/rebuild frames and actual selected carrier/code observations."""
import ast,copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['cut','ontology','semantic_cursor','governance_cursor','event_set_digest','state_digest','join_policy','source_epoch','registry_epoch']
SUPPORT=['one_ontology','exact_dual_cursors','compatible_event_positions','endpoint_integrity','state_completeness','digest_authentication','immutable_storage','deterministic_rebuild','noncanonical_source','scope_use','authority_separation']
def profiles():
 context={n:'hyp:'+n for n in AXES};base={'context':context,'query':dict(context),'supports':{n:True for n in SUPPORT},'canonical_replay_source':False,'infers_authority':False,'infers_admission':False,'infers_state_truth':False,'infers_external_effect':False,'actual_claim':False,'cut_current':True,'bindings_current':True};rows=[]
 def add(id,change,reject=False,use=True):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['context']!=x['query']:errors.append('exact-cut-context-mismatch')
  if not all(x['supports'].values()):errors.append('missing-qualified-support')
  if any(x[n] for n in ['canonical_replay_source','infers_authority','infers_admission','infers_state_truth','infers_external_effect','actual_claim']):errors.append('unverified-role-or-outcome')
  allowed=not errors and x['cut_current'] and x['bindings_current'];assert bool(errors)==reject and allowed==use,(id,errors)
  rows.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'actual_runtime_execution':False,'actual_cut_or_dual_cursor_hash_rebuild_verified':False,'source_fidelity_accepted':False,'use_allowed_under_hypotheses':allowed})
 add('qualified-immutable-dual-position-cut-under-separate-authority',lambda x:None)
 for n in AXES:add('mismatched-'+n,lambda x,n=n:x['query'].update({n:'hyp:other'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in ['canonical_replay_source','infers_authority','infers_admission','infers_state_truth','infers_external_effect','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-cut-no-reuse',lambda x:x.update(cut_current=False),False,False);add('changed-bindings-no-reuse',lambda x:x.update(bindings_current=False),False,False)
 return rows
def frames():
 state={'ontology':'hyp:o','semantic_cursor':1,'governance_cursor':2,'event_set_digest':'hyp:events','state_digest':'hyp:state','node_refs':['hyp:n'],'edge_refs':['hyp:e'],'node_states':{'hyp:n':'meaning'},'edge_states':{'hyp:e':{'source':'hyp:n','target':'hyp:n'}}};base={'before':state,'after':copy.deepcopy(state),'rebuilt':copy.deepcopy(state),'canonical_replay_source':False,'mix_incompatible_positions':False,'actual_claim':False};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['before']!=x['after']:errors.append('immutable-state-changed')
  if x['before']!=x['rebuilt']:errors.append('rebuilt-cut-not-equivalent')
  if x['canonical_replay_source'] or x['mix_incompatible_positions']:errors.append('forbidden-replay-role-or-position-mixing')
  if x['actual_claim']:errors.append('actual-temporal-proof-unverified')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'universal_immutability_or_rebuild_proof':False,'actual_runtime_execution':False})
 add('immutable-state-and-equivalent-rebuild',lambda x:None)
 for n in ['ontology','semantic_cursor','governance_cursor','event_set_digest','state_digest']:add('same-cut-changes-'+n,lambda x,n=n:x['after'].update({n:'hyp:other'}),True)
 for n in ['node_refs','edge_refs']:add('same-cut-membership-changes-'+n,lambda x,n=n:x['after'].update({n:[]}),True)
 add('same-cut-node-content-changes',lambda x:x['after']['node_states'].update({'hyp:n':'changed'}),True)
 add('same-cut-edge-endpoints-change',lambda x:x['after']['edge_states']['hyp:e'].update(target='absent:n'),True)
 for n in ['semantic_cursor','governance_cursor','event_set_digest','state_digest']:add('rebuilt-mismatch-'+n,lambda x,n=n:x['rebuilt'].update({n:'hyp:other'}),True)
 for n in ['canonical_replay_source','mix_incompatible_positions','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 return rows
def extracted(raw,path,names,namespace):
 tree=ast.parse(raw,filename=str(path));selected=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names]
 if {x.name for x in selected}!=set(names):raise ValueError('Missing selected pure functions')
 exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace);return namespace

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert [x['artifact_type_ref'] for x in direct]==['cal.artifact-type.ontology-cut/v1'];row=direct[0];pkg=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((pkg/'artifact.json').read_bytes());paths={'registry':rp,'descriptor':pkg/'artifact.json','schema':b.ROOT/row['schema_path'],'fixture':pkg/'fixtures/valid/record.json','artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/'fixtures/valid/RECORD.md','generator':b.ROOT/artifact['source_direction']['generator_path'],'wrapper':pkg/'validate.py','validator':b.ROOT/'authority/ontology-integration/candidates/0002-carrier-materialization/validate.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json','native_runtime':b.ROOT/'ontology-lifecycle/runtime/src/lib.rs','domainspec_cut':b.ROOT/'ontology-lifecycle/domainspec/specs/ontology-lifecycle/nodes/consistent-ontology-cut.json','project_session':b.ROOT/'implementation/lab-runtime/v1/lab_runtime/session.py'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-cut-binding',len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]) and binding[0]['admission_decision_ref']=='CAL-DECISION-0065-INTEGRATED-LAB-DEFINITION-MODEL-ADMISSION')
 ck('current-registry-records-C70-type-admission',row['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION' and row['lifecycle_state']=='admitted-current')
 ck('retained-descriptor-and-fixture-candidate-posture',artifact['status']=='candidate-unadmitted' and fixture['record_state']=='candidate' and artifact['authority_effect']==fixture['authority_effect']=='none')
 ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('root-descriptor-binding',artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 renderer=extracted(raw['generator'],paths['generator'],['render_record'],{'json':json})['render_record'];before=copy.deepcopy(fixture);ck('two-pure-fixture-renders-exact',renderer(fixture).encode()==renderer(fixture).encode()==raw['fixture_projection']);ck('render-input-preserved',fixture==before)
 expected='\n'.join(['<!-- GENERATED FILE: canonical data is artifact.json. -->','',f"# {artifact['name']}/v1",'',artifact['distinct_validation_purpose'],'','## Claim ceiling','',artifact['claim_ceiling'],'']).encode();ck('generator-artifact-template-projection-exact',expected==raw['artifact_projection'] and 'item["distinct_validation_purpose"]' in raw['generator'].decode())
 payload=schema['properties']['payload'];ck('closed-top-and-payload',schema['additionalProperties'] is payload['additionalProperties'] is False)
 ck('semantic-cursor-and-join-policy-without-governance-cursor','semantic_cursor' in payload['required'] and 'governance_join_policy_ref' in payload['required'] and 'governance_cursor' not in payload['properties'])
 ck('asserted-integrity-and-digest-shape-not-computation',payload['properties']['integrity_result']['const']=='pass' and payload['properties']['source_event_set_digest']['pattern']=='^[0-9a-f]{64}$' and payload['properties']['calculated_digest']['pattern']=='^[0-9a-f]{64}$')
 ck('noncanonical-replay-flag-closed',payload['properties']['replay_source']['const'] is False)
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('four-hostiles-rejected',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles))
 tree=ast.parse(raw['validator']);fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');code=ast.get_source_segment(raw['validator'].decode(),fn)
 ck('selected-package-validator-generic-and-receipt-writing',all(n not in code for n in ['semantic_cursor','governance_cursor','source_event_set_digest','calculated_digest','node_refs','edge_refs']) and 'dump(package/' in code)
 native=raw['native_runtime'].decode();cutstruct=native.split('pub struct ConsistentOntologyCut {',1)[1].split('\n}',1)[0];cutfn=native.split('    pub fn ontology_at(&self, cursor: u64)',1)[1].split('    pub fn checkpoint_at',1)[0]
 ck('native-cut-semantic-only-fields-inspected','pub semantic_cursor: u64' in cutstruct and 'pub subjects: Vec<ProjectedSubject>' in cutstruct and 'governance_cursor' not in cutstruct)
 ck('native-cut-active-subjects-projection-reference-digest-inspected','Lifecycle::Active' in cutfn and 'map(projection_reference)' in cutfn and 'source_event_set_digest: digest_value(&refs)?' in cutfn and 'source_event_count:' in cutfn)
 ck('native-endpoint-validated-latest-state-inspected','validate_relation_endpoints(&latest)?;' in native.split('    fn latest_by_subject(',1)[1].split('    fn reduced_latest_by_subject(',1)[0])
 ck('native-cursor-range-and-noncanonical-rejection-inspected','CURSOR_OUT_OF_RANGE' in native and 'NONCANONICAL_REPLAY_SOURCE' in native and 'Some("canonical_event")' in native)
 ck('DomainSpec-cursor-and-map-extensional-equality-inspected',[x['name'] for x in docs['domainspec_cut']['body']['fields']]==['cursor','subjects'] and docs['domainspec_cut']['body']['equality']=='Two ontology cuts are equal exactly when their cursor and sorted complete subject-state maps are equal.')
 sessiontree=ast.parse(raw['project_session']);cls=next(x for x in sessiontree.body if isinstance(x,ast.ClassDef) and x.name=='Session');method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_build');session=ast.get_source_segment(raw['project_session'].decode(),method)
 ck('Project-cut-histories-and-selected-state-digests-inspected','event_set_digest = digest(p["histories"])' in session and 'cut_digest = digest({"nodes": node_records, "edges": edge_records})' in session and 'semantic_cursor=event["cursor"]' in session and 'governance_cursor=' not in session)
 ck('Project-templates-and-session-query-boundaries-inspected','copy.deepcopy(p["documents"][TEMPLATES + name + ".json"])' in session and 'depth=2, max_nodes=60, max_edges=100' in session)
 derr=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not derr,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in derr],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not errors)==accept,(id,errors);probes.append({'case_id':id,'record':x,'schema_accepted':not errors,'expected_schema_acceptance':accept,'errors':errors,'actual_dual_cursor_hash_endpoint_immutability_or_rebuild_verified':False})
 probe('unresolved-ontology-node-edge-join-refs-accepted',lambda x:x['payload'].update(ontology_ref='absent:o',node_refs=['absent:n'],edge_refs=['absent:e'],governance_join_policy_ref='absent:join'),True)
 probe('no-explicit-governance-cursor-required',lambda x:None,True)
 probe('wrong-plausible-digests-accepted',lambda x:x['payload'].update(source_event_set_digest='0'*64,calculated_digest='0'*64),True)
 probe('empty-node-and-edge-sets-accepted',lambda x:x['payload'].update(node_refs=[],edge_refs=[]),True)
 probe('edge-without-node-endpoints-accepted',lambda x:x['payload'].update(node_refs=[]),True)
 probe('one-ref-as-node-and-edge-accepted',lambda x:x['payload'].update(node_refs=['same:ref'],edge_refs=['same:ref']),True)
 probe('same-cut-id-changed-digest-accepted',lambda x:x['payload'].update(calculated_digest='f'*64),True)
 probe('same-cut-id-changed-semantic-position-accepted',lambda x:x['payload'].update(semantic_cursor=1),True)
 probe('same-cut-id-changed-join-policy-accepted',lambda x:x['payload'].update(governance_join_policy_ref='other:join'),True)
 probe('record-state-admitted-with-no-authority-effect-accepted',lambda x:x.update(record_state='admitted'),True)
 probe('permission-sounding-claim-accepted',lambda x:x.update(claim_ceiling='This cut proves true states and authorizes all effects.'),True)
 probe('empty-evidence-and-successor-sets-accepted',lambda x:x.update(evidence_refs=[],successor_refs=[]),True)
 probe('whitespace-nonempty-references-accepted',lambda x:(x.update(owner_ref=' ',scope_ref=' '),x['payload'].update(ontology_ref=' ',governance_join_policy_ref=' ',node_refs=[' '],edge_refs=[' '])),True)
 probe('unbounded-positive-cursor-accepted',lambda x:x['payload'].update(semantic_cursor=10**100),True)
 probe('integral-floating-point-JSON-number-accepted',lambda x:x['payload'].update(semantic_cursor=1.0),True)
 for n in ['ontology_ref','semantic_cursor','governance_join_policy_ref','source_event_set_digest','calculated_digest','node_refs','edge_refs','integrity_result','replay_source']:probe('missing-'+n+'-rejected',lambda x,n=n:x['payload'].pop(n),False)
 for id,val in [('zero',0),('negative',-1),('fraction',1.5),('boolean',True)]:probe('invalid-cursor-'+id+'-rejected',lambda x,val=val:x['payload'].update(semantic_cursor=val),False)
 for n in ['node_refs','edge_refs']:probe('duplicate-'+n+'-rejected',lambda x,n=n:x['payload'][n].append(x['payload'][n][0]),False)
 for n in ['source_event_set_digest','calculated_digest']:
  for id,val in [('short','a'),('uppercase','A'*64),('nonhex','z'*64)]:probe('invalid-'+n+'-'+id+'-rejected',lambda x,n=n,val=val:x['payload'].update({n:val}),False)
 probe('replay-source-true-rejected',lambda x:x['payload'].update(replay_source=True),False)
 probe('integrity-result-fail-rejected',lambda x:x['payload'].update(integrity_result='fail'),False)
 probe('explicit-governance-cursor-extra-field-rejected',lambda x:x['payload'].update(governance_cursor=1),False)
 probe('inline-state-extra-field-rejected',lambda x:x['payload'].update(complete_state={'meaning':'claim'}),False)
 for n in ['implicit_admission','derived_authority','runtime_activation']:probe('extra-'+n+'-rejected',lambda x,n=n:x.update({n:True}),False)
 probe('authority-effect-admitted-rejected',lambda x:x.update(authority_effect='admitted'),False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-OntologyCut-profile/v1-candidate','status':'PASS-for-qualified-cut-hypotheses-and-selected-carrier-native-project-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'exact_definition_binding':binding[0],'current_registry_selection':row,'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'descriptor_version':artifact['version'],'carrier_schema_ref':artifact['schema_ref'],'fixture_status':fixture['record_state'],'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_cut_frames':frames(),'native_cut_struct_source':cutstruct,'native_runtime_source_inspected':True,'native_runtime_executed':False,'project_session_source_inspected':True,'project_session_executed':False,'domainspec_cut_source_inspected':True,'bound_package_validator_executed':False,'bound_package_validator_static_source_inspected':True,'generator_module_or_materialization_writer_executed':False,'historical_source_current_definition_shape':shape,'generic_native_project_common_cut_map_accepted':False,'actual_dual_cursor_hash_endpoint_immutability_rebuild_or_authority_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Actual closed carrier schema and pure generated projection checks;native/DomainSpec/Project cut source statically inspected. Explicit governance cursor absent from generic/native cut;actual dual-cursor semantics,hash provenance,immutable storage,rebuild,currentness,source-owner fidelity and common carrier maps unresolved.'}
 b.unchanged(list(refs.values())+context['sources']+report['checker_bindings']+report['input_refs']);assert runtime==v.f.current_bindings()
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh cut carrier/profile observations differ')
 return report

def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'frames':len(x['finite_cut_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_cut_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(z['schema_accepted'] for z in x['schema_probes']),'catalog_checks':x['actual_check_count']},indent=2))
if __name__=='__main__':main()
