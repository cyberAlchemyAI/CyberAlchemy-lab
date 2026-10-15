"""Qualified Surface hypotheses and exact historical/current manifest consumer observations."""
import ast,copy,json
import build_candidate as b
import verifier as v
AXES=['package_ref', 'governed_file_ref', 'selected_role', 'explicit_role_tuple', 'registry_ref', 'resolved_type_ref', 'versioned_type_key', 'canonical_home_ref', 'manifest_file_ref', 'manifest_self_entry', 'canonical_subject_scope', 'canonical_dependency_ref']
FORBIDDEN=['role_from_path', 'classification_proves_actual_resolution', 'declared_admission_proves_actual_admission', 'component_is_independent_instance', 'fixture_is_canonical_subject', 'transient_satisfies_canonical_dependency', 'global_subject_scope_silently_accepted', 'type_key_is_unversioned_identity', 'total_selector_hides_multiple_role_tuples', 'total_selector_hides_multiple_resolution_tuples', 'manifest_omitted_from_surface', 'generic_Definition_profile_proves_Surface_consistency', 'schema_PASS_grants_admission', 'historical_binding_substitutes_current', 'source_admission_is_translation_fidelity', 'current_carrier_overlay_accepts_translation', 'declared_resolution_count_executes_resolver', 'hypothetical_map_is_owner_acceptance']
MAP_FIELDS=['package_ref', 'governed_file_ref', 'selected_role', 'explicit_role_tuple', 'registry_ref', 'resolved_type_ref', 'versioned_type_key', 'canonical_home_ref', 'manifest_file_ref', 'manifest_self_entry', 'canonical_subject_scope', 'canonical_dependency_ref', 'governed_enumeration', 'all_six_roles', 'type_admission', 'resolver_relation_scope', 'reference_key_correspondence', 'canonical_subject_scope_owner_choice', 'manifest_exact_type', 'transient_dependency_exclusion', 'actual_Conformance', 'owner_fidelity', 'historical_vs_current_consumer', 'current_carrier_admission_overlay', 'validator_shared_code', 'consumer_claim_ceiling']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_role_resolution_admission_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-Surface-necessary-guard-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('distinct-current-manifest-carrier-and-C13-Definition-profile-with-unaccepted-map',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'posture_metadata_as_sufficient_authority':False,'unresolved_subject_scope_ignored':False,'sibling_assignment_declared':True,'explicit_sibling_refs':['hyp:historical-manifest-consumer','hyp:current-manifest-consumer']};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   for n in ['source_role_collapsed','posture_metadata_as_sufficient_authority','unresolved_subject_scope_ignored']:
    if x[n]:errors.append('forbidden:'+n)
   if x['sibling_assignment_declared'] and (len(x['explicit_sibling_refs'])!=2 or len(set(x['explicit_sibling_refs']))!=2):errors.append('missing-sibling-ref')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-shape-or-profile-does-not-prove-actual-outcome')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_role_resolution_admission_or_authority_verified':False,'universal_source_to_profile_mapping_proof':False})
 add('complete-proposed-source-map-without-acceptance',lambda x:None,False)
 add('separate-Definition-profile-with-explicit-Surface-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS}),False)
 add('no-sibling-assignment',lambda x:x.update(sibling_assignment_declared=False,explicit_sibling_refs=[]),False)
 add('outside-selected-map-scope',lambda x:x.update(selected=False,map_fields={},source_role_collapsed=True),False)
 add('hypothetical-map-references-not-actual-owner-review',qualified,False)
 for n in AXES:add('changed-binding-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),True)
 for n in MAP_FIELDS:
  add('lost-map-'+n,lambda x,n=n:x['map_fields'].pop(n),True)
  def missing(x,n=n):qualified(x);x['accepted_map_refs'][n]=''
  add('missing-accepted-map-'+n,missing,True)
 add('shape-claimed-full-fidelity',lambda x:x.update(full_alignment_claimed=True),True)
 for n in ['owner_review_ref','claim_scope_ref']:
  def missing(x,n=n):qualified(x);x[n]=''
  add('missing-'+n,missing,True)
 for n in ['source_role_collapsed','posture_metadata_as_sufficient_authority','unresolved_subject_scope_ignored','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_refs=[]),True)
 return rows
def pure_functions(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={'Any':object,'json':json};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
def verify(write=False):
 context=load('context.json');typed_receipt=load('types-logic-receipt.json');b.unchanged(typed_receipt['inputs']+typed_receipt['producer_results']+context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');profile_type=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation-profile/v1');carrier=next(x for x in direct if x['artifact_type_ref']=='cal.artifact-type.canonical-package-manifest/v1')
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/generic['schema_path'],'C13_foundation_schema':b.ROOT/profile_type['schema_path'],'C13_profile':b.ROOT/'authority/profiles/definition/v1/evaluation.json','C13_decision':b.ROOT/'docs/decisions/0013-foundation-01-admission/decision.json','C13_profile_generator':b.ROOT/'authority/foundation/v1/render.py','C13_profile_projection':b.ROOT/'authority/profiles/definition/v1/EVALUATION.md','Surface_generator':b.ROOT/'tooling/generators/artifact_surface.py','declared_validator':b.ROOT/'tooling/validators/artifact_surface.py','current_validator':b.ROOT/'tooling/validators/artifact_surface_candidate_2.py','checker':b.UNIT/'verify_authority_profile.py'}
 roots={'historical':b.ROOT/'authority/artifact-types/canonical-package-manifest/v1','current':(b.ROOT/carrier['artifact_path']).parent}
 for label,path in roots.items():
  artifact=json.loads((path/'artifact.json').read_bytes())
  for k,q in {'artifact':path/'artifact.json','schema':path/'schema.json','artifact_projection':path/'ARTIFACT.md','fixture':path/artifact['validation_contract']['positive_witness'],'fixture_projection':path/artifact['validation_contract']['positive_projection']}.items():paths[label+'_'+k]=q
  for i,rel in enumerate(artifact['validation_contract']['negative_witnesses']):paths[label+'_negative_'+str(i)]=path/rel
  for binding in artifact['semantic_definition_bindings']:paths[label+'_binding_'+binding['definition_ref']]=b.ROOT/binding['path']
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];foundation=docs['C13_foundation_schema'];ps={'$schema':foundation['$schema'],'$defs':foundation['$defs'],'$ref':profile_type['schema_selector']};b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(ps);dv=b.c.Draft202012Validator(ds);pv=b.c.Draft202012Validator(ps);record=docs['C13_profile'];decision=docs['C13_decision'];admitted=[x for x in decision['admitted_records'] if x['record_id']==record['record_id']];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('catalog143rows121current',len(rows)==143 and len(current)==121)
 ck('one-current-direct-Surface-manifest-carrier',len(direct)==1 and direct[0]==carrier and carrier['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('carrier-exact-admitted-current-bytes',carrier['artifact_path']==refs['current_artifact']['path'] and carrier['artifact_sha256']==refs['current_artifact']['sha256'] and carrier['schema_path']==refs['current_schema']['path'] and carrier['schema_sha256']==refs['current_schema']['sha256'])
 ck('generic-current-Definition-separate-meaning',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('generic-C13-EvaluationProfile-selector-exact',profile_type['admission_decision_ref']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and profile_type['schema_selector']=='#/$defs/evaluationProfile' and profile_type['semantic_definition_refs']==[] and refs['C13_foundation_schema']['sha256']==profile_type['schema_sha256'])
 ck('C13-exact-Definition-profile-admission',decision['status']=='owner-admitted' and len(admitted)==1 and admitted[0]['path']==refs['C13_profile']['path'] and admitted[0]['sha256']==refs['C13_profile']['sha256']=='8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9' and admitted[0]['admission_effect']=='definition-evaluation-profile-admitted')
 ck('C13-retained-profile-body-candidate-none',record['status']=='candidate-unadmitted' and record['authority_effect']=='none')
 ck('C13-profile-subject-Definition-not-Surface-consistency',record['record_id']=='CAL-EVALUATION-DEFINITION-V1' and record['subject_artifact_type_ref']=='cal.artifact-type.definition/v1' and record['outcomes']==['PASS','FAIL','NOT_EVALUABLE'] and record['evaluation_mode']=='collect-all')
 ck('C13-profile13required7checks',len(foundation['$defs']['evaluationProfile']['allOf'][1]['required'])==13 and len(record['checks'])==7 and not list(pv.iter_errors(record)))
 ck('C13-generator-bytes-bound',record['source_direction']['generator_sha256']==refs['C13_profile_generator']['sha256'])
 ck('selected-Definition-v1-valid',not list(dv.iter_errors(docs['source'])))
 gen=pure_functions(paths['C13_profile_generator'],['header','evaluation']);before=copy.deepcopy(record);p1=(gen['evaluation'](before).rstrip()+'\n').encode();p2=(gen['evaluation'](before).rstrip()+'\n').encode();ck('two-pure-C13-profile-projections-preserve-input',p1==p2==paths['C13_profile_projection'].read_bytes() and before==record)
 ck('Surface-exact-two-primary-labels',docs['source']['primary_consumer_refs']==['cal.artifact-type.canonical-package-manifest/v1','tooling/validators/artifact_surface.py'])
 gen=pure_functions(paths['Surface_generator'],['render_artifact','render_instance']);semantic=pure_functions(paths['current_validator'],['manifest_semantic_failures'])['manifest_semantic_failures'];consumer_observations=[];manifest_probes=[]
 def manifest_probe(id,doc,validator,schema_expected,semantic_expected):
  before=copy.deepcopy(doc);errors=sorted(e.message for e in validator.iter_errors(doc));failures=semantic(doc);assert (not errors)==schema_expected and (not failures)==semantic_expected and doc==before,(id,errors,failures)
  manifest_probes.append({'case_id':id,'schema_accepted':not errors,'schema_errors':errors,'pure_current_manifest_guard_accepted':not failures,'pure_guard_failures':failures,'native_or_live_consumer_executed':False,'accepted_translation':False})
 for label,path in roots.items():
  artifact=docs[label+'_artifact'];schema=docs[label+'_schema'];fixture=docs[label+'_fixture'];b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema)
  ck(label+'-schema-digest',artifact['schema_digest']==refs[label+'_schema']['sha256'])
  ck(label+'-retained-body-candidate-none',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none')
  ck(label+'-shared-generator-digest',artifact['source_direction']['shared_generator_sha256']==refs['Surface_generator']['sha256'])
  ck(label+'-shared-validator-exact',artifact['validation_contract']['shared_validator_path']==refs['declared_validator' if label=='historical' else 'current_validator']['path'] and artifact['validation_contract']['shared_validator_sha256']==refs['declared_validator' if label=='historical' else 'current_validator']['sha256'])
  ck(label+'-semantic-ref-closure',set(artifact['semantic_definition_refs'])=={x['definition_ref'] for x in artifact['semantic_definition_bindings']})
  selected_binding=next(x for x in artifact['semantic_definition_bindings'] if x['definition_ref'].startswith('cal.definition.artifact-surface-classification@'))
  for binding in artifact['semantic_definition_bindings']:ck(label+'-exact-binding-'+binding['definition_ref'],refs[label+'_binding_'+binding['definition_ref']]=={'path':binding['path'],'sha256':binding['sha256']})
  ck(label+'-exact-Surface-version',selected_binding['definition_ref']=='cal.definition.artifact-surface-classification@1.0.0-candidate.'+('1' if label=='historical' else '2'))
  if label=='current':ck('current-Surface-source-exact',selected_binding['definition_ref']==source['version_ref'] and selected_binding['path']==source['path'] and selected_binding['sha256']==source['sha256'])
  before=copy.deepcopy(artifact);first=gen['render_artifact'](before).encode();second=gen['render_artifact'](before).encode();ck(label+'-two-pure-artifact-projections',first==second==paths[label+'_artifact_projection'].read_bytes() and before==artifact)
  before=copy.deepcopy(fixture);first=gen['render_instance'](artifact,before).encode();second=gen['render_instance'](artifact,before).encode();ck(label+'-two-pure-fixture-projections',first==second==paths[label+'_fixture_projection'].read_bytes() and before==fixture)
  ck(label+'-positive-schema',not list(validator.iter_errors(fixture)))
  for i,rel in enumerate(artifact['validation_contract']['negative_witnesses']):ck(label+'-negative-schema-'+str(i),bool(list(validator.iter_errors(docs[label+'_negative_'+str(i)]))))
  manifest_probe(label+'-supplied-positive',copy.deepcopy(fixture),validator,True,label=='current')
  consumer_observations.append({'variant':label,'artifact_ref':refs[label+'_artifact'],'schema_ref':refs[label+'_schema'],'Surface_binding':selected_binding,'registry_overlay':'admitted-current-C70' if label=='current' else 'not-selected-current-carrier','embedded_status':artifact['status'],'shared_validator_ref':refs['declared_validator' if label=='historical' else 'current_validator'],'pure_projection_and_schema_observations':True,'native_or_live_consumer_executed':False,'accepted_consumer_map_refs':[]})
 current_fixture=docs['current_fixture'];validator=b.c.Draft202012Validator(docs['current_schema'])
 x=copy.deepcopy(current_fixture);x['surface_entries']=[z for z in x['surface_entries'] if z['path']!='package.json'];manifest_probe('missing-self-entry-current-schema-and-guard-rejection',x,validator,False,False)
 x=copy.deepcopy(current_fixture);x['surface_entries'].append(copy.deepcopy(x['surface_entries'][0]));manifest_probe('duplicate-self-entry-current-schema-and-guard-rejection',x,validator,False,False)
 x=copy.deepcopy(current_fixture);x['surface_entries'][0]['artifact_type_ref']='cal.artifact-type.product-identity/v1';manifest_probe('wrong-self-type-current-schema-and-guard-rejection',x,validator,False,False)
 x=copy.deepcopy(current_fixture);x['surface_entries'][0]['role']='fixture';x['surface_entries'][0]['artifact_type_ref']=None;x['surface_entries'][0].pop('resolution_count');manifest_probe('noncanonical-self-current-schema-and-guard-rejection',x,validator,False,False)
 for value in [0,2]:
  x=copy.deepcopy(current_fixture);x['surface_entries'][0]['resolution_count']=value;manifest_probe('canonical-resolution-count-'+str(value),x,validator,False,False)
 x=copy.deepcopy(current_fixture);x['surface_entries'][2]['artifact_type_ref']='cal.artifact-type.product-identity/v1';manifest_probe('generated-claims-type',x,validator,False,False)
 x=copy.deepcopy(current_fixture);x['surface_entries'][2]['role']='invented-role';manifest_probe('seventh-role-rejected-by-schema',x,validator,False,True)
 cross={'finding_id':'SURF-CONSUMER-FINDING-001','status':'unresolved','source_declared_validator_ref':refs['declared_validator'],'current_carrier_validator_ref':refs['current_validator'],'historical_manifest_binds_predecessor':True,'current_C70_carrier_binds_current_Surface':True,'historical_positive_fixture_missing_self_entry':True,'current_positive_fixture_has_exact_self_entry':True,'current_schema_rejects_missing_duplicate_wrong_type_and_wrong_role_self_entry':True,'current_pure_manifest_guard_rejects_these':True,'common_meaning_consistency_verified':False,'accepted_consumer_map_refs':[],'owner_route':'Surface,CanonicalPackageManifest,artifact-mechanics and consumer owners','possible_resolution':'Record the exact historical and current consumer route,then accept package/file/role/reference correspondence and canonical subject scope explicitly. Do not replace the declared historical validator label silently.','claim_ceiling':'Exact consumer bytes,projection,schema and pure function observations only;no live validator writer or accepted translation.'}
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];profile_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_role_resolution_admission_or_authority_verified':False})
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in AXES:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:declared role and type resolution prove actual classification,admission and authority';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 probe(profile_probes,'exact-admitted-C13-Definition-profile-body',copy.deepcopy(record),pv,True)
 for n in foundation['$defs']['evaluationProfile']['allOf'][1]['required']:
  x=copy.deepcopy(record);x.pop(n);probe(profile_probes,'missing-root-'+n,x,pv,False)
 for n in ['check_id','purpose','blocked_by']:
  x=copy.deepcopy(record);x['checks'][0].pop(n);probe(profile_probes,'missing-check-'+n,x,pv,False)
 for n in ['record_id','owner_ref','claim_ceiling','admission_rule']:
  for label,value,expected in [('empty','',False),('whitespace',' ',True),('unresolved','hyp:unresolved',True)]:
   x=copy.deepcopy(record);x[n]=value;probe(profile_probes,n+'-'+label,x,pv,expected)
 x=copy.deepcopy(record);x['claim_ceiling']='hyp:this profile grants Surface classification,admission and authority';probe(profile_probes,'overclaimed-profile-text-shape-valid',x,pv,True)
 reports=profiles();fs=frames();report={'schema_version':'definition-assurance-ArtifactSurface-authority-profile/v1-candidate','status':'PASS-for-qualified-Surface-hypotheses-and-exact-current-historical-consumer-observations','authority_effect':'none','source':source,'profiles':reports,'finite_comparison_frames':fs,'actual_checks':checks,'actual_check_count':len(checks),'selected_inputs':refs,'checker_bindings':[refs['checker'],b.ref(b.IMPL/'contracts.py')],'runtime_bindings':runtime,'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic['artifact_type_ref'],'generic_Definition_semantic_ref':generic['semantic_definition_refs'][0],'C13_profile_record_ref':record['record_id'],'C13_profile_is_Surface_consistency_detector':False,'Definition_schema_probes':definition_probes,'C13_profile_schema_probes':profile_probes,'manifest_schema_and_pure_guard_probes':manifest_probes,'consumer_observations':consumer_observations,'cross_definition_review_findings':[cross],'source_map_obligations':MAP_FIELDS,'accepted_source_to_carrier_or_consumer_map_refs':[],'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'current_manifest_semantic_function_evaluated_on_in_memory_fixtures':True,'actual_role_resolution_admission_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified proposed maps,current catalog,C13 generic Definition profile,exact historical/current manifest bindings,two pure projections and schema/pure manifest-guard probes. No accepted canonical-subject scope,live consumer writer,actual enumeration,resolution,admission,owner fidelity or whole proof.'}
 b.unchanged(list(refs.values())+context['sources']+typed_receipt['inputs']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh qualification/profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'qualification_profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'finite_frames':len(x['finite_comparison_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_comparison_frames']),'actual_checks':x['actual_check_count'],'Definition_schema_probes':len(x['Definition_schema_probes']),'C13_profile_schema_probes':len(x['C13_profile_schema_probes']),'manifest_schema_and_pure_guard_probes':len(x['manifest_schema_and_pure_guard_probes']),'mapping_obligations':len(x['source_map_obligations']),'direct_current_definition_binding_types':x['direct_current_definition_binding_types'],'semantic_ready':False},indent=2))
if __name__=='__main__':main()
