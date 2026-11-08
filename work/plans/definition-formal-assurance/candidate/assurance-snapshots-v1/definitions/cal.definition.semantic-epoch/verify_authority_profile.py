"""Qualified SemanticEpoch correspondence hypotheses; no accepted maps or authority effects."""
import copy,json
import build_candidate as b
import inspect_carrier_consumers as consumer
import verifier as v
AXES=[n for fields,carrier in b.GROUPS for n in fields]+['epoch_genus_and_immutability','owner_selection_reference_vs_execution','material_meaning_and_five_coordinate_maps','short_iff_and_owner_criterion_precedence','identity_preservation_and_epoch_label_aliases','inclusive_material_dimensions','raw_reference_changes_vs_materiality','representation_bytes_and_nonsemantic_classes','predecessor_delta_and_lineage_fidelity','contested_preservation_and_reviewable_evidence','conditional_successor_and_evidence_records','scope_and_independent_authority']
FORBIDDEN=['Definition_is_epoch_instance','Definition_admission_accepts_translation','Definition_schema_PASS_proves_successor','ContextLineage_shape_selects_epoch','BoundedContext_version_proves_material_change','IdentityLineage_and_epoch_alias','candidate_epoch_and_SemanticEpoch_alias','opaque_owner_ref_authenticates_selection','raw_reference_difference_proves_materiality','byte_change_proves_new_epoch','representation_change_proves_material_change','preservation_claim_proves_equivalence','immutable_flag_proves_storage','lineage_reference_creates_lineage','parent_meaning_grants_authority','unused_successor_fields_always_required','global_epoch_label_injectivity_invented','all_semantic_dimension_changes_required','source_body_posture_overwrites_C28','same_sort_names_prove_shared_meaning','hypothetical_map_is_owner_acceptance','nonentailment_denies_independent_actual_outcomes']
def envelope():return {'source':b.source_ref(b.snapshot(),'cal.definition.semantic-epoch'),'scope':b.SCOPE,'role':'candidate-exact-semantic-epoch-declarations','authority_effect':'none','claim_scope':'necessary-declarations-only','facets':{n:'hyp:'+n for n in AXES},'actual_owner_review_ref':'','accepted_map_refs':[]}
def valid_profile(x):
 before=x['before'];after=x['after']
 return before==after and before==envelope() and not any(x['forbidden'].values()) and set(x['forbidden'])==set(FORBIDDEN) and x['source_role_preserved'] and x['declared_and_actual_epoch_selection_separate'] and x['eight_consumer_findings_retained'] and not x['semantic_acceptance_claimed'] and not x['actual_outcome_claimed']
def profiles():
 baseline={'before':envelope(),'after':envelope(),'forbidden':{n:False for n in FORBIDDEN},'source_role_preserved':True,'declared_and_actual_epoch_selection_separate':True,'eight_consumer_findings_retained':True,'semantic_acceptance_claimed':False,'actual_outcome_claimed':False};cases=[]
 def add(n,mutate,expected):
  x=copy.deepcopy(baseline);mutate(x);assert valid_profile(x)==expected,n;cases.append({'case_id':n,'profile':x,'expected_rejection':not expected,'qualified_hypothesis_satisfied':valid_profile(x),'accepted_semantic_map':False})
 add('exact-unaccepted-semantic-epoch-profile',lambda x:None,True)
 for n in FORBIDDEN:add('reject-'+n,lambda x,n=n:x['forbidden'].update({n:True}),False)
 for n in ['source_role_preserved','declared_and_actual_epoch_selection_separate','eight_consumer_findings_retained']:add('missing-'+n,lambda x,n=n:x.update({n:False}),False)
 for n in ['semantic_acceptance_claimed','actual_outcome_claimed']:add('unreviewed-'+n,lambda x,n=n:x.update({n:True}),False)
 for n in ['scope','role','authority_effect','claim_scope']:add('changed-'+n,lambda x,n=n:x['after'].update({n:'hyp:changed'}),False)
 return cases
