"""Qualified correspondence hypotheses; no accepted owner maps or instance effects."""
import copy, json
import build_candidate as b
import inspect_carrier_consumers as consumer
import verifier as v

AXES = [n for fields, carrier in b.GROUPS for n in fields] + [
    'sixteen_source_coordinates_plus_owner_companion', 'realization_or_specialization_inclusive',
    'exact_parent_version_common_identity_map', 'semantic_context_collection_membership',
    'owner_local_to_coordination_relation', 'claim_records_and_distinct_lanes',
    'budget_or_stop_inclusive_conditional_bindings', 'recomposition_and_terminal_handoff',
    'conformance_collection_not_authority', 'lifecycle_not_admission_posture',
    'C18_meaning_C21_historical_C70_current_type_scopes',
    'v2_discriminator_v1_classification_difference', 'legacy_helper_not_current_package',
    'finite_T_and_required_I_independent',
]
FORBIDDEN = [
    'Definition_admission_accepts_translation', 'type_admission_adopts_CI_instance',
    'CI_is_parent_context_Project_Goal_directory_deployment_or_authority_grant',
    'opaque_parent_version_proves_exact_resolution', 'version_text_is_parent_identity',
    'printed_handle_equality_merges_denotations', 'owner_ref_proves_local_owner_authorization',
    'context_array_shape_proves_context_resolution', 'context_handle_without_members_is_sufficient',
    'realization_and_specialization_must_be_disjoint', 'shared_claim_record_policy_owner_accepted',
    'claim_reference_inequality_proves_lane_separation', 'parent_claim_confers_instance_authority',
    'conformance_implies_authority', 'empty_conformance_proves_conformance',
    'adoption_reference_is_adoption', 'construction_reference_proves_D65_completion',
    'extension_scope_proves_extension_permission', 'status_or_classification_is_lifecycle_without_map',
    'budget_kind_missing_budget_proves_enforcement', 'condition_text_proves_termination',
    'copied_folders_establish_recursion', 'legacy_helper_is_current_package_validator',
    'schema_and_pure_projection_establish_source_fidelity', 'finite_T_I_models_are_whole_proofs',
    'scoped_scan_proves_global_or_private_absence', 'nonentailment_denies_independent_authority',
]
MAP_FIELDS = AXES + [
    'thirty_one_exact_meanings', 'C70_integrated_Governed_Model_instance_exclusion',
    'owner_context_identity_and_parent_version_denotations', 'claim_record_identity_and_lane_policy',
    'external_lifecycle_representation', 'recursion_kind_budget_and_condition_correspondence',
    'adoption_construction_contract_and_conformance_scope', 'owner_acceptance_and_claim_ceiling',
]
SIBLINGS = ['hyp:C18-exact-CI-meaning', 'hyp:C21-historical-v1-type',
            'hyp:C70-current-v2-type', 'hyp:C70-ordinary-instance-only-integrated-Governed-Model',
            'hyp:legacy-helper-current-validator-separation']


def envelope():
    return {'source': b.source_ref(b.snapshot(), 'cal.definition.capability-instance'),
            'scope': b.SCOPE, 'role': 'candidate-exact-CI-coordinate-owner-context-claim-recursion-declarations',
            'authority_effect': 'none', 'claim_scope': 'necessary-declarations-and-proposed-correspondence-only',
            'facets': {n: 'hyp:'+n for n in AXES}, 'actual_owner_review_ref': '', 'accepted_map_refs': []}


def valid_profile(x):
    return (x['before'] == x['after'] == envelope() and set(x['forbidden']) == set(FORBIDDEN)
            and not any(x['forbidden'].values()) and x['source_role_preserved']
            and x['declared_actual_and_carrier_meanings_separate'] and x['twelve_consumer_findings_retained']
            and not x['semantic_acceptance_claimed'] and not x['actual_outcome_claimed'])


