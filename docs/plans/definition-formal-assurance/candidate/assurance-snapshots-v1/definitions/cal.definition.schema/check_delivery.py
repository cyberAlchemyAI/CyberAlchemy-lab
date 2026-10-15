"""Read-only preservation, finite-profile and partial-claim audit."""
import json
import build_candidate as b


def main():
    def load(name): return json.loads((b.UNIT / name).read_bytes())
    receipt = load('receipt.json'); manifest = load('delivery-manifest.json'); source_checks = load('source-checks.json')
    prior = json.loads((b.BASE / 'definitions/cal.definition.premise/delivery-manifest.json').read_bytes())
    for ref in receipt['inputs'] + receipt['outputs'] + manifest['files'] + prior['files'] + list(source_checks['selected_inputs'].values()):
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Changed bound bytes: ' + ref['path'])
    context = load('context.json'); b.external_current(context); source = b.r.verify(b.snapshot(), b.ROOT)
    if receipt['whole_definition_translation'] != 'pending' or receipt['source_fidelity'] != 'pending' or receipt['semantic_ready'] is not False or receipt['mechanized_proof'] is not False:
        raise ValueError('False whole fidelity/proof/readiness acceptance')
    expected = {'model_controls': 44, 'nonentailment_query_outcomes': 5, 'finite_structural_controls': 18,
        'revision_controls': 3, 'actual_shape_schema_fixture_checks': 1, 'actual_bounded_source_checks': 12}
    if any(receipt['validation'][key] != value for key, value in expected.items()) or receipt['validation']['subject_executed'] is not False or receipt['validation']['occupants_added'] != 0 or receipt['validation']['profile_embedding_reviewed'] is not False:
        raise ValueError('Wrong evidence/profile denominator')
    if not source_checks['source_testable_conditions'][1]['result'].startswith('PARTIAL:') or source_checks['source_location']['repository_identity_authenticated'] is not False:
        raise ValueError('Selected copy cannot certify live producer currentness')
    profile = load('structural-profile-checks.json')
    if profile['actual_schema_fixture']['fixture_owner_authenticated'] is not False or profile['universal_C_N_independence_proved'] is not False:
        raise ValueError('Shape or finite fixtures mistaken for authenticated owner/general independence')
    if source['files'] != 201 or len(prior['files']) != 977: raise ValueError('Wrong source/predecessor denominator')
    print(json.dumps({'result': 'PASS-for-byte-preservation-and-partial-claim-boundary', 'candidate_files': len(manifest['files']),
        'prior_candidate_files_preserved': 977, 'source_files_current': 201, 'external_selected_local_files_current': 1, **expected,
        'whole_translation': 'pending', 'source_fidelity': 'pending', 'semantic_ready': False, 'goal_status': 'active',
        'next_independent_unit': 'F01-T.cal.definition.semantic-primitive'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
