"""Qualified Resolution correspondence hypotheses; no accepted maps or authority effects."""
import copy,json
import build_candidate as b
import inspect_carrier_consumers as consumer
import verifier as v
AXES=list(b.FACETS)+['operation_identity_key','carrier_identity_key','registry_identity_key','type_identity_key','state_identity_key','result_identity_key','discriminator_path_key','discriminator_value_key','explicit_admitted_current_or_historical','current_only_discriminator','exact_union','deduplication','zero_single_multiple_outcomes','recorded_lifecycle_state','none_effect','movement_result_projection','candidate_exclusion','schema_validation_responsibility','product_activation_residue','legacy_and_current_registry_map']
FORBIDDEN=['path_proves_identity','filename_proves_type','extension_proves_type','nearest_name_is_evidence','candidate_explicit_is_admitted','historical_discriminator_is_current','both_routes_count_as_two_types','unknown_reference_is_nearest_type','same_input_changes_match_set','path_projection_difference_changes_type','resolution_is_schema_validation','resolution_is_type_admission','declared_none_effect_grants_authority','out_of_schema_probe_is_compliant_violation','legacy_entries_are_current_v2_without_map','result_discriminator_absence_is_admission_defect','carrier_admission_activates_resolver','hypothetical_map_is_owner_acceptance']
def envelope():return {'source':b.source_ref(b.snapshot(),'cal.definition.artifact-type-resolution'),'scope':b.SCOPE,'role':'candidate-exact-match-union','authority_effect':'none','claim_scope':'necessary-declarations-only','facets':{n:'hyp:'+n for n in AXES},'actual_owner_review_ref':'','accepted_map_refs':[]}
def valid_profile(x):
 before=x['before'];after=x['after']
 return before==after and before==envelope() and not any(x['forbidden'].values()) and set(x['forbidden'])==set(FORBIDDEN) and x['source_role_preserved'] and x['historical_and_current_registry_routes_separate'] and x['four_consumer_findings_retained'] and not x['semantic_acceptance_claimed'] and not x['actual_outcome_claimed']
