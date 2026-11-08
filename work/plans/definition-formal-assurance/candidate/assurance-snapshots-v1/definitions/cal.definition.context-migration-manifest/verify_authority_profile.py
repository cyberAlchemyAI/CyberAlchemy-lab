"""Qualified exact-plan hypotheses, immutable-epoch frames and selected carrier observations."""
import ast,copy,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['manifest','manifest_version','source_repository','source_selection','source_digest','dispositions','destinations','dependency_order','preimages','expected_postimages','validation_obligations','owner_gate','registry_epoch']
SUPPORT=['source_resolution','digest_authentication','disposition_coverage','destination_identity','dependency_coverage','per_item_validation','preimage_binding','postimage_binding','owner_gate','rollback','exclusions','immutable_epoch']
def profile_errors(x):
 errors=[]
 if x['context']!=x['query']:errors.append('exact-context-mismatch')
 if not all(x['supports'].values()):errors.append('missing-qualified-support')
 if set(x['sources'])!=set(x['disposition_sources']):errors.append('disposition-source-set-not-exact')
 if len(x['sources'])!=len(set(x['sources'])):errors.append('duplicate-source-identity')
 if not set(x['sources']+x['destinations'])<=set(x['ordered_items']):errors.append('selected-item-order-coverage-missing')
 if not set(x['sources']+x['destinations'])<=set(x['validated_items']):errors.append('selected-item-validation-coverage-missing')
 if x['glob_inferred']:errors.append('glob-inferred-selection')
 if x['execution_authority'] or x['source_admission_inferred'] or x['migration_inferred'] or x['deletion_inferred']:errors.append('manifest-inferred-effect')
 if x['actual_claim']:errors.append('actual-claim-unverified')
 return errors
