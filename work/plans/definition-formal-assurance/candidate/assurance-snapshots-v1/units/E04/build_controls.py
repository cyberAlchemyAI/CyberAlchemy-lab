"""Declare a closed, source-bound denominator of actual hostile fixture methods."""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
UNIT=Path(__file__).resolve().parent
TESTS=ROOT/'craft/formalization/candidates/definition-assurance-v1/tests'
# category | module | class | method suffix | expected literal assertions
SELECTION='''
schema|A01|InputControls|all_seven_kinds_are_structural_only|structurally-valid,not-assessed
schema|A01|InputControls|duplicate_json_keys_nested_and_unicode_escaped|duplicate-json-key
schema|A01|InputControls|wrong_types_boolean_is_not_integer_and_no_defaults|
schema|A01|InputControls|nonfinite_and_overflow_numbers_are_typed_malformed|nonfinite-number
schema|A01|InputControls|utf8_surrogates_wrong_transport_and_invalid_json|utf8-bytes-required
schema|A01|InputControls|explicit_resource_limits_precede_schema_validation|byte-limit,depth-limit,node-limit
schema|A01|InputControls|submitter_cannot_declare_derived_readiness_or_authority_effect|
schema|A01|InputControls|scope_paths_and_version_identity_are_checked_without_source_io|
types|C01|TypeControls|valid_closed_formula_and_preserved_origin_namespace|not-assessed
types|C01|TypeControls|equal_labels_different_source_version_scope_have_distinct_symbols|
types|C01|TypeControls|unbound_variable_and_predicate_arity_rejected|unbound-variable,predicate-arity
types|C01|TypeControls|ill_sorted_predicate_and_equality_rejected|predicate-argument-sort,unaligned-equality-sorts
types|C01|TypeControls|partial_function_and_extension_features_are_unsupported|
types|C01|TypeControls|nominal_sort_separation_not_proof_of_semantic_difference|duplicate-interpretation-namespace
types|C01|TypeControls|explicit_shared_carrier_alignment_enables_cross_predicate_query|predicate-argument-sort,stale-carrier-alignment
types|C01|TypeControls|rehashed_composition_cannot_substitute_independent_inputs|composed-IR-input-or-alignment-substitution
relations|A05|RelationControls|alias_no_forced_distinction_and_false_alias_countermodel|model-local-supported,model-local-counterexample
relations|A05|RelationControls|subtype_direction_and_selected_properness|model-local-supported,model-local-counterexample
relations|A05|RelationControls|overlap_and_both_directed_differences|model-local-supported,model-local-counterexample
relations|A05|RelationControls|distinction_witness_not_all_model_proof|model-witness,universal-property
relations|A05|RelationControls|empty_required_population_precedes_vacuous_alias_success|vacuous-required-population,missing-population-policy
relations|A05|RelationControls|population_target_not_weakened_or_replaced|population-statement-substitution
relations|A05|RelationControls|exemption_requires_review_and_stays_pending|unreviewable-population-exemption,exemption-review-required
relations|A05|RelationControls|unaligned_label_and_stale_alignment_rejected|unresolved-carrier-alignment,stale-alignment-binding
relations|A05|RelationControls|endpoint_source_scope_and_unknown_marker_rejected|endpoint-source-scope-mismatch,malformed-endpoint-binding
relations|A05|RelationControls|forbidden_inference_targets_are_named_and_directional|explicit-forbidden-inferences-required
relations|A05|RelationControls|empty_target_list_never_reports_model_support|empty-control-denominator
search|P02|FiniteControls|first_witness_streams_a_complete_interpretation|witness-found,PASS
search|P02|FiniteControls|required_populations_must_coexist_under_one_interpretation|bounded-no-admissible-model,bounded-supported
search|P02|FiniteControls|interpretation_budget_exhaustion_is_unknown_not_absence|resource-limit
search|P02|FiniteControls|global_evaluation_budget_does_not_reset_per_model|evaluation-step-limit
search|P02|FiniteControls|cancellation_before_search_and_during_quantification|cancelled
search|P02|FiniteControls|deadline_checked_before_enumeration|timeout
search|P02|FiniteControls|output_limit_has_no_model_or_absence_evidence|resource-limit
search|P02|FiniteControls|capped_radix_never_marks_a_prefix_as_full_exhaustion|resource-limit
search|P02|FiniteControls|provider_errors_do_not_receive_a_truth_value|provider-error
witness|E03|DenotationControls|actual_provider_witness_checked_by_separate_evaluator|checked-model-witness
witness|E03|DenotationControls|rehashed_false_witness_rejected|witness-fails-query
witness|E03|DenotationControls|substituted_query_and_provider_rejected|witness-input-substitution,provider-build-substitution
witness|E03|DenotationControls|boolean_cardinality_and_claim_promotion_rejected|invalid-witness-cardinalities,invalid-witness-claim-boundary
witness|E03|DenotationControls|native_policy_and_missing_null_context_binding_rejected|native-policy-substitution
witness|E03|DenotationControls|duplicate_or_ill_sorted_extension_has_no_truth|duplicate-predicate-tuple,ill-sorted-model-tuple
witness|E03|DenotationControls|model_incomplete_empty_domain_or_extra_predicate_rejected|model-signature-denominator-mismatch,empty-or-malformed-domain
witness|E03|DenotationControls|population_and_theory_failure_are_distinct|witness-fails-theory,witness-fails-population
witness|E03|DenotationControls|cancellation_and_step_limit_no_truth|cancelled,verifier-step-limit
witness|E03|DenotationControls|verifier_deadline_has_no_truth_outcome|verifier-timeout
witness|E03|DenotationControls|bounded_exhaustion_is_not_accepted_as_model_or_theorem|no-checkable-model-witness
witness|E03|DenotationControls|boolean_truth_rank_and_mode_substitution_rejected|invalid-witness-rank,witness-mode-substitution
denominator|E03|SelectionControls|complete_missing_package_regenerated_independently_stays_pending|verified-candidate-accounting
denominator|E03|SelectionControls|removed_required_statement_rejected_not_inferred_from_result_list|publication-unresolved
denominator|E03|SelectionControls|independently_selected_relation_changes_denominator|published-contract-accounting-invalid
denominator|E03|SelectionControls|dependency_or_assumption_artifact_substitution_rejected|independent-artifact-substitution
denominator|E03|SelectionControls|same_byte_bound_nominal_mapping_cannot_attribute_Q_to_source_A|nominal-source-or-identity-substitution
denominator|E03|SelectionControls|selected_input_mutation_during_check_is_rejected|independent-input-changed-during-verification
denominator|E03|SelectionControls|pending_gate_support_is_not_independently_verified|reported-supported
denominator|E03|SelectionControls|unknown_selection_fields_and_non_json_inputs_have_no_escape|malformed-independent-selection
publication|E02|PublicationControls|actual_publish_and_closed_capture_inspection|published-candidate,PASS
publication|E02|PublicationControls|empty_directory_created_at_final_race_is_not_overwritten|publication-collision
publication|E02|PublicationControls|target_symlink_does_not_replace_or_modify_its_referent|publication-collision
publication|E02|PublicationControls|interruption_keeps_private_attempt_and_previous_success|publication-unresolved
publication|E02|PublicationControls|source_change_before_installation_keeps_attempt_without_publication|artifact-changed-before-publication
publication|E02|PublicationControls|registry_change_is_detected_by_final_full_snapshot_check|stale-captured-source
publication|E02|PublicationControls|unsupported_atomic_operation_has_no_unsafe_rename_fallback|atomic-no-replace-unavailable
publication|E02|PublicationControls|post_installation_source_race_is_retained_but_not_reported_current|published-currentness-unconfirmed
publication|E02|PublicationControls|historical_capture_survives_later_live_source_change|historical-capture-only
records|A09|ReplayTests|right_and_duty_overlap_preserves_tags|
records|A09|ReplayTests|ungranted_claim_and_unclaimed_grant|unknown
records|A09|ReplayTests|silent_status_unrelated_subject_and_hash_mismatch_fail_frame|
records|A09|ReplayTests|substituted_model_rank_is_rejected|native-witness-rank-or-byte-substitution
records|A09|ReplayTests|witness_cannot_satisfy_a_different_query|native-witness-fails-independent-query
records|A09|ReplayTests|native_omitted_query_and_forged_strength_fail|native-required-denominator-substitution,native-witness-strength-substitution
records|A09|ReplayTests|injected_wrong_predicate_and_wrong_enumerator_fail|record-or-logical-denotation-disagreement,configuration-enumeration-disagreement
records|A09|ReplayTests|missing_whole_translation_and_dependency_closure_are_explicit|missing-whole-definition-translation,missing-semantic-dependency-closure
records|A09|ReplayTests|output_limit_is_bounded_and_preserves_selected_query_ids|resource-limit
records|A09|ReplayTests|merge_rejects_gap_overlap_missing_tail_and_incomplete|range-gap-overlap-or-outside-scope,range-cover-incomplete
records|A09|ReplayTests|merge_rejects_different_runtime_policy_and_query_denominator|mixed-range-input-epochs,range-query-denominator-substitution
'''