def profiles():
 baseline={'before':envelope(),'after':envelope(),'forbidden':{n:False for n in FORBIDDEN},'source_role_preserved':True,'historical_and_current_registry_routes_separate':True,'four_consumer_findings_retained':True,'semantic_acceptance_claimed':False,'actual_outcome_claimed':False};cases=[]
 def add(n,mutate,expected):
  x=copy.deepcopy(baseline);mutate(x);assert valid_profile(x)==expected,n;cases.append({'case_id':n,'profile':x,'expected_rejection':not expected,'qualified_hypothesis_satisfied':valid_profile(x),'accepted_semantic_map':False})
 add('exact-unaccepted-resolution-profile',lambda x:None,True)
 for n in FORBIDDEN:add('reject-'+n,lambda x,n=n:x['forbidden'].update({n:True}),False)
 for n in ['source_role_preserved','historical_and_current_registry_routes_separate','four_consumer_findings_retained']:add('missing-'+n,lambda x,n=n:x.update({n:False}),False)
 for n in ['semantic_acceptance_claimed','actual_outcome_claimed']:add('unreviewed-'+n,lambda x,n=n:x.update({n:True}),False)
 for n in ['scope','role','authority_effect','claim_scope']:add('changed-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),False)
 return cases
MAP_FIELDS=AXES+['six_current_meaning_bindings','carrier_body_vs_current_overlay','structured_result_classification','concrete_discriminator_matching','schema_input_domain_correctness','owner_acceptance_and_claim_ceiling']
def valid_frame(x):
 return x['before']==x['after']==envelope() and x['selected'] is True and set(x['map_fields'])==set(MAP_FIELDS) and all(x['map_fields'].values()) and set(x['accepted_map_refs'])==set(MAP_FIELDS) and not any(x['accepted_map_refs'].values()) and x['owner_review_ref']=='' and x['full_alignment_claimed'] is False and x['actual_outcome_claimed'] is False and x['source_role_collapsed'] is False and x['upstream_findings_retained'] is True and x['explicit_sibling_refs']==['hyp:Request-v1-legacy-route','hyp:Registry-v2-current-route','hyp:Resolution-candidate2-current-meaning']
def frames():
 baseline={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'upstream_findings_retained':True,'explicit_sibling_refs':['hyp:Request-v1-legacy-route','hyp:Registry-v2-current-route','hyp:Resolution-candidate2-current-meaning']};cases=[]
 def add(n,mutate,expected):
  x=copy.deepcopy(baseline);mutate(x);assert valid_frame(x)==expected,n;cases.append({'case_id':n,'frame':x,'expected_rejection':not expected,'qualified_unaccepted_frame_satisfied':valid_frame(x)})
 add('complete-pending-source-map',lambda x:None,True)
 for n in MAP_FIELDS:
  add('missing-map-'+n,lambda x,n=n:x['map_fields'].pop(n),False)
  add('empty-map-'+n,lambda x,n=n:x['map_fields'].update({n:''}),False)
  add('invented-map-acceptance-'+n,lambda x,n=n:x['accepted_map_refs'].update({n:'hyp:accepted'}),False)
 for n in ['full_alignment_claimed','actual_outcome_claimed','source_role_collapsed']:add('forbidden-frame-'+n,lambda x,n=n:x.update({n:True}),False)
 add('discarded-upstream-findings',lambda x:x.update(upstream_findings_retained=False),False)
 add('silent-sibling-merge',lambda x:x.update(explicit_sibling_refs=[]),False)
 add('changed-resolution-owner-field',lambda x:x['after']['facets'].update(operationRegistry='hyp:changed'),False)
 return cases

def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.external_current(context);runtime=v.f.current_bindings();observation=consumer.inspect();ps=profiles();fs=frames();findings=observation['unresolved_consumer_findings'];assert len(findings)==4 and all(x['status']=='unresolved' and x['accepted_map_refs']==[] for x in findings) and observation['accepted_semantic_map_refs']==[] and observation['real_subject_type_result_or_authority_created'] is False and observation['raw_current_v2_helper_observation']['missing_key']=='entries'
 refs=[b.ref(b.UNIT/n) for n in ['verify_authority_profile.py','carrier-consumer-inspection.json','carrier-inspection-command-result.json','CONSUMER-REVIEW.md','types-logic-receipt.json']];b.unchanged(refs+list(observation['selected_inputs'].values()))
 report={'schema_version':'definition-assurance-Resolution-authority-profile/v1-candidate','status':'PASS-for-qualified-Resolution-hypotheses-and-exact-consumer-observations-with-four-unresolved-mappings','authority_effect':'none','source':context['source_selection'],'profiles':ps,'finite_comparison_frames':fs,'source_map_obligations':MAP_FIELDS,'accepted_source_to_carrier_or_consumer_map_refs':[],'cross_definition_review_findings':findings,'actual_checks':observation['checks'],'actual_check_count':observation['check_count'],'carrier_consumer_observation':observation,'selected_inputs':{str(i):x for i,x in enumerate(refs+list(observation['selected_inputs'].values()))},'checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.UNIT/'inspect_carrier_consumers.py'),b.ref(b.IMPL/'contracts.py')],'runtime_bindings':runtime,'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'isolated_pure_resolver_functions_executed':True,'actual_subject_type_result_or_admission_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified hypothetical maps and exact post-typed carrier observations only. Identity,registry-version,input domain,result lifecycle and product activation maps remain unaccepted.'}
 assert runtime==v.f.current_bindings();b.unchanged(context['sources']);b.external_current(context)
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'authority-profile-checks.json').read_bytes())):raise ValueError('Fresh qualified Resolution profile differs')
 return report
if __name__=='__main__':
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'finite_frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'actual_checks':x['actual_check_count'],'source_map_obligations':len(x['source_map_obligations']),'unresolved_consumer_findings':len(x['cross_definition_review_findings']),'accepted_maps':0,'semantic_ready':False},indent=2))
