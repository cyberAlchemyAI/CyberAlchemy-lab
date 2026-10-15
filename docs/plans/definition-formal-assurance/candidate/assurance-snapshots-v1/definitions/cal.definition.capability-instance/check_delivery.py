"""Separate read-only CI full audit, with exact current candidate file-set equality."""
import json
import build_candidate as b
import finalize


def main():
    context, core, counts, inventory, graph, qualified, source, prior = finalize.audit()
    receipt, manifest = finalize.load('receipt.json'), finalize.load('delivery-manifest.json')
    b.unchanged(receipt['inputs'] + receipt['outputs'] + manifest['files'] + receipt['retained_diagnostic_and_interruption_refs'] + receipt['retained_successful_preparation_refs'])
    assert receipt['task_result'] == 'PARTIAL-DRAFT-VERIFIED' and receipt['source_fidelity'] == 'pending'
    assert receipt['semantic_ready'] is receipt['mechanized_proof'] is False
    assert receipt['whole_definition_translation'] == 'pending' and receipt['whole_definition_proof'] is None
    assert receipt['validation']['accepted_CI_carrier_or_consumer_maps'] == 0 and receipt['validation']['actual_CI_instance_effects_established'] is False
    assert len(receipt['cross_definition_review_findings']) == 12 and len(receipt['retained_failed_consumer_comparison_refs']) == 10
    assert receipt['validation']['retained_failed_consumer_comparisons'] == 2 and receipt['validation']['retained_interrupted_typed_audits'] == 1
    assert len(list((b.BASE/'definitions').glob('*/t.json'))) == 109
    assert manifest['validation'] == receipt['validation'] and manifest['prior_seal_files'] == receipt['validation']['prior_candidate_files_preserved'] == len(prior['files']) == 10188
    for ref in receipt['external_source_refs']:
        assert b.r.digest(b.Path(ref['absolute_path']).read_bytes()) == ref['sha256']
    current = sorted([b.ref(path) for folder in [b.BASE, b.IMPL] for path in folder.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc' and path != b.UNIT/'delivery-manifest.json'], key=lambda x: x['path'])
    assert current == manifest['files'], 'Current candidate files differ from the full CI seal'
    print(json.dumps({'result': 'PASS-for-CI-preservation-and-partial-claim-boundary', 'candidate_files': len(current),
                      'prior_candidate_files_preserved': 10188, 'source_files_current': 201,
                      'partial_drafts': 109, 'missing_current_drafts': 74, 'accepted_CI_maps': 0,
                      'whole_definition_proofs': 0, 'semantic_ready': False,
                      'next_definition_priority': finalize.NEXT, 'goal_status': 'active'}, indent=2))


if __name__ == '__main__':
    main()
