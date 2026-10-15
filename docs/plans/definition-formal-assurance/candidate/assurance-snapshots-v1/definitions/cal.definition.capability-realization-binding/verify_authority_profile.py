"""Qualified correspondence hypotheses; no accepted owner maps or instance effects."""
import copy, json
import build_candidate as b
import inspect_carrier_consumers as consumer
import verifier as v

AXES=[n for fields,carrier in b.GROUPS for n in fields]+['one_exact_Capability_revision','one_or_more_exact_Implementation_members','broader_realization_kind_Implementation_maps','distinct_posture_and_lifecycle','exactly_one_canonical_association_authority','optional_at_most_one_projection','readonly_projection_not_second_writer','exact_selected_digest_binding','four_evidence_purposes_common_carrier','extensional_member_change_not_handle_change','independent_intended_state','required_distinct_matching_successor','C60_C66_C70_separate_positive_scopes','identical_shape_different_primary_meanings','independent_finite_T_and_I']
FORBIDDEN=['Definition_admission_accepts_translation','type_admission_adopts_Binding','workflow_kind_resolves_exact_Implementation','nonempty_collection_handle_supplies_members','duplicate_array_proves_distinct_members','raw_ID_noncollapse_accepts_common_identity_map','binding_state_is_posture_and_lifecycle_without_maps','opaque_adoption_decision_performs_adoption','conformance_refs_prove_deployment','owner_ref_grants_permission','general_scope_proves_deployment_applicability','policy_lists_prove_compatibility','schema_shape_supplies_canonical_authority','two_canonical_authorities_allowed','human_RECORD_view_is_TypedRelation_projection','projection_is_second_writable_authority','nominated_digest_equality_proves_authenticity','all_Bindings_require_projection','four_evidence_roles_require_disjoint_content','observation_refs_prove_Product_value','successor_string_proves_distinct_revision','self_successor_discharge_changed_state','endpoint_change_keeps_same_revision','collection_handle_change_is_endpoint_change','no_change_forbids_all_other_succession','all_succession_has_unique_global_successor','finite_separate_models_are_joint_whole_proof','nonentailment_denies_independent_authorized_outcomes']
MAP_FIELDS=AXES+['twenty_eight_exact_meanings','historical_ProductCapability_current_CRB_meaning','C60_zero_instances_C70_exact_GovernedModel_exclusion','realization_kind_and_revision_resolution','canonical_authority_and_projection_denotations','evidence_purpose_and_actual_claim_scope','authenticated_before_desired_successor_history','owner_fidelity_and_claim_ceiling']
SIBLINGS=['hyp:C60-one-type-no-instance','hyp:C66-exact-CRB-meaning','hyp:C70-current-v2-type','hyp:C70-only-integrated-GovernedModel-ordinary-instance','hyp:current-expression-subset-not-whole-package']


def envelope():
    return {'source': b.source_ref(b.snapshot(), 'cal.definition.capability-realization-binding'),
            'scope': b.SCOPE, 'role': 'candidate-exact-CRB-association-endpoint-evidence-projection-succession-declarations',
            'authority_effect': 'none', 'claim_scope': 'necessary-declarations-and-proposed-correspondence-only',
            'facets': {n: 'hyp:'+n for n in AXES}, 'actual_owner_review_ref': '', 'accepted_map_refs': []}


def valid_profile(x):
    return (x['before'] == x['after'] == envelope() and set(x['forbidden']) == set(FORBIDDEN)
            and not any(x['forbidden'].values()) and x['source_role_preserved']
            and x['declared_actual_and_carrier_meanings_separate'] and x['thirteen_consumer_findings_retained']
            and not x['semantic_acceptance_claimed'] and not x['actual_outcome_claimed'])