MAP_FIELDS=AXES+['twenty_exact_meaning_bindings','C28_admission_and_body_ceiling','four_separate_current_contract_roles','three_directory_labels_and_two_candidate_lineages','historical_candidate_epoch_vs_SemanticEpoch','owner_acceptance_and_claim_ceiling']
def valid_frame(x):
 return x['before']==x['after']==envelope() and x['selected'] is True and set(x['map_fields'])==set(MAP_FIELDS) and all(x['map_fields'].values()) and set(x['accepted_map_refs'])==set(MAP_FIELDS) and not any(x['accepted_map_refs'].values()) and x['owner_review_ref']=='' and x['full_alignment_claimed'] is False and x['actual_outcome_claimed'] is False and x['source_role_collapsed'] is False and x['upstream_findings_retained'] is True and x['explicit_sibling_refs']==['hyp:SemanticEpoch-C28-own-meaning','hyp:ContextLineage-C70-own-meaning','hyp:BoundedContext-C70-Definition2-own-meaning','hyp:IdentityLineage-C30-own-meaning','hyp:Context-C70-own-meaning']
def frames():
 baseline={'before':envelope(),'after':envelope(),'selected':True,'map_fields':{n:'proposed-map-or-explicit-residue' for n in MAP_FIELDS},'accepted_map_refs':{n:'' for n in MAP_FIELDS},'owner_review_ref':'','full_alignment_claimed':False,'actual_outcome_claimed':False,'source_role_collapsed':False,'upstream_findings_retained':True,'explicit_sibling_refs':['hyp:SemanticEpoch-C28-own-meaning','hyp:ContextLineage-C70-own-meaning','hyp:BoundedContext-C70-Definition2-own-meaning','hyp:IdentityLineage-C30-own-meaning','hyp:Context-C70-own-meaning']};cases=[]
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
 add('changed-selection-owner-field',lambda x:x['after']['facets'].update(selectionOwner='hyp:changed'),False)
 return cases

def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.external_current(context);runtime=v.f.current_bindings();observation=consumer.inspect();ps=profiles();fs=frames();findings=observation['unresolved_consumer_findings'];assert len(findings)==8 and all(x['status']=='unresolved' and x['accepted_map_refs']==[] for x in findings) and observation['accepted_semantic_map_refs']==[] and observation['actual_semantic_epoch_owner_selection_materiality_lineage_or_authority_created'] is False and observation['direct_current_definition_binding_types']==[] and len(observation['separately_bound_comparison_contracts'])==4
 refs=[b.ref(b.UNIT/n) for n in ['verify_authority_profile.py','carrier-consumer-inspection.json','carrier-inspection-command-result.json','CONSUMER-REVIEW.md','types-logic-receipt.json']];b.unchanged(refs+list(observation['selected_inputs'].values()))
 report={'schema_version':'definition-assurance-SemanticEpoch-authority-profile/v1-candidate','status':'PASS-for-qualified-SemanticEpoch-hypotheses-and-exact-consumer-observations-with-eight-unresolved-mappings','authority_effect':'none','source':context['source_selection'],'profiles':ps,'finite_comparison_frames':fs,'source_map_obligations':MAP_FIELDS,'accepted_source_to_carrier_or_consumer_map_refs':[],'cross_definition_review_findings':findings,'actual_checks':observation['checks'],'actual_check_count':observation['check_count'],'carrier_consumer_observation':observation,'selected_inputs':{str(i):x for i,x in enumerate(refs+list(observation['selected_inputs'].values()))},'checker_bindings':[b.ref(b.UNIT/'verify_authority_profile.py'),b.ref(b.UNIT/'inspect_carrier_consumers.py'),b.ref(b.IMPL/'contracts.py')],'runtime_bindings':runtime,'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'isolated_pure_Definition_helpers_executed':True,'actual_semantic_epoch_owner_selection_materiality_lineage_or_authority_created':False,'direct_carrier_or_consumer_alignment_accepted':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Qualified hypothetical maps and exact post-typed carrier observations only. Exact epoch/artifact/assessment/reference denotations,material meaning and owner judgment,predecessor/delta/selection/lineage,representation/preservation boundaries,four separate current contract meanings,two candidate context-lineage examples and independent authority remain unaccepted.'}
 assert runtime==v.f.current_bindings();b.unchanged(context['sources']);b.external_current(context)
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'authority-profile-checks.json').read_bytes())):raise ValueError('Fresh qualified SemanticEpoch profile differs')
 return report
if __name__=='__main__':
 x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'profiles':len(x['profiles']),'rejected_profiles':sum(y['expected_rejection'] for y in x['profiles']),'finite_frames':len(x['finite_comparison_frames']),'rejected_frames':sum(y['expected_rejection'] for y in x['finite_comparison_frames']),'actual_checks':x['actual_check_count'],'source_map_obligations':len(x['source_map_obligations']),'unresolved_consumer_findings':len(x['cross_definition_review_findings']),'accepted_maps':0,'semantic_ready':False},indent=2))
