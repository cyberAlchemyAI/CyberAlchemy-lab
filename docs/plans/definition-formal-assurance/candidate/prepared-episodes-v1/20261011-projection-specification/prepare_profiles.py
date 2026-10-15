"""Prepare qualified PS maps and fresh94-draft inventory checks."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.projection-specification');prev=u.with_name('cal.definition.generated-output')
s=(prev/'verify_authority_profile.py').read_text().replace('GeneratedOutput','ProjectionSpecification').replace('cal.definition.generated-output','cal.definition.projection-specification')
i=s.index('AXES=');j=s.index('\ndef envelope',i)
s=s[:i]+'''AXES=list(b.MEANING_FIELDS)+list(b.CONCEPT_FIELDS)+list(b.VIEW_FIELDS)+['D44_ViewBearing_normalized_identity_role','five_condition_precedence_map','declared_vs_actual_threshold','nominated_and_additional_view_universe','explicit_empty_sets_vs_missing_fields','preservation_inclusive_OR','fallback_term_candidate_local_overlap','current_ContextView_separate_contract','current_OntologyView_separate_contract','actual_inspectability_and_usability','actual_scope_and_consumer_selection','external_source_relation_authenticity']
FORBIDDEN=['Definition_is_view_instance','Definition_admission_accepts_translation','Definition_schema_PASS_proves_threshold','ContextView_schema_PASS_proves_D44','OntologyView_schema_PASS_proves_D44','two_view_contracts_alias_PS','opaque_owner_ref_is_live_route','hash_pattern_is_computed_digest','view_label_proves_load_bearing','five_flags_prove_actual_threshold','empty_explicit_set_is_absent_field','missing_required_fields_are_complete','all_six_preservation_roles_required','every_term_requires_new_tree','view_fields_grant_authority','canonical_meaning_grants_instance_authority','schema_record_admitted_is_actual_admission','nondate_freshness_proves_currentness','current_type_admission_accepts_field_map','same_sort_names_prove_shared_meaning','hypothetical_map_is_owner_acceptance','nonentailment_denies_independent_actual_outcomes']'''+s[j:]
s=s.replace('candidate-exact-output-generation-conditional-canonicalness','candidate-exact-view-bearing-concept-declarations').replace('declared_and_actual_generation_routes_separate','declared_and_actual_view_routes_separate').replace('exact-unaccepted-generated-output-profile','exact-unaccepted-projection-specification-profile')
i=s.index('MAP_FIELDS=');j=s.index('\ndef valid_frame',i)
s=s[:i]+"MAP_FIELDS=AXES+['eight_exact_meaning_bindings','C53_overlay_D44_and_scaffold_metadata','two_separate_view_contract_role_correspondences','View_payload_to_threshold_readings_moves','view_tree_universe_completeness','actual_preservation_checks_effect_authorization','owner_acceptance_and_claim_ceiling']"+s[j:]
s=s.replace("['hyp:GO-C65-definition-C74A-carrier','hyp:Registry-C68-generated-view-role','hyp:OntologyPackage-C70-output-role']","['hyp:PS-C53-D44-normalized-role','hyp:ContextView-C70-own-meaning','hyp:OntologyView-C70-own-meaning']")
s=s.replace('changed-output-owner-field','changed-concept-owner-field').replace('outputOwner','conceptOwnerRoute')
s=s.replace("observation['real_generator_execution_contract_or_authority_created']","observation['real_view_helpfulness_preservation_or_authority_created']").replace("len(observation['direct_current_definition_binding_types'])==3","observation['direct_current_definition_binding_types']==[] and len(observation['separately_bound_comparison_contracts'])==2")
s=s.replace('actual_generator_execution_canonical_contract_or_authority_created','actual_view_helpfulness_preservation_or_authority_created')
s=s.replace('Exact input/generator/run/lineage/parity,conditional canonical contract,three current carrier roles,current consumers and independent authority maps remain unaccepted.','Exact D44/normalized role, five-condition precedence, explicit field/set denotations, view universe, preservation disjunction, two separate view contracts, current consumers and independent authority maps remain unaccepted.')
ast.parse(s)
with (u/'verify_authority_profile.py').open('x') as f:f.write(s)
for n in ['static_snapshot_reuse.py','verify_static_snapshot_reuse.py','verify_dependencies.py','replay.py']:
 s=(prev/n).read_text().replace('cal.definition.four-facet-artifact-invariant/','cal.definition.generated-output/');ast.parse(s)
 with (u/n).open('x') as f:f.write(s)
s=(prev/'verify_current_inventory.py').read_text().replace('ninety-three','ninety-four').replace('Ninety-three','Ninety-four').replace('!=93','!=94').replace('cal.definition.four-facet-artifact-invariant/','cal.definition.generated-output/').replace("'F04-T.cal.definition.projection-specification'","'F04-T.cal.definition.representation-revision'");ast.parse(s)
with (u/'verify_current_inventory.py').open('x') as f:f.write(s)
s=(p.with_name('20261011-generated-output')/'capture_delivery_checks.py').read_text().replace('cal.definition.generated-output','cal.definition.projection-specification')
with (p/'capture_delivery_checks.py').open('x') as f:f.write(s)
print('Prepared qualified PS maps and94-draft checks.')
