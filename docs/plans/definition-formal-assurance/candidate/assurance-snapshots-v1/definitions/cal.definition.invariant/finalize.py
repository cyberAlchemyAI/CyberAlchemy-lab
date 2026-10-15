"""Seal exact partial Invariant evidence without promoting satisfaction or owner fidelity."""
import json
import build_candidate as b
import verifier as v


def load(name): return json.loads((b.UNIT / name).read_bytes())
def unchanged(refs):
    for ref in refs:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Changed bound bytes: ' + ref['path'])


def main():
    context = load('context.json'); unchanged(context['sources']); b.external_current(context)
    prior = json.loads((b.BASE / 'definitions/cal.definition.hypothesis/delivery-manifest.json').read_bytes()); unchanged(prior['files'])
    for name in ['A04', 'C01', 'E02']:
        upstream = json.loads((b.BASE / f'units/{name}/receipt.json').read_bytes()); unchanged(upstream['inputs'] + upstream['outputs'])
    model = load('model-controls.json'); fresh = load('fresh-model-stdout.txt')
    packet = load('correspondence.json'); core = load('t.json')['payload']; graph = load('dependency-graph.json')
    source_checks = load('source-checks.json'); scenarios = load('scenario-checks.json')
    counts = {'controls': 32, 'nonentailment_query_outcomes': 2, 'source_units': 22, 'mapped_clauses': 38,
        'encoded_clauses': 11, 'deferred_clauses': 18, 'required_populations': 5, 'unresolved_populations': 9}
    if any(fresh[key] != value for key, value in counts.items()) or fresh['result'] != model['status']:
        raise ValueError('Wrong model replay/denominator')
    if model['control_count'] != 32 or len(core['declarations']) != 26: raise ValueError('Wrong model/type denominator')
    for name in ['contract-check-stdout.txt', 'scenario-contract-stdout.txt']:
        if load(name)['status'] != 'structurally-valid': raise ValueError('Declared input contract failed')
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (13, 15, 10):
        raise ValueError('Wrong dependency denominator')
    if load('fresh-dependency-stdout.txt')['result'] != 'PASS-for-exact-authored-and-transitive-uses' or graph['edge_denominator'] != 'requires-independent-review':
        raise ValueError('Dependency replay/independent review ceiling missing')
    if len(graph['cycle_reviews']) != 1 or graph['cycle_reviews'][0]['disposition'] != 'unresolved-cycle-classification':
        raise ValueError('Mutual Axiom/Invariant references require cycle review')
    if len(source_checks['checks']) != 12 or not all(x['result'] is True for x in source_checks['checks']) or load('fresh-source-stdout.txt')['result'] != source_checks['status']:
        raise ValueError('Actual source checks/fresh replay required')
    if not source_checks['source_testable_conditions'][1]['result'].startswith('PARTIAL:') or source_checks['source_location']['repository_identity_authenticated'] is not False:
        raise ValueError('Local bytes cannot certify live source currentness')
    scenario_fresh = load('fresh-scenario-stdout.txt'); interface = load('scenario-interface-input.json')['payload']
    if scenario_fresh['result'] != scenarios['status'] or scenarios['scenario_count'] != 6 or scenarios['valid_synthetic_profiles'] != 4 or scenarios['invalid_synthetic_profiles'] != 2:
        raise ValueError('Wrong operational example/profile denominator')
    if scenarios['targets_assembled_into_primary_T'] is not False or load('scenario-selection.json')['targets_are_premises'] is not False:
        raise ValueError('Proof targets assumed')
    if not b.r.same_json(interface['clauses'], core['clauses']) or not b.r.same_json(interface['populations'], core['populations']) or interface['assumptions']:
        raise ValueError('Auxiliary signature changed primary theory')
    if len(packet['source_precedence']['conflicts']) != 5 or core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending':
        raise ValueError('Findings omitted or assumption/fidelity fabricated')
    for evidence in [model, scenarios]:
        if evidence['semantic_ready'] is not False or evidence['mechanized_proof'] is not False: raise ValueError('False readiness/proof acceptance')
        unchanged(evidence['input_refs'] + evidence['checker_bindings'])
        if evidence['runtime_bindings'] != v.f.current_bindings(): raise ValueError('Runtime drift')
    unchanged(list(source_checks['selected_inputs'].values()))
    for stem in ['build', 'model-check', 'source-check', 'dependency-check', 'scenario-check', 'contract-check', 'scenario-contract', 'fresh-model', 'fresh-source', 'fresh-dependency', 'fresh-scenario']:
        if (b.UNIT / (stem + '-stderr.txt')).read_bytes(): raise ValueError('Unresolved execution failure: ' + stem)
    if not (b.UNIT / 'REVIEW.md').is_file(): raise ValueError('Detailed aspect review missing')
    b.external_current(context); source = b.r.verify(b.snapshot(), b.ROOT)
    if source['files'] != 201 or len(prior['files']) != 869: raise ValueError('Wrong currentness/predecessor denominator')
    b.put('episode-status.json', {'authority_effect': 'none', 'goal_status': 'active', 'latest_candidate_draft': 'F01-T.cal.definition.invariant',
        'phase_result': 'partial-requirement-draft-verified; whole-source fidelity and actual preservation unresolved',
        'current_definitions': 183, 'admitted_source_versions': 189,
        'per_definition_T_candidate_drafts': len(list((b.BASE / 'definitions').glob('*/t.json'))),
        'new_source_units_accounted': 22, 'new_clauses_accounted': 38, 'new_static_clauses_encoded': 11,
        'invariant_deferred_clauses': 18, 'invariant_unresolved_population_policies': 9, 'missing_transitive_dependency_packets': 10,
        'unresolved_semantic_cycle': ['cal.definition.axiom', 'cal.definition.invariant'],
        'canonical_legacy_source_currentness': 'not-established; bound local copy only',
        'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0,
        'source_files_current': 201, 'external_selected_local_files_current': 1, 'prior_candidate_files_preserved': 869,
        'next_independent_unit': 'F01-T.cal.definition.premise',
        'remaining_foundations_family': ['cal.definition.premise', 'cal.definition.schema', 'cal.definition.semantic-primitive'],
        'full_project_completion': 'not-established'})
    b.put('coverage-row.json', {'authority_effect': 'none', 'definition_id': core['source']['definition_id'], 'source': core['source'],
        'interpretation_ref': b.ref(b.UNIT / 't.json'), 'correspondence_ref': b.ref(b.UNIT / 'correspondence.json'),
        'static_ir_ref': b.ref(b.UNIT / 'static-ir.json'), 'review_ref': b.ref(b.UNIT / 'REVIEW.md'),
        'model_evidence_ref': b.ref(b.UNIT / 'model-controls.json'), 'source_checks_ref': b.ref(b.UNIT / 'source-checks.json'),
        'scenario_selection_ref': b.ref(b.UNIT / 'scenario-selection.json'), 'scenario_evidence_ref': b.ref(b.UNIT / 'scenario-checks.json'),
        'dependency_graph_ref': b.ref(b.UNIT / 'dependency-graph.json'),
        'logical_status': 'typed-static-requirement-and-scoped-breach-draft-with-separate-operational-targets',
        'character_accounting_complete': True, 'source_units': 22, 'mapped_clauses': 38, 'encoded_clauses': 11,
        'explanatory_clauses': 9, 'deferred_clauses': 18, 'required_populations': 5, 'unresolved_populations': 9, 'direct_semantic_uses': 8,
        'scenario_targets_assumed_in_T': False, 'actual_implementation_preservation': 'not-established',
        'semantic_closure': 'unresolved-ten-missing-counterpart-packets-and-Axiom-Invariant-cycle-review',
        'canonical_legacy_source_currentness': 'not-established; declared producer file absent',
        'source_fidelity': 'pending', 'semantic_ready': False, 'whole_definition_translation': 'pending', 'whole_definition_proof': None,
        'owner_review': {'status': 'pending', 'source_owner_ref': 'role:definition-owner', 'owner_principal_ref': None, 'decision_ref': None,
            'findings': [x['finding_id'] for x in packet['source_precedence']['conflicts']]}})
    outputs = [b.ref(path) for path in sorted(b.UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('receipt.json', {'schema_version': 'definition-assurance-unit-receipt/v1-candidate', 'unit_id': 'F01-T.cal.definition.invariant',
        'authority_effect': 'none', 'goal_status': 'active',
        'task_result': 'PARTIAL: exact source-accounted typed requirement/breach slice and separate finite targets verified; whole fidelity, closure, semantic cycle, population policies, actual preservation and canonical legacy-source currentness unresolved',
        'inputs': context['sources'], 'external_inputs': context['external_sources'], 'outputs': outputs,
        'validation': {'model_controls': 32, 'nonentailment_query_outcomes': 2, 'finite_authored_scenarios': 6,
            'valid_synthetic_profiles': 4, 'invalid_synthetic_profiles': 2, 'actual_bounded_source_checks': 12,
            'scenario_targets_assembled_into_primary_T': False, 'actual_implementation_checked': False,
            'declared_input_contracts': 'PASS', 'fresh_model_replay': 'PASS', 'fresh_dependency_replay': 'PASS',
            'fresh_source_replay': 'PASS', 'fresh_scenario_replay': 'PASS', 'source_currentness': '201 captured local files plus 1 exact selected external file',
            'canonical_legacy_source_currentness': 'PARTIAL: declared producer file absent; selected mirror bytes match',
            'prior_candidate_files_preserved': 869},
        'criterion_results': [
            {'criterion': 'Exact source clauses and proposed signature', 'result': 'PARTIAL', 'evidence': '22 units,38 spans,11 encoded,9 explanatory,18 deferred;26 declarations; owner fidelity pending.'},
            {'criterion': 'Requirement versus satisfaction and governance', 'result': 'PASS for authored countermodels', 'evidence': 'Two targets outside T fail while T and required populations hold; neither actual satisfaction nor authority is inferred.'},
            {'criterion': 'Operational preservation', 'result': 'PARTIAL', 'evidence': 'Six authored finite scenarios with independently traversed graphs; no actual program or unbounded proof.'},
            {'criterion': 'Semantic closure', 'result': 'PARTIAL', 'evidence': '13 nodes,15 declared edges,10 missing counterparts and unresolved Axiom/Invariant mutual-reference classification.'},
            {'criterion': 'Source, schema and projection', 'result': 'PARTIAL', 'evidence': '12 bounded checks pass for selected artifact/local section/admission; declared live producer unavailable.'},
            {'criterion': 'Selected source and predecessor preservation', 'result': 'PASS for selected bytes', 'evidence': '201 captured files,1 selected local external file and869 preceding sealed files rechecked.'}],
        'preserved_attempts': [{'path': 'attempt-001-scenario-interface-empty-clauses', 'result': 'FAIL-before-evidence-write',
            'cause': 'Closed contract required nonempty clauses; corrected interface retains exact primary clauses/populations and extends only the auxiliary signature.'}],
        'review_disposition': {'kind': 'candidate-agent-self-review', 'reviewer': 'agent:Codex', 'result': 'Exact partial evidence verified; no owner fidelity, operational preservation theorem or whole translation accepted.'},
        'source_binding_check': source, 'coverage_row_ref': b.ref(b.UNIT / 'coverage-row.json'),
        'whole_definition_translation': 'pending', 'source_fidelity': 'pending', 'semantic_ready': False, 'mechanized_proof': False,
        'next_independent_unit': 'F01-T.cal.definition.premise', 'full_project_completion': 'not-established'})
    files = [b.ref(path) for folder in [b.BASE, b.IMPL] for path in sorted(folder.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('delivery-manifest.json', {'schema_version': 'definition-assurance-delivery-manifest/v1-candidate', 'authority_effect': 'none',
        'files': sorted(files, key=lambda x: x['path']),
        'claim_ceiling': 'Exact preserved candidate bytes, partial Invariant requirement/breach slice and finite authored scenarios only. No whole fidelity, admitted role alignment, resolved semantic cycle, live producer currentness, implementation/deontic/temporal theorem or episode completion.'})
    print(json.dumps({'result': 'PARTIAL-DRAFT-VERIFIED', 'candidate_files': len(files), 'prior_candidate_files_preserved': 869,
        'source_files_current': 201, 'external_selected_local_files_current': 1, **counts,
        'finite_authored_scenarios': 6, 'actual_bounded_source_checks': 12, 'scenario_targets_assembled_into_primary_T': False,
        'whole_translation': 'pending', 'goal_status': 'active', 'next_independent_unit': 'F01-T.cal.definition.premise'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