def digest(raw):return hashlib.sha256(raw).hexdigest()
def build():
 context=json.loads((UNIT/'context.json').read_bytes())
 for row in context['sources']:assert digest((ROOT/row['path']).read_bytes())==row['sha256'],row['path']
 cases=[]
 for line in SELECTION.strip().splitlines():
  category,module,cls,suffix,tokens=line.split('|');path=TESTS/f'test_{module}.py';raw=path.read_bytes();text=raw.decode();tree=ast.parse(text);c=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==cls);method='test_'+suffix;n=next(n for n in c.body if isinstance(n,ast.FunctionDef) and n.name==method);excerpt=ast.get_source_segment(text,n);checks=tokens.split(',') if tokens else [];literals={x.value for x in ast.walk(n) if isinstance(x,ast.Constant) and isinstance(x.value,str)};assert set(checks)<=literals,(suffix,checks)
  cases.append({'case_id':f'E04-{len(cases)+1:03d}','category':category,'module':f'test_{module}','class':cls,'method':method,'source_ref':{'path':path.relative_to(ROOT).as_posix(),'sha256':digest(raw)},'method_sha256':digest(excerpt.encode()),'source_line':n.lineno,'named_cause':suffix.replace('_',' '),'expected_literal_checks':checks,'fixture_assertion_contract':excerpt,'mutation_boundary':'Synthetic in-memory value / private temporary fixture or isolated copied candidate; source code and canonical inputs preserved.','expected_test_outcome':'pass-with-no-skips-errors-or-unexpected-success'})
 value={'schema_version':'definition-assurance-hostile-controls/v1-candidate','authority_effect':'none','semantic_ready':False,'unit':'E04.1','categories':sorted({r['category'] for r in cases}),'cases':cases,'declared_case_count':len(cases),'preserved_delivery_manifest_ref':{'path':(UNIT.parent/'A10/delivery-manifest.json').relative_to(ROOT).as_posix(),'sha256':digest((UNIT.parent/'A10/delivery-manifest.json').read_bytes())},'claim_ceiling':'Actual selected fixture assertions only. No universal malformed-input proof, exhaustive adversary model, owner fidelity, admission or unbounded theorem.','fixture_reuse':'Source-bound existing adversarial fixtures are deliberately reused; E04 adds an explicit cross-layer denominator and executes every declared member.','goal_status':'active'}
 out=TESTS/'hostile-cases.json'
 with out.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
 print(json.dumps({'declared_cases':len(cases),'categories':value['categories']}))
if __name__=='__main__':build()
