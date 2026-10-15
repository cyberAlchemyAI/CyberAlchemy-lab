"""Read-only audit of actual CI consumer/profile/reuse evidence and original scope."""
from pathlib import Path
import collections, hashlib, json, sys
root = Path.cwd()
prepared = Path(__file__).resolve().parent
unit = root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.capability-instance'
sys.path.insert(0, str(unit))
import build_candidate as b
import inspect_carrier_consumers as consumer
import verify_authority_profile as profile


def load(path):
    return json.loads(path.read_bytes())


checks = []


def check(name, condition):
    assert condition, name
    checks.append({'check_id': name, 'result': True})


observation = consumer.inspect()
qualified = profile.verify()
check('fresh-observations-equal-recorded-report', observation == load(unit/'carrier-consumer-inspection.json'))
check('fresh-profiles-equal-recorded-report', qualified == load(unit/'authority-profile-checks.json'))
check('407actual-observation-checks', observation['check_count'] == len(observation['checks']) == 407 and all(x['result'] is True for x in observation['checks']))
source = load(root/observation['source']['path'])
expression = source['voices']['scientific_formal']['formal_expression']
coordinates = [x.strip() for x in expression.split('(', 1)[1].split(')', 1)[0].split(',')]
matrix = observation['source_coordinate_correspondence']
check('exact-canonical-sixteen-coordinate-order', [x['source_coordinate'] for x in matrix[:16]] == coordinates and len(coordinates) == 16)
check('owner-companion-not-tuple-rewrite', len(matrix) == 17 and matrix[-1]['source_coordinate'] == 'local_owner_companion' and 'local owner' in source['voices']['scientific_formal']['testable_conditions'][0])
check('each-map-explicit-and-unaccepted', all(x['status'] == 'pending-owner-correspondence' and x['accepted_map_refs'] == [] and x['meaning_obligation'] for x in matrix))
check('candidate-symbol-types-exact', all(b.FUNCTIONS[x['candidate_symbol']][1] == x['candidate_sort'] for x in matrix))
check('lifecycle-residue-retained', next(x for x in matrix if x['source_coordinate'] == 'lifecycle')['direct_schema_field_present'] is False)
check('31current-meanings-no-whole-import', len(observation['meaning_observations']) == 31 and all(not x['accepted_map_refs'] and x['whole_theory_imported'] is False for x in observation['meaning_observations']))
check('30Definition75carrierprobes', observation['definition_shape_probe_count'] == len(observation['definition_shape_probes']) == 30 and observation['carrier_shape_probe_count'] == len(observation['carrier_shape_probes']) == 75)
comparison = {x['case_id']: x for x in observation['typed_comparison_models']}
check('36models19isolatedguards', len(comparison) == 36 and sum(x['semantic_guard_isolated'] for x in comparison.values()) == 19)
for case in comparison.values():
    check('model-hash-'+case['case_id'], b.ir.digest(case['model']) == case['model_sha256'])
    if case['semantic_guard_isolated']:
        check('isolated-'+case['case_id'], [n for n, truth in case['primitive_results'].items() if not truth] == case['expected_only_failed_primitives'])
check('common-claim-record-model-is-true-true', comparison['same-claim-record-reference-with-distinct-declared-lanes']['T'] is True and comparison['same-claim-record-reference-with-distinct-declared-lanes']['I'] is True)
check('common-printed-handle-not-common-denotation', comparison['same-printed-instance-identity-and-version-handle-with-distinct-denotation']['T'] is True and comparison['same-printed-instance-identity-and-version-handle-with-distinct-denotation']['I'] is True)
counts = collections.Counter((x['T'], x['I']) for x in comparison.values())
check('T-I-independent-distribution', counts == {(True, True): 10, (True, False): 7, (False, True): 18, (False, False): 1})
check('step-limits-not-weakened', max(x['T_I_steps'] for x in comparison.values()) == 30041 and max(x['primitive_steps'] for x in comparison.values()) == 7918)
check('37profiles36rejections', len(qualified['profiles']) == 37 and sum(x['expected_rejection'] for x in qualified['profiles']) == 36)
check('142frames141rejections45obligations', len(qualified['finite_comparison_frames']) == 142 and sum(x['expected_rejection'] for x in qualified['finite_comparison_frames']) == 141 and len(qualified['source_map_obligations']) == 45)
check('12unresolved-findings-no-map-acceptance', len(observation['unresolved_consumer_findings']) == 12 and not qualified['accepted_source_to_carrier_or_consumer_map_refs'] and observation['accepted_semantic_correspondence_complete'] is False)
check('no-actual-effects-or-whole-proof', observation['actual_instance_adoption_conformance_or_authority_created'] is False and qualified['actual_instance_effects_created'] is False and observation['semantic_ready'] is qualified['semantic_ready'] is False and observation['mechanized_proof'] is qualified['mechanized_proof'] is False)
check('current-package-and-legacy-remain-distinct', observation['bound_package_validator_executed'] is False and observation['legacy_helper_is_current_bound_package'] is False)
check('historical-schema-local-no-remote-retrieval', observation['historical_schema_reference_resolved_from_exact_local_bytes'] is True and observation['schema_remote_retrieval_disabled'] is True)
bindings = []
for stem in ['consumer-inspection', 'consumer-inspection-replay', 'profile', 'profile-replay', 'reuse']:
    path = prepared/(stem+'-command-result.json')
    result = load(path)
    check('actual-terminal0-'+stem, result['exit_code'] == 0 and not (prepared/result['stderr']).read_bytes())
    bindings.extend([b.ref(path), b.ref(prepared/result['stdout']), b.ref(prepared/result['stderr'])])
