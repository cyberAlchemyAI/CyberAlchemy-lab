"""Qualified Actor classification and attribution map hypotheses;no accepted maps or effects."""
import copy,json
import build_candidate as b
import inspect_carrier_consumers as consumer
import verifier as v
AXES=[n for fields,carrier in b.GROUPS for n in fields]+['governed_participant_identity_genus','inclusive_identity_or_record_criterion','abstract_without_concrete_use','no_universal_carrier_required','independently_governed_subject_coordinates','exact_Scheme_Assignment_value_coherence','separate_Actor_and_Scheme_scope','exact_use_subject_and_activity_attribution','versioned_subject_refs_with_four_coordinates_preserved','legitimate_kind_overlap_without_authority_inference','historical_review_vs_C65_current_admission','scope_and_independent_actual_outcomes']
FORBIDDEN=['Definition_is_concrete_Actor_instance','C65_admission_classifies_subject','schema_PASS_proves_attribution','universal_Actor_carrier_required','Actor_equals_Agent_Person_Principal_Team_Role','classification_creates_agency_personhood','classification_creates_ownership_permission_authority','classification_proves_successful_action','Scheme_label_authenticates_classification','Assignment_reference_authenticates_subject','independent_fixtures_are_exact_joined_instance','Scheme_scope_must_equal_Actor_scope','abstract_Actor_requires_activity','concrete_use_requires_attribution','attribution_merges_subject_identity','attribution_transfers_owner_or_lifecycle','attribution_grants_authority','equal_coordinates_prove_actual_preservation','historical_review_is_current_runtime_fact','same_sort_names_prove_shared_meaning','hypothetical_map_is_owner_acceptance','nonentailment_denies_independent_actual_outcomes']
def envelope():return {'source':b.source_ref(b.snapshot(),'cal.definition.actor'),'scope':b.SCOPE,'role':'candidate-exact-Actor-classification-attribution-declarations','authority_effect':'none','claim_scope':'necessary-declarations-only','facets':{n:'hyp:'+n for n in AXES},'actual_owner_review_ref':'','accepted_map_refs':[]}
def valid_profile(x):
 before=x['before'];after=x['after']
 return before==after and before==envelope() and not any(x['forbidden'].values()) and set(x['forbidden'])==set(FORBIDDEN) and x['source_role_preserved'] and x['declared_and_actual_classification_attribution_separate'] and x['eight_consumer_findings_retained'] and not x['semantic_acceptance_claimed'] and not x['actual_outcome_claimed']
