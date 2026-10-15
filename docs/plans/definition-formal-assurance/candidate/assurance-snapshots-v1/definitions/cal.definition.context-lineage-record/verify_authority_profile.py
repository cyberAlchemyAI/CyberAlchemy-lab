"""Hypothetical qualified immutable-history frames and exact current/historical carrier probes."""
import ast,copy,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['record','predecessor','successors','source_version','destination_versions','preserved_scope','changed_scope','decision','effective_boundary']
SUPPORT=['identity','owner','exact_versions','scope_mapping','decision_evidence','challenge','history_retention','immutability']
def profile_errors(x):
 errors=[]
 if x['context']!=x['query']:errors.append('exact-context-mismatch')
 if not all(x['supports'].values()):errors.append('missing-qualified-support')
 if x['lineage_kind'] not in [n.lower() for n in b.KINDS]:errors.append('unknown-kind')
 if x['actual_claim']:errors.append('actual-claim-unverified')
 return errors
def profiles():
 base={'context':{n:'hyp:'+n for n in AXES},'query':{n:'hyp:'+n for n in AXES},'supports':{n:True for n in SUPPORT},'lineage_kind':'successor','current':True,'actual_claim':False};rows=[]
 def add(id,change,reject=False,allowed=True):
  x=copy.deepcopy(base);change(x);errors=profile_errors(x);assert bool(errors)==reject;use=not errors and x['current'];assert use==allowed;rows.append({'case_id':id,'profile':x,'errors':errors,'expected_rejection':reject,'expected_use':allowed,'observations':{'use_allowed_under_hypotheses':use,'actual_lineage_owner_reference_or_history_verified':False,'source_fidelity_accepted':False},'actual_runtime_execution':False})
 add('qualified-current-history',lambda x:None)
 for n in AXES:add('mismatched-'+n,lambda x,n=n:x['query'].update({n:'hyp:other'}),True,False)
 for n in SUPPORT:add('missing-'+n,lambda x,n=n:x['supports'].update({n:False}),True,False)
 for n in b.KINDS:add('qualified-'+n.lower(),lambda x,n=n:x.update(lineage_kind=n.lower()))
 add('stale-record',lambda x:x.update(current=False),False,False);add('unknown-kind',lambda x:x.update(lineage_kind='redirect'),True,False);add('unverified-actual-lineage',lambda x:x.update(actual_claim=True),True,False)
 return rows
