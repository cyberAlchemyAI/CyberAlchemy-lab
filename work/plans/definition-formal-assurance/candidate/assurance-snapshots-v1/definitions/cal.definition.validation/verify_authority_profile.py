"""Qualified Validation hypotheses and current semantic-use/C13 profile observations."""
import ast,copy,json
import build_candidate as b
import verifier as v
AXES=['identity', 'kind', 'source', 'normalized_context', 'evaluation', 'subject', 'criteria_profile', 'input', 'environment', 'validator', 'receipt', 'context', 'profile_digest', 'subject_digest', 'input_digest', 'declared_checks', 'included_outcomes', 'outcome_tags', 'evaluable_checks', 'reported_PASS', 'PASS_coverage', 'conformance_profile', 'evidence_scope', 'applicability', 'sufficiency']
FORBIDDEN=['C13_Definition_profile_is_every_Validation_profile', 'migration_semantic_use_is_Validation_record_alignment', 'generic_type_admission_is_instance_admission', 'source_admission_is_translation_fidelity', 'profile_declaration_proves_check_correctness', 'digest_equality_proves_currentness_or_execution', 'reported_PASS_is_complete_coverage', 'NOT_EVALUABLE_is_PASS_covered', 'omitted_checks_are_PASS_covered', 'receipt_reference_proves_receipt_storage', 'multiple_outcomes_are_forbidden_without_owner_policy', 'empty_profile_policy_is_accepted', 'conformance_scope_covers_whole_profile_implicitly', 'sufficiency_declaration_proves_actual_Conformance', 'Validation_is_Admission', 'schema_PASS_grants_authority', 'nonentailment_denies_supported_outcomes']
MAP_FIELDS=['normalized_classification', 'C29_exact_source', 'specialized_Evaluation_binding', 'exact_subject', 'exact_criteria_profile', 'exact_input', 'exact_environment', 'validator_identity', 'receipt_reference', 'context', 'three_digest_bindings', 'profile_coverage_scope', 'profile_evaluation_mode', 'declared_checks', 'included_outcomes', 'tag_and_evaluability_guard', 'receipt_outcome_membership', 'per_check_record_completeness', 'reported_PASS_rule', 'PASS_covered_subset', 'complete_PASS_coverage', 'Conformance_profile_applicability', 'scoped_sufficiency', 'required_evidence_checks', 'consumer_binding']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_execution_check_correctness_complete_coverage_Conformance_admission_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-Validation-necessary-guard-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('distinct-migration-semantic-use-and-C13-Definition-profile-with-unaccepted-map',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'Evaluation_specialization_collapsed':False,'reported_PASS_as_sufficient_Conformance':False,'NOT_EVALUABLE_counted_as_PASS_coverage':False,'sibling_assignment_declared':True,'explicit_sibling_ref':'hyp:separate-conformance-evidence-use'};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   for n in ['Evaluation_specialization_collapsed','reported_PASS_as_sufficient_Conformance','NOT_EVALUABLE_counted_as_PASS_coverage']:
    if x[n]:errors.append('forbidden:'+n)
   if x['sibling_assignment_declared'] and not x['explicit_sibling_ref']:errors.append('missing-sibling-ref')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-shape-or-profile-does-not-prove-actual-outcome')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_execution_check_correctness_complete_coverage_Conformance_admission_or_authority_verified':False,'universal_source_to_profile_mapping_proof':False})
 add('complete-proposed-source-map-without-acceptance',lambda x:None,False)
 add('separate-carrier-purpose-with-explicit-Validation-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS}),False)
 add('no-sibling-assignment',lambda x:x.update(sibling_assignment_declared=False,explicit_sibling_ref=''),False)
 add('outside-selected-map-scope',lambda x:x.update(selected=False,map_fields={},Evaluation_specialization_collapsed=True),False)
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
 for n in ['Evaluation_specialization_collapsed','reported_PASS_as_sufficient_Conformance','NOT_EVALUABLE_counted_as_PASS_coverage','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_ref=''),True)
 return rows
def pure_functions(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns

def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source']
 rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];assert len(direct)==1;carrier=direct[0];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');profile_type=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation-profile/v1');cp=(b.ROOT/carrier['artifact_path']).parent
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/generic['schema_path'],'C13_foundation_schema':b.ROOT/profile_type['schema_path'],'C13_profile':b.ROOT/'authority/profiles/definition/v1/evaluation.json','C13_decision':b.ROOT/'docs/decisions/0013-foundation-01-admission/decision.json','C13_profile_generator':b.ROOT/'authority/foundation/v1/render.py','C13_profile_projection':b.ROOT/'authority/profiles/definition/v1/EVALUATION.md','migration_artifact':cp/'artifact.json','migration_schema':b.ROOT/carrier['schema_path'],'migration_fixture':cp/'fixtures/valid/migration.json','migration_projection':cp/'fixtures/valid/MIGRATION.md','migration_type_projection':cp/'ARTIFACT.md','migration_generator':b.ROOT/'tooling/generators/artifact_surface.py','migration_validator':b.ROOT/'tooling/validators/artifact_surface_candidate_2.py','migration_package_validator':cp/'validate.py','checker':b.UNIT/'verify_authority_profile.py'}
 for name in ['execution-authority','overwrite','missing-rollback']:paths['negative_'+name]=cp/('fixtures/invalid/'+name+'.json')
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];foundation=docs['C13_foundation_schema'];ps={'$schema':foundation['$schema'],'$defs':foundation['$defs'],'$ref':profile_type['schema_selector']};ms=docs['migration_schema']
 for schema in [ds,ps,ms]:b.c.Draft202012Validator.check_schema(schema)
 dv=b.c.Draft202012Validator(ds);pv=b.c.Draft202012Validator(ps);mv=b.c.Draft202012Validator(ms);record=docs['C13_profile'];artifact=docs['migration_artifact'];fixture=docs['migration_fixture'];decision=docs['C13_decision'];admitted=[x for x in decision['admitted_records'] if x['record_id']==record['record_id']];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('catalog143rows121current',len(rows)==143 and len(current)==121)
 ck('one-current-Validation-semantic-use-type',carrier['artifact_type_ref']=='cal.artifact-type.repository-migration-manifest/v1' and carrier['admission_decision_ref']=='CAL-DECISION-0070-DEFINITION-COMPLETE-LAB-MODEL-ADMISSION')
 ck('current-migration-exact-artifact-schema',refs['migration_artifact']['sha256']==carrier['artifact_sha256']=='7be737ec03d54084cd88bbadaac09fcdc14126c42a63d2bc6c47e866bc067b65' and refs['migration_schema']['sha256']==carrier['schema_sha256']==artifact['schema_digest']=='ccfbeea982c405c09e454eb2bdec5081df6dbdeeeaccf6553148046481b5d084' and carrier['schema_selector'] is None)
 ck('migration-exact-Validation-binding',next(x for x in artifact['semantic_definition_bindings'] if x['definition_ref']==source['version_ref'])=={'admission_posture':'admitted','definition_ref':source['version_ref'],'path':source['path'],'sha256':source['sha256']} and artifact['semantic_definition_refs']==carrier['semantic_definition_refs'])
 ck('retained-type-candidate-posture-separate-current-overlay',artifact['status']=='candidate-unadmitted' and artifact['authority_effect']=='none' and artifact['classification']['authority_kind']=='none' and carrier['lifecycle_state']=='admitted-current')
 ck('migration-closed19root-fields',ms['additionalProperties'] is False and len(ms['required'])==19 and set(ms['required'])==set(ms['properties']))
 ck('migration-fixture-no-effects',fixture['status']=='candidate-unapproved' and fixture['authority_effect']=='none' and fixture['execution_authority'] is False and fixture['copy_semantics']=={'additive_only':True,'overwrite':False,'source_mutation':False,'import_grants_authority':False} and not list(mv.iter_errors(fixture)))
 ck('migration-discriminator-exact',carrier['instance_discriminator']=={'path':'/schema_version','value':fixture['schema_version']})
 ck('migration8required-semantic-fields3forbidden',len(artifact['instance_contract']['required_semantic_fields'])==8 and artifact['instance_contract']['forbidden_canonical_fields']==['approval','admission_effect','execution_token'])
 ck('migration4orthogonality-rules',len(artifact['orthogonality_rules'])==4 and [x['rule_id'] for x in artifact['orthogonality_rules']]==['RMM-01','RMM-02','RMM-03','RMM-04'])
 ck('migration6fixture-obligation-names-not-outcomes',fixture['validation_obligations']==['complete-accounting','hash-currency','collision-free','dry-run','isolated-rehearsal','rollback-closure'])
 ck('fixture-ref-list-does-not-force-Validation-ref',fixture['semantic_definition_refs']==['cal.definition.repository-migration-manifest@1.0.0-candidate.1'] and source['version_ref'] not in fixture['semantic_definition_refs'])
 ck('migration-pure-generator-binding',artifact['source_direction']['shared_generator_sha256']==refs['migration_generator']['sha256'])
 ck('migration-validator-bytes-bound-not-executed',artifact['validation_contract']['shared_validator_sha256']==refs['migration_validator']['sha256'] and artifact['validation_contract']['admission_effect']=='none')
 missing=['evaluation_ref','subject_ref','criteria_profile_ref','input_ref','environment_ref','validator_ref','receipt_ref','outcomes','reported_PASS','PASS_coverage','conformance_profile_ref','applicability','sufficiency']
 ck('no-dedicated-Validation-evaluation-record-fields',all(n not in ms['properties'] for n in missing))
 ck('generic-current-Definition-separate-meaning',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('generic-C13-EvaluationProfile-selector-exact',profile_type['admission_decision_ref']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and profile_type['schema_selector']=='#/$defs/evaluationProfile' and profile_type['semantic_definition_refs']==[] and refs['C13_foundation_schema']['sha256']==profile_type['schema_sha256'])
 ck('C13-exact-Definition-profile-admission',decision['status']=='owner-admitted' and len(admitted)==1 and admitted[0]['path']==refs['C13_profile']['path'] and admitted[0]['sha256']==refs['C13_profile']['sha256']=='8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9' and admitted[0]['admission_effect']=='definition-evaluation-profile-admitted')
 ck('C13-profile-retains-candidate-none',record['status']=='candidate-unadmitted' and record['authority_effect']=='none')
 ck('C13-profile-Definition-subject-7checks',record['subject_artifact_type_ref']=='cal.artifact-type.definition/v1' and record['outcomes']==['PASS','FAIL','NOT_EVALUABLE'] and record['evaluation_mode']=='collect-all' and len(record['checks'])==7 and not list(pv.iter_errors(record)))
 ck('C13-profile-generator-bytes-bound',record['source_direction']['generator_sha256']==refs['C13_profile_generator']['sha256'])
 ck('selected-Validation-Definition-v1-valid',not list(dv.iter_errors(docs['source'])) and load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1')
 gen=pure_functions(paths['C13_profile_generator'],['header','evaluation']);before=copy.deepcopy(record);p1=(gen['evaluation'](before).rstrip()+'\n').encode();p2=(gen['evaluation'](before).rstrip()+'\n').encode();ck('two-pure-C13-projections-input-preserved',p1==p2==paths['C13_profile_projection'].read_bytes() and before==record)
 ns={};exec(compile(ast.parse(paths['migration_generator'].read_bytes()),str(paths['migration_generator']),'exec'),ns)
 for name,func,args,target in [('type','render_artifact',[artifact],paths['migration_type_projection']),('fixture','render_instance',[artifact,fixture],paths['migration_projection'])]:
  before=copy.deepcopy(args);p1=ns[func](*before).encode();p2=ns[func](*before).encode();ck('two-pure-migration-'+name+'-projections-input-preserved',p1==p2==target.read_bytes() and before==args)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];profile_probes=[];carrier_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_execution_check_correctness_complete_coverage_Conformance_admission_or_authority_verified':False})
 original=docs['source'];probe(definition_probes,'exact-selected-Validation-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in missing:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:PASS proves complete coverage,Conformance and admission';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 probe(profile_probes,'exact-admitted-C13-Definition-profile-body',copy.deepcopy(record),pv,True)
 for n in foundation['$defs']['evaluationProfile']['allOf'][1]['required']:
  x=copy.deepcopy(record);x.pop(n);probe(profile_probes,'missing-root-'+n,x,pv,False)
 for n in ['check_id','purpose','blocked_by']:
  x=copy.deepcopy(record);x['checks'][0].pop(n);probe(profile_probes,'missing-check-'+n,x,pv,False)
 for n in ['record_id','owner_ref','claim_ceiling','admission_rule']:
  for label,value,expected in [('empty','',False),('whitespace',' ',True),('unresolved','hyp:unresolved',True)]:
   x=copy.deepcopy(record);x[n]=value;probe(profile_probes,n+'-'+label,x,pv,expected)
 x=copy.deepcopy(record);x['claim_ceiling']='hyp:this profile grants all Validation coverage,Conformance and authority';probe(profile_probes,'overclaimed-profile-text-shape-valid',x,pv,True)
 probe(carrier_probes,'exact-migration-fixture',copy.deepcopy(fixture),mv,True)
 for n in ms['required']:
  x=copy.deepcopy(fixture);x.pop(n);probe(carrier_probes,'missing-root-'+n,x,mv,False)
 for n in ['approval','admission_effect','execution_token',*missing]:
  x=copy.deepcopy(fixture);x[n]='hyp:claimed';probe(carrier_probes,'forbidden-extra-root-'+n,x,mv,False)
 for n in ['migration_manifest_id','version','claim_ceiling']:
  for label,value,expected in [('empty','',False),('whitespace',' ',True),('unresolved','hyp:unresolved',True)]:
   x=copy.deepcopy(fixture);x[n]=value;probe(carrier_probes,n+'-'+label,x,mv,expected)
 for n in ['validation_obligations','semantic_definition_refs']:
  for label,value,expected in [('empty',[],False),('duplicate',[fixture[n][0],fixture[n][0]],True),('unresolved',['hyp:unresolved'],True)]:
   x=copy.deepcopy(fixture);x[n]=value;probe(carrier_probes,n+'-'+label,x,mv,expected)
 for n in ['architecture','copy_allowlist','exclusion_inventory','expected_postimage','mapping_rules','rollback_ref']:
  for label,digest,expected in [('bad-format','not-a-digest',False),('opaque-format-only','a'*64,True)]:
   x=copy.deepcopy(fixture);x[n]['sha256']=digest;x[n]['path']='hyp:unresolved';probe(carrier_probes,n+'-'+label,x,mv,expected)
 for n in ['source_repository','target_repository']:
  x=copy.deepcopy(fixture);x[n]['path']='hyp:unresolved';probe(carrier_probes,n+'-unresolved-path',x,mv,True)
 x=copy.deepcopy(fixture);x['claim_ceiling']='hyp:This migration already ran successfully and grants authority';probe(carrier_probes,'overclaimed-migration-text-shape-valid',x,mv,True)
 for name in ['execution-authority','overwrite','missing-rollback']:probe(carrier_probes,'bound-negative-'+name,docs['negative_'+name],mv,False)
 reports=profiles();fs=frames();report={'schema_version':'definition-assurance-Validation-authority-profile/v1-candidate','status':'PASS-for-qualified-Validation-hypotheses-and-migration-semantic-use-C13-shape-observations','authority_effect':'none','source':source,'profiles':reports,'finite_comparison_frames':fs,'actual_checks':checks,'actual_check_count':len(checks),'selected_inputs':refs,'checker_bindings':[refs['checker'],b.ref(b.IMPL/'contracts.py')],'runtime_bindings':runtime,'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'direct_binding_is_semantic_use':True,'direct_binding_is_accepted_Validation_evaluation_record_map':False,'generic_Definition_current_type_ref':generic['artifact_type_ref'],'generic_Definition_semantic_ref':generic['semantic_definition_refs'][0],'C13_profile_record_ref':record['record_id'],'C13_profile_is_every_Validation_profile':False,'Definition_schema_probes':definition_probes,'C13_profile_schema_probes':profile_probes,'migration_schema_probes':carrier_probes,'missing_dedicated_Validation_fields':missing,'field_absence_proves_representational_impossibility':False,'source_map_obligations':MAP_FIELDS,'accepted_source_to_carrier_or_consumer_map_refs':[],'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_execution_check_correctness_complete_coverage_Conformance_admission_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified hypotheses,finite proposed-map frames and actual current catalog/migration-semantic-use/C13 generic Definition-profile schema and pure projection observations only. One current type metadata binding uses exact Validation meaning; no accepted Validation evaluation-record map,executed package validator,reference resolution,migration execution,actual correctness or coverage,Conformance,admission,authority,owner fidelity or whole proof.'}
 b.unchanged(list(refs.values())+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh qualification/profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'qualification_profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'finite_frames':len(x['finite_comparison_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_comparison_frames']),'actual_checks':x['actual_check_count'],'Definition_schema_probes':len(x['Definition_schema_probes']),'C13_profile_schema_probes':len(x['C13_profile_schema_probes']),'migration_schema_probes':len(x['migration_schema_probes']),'direct_current_definition_binding_types':x['direct_current_definition_binding_types'],'semantic_ready':False},indent=2))
if __name__=='__main__':main()