def profiles():
 baseline={'before':envelope(),'after':envelope(),'forbidden':{n:False for n in FORBIDDEN},'source_role_preserved':True,'declared_and_actual_classification_attribution_separate':True,'eight_consumer_findings_retained':True,'semantic_acceptance_claimed':False,'actual_outcome_claimed':False};cases=[]
 def add(n,mutate,expected):
  x=copy.deepcopy(baseline);mutate(x);assert valid_profile(x)==expected,n;cases.append({'case_id':n,'profile':x,'expected_rejection':not expected,'qualified_hypothesis_satisfied':valid_profile(x),'accepted_semantic_map':False})
 add('exact-unaccepted-Actor-profile',lambda x:None,True)
 for n in FORBIDDEN:add('reject-'+n,lambda x,n=n:x['forbidden'].update({n:True}),False)
 for n in ['source_role_preserved','declared_and_actual_classification_attribution_separate','eight_consumer_findings_retained']:add('missing-'+n,lambda x,n=n:x.update({n:False}),False)
 for n in ['semantic_acceptance_claimed','actual_outcome_claimed']:add('unreviewed-'+n,lambda x,n=n:x.update({n:True}),False)
 for n in ['scope','role','authority_effect','claim_scope']:add('changed-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),False)
 return cases
MAP_FIELDS=AXES+['twenty_five_exact_meaning_bindings','C65_positive_admission_and_review_body_ceiling','historical_review_vs_current_Definition','eight_independent_carriers_to_concrete_Actor_use','exact_classification_fixture_join_and_attribution','owner_acceptance_and_claim_ceiling']
def valid_frame(x):
 return x['before']==x['after']==envelope() and x['selected'] is True and set(x['map_fields'])==set(MAP_FIELDS) and all(x['map_fields'].values()) and set(x['accepted_map_refs'])==set(MAP_FIELDS) and not any(x['accepted_map_refs'].values()) and x['owner_review_ref']=='' and x['full_alignment_claimed'] is False and x['actual_outcome_claimed'] is False and x['source_role_collapsed'] is False and x['upstream_findings_retained'] is True and x['explicit_sibling_refs']==['hyp:Actor-C65-abstract-own-meaning','hyp:Scheme-Assignment-Value-independent-meanings','hyp:Person-Reference-Principal-Team-independent-meanings','hyp:AgentInstance-ephemeral-own-meaning','hyp:IntegratedModel-review-no-activation']
def frames():
 baseline={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'upstream_findings_retained':True,'explicit_sibling_refs':['hyp:Actor-C65-abstract-own-meaning','hyp:Scheme-Assignment-Value-independent-meanings','hyp:Person-Reference-Principal-Team-independent-meanings','hyp:AgentInstance-ephemeral-own-meaning','hyp:IntegratedModel-review-no-activation']};cases=[]
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
 add('changed-subject-owner-coordinate',lambda x:x['after']['facets'].update(subjectOwner='hyp:changed'),False)
 return cases

def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.external_current(context);runtime=v.f.current_bindings();observation=consumer.inspect();ps=profiles();fs=frames();findings=observation['unresolved_consumer_findings'];assert len(findings)==8 and all(x['status']=='unresolved' and x['accepted_map_refs']==[] for x in findings) and observation['accepted_semantic_map_refs']==[] and observation['actual_Actor_classification_attribution_or_authority_created'] is False and observation['direct_current_definition_binding_types']==[] and len(observation['separately_bound_comparison_contracts'])==8 and observation['classification_fixture_join_observation']['exact_joined_instance_claimed'] is False and observation['typed_comparison_count']==16
 refs=[b.ref(b.UNIT/n) for n in ['verify_authority_profile.py','carrier-consumer-inspection.json','carrier-inspection-command-result.json','CONSUMER-REVIEW.md','types-logic-receipt.json']];b.unchanged(refs+list(observation['selected_inputs'].values()))
 report={'schema_version':'definition-assurance-Actor-authority-profile/v1-candidate','status':'PASS-for-qualified-Actor-hypotheses-and-exact-consumer-observations-with-eight-unresolved-mappings','authority_effect':'none','source':context['source_selection'],'profiles':ps,'finite_comparison_frames':fs,'source_map_obligations':MAP_FIELDS,'accepted_source_to_carrier_or_consumer_map_refs':[],'cross_definition_review_findings':findings,'actual_checks':observation['checks'],'actual_check_count':observation['check_count'],'carrier_consumer_observation':observation,'selected_inputs':{str(i):x for i,x in enumerate(refs+list(observation['selected_inputs'].values()))},'checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.UNIT/'inspect_carrier_consumers.py'),b.ref(b.IMPL/'contracts.py')],'runtime_bindings':runtime,'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'isolated_pure_Definition_helpers_executed':True,'actual_Actor_classification_attribution_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified hypothetical maps and exact post-typed carrier observations only. Actor/subject/Scheme/Assignment/value/activity,preservation,concrete-kind and C65/historical-review denotations remain unaccepted;no classification,attribution,authority,effect or whole proof.'}
 assert runtime==v.f.current_bindings();b.unchanged(context['sources']);b.external_current(context)
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'authority-profile-checks.json').read_bytes())):raise ValueError('Fresh qualified Actor profile differs')
 return report
if __name__=='__main__':
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'finite_frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'actual_checks':x['actual_check_count'],'source_map_obligations':len(x['source_map_obligations']),'unresolved_consumer_findings':len(x['cross_definition_review_findings']),'accepted_maps':0,'semantic_ready':False},indent=2))
