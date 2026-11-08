"""Seal an exact partial CI candidate; accepted translation and whole proof stay pending."""
import collections, json, re, sys
import build_candidate as b
import close_types_logic_stage as stage
import verify_authority_profile as profile
import verifier as v
NEXT = 'F08-T.cal.definition.capability-realization-binding'
PREPARED = b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-capability-instance'


def load(name):
    return json.loads((b.UNIT/name).read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def terminal(folder, stem):
    result = json.loads((folder/(stem+'-command-result.json')).read_bytes())
    require(result['exit_code'] == 0 and not (folder/result['stderr']).read_bytes(), 'Missing successful terminal evidence: '+stem)
    return result


def audit():
    context, counts, model, source, typed_fresh, prior = stage.audit()
    core, typed = load('t.json')['payload'], load('types-logic-receipt.json')
    b.unchanged(typed['inputs'] + typed['checker_bindings'])
    require(len(typed['inputs']) == 17 and len(typed['checker_bindings']) == 5 and typed['full_delivery_sealed'] is False, 'Frozen typed boundary changed')
    for stem in ['typed-stage-freeze', 'typed-stage-audit', 'consumer-inspection', 'consumer-inspection-replay', 'profile', 'profile-replay', 'reuse', 'consumer-profile-audit', 'dependency', 'inventory']:
        terminal(PREPARED, stem)
    root = b.ROOT/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1'
    plan = json.loads((root/'dag.json').read_bytes())
    work = json.loads((root/'swu-manifest.json').read_bytes())
    frontiers = json.loads((root/'topological-frontiers.json').read_bytes())
    require((len(plan['tasks']), sum(len(x['depends_on']) for x in plan['tasks']), len(work['units']), len(frontiers['frontiers'])) == (121, 511, 797, 36), 'Original task scope changed')
    qualified = profile.verify()
    consumer = qualified['carrier_consumer_observation']
    require((len(qualified['profiles']), sum(x['expected_rejection'] for x in qualified['profiles']), len(qualified['finite_comparison_frames']), sum(x['expected_rejection'] for x in qualified['finite_comparison_frames']), len(qualified['source_map_obligations'])) == (37, 36, 142, 141, 45), 'Profile dimensions changed')
    require(consumer['check_count'] == 407 and all(x['result'] for x in consumer['checks']), 'Consumer checks changed')
    require((len(consumer['meaning_observations']), consumer['definition_shape_probe_count'], consumer['definition_shape_acceptances'], consumer['carrier_shape_probe_count'], consumer['carrier_shape_acceptances'], consumer['typed_comparison_count'], consumer['isolated_primitive_comparison_count']) == (31, 30, 6, 75, 25, 36, 19), 'Consumer scope changed')
    require(consumer['direct_current_definition_binding_types'] == ['cal.artifact-type.capability-instance/v2'] and len(consumer['source_coordinate_correspondence']) == 17 and consumer['source_coordinate_account_complete'] is True and consumer['accepted_semantic_correspondence_complete'] is False, 'Coordinate or current binding scope changed')
    require(qualified['accepted_source_to_carrier_or_consumer_map_refs'] == consumer['accepted_semantic_map_refs'] == [], 'Invented accepted maps')
    require([x['finding_id'] for x in qualified['cross_definition_review_findings']] == ['CI-CONSUMER-FINDING-'+str(i).zfill(3) for i in range(1, 13)] and all(x['status'] == 'unresolved' and x['accepted_map_refs'] == [] for x in qualified['cross_definition_review_findings']), 'Consumer findings promoted')
    isolated = [x for x in consumer['typed_comparison_models'] if x['semantic_guard_isolated']]
    require(len(isolated) == 19 and all([n for n, truth in x['primitive_results'].items() if not truth] == x['expected_only_failed_primitives'] and len(x['expected_only_failed_primitives']) == 1 for x in isolated), 'Primitive isolation changed')
    require(all(b.ir.digest(x['model']) == x['model_sha256'] for x in consumer['typed_comparison_models']), 'Comparison model substitution')
    distribution = collections.Counter((x['T'], x['I']) for x in consumer['typed_comparison_models'])
    require(distribution == {(True, True): 10, (True, False): 7, (False, True): 18, (False, False): 1}, 'Independent T/I evidence changed')
    require(all(consumer[n] is False for n in ['legacy_helper_is_current_bound_package', 'bound_package_validator_executed', 'canonical_or_candidate_carrier_writer_executed', 'native_or_live_consumer_executed', 'actual_instance_adoption_conformance_or_authority_created']), 'Unrequested consumer effects')
    c70 = consumer['positive_C70_effects']
    require(c70['artifact_types_admitted'] == 93 and c70['artifact_type_predecessors_to_historical'] == 9 and c70['ordinary_artifact_instances_admitted'] == 1 and c70['typed_relation_instances_admitted'] == c70['consumer_activations'] == c70['runtime_activations'] == 0, 'C70 scope changed')
    probes = {x['case_id']: x for x in consumer['carrier_shape_probes'] if x['version'] == 'v2'}
    for name in ['same-parent-instance-claim-reference', 'instance-ID-equals-version-reference']:
        require(probes[name]['schema_accepted'] is True and probes[name]['legacy_helper_accepted'] is False, 'Schema/helper distinction erased')
    for name in ['budget-kind-missing-budget', 'budget-kind-null-budget', 'owner-stop-no-budget', 'terminal-condition-no-budget', 'empty-conformance-list']:
        require(probes[name]['schema_accepted'] is True, 'Concrete carrier observation changed')
    for name in ['budget-zero', 'budget-negative', 'budget-only-without-condition', 'unreviewed-direct-lifecycle', 'classification-v2-replaces-inherited-v1']:
        require(probes[name]['schema_accepted'] is False, 'Carrier rejection changed')
    require(consumer['historical_schema_reference_resolved_from_exact_local_bytes'] and consumer['schema_remote_retrieval_disabled'], 'Historical schema resource boundary changed')
    graph, local, inventory = load('current-dependency-graph.json'), load('dependency-graph.json'), load('current-inventory.json')
    old_graph, old_inventory = load('../CAV2-D60/current-dependency-graph.json'), load('../CAV2-D60/current-inventory.json')
    old_nodes = {json.dumps(x['source'], sort_keys=True) for x in old_graph['nodes']}
    new_nodes = {json.dumps(x['source'], sort_keys=True) for x in graph['nodes']}
    require(old_nodes <= new_nodes and len(graph['edges']) == len(old_graph['edges']) + 30, 'Joint graph delta changed')
    require({json.dumps(x, sort_keys=True) for x in old_graph['edges']} <= {json.dumps(x, sort_keys=True) for x in graph['edges']} and {json.dumps(x, sort_keys=True) for x in local['edges']} <= {json.dumps(x, sort_keys=True) for x in graph['edges']}, 'Prior or local edges omitted')
    require((len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations']), len(graph['cycle_reviews'])) == (151, 2730, 42, 1), 'Whole graph observations changed')
    require((len(local['nodes']), len(local['edges']), len(local['missing_or_quarantined_interpretations']), len(load('dependency-selection.json')['packet_refs'])) == (147, 2650, 41, 106), 'Reachable graph scope changed')
    require(local['selected_roots'] == [core['source']['version_ref']] and inventory['joint_declared_graph'] == {'nodes': len(graph['nodes']), 'edges': len(graph['edges']), 'missing_counterpart_packets': graph['missing_or_quarantined_interpretations'], 'cycles': graph['cycle_reviews'], 'edge_denominator': graph['edge_denominator']}, 'Inventory/graph mismatch')
    for candidate in [graph, local]:
        require(candidate['semantic_ready'] is False and candidate['edge_denominator'] == 'requires-independent-review' and len(candidate['cycle_reviews']) == 1 and all(x['disposition'] == 'unresolved-cycle-classification' for x in candidate['cycle_reviews']), 'Semantic closure or cycle policy invented')
    require(inventory['counts'] == {k: old_inventory['counts'][k] + counts[k] for k in old_inventory['counts']} and inventory['partial_drafts'] == 109 and len(inventory['missing_current_drafts']) == 74 and inventory['current_definitions'] == 183 and inventory['admitted_source_versions'] == 189 and inventory['next_definition_priority'] == NEXT, 'Original inventory scope changed')
    require(inventory['source_owner_accepted_whole_translations'] == inventory['whole_definition_proofs'] == 0 and inventory['all_per_definition_T_I_models_freshly_evaluated'] is True and len(inventory['selected_model_checks']) == len(inventory['draft_rows']) == 109 and all(x['model_sha256'] == y['selected_model_sha256'] for x, y in zip(inventory['selected_model_checks'], inventory['draft_rows'])), 'Fresh independent witnesses missing')
    reuse = load('static-snapshot-reuse-checks.json')
    require(len(reuse['checks']) == 15 and all(x['result'] for x in reuse['checks']) and all(reuse[n] is False for n in ['live_currentness_reused', 'model_evaluation_or_correspondence_checks_skipped', 'shared_sealed_validator_files_modified', 'semantic_ready', 'mechanized_proof']), 'Static reuse bound changed')
    for observation in [inventory['static_snapshot_verification_reuse'], load('dependency-selection.json')['static_snapshot_verification_reuse']]:
        require(observation['original_static_verifications'] == 2 and observation['reused_static_verifications'] > 0 and observation['live_repository_verifications_reused'] == 0 and observation['live_repository_verifications_delegated'] >= 1 and observation['original_verifier_restored'] and observation['initial_and_final_original_static_results_equal'] and observation['semantic_proof_claimed'] is False, 'Static proof reuse changed')
    for report in [model, qualified, inventory]:
        b.unchanged(report['checker_bindings'] + report.get('input_refs', []))
        require(report['runtime_bindings'] == v.f.current_bindings() and report['semantic_ready'] is False and report['source_fidelity'] == 'pending' and report['mechanized_proof'] is False, 'Runtime or semantic acceptance changed')
    b.unchanged(list(source['selected_inputs'].values()) + list(qualified['selected_inputs'].values()) + reuse['selected_inputs'])
    fresh = load('fresh-command-results.json')
    require([x['check'] for x in fresh] == ['contract', 'model', 'source', 'profile', 'dependency', 'inventory'], 'Missing six-check ledger')
    for row in fresh:
        require(row == terminal(b.UNIT, 'fresh-'+row['check']), 'Fresh terminal record substituted')
        original = 'fresh-types-contract-stdout.txt' if row['check'] == 'contract' else row['check']+'-stdout.txt'
        require((b.UNIT/row['stdout']).read_bytes() == (b.UNIT/original).read_bytes(), 'Fresh stdout differs')
    for name in ['author', 'build', 'model', 'source', 'carrier-inspection', 'profile', 'reuse', 'dependency', 'inventory']:
        terminal(b.UNIT, name)
    require(len(consumer['retained_pre_report_failure_refs']) == 10, 'Consumer failures discarded')
    b.unchanged(consumer['retained_pre_report_failure_refs'] + typed['retained_review_writer_failure_refs'] + context['retained_preparation_failure_refs'] + context['retained_successful_preparation_refs'])
    dag = load('work-delivery-dag.json')
    require(dag['source'] == core['source'] and len(dag['nodes']) == len(dag['edges']) == 18 and dag['next_native_requires_full_separate_audit'] is True and dag['whole_episode_complete'] is False and dag['authority_effect'] == 'none', 'Work DAG scope changed')
    pending = {x['id'] for x in dag['nodes']}
    done = set()
    while pending:
        ready = {n for n in pending if all(left in done for left, right in dag['edges'] if right == n)}
        require(ready, 'Work DAG has a cycle')
        done |= ready; pending -= ready
    review = (b.UNIT/'DELIVERY-REVIEW.md').read_text()
    require(len(review.split()) > 4000 and len(re.findall(r'^## [0-9]+\.', review, re.M)) == 13 and all('CI-FINDING-'+str(i).zfill(3) in review for i in range(1, 27)) and all('CI-CONSUMER-FINDING-'+str(i).zfill(3) in review for i in range(1, 13)), 'Full aspect explanation incomplete')
    unrelated = json.loads((b.ROOT/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-project/unrelated-tracked-work.json').read_bytes())
    b.unchanged(unrelated['refs'])
    require(unrelated['tracked_dirty_count'] == len(unrelated['refs']) == 30, 'Unrelated work denominator changed')
    b.unchanged(prior['files'] + context['sources'])
    b.external_current(context)
    return context, core, counts, inventory, graph, qualified, source, prior


def main():
    context, core, counts, inventory, graph, qualified, source, prior = audit()
    common = {'authority_effect': 'none', 'goal_status': 'active', 'source_fidelity': 'pending',
              'semantic_ready': False, 'mechanized_proof': False, 'whole_definition_translation': 'pending',
              'full_episode_completion': 'not-established', 'next_definition_priority': NEXT}
    validation = {**counts, 'sorts': 23, 'constants': 3, 'functions': 45, 'predicate_signatures': 100,
                  'primitive_theory_templates': 7, 'model_controls': 186, 'T_true_controls': 57,
                  'T_false_controls': 121, 'malformed_rejections': 8, 'nonentailment_queries': 28,
                  'source_conditioned_queries': 2, 'actual_source_checks': 93,
                  'source_query_obligations': 63, 'qualification_profiles': 37, 'rejected_profiles': 36,
                  'finite_source_map_frames': 142, 'rejected_frames': 141,
                  'catalog_and_consumer_checks': 407, 'Definition_schema_probes': 30,
                  'Definition_schema_acceptances': 6, 'carrier_schema_probes': 75,
                  'carrier_schema_acceptances': 25, 'typed_comparison_models': 36,
                  'isolated_semantic_guard_models': 19, 'source_map_obligations': 45,
                  'source_coordinate_and_owner_map_rows': 17, 'unresolved_cross_definition_findings': 12,
                  'accepted_CI_carrier_or_consumer_maps': 0, 'static_reuse_adversarial_differential_checks': 15,
                  'all_per_definition_T_I_models_freshly_evaluated': True,
                  'prior_candidate_files_preserved': len(prior['files']), 'source_files_current': 201,
                  'fresh_replays': 'PASS for six actual terminal checks',
                  'retained_prepared_syntax_failures': 1, 'retained_review_writer_failures': 1,
                  'retained_consumer_discovery_failures': 1, 'retained_failed_consumer_comparisons': 2,
                  'retained_interrupted_typed_audits': 1, 'retained_failed_prepared_semantic_controls': 0,
                  'retained_failed_native_definition_producers': 0, 'retained_failed_fresh_checks': 0,
                  'checker_limits_unchanged': True, 'actual_CI_instance_effects_established': False}
    typed = load('types-logic-receipt.json')
    retained = context['retained_preparation_failure_refs'] + typed['retained_review_writer_failure_refs'] + qualified['retained_failed_consumer_comparison_refs']
    discovery_failure = PREPARED/'retained-consumer-discovery-1'
    retained += [b.ref(path) for path in sorted(discovery_failure.iterdir()) if path.is_file()]
    retained += [b.ref(PREPARED/'interrupted-typed-audit-observation.json')]
    b.unchanged(retained + context['retained_successful_preparation_refs'])
    inputs = context['sources'] + list(source['selected_inputs'].values()) + list(qualified['selected_inputs'].values()) + inventory['input_refs']
    inputs += [b.ref(PREPARED/name) for name in ['ARE-dependencies-inventory.json', 'GRAPH-INVENTORY-CONTEXT.md',
                                               'consumer-profile-closeout-audit.json', 'consumer-profile-audit-command-result.json']]
    outputs = [b.ref(path) for path in sorted(b.UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc' and path.name not in ['receipt.json', 'delivery-manifest.json', 'coverage-row.json', 'episode-status.json']]
    b.put('receipt.json', {'schema_version': 'definition-assurance-task-receipt/v1-candidate', **common,
                          'unit_id': context['unit_id'], 'task_result': 'PARTIAL-DRAFT-VERIFIED',
                          'artifact_owner_translation_acceptance': 'pending', 'whole_definition_proof': None,
                          'inputs': inputs, 'outputs': outputs, 'external_source_refs': context['external_sources'],
                          'validation': validation, 'cross_definition_review_findings': qualified['cross_definition_review_findings'],
                          'retained_failed_native_attempt_refs': [], 'retained_failed_preparation_refs': context['retained_preparation_failure_refs'],
                          'retained_successful_preparation_refs': context['retained_successful_preparation_refs'],
                          'retained_failed_consumer_comparison_refs': qualified['retained_failed_consumer_comparison_refs'],
                          'retained_diagnostic_and_interruption_refs': retained,
                          'native_vs_historical_reporting': 'Current109 inventory remains separate from earlier scoped inventories and original planned-output presence reviews.'})
    b.put('coverage-row.json', {'schema_version': 'definition-assurance-coverage-row/v1-candidate', **common,
                              'definition_id': core['source']['definition_id'], 'source': core['source'], 'counts': counts,
                              'status': 'partial-draft-verified', 'whole_definition_proof': None, 'owner_translation_acceptance': 'pending'})
    b.put('episode-status.json', {'schema_version': 'definition-assurance-episode-status/v1-candidate', **common,
                                'partial_drafts': 109, 'missing_current_drafts': 74, 'current_definitions': 183,
                                'admitted_source_versions': 189, 'source_files_current': 201,
                                'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0,
                                'current_inventory_counts': inventory['counts'], 'joint_declared_graph': inventory['joint_declared_graph'],
                                'original_tasks': 121, 'original_edges': 511, 'original_SWUs': 797, 'original_frontiers': 36})
    files = sorted([b.ref(path) for folder in [b.BASE, b.IMPL] for path in folder.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc' and path != b.UNIT/'delivery-manifest.json'], key=lambda x: x['path'])
    b.put('delivery-manifest.json', {'schema_version': 'definition-assurance-delivery-manifest/v1-candidate', **common,
                                   'files': files, 'prior_seal_files': len(prior['files']), 'validation': validation})
    print(json.dumps({'result': 'PARTIAL-DRAFT-VERIFIED', 'candidate_files': len(files),
                      'prior_candidate_files_preserved': len(prior['files']), 'source_files_current': 201,
                      'partial_drafts': 109, 'missing_current_drafts': 74, 'accepted_CI_maps': 0,
                      'whole_definition_proofs': 0, 'semantic_ready': False, 'next_definition_priority': NEXT,
                      'goal_status': 'active'}, indent=2))


if __name__ == '__main__':
    main()
