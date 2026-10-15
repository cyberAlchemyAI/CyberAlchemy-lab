"""Qualified Lifetime hypotheses; actual catalog,C12/C13 and paired consumer meaning observations."""
import ast,copy,json
import build_candidate as b
import verifier as v
AXES=['lifetime_assignment', 'artifact_ref', 'canonical_kind', 'authority_kind', 'maturity_status', 'kind_default_durability', 'effective_durability', 'intended_lifespan', 'owner', 'owner_note', 'owner_note_subject', 'owner_note_owner', 'owner_note_chosen_value', 'proposition_ref', 'assertion_record', 'assertion_sign', 'assertion_use', 'time', 'context', 'supersession_declaration', 'supersession_old', 'supersession_new', 'supersession_order']
FORBIDDEN=['C12_scaffold_is_instance_authority', 'C13_Definition_profile_is_Lifetime_consistency_detector', 'generic_type_admission_is_instance_admission', 'source_admission_is_translation_fidelity', 'declared_lifespan_proves_retention', 'perennial_class_implies_authority', 'authority_kind_determines_lifespan', 'maturity_determines_lifespan', 'kind_default_is_always_effective_value', 'owner_note_declaration_proves_override_authority', 'owner_reference_authenticates_owner', 'assertion_sign_is_logical_truth', 'ephemeral_requires_live_opposition_everywhere', 'perennial_quoted_opposition_is_live_defect', 'historical_use_is_live_endorsement', 'local_declared_order_proves_chronology', 'future_third_tag_is_current_value', 'D52_split_targets_merged', 'Artifact_fixed_durability_imported_as_effective_value', 'unresolved_Artifact_Lifetime_mapping_claimed_consistent', 'schema_PASS_grants_admission', 'nonentailment_denies_supported_outcomes']
MAP_FIELDS=['lifetime_assignment', 'artifact_ref', 'canonical_kind', 'authority_kind', 'maturity_status', 'kind_default_durability', 'effective_durability', 'intended_lifespan', 'owner', 'owner_note', 'owner_note_subject', 'owner_note_owner', 'owner_note_chosen_value', 'proposition_ref', 'assertion_record', 'assertion_sign', 'assertion_use', 'time', 'context', 'supersession_declaration', 'supersession_old', 'supersession_new', 'supersession_order', 'normalized_classification', 'D52_lineage_and_split_targets', 'canonical_artifact_applicability', 'current_two_tag_durability', 'exact_owner_noted_override', 'authority_maturity_orthogonality', 'scoped_live_contradiction', 'ephemeral_permission_without_requirement', 'historical_and_quoted_not_live', 'exact_supersession_binding', 'local_declared_order_not_chronology', 'Artifact_default_effective_bridge', 'consumer_binding']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def envelope():return {n:'hyp:'+n for n in AXES}
def profiles():
 rows=[];base=envelope();flags={n:False for n in FORBIDDEN}
 def add(id,after,f,reject):
  errors=['changed-binding:'+n for n in AXES if base[n]!=after[n]]+['forbidden-inference:'+n for n in FORBIDDEN if f[n]];assert bool(errors)==reject
  rows.append({'case_id':id,'before':base,'after':after,'flags':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_preservation_truth_chronology_override_authority_verified':False,'source_fidelity_accepted':False})
 add('exact-qualified-Lifetime-necessary-guard-hypothesis',copy.deepcopy(base),copy.deepcopy(flags),False)
 add('distinct-C12-Lifetime-scaffold-and-C13-Definition-profile-with-unaccepted-map',copy.deepcopy(base),copy.deepcopy(flags),False)
 for n in AXES:
  x=copy.deepcopy(base);x[n]='hyp:changed';add('changed-'+n,x,copy.deepcopy(flags),True)
 for n in FORBIDDEN:
  x=copy.deepcopy(flags);x[n]=True;add('forbidden-'+n,copy.deepcopy(base),x,True)
 return rows
def frames():
 base={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','claim_scope_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'posture_metadata_as_sufficient_authority':False,'unresolved_durability_mapping_ignored':False,'sibling_assignment_declared':True,'explicit_sibling_refs':['hyp:profile.retention','hyp:profile.semantic-consistency']};rows=[]
 def qualified(x):x.update(full_alignment_claimed=True,accepted_map_refs={n:'hyp:map:'+n for n in MAP_FIELDS},owner_review_ref='hyp:owner',claim_scope_ref='hyp:scope')
 def add(id,mutate,reject):
  x=copy.deepcopy(base);mutate(x);errors=[]
  if x['before']!=x['after']:errors.append('changed-qualification')
  if x['selected']:
   errors+=['lost-obligation:'+n for n in MAP_FIELDS if not x['map_fields'].get(n)]
   for n in ['source_role_collapsed','posture_metadata_as_sufficient_authority','unresolved_durability_mapping_ignored']:
    if x[n]:errors.append('forbidden:'+n)
   if x['sibling_assignment_declared'] and (len(x['explicit_sibling_refs'])!=2 or len(set(x['explicit_sibling_refs']))!=2):errors.append('missing-sibling-ref')
   if x['full_alignment_claimed']:
    errors+=['missing-accepted-map:'+n for n in MAP_FIELDS if not x['accepted_map_refs'].get(n)]
    if not x['owner_review_ref'] or not x['claim_scope_ref']:errors.append('missing-owner-review-or-scope')
  if x['actual_outcome_claimed']:errors.append('hypothesis-shape-or-profile-does-not-prove-actual-outcome')
  assert bool(errors)==reject,(id,errors)
  rows.append({'case_id':id,'frame':x,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'actual_preservation_truth_chronology_override_authority_verified':False,'universal_source_to_profile_mapping_proof':False})
 add('complete-proposed-source-map-without-acceptance',lambda x:None,False)
 add('separate-Definition-profile-with-explicit-Lifetime-residue',lambda x:x['map_fields'].update({n:'explicit-source-residue' for n in MAP_FIELDS}),False)
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
 for n in ['source_role_collapsed','posture_metadata_as_sufficient_authority','unresolved_durability_mapping_ignored','actual_outcome_claimed']:add('forbidden-'+n,lambda x,n=n:x.update({n:True}),True)
 add('missing-sibling-ref',lambda x:x.update(explicit_sibling_refs=[]),True)
 return rows
def pure_functions(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==set(names);ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns);return ns
def verify(write=False):
 context=load('context.json');typed_receipt=load('types-logic-receipt.json');b.unchanged(typed_receipt['inputs']+typed_receipt['producer_results']+context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();source=load('t.json')['payload']['source'];rp=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=json.loads(rp.read_bytes());rows=registry['admitted_contracts'];current=[x for x in rows if x['lifecycle_state']=='admitted-current'];direct=[x for x in current if source['version_ref'] in x['semantic_definition_refs']];generic=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.definition/v2');profile_type=next(x for x in current if x['artifact_type_ref']=='cal.artifact-type.evaluation-profile/v1')
 prototype=b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-artifact-lifetime/v1/artifact.json'
 paths={'registry':rp,'source':b.ROOT/source['path'],'Definition_generator':b.ROOT/'authority/artifact-types/definition/v1/generator.py','Definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json','current_Definition_schema':b.ROOT/generic['schema_path'],'C13_foundation_schema':b.ROOT/profile_type['schema_path'],'C13_profile':b.ROOT/'authority/profiles/definition/v1/evaluation.json','C13_decision':b.ROOT/'docs/decisions/0013-foundation-01-admission/decision.json','C13_profile_generator':b.ROOT/'authority/foundation/v1/render.py','C13_profile_projection':b.ROOT/'authority/profiles/definition/v1/EVALUATION.md','C12_prototype':prototype,'C12_prototype_projection':prototype.with_name('ARTIFACT.md'),'C12_prototype_renderer':b.ROOT/'evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/followups.py','C12_normalization':b.ROOT/'docs/normalizations/0001-definition-migration-model/normalization.json','checker':b.UNIT/'verify_authority_profile.py'}
 consumer_sources=[b.source_ref(snap,'cal.definition.'+n) for n in ['artifact','canonical-representation-invariant']]
 for selected in consumer_sources:
  n=selected['definition_id'];q=b.ROOT/selected['path'];paths[n]=q;paths[n+'-projection']=q.with_name('DEFINITION.md')
 refs={k:b.ref(p) for k,p in paths.items()};docs={k:json.loads(p.read_bytes()) for k,p in paths.items() if p.suffix=='.json'};ds=docs['Definition_schema'];foundation=docs['C13_foundation_schema'];ps={'$schema':foundation['$schema'],'$defs':foundation['$defs'],'$ref':profile_type['schema_selector']};b.c.Draft202012Validator.check_schema(ds);b.c.Draft202012Validator.check_schema(ps);dv=b.c.Draft202012Validator(ds);pv=b.c.Draft202012Validator(ps);record=docs['C13_profile'];proto=docs['C12_prototype'];decision=docs['C13_decision'];admitted=[x for x in decision['admitted_records'] if x['record_id']==record['record_id']];checks=[]
 def ck(id,ok):checks.append({'check_id':id,'result':bool(ok)})
 ck('catalog143rows121current',len(rows)==143 and len(current)==121)
 ck('no-direct-current-Lifetime-carrier',not direct)
 ck('generic-current-Definition-separate-meaning',generic['semantic_definition_refs']==[b.source_ref(snap,'cal.definition.definition')['version_ref']])
 ck('generic-C13-EvaluationProfile-selector-exact',profile_type['admission_decision_ref']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and profile_type['schema_selector']=='#/$defs/evaluationProfile' and profile_type['semantic_definition_refs']==[] and refs['C13_foundation_schema']['sha256']==profile_type['schema_sha256'])
 ck('C13-exact-Definition-profile-admission',decision['status']=='owner-admitted' and decision['decision_id']=='CAL-DECISION-0013-FOUNDATION-01-ADMISSION' and len(admitted)==1 and admitted[0]['path']==refs['C13_profile']['path'] and admitted[0]['sha256']==refs['C13_profile']['sha256']=='8d77ba1a649cff55e51fc55cbbad17fed59a4f19e0be0638a5b18bf2ba4d04a9' and admitted[0]['admission_effect']=='definition-evaluation-profile-admitted')
 ck('C13-retained-profile-body-candidate-none',record['status']=='candidate-unadmitted' and record['authority_effect']=='none')
 ck('C13-profile-subject-Definition-not-Lifetime-consistency',record['record_id']=='CAL-EVALUATION-DEFINITION-V1' and record['subject_artifact_type_ref']=='cal.artifact-type.definition/v1' and record['outcomes']==['PASS','FAIL','NOT_EVALUABLE'] and record['evaluation_mode']=='collect-all')
 ck('C13-profile13required7checks',len(foundation['$defs']['evaluationProfile']['allOf'][1]['required'])==13 and len(record['checks'])==7 and not list(pv.iter_errors(record)))
 ck('C13-generator-bytes-bound',record['source_direction']['generator_sha256']==refs['C13_profile_generator']['sha256'])
 ck('C12-Lifetime-exact-normalization-contract',proto['normalized_contract']==next(x for x in docs['C12_normalization']['semantic_concepts'] if x['concept_id']=='semantic.artifact-lifetime')=={'carrier_ref':'type.definition','concept_id':'semantic.artifact-lifetime','owner_scope':'scope.shared-authority','semantic_kind':'definition','term':'Artifact Lifetime'})
 ck('C12-retained-Lifetime-scaffold-no-instance-admission',proto['target_id']=='semantic.artifact-lifetime' and proto['family']=='semantic' and proto['status']=='prototype-scaffold' and proto['authority_effect']=='none' and proto['owner_decision_ref']=='CAL-DECISION-0012-NORMALIZE-01-DEFAULTS')
 ck('C12-split-D52-keeps-three-distinct-targets',proto['accepted_source_decisions']==[{'decision':'split','legacy_id':'CAV2-D52','legacy_term':'Artifact Durability'}] and next(x for x in docs['C12_normalization']['migration_decisions'] if x['legacy_id']=='CAV2-D52')['targets']==['semantic.artifact-lifetime','profile.retention','profile.semantic-consistency'])
 ck('C12-D52-source-digest-exact',len(proto['source_refs'])==1 and proto['source_refs'][0]['section_sha256']==load('source-checks.json')['recorded_D52_source_use']['selected_sha256']=='13901f51e52227f10c9dc9aab3d9977d2047127114a82c3aaf6dbdaf17fbf7c5')
 ck('selected-Definition-v1-valid',not list(dv.iter_errors(docs['source'])))
 ck('C53-current-meaning-distinct-from-C12-split',load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION' and load('source-checks.json')['recorded_D52_source_use']['target_definition_refs']==[source['version_ref']])
 gen=pure_functions(paths['C13_profile_generator'],['header','evaluation']);before=copy.deepcopy(record);p1=(gen['evaluation'](before).rstrip()+'\n').encode();p2=(gen['evaluation'](before).rstrip()+'\n').encode();ck('two-pure-C13-profile-projections-preserve-input',p1==p2==paths['C13_profile_projection'].read_bytes() and before==record)
 gen=pure_functions(paths['C12_prototype_renderer'],['render_target']);before=copy.deepcopy(proto);p1=gen['render_target'](before).encode();p2=gen['render_target'](before).encode();ck('two-pure-C12-Lifetime-projections-preserve-input',p1==p2==paths['C12_prototype_projection'].read_bytes() and before==proto)
 ck('Lifetime-source-two-primary-consumer-labels',docs['source']['primary_consumer_refs']==['semantic.artifact','semantic.canonical-representation-invariant'])
 override=docs['source']['scope']['applicability'];ck('Lifetime-kind-default-owner-noted-override-retained','Assign durability per canonical-kind as a default' in override and 'overridable per instance with an owner note' in override)
 gen=pure_functions(paths['Definition_generator'],['esc','bullets','render']);observations=[]
 for selected,label,sha in zip(consumer_sources,['semantic.artifact','semantic.canonical-representation-invariant'],['554dda3aec8fb66fdfd2a910d90defa56235705e482fa24184f31957a2b1d785','36d484e269e9aeb79e2e4653874062157a07cc6a04d5edacfaa3502b441bbe76']):
  name=selected['definition_id'];doc=docs[name];row=next(x for x in snap['current_entries'] if x['definition_id']==name)
  ck(name+'-exact-current-C53',refs[name]=={'path':selected['path'],'sha256':selected['sha256']} and selected['sha256']==sha and row['admission_decision_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION')
  ck(name+'-normalized-label-and-Definition-shape','identified by '+label in doc['voices']['scientific_formal']['normative_statement'] and not list(dv.iter_errors(doc)))
  formal=doc['voices']['scientific_formal']['formal_expression'];start=formal.index('Each canonical artifact');end=formal.index('`allowed_origins(kind)`');excerpt=formal[start:end]
  ck(name+'-kind-derived-durability-observed','inherits from its kind' in excerpt and 'CAV2-D52' in excerpt and 'durability' in excerpt and 'derived, not' in excerpt)
  before=copy.deepcopy(doc);first=gen['render'](before).encode();second=gen['render'](before).encode();ck(name+'-two-pure-projections-preserve-input',first==second==paths[name+'-projection'].read_bytes() and before==doc)
  observations.append({'declared_consumer_ref':label,'observed_current_meaning_source':selected,'observed_kind':'Definition meaning;not implemented or live consumer','source_selector':'/voices/scientific_formal/formal_expression','kind_derived_durability_excerpt':excerpt,'excerpt_sha256':b.r.digest(excerpt.encode()),'first_render_sha256':b.r.digest(first),'second_render_sha256':b.r.digest(second),'accepted_consumer_map_refs':[],'native_or_live_consumer_executed':False})
 cross={'finding_id':'LIFE-CONSUMER-FINDING-001','related_prior_finding_id':'ART-CONSUMER-FINDING-001','status':'unresolved','Artifact_and_CanonicalRepresentation_sources_inherit_kind_durability':True,'Lifetime_explicit_owner_noted_effective_override':True,'Lifetime_override_selector':'/scope/applicability','Lifetime_override_excerpt':override,'Lifetime_override_excerpt_sha256':b.r.digest(override.encode()),'affected_consumer_meaning_sources':consumer_sources,'possible_resolution':'Distinguish kind-derived default from effective instance durability;resolve exact fields,kind granularity and owner precedence. Fine versus coarse kinds alone do not resolve the instance override.','accepted_kind_granularity_or_durability_map_refs':[],'common_meaning_consistency_verified':False,'owner_route':'Artifact,Lifetime,CanonicalRepresentationInvariant,kind,classifications and definition owners','claim_ceiling':'Paired source observations only;no accepted consistency or proved contradiction.'}
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 definition_probes=[];profile_probes=[]
 def probe(bucket,id,doc,validator,expected):
  errors=[{'path':'/'+('/'.join(str(x) for x in e.absolute_path)),'message':e.message} for e in validator.iter_errors(doc)];accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected shape '+id+' '+str(errors))
  bucket.append({'case_id':id,'schema_accepted':accepted,'errors':errors,'actual_preservation_truth_chronology_override_authority_verified':False})
 original=docs['source'];probe(definition_probes,'exact-selected-Definition',copy.deepcopy(original),dv,True)
 for n in ds['required']:
  x=copy.deepcopy(original);x.pop(n);probe(definition_probes,'missing-root-'+n,x,dv,False)
 for n in ['lifetime_assignment_ref', 'artifact_ref', 'canonical_kind', 'authority_kind', 'maturity_status', 'kind_default_durability', 'effective_durability', 'intended_lifespan_ref', 'owner_note_ref', 'proposition_ref', 'assertion_record_ref', 'assertion_sign', 'assertion_use', 'time_ref', 'context_ref', 'supersession_old_ref', 'supersession_new_ref', 'temporal_order_ref']:
  x=copy.deepcopy(original);x[n]='hyp:claimed';probe(definition_probes,'instance-field-not-Definition-'+n,x,dv,False)
 for n in ['definition_id','term','semantic_owner_ref']:
  x=copy.deepcopy(original);x[n]='hyp:unresolved';probe(definition_probes,'unresolved-'+n,x,dv,True)
 x=copy.deepcopy(original);x['voices']['scientific_formal']['normative_statement']='hyp:lifespan and owner-note declarations prove retention,logical truth,verified chronology and override authority';probe(definition_probes,'overclaimed-text-shape-valid',x,dv,True)
 probe(profile_probes,'exact-admitted-C13-Definition-profile-body',copy.deepcopy(record),pv,True)
 for n in foundation['$defs']['evaluationProfile']['allOf'][1]['required']:
  x=copy.deepcopy(record);x.pop(n);probe(profile_probes,'missing-root-'+n,x,pv,False)
 for n in ['check_id','purpose','blocked_by']:
  x=copy.deepcopy(record);x['checks'][0].pop(n);probe(profile_probes,'missing-check-'+n,x,pv,False)
 for n in ['record_id','owner_ref','claim_ceiling','admission_rule']:
  for label,value,expected in [('empty','',False),('whitespace',' ',True),('unresolved','hyp:unresolved',True)]:
   x=copy.deepcopy(record);x[n]=value;probe(profile_probes,n+'-'+label,x,pv,expected)
 x=copy.deepcopy(record);x['claim_ceiling']='hyp:this profile grants Lifetime retention,truth,chronology and override authority';probe(profile_probes,'overclaimed-profile-text-shape-valid',x,pv,True)
 reports=profiles();fs=frames();report={'schema_version':'definition-assurance-ArtifactLifetime-authority-profile/v1-candidate','status':'PASS-for-qualified-Lifetime-hypotheses-and-separate-C12-C13-consumer-meaning-observations','authority_effect':'none','source':source,'profiles':reports,'finite_comparison_frames':fs,'actual_checks':checks,'actual_check_count':len(checks),'selected_inputs':refs,'checker_bindings':[refs['checker'],b.ref(b.IMPL/'contracts.py')],'runtime_bindings':runtime,'current_type_registry_rows':len(rows),'admitted_current_type_rows':len(current),'direct_current_definition_binding_types':[x['artifact_type_ref'] for x in direct],'generic_Definition_current_type_ref':generic['artifact_type_ref'],'generic_Definition_semantic_ref':generic['semantic_definition_refs'][0],'C13_profile_record_ref':record['record_id'],'C13_profile_is_Lifetime_consistency_detector':False,'C12_prototype_status':proto['status'],'C12_prototype_disposition':'split','C12_split_targets':['semantic.artifact-lifetime','profile.retention','profile.semantic-consistency'],'Definition_schema_probes':definition_probes,'C13_profile_schema_probes':profile_probes,'consumer_meaning_observations':observations,'cross_definition_review_findings':[cross],'source_map_obligations':MAP_FIELDS,'accepted_source_to_carrier_or_consumer_map_refs':[],'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_preservation_truth_chronology_override_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified proposed lifespan/default/override/record-use maps,current catalog,C12 semantic scaffold and C13 generic Definition-profile shape and pure projections;two consumer Definition meanings observed. No accepted default/effective bridge,live consumer,actual preservation,truth,chronology,override authority,owner fidelity or whole proof.'}
 b.unchanged(list(refs.values())+context['sources']+typed_receipt['inputs']);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh qualification/profile observations differ')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'qualification_profiles':len(x['profiles']),'rejected_profiles':sum(z['expected_rejection'] for z in x['profiles']),'finite_frames':len(x['finite_comparison_frames']),'rejected_frames':sum(z['expected_rejection'] for z in x['finite_comparison_frames']),'actual_checks':x['actual_check_count'],'Definition_schema_probes':len(x['Definition_schema_probes']),'C13_profile_schema_probes':len(x['C13_profile_schema_probes']),'consumer_meaning_sources':len(x['consumer_meaning_observations']),'mapping_obligations':len(x['source_map_obligations']),'direct_current_definition_binding_types':x['direct_current_definition_binding_types'],'semantic_ready':False},indent=2))
if __name__=='__main__':main()