def profiles():
 context={n:'hyp:'+n for n in AXES};base={'context':context,'query':dict(context),'supports':{n:True for n in SUPPORT},'sources':['hyp:s1','hyp:s2'],'destinations':['hyp:d1'],'disposition_sources':['hyp:s1','hyp:s2'],'ordered_items':['hyp:s1','hyp:s2','hyp:d1'],'validated_items':['hyp:s1','hyp:s2','hyp:d1'],'glob_inferred':False,'execution_authority':False,'source_admission_inferred':False,'migration_inferred':False,'deletion_inferred':False,'plan_current':True,'inputs_current':True,'actual_claim':False};rows=[]
 def add(id,change,reject=False,use=True):
  x=copy.deepcopy(base);change(x);errors=profile_errors(x);allowed=not errors and x['plan_current'] and x['inputs_current'];assert bool(errors)==reject and allowed==use,(id,errors);rows.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':use,'observations':{'use_allowed_under_hypotheses':allowed,'actual_source_destination_hash_gate_or_execution_verified':False,'source_fidelity_accepted':False},'actual_runtime_execution':False})
 add('qualified-current-exact-plan-with-covered-source-and-destination-items',lambda x:None)
 for n in AXES:add('mismatched-'+n,lambda x,n=n:x['query'].update({n:'hyp:other'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 add('disposition-for-unselected-source',lambda x:x['disposition_sources'].append('hyp:outside'),True,False);add('selected-source-without-disposition',lambda x:x['disposition_sources'].pop(),True,False);add('duplicate-source-identity',lambda x:x['sources'].append('hyp:s1'),True,False);add('destination-omitted-from-order',lambda x:x['ordered_items'].remove('hyp:d1'),True,False);add('source-omitted-from-validation',lambda x:x['validated_items'].remove('hyp:s1'),True,False)
 for n in ['glob_inferred','execution_authority','source_admission_inferred','migration_inferred','deletion_inferred','actual_claim']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True,False)
 add('stale-plan',lambda x:x.update(plan_current=False),False,False);add('stale-input-digests',lambda x:x.update(inputs_current=False),False,False)
 add('two-dispositions-for-one-source-not-prohibited-by-set-coverage',lambda x:x['disposition_sources'].append('hyp:s1'))
 return rows
def frames():
 immutable_fields=['source_repository','sources','digests','dispositions','destinations','dependency_order','preimages','expected_postimages','validation_obligations','owner_gates','rollback','exclusions','residue','lifecycle']
 before={'manifest_id':'hyp:m','version':'hyp:v1',**{n:'hyp:'+n for n in immutable_fields}}
 base={'before':before,'after':copy.deepcopy(before),'prior_plan_retained':True,'sources_preserved':True,'separate_gate':False,'execution_requested':False,'rollback_declared_before':True,'exclusions_declared_before':True,'manifest_infers_effect':False,'actual_claim':False};rows=[]
 def add(id,change,reject=False):
  x=copy.deepcopy(base);change(x);errors=[]
  if x['before']!=x['after'] and x['before']['version']==x['after']['version']:errors.append('same-version-immutable-plan-changed')
  if not x['prior_plan_retained']:errors.append('prior-plan-erased')
  if not x['sources_preserved']:errors.append('source-preservation-unestablished')
  if x['execution_requested'] and not x['separate_gate']:errors.append('execution-without-separate-qualified-gate')
  if not x['rollback_declared_before'] or not x['exclusions_declared_before']:errors.append('missing-pre-execution-declarations')
  if x['manifest_infers_effect']:errors.append('manifest-inferred-effect')
  if x['actual_claim']:errors.append('actual-transition-unverified')
  assert bool(errors)==reject,(id,errors);rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'universal_temporal_proof':False,'actual_runtime_execution':False})
 add('same-exact-plan-no-execution',lambda x:None)
 for n in ['manifest_id',*immutable_fields]:add('same-version-change-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 add('new-version-retains-old-plan-and-source-bytes',lambda x:x['after'].update(version='hyp:v2',sources='hyp:new-source'))
 add('hypothetical-separate-gate-does-not-make-manifest-the-authorizer',lambda x:x.update(execution_requested=True,separate_gate=True))
 for n in ['prior_plan_retained','sources_preserved','rollback_declared_before','exclusions_declared_before']:add('missing-'+n,lambda x,n=n:x.update({n:False}),True)
 add('execution-without-separate-gate',lambda x:x.update(execution_requested=True),True);add('manifest-existence-infers-effect',lambda x:x.update(manifest_infers_effect=True),True);add('actual-migration-claimed',lambda x:x.update(actual_claim=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];row=next(x for x in current if x['semantic_kind']=='context-migration-manifest');root=b.ROOT/row['artifact_path'];artifact=json.loads(root.read_bytes());pkg=root.parent
 paths={'registry':rp,'descriptor':root,'schema':b.ROOT/row['schema_path'],'fixture':pkg/artifact['validation_contract']['positive_witness'],'artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/artifact['validation_contract']['positive_projection'],'generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'validator':b.ROOT/artifact['validation_contract']['shared_validator_path'],'historical_semantic_validator':b.ROOT/'tooling/validators/ctx01_artifact_type.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'predecessor_descriptor':b.ROOT/artifact['predecessor_contract']['path'],'predecessor_schema':b.ROOT/artifact['predecessor_contract']['schema_path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-migration-v2-binding',[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']]==['cal.artifact-type.context-migration-manifest/v2'] and len(binding)==1 and binding[0]['definition_ref']==source['version_ref'] and binding[0]['sha256']==source['sha256'] and binding[0]['path']==source['path']);ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('historical-predecessor-binding',artifact['predecessor_contract']['sha256']==refs['predecessor_descriptor']['sha256'] and artifact['predecessor_contract']['schema_sha256']==refs['predecessor_schema']['sha256']);ck('generator-validator-root-bindings',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['validator']['sha256'] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 module=types.ModuleType('_migration_pure_renderer');exec(compile(raw['generator'],str(paths['generator']),'exec'),module.__dict__);before=copy.deepcopy([artifact,fixture]);ck('two-artifact-renders-exact',module.render_artifact(artifact).encode()==module.render_artifact(artifact).encode()==raw['artifact_projection']);ck('two-fixture-renders-exact',module.render_instance(artifact,fixture).encode()==module.render_instance(artifact,fixture).encode()==raw['fixture_projection']);ck('render-inputs-preserved',before==[artifact,fixture])
 tree=ast.parse(raw['historical_semantic_validator']);functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='semantic_invariants'];assert len(functions)==1;ns={};exec(compile(ast.Module(body=functions,type_ignores=[]),str(paths['historical_semantic_validator']),'exec'),ns);old=ns['semantic_invariants'];ck('historical-pure-selection-disposition-invariants-on-current-fixture',all(x[1] for x in old('context-migration-manifest',fixture)))
 probes=[]
 def probe(id,change,accept):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not errors)==accept,(id,errors)
  try:invariants=[{'check_id':z[0],'result':z[1],'detail':z[2]} for z in old('context-migration-manifest',x)];fault=None
  except (KeyError,TypeError) as err:invariants=[];fault=type(err).__name__
  probes.append({'case_id':id,'record':x,'schema_accepted':not errors,'expected_schema_acceptance':accept,'errors':errors,'historical_pure_invariants':invariants,'historical_helper_fault':fault,'historical_pure_invariants_passed':bool(invariants) and all(z['result'] for z in invariants),'actual_source_destination_hash_gate_or_execution_verified':False})
 probe('disposition-for-unselected-source-schema-accepts',lambda x:x['dispositions'][0].update(source_ref='absent:source'),True)
 probe('selected-source-without-disposition-schema-accepts',lambda x:x['source_selections'].append({**x['source_selections'][0],'source_ref':'absent:second'}),True)
 probe('duplicate-source-identity-schema-accepts',lambda x:x['source_selections'].append(copy.deepcopy(x['source_selections'][0])),True)
 probe('duplicate-disposition-schema-and-historical-set-coverage-accept',lambda x:x['dispositions'].append(copy.deepcopy(x['dispositions'][0])),True)
 probe('missing-disposition-destination-accepted',lambda x:x['dispositions'][0].pop('destination_ref'),True)
 probe('null-disposition-destination-accepted',lambda x:x['dispositions'][0].update(destination_ref=None),True)
 probe('unresolved-disposition-destination-accepted',lambda x:x['dispositions'][0].update(destination_ref='absent:destination'),True)
 probe('empty-proposed-destinations-accepted',lambda x:x.update(destination_candidates=[]),True)
 probe('unselected-item-dependency-order-accepted',lambda x:x.update(dependency_order=['absent:item']),True)
 probe('destination-omitted-from-dependency-order-accepted',lambda x:None,True)
 probe('unrelated-generic-validation-obligation-accepted',lambda x:x.update(validation_obligations=['Unrelated generic check.']),True)
 probe('unselected-preimage-and-postimage-paths-accepted',lambda x:(x['preimages'][0].update(path='absent:preimage'),x['expected_postimages'][0].update(path='absent:postimage')),True)
 probe('zero-digests-accepted-without-byte-authentication',lambda x:None,True)
 probe('literal-glob-selector-accepted',lambda x:x['source_selections'][0].update(selector='**/*'),True)
 probe('whitespace-selector-gate-and-rollback-accepted',lambda x:(x['source_selections'][0].update(selector=' '),x['owner_gates'][0].update(effect=' ',role_ref=' '),x.update(rollback_boundary=' ')),True)
 probe('unresolved-source-repository-owner-and-destination-type-accepted',lambda x:(x.update(source_repository_ref='absent:repository',owner_ref='absent:owner'),x['destination_candidates'][0].update(artifact_type_ref='absent:type')),True)
 probe('same-identity-version-changed-source-digest-shape-accepts',lambda x:x['source_selections'][0].update(sha256='1'*64),True)
 probe('same-identity-version-changed-plan-fields-shape-accepts',lambda x:x.update(rollback_boundary='Other boundary.',dependency_order=['absent:other']),True)
 probe('empty-evidence-and-residue-accepted',lambda x:x.update(evidence_refs=[],residue_refs=[]),True)
 for n in ['preserve','revise','split','collapse','reclassify','drop','withdraw']:probe('disposition-enum-'+n+'-does-not-authorize-execution',lambda x,n=n:x['dispositions'][0].update(disposition=n),True)
 probe('unknown-disposition-rejected',lambda x:x['dispositions'][0].update(disposition='delete'),False)
 probe('execution-authority-true-rejected',lambda x:x.update(execution_authority=True),False)
 probe('immutable-false-rejected',lambda x:x.update(immutable=False),False)
 probe('empty-rollback-rejected',lambda x:x.update(rollback_boundary=''),False)
 for n in ['source_selections','dispositions','dependency_order','preimages','expected_postimages','validation_obligations','owner_gates','exclusions']:probe('empty-'+n+'-rejected',lambda x,n=n:x.update({n:[]}),False)
 for n in ['lifecycle','residue','actual_source_admission','migration_receipt']:probe('direct-'+n+'-field-not-carried',lambda x,n=n:x.update({n:'fixture:value'}),False)
 probe('v2-classification-rejected',lambda x:x['classification'].update(artifact_type_ref='cal.artifact-type.context-migration-manifest/v2'),False)
 probe('v1-discriminator-rejected',lambda x:x.update(schema_version='cyberalchemy-lab-context-migration-manifest/v1'),False)
 probe('actual-authority-effect-rejected',lambda x:x.update(authority_effect='admitted'),False)
 probe('admitted-status-rejected',lambda x:x.update(status='admitted'),False)
 probe('bad-digest-shape-rejected',lambda x:x['source_selections'][0].update(sha256='other'),False)
 probe('duplicate-dependency-order-item-rejected',lambda x:x['dependency_order'].append(x['dependency_order'][0]),False)
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('two-hostile-fixtures-rejected',len(hostiles)==2 and all(x['schema_rejected'] for x in hostiles))
 vt=ast.parse(raw['validator']);vf=next(x for x in vt.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');code=ast.get_source_segment(raw['validator'].decode(),vf);ck('current-package-validator-no-old-selection-coverage-call','semantic_invariants' not in code and 'source_selections' not in code and 'dispositions' not in code and 'dependency_order' not in code)
 derr=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not derr,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in derr],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-ContextMigrationManifest-profile/v1-candidate','status':'PASS-for-hypothetical-exact-plan-and-selected-carrier-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'dedicated_current_carrier_selection':{'direct_definition_binding_types':['cal.artifact-type.context-migration-manifest/v2'],'dedicated_current_carrier_established':True,'exact_definition_binding':binding[0]},'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'retained_fixture_classification':fixture['classification']['artifact_type_ref'],'fixture_schema_version':fixture['schema_version'],'source_tuple_fields':b.FIELDS,'possible_locators_not_accepted_maps':{'id':'migration_manifest_id','source_repository':'source_repository_ref','residue':'residue_refs','lifecycle':'status',**{n:n for n in b.FIELDS if n not in ['id','source_repository','residue','lifecycle']}},'whole_record_selection_digest_disposition_destination_order_gate_and_epoch_map_accepted':False,'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_history_frames':frames(),'bound_package_validator_executed':False,'bound_package_validator_static_source_inspected':True,'historical_pure_semantic_invariants_executed':True,'historical_pure_helpers_are_current_package_checks':False,'historical_source_current_definition_shape':shape,'actual_source_admission_migration_deletion_publication_or_deployment_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Exact current carrier/source/schema and pure projections;historical source/disposition-set helper evaluated separately,current package validator inspected not executed. Cross-field coverage,destination linkage,opaque selector/byte/gate/immutable-history gaps and retained v1 classification remain. No actual migration,authority,owner fidelity,universal epoch proof or shared closure.'}
 b.unchanged(list(refs.values())+context['sources']+report['checker_bindings']+report['input_refs']);assert runtime==v.f.current_bindings()
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh carrier/profiles differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'frames':len(x['finite_history_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_history_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(z['schema_accepted'] for z in x['schema_probes']),'catalog_checks':x['actual_check_count']},indent=2))
if __name__=='__main__':main()
