"""Read-only preservation, unassembled-comparison and partial-source-currentness audit."""
import json
import build_candidate as b


def main():
    receipt = json.loads((b.UNIT / 'receipt.json').read_bytes())
    manifest = json.loads((b.UNIT / 'delivery-manifest.json').read_bytes())
    prior = json.loads((b.BASE / 'definitions/cal.definition.governed-model/delivery-manifest.json').read_bytes())
    checks = json.loads((b.UNIT / 'source-checks.json').read_bytes())
    for reference in receipt['inputs'] + receipt['outputs'] + manifest['files'] + prior['files'] + list(checks['selected_inputs'].values()):
        if b.ref(b.ROOT / reference['path']) != reference: raise ValueError('Changed bound bytes: ' + reference['path'])
    context = json.loads((b.UNIT / 'context.json').read_bytes()); b.external_current(context)
    source = b.r.verify(b.snapshot(), b.ROOT)
    if receipt['whole_definition_translation'] != 'pending' or receipt['source_fidelity'] != 'pending' or receipt['semantic_ready'] is not False or receipt['mechanized_proof'] is not False:
        raise ValueError('False whole translation/fidelity/proof acceptance')
    expected = {'model_controls': 34, 'nonentailment_query_outcomes': 4, 'separate_comparison_clauses': 4, 'actual_bounded_source_checks': 13}
    if any(receipt['validation'][key] != value for key, value in expected.items()) or receipt['validation']['comparison_assembled_into_primary_T'] is not False:
        raise ValueError('Wrong evidence/slice denominator')
    if not checks['source_testable_conditions'][1]['result'].startswith('PARTIAL:') or checks['source_location']['repository_identity_authenticated'] is not False:
        raise ValueError('Local source copy cannot certify canonical upstream currentness')
    if source['files'] != 201 or len(prior['files']) != 811: raise ValueError('Wrong source/predecessor denominator')
    print(json.dumps({'result': 'PASS-for-byte-preservation-and-partial-claim-boundary', 'candidate_files': len(manifest['files']),
        'prior_candidate_files_preserved': 811, 'source_files_current': 201, 'external_selected_local_files_current': 1, **expected,
        'comparison_assembled_into_primary_T': False, 'whole_translation': 'pending', 'source_fidelity': 'pending',
        'semantic_ready': False, 'goal_status': 'active', 'next_independent_unit': 'F01-T.cal.definition.invariant'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