def profiles():
    baseline = {'before': envelope(), 'after': envelope(), 'forbidden': {n: False for n in FORBIDDEN},
                'source_role_preserved': True, 'declared_actual_and_carrier_meanings_separate': True,
                'thirteen_consumer_findings_retained': True, 'semantic_acceptance_claimed': False,
                'actual_outcome_claimed': False}
    cases = []

    def add(name, mutate, expected):
        x = copy.deepcopy(baseline)
        mutate(x)
        assert valid_profile(x) == expected, name
        cases.append({'case_id': name, 'profile': x, 'expected_rejection': not expected,
                      'qualified_hypothesis_satisfied': valid_profile(x), 'accepted_semantic_map': False})

    add('exact-unaccepted-CRB-profile', lambda x: None, True)
    for n in FORBIDDEN:
        add('reject-'+n, lambda x, n=n: x['forbidden'].update({n: True}), False)
    for n in ['source_role_preserved', 'declared_actual_and_carrier_meanings_separate', 'thirteen_consumer_findings_retained']:
        add('missing-'+n, lambda x, n=n: x.update({n: False}), False)
    for n in ['semantic_acceptance_claimed', 'actual_outcome_claimed']:
        add('unreviewed-'+n, lambda x, n=n: x.update({n: True}), False)
    for n in ['scope', 'role', 'authority_effect', 'claim_scope']:
        add('changed-'+n, lambda x, n=n: x['after'].update({n: 'hyp:changed'}), False)
    return cases


def valid_frame(x):
    return (x['before'] == x['after'] == envelope() and x['selected'] is True
            and set(x['map_fields']) == set(MAP_FIELDS) and all(x['map_fields'].values())
            and set(x['accepted_map_refs']) == set(MAP_FIELDS) and not any(x['accepted_map_refs'].values())
            and x['owner_review_ref'] == '' and x['full_alignment_claimed'] is False
            and x['actual_outcome_claimed'] is False and x['source_role_collapsed'] is False
            and x['upstream_findings_retained'] is True and x['explicit_sibling_refs'] == SIBLINGS)


def frames():
    baseline = {'before': envelope(), 'after': envelope(), 'selected': True,
                'map_fields': {n: 'proposed-map-or-explicit-residue' for n in MAP_FIELDS},
                'accepted_map_refs': {n: '' for n in MAP_FIELDS}, 'owner_review_ref': '',
                'full_alignment_claimed': False, 'actual_outcome_claimed': False,
                'source_role_collapsed': False, 'upstream_findings_retained': True,
                'explicit_sibling_refs': SIBLINGS}
    cases = []

    def add(name, mutate, expected):
        x = copy.deepcopy(baseline)
        mutate(x)
        assert valid_frame(x) == expected, name
        cases.append({'case_id': name, 'frame': x, 'expected_rejection': not expected,
                      'qualified_unaccepted_frame_satisfied': valid_frame(x)})

    add('complete-pending-CRB-source-map', lambda x: None, True)
    for n in MAP_FIELDS:
        add('missing-map-'+n, lambda x, n=n: x['map_fields'].pop(n), False)
        add('empty-map-'+n, lambda x, n=n: x['map_fields'].update({n: ''}), False)
        add('invented-map-acceptance-'+n, lambda x, n=n: x['accepted_map_refs'].update({n: 'hyp:accepted'}), False)
    for n in ['full_alignment_claimed', 'actual_outcome_claimed', 'source_role_collapsed']:
        add('forbidden-frame-'+n, lambda x, n=n: x.update({n: True}), False)
    add('discarded-upstream-findings', lambda x: x.update(upstream_findings_retained=False), False)
    add('silent-sibling-merge', lambda x: x.update(explicit_sibling_refs=[]), False)
    add('changed-owner-coordinate', lambda x: x['after']['facets'].update(bindingOwner='hyp:changed'), False)
    return cases


