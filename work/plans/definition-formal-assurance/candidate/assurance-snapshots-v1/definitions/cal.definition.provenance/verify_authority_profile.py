"""Qualified Provenance hypotheses and actual C12 prototype/C13 Definition evaluation profile observations."""
import ast,copy,json
import build_candidate as b
import verifier as v
AXES=['identity','kind','source','normalized_context','object','path','step_position','source_reference','relation_kind','operation','handler','posture','missing_segment','residue_route','typed_use']
FORBIDDEN=['C12_scaffold_is_instance_authority','C13_Definition_profile_is_Provenance_path_profile','generic_type_admission_is_instance_admission','source_admission_is_translation_fidelity','typed_trail_is_proof','complete_trail_is_actual_completeness','complete_trail_is_truth','posture_metadata_inherits_authority','operation_label_executes_operation','strict_path_order_proves_historical_chronology','source_object_graph_is_automatically_acyclic','empty_trail_is_automatically_complete','owner_process_labels_are_exclusive','untyped_came_from_licenses_authority_use','schema_PASS_grants_admission','nonentailment_denies_supported_outcomes']
MAP_FIELDS=['normalized_classification','D35_lineage','record_object','record_context','typed_path','five_field_step','step_positions','strict_per_path_order','repeated_sources','source_reference_precision','relation_labels','operation_semantics','owner_or_process','historical_posture','missing_segments','explicit_residue','owner_routes','complete_incomplete_declarations','empty_trail_policy','typed_authority_use']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_completeness_truth_proof_trust_validation_credit_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-Provenance-necessary-guard-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('distinct-C12-Provenance-scaffold-and-C13-Definition-profile-with-unaccepted-map',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'typed_precision_as_sufficient_authority':False,'incomplete_without_owner_routed_residue':False,'sibling_assignment_declared':True,'explicit_sibling_ref':'hyp:separate-originates-from-relation'};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   for n in ['source_role_collapsed','typed_precision_as_sufficient_authority','incomplete_without_owner_routed_residue']:
    if x[n]:errors.append('forbidden:'+n)
   if x['sibling_assignment_declared'] and not x['explicit_sibling_ref']:errors.append('missing-sibling-ref')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-shape-or-profile-does-not-prove-actual-outcome')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_completeness_truth_proof_trust_validation_credit_or_authority_verified':False,'universal_source_to_profile_mapping_proof':False})
 add('complete-proposed-source-map-without-acceptance',lambda x:None,False)
 add('separate-Definition-profile-with-explicit-Provenance-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS}),False)
 add('no-sibling-assignment',lambda x:x.update(sibling_assignment_declared=False,explicit_sibling_ref=''),False)
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
 for n in ['source_role_collapsed','typed_precision_as_sufficient_authority','incomplete_without_owner_routed_residue','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_ref=''),True)
 return rows
def pure_functions(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');profile_type=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation-profile/v1')
 prototype=b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-provenance/v1/artifact.json'
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/generic['schema_path'],'C13_foundation_schema':b.ROOT/profile_type['schema_path'],'C13_profile':b.ROOT/'authority/profiles/definition/v1/evaluation.json','C13_decision':b.ROOT/'docs/decisions/0013-foundation-01-admission/decision.json','C13_profile_generator':b.ROOT/'authority/foundation/v1/render.py','C13_profile_projection':b.ROOT/'authority/profiles/definition/v1/EVALUATION.md','C12_prototype':prototype,'C12_prototype_projection':prototype.with_name('ARTIFACT.md'),'C12_prototype_renderer':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/followups.py','C12_normalization':b.ROOT/'docs/normalizations/0001-definition-migration-model/normalization.json','checker':b.UNIT/'verify_authority_profile.py'};refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];foundation=docs['C13_foundation_schema'];ps={'$schema':foundation['$schema'],'$defs':foundation['$defs'],'$ref':profile_type['schema_selector']};b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(ps);dv=b.c.Draft202012Validator(ds);pv=b.c.Draft202012Validator(ps);record=docs['C13_profile'];proto=docs['C12_prototype'];decision=docs['C13_decision'];admitted=[x for x in decision['admitted_records'] if x['record_id']==record['record_id']];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('catalog143rows121current',len(rows)==143 and len(current)==121)
 ck('no-direct-current-Provenance-carrier',not direct)
 ck('generic-current-Definition-separate-meaning',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('generic-C13-EvaluationProfile-selector-exact',profile_type['admission_decision_ref']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and profile_type['schema_selector']=='#/$defs/evaluationProfile' and profile_type['semantic_definition_refs']==[] and refs['C13_foundation_schema']['sha256']==profile_type['schema_sha256'])
 ck('C13-exact-Definition-profile-admission',decision['status']=='owner-admitted' and decision['decision_id']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and len(admitted)==1 and admitted[0]['path']==refs['C13_profile']['path'] and admitted[0]['sha256']==refs['C13_profile']['sha256']=='8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9' and admitted[0]['admission_effect']=='definition-evaluation-profile-admitted')
 ck('C13-retained-profile-body-candidate-none',record['status']=='candidate-unadmitted' and record['authority_effect']=='none')
 ck('C13-profile-subject-Definition-not-Provenance-path',record['record_id']=='CAL-EVALUATION-DEFINITION-V1' and record['subject_artifact_type_ref']=='cal.artifact-type.definition/v1' and record['outcomes']==['PASS','FAIL','NOT_EVALUABLE'] and record['evaluation_mode']=='collect-all')
 ck('C13-profile13required7checks',len(foundation['$defs']['evaluationProfile']['allOf'][1]['required'])==13 and len(record['checks'])==7 and not list(pv.iter_errors(record)))
 ck('C13-generator-bytes-bound',record['source_direction']['generator_sha256']==refs['C13_profile_generator']['sha256'])
 ck('C12-Provenance-exact-normalization-contract',proto['normalized_contract']==next(x for x in docs['C12_normalization']['semantic_concepts'] if x['concept_id']=='semantic.provenance')=={'carrier_ref':'type.definition','concept_id':'semantic.provenance','owner_scope':'scope.lineage','semantic_kind':'definition','term':'Provenance'})
 ck('C12-retained-semantic-scaffold-no-instance-admission',proto['target_id']=='semantic.provenance' and proto['family']=='semantic' and proto['status']=='prototype-scaffold' and proto['authority_effect']=='none' and proto['owner_decision_ref']=='CAL-DECISION-0012-NORMALIZE-01-DEFAULTS')
 ck('C12-revise-D35-keeps-separate-originates-from-target',proto['accepted_source_decisions']==[{'decision':'revise','legacy_id':'CAV2-D35','legacy_term':'Provenance'}] and next(x for x in docs['C12_normalization']['migration_decisions'] if x['legacy_id']=='CAV2-D35')['targets']==['semantic.provenance','relation.originates-from'])
 ck('C12-D35-source-digest-exact',len(proto['source_refs'])==1 and proto['source_refs'][0]['section_sha256']==load('source-checks.json')['selected_source_sections'][0]['sha256']=='b7855fd81c1ed14fe1bdb097fddfa2b1d32c2f88c8dc2f56dbf131f0164c5439')
 ck('selected-Definition-v1-valid',not list(dv.iter_errors(docs['source'])))
 ck('C53-source-meaning-admission-not-replaced',load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and load('source-checks.json')['selected_source_sections'][0]['admission']['target_definition_refs']==[source['version_ref']])
 gen=pure_functions(paths['C13_profile_generator'],['header','evaluation']);before=copy.deepcopy(record);p1=(gen['evaluation'](before).rstrip()+'\n').encode();p2=(gen['evaluation'](before).rstrip()+'\n').encode();ck('two-pure-C13-profile-projections-preserve-input',p1==p2==paths['C13_profile_projection'].read_bytes() and before==record)
 gen=pure_functions(paths['C12_prototype_renderer'],['render_target']);before=copy.deepcopy(proto);p1=gen['render_target'](before).encode();p2=gen['render_target'](before).encode();ck('two-pure-C12-Provenance-projections-preserve-input',p1==p2==paths['C12_prototype_projection'].read_bytes() and before==proto)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];profile_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_completeness_truth_proof_trust_validation_credit_or_authority_verified':False})
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in ['object_ref','path','step_position','source_reference','relation_kind','operation','handler','posture','missing_segment','residue_route','typed_authority_use']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:complete typed lineage proves truth,trust,validation and actual authority';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 probe(profile_probes,'exact-admitted-C13-Definition-profile-body',copy.deepcopy(record),pv,True)
 for n in foundation['$defs']['evaluationProfile']['allOf'][1]['required']:
  x=copy.deepcopy(record);x.pop(n);probe(profile_probes,'missing-root-'+n,x,pv,False)
 for n in ['check_id','purpose','blocked_by']:
  x=copy.deepcopy(record);x['checks'][0].pop(n);probe(profile_probes,'missing-check-'+n,x,pv,False)
 for n in ['record_id','owner_ref','claim_ceiling','admission_rule']:
  for label,value,expected in [('empty','',False),('whitespace',' ',True),('unresolved','hyp:unresolved',True)]:
   x=copy.deepcopy(record);x[n]=value;probe(profile_probes,n+'-'+label,x,pv,expected)
 x=copy.deepcopy(record);x['claim_ceiling']='hyp:this profile grants Provenance completeness,proof and authority';probe(profile_probes,'overclaimed-profile-text-shape-valid',x,pv,True)
 reports=profiles();fs=frames();report={'schema_version':'definition-assurance-Provenance-authority-profile/v1-candidate','status':'PASS-for-qualified-Provenance-hypotheses-and-separate-C12-C13-shape-observations','authority_effect':'none','source':source,'profiles':reports,'finite_comparison_frames':fs,'actual_checks':checks,'actual_check_count':len(checks),'selected_inputs':refs,'checker_bindings':[refs['checker'],b.ref(b.IMPL/'contracts.py')],'runtime_bindings':runtime,'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic['artifact_type_ref'],'generic_Definition_semantic_ref':generic['semantic_definition_refs'][0],'C13_profile_record_ref':record['record_id'],'C13_profile_is_Provenance_path_profile':False,'C12_prototype_status':proto['status'],'C12_prototype_disposition':'revise','Definition_schema_probes':definition_probes,'C13_profile_schema_probes':profile_probes,'source_map_obligations':MAP_FIELDS,'accepted_source_to_carrier_or_consumer_map_refs':[],'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_provenance_completeness_truth_proof_trust_validation_credit_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Authored qualified hypotheses,finite proposed-map frames and actual current catalog/C12 semantic scaffold/C13 generic Definition-profile schema and pure projection observations. No direct current Provenance carrier was found. No accepted lineage map,live consumer,actual completeness,truth,proof,trust,validation,credit,authority or whole proof.'}
 b.unchanged(list(refs.values())+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh qualification/profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'qualification_profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'finite_frames':len(x['finite_comparison_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_comparison_frames']),'actual_checks':x['actual_check_count'],'Definition_schema_probes':len(x['Definition_schema_probes']),'C13_profile_schema_probes':len(x['C13_profile_schema_probes']),'direct_current_definition_binding_types':x['direct_current_definition_binding_types'],'semantic_ready':False},indent=2))
if __name__=='__main__':main()
