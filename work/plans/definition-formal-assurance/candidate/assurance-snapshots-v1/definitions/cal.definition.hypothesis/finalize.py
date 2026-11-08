"""Seal partial Hypothesis evidence; inherited comparison and live-source limit remain explicit."""
import json
import build_candidate as b
import verifier as v


def load(name): return json.loads((b.UNIT / name).read_bytes())
def unchanged(refs):
    for ref in refs:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Changed bound bytes: ' + ref['path'])


def main():
    context = load('context.json'); unchanged(context['sources']); b.external_current(context)
    prior = json.loads((b.BASE / 'definitions/cal.definition.governed-model/delivery-manifest.json').read_bytes())
    unchanged(prior['files'])
    for name in ['A04', 'C01', 'E02']:
        upstream = json.loads((b.BASE / f'units/{name}/receipt.json').read_bytes())
        unchanged(upstream['inputs'] + upstream['outputs'])
    model = load('model-controls.json'); fresh = load('fresh-model-stdout.txt')
    packet = load('correspondence.json'); core = load('t.json')['payload']
    graph = load('dependency-graph.json'); fresh_graph = load('fresh-dependency-stdout.txt')
    source_checks = load('source-checks.json'); fresh_source = load('fresh-source-stdout.txt')
    counts = {'controls': 34, 'nonentailment_query_outcomes': 4, 'source_units': 24,
        'mapped_clauses': 41, 'encoded_clauses': 1, 'deferred_clauses': 31,
        'required_populations': 5, 'unresolved_populations': 7, 'separate_comparison_clauses': 4}
    if any(fresh[key] != value for key, value in counts.items()) or fresh['result'] != model['status']:
        raise ValueError('Wrong model/slice replay or denominator')
    if model['control_count'] != 34 or len(core['declarations']) != 27:
        raise ValueError('Wrong model/type denominator')
    for name in ['contract-check-stdout.txt', 'comparison-contract-stdout.txt']:
        if load(name)['status'] != 'structurally-valid': raise ValueError('Declared input contract failed')
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (13, 15, 10):
        raise ValueError('Wrong authored/transitive closure denominator')
    if fresh_graph['result'] != 'PASS-for-exact-authored-and-transitive-uses' or graph['edge_denominator'] != 'requires-independent-review':
        raise ValueError('Dependency replay/independent-review ceiling missing')
    if len(source_checks['checks']) != 13 or not all(x['result'] is True for x in source_checks['checks']) or fresh_source['result'] != source_checks['status']:
        raise ValueError('Actual source checks/fresh replay required')
    if not source_checks['source_testable_conditions'][1]['result'].startswith('PARTIAL:') or source_checks['source_location']['repository_identity_authenticated'] is not False:
        raise ValueError('Local bytes cannot certify registered/canonical legacy-source currentness')
    selection = load('comparison-selection.json')
    if model['comparison_assembled_into_primary_T'] is not False or selection['assembled_into_primary_T'] is not False:
        raise ValueError('Inherited Premise silently assembled into Hypothesis T')
    if set(model['encoded_clause_ids']) & set(model['separate_comparison_clause_ids']):
        raise ValueError('Primary and comparison source selections overlap')
    if len(packet['source_precedence']['conflicts']) != 5 or 'FID-HYP-001' not in {x['finding_id'] for x in packet['source_precedence']['conflicts']}:
        raise ValueError('Source conflict omitted')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending' or model['semantic_ready'] is not False or model['mechanized_proof'] is not False:
        raise ValueError('False adopted assumption, fidelity or proof promotion')
    unchanged(model['input_refs'] + model['checker_bindings'] + list(source_checks['selected_inputs'].values()))
    if model['runtime_bindings'] != v.f.current_bindings(): raise ValueError('Closing runtime drift')
    for stem in ['build', 'model-check', 'source-check', 'dependency-check', 'contract-check', 'comparison-contract', 'fresh-model', 'fresh-source', 'fresh-dependency']:
        if (b.UNIT / (stem + '-stderr.txt')).read_bytes(): raise ValueError('Unresolved execution failure: ' + stem)
    if not (b.UNIT / 'REVIEW.md').is_file(): raise ValueError('Detailed aspect review missing')
    b.external_current(context); source = b.r.verify(b.snapshot(), b.ROOT)
    if source['files'] != 201 or len(prior['files']) != 811: raise ValueError('Wrong currentness/predecessor denominator')
    b.put('episode-status.json', {'authority_effect': 'none', 'goal_status': 'active',
        'latest_candidate_draft': 'F01-T.cal.definition.hypothesis',
        'phase_result': 'partial-target-draft-verified; whole-source precedence/fidelity unresolved',
        'current_definitions': 183, 'admitted_source_versions': 189,
        'per_definition_T_candidate_drafts': len(list((b.BASE / 'definitions').glob('*/t.json'))),
        'new_source_units_accounted': 24, 'new_clauses_accounted': 41, 'new_static_clauses_encoded': 1,
        'hypothesis_deferred_clauses': 31, 'separate_inherited_comparison_clauses': 4,
        'hypothesis_unresolved_population_policies': 7, 'missing_transitive_dependency_packets': 10,
        'canonical_legacy_source_currentness': 'not-established; bound local copy only',
        'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0,
        'source_files_current': 201, 'external_selected_local_files_current': 1,
        'prior_candidate_files_preserved': 811,
        'next_independent_unit': 'F01-T.cal.definition.invariant',
        'remaining_foundations_family': ['cal.definition.invariant', 'cal.definition.premise', 'cal.definition.schema', 'cal.definition.semantic-primitive'],
        'full_project_completion': 'not-established'})
    b.put('coverage-row.json', {'authority_effect': 'none', 'definition_id': core['source']['definition_id'], 'source': core['source'],
        'interpretation_ref': b.ref(b.UNIT / 't.json'), 'correspondence_ref': b.ref(b.UNIT / 'correspondence.json'),
        'static_ir_ref': b.ref(b.UNIT / 'static-ir.json'), 'review_ref': b.ref(b.UNIT / 'REVIEW.md'),
        'model_evidence_ref': b.ref(b.UNIT / 'model-controls.json'), 'source_checks_ref': b.ref(b.UNIT / 'source-checks.json'),
        'comparison_selection_ref': b.ref(b.UNIT / 'comparison-selection.json'), 'dependency_graph_ref': b.ref(b.UNIT / 'dependency-graph.json'),
        'logical_status': 'typed-static-target-necessary-condition-draft-with-separate-inherited-comparison',
        'character_accounting_complete': True, 'source_units': 24, 'mapped_clauses': 41,
        'encoded_clauses': 1, 'explanatory_clauses': 9, 'deferred_clauses': 31,
        'separate_comparison_clauses': 4, 'comparison_assembled_into_primary_T': False,
        'required_populations': 5, 'unresolved_populations': 7, 'direct_semantic_uses': 8,
        'semantic_closure': 'unresolved-ten-missing-transitive-counterpart-packets',
        'canonical_legacy_source_currentness': 'not-established; declared producer file absent',
        'source_fidelity': 'pending', 'semantic_ready': False, 'whole_definition_translation': 'pending', 'whole_definition_proof': None,
        'owner_review': {'status': 'pending', 'source_owner_ref': 'role:definition-owner', 'owner_principal_ref': None, 'decision_ref': None,
            'findings': [x['finding_id'] for x in packet['source_precedence']['conflicts']]}})
    outputs = [b.ref(path) for path in sorted(b.UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('receipt.json', {'schema_version': 'definition-assurance-unit-receipt/v1-candidate', 'unit_id': 'F01-T.cal.definition.hypothesis',
        'authority_effect': 'none', 'goal_status': 'active',
        'task_result': 'PARTIAL: exact source-accounted typed target, separate inherited comparison and bounded source/model checks verified; whole-source precedence, fidelity, closure, population policies and canonical legacy-source currentness unresolved',
        'inputs': context['sources'], 'external_inputs': context['external_sources'], 'outputs': outputs,
        'validation': {'declared_contract_command': ['python3', 'craft/formalization/candidates/definition-assurance-v1/contracts.py', 'validate', '--kind', 'interpretation', '--input', b.ref(b.UNIT / 't.json')['path']],
            'contract_result': 'structurally-valid', 'comparison_contract_result': 'structurally-valid-for-four-clause-slice',
            'model_controls': 34, 'nonentailment_query_outcomes': 4, 'separate_comparison_clauses': 4,
            'comparison_assembled_into_primary_T': False, 'actual_bounded_source_checks': 13,
            'live_legacy_source_currentness': 'not-established; partial testable condition',
            'fresh_model_ref': b.ref(b.UNIT / 'fresh-model-stdout.txt'), 'fresh_dependency_ref': b.ref(b.UNIT / 'fresh-dependency-stdout.txt'),
            'fresh_source_ref': b.ref(b.UNIT / 'fresh-source-stdout.txt')},
        'criterion_results': [
            {'criterion': 'Exact clauses, logical roles and source conflict', 'result': 'PASS for character accounting; fidelity pending', 'evidence': '24 units/41 clauses:1 primary encoded,9 explanatory,31 deferred. FID-HYP-001 and four further findings retained.'},
            {'criterion': 'Typed signature, assumptions, populations and dependencies', 'result': 'PARTIAL', 'evidence': '27 declarations; zero selected assumptions;5 required and7 unresolved populations. Eight direct and seven transitive edges; ten counterpart packets missing.'},
            {'criterion': 'Examples and counterexamples', 'result': 'PASS for exact authored candidate structures', 'evidence': '34 model controls and4 separate non-entailment query outcomes; inherited4-clause comparison independently reported outside primaryT.'},
            {'criterion': 'Actual artifact/source conditions', 'result': 'PARTIAL for live-source currentness; PASS for thirteen bounded checks', 'evidence': 'Source identity/schema and8061-byte projection checked. D55 section4648 bytes matches admitted selection and local whole-file digest. Producer path absent; live registered source currentness unproved.'},
            {'criterion': 'Whole-source faithful translation and owner review', 'result': 'UNRESOLVED', 'evidence': 'Source precedence, proposition/role/carrier mapping, primitive testability, typicality, hedge classifier, lifecycle and owner review unresolved. No actual observation/adoption/promotion.'},
            {'criterion': 'Preservation and boundary currentness', 'result': 'PASS for declared selected bytes', 'evidence': '201 captured files,1 selected local external file and811 preceding sealed candidate files rechecked; no upstream source or producer changes.'}],
        'preserved_attempts': [
            {'path': 'attempt-001-experiment-identity', 'result': 'FAIL', 'cause': 'No current cal.definition.experiment identity; inspected Experiment Design bound to declared test-condition comparison instead.'},
            {'path': 'attempt-002-before-live-source-ceiling', 'result': 'superseded-unsealed-report', 'cause': 'Made live registered source currentness explicitly partial despite matching selected local bytes.'}],
        'review_disposition': {'kind': 'candidate-agent-self-review', 'reviewer': 'agent:Codex', 'result': 'Candidate target and separate comparison/source evidence verified; no source-owner precedence, whole fidelity or proof accepted.'},
        'source_binding_check': source, 'coverage_row_ref': b.ref(b.UNIT / 'coverage-row.json'),
        'whole_definition_translation': 'pending', 'source_fidelity': 'pending', 'semantic_ready': False, 'mechanized_proof': False,
        'next_independent_unit': 'F01-T.cal.definition.invariant', 'full_project_completion': 'not-established'})
    files = [b.ref(path) for folder in [b.BASE, b.IMPL] for path in sorted(folder.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('delivery-manifest.json', {'schema_version': 'definition-assurance-delivery-manifest/v1-candidate', 'authority_effect': 'none',
        'files': sorted(files, key=lambda x: x['path']),
        'claim_ceiling': 'Exact preserved candidate bytes, partial Hypothesis target and separate inherited comparison. No whole translation, resolved source precedence, live canonical legacy-source currentness, actual observation/adoption/promotion, unbounded proof or episode completion.'})
    print(json.dumps({'result': 'PARTIAL-DRAFT-VERIFIED', 'candidate_files': len(files), 'prior_candidate_files_preserved': 811,
        'source_files_current': 201, 'external_selected_local_files_current': 1, **counts,
        'actual_bounded_source_checks': 13, 'comparison_assembled_into_primary_T': False,
        'whole_translation': 'pending', 'goal_status': 'active', 'next_independent_unit': 'F01-T.cal.definition.invariant'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