def verify(write=False):
    context = consumer.load(b.UNIT/'context.json')
    b.unchanged(context['sources'])
    b.external_current(context)
    runtime = v.f.current_bindings()
    observation = consumer.inspect()
    terminal = consumer.load(b.UNIT/'carrier-inspection-command-result.json')
    assert terminal['exit_code'] == 0 and not (b.UNIT/terminal['stderr']).read_bytes()
    ps, fs = profiles(), frames()
    findings = observation['unresolved_consumer_findings']
    assert len(findings) == 13 and all(x['status'] == 'unresolved' and not x['accepted_map_refs'] for x in findings)
    assert not observation['accepted_semantic_map_refs'] and not observation['actual_Binding_adoption_deployment_conformance_operation_value_or_authority_created']
    assert observation['source_coordinate_account_complete'] is True and observation['accepted_semantic_correspondence_complete'] is False
    assert observation['check_count'] == 400 and len(observation['meaning_observations']) == 28
    assert observation['carrier_shape_probe_count'] == 71 and observation['typed_comparison_count'] == 42
    assert observation['isolated_primitive_comparison_count'] == 23
    refs = [b.ref(b.UNIT/n) for n in ['verify_authority_profile.py', 'carrier-consumer-inspection.json',
                                   'carrier-inspection-command-result.json', 'CONSUMER-REVIEW.md', 'types-logic-receipt.json']]
    retained = []
    b.unchanged(refs + list(observation['selected_inputs'].values()) + retained)
    report = {
        'schema_version': 'definition-assurance-CapabilityRealizationBinding-authority-profile/v1-candidate',
        'status': 'PASS-for-qualified-CRB-hypotheses-and-exact-consumer-comparisons',
        'authority_effect': 'none', 'source': context['source_selection'], 'profiles': ps,
        'finite_comparison_frames': fs, 'source_map_obligations': MAP_FIELDS,
        'accepted_source_to_carrier_or_consumer_map_refs': [], 'cross_definition_review_findings': findings,
        'actual_checks': observation['checks'], 'actual_check_count': observation['check_count'],
        'carrier_consumer_observation': observation,
        'selected_inputs': {str(i): x for i, x in enumerate(refs + list(observation['selected_inputs'].values()) + retained)},
        'checker_bindings': [b.ref(b.UNIT/'verify_authority_profile.py'), b.ref(b.UNIT/'inspect_carrier_consumers.py'), b.ref(b.IMPL/'contracts.py')],
        'runtime_bindings': runtime, 'bound_package_validator_executed': False,
        'canonical_or_candidate_carrier_writer_executed': False, 'native_or_live_consumer_executed': False,
        'current_expression_is_whole_package': False, 'actual_instance_effects_created': False,
        'direct_carrier_or_consumer_alignment_accepted': False,
        'retained_failed_consumer_comparison_refs': retained, 'new_authorities_or_relations_created': 0,
        'source_fidelity': 'pending', 'semantic_ready': False, 'mechanized_proof': False,
        'claim_ceiling': 'Finite qualified CRB correspondence hypotheses and exact observations only. Proposed maps and explicit residue do not establish owner acceptance, actual adoption/deployment/conformance/operation/value/authority, fidelity or whole proof.'}
    assert runtime == v.f.current_bindings()
    b.unchanged(context['sources'])
    b.external_current(context)
    if write:
        b.put('authority-profile-checks.json', report)
    else:
        assert b.r.same_json(report, consumer.load(b.UNIT/'authority-profile-checks.json')), 'Fresh CI profiles differ'
    return report


if __name__ == '__main__':
    result = verify('--write' in b.sys.argv)
    print(json.dumps({'result': result['status'], 'profiles': len(result['profiles']),
                      'rejected_profiles': sum(x['expected_rejection'] for x in result['profiles']),
                      'finite_frames': len(result['finite_comparison_frames']),
                      'rejected_frames': sum(x['expected_rejection'] for x in result['finite_comparison_frames']),
                      'actual_checks': result['actual_check_count'],
                      'source_map_obligations': len(result['source_map_obligations']),
                      'unresolved_consumer_findings': len(result['cross_definition_review_findings']),
                      'accepted_maps': 0, 'semantic_ready': False}, indent=2))
