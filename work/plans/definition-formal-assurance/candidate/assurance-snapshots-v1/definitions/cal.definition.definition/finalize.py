"""Seal partial Definition draft evidence without accepting a whole translation."""
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
    prior = json.loads((b.BASE / 'definitions/cal.definition.axiom/delivery-manifest.json').read_bytes())
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
    counts = {'controls': 49, 'nonentailment_countermodels': 4,
              'generic_metadata_model_pairs': 7, 'source_units': 23,
              'mapped_clauses': 28, 'encoded_clauses': 11, 'deferred_clauses': 10,
              'required_populations': 19, 'unresolved_populations': 16}
    if any(fresh[key] != value for key, value in counts.items()):
        raise ValueError('Wrong replay denominator')
    if fresh['result'] != model['status'] or model['control_count'] != 49:
        raise ValueError('Fresh independent model replay required')
    if contract['status'] != 'structurally-valid':
        raise ValueError('Declared contract command must pass')
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (4, 3, 3):
        raise ValueError('Wrong dependency closure denominator')
    if fresh_graph['result'] != 'PASS-for-exact-authored-uses' or graph['edge_denominator'] != 'requires-independent-review':
        raise ValueError('Dependency replay or independent-review ceiling missing')
    if len(source_checks['checks']) != 9 or not all(row['result'] is True for row in source_checks['checks']):
        raise ValueError('Nine actual source checks required')
    if fresh_source['result'] != source_checks['status'] or fresh_source['checks'] != 9:
        raise ValueError('Fresh actual-source replay required')
    unchanged(model['input_refs'] + model['checker_bindings'] + list(source_checks['selected_inputs'].values()))
    if model['runtime_bindings'] != v.f.current_bindings():
        raise ValueError('Closing runtime drift')
    for stem in ['build', 'model-check', 'dependency-check', 'contract-check',
                 'source-check', 'fresh-model', 'fresh-dependency', 'fresh-source']:
        if (b.UNIT / (stem + '-stderr.txt')).read_bytes():
            raise ValueError('Unresolved execution failure: ' + stem)
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending':
        raise ValueError('Assumption or fidelity substitution')
    if model['semantic_ready'] is not False or model['mechanized_proof'] is not False:
        raise ValueError('False semantic/proof promotion')
    if not (b.UNIT / 'REVIEW.md').is_file():
        raise ValueError('Detailed aspect review missing')
    source = b.r.verify(b.snapshot(), b.ROOT)
    if source['files'] != 201 or len(prior['files']) != 662:
        raise ValueError('Wrong source or predecessor denominator')
    episode = {
        'authority_effect': 'none', 'goal_status': 'active',
        'latest_candidate_draft': 'F01-T.cal.definition.definition',
        'phase_result': 'partial-draft-verified; whole translation unresolved',
        'current_definitions': 183, 'admitted_source_versions': 189,
        'per_definition_T_candidate_drafts': len(list((b.BASE / 'definitions').glob('*/t.json'))),
        'new_source_units_accounted': 23, 'new_clauses_accounted': 28,
        'new_static_clauses_encoded': 11, 'definition_deferred_clauses': 10,
        'definition_unresolved_population_policies': 16,
        'definition_unresolved_dependency_packets': 3,
        'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0,
        'source_files_current': 201, 'prior_candidate_files_preserved': 662,
        'next_independent_unit': 'F01-T.cal.definition.governed-model',
        'remaining_foundations_family': ['cal.definition.governed-model', 'cal.definition.hypothesis',
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
        'dependency_graph_ref': b.ref(b.UNIT / 'dependency-graph.json'),
        'logical_status': 'typed-static-record-necessary-condition-draft',
        'character_accounting_complete': True, 'source_units': 23, 'mapped_clauses': 28,
        'encoded_clauses': 11, 'explanatory_clauses': 7, 'deferred_clauses': 10,
        'required_populations': 19, 'unresolved_populations': 16,
        'direct_semantic_uses': 3, 'semantic_closure': 'unresolved-three-missing-dependency-packets',
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
        'unit_id': 'F01-T.cal.definition.definition', 'authority_effect': 'none',
        'goal_status': 'active',
        'task_result': 'PARTIAL: exact source-accounted typed draft and model/source checks verified; whole translation, fidelity, closure and population policies unresolved',
        'inputs': context['sources'], 'outputs': outputs,
        'validation': {'declared_contract_command': ['python3',
            'craft/formalization/candidates/definition-assurance-v1/contracts.py', 'validate',
            '--kind', 'interpretation', '--input', b.ref(b.UNIT / 't.json')['path']],
            'contract_result': 'structurally-valid', 'model_controls': 49,
            'nonentailment_query_outcomes': 4, 'generic_metadata_model_pairs': 7,
            'actual_source_checks': 9,
            'fresh_model_ref': b.ref(b.UNIT / 'fresh-model-stdout.txt'),
            'fresh_dependency_ref': b.ref(b.UNIT / 'fresh-dependency-stdout.txt'),
            'fresh_source_ref': b.ref(b.UNIT / 'fresh-source-stdout.txt')},
        'criterion_results': [
            {'criterion': 'Exact source clauses and logical roles', 'result': 'PASS for character accounting; fidelity pending',
             'evidence': '23 units, 28 clauses:11 encoded,7 explanatory,10 deferred. Four unresolved source findings retained.'},
            {'criterion': 'Types, assumptions, populations and dependencies', 'result': 'PARTIAL',
             'evidence': '79 declarations; zero selected assumptions;19 required and16 unresolved populations. Three authored edges, three missing counterpart packets and independently unreviewed edge denominator.'},
            {'criterion': 'Examples and counterexamples', 'result': 'PASS for exact authored candidate structures',
             'evidence': '49 denotation controls,4 separate non-entailment query outcomes and7 generic-record pairs. No exhaustive native-provider search or unbounded proof.'},
            {'criterion': 'Actual selected source implementation conditions', 'result': 'PASS for one exact record',
             'evidence': 'Nine schema/digest/render/proposed-current lookup checks and fresh replay; two renders match existing4819-byte projection.'},
            {'criterion': 'Whole-source faithful translation and owner review', 'result': 'UNRESOLVED',
             'evidence': 'Ten deferred clauses, sixteen population policies, source discrepancies, generic canonical-axis semantics, dependency closure and attributable owner review remain open.'},
            {'criterion': 'Currentness and preservation', 'result': 'PASS',
             'evidence': 'All201 selected source/registry/provenance files current;662 prior sealed candidate files preserved. Five earlier attempts retained.'}],
        'preserved_attempts': [
            {'path': 'attempt-001-diagnostic', 'result': 'FAIL', 'cause': 'Wrong expected diagnostic corrected to ill-sorted-function-result.'},
            {'path': 'attempt-002-index-columns', 'result': 'FAIL', 'cause': 'Proposed and current index column layouts differ; header-driven exact row check added.'},
            {'path': 'attempt-003-before-exclusion-completion', 'result': 'superseded-unsealed-draft', 'cause': 'Standalone summary/hint exclusions made explicit.'},
            {'path': 'attempt-004-before-completeness-subtype', 'result': 'superseded-unsealed-draft', 'cause': 'Complete subtype, entailed attribute populations and Definition-restricted query domains made explicit.'},
            {'path': 'attempt-005-authoring-quote', 'result': 'FAIL', 'cause': 'Syntax error in rationale quotation corrected before final generation.'}],
        'review_disposition': {'kind': 'candidate-agent-self-review', 'reviewer': 'agent:Codex',
            'result': 'Typed static draft and exact controls accepted as candidate progress only; whole translation, owner fidelity, closure and proof unresolved.'},
        'source_binding_check': source, 'coverage_row_ref': b.ref(b.UNIT / 'coverage-row.json'),
        'whole_definition_translation': 'pending', 'source_fidelity': 'pending',
        'semantic_ready': False, 'mechanized_proof': False,
        'next_independent_unit': 'F01-T.cal.definition.governed-model',
        'full_project_completion': 'not-established'}
    b.put('receipt.json', receipt)
    files = [b.ref(path) for folder in [b.BASE, b.IMPL] for path in sorted(folder.rglob('*'))
             if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('delivery-manifest.json', {
        'schema_version': 'definition-assurance-delivery-manifest/v1-candidate',
        'authority_effect': 'none', 'files': sorted(files, key=lambda row: row['path']),
        'claim_ceiling': 'Exact preserved candidate bytes and verified partial Definition draft. No whole owner-accepted translation, canonical axis independence, unbounded proof or episode completion.'})
    print(json.dumps({'result': 'PARTIAL-DRAFT-VERIFIED', 'candidate_files': len(files),
        'prior_candidate_files_preserved': 662, 'source_files_current': 201, **counts,
        'actual_source_checks': 9, 'whole_translation': 'pending', 'goal_status': 'active',
        'next_independent_unit': 'F01-T.cal.definition.governed-model'}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
