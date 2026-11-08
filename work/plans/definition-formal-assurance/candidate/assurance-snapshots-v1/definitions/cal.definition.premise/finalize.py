"""Seal exact partial Premise evidence while preserving conditional-inference boundaries."""
import json
import build_candidate as b
import verifier as v


def load(name): return json.loads((b.UNIT / name).read_bytes())
def unchanged(refs):
    for ref in refs:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Changed bound bytes: ' + ref['path'])


def main():
    context = load('context.json'); unchanged(context['sources']); b.external_current(context)
    prior = json.loads((b.BASE / 'definitions/cal.definition.invariant/delivery-manifest.json').read_bytes()); unchanged(prior['files'])
    for name in ['A04', 'C01', 'E02']:
        upstream = json.loads((b.BASE / f'units/{name}/receipt.json').read_bytes()); unchanged(upstream['inputs'] + upstream['outputs'])
    model = load('model-controls.json'); fresh = load('fresh-model-stdout.txt'); core = load('t.json')['payload']; packet = load('correspondence.json')
    graph = load('dependency-graph.json'); source_checks = load('source-checks.json'); reasoning = load('reasoning-checks.json')
    counts = {'controls': 32, 'nonentailment_query_outcomes': 4, 'source_units': 24, 'mapped_clauses': 40,
        'encoded_clauses': 9, 'deferred_clauses': 22, 'required_populations': 8, 'unresolved_populations': 9}
    if any(fresh[key] != value for key, value in counts.items()) or fresh['result'] != model['status'] or model['control_count'] != 32 or len(core['declarations']) != 26:
        raise ValueError('Wrong model/type/replay denominator')
    for name in ['contract-check-stdout.txt', 'reasoning-contract-stdout.txt']:
        if load(name)['status'] != 'structurally-valid': raise ValueError('Declared input contract failed')
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (19, 30, 14):
        raise ValueError('Wrong dependency denominator')
    if load('fresh-dependency-stdout.txt')['result'] != 'PASS-for-exact-authored-and-transitive-uses' or graph['edge_denominator'] != 'requires-independent-review':
        raise ValueError('Dependency replay or denominator review ceiling missing')
    if len(graph['cycle_reviews']) != 1 or len(graph['cycle_reviews'][0]['members']) != 4 or graph['cycle_reviews'][0]['disposition'] != 'unresolved-cycle-classification':
        raise ValueError('Four-definition mutual references require cycle review')
    if len(source_checks['checks']) != 13 or not all(x['result'] is True for x in source_checks['checks']) or load('fresh-source-stdout.txt')['result'] != source_checks['status']:
        raise ValueError('Actual source checks/fresh replay required')
    if not source_checks['source_testable_conditions'][1]['result'].startswith('PARTIAL:') or source_checks['source_location']['repository_identity_authenticated'] is not False:
        raise ValueError('Local bytes cannot certify registered source currentness')
    if load('fresh-reasoning-stdout.txt')['result'] != reasoning['status'] or reasoning['boolean_rows'] != 4 or reasoning['rows_satisfying_synthetic_conditional_premises'] != 1:
        raise ValueError('Wrong conditional reasoning denominator/replay')
    selection = load('reasoning-selection.json'); interface = load('reasoning-interface-input.json')['payload']
    if reasoning['actual_content_or_assumptions_selected'] is not False or selection['primary_theory_extended_with_content_premises'] is not False or selection['actual_project_content_binding'] is not None:
        raise ValueError('Synthetic content treated as actual source assumptions')
    if not b.r.same_json(interface['clauses'], core['clauses']) or not b.r.same_json(interface['populations'], core['populations']) or interface['assumptions']:
        raise ValueError('Reasoning interface changed primary theory')
    if len(packet['source_precedence']['conflicts']) != 5 or core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending':
        raise ValueError('Findings omitted or assumption/fidelity fabricated')
    for evidence in [model, reasoning]:
        if evidence['semantic_ready'] is not False or evidence['mechanized_proof'] is not False: raise ValueError('False readiness/proof acceptance')
        unchanged(evidence['input_refs'] + evidence['checker_bindings'])
        if evidence['runtime_bindings'] != v.f.current_bindings(): raise ValueError('Runtime drift')
    unchanged(list(source_checks['selected_inputs'].values()))
    for stem in ['build', 'model-check', 'source-check', 'dependency-check', 'reasoning-check', 'contract-check', 'reasoning-contract', 'fresh-model', 'fresh-source', 'fresh-dependency', 'fresh-reasoning']:
        if (b.UNIT / (stem + '-stderr.txt')).read_bytes(): raise ValueError('Unresolved execution failure: ' + stem)
    if not (b.UNIT / 'REVIEW.md').is_file(): raise ValueError('Detailed aspect review missing')
    b.external_current(context); source = b.r.verify(b.snapshot(), b.ROOT)
    if source['files'] != 201 or len(prior['files']) != 925: raise ValueError('Wrong currentness/predecessor denominator')
    b.put('episode-status.json', {'authority_effect': 'none', 'goal_status': 'active', 'latest_candidate_draft': 'F01-T.cal.definition.premise',
        'phase_result': 'partial-contextual-working-role-draft-verified; whole fidelity and lifecycle unresolved',
        'current_definitions': 183, 'admitted_source_versions': 189,
        'per_definition_T_candidate_drafts': len(list((b.BASE / 'definitions').glob('*/t.json'))),
        'new_source_units_accounted': 24, 'new_clauses_accounted': 40, 'new_static_clauses_encoded': 9,
        'premise_deferred_clauses': 22, 'premise_unresolved_population_policies': 9, 'missing_transitive_dependency_packets': 14,
        'unresolved_semantic_cycle': ['cal.definition.axiom', 'cal.definition.hypothesis', 'cal.definition.invariant', 'cal.definition.premise'],
        'canonical_legacy_source_currentness': 'not-established; bound local copy only',
        'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0,
        'source_files_current': 201, 'external_selected_local_files_current': 1, 'prior_candidate_files_preserved': 925,
        'next_independent_unit': 'F01-T.cal.definition.schema', 'remaining_foundations_family': ['cal.definition.schema', 'cal.definition.semantic-primitive'],
        'full_project_completion': 'not-established'})
    b.put('coverage-row.json', {'authority_effect': 'none', 'definition_id': core['source']['definition_id'], 'source': core['source'],
        'interpretation_ref': b.ref(b.UNIT / 't.json'), 'correspondence_ref': b.ref(b.UNIT / 'correspondence.json'),
        'static_ir_ref': b.ref(b.UNIT / 'static-ir.json'), 'review_ref': b.ref(b.UNIT / 'REVIEW.md'),
        'model_evidence_ref': b.ref(b.UNIT / 'model-controls.json'), 'source_checks_ref': b.ref(b.UNIT / 'source-checks.json'),
        'reasoning_selection_ref': b.ref(b.UNIT / 'reasoning-selection.json'), 'reasoning_evidence_ref': b.ref(b.UNIT / 'reasoning-checks.json'),
        'dependency_graph_ref': b.ref(b.UNIT / 'dependency-graph.json'),
        'logical_status': 'typed-static-contextual-working-role-and-carried-metadata-draft',
        'character_accounting_complete': True, 'source_units': 24, 'mapped_clauses': 40, 'encoded_clauses': 9,
        'explanatory_clauses': 9, 'deferred_clauses': 22, 'required_populations': 8, 'unresolved_populations': 9, 'direct_semantic_uses': 7,
        'synthetic_reasoning_assumptions_added_to_primary_T': False, 'actual_proposition_truth_or_lifecycle': 'not-established',
        'semantic_closure': 'unresolved-four-definition-cycle-review-and-fourteen-missing-counterpart-packets',
        'canonical_legacy_source_currentness': 'not-established; declared producer file absent',
        'source_fidelity': 'pending', 'semantic_ready': False, 'whole_definition_translation': 'pending', 'whole_definition_proof': None,
        'owner_review': {'status': 'pending', 'source_owner_ref': 'role:definition-owner', 'owner_principal_ref': None, 'decision_ref': None,
            'findings': [x['finding_id'] for x in packet['source_precedence']['conflicts']]}})
    outputs = [b.ref(path) for path in sorted(b.UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('receipt.json', {'schema_version': 'definition-assurance-unit-receipt/v1-candidate', 'unit_id': 'F01-T.cal.definition.premise',
        'authority_effect': 'none', 'goal_status': 'active',
        'task_result': 'PARTIAL: exact source-accounted contextual working-role/metadata slice and separate conditional illustration verified; whole fidelity, closure, semantic cycle, population policies, lifecycle and live legacy-source currentness unresolved',
        'inputs': context['sources'], 'external_inputs': context['external_sources'], 'outputs': outputs,
        'validation': {'model_controls': 32, 'nonentailment_query_outcomes': 4, 'conditional_boolean_rows': 4,
            'rows_satisfying_synthetic_conditional_premises': 1, 'actual_bounded_source_checks': 13,
            'primary_content_assumptions_added': False, 'actual_content_or_assumptions_selected': False,
            'declared_input_contracts': 'PASS', 'fresh_model_replay': 'PASS', 'fresh_dependency_replay': 'PASS',
            'fresh_source_replay': 'PASS', 'fresh_reasoning_replay': 'PASS', 'source_currentness': '201 captured local files plus 1 exact selected external file',
            'canonical_legacy_source_currentness': 'PARTIAL: declared producer file absent; selected mirror bytes match', 'prior_candidate_files_preserved': 925},
        'criterion_results': [
            {'criterion': 'Exact source clauses and proposed signature', 'result': 'PARTIAL', 'evidence': '24 units,40 spans,9 encoded,9 explanatory,22 deferred;26 declarations; owner fidelity pending.'},
            {'criterion': 'Adoption, truth, commitment and investigation', 'result': 'PASS for authored countermodel', 'evidence': 'Four targets outside T fail while T/I hold; actual truth, typical status values or Hypothesis membership are not inferred.'},
            {'criterion': 'Conditional reasoning', 'result': 'PASS for exact method illustration', 'evidence': 'Four Boolean rows; one satisfies both hypothetical premises; unconditional consequence has a countermodel. No actual proposition or assumption set selected.'},
            {'criterion': 'Metadata and lifecycle', 'result': 'PARTIAL', 'evidence': 'Four carried metadata relations checked for presence and correct role binding; schema, uniqueness, guards, routes and actual lifecycle remain open.'},
            {'criterion': 'Semantic closure', 'result': 'PARTIAL', 'evidence': '19 nodes,30 edges,14 missing counterparts; Axiom/Hypothesis/Invariant/Premise cycle remains unclassified.'},
            {'criterion': 'Source, schema and projection', 'result': 'PARTIAL', 'evidence': '13 bounded artifact/local section/admission/sibling checks pass; declared live producer unavailable.'},
            {'criterion': 'Selected source and predecessor preservation', 'result': 'PASS for selected bytes', 'evidence': '201 captured files,1 selected local external file and925 preceding sealed files rechecked.'}],
        'preserved_attempts': [], 'review_disposition': {'kind': 'candidate-agent-self-review', 'reviewer': 'agent:Codex',
            'result': 'Exact partial evidence verified; no owner fidelity, actual proposition truth, lifecycle or whole translation accepted.'},
        'source_binding_check': source, 'coverage_row_ref': b.ref(b.UNIT / 'coverage-row.json'),
        'whole_definition_translation': 'pending', 'source_fidelity': 'pending', 'semantic_ready': False, 'mechanized_proof': False,
        'next_independent_unit': 'F01-T.cal.definition.schema', 'full_project_completion': 'not-established'})
    files = [b.ref(path) for folder in [b.BASE, b.IMPL] for path in sorted(folder.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('delivery-manifest.json', {'schema_version': 'definition-assurance-delivery-manifest/v1-candidate', 'authority_effect': 'none',
        'files': sorted(files, key=lambda x: x['path']),
        'claim_ceiling': 'Exact preserved candidate bytes, partial Premise working-role/metadata slice and conditional method illustration. No whole fidelity, selected actual proposition/premises, world truth, lifecycle, resolved semantic cycle, live producer currentness, unbounded theorem or episode completion.'})
    print(json.dumps({'result': 'PARTIAL-DRAFT-VERIFIED', 'candidate_files': len(files), 'prior_candidate_files_preserved': 925,
        'source_files_current': 201, 'external_selected_local_files_current': 1, **counts, 'conditional_boolean_rows': 4,
        'actual_bounded_source_checks': 13, 'primary_content_assumptions_added': False, 'whole_translation': 'pending',
        'goal_status': 'active', 'next_independent_unit': 'F01-T.cal.definition.schema'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