def frames():
 before={n:'hyp:'+n for n in b.FIELDS};rows=[]
 def add(id,after_id,after,retained=True,owner=True,reject=False):
  x={'record_before':'hyp:r1','record_after':after_id,'before':before,'after':after,'old_record_retained':retained,'owner_qualified':owner,'actual_transition_verified':False};errors=[]
  if not owner:errors.append('owner-unqualified')
  if not retained:errors.append('old-history-erased')
  if after_id=='hyp:r1' and before!=after:errors.append('same-immutable-record-changed')
  assert bool(errors)==reject;rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'universal_temporal_proof':False,'actual_runtime_execution':False})
 add('same-record-exact-bytes-preserved','hyp:r1',copy.deepcopy(before))
 for n in b.FIELDS:
  after=copy.deepcopy(before);after[n]='hyp:changed';add('same-record-changed-'+n,'hyp:r1',after,reject=True)
 after=copy.deepcopy(before);after['lineage_kind']='hyp:withdrawn';add('new-history-record-old-retained','hyp:r2',after)
 add('withdrawal-erases-old-record','hyp:r2',after,retained=False,reject=True);add('successor-owner-unqualified','hyp:r2',after,owner=False,reject=True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(rp.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];row=next(x for x in current if x['semantic_kind']=='context-lineage-record');root=b.ROOT/row['artifact_path'];artifact=json.loads(root.read_bytes());pkg=root.parent
 paths={'registry':rp,'descriptor':root,'schema':b.ROOT/row['schema_path'],'fixture':pkg/artifact['validation_contract']['positive_witness'],'artifact_projection':pkg/'ARTIFACT.md','fixture_projection':pkg/artifact['validation_contract']['positive_projection'],'generator':b.ROOT/artifact['source_direction']['shared_generator_path'],'validator':b.ROOT/artifact['validation_contract']['shared_validator_path'],'old_semantic_validator':b.ROOT/'tooling/validators/ctx01_artifact_type.py','root_descriptor':b.ROOT/artifact['artifact_type_root_binding']['path'],'predecessor_descriptor':b.ROOT/artifact['predecessor_contract']['path'],'predecessor_schema':b.ROOT/artifact['predecessor_contract']['schema_path'],'definition_schema':b.ROOT/'authority/artifact-types/definition/v2/schema.json'}
 for i,n in enumerate(artifact['validation_contract']['negative_witnesses']):paths['negative_'+str(i)]=pkg/n
 refs={n:b.ref(p) for n,p in paths.items()};raw={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(x) for n,x in raw.items() if paths[n].suffix=='.json'};schema=docs['schema'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema);fixture=docs['fixture'];binding=artifact['semantic_definition_bindings'];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('one-current-exact-lineage-v2-binding',[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']]==['cal.artifact-type.context-lineage-record/v2'] and len(binding)==1 and binding[0]['definition_ref']==source['version_ref'] and binding[0]['sha256']==source['sha256'] and binding[0]['path']==source['path']);ck('registry-descriptor-schema-digests',row['artifact_sha256']==refs['descriptor']['sha256'] and row['schema_sha256']==artifact['schema_digest']==refs['schema']['sha256']);ck('historical-predecessor-binding',artifact['predecessor_contract']['sha256']==refs['predecessor_descriptor']['sha256'] and artifact['predecessor_contract']['schema_sha256']==refs['predecessor_schema']['sha256']);ck('generator-validator-root-bindings',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['validator']['sha256'] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('fixture-shape-valid',not list(validator.iter_errors(fixture)))
 module=types.ModuleType('_lineage_pure_renderer');exec(compile(raw['generator'],str(paths['generator']),'exec'),module.__dict__);before=copy.deepcopy([artifact,fixture]);ck('two-artifact-renders-exact',module.render_artifact(artifact).encode()==module.render_artifact(artifact).encode()==raw['artifact_projection']);ck('two-fixture-renders-exact',module.render_instance(artifact,fixture).encode()==module.render_instance(artifact,fixture).encode()==raw['fixture_projection']);ck('render-inputs-preserved',before==[artifact,fixture])
 tree=ast.parse(raw['old_semantic_validator']);functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='semantic_invariants'];assert len(functions)==1;namespace={};exec(compile(ast.Module(body=functions,type_ignores=[]),str(paths['old_semantic_validator']),'exec'),namespace);old=namespace['semantic_invariants'];ck('historical-pure-lineage-invariants-on-fixture',all(x[1] for x in old('context-lineage-record',fixture)))
 probes=[]
 def probe(id,change,accept,paired=None):
  x=copy.deepcopy(fixture);change(x);errors=[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in validator.iter_errors(x)];assert (not errors)==accept,(id,errors);invariants=old('context-lineage-record',x);pair=next(z[1] for z in invariants if z[0]=='lineage-version-cardinality');assert paired is None or pair==paired;probes.append({'case_id':id,'record':x,'schema_accepted':not errors,'expected_schema_acceptance':accept,'errors':errors,'historical_pure_version_cardinality_passed':pair,'historical_pure_invariants':[{'check_id':z[0],'result':z[1],'detail':z[2]} for z in invariants],'actual_reference_owner_scope_history_or_equivalence_verified':False})
 for n in b.KINDS:probe('closed-kind-'+n.lower(),lambda x,n=n:x.update(lineage_kind=n.lower()),True)
 probe('unknown-kind',lambda x:x.update(lineage_kind='redirect'),False);probe('null-predecessor-permitted',lambda x:x.update(predecessor_context_ref=None),True);probe('omitted-predecessor-rejected',lambda x:x.pop('predecessor_context_ref'),False);probe('whitespace-predecessor-accepted',lambda x:x.update(predecessor_context_ref=' '),True)
 probe('mismatched-successor-version-count-schema-accepts',lambda x:x.update(successor_context_refs=['absent:c1','absent:c2']),True,False)
 probe('two-successors-same-version-list-rejected',lambda x:x.update(lineage_kind='split',successor_context_refs=['absent:c1','absent:c2'],destination_versions=['v1','v1']),False,True)
 probe('two-successors-two-unresolved-distinct-versions',lambda x:x.update(lineage_kind='split',successor_context_refs=['absent:c1','absent:c2'],destination_versions=['v1','v2']),True,True)
 probe('null-predecessor-with-split',lambda x:x.update(lineage_kind='split',predecessor_context_ref=None),True);probe('withdrawn-still-requires-successor-list',lambda x:x.update(lineage_kind='withdrawn',successor_context_refs=[]),False,False)
 probe('empty-evidence-list-accepted',lambda x:x.update(evidence_refs=[]),True);probe('empty-residue-list-accepted',lambda x:x.update(residue_refs=[]),True);probe('unresolved-owner-decision-context-version',lambda x:x.update(owner_ref='absent:owner',decision_ref='absent:decision',predecessor_context_ref='absent:p',source_version='absent:v'),True)
 probe('whitespace-decision-evidence-challenge-accepted',lambda x:x.update(decision_ref=' ',evidence_refs=[' '],challenge_route=' '),True);probe('preserved-changed-scopes-identical',lambda x:x.update(changed_scope=x['preserved_scope']),True)
 probe('inferred-equivalence-rejected',lambda x:x.update(equivalence_inferred=True),False);probe('inferred-admission-rejected',lambda x:x.update(admission_inferred=True),False);probe('v2-schema-v2-classification-rejected',lambda x:x['classification'].update(artifact_type_ref='cal.artifact-type.context-lineage-record/v2'),False)
 probe('same-id-changed-scope-no-lineage-history-required',lambda x:x.update(changed_scope='changed actual meaning unverified'),True);probe('same-id-changed-successor-accepted',lambda x:x.update(successor_context_refs=['absent:new']),True);probe('actual-authority-field-rejected',lambda x:x.update(authority_effect='admitted'),False)
 for n in ['decision_ref','challenge_route','preserved_scope','source_version']:probe('empty-'+n+'-rejected',lambda x,n=n:x.update({n:''}),False)
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=[e.message for e in validator.iter_errors(docs[n])];hostiles.append({'fixture_ref':refs[n],'schema_rejected':bool(errors),'errors':errors})
 ck('two-hostile-fixtures-rejected',len(hostiles)==2 and all(x['schema_rejected'] for x in hostiles))
 vt=ast.parse(raw['validator']);vf=next(x for x in vt.body if isinstance(x,ast.FunctionDef) and x.name=='validate_package');source_code=ast.get_source_segment(raw['validator'].decode(),vf);ck('current-package-validator-no-specialized-cardinality-call','semantic_invariants' not in source_code and 'successor_context_refs' not in source_code and 'destination_versions' not in source_code)
 derr=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(b.co.source_document(snap,source)));shape={'current_schema_accepted':not derr,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in derr],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-Definition-v1-current-v2-four-errors',{x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 report={'schema_version':'definition-assurance-ContextLineageRecord-profile/v1-candidate','status':'PASS-for-hypothetical-lineage-history-and-selected-carrier-observations','authority_effect':'none','checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.IMPL/'contracts.py'),b.ref(b.IMPL/'ir.py'),b.ref(b.IMPL/'verifier.py')],'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'dedicated_current_carrier_selection':{'direct_definition_binding_types':['cal.artifact-type.context-lineage-record/v2'],'dedicated_current_carrier_established':True,'exact_definition_binding':binding[0]},'registry_carrier_state':row['lifecycle_state'],'retained_descriptor_status':artifact['status'],'retained_fixture_classification':fixture['classification']['artifact_type_ref'],'fixture_schema_version':fixture['schema_version'],'source_tuple_fields':b.FIELDS,'possible_locators_not_accepted_maps':{'id':'lineage_record_id','residue':'residue_refs',**{n:n for n in b.FIELDS if n not in ['id','residue']}},'whole_field_context_owner_version_scope_and_history_map_accepted':False,'actual_check_count':len(checks),'actual_checks':checks,'schema_probes':probes,'negative_fixture_checks':hostiles,'profiles':profiles(),'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'finite_history_frames':frames(),'bound_package_validator_executed':False,'bound_package_validator_static_source_inspected':True,'historical_pure_semantic_invariants_executed':True,'historical_pure_invariants_are_current_package_checks':False,'historical_source_current_definition_shape':shape,'actual_lineage_equivalence_admission_deletion_or_runtime_effect_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Exact selected schemas,bindings,fixtures and pure renders;historical pure cardinality/inference helper evaluated separately,current bound package validator inspected but not executed. Hypothetical owner/history support only. No authenticated references,real lineage,semantic equivalence/admission,deletion,immutable temporal proof or shared meaning closure.'}
 b.unchanged(list(refs.values())+context['sources']+report['checker_bindings']+report['input_refs']);assert runtime==v.f.current_bindings()
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profiles/carrier evidence differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'frames':len(x['finite_history_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_history_frames']),'schema_probes':len(x['schema_probes']),'schema_acceptances':sum(z['schema_accepted'] for z in x['schema_probes']),'catalog_checks':x['actual_check_count']},indent=2))
if __name__=='__main__':main()
