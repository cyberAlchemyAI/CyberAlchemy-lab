"""Read-only preservation and claim-boundary audit of the sealed Governed Model draft."""
import json
import build_candidate as b


def main():
    receipt = json.loads((b.UNIT / 'receipt.json').read_bytes())
    manifest = json.loads((b.UNIT / 'delivery-manifest.json').read_bytes())
    prior = json.loads((b.BASE / 'definitions/cal.definition.definition/delivery-manifest.json').read_bytes())
    source_checks = json.loads((b.UNIT / 'source-checks.json').read_bytes())
    references = receipt['inputs'] + receipt['outputs'] + manifest['files'] + prior['files']
    references += list(source_checks['selected_inputs'].values())
    posture = json.loads((b.UNIT / 'source-posture-review.json').read_bytes())
    references += posture['input_refs']
    if posture['logical_contradiction'] != 'not-established' or posture['semantic_ready'] is not False:
        raise ValueError('False source-posture semantic promotion')
    for reference in references:
        if b.ref(b.ROOT / reference['path']) != reference:
            raise ValueError('Changed bound bytes: ' + reference['path'])
    source = b.r.verify(b.snapshot(), b.ROOT)
    if receipt['whole_definition_translation'] != 'pending' or receipt['source_fidelity'] != 'pending':
        raise ValueError('False whole translation/fidelity acceptance')
    if receipt['semantic_ready'] is not False or receipt['mechanized_proof'] is not False:
        raise ValueError('False readiness/proof promotion')
    expected = {'model_controls': 36, 'nonentailment_query_outcomes': 7, 'actual_source_checks': 9}
    if any(receipt['validation'][key] != value for key, value in expected.items()):
        raise ValueError('Wrong evidence denominator')
    if source['files'] != 201 or len(prior['files']) != 746:
        raise ValueError('Wrong predecessor/source denominator')
    print(json.dumps({'result': 'PASS-for-byte-preservation-and-partial-claim-boundary',
        'candidate_files': len(manifest['files']), 'prior_candidate_files_preserved': 746,
        'source_files_current': 201, **expected, 'whole_translation': 'pending',
        'source_fidelity': 'pending', 'semantic_ready': False, 'goal_status': 'active',
        'next_independent_unit': 'F01-T.cal.definition.hypothesis'}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