for stem in ['consumer-inspection', 'profile']:
    check('actual-replay-stdout-parity-'+stem, (prepared/(stem+'-stdout.txt')).read_bytes() == (prepared/(stem+'-replay-stdout.txt')).read_bytes())
retained = observation['retained_pre_report_failure_refs']
check('10retained-failure-bindings', len(retained) == 10)
for number in [1, 2]:
    retained_path = prepared/('retained-consumer-inspection-'+str(number))
    check('retained-actual-failure-'+str(number), load(retained_path/'consumer-inspection-command-result.json')['exit_code'] == 1 and load(retained_path/'observation.json')['report_created'] is False)
reuse = load(unit/'static-snapshot-reuse-checks.json')
check('15strict-reuse-checks', len(reuse['checks']) == 15 and all(x['result'] for x in reuse['checks']))
check('reuse-no-live-reuse-or-shared-validator-change', reuse['live_currentness_reused'] is reuse['shared_sealed_validator_files_modified'] is reuse['model_evaluation_or_correspondence_checks_skipped'] is False)
for name in ['static_snapshot_reuse.py', 'verify_static_snapshot_reuse.py']:
    check('exact-generic-reuse-copy-'+name, (unit/name).read_bytes() == (b.BASE/'definitions/CAV2-D60'/name).read_bytes())
frozen = load(unit/'types-logic-receipt.json')
check('typed-stage-remains17inputs5checkers-full-unsealed', len(frozen['inputs']) == 17 and len(frozen['checker_bindings']) == 5 and frozen['full_delivery_sealed'] is False)
prior = load(b.BASE/'definitions/CAV2-D60/delivery-manifest.json')['files']
b.unchanged(frozen['inputs'] + frozen['checker_bindings'] + prior + retained + bindings + list(observation['selected_inputs'].values()) + list(qualified['selected_inputs'].values()))
check('10188predecessors201sources-preserved', len(prior) == 10188 and b.r.verify(b.snapshot(), root)['files'] == 201)
manifest = load(root/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/swu-manifest.json')
check('original797work-units-retained', len(manifest['units']) == 797)
state = load(prepared/'current-state.json')
check('original-scope-and-active-goal-retained', state['original_scope'] == {'identities': 183, 'versions': 189, 'source_files': 201, 'tasks': 121, 'edges': 511, 'work_units': 797, 'frontiers': 36} and state['goal_status'] == 'active')
report = {'schema_version': 'CapabilityInstance-consumer-profile-closeout-audit/v1-candidate',
          'result': 'PASS-for-bounded-consumer-profile-and-static-reuse-stage',
          'checks': checks, 'check_count': len(checks), 'actual_terminal_records': bindings,
          'selected_inputs': [b.ref(unit/n) for n in ['carrier-consumer-inspection.json', 'authority-profile-checks.json', 'CONSUMER-REVIEW.md', 'static-snapshot-reuse-checks.json']] + [b.ref(Path(__file__).resolve())],
          'frozen_inputs_preserved': 17, 'frozen_checker_bindings_preserved': 5,
          'prior_candidate_files_preserved': 10188, 'source_files_current': 201,
          'original_work_units': 797, 'source_coordinate_account_complete': True,
          'accepted_semantic_correspondence_complete': False, 'full_delivery_sealed': False,
          'source_fidelity': 'pending', 'semantic_ready': False, 'whole_definition_proofs': 0,
          'source_owner_accepted_whole_translations': 0, 'authority_effect': 'none', 'goal_status': 'active'}
with (prepared/'consumer-profile-closeout-audit.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True); stream.write('\n')
print(json.dumps({'result': report['result'], 'checks': len(checks), 'full_delivery_sealed': False, 'semantic_ready': False}, indent=2))
