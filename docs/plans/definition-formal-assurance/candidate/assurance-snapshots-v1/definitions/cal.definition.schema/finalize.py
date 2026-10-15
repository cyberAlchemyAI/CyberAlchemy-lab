"""Seal exact partial Schema evidence without promoting general decidability or authority."""
import json
import build_candidate as b
import verifier as v


def load(name): return json.loads((b.UNIT / name).read_bytes())
def unchanged(refs):
    for ref in refs:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Changed bound bytes: ' + ref['path'])


def main():
    context = load('context.json'); unchanged(context['sources']); b.external_current(context)
    prior = json.loads((b.BASE / 'definitions/cal.definition.premise/delivery-manifest.json').read_bytes()); unchanged(prior['files'])
    for name in ['A04', 'C01', 'E02']:
        upstream = json.loads((b.BASE / f'units/{name}/receipt.json').read_bytes()); unchanged(upstream['inputs'] + upstream['outputs'])
    model = load('model-controls.json'); fresh = load('fresh-model-stdout.txt'); core = load('t.json')['payload']; packet = load('correspondence.json')
    graph = load('dependency-graph.json'); source_checks = load('source-checks.json'); profile = load('structural-profile-checks.json')
    counts = {'controls': 44, 'nonentailment_query_outcomes': 5, 'source_units': 22, 'mapped_clauses': 38,
        'encoded_clauses': 16, 'deferred_clauses': 13, 'required_populations': 7, 'unresolved_populations': 27}
    if any(fresh[key] != value for key, value in counts.items()) or fresh['result'] != model['status'] or model['control_count'] != 44 or len(core['declarations']) != 43:
        raise ValueError('Wrong model/type/replay denominator')
    if load('contract-check-stdout.txt')['status'] != 'structurally-valid': raise ValueError('Declared input contract failed')
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (25, 41, 19):
        raise ValueError('Wrong dependency denominator')
    if load('fresh-dependency-stdout.txt')['result'] != 'PASS-for-exact-authored-and-transitive-uses' or graph['edge_denominator'] != 'requires-independent-review':
        raise ValueError('Dependency replay or completeness review ceiling missing')
    if len(graph['cycle_reviews']) != 1 or len(graph['cycle_reviews'][0]['members']) != 4 or graph['cycle_reviews'][0]['disposition'] != 'unresolved-cycle-classification':
        raise ValueError('Mutual semantic references falsely resolved')
    if len(source_checks['checks']) != 12 or not all(x['result'] is True for x in source_checks['checks']) or load('fresh-source-stdout.txt')['result'] != source_checks['status']:
        raise ValueError('Actual source checks/fresh replay required')
    if not source_checks['source_testable_conditions'][1]['result'].startswith('PARTIAL:') or source_checks['source_location']['repository_identity_authenticated'] is not False:
        raise ValueError('Selected local bytes cannot certify live source currentness')
    profile_fresh = load('fresh-profile-stdout.txt')
    if profile_fresh['result'] != profile['status'] or profile['structural_controls'] != 18 or profile['rejected_structural_inputs'] != 5 or profile['revision_controls'] != 3 or profile['actual_schema_fixture_checks'] != 1:
        raise ValueError('Wrong finite profile/revision/fixture denominator')
    if profile['source_Conforms_to_inspector_embedding_reviewed'] is not False or profile['universal_C_N_independence_proved'] is not False or profile['subject_executed'] is not False or profile['occupants_added'] != 0:
        raise ValueError('False profile embedding, independence or execution/population claim')
    if any(x['universal_compatibility_proved'] is not False or x['semantic_preservation_proved'] is not False or x['revision_authorized'] is not False for x in profile['revision_results']):
        raise ValueError('Finite revision fixtures cannot certify general compatibility or authorize mutation')
    if profile['actual_schema_fixture']['Definition_v1_schema_valid'] is not True or profile['actual_schema_fixture']['matches_current_registered_source_bytes'] is not False or profile['actual_schema_fixture']['fixture_owner_authenticated'] is not False:
        raise ValueError('Shape fixture mistaken for admitted owner/source evidence')
    if len(packet['source_precedence']['conflicts']) != 5 or core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending':
        raise ValueError('Findings omitted or assumption/fidelity fabricated')
    unchanged(model['input_refs'])
    for evidence in [model, profile]:
        if evidence['semantic_ready'] is not False or evidence['mechanized_proof'] is not False: raise ValueError('False readiness/proof acceptance')
        unchanged(evidence['checker_bindings'])
        if evidence['runtime_bindings'] != v.f.current_bindings(): raise ValueError('Runtime drift')
    unchanged([profile['selected_actual_schema_ref'], *source_checks['selected_inputs'].values()])
    for stem in ['build', 'model-check', 'source-check', 'dependency-check', 'profile-check', 'contract-check', 'fresh-model', 'fresh-source', 'fresh-dependency', 'fresh-profile']:
        if (b.UNIT / (stem + '-stderr.txt')).read_bytes(): raise ValueError('Unresolved execution failure: ' + stem)
    if not (b.UNIT / 'REVIEW.md').is_file(): raise ValueError('Detailed aspect review missing')
    b.external_current(context); source = b.r.verify(b.snapshot(), b.ROOT)
    if source['files'] != 201 or len(prior['files']) != 977: raise ValueError('Wrong currentness/predecessor denominator')
    b.put('episode-status.json', {'authority_effect': 'none', 'goal_status': 'active', 'latest_candidate_draft': 'F01-T.cal.definition.schema',
        'phase_result': 'partial-structural-schema-draft-and-finite-inspector-verified; whole fidelity, profile embedding and general independence unresolved',
        'current_definitions': 183, 'admitted_source_versions': 189,
        'per_definition_T_candidate_drafts': len(list((b.BASE / 'definitions').glob('*/t.json'))),
        'new_source_units_accounted': 22, 'new_clauses_accounted': 38, 'new_static_clauses_encoded': 16,
        'schema_deferred_clauses': 13, 'schema_unresolved_population_policies': 27, 'missing_transitive_dependency_packets': 19,
        'canonical_legacy_source_currentness': 'not-established; bound local copy only',
        'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0,
        'source_files_current': 201, 'external_selected_local_files_current': 1, 'prior_candidate_files_preserved': 977,
        'next_independent_unit': 'F01-T.cal.definition.semantic-primitive', 'remaining_foundations_family': ['cal.definition.semantic-primitive'],
        'full_project_completion': 'not-established'})
    b.put('coverage-row.json', {'authority_effect': 'none', 'definition_id': core['source']['definition_id'], 'source': core['source'],
        'interpretation_ref': b.ref(b.UNIT / 't.json'), 'correspondence_ref': b.ref(b.UNIT / 'correspondence.json'),
        'static_ir_ref': b.ref(b.UNIT / 'static-ir.json'), 'review_ref': b.ref(b.UNIT / 'REVIEW.md'),
        'model_evidence_ref': b.ref(b.UNIT / 'model-controls.json'), 'source_checks_ref': b.ref(b.UNIT / 'source-checks.json'),
        'structural_profile_evidence_ref': b.ref(b.UNIT / 'structural-profile-checks.json'), 'dependency_graph_ref': b.ref(b.UNIT / 'dependency-graph.json'),
        'logical_status': 'typed-static-structure-components-relative-level-and-shape-evidence-draft',
        'character_accounting_complete': True, 'source_units': 22, 'mapped_clauses': 38, 'encoded_clauses': 16,
        'explanatory_clauses': 9, 'deferred_clauses': 13, 'required_populations': 7, 'unresolved_populations': 27, 'direct_semantic_uses': 11,
        'source_Conforms_to_inspector_embedding_reviewed': False, 'universal_independence_or_compatibility': 'not-established',
        'semantic_closure': 'unresolved-nineteen-counterpart-packets-and-four-definition-cycle-review',
        'canonical_legacy_source_currentness': 'not-established; declared producer file absent',
        'source_fidelity': 'pending', 'semantic_ready': False, 'whole_definition_translation': 'pending', 'whole_definition_proof': None,
        'owner_review': {'status': 'pending', 'source_owner_ref': 'role:definition-owner', 'owner_principal_ref': None, 'decision_ref': None,
            'findings': [x['finding_id'] for x in packet['source_precedence']['conflicts']]}})
    outputs = [b.ref(path) for path in sorted(b.UNIT.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('receipt.json', {'schema_version': 'definition-assurance-unit-receipt/v1-candidate', 'unit_id': 'F01-T.cal.definition.schema',
        'authority_effect': 'none', 'goal_status': 'active',
        'task_result': 'PARTIAL: exact source-accounted typed structural slice and bounded actual inspection profile verified; whole fidelity, profile embedding, role/level alignment, general independence/compatibility, populations, closure and live source currentness unresolved',
        'inputs': context['sources'], 'external_inputs': context['external_sources'], 'outputs': outputs,
        'validation': {'model_controls': 44, 'nonentailment_query_outcomes': 5, 'finite_structural_controls': 18,
            'rejected_structural_inputs': 5, 'C_N_variation_cases': 4, 'revision_controls': 3, 'actual_shape_schema_fixture_checks': 1,
            'actual_bounded_source_checks': 12, 'subject_executed': False, 'occupants_added': 0,
            'universal_compatibility_proved': False, 'profile_embedding_reviewed': False,
            'declared_input_contract': 'PASS', 'fresh_model_replay': 'PASS', 'fresh_dependency_replay': 'PASS',
            'fresh_source_replay': 'PASS', 'fresh_profile_replay': 'PASS', 'source_currentness': '201 captured local files plus1 exact selected external file',
            'canonical_legacy_source_currentness': 'PARTIAL: declared producer file absent; selected mirror bytes match', 'prior_candidate_files_preserved': 977},
        'criterion_results': [
            {'criterion': 'Exact source correspondence and signature', 'result': 'PARTIAL', 'evidence': '22 units,38 spans,16 encoded,9 explanatory,13 deferred;43 declarations; owner fidelity pending.'},
            {'criterion': 'Shape versus authority/truth/ownership/promotion/execution', 'result': 'PASS for authored countermodel and actual shape fixture', 'evidence': 'Five targets outside T fail with T/I; altered-owner Definition fixture passes actual shape schema without authenticated source/owner evidence.'},
            {'criterion': 'C/N and finite inspection', 'result': 'PARTIAL', 'evidence': '18 bounded-profile controls, including four C/N combinations, endpoint/multiplicity/path checks and5 rejected inputs; no reviewed source embedding or general independence.'},
            {'criterion': 'Schema revisions', 'result': 'PARTIAL', 'evidence': 'Three acceptance comparisons; tightening has a selected backward-preservation counterexample. No general compatibility, semantic preservation or revision authority.'},
            {'criterion': 'Semantic closure and relative levels', 'result': 'PARTIAL', 'evidence': '25 nodes,41 edges,19 missing counterparts; level hierarchy, scoped role alignment and mutual foundational references require review.'},
            {'criterion': 'Source, schema and projection', 'result': 'PARTIAL', 'evidence': '12 bounded artifact/local section/admission checks pass; declared live producer unavailable.'},
            {'criterion': 'Selected source and predecessor preservation', 'result': 'PASS for selected bytes', 'evidence': '201 captured files,1 selected local external file and977 preceding sealed files rechecked.'}],
        'preserved_attempts': [{'path': 'attempt-001-before-kind-owner-guard', 'result': 'superseded-unsealed-candidate',
            'cause': 'Added missing HasKind=>Schema owner guard and rejecting control before delivery sealing; previous code/reports/outputs preserved.'}],
        'review_disposition': {'kind': 'candidate-agent-self-review', 'reviewer': 'agent:Codex',
            'result': 'Exact partial evidence verified; no owner fidelity, general decidability/independence/compatibility, authority or whole translation accepted.'},
        'source_binding_check': source, 'coverage_row_ref': b.ref(b.UNIT / 'coverage-row.json'),
        'whole_definition_translation': 'pending', 'source_fidelity': 'pending', 'semantic_ready': False, 'mechanized_proof': False,
        'next_independent_unit': 'F01-T.cal.definition.semantic-primitive', 'full_project_completion': 'not-established'})
    files = [b.ref(path) for folder in [b.BASE, b.IMPL] for path in sorted(folder.rglob('*')) if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']
    b.put('delivery-manifest.json', {'schema_version': 'definition-assurance-delivery-manifest/v1-candidate', 'authority_effect': 'none',
        'files': sorted(files, key=lambda x: x['path']),
        'claim_ceiling': 'Exact preserved candidate bytes, partial Schema structural/relative-level slice and bounded inspection/revision fixtures only. No whole fidelity, source-profile embedding, general decidability/C-N independence/migration compatibility, hierarchy proof, authority/truth, live producer currentness or episode completion.'})
    print(json.dumps({'result': 'PARTIAL-DRAFT-VERIFIED', 'candidate_files': len(files), 'prior_candidate_files_preserved': 977,
        'source_files_current': 201, 'external_selected_local_files_current': 1, **counts, 'finite_structural_controls': 18,
        'revision_controls': 3, 'actual_shape_schema_fixture_checks': 1, 'actual_bounded_source_checks': 12,
        'whole_translation': 'pending', 'goal_status': 'active', 'next_independent_unit': 'F01-T.cal.definition.semantic-primitive'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
