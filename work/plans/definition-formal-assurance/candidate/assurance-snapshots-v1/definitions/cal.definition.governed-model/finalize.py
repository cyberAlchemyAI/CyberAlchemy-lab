"""Seal partial Governed Model draft evidence without accepting a whole translation."""
import json
import build_candidate as b
import verifier as v


def load(name):
    return json.loads((b.UNIT / name).read_bytes())


def unchanged(references):
    for reference in references:
        if b.ref(b.ROOT / reference['path']) != reference:
            raise ValueError('Changed bound bytes: ' + reference['path'])


def main():
    context = load('context.json')
    unchanged(context['sources'])
    prior = json.loads((b.BASE / 'definitions/cal.definition.definition/delivery-manifest.json').read_bytes())
    unchanged(prior['files'])
    for name in ['A04', 'C01', 'E02']:
        upstream = json.loads((b.BASE / f'units/{name}/receipt.json').read_bytes())
        unchanged(upstream['inputs'] + upstream['outputs'])
    model = load('model-controls.json')
    fresh = load('fresh-model-stdout.txt')
    graph = load('dependency-graph.json')
    fresh_graph = load('fresh-dependency-stdout.txt')
    source_checks = load('source-checks.json')
    fresh_source = load('fresh-source-stdout.txt')
    packet = load('correspondence.json')
    core = load('t.json')['payload']
    contract = load('contract-check-stdout.txt')
    counts = {'controls': 36, 'nonentailment_query_outcomes': 7, 'source_units': 21,
              'mapped_clauses': 23, 'encoded_clauses': 4, 'deferred_clauses': 13,
              'required_populations': 13, 'unresolved_populations': 11}
    if any(fresh[key] != value for key, value in counts.items()):
        raise ValueError('Wrong replay denominator')
    if fresh['result'] != model['status'] or model['control_count'] != 36:
        raise ValueError('Fresh independent model replay required')
    if contract['status'] != 'structurally-valid':
        raise ValueError('Declared contract command must pass')
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (13, 13, 11):
        raise ValueError('Wrong dependency closure denominator')
    if fresh_graph['result'] != 'PASS-for-exact-authored-and-transitive-uses' or graph['edge_denominator'] != 'requires-independent-review':
        raise ValueError('Dependency replay or independent-review ceiling missing')
    if len(source_checks['checks']) != 9 or not all(row['result'] is True for row in source_checks['checks']):
        raise ValueError('Nine actual source checks required')
    if fresh_source['result'] != source_checks['status'] or fresh_source['checks'] != 9:
        raise ValueError('Fresh actual-source replay required')
    posture = load('source-posture-review.json')
    fresh_posture = load('fresh-source-posture-stdout.txt')
    if fresh_posture['result'] != posture['status'] or posture['logical_contradiction'] != 'not-established' or posture['semantic_ready'] is not False:
        raise ValueError('Source-posture facts cannot become contradiction or fidelity claims')
    if len(packet['source_precedence']['conflicts']) != 5:
        raise ValueError('All five source findings required')
    unchanged(posture['input_refs'])
    unchanged(model['input_refs'] + model['checker_bindings'] + list(source_checks['selected_inputs'].values()))
    if model['runtime_bindings'] != v.f.current_bindings():
        raise ValueError('Closing runtime drift')
    for stem in ['build', 'model-check', 'dependency-check', 'contract-check',
                 'source-check', 'fresh-model', 'fresh-dependency', 'fresh-source',
                 'source-posture', 'fresh-source-posture']:
        if (b.UNIT / (stem + '-stderr.txt')).read_bytes():
            raise ValueError('Unresolved execution failure: ' + stem)
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending':
        raise ValueError('Assumption or fidelity substitution')
    if model['semantic_ready'] is not False or model['mechanized_proof'] is not False:
        raise ValueError('False semantic/proof promotion')
    if not (b.UNIT / 'REVIEW.md').is_file():
        raise ValueError('Detailed aspect review missing')
    source = b.r.verify(b.snapshot(), b.ROOT)
    if source['files'] != 201 or len(prior['files']) != 746:
        raise ValueError('Wrong source or predecessor denominator')
    episode = {
        'authority_effect': 'none', 'goal_status': 'active',
        'latest_candidate_draft': 'F01-T.cal.definition.governed-model',
        'phase_result': 'partial-draft-verified; whole translation unresolved',
        'current_definitions': 183, 'admitted_source_versions': 189,
        'per_definition_T_candidate_drafts': len(list((b.BASE / 'definitions').glob('*/t.json'))),
        'new_source_units_accounted': 21, 'new_clauses_accounted': 23,
        'new_static_clauses_encoded': 4, 'governed_model_deferred_clauses': 13,
        'governed_model_unresolved_population_policies': 11,
        'governed_model_missing_transitive_dependency_packets': 11,
        'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0,
        'source_files_current': 201, 'prior_candidate_files_preserved': 746,
        'next_independent_unit': 'F01-T.cal.definition.hypothesis',
        'remaining_foundations_family': ['cal.definition.hypothesis',
            'cal.definition.invariant', 'cal.definition.premise', 'cal.definition.schema',
            'cal.definition.semantic-primitive'],
        'full_project_completion': 'not-established'}
    b.put('episode-status.json', episode)
    coverage = {
        'authority_effect': 'none', 'definition_id': core['source']['definition_id'],
        'source': core['source'], 'interpretation_ref': b.ref(b.UNIT / 't.json'),
        'correspondence_ref': b.ref(b.UNIT / 'correspondence.json'),
        'static_ir_ref': b.ref(b.UNIT / 'static-ir.json'),
        'review_ref': b.ref(b.UNIT / 'REVIEW.md'),
        'model_evidence_ref': b.ref(b.UNIT / 'model-controls.json'),
        'source_checks_ref': b.ref(b.UNIT / 'source-checks.json'),
        'source_posture_review_ref': b.ref(b.UNIT / 'source-posture-review.json'),
        'dependency_graph_ref': b.ref(b.UNIT / 'dependency-graph.json'),
        'logical_status': 'typed-static-subject-necessary-condition-draft',
        'character_accounting_complete': True, 'source_units': 21, 'mapped_clauses': 23,
        'encoded_clauses': 4, 'explanatory_clauses': 6, 'deferred_clauses': 13,
        'required_populations': 13, 'unresolved_populations': 11,
        'direct_semantic_uses': 10, 'semantic_closure': 'unresolved-eleven-missing-transitive-counterpart-packets',
        'source_fidelity': 'pending', 'semantic_ready': False,
        'whole_definition_translation': 'pending', 'whole_definition_proof': None,
        'owner_review': {'status': 'pending', 'source_owner_ref': 'role:definition-owner',
            'owner_principal_ref': None, 'decision_ref': None,
            'findings': [row['finding_id'] for row in packet['source_precedence']['conflicts']]}}
    b.put('coverage-row.json', coverage)
    outputs = [b.ref(path) for path in sorted(b.UNIT.rglob('*'))
               if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    receipt = {
        'schema_version': 'definition-assurance-unit-receipt/v1-candidate',
        'unit_id': 'F01-T.cal.definition.governed-model', 'authority_effect': 'none',
        'goal_status': 'active',
        'task_result': 'PARTIAL: exact source-accounted typed draft and model/source checks verified; whole translation, fidelity, closure and population policies unresolved',
        'inputs': context['sources'], 'outputs': outputs,
        'validation': {'declared_contract_command': ['python3',
            'craft/formalization/candidates/definition-assurance-v1/contracts.py', 'validate',
            '--kind', 'interpretation', '--input', b.ref(b.UNIT / 't.json')['path']],
            'contract_result': 'structurally-valid', 'model_controls': 36,
            'nonentailment_query_outcomes': 7,
            'actual_source_checks': 9,
            'fresh_model_ref': b.ref(b.UNIT / 'fresh-model-stdout.txt'),
            'fresh_dependency_ref': b.ref(b.UNIT / 'fresh-dependency-stdout.txt'),
            'fresh_source_ref': b.ref(b.UNIT / 'fresh-source-stdout.txt'),
            'fresh_source_posture_ref': b.ref(b.UNIT / 'fresh-source-posture-stdout.txt')},
        'criterion_results': [
            {'criterion': 'Exact source clauses and logical roles', 'result': 'PASS for character accounting; fidelity pending',
             'evidence': '21 units,23 clauses:4 encoded,6 explanatory,13 deferred. Five unresolved source findings retained.'},
            {'criterion': 'Types, assumptions, populations and dependencies', 'result': 'PARTIAL',
             'evidence': '24 declarations; zero selected assumptions;13 required and11 unresolved populations. Ten direct edges, three transitive Definition edges, eleven missing counterpart packets and independently unreviewed edge denominator.'},
            {'criterion': 'Examples and counterexamples', 'result': 'PASS for exact authored candidate structures',
             'evidence': '36 denotation controls and7 separate non-entailment query outcomes. Required metadata, inclusive content, permitted abstract overlap, subject binding and malformed structures checked. No native-provider search or unbounded proof.'},
            {'criterion': 'Actual selected source implementation conditions', 'result': 'PASS for one exact record',
             'evidence': 'Nine schema/digest/render/proposed-current lookup checks and fresh replay; two renders match existing4501-byte projection.'},
            {'criterion': 'Whole-source faithful translation and owner review', 'result': 'UNRESOLVED',
             'evidence': 'Thirteen deferred clauses, eleven population policies, full carrier/membership semantics, universal consumer/use contracts, source-posture mapping, dependency closure and attributable owner review remain open.'},
            {'criterion': 'Currentness and preservation', 'result': 'PASS',
             'evidence': 'All201 selected source/registry/provenance files current;746 prior sealed candidate files preserved. Failed sort-schema authoring and superseded pre-provenance-review draft retained.'}],
        'preserved_attempts': [
            {'path': 'attempt-001-sort-schema', 'result': 'FAIL', 'cause': 'Sort declaration used wrong schema field; domain_policy corrected before successful publication.'},
            {'path': 'attempt-002-before-source-posture-review', 'result': 'superseded-unsealed-draft', 'cause': 'Historical source posture and current admission comparison added as GM-SOURCE-005.'}],
        'review_disposition': {'kind': 'candidate-agent-self-review', 'reviewer': 'agent:Codex',
            'result': 'Typed static draft and exact controls accepted as candidate progress only; whole translation, owner fidelity, closure and proof unresolved.'},
        'source_binding_check': source, 'coverage_row_ref': b.ref(b.UNIT / 'coverage-row.json'),
        'whole_definition_translation': 'pending', 'source_fidelity': 'pending',
        'semantic_ready': False, 'mechanized_proof': False,
        'next_independent_unit': 'F01-T.cal.definition.hypothesis',
        'full_project_completion': 'not-established'}
    b.put('receipt.json', receipt)
    files = [b.ref(path) for folder in [b.BASE, b.IMPL] for path in sorted(folder.rglob('*'))
             if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('delivery-manifest.json', {
        'schema_version': 'definition-assurance-delivery-manifest/v1-candidate',
        'authority_effect': 'none', 'files': sorted(files, key=lambda row: row['path']),
        'claim_ceiling': 'Exact preserved candidate bytes and verified partial Governed Model draft. No whole owner-accepted translation, admitted carrier/instance, consumer compliance, universal use coverage, unbounded proof or episode completion.'})
    print(json.dumps({'result': 'PARTIAL-DRAFT-VERIFIED', 'candidate_files': len(files),
        'prior_candidate_files_preserved': 746, 'source_files_current': 201, **counts,
        'actual_source_checks': 9, 'whole_translation': 'pending', 'goal_status': 'active',
        'next_independent_unit': 'F01-T.cal.definition.hypothesis'}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