def profiles():
    baseline = {'before': envelope(), 'after': envelope(), 'forbidden': {n: False for n in FORBIDDEN},
                'source_role_preserved': True, 'declared_actual_and_carrier_meanings_separate': True,
                'twelve_consumer_findings_retained': True, 'semantic_acceptance_claimed': False,
                'actual_outcome_claimed': False}
    cases = []

    def add(name, mutate, expected):
        x = copy.deepcopy(baseline)
        mutate(x)
        assert valid_profile(x) == expected, name
        cases.append({'case_id': name, 'profile': x, 'expected_rejection': not expected,
                      'qualified_hypothesis_satisfied': valid_profile(x), 'accepted_semantic_map': False})

    add('exact-unaccepted-CI-profile', lambda x: None, True)
    for n in FORBIDDEN:
        add('reject-'+n, lambda x, n=n: x['forbidden'].update({n: True}), False)
    for n in ['source_role_preserved', 'declared_actual_and_carrier_meanings_separate', 'twelve_consumer_findings_retained']:
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

    add('complete-pending-CI-source-map', lambda x: None, True)
    for n in MAP_FIELDS:
        add('missing-map-'+n, lambda x, n=n: x['map_fields'].pop(n), False)
        add('empty-map-'+n, lambda x, n=n: x['map_fields'].update({n: ''}), False)
        add('invented-map-acceptance-'+n, lambda x, n=n: x['accepted_map_refs'].update({n: 'hyp:accepted'}), False)
    for n in ['full_alignment_claimed', 'actual_outcome_claimed', 'source_role_collapsed']:
        add('forbidden-frame-'+n, lambda x, n=n: x.update({n: True}), False)
    add('discarded-upstream-findings', lambda x: x.update(upstream_findings_retained=False), False)
    add('silent-sibling-merge', lambda x: x.update(explicit_sibling_refs=[]), False)
    add('changed-owner-coordinate', lambda x: x['after']['facets'].update(instanceLocalOwner='hyp:changed'), False)
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
    assert len(findings) == 12 and all(x['status'] == 'unresolved' and not x['accepted_map_refs'] for x in findings)
    assert not observation['accepted_semantic_map_refs'] and not observation['actual_instance_adoption_conformance_or_authority_created']
    assert observation['source_coordinate_account_complete'] is True and observation['accepted_semantic_correspondence_complete'] is False
    assert observation['check_count'] == 407 and len(observation['meaning_observations']) == 31
    assert observation['carrier_shape_probe_count'] == 75 and observation['typed_comparison_count'] == 36
    assert observation['isolated_primitive_comparison_count'] == 19
    refs = [b.ref(b.UNIT/n) for n in ['verify_authority_profile.py', 'carrier-consumer-inspection.json',
                                   'carrier-inspection-command-result.json', 'CONSUMER-REVIEW.md', 'types-logic-receipt.json']]
    retained = observation['retained_pre_report_failure_refs']
    b.unchanged(refs + list(observation['selected_inputs'].values()) + retained)
    report = {
        'schema_version': 'definition-assurance-CapabilityInstance-authority-profile/v1-candidate',
        'status': 'PASS-for-qualified-CI-hypotheses-and-exact-consumer-comparisons',
        'authority_effect': 'none', 'source': context['source_selection'], 'profiles': ps,
        'finite_comparison_frames': fs, 'source_map_obligations': MAP_FIELDS,
        'accepted_source_to_carrier_or_consumer_map_refs': [], 'cross_definition_review_findings': findings,
        'actual_checks': observation['checks'], 'actual_check_count': observation['check_count'],
        'carrier_consumer_observation': observation,
        'selected_inputs': {str(i): x for i, x in enumerate(refs + list(observation['selected_inputs'].values()) + retained)},
        'checker_bindings': [b.ref(b.UNIT/'verify_authority_profile.py'), b.ref(b.UNIT/'inspect_carrier_consumers.py'), b.ref(b.IMPL/'contracts.py')],
        'runtime_bindings': runtime, 'bound_package_validator_executed': False,
        'canonical_or_candidate_carrier_writer_executed': False, 'native_or_live_consumer_executed': False,
        'legacy_helper_is_current_bound_package': False, 'actual_instance_effects_created': False,
        'direct_carrier_or_consumer_alignment_accepted': False,
        'retained_failed_consumer_comparison_refs': retained, 'new_authorities_or_relations_created': 0,
        'source_fidelity': 'pending', 'semantic_ready': False, 'mechanized_proof': False,
        'claim_ceiling': 'Finite qualified CI correspondence hypotheses and exact observations only. Proposed maps and explicit residue do not establish owner acceptance, actual instance adoption/conformance/authority, fidelity or whole proof.'}
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
