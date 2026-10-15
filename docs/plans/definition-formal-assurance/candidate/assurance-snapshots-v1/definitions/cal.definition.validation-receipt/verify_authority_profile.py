"""Qualified ValidationReceipt hypotheses and actual producer-report/C13 Definition evaluation profile observations."""
import ast,copy,json
import build_candidate as b
import verifier as v
AXES=['receipt_identity', 'event', 'subject', 'profile', 'validator', 'environment', 'emitted_at', 'claim_ceiling', 'context', 'input_occurrence', 'input_reference', 'exact_digest', 'declared_check', 'outcome', 'evidence', 'causal_blocker', 'observation', 'input_comparison', 'authority_state', 'lifecycle_state']
FORBIDDEN=['recorded_report_is_instance_authority', 'C13_Definition_profile_is_Receipt_record_profile', 'generic_type_admission_is_instance_admission', 'source_admission_is_translation_fidelity', 'receipt_existence_proves_Conformance', 'reported_PASS_proves_Admission', 'stable_scoped_observations_prove_temporal_immutability', 'declared_inputs_prove_byte_resolution', 'declared_checks_prove_discovery_completeness', 'declared_blockers_prove_causal_adequacy', 'equal_states_prove_runtime_preservation', 'recorded_time_proves_clock_accuracy', 'missing_root_field_proves_mapping_impossibility', 'report_material_digest_is_accepted_receipt_map', 'countermodel_denies_independent_support', 'report_schema_is_admitted_Receipt_format', 'historical_blockers_are_current_admission_state']
MAP_FIELDS=['receipt_identity', 'event', 'subject', 'profile', 'validator', 'environment', 'emitted_at', 'claim_ceiling', 'context', 'input_occurrence', 'input_reference', 'exact_digest', 'declared_check', 'outcome', 'evidence', 'causal_blocker', 'observation', 'input_comparison', 'authority_state', 'lifecycle_state', 'event_scalar_correspondence', 'exact_event_membership', 'check_dependency_endpoints', 'all_declared_checks_recorded', 'inclusive_change_or_invalidation', 'record_only_preservation', 'authority_effect_none', 'consumer_binding']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_immutability_event_coverage_causality_preservation_conformance_or_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-ValidationReceipt-necessary-guard-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('distinct-consumer-reports-and-C13-Definition-profile-with-unaccepted-map',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'posture_metadata_as_sufficient_authority':False,'declared_check_omitted':False,'sibling_assignment_declared':True,'explicit_sibling_ref':'hyp:separate-receipt-type'};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   for n in ['source_role_collapsed','posture_metadata_as_sufficient_authority','declared_check_omitted']:
    if x[n]:errors.append('forbidden:'+n)
   if x['sibling_assignment_declared'] and not x['explicit_sibling_ref']:errors.append('missing-sibling-ref')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-shape-or-profile-does-not-prove-actual-outcome')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_immutability_event_coverage_causality_preservation_conformance_or_authority_verified':False,'universal_source_to_profile_mapping_proof':False})
 add('complete-proposed-source-map-without-acceptance',lambda x:None,False)
 add('separate-Definition-profile-with-explicit-Receipt-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS}),False)
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
 for n in ['source_role_collapsed','posture_metadata_as_sufficient_authority','declared_check_omitted','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_ref=''),True)
 return rows
def pure_functions(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source']
 rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');profile_type=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation-profile/v1')
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/generic['schema_path'],'C13_foundation_schema':b.ROOT/profile_type['schema_path'],'C13_profile':b.ROOT/'authority/profiles/definition/v1/evaluation.json','C13_decision':b.ROOT/'docs/decisions/0013-foundation-01-admission/decision.json','C13_profile_generator':b.ROOT/'authority/foundation/v1/render.py','C13_profile_projection':b.ROOT/'authority/profiles/definition/v1/EVALUATION.md','checker':b.UNIT/'verify_authority_profile.py'}
 original=json.loads(paths['source'].read_bytes());consumer_paths=original['primary_consumer_refs']
 for i,p in enumerate(consumer_paths):paths['consumer_'+str(i)]=b.ROOT/p
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];foundation=docs['C13_foundation_schema'];ps={'$schema':foundation['$schema'],'$defs':foundation['$defs'],'$ref':profile_type['schema_selector']};b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(ps);dv=b.c.Draft202012Validator(ds);pv=b.c.Draft202012Validator(ps);record=docs['C13_profile'];decision=docs['C13_decision'];admitted=[x for x in decision['admitted_records'] if x['record_id']==record['record_id']];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('catalog143rows121current',len(rows)==143 and len(current)==121)
 ck('no-direct-current-Receipt-meaning-binding',not direct)
 ck('no-current-receipt-named-carrier',not [x for x in current if 'receipt' in x['artifact_type_ref'].lower()])
 ck('generic-current-Definition-separate-meaning',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('generic-C13-EvaluationProfile-selector-exact',profile_type['admission_decision_ref']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and profile_type['schema_selector']=='#/$defs/evaluationProfile' and profile_type['semantic_definition_refs']==[] and refs['C13_foundation_schema']['sha256']==profile_type['schema_sha256'])
 ck('C13-exact-Definition-profile-admission',decision['status']=='owner-admitted' and decision['decision_id']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and len(admitted)==1 and admitted[0]['path']==refs['C13_profile']['path'] and admitted[0]['sha256']==refs['C13_profile']['sha256']=='8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9' and admitted[0]['admission_effect']=='definition-evaluation-profile-admitted')
 ck('C13-retained-profile-body-candidate-none',record['status']=='candidate-unadmitted' and record['authority_effect']=='none')
 ck('C13-profile-subject-Definition-not-Receipt-record',record['record_id']=='CAL-EVALUATION-DEFINITION-V1' and record['subject_artifact_type_ref']=='cal.artifact-type.definition/v1' and record['outcomes']==['PASS','FAIL','NOT_EVALUABLE'] and record['evaluation_mode']=='collect-all')
 ck('C13-profile13required7checks',len(foundation['$defs']['evaluationProfile']['allOf'][1]['required'])==13 and len(record['checks'])==7 and not list(pv.iter_errors(record)))
 ck('C13-generator-bytes-bound',record['source_direction']['generator_sha256']==refs['C13_profile_generator']['sha256'])
 ck('selected-Definition-v1-valid',not list(dv.iter_errors(original)))
 ck('C29-source-meaning-admission-separate-from-records',load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1' and 'cal.definition.validation-receipt' in load('source-checks.json')['recorded_D38_source_use']['target_definition_ids'])
 gen=pure_functions(paths['C13_profile_generator'],['header','evaluation']);before=copy.deepcopy(record);p1=(gen['evaluation'](before).rstrip()+'\n').encode();p2=(gen['evaluation'](before).rstrip()+'\n').encode();ck('two-pure-C13-profile-projections-preserve-input',p1==p2==paths['C13_profile_projection'].read_bytes() and before==record)
 expected_schemas=['cyberalchemy-lab-definition-candidate-validation/v1','cyberalchemy-lab-artifact-type-v2-validation/v1','cyberalchemy-lab-craft-identity-chain-validation/v2'];expected_counts=[25,10,12];observations=[]
 for i,p in enumerate(consumer_paths):
  doc=docs['consumer_'+str(i)];summary=doc['summary'];cs=doc['checks']
  ck('consumer-'+str(i)+'-exact-named-producer-schema',doc['schema_version']==expected_schemas[i])
  ck('consumer-'+str(i)+'-recorded-none-and-PASS',doc['authority_effect']=='none' and doc['result']=='PASS')
  ck('consumer-'+str(i)+'-recorded-summary-arithmetic',summary['total']==len(cs)==expected_counts[i] and summary['passed']+summary['failed']==summary['total'] and summary['failed']==0)
  observations.append({'input_ref':refs['consumer_'+str(i)],'schema_version':doc['schema_version'],'subject':doc['subject'],'recorded_result':doc['result'],'authority_effect':doc['authority_effect'],'root_fields':sorted(doc),'materials':doc['materials'],'recorded_summary':summary,'recorded_check_ids':[x.get('check_id',x.get('id')) for x in cs],'retained_promotion_blockers':doc.get('promotion_blockers',[]),'claim_ceiling':doc['claim_ceiling'],'accepted_Receipt_format':False,'accepted_source_map_refs':[],'producer_checks_executed':False,'historical_blockers_reinterpreted_as_current_admission_state':False,'missing_root_fields_imply_mapping_impossibility':False})
 ck('consumer0-recorded-candidate-byte-binding',docs['consumer_0']['materials']['candidate_json_sha256']==b.ref(b.ROOT/'authority/definitions/candidates/0007-cml07-semantic-closure/candidate.json')['sha256'])
 ck('consumer0-recorded-Receipt-definition-byte-binding',docs['consumer_0']['materials']['definition_digests']['cal.definition.validation-receipt']==source['sha256'])
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];profile_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_event_authenticity_immutability_coverage_causality_conformance_or_authority_verified':False})
 probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in ['receipt_id','event_ref','subject_digest','profile_digest','validator_digest','input_occurrences','outcome_records','causal_blockers','emitted_at','before_authority_state','after_lifecycle_state']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:recorded PASS establishes immutable storage,complete causal discovery,Conformance and authority';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 probe(profile_probes,'exact-admitted-C13-Definition-profile-body',copy.deepcopy(record),pv,True)
 for n in foundation['$defs']['evaluationProfile']['allOf'][1]['required']:
  x=copy.deepcopy(record);x.pop(n);probe(profile_probes,'missing-root-'+n,x,pv,False)
 for n in ['check_id','purpose','blocked_by']:
  x=copy.deepcopy(record);x['checks'][0].pop(n);probe(profile_probes,'missing-check-'+n,x,pv,False)
 for n in ['record_id','owner_ref','claim_ceiling','admission_rule']:
  for label,value,expected in [('empty','',False),('whitespace',' ',True),('unresolved','hyp:unresolved',True)]:
   x=copy.deepcopy(record);x[n]=value;probe(profile_probes,n+'-'+label,x,pv,expected)
 x=copy.deepcopy(record);x['claim_ceiling']='hyp:this profile grants Receipt immutable storage,Conformance and authority';probe(profile_probes,'overclaimed-profile-text-shape-valid',x,pv,True)
 reports=profiles();fs=frames();report={'schema_version':'definition-assurance-ValidationReceipt-authority-profile/v1-candidate','status':'PASS-for-qualified-Receipt-hypotheses-and-current-catalog-profile-consumer-observations','authority_effect':'none','source':source,'profiles':reports,'finite_comparison_frames':fs,'actual_checks':checks,'actual_check_count':len(checks),'selected_inputs':refs,'checker_bindings':[refs['checker'],b.ref(b.IMPL/'contracts.py')],'runtime_bindings':runtime,'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic['artifact_type_ref'],'generic_Definition_semantic_ref':generic['semantic_definition_refs'][0],'C13_profile_record_ref':record['record_id'],'C13_profile_is_Receipt_record_profile':False,'Definition_schema_probes':definition_probes,'C13_profile_schema_probes':profile_probes,'named_consumer_observations':observations,'source_map_obligations':MAP_FIELDS,'accepted_source_to_carrier_or_consumer_map_refs':[],'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'direct_carrier_or_consumer_alignment_accepted':False,'actual_immutability_event_coverage_causality_preservation_conformance_or_authority_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Finite authored qualification and proposed-map controls,current catalog,C13 generic Definition-profile schema/pure projection checks,and exact three existing producer-report observations. No admitted Receipt format,accepted mapping,producer-validator execution,actual immutability,event authenticity,discovered completeness,causal adequacy,runtime preservation,Conformance,Admission or whole proof.'}
 b.unchanged(list(refs.values())+context['sources']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh qualification/profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'qualification_profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'finite_frames':len(x['finite_comparison_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_comparison_frames']),'actual_checks':x['actual_check_count'],'Definition_schema_probes':len(x['Definition_schema_probes']),'C13_profile_schema_probes':len(x['C13_profile_schema_probes']),'named_consumer_observations':len(x['named_consumer_observations']),'direct_current_definition_binding_types':x['direct_current_definition_binding_types'],'semantic_ready':False},indent=2))
if __name__=='__main__':main()
