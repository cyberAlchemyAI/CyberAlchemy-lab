"""Qualified frozen projection hypotheses,retention frames and current View carrier observations."""
import ast,copy,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['view','request','context','context_version','source_epoch','projection_digest','included_material','excluded_material','lineage','limitations','expiry_or_refresh','owner','registry_epoch']
SUPPORT=['exact_request_resolution','request_Context_binding','Context_version_resolution','source_epoch_resolution','projection_digest_verification','included_material_verification','excluded_material_coverage','lineage_support','limitation_support','expiry_or_refresh_evaluation','immutable_storage','prior_View_retention']
def profiles():
 context={n:'hyp:'+n for n in AXES};base={'context':context,'query':dict(context),'supports':{n:True for n in SUPPORT},'is_Context':False,'is_Request':False,'infers_Context_current':False,'infers_source_truth':False,'infers_source_authority':False,'infers_external_effect':False,'actual_claim':False,'view_current':True,'bindings_current':True};rows=[]
 def add(id,change,reject=False,use=True):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['context']!=x['query']:errors.append('exact-projection-mismatch')
  if not all(x['supports'].values()):errors.append('missing-qualified-support')
  if any(x[n] for n in ['is_Context','is_Request','infers_Context_current','infers_source_truth','infers_source_authority','infers_external_effect','actual_claim']):errors.append('unverified-inferred-meaning-or-outcome')
  allowed=not errors and x['view_current'] and x['bindings_current'];assert bool(errors)==reject and allowed==use,(id,errors)
  rows.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'observations':{'actual_View_binding_digest_epoch_lineage_expiry_immutability_verified':False,'source_fidelity_accepted':False,'use_allowed_under_hypotheses':allowed},'actual_runtime_execution':False})
 add('qualified-frozen-View-exact-bindings-without-Context-currentness-inference',lambda x:None)
 for n in AXES:add('mismatched-'+n,lambda x,n=n:x['query'].update({n:'hyp:other'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in ['is_Context','is_Request','infers_Context_current','infers_source_truth','infers_source_authority','infers_external_effect','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-View-not-reused',lambda x:x.update(view_current=False),False,False)
 add('changed-bindings-not-reused',lambda x:x.update(bindings_current=False),False,False)
 return rows
def frames():
 before={n:'hyp:'+n for n in ['request','context','epoch','projection_digest','included_material','excluded_material','lineage','limitations','expiry_or_refresh']};base={'before':before,'after':copy.deepcopy(before),'same_View_identity':True,'prior_View_retained':True,'new_View_required':False,'stale':False,'consumer_use':False,'reresolution_required':False,'silent_stale_reuse':False,'actual_new_View':False,'actual_claim':False};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['before']!=x['after'] and (x['same_View_identity'] or not x['prior_View_retained'] or not x['new_View_required']):errors.append('changed-frozen-View-without-new-identity-and-retention')
  if x['stale'] and x['consumer_use'] and (not x['reresolution_required'] or x['silent_stale_reuse']):errors.append('silent-stale-consumer-reuse')
  if x['actual_claim']:errors.append('actual-transition-unverified')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'universal_temporal_proof':False,'actual_runtime_execution':False})
 add('unchanged-frozen-projection-retained',lambda x:None)
 for n in before:add('same-View-mutated-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 add('new-View-required-with-prior-retention-without-actual-creation',lambda x:(x['after'].update(epoch='hyp:new'),x.update(same_View_identity=False,new_View_required=True)))
 add('changed-bindings-missing-retention',lambda x:(x['after'].update(epoch='hyp:new'),x.update(same_View_identity=False,new_View_required=True,prior_View_retained=False)),True)
 add('changed-bindings-missing-new-View-requirement',lambda x:(x['after'].update(epoch='hyp:new'),x.update(same_View_identity=False)),True)
 add('stale-unused-View-can-be-retained',lambda x:x.update(stale=True))
 add('stale-consumer-use-needs-reresolution',lambda x:x.update(stale=True,consumer_use=True,reresolution_required=True))
 add('stale-use-no-reresolution',lambda x:x.update(stale=True,consumer_use=True),True)
 add('stale-use-silent-reuse',lambda x:x.update(stale=True,consumer_use=True,reresolution_required=True,silent_stale_reuse=True),True)
 add('actual-creation-can-coexist-with-normative-requirement',lambda x:x.update(actual_new_View=True))
 add('actual-temporal-claim',lambda x:x.update(actual_claim=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];row=next(x for x in current if x['semantic_kind']=='context-view');root=b.ROOT/row['artifact_path'];artifact=json.loads(root.read_bytes());pkg=root.parent
 paths={'registry':rp,'descriptor':root,'schema':b.ROOT/row['schema_path'],'fixture':pkg/artifact['validation_contract']['positive_witness'],'artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/artifact['validation_contract']['positive_projection'],'generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'validator':b.ROOT/artifact['validation_contract']['shared_validator_path'],'root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-context-view-v1-binding',[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']]==['cal.artifact-type.context-view/v1'] and len(binding)==1 and all(binding[0][k]==source[z] for k,z in [('definition_ref','version_ref'),('path','path'),('sha256','sha256')]));ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('generator-validator-root-bindings',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['validator']['sha256'] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)));module=types.ModuleType('_pure_View_renderer');exec(compile(raw['generator'],str(paths['generator']),'exec'),module.__dict__);before=copy.deepcopy([artifact,fixture]);ck('two-artifact-renders-exact',module.render_artifact(artifact).encode()==module.render_artifact(artifact).encode()==raw['artifact_projection']);ck('two-fixture-renders-exact',module.render_instance(artifact,fixture).encode()==module.render_instance(artifact,fixture).encode()==raw['fixture_projection']);ck('render-inputs-preserved',before==[artifact,fixture]);ck('closed-actual-instance-schema',schema['type']=='object' and schema['additionalProperties'] is False);ck('timestamp-lexical-shape-only',all(schema['properties'][n]['pattern']==r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$' and 'format' not in schema['properties'][n] for n in ['generated_at','expires_at']))
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not errors)==accept,(id,errors);probes.append({'case_id':id,'record':x,'schema_accepted':not errors,'expected_schema_acceptance':accept,'errors':errors,'actual_View_binding_digest_epoch_lineage_expiry_immutability_verified':False})

 probe('Context-reference-and-version-identity-mismatch-accepted',lambda x:x.update(context_version_ref='context:other@v1'),True)
 probe('unresolved-request-reference-accepted',lambda x:x.update(request_ref='absent:request'),True)
 probe('opaque-source-epoch-accepted',lambda x:x.update(source_epoch='unknown:epoch'),True)
 probe('all-zero-material-digest-accepted-without-byte-verification',lambda x:x['included_material'][0].update(sha256='0'*64),True)
 probe('literal-glob-selector-accepted',lambda x:x['included_material'][0].update(selector='**/*'),True)
 probe('duplicate-included-records-accepted',lambda x:x['included_material'].append(copy.deepcopy(x['included_material'][0])),True)
 probe('duplicate-excluded-records-accepted',lambda x:x['excluded_material'].append(copy.deepcopy(x['excluded_material'][0])),True)
 probe('same-source-included-and-excluded-records-accepted',lambda x:x['excluded_material'][0].update(source_ref=x['included_material'][0]['source_ref']),True)
 probe('empty-exclusions-accepted',lambda x:x.update(excluded_material=[]),True)
 probe('unresolved-lineage-without-request-link-accepted',lambda x:x.update(lineage_refs=['absent:receipt']),True)
 probe('opaque-limitations-accepted',lambda x:x.update(limitations=['All sources always true.']),True)
 probe('expires-before-generated-accepted',lambda x:x.update(expires_at='2020-01-01T00:00:00Z'),True)
 probe('expires-equal-generated-accepted',lambda x:x.update(expires_at=x['generated_at']),True)
 probe('impossible-calendar-and-clock-timestamps-accepted',lambda x:x.update(generated_at='2026-99-99T99:99:99Z',expires_at='0000-99-99T99:99:99Z'),True)
 probe('future-timestamp-without-currentness-check-accepted',lambda x:x.update(generated_at='9999-01-01T00:00:00Z'),True)
 probe('same-View-identity-changed-bindings-and-digest-accepted',lambda x:(x.update(request_ref='request:other',context_ref='context:other',source_epoch='epoch:other'),x['included_material'][0].update(sha256='b'*64)),True)
 probe('permission-sounding-fixture-claim-accepted-with-no-effect',lambda x:x.update(claim_ceiling='This projection proves all source authority and permits deployment.'),True)
 for n in ['included_material','lineage_refs','limitations']:probe('empty-'+n+'-rejected',lambda x,n=n:x.update({n:[]}),False)
 for n in ['request_ref','context_ref','context_version_ref','source_epoch','selection_basis','owner_ref','scope_ref','owner_route','challenge_route','claim_ceiling']:probe('whitespace-'+n+'-rejected',lambda x,n=n:x.update({n:' '}),False)
 for n in ['lineage_refs','limitations']:probe('duplicate-'+n+'-rejected',lambda x,n=n:x[n].append(x[n][0]),False)
 for n in ['source_ref','selector']:probe('whitespace-included-'+n+'-rejected',lambda x,n=n:x['included_material'][0].update({n:' '}),False)
 for id,val in [('short','a'),('uppercase','A'*64),('nonhex','z'*64)]:probe('invalid-material-digest-'+id+'-rejected',lambda x,val=val:x['included_material'][0].update(sha256=val),False)
 probe('missing-included-digest-rejected',lambda x:x['included_material'][0].pop('sha256'),False)
 probe('whitespace-excluded-reason-rejected',lambda x:x['excluded_material'][0].update(reason=' '),False)
 probe('missing-excluded-reason-rejected',lambda x:x['excluded_material'][0].pop('reason'),False)
 probe('more-than100-included-records-rejected',lambda x:x.update(included_material=[copy.deepcopy(x['included_material'][0]) for i in range(101)]),False)
 probe('more-than100-excluded-records-rejected',lambda x:x.update(excluded_material=[copy.deepcopy(x['excluded_material'][0]) for i in range(101)]),False)
 probe('refresh-only-without-expiry-rejected',lambda x:(x.pop('expires_at'),x.update(refresh_conditions='On epoch change.')),False)
 for n in ['refresh_conditions','projection_digest','immutable','current','context_profile','grants_source_authority','derived_authority']:probe('extra-'+n+'-field-rejected',lambda x,n=n:x.update({n:'fixture:value'}),False)
 for n in ['generated_at','expires_at']:
  for id,val in [('offset','2026-10-05T15:00:00-03:00'),('fraction','2026-10-05T15:00:00.5Z'),('lowercase-z','2026-10-05T15:00:00z')]:probe(n+'-'+id+'-rejected',lambda x,n=n,val=val:x.update({n:val}),False)
 probe('Context-kind-rejected',lambda x:x.update(kind='context'),False)
 probe('authority-effect-admitted-rejected',lambda x:x.update(authority_effect='admitted'),False)
 probe('status-admitted-rejected',lambda x:x.update(status='admitted'),False)

 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('four-hostile-fixtures-rejected',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles));vt=ast.parse(raw['validator']);vf=next(x for x in vt.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');code=ast.get_source_segment(raw['validator'].decode(),vf);ck('bound-package-validator-generic-without-Request-resolution-checks',all(n not in code for n in ['context_version_ref','request_ref','source_epoch','included_material','expires_at','projection_digest','context-view']))
 derr=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not derr,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in derr],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-ContextView-profile/v1-candidate','status':'PASS-for-hypothetical-View-qualification-and-selected-current-carrier-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'dedicated_current_carrier_selection':{'direct_definition_binding_types':['cal.artifact-type.context-view/v1'],'dedicated_current_carrier_established':True,'exact_definition_binding':binding[0]},'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'descriptor_version':artifact['version'],'carrier_schema_ref':artifact['schema_ref'],'fixture_kind':fixture['kind'],'fixture_status':fixture['status'],'source_tuple_fields':b.FIELDS,'possible_locators_not_accepted_maps':{n:n for n in b.FIELDS},'carrier_additional_constraints_not_adopted_into_T':['context_version_ref','generated_at','mandatory_expires_at','nonempty_included_material','owner_route','challenge_route','claim_ceiling'],'whole_View_record_binding_digest_epoch_lineage_expiry_and_immutability_map_accepted':False,'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_history_frames':frames(),'bound_package_validator_executed':False,'bound_package_validator_static_source_inspected':True,'historical_source_current_definition_shape':shape,'retained_fixture_projection_claim':fixture['claim_ceiling'],'fixture_claim_authentication_or_authority_verified':False,'actual_View_projection_refresh_immutable_storage_or_external_effect_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Exact current carrier/source/schema and pure projections. Package validator generic and inspected not executed. Identity/version/epoch mismatches,unverified material hashes,duplicate records,missing whole projection digest,mandatory expiry versus refresh and impossible or reversed timestamps retained. No actual frozen storage,resolution,refresh,currentness,owner fidelity,universal temporal proof or shared closure.'}
 b.unchanged(list(refs.values())+context['sources']+report['checker_bindings']+report['input_refs']);b.external_current(context);assert runtime==v.f.current_bindings()
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh View carrier/profiles differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'frames':len(x['finite_history_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_history_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(z['schema_accepted'] for z in x['schema_probes']),'catalog_checks':x['actual_check_count']},indent=2))
if __name__=='__main__':main()
