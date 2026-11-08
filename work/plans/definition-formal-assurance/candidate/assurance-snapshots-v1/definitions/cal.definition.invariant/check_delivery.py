"""Read-only delivery preservation and partial formalization claim audit."""
import json
import build_candidate as b


def main():
    def load(name): return json.loads((b.UNIT / name).read_bytes())
    receipt = load('receipt.json'); manifest = load('delivery-manifest.json'); checks = load('source-checks.json')
    prior = json.loads((b.BASE / 'definitions/cal.definition.hypothesis/delivery-manifest.json').read_bytes())
    for ref in receipt['inputs'] + receipt['outputs'] + manifest['files'] + prior['files'] + list(checks['selected_inputs'].values()):
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Changed bound bytes: ' + ref['path'])
    context = load('context.json'); b.external_current(context); source = b.r.verify(b.snapshot(), b.ROOT)
    if receipt['whole_definition_translation'] != 'pending' or receipt['source_fidelity'] != 'pending' or receipt['semantic_ready'] is not False or receipt['mechanized_proof'] is not False:
        raise ValueError('False whole fidelity/proof/readiness acceptance')
    expected = {'model_controls': 32, 'nonentailment_query_outcomes': 2, 'finite_authored_scenarios': 6, 'actual_bounded_source_checks': 12}
    if any(receipt['validation'][key] != value for key, value in expected.items()) or receipt['validation']['scenario_targets_assembled_into_primary_T'] is not False or receipt['validation']['actual_implementation_checked'] is not False:
        raise ValueError('Wrong evidence/target denominator')
    if not checks['source_testable_conditions'][1]['result'].startswith('PARTIAL:') or checks['source_location']['repository_identity_authenticated'] is not False:
        raise ValueError('Selected local copy cannot certify live producer currentness')
    graph = load('dependency-graph.json')
    if len(graph['cycle_reviews']) != 1 or graph['cycle_reviews'][0]['disposition'] != 'unresolved-cycle-classification':
        raise ValueError('Mutual source-reference cycle falsely settled')
    if source['files'] != 201 or len(prior['files']) != 869: raise ValueError('Wrong source/predecessor denominator')
    print(json.dumps({'result': 'PASS-for-byte-preservation-and-partial-claim-boundary', 'candidate_files': len(manifest['files']),
        'prior_candidate_files_preserved': 869, 'source_files_current': 201, 'external_selected_local_files_current': 1, **expected,
        'scenario_targets_assembled_into_primary_T': False, 'whole_translation': 'pending', 'source_fidelity': 'pending',
        'semantic_ready': False, 'goal_status': 'active', 'next_independent_unit': 'F01-T.cal.definition.premise'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
