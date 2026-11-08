"""Review all eight partial foundations; nominal consistency is not semantic closure."""
import copy
import json
import build_candidate as b
import dependencies as d
import verifier as v


def read(path): return json.loads(path.read_bytes())
def verify(write=False):
    context = read(b.UNIT / 'context.json'); b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    queue_path = b.ROOT / 'docs/plans/definition-formal-assurance/candidate/foundations-first-v1/foundation-source-queue.json'
    queue = read(queue_path)['sources']; bindings = [b.ref(queue_path), b.ref(b.UNIT / 'verify_foundations.py'),
        b.ref(b.IMPL / 'ir.py'), b.ref(b.IMPL / 'verifier.py'), b.ref(b.IMPL / 'dependencies.py'), b.ref(b.BASE / 'units/A04/correspondence.py')]
    runtime = v.f.current_bindings(); packets, inputs, roots, rows, chosen, slices = [], [], [], [], [], []
    nominal_model = {key: {} for key in ['domains', 'constants', 'functions', 'predicates']}
    for selection in queue:
        identity = selection['definition_id']; folder = b.BASE / 'definitions' / identity
        paths = {name: folder / filename for name, filename in [('interpretation', 't.json'), ('correspondence', 'correspondence.json'),
            ('IR', 'static-ir.json'), ('model_evidence', 'model-controls.json')]}
        refs = {name: b.ref(path) for name, path in paths.items()}; bindings.extend(refs.values())
        envelope, packet, typed, models = [read(paths[name]) for name in paths]; core = envelope['payload']
        source = b.source_ref(snap, identity)
        if not b.r.same_json(core['source'], source) or not b.r.same_json(packet['interpretation'], core) or not b.r.same_json(typed, b.ir.compile_interpretation(core, snap)):
            raise ValueError('Foundation source/interpretation/IR substitution: ' + identity)
        if core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending' or packet['review_packet']['review_status'] != 'pending':
            raise ValueError('Owner fidelity/adopted assumptions fabricated: ' + identity)
        correspondence = b.co.check(packet, snap, required_dependencies=[x['version_ref'] for x in core['depends_on']],
            required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
        if not correspondence['character_accounting_complete']: raise ValueError('Incomplete source accounting')
        b.ir.verify_ir(typed); packets.append(packet); inputs.append(typed); roots.append(source)
        model = None; selected_case = None
        for case in models['results']:
            candidate = case.get('model')
            if candidate is None: continue
            try:
                evaluator = v.Denotation(typed['declarations'], candidate)
                satisfied = all(evaluator.truth(x['formal_statement']) for x in typed['clauses'] if x['disposition'] == 'encoded')
                inhabited = all(evaluator.truth(x['statement']) for x in typed['populations'] if x['requirement'] == 'required')
            except v.VerificationFault: continue
            if satisfied and inhabited:
                if b.ir.digest(candidate) != case['model_sha256']: raise ValueError('Substituted foundation model')
                model = candidate; selected_case = case['case_id']; break
        if model is None: raise ValueError('No independently verified nominal slice witness: ' + identity)
        for bucket, values in model.items():
            if set(values) & set(nominal_model[bucket]): raise ValueError('Unexpected source-qualified symbol collision')
            nominal_model[bucket].update(copy.deepcopy(values))
        chosen.append({'definition_id': identity, 'case_id': selected_case, 'model_evidence_ref': refs['model_evidence'], 'model_sha256': b.ir.digest(model)})
        slices.extend([{'definition_id': identity, 'population_id': x['population_id'], 'statement': x['statement']} for x in typed['populations'] if x['requirement'] == 'required'])
        rows.append({'definition_id': identity, 'source': source, 'draft_refs': refs, 'source_units': len(packet['source_units']),
            'mapped_clauses': len(core['clauses']), 'encoded_clauses': sum(x['disposition'] == 'encoded' for x in core['clauses']),
            'explanatory_clauses': sum(x['disposition'] == 'explanatory' for x in core['clauses']), 'deferred_clauses': len(correspondence['unresolved_clauses']),
            'required_populations': sum(x['requirement'] == 'required' for x in core['populations']), 'unresolved_populations': sum(x['requirement'] == 'unresolved' for x in core['populations']),
            'findings': [x['finding_id'] for x in packet['source_precedence']['conflicts']], 'source_fidelity': 'pending',
            'whole_definition_translation': 'pending', 'whole_definition_proof': None, 'owner_review': 'pending', 'task_result': 'PARTIAL'})
    if len(rows) != 8 or len({x['definition_id'] for x in rows}) != 8: raise ValueError('Wrong foundation denominator')
    nominal = b.ir.compose(inputs); b.ir.verify_composed(nominal, inputs, [], b.ROOT)
    evaluator = v.Denotation(nominal['declarations'], nominal_model)
    clauses = [{'namespace': x['namespace'], 'clause_id': x['clause_id'], 'truth': evaluator.truth(x['formal_statement'])}
        for x in nominal['clauses'] if x['disposition'] == 'encoded']
    populations = []
    for x in slices:
        b.ir.check_composed_formula(nominal, x['statement'])
        populations.append({'definition_id': x['definition_id'], 'population_id': x['population_id'], 'truth': evaluator.truth(x['statement'])})
    if not all(x['truth'] for x in clauses + populations): raise ValueError('Nominal product slice lacks joint T/I')
    graph = d.compile_graph(snap, roots, packets, live_root=b.ROOT)
    if (len(graph['nodes']), len(graph['edges']), len(graph['missing_or_quarantined_interpretations'])) != (34, 59, 26):
        raise ValueError('Wrong all-foundation authored graph denominator')
    if len(graph['cycle_reviews']) != 2 or any(x['disposition'] != 'unresolved-cycle-classification' for x in graph['cycle_reviews']):
        raise ValueError('Two semantic cycles must remain explicit')
    counts = {key: sum(x[key] for x in rows) for key in ['source_units', 'mapped_clauses', 'encoded_clauses', 'explanatory_clauses', 'deferred_clauses', 'required_populations', 'unresolved_populations']}
    expected = {'source_units': 180, 'mapped_clauses': 287, 'encoded_clauses': 79, 'explanatory_clauses': 69, 'deferred_clauses': 139,
        'required_populations': 68, 'unresolved_populations': 97}
    if counts != expected or len(clauses) != 79 or len(populations) != 68: raise ValueError('Wrong clause/population denominator: ' + json.dumps(counts))
    selection = {'authority_effect': 'none', 'foundation_queue_ref': b.ref(queue_path), 'root_sources': roots, 'selected_drafts': rows,
        'selected_authored_models': chosen, 'carrier_alignments': [], 'assumptions_added': [],
        'meaning': 'Exact nominal composition of eight independently authored partial T/I slices. No shared-meaning alignment or owner fidelity is accepted.'}
    witness = {'authority_effect': 'none', 'model': nominal_model, 'model_sha256': b.ir.digest(nominal_model),
        'nominal_IR_sha256': nominal['ir_sha256'], 'selected_model_bindings': chosen, 'clause_results': clauses, 'population_results': populations,
        'status': 'independently-checked-finite-witness-for-nominal-partial-foundation-slices',
        'semantic_ready': False, 'whole_source_combined_consistency': 'not-established', 'canonical_carrier_alignment': 'not-established',
        'claim_ceiling': 'Finite model for exactly79 encoded clauses and68 required populations in source-qualified, unaligned signatures. Excludes139 deferred clauses and97 unresolved policies; not canonical/all-source combined consistency, semantic noncollapse or whole-definition proof.'}
    report = {'schema_version': 'definition-assurance-foundation-draft-review/v1-candidate',
        'status': 'PASS-for-exact-eight-partial-drafts-and-nominal-witness;family-exit-not-ready', 'authority_effect': 'none',
        'checker_bindings': bindings, 'runtime_bindings': runtime, 'rows': rows, 'counts': counts, 'current_definitions': 183,
        'admitted_source_versions': 189, 'foundation_partial_drafts': 8, 'remaining_current_identities_without_per_definition_T_draft': 175,
        'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0, 'source_fidelity': 'pending', 'semantic_ready': False,
        'F01_T_family_result': 'PARTIAL', 'F01_joint_review_exit': 'not-ready', 'authored_dependency_nodes': 34, 'authored_dependency_edges': 59,
        'missing_counterpart_packets': graph['missing_or_quarantined_interpretations'], 'unresolved_cycles': graph['cycle_reviews'],
        'nominal_witness': {'encoded_clauses_satisfied': len(clauses), 'required_populations_satisfied': len(populations),
            'declarations': len(nominal['declarations']), 'model_sha256': witness['model_sha256'], 'reviewed_carrier_alignments': 0},
        'next_independent_unit': 'I04.1', 'goal_status': 'active',
        'claim_ceiling': 'All eight foundational candidates are accounted as partial. A nominal model cannot settle source meaning, scope/owner mappings, deferred clauses, Hypothesis precedence, semantic cycles, canonical noncollapse or all183-definition assurance. Full episode remains incomplete.'}
    prior = read(b.BASE / 'definitions/cal.definition.schema/delivery-manifest.json')
    for ref in prior['files'] + context['sources'] + bindings:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing foundation input/checker/prior drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Runtime drift')
    documents = [('foundation-selection.json', selection), ('foundation-nominal-ir.json', nominal), ('foundation-nominal-witness.json', witness),
        ('foundation-dependency-graph.json', graph), ('foundation-draft-review.json', report)]
    table = '\n'.join('| ' + x['definition_id'].split('.')[-1] + ' | ' + ' | '.join(str(x[k]) for k in ['source_units','mapped_clauses','encoded_clauses','deferred_clauses','required_populations','unresolved_populations']) + ' |' for x in rows)
    markdown = '''# Foundational formalization draft review

Candidate progress, 2026-10-08. Authority effect: none. All eight foundational identities have source-bound **partial** drafts. F01-T and the joint family exit remain unready; there are no owner-accepted whole translations or whole-definition proofs.

| Definition | Source units | Clauses | Encoded | Deferred | Required populations | Unresolved populations |
| --- | --- | --- | --- | --- | --- | --- |
''' + table + '''

The exact denominator is 180 source units,287 clauses,79 encoded clauses,69 explanatory clauses and139 deferred clauses. Eight sources and their independent candidate IRs are selected; no source-owner fidelity or precedence decision is simulated. There are68 required and97 unresolved population policies.

An independently evaluated finite model satisfies the79 encoded clauses and68 required populations after **nominal** composition. No carrier or meaning alignment is selected. This supports only the source-qualified partial slice; private vocabularies cannot reveal contradictions that would appear after real meaning alignment. It does not establish consistency of the complete source meanings, required semantic distinction, or the final canonical theory.

The all-foundation authored dependency graph has34 nodes and59 edges. Twenty-six counterpart packets remain missing. Axiom/Hypothesis/Invariant/Premise form one unclassified semantic component; Schema/Semantic Primitive form another. Joint review is needed, without interpreting either component as an inductive or least-fixed-point construction.

The reviews preserve several distinctions: a Definition artifact versus its represented concept; foundational posture versus actual truth; investigation versus deliberate working adoption; a must-hold requirement versus implementation satisfaction; structural conformance versus meaning/authority; and a local primitive role versus a borrowed external meaning or an unqualified label. Current source admission and historical embedded candidate posture are separately reported.

Logical typing, required inhabitation, relation classification, source correspondence, assumption selection, fixed-point/temporal/normative semantics, provider limits, real operational bindings and owner review remain separate assurance aspects. The nominal witness is not a substitute for those obligations. The inherited Hypothesis/Premise precedence conflict, Axiom fan-out interpretation, legacy/local-role/current Lab scope, metadata payloads, populations, actual lifecycle and lower-layer preservation need explicit disposition.

Only eight of183 current identities have per-definition T drafts in this candidate tree;175 remain without such a draft. The189 admitted source-version denominator remains intact. Whole source fidelity, semantic dependency completeness, all-current evidence, one meaning-aligned combined theory, clean replay and the final complete episode review are still outstanding.

The next independent unit is I04.1, the read-only candidate CLI/coverage report. Its purpose is to expose this exact partial state and remaining obligations without granting semantic readiness or touching admissions. Completing a report will not complete the foundational family or the full episode.
'''
    if write:
        for name, value in documents: b.put(name, value)
        with (b.UNIT / 'foundation-draft-review.md').open('x') as stream: stream.write(markdown)
    else:
        for name, value in documents:
            if not b.r.same_json(read(b.UNIT / name), value): raise ValueError('Fresh foundation evidence differs: ' + name)
        if (b.UNIT / 'foundation-draft-review.md').read_text() != markdown: raise ValueError('Fresh foundation narrative differs')
    return report


def main():
    report = verify('--write' in b.sys.argv)
    print(json.dumps({'result': report['status'], 'foundation_partial_drafts': 8, **report['counts'],
        'nominal_encoded_clause_results': 79, 'nominal_required_population_results': 68,
        'dependency_nodes': 34, 'dependency_edges': 59, 'missing_counterpart_packets': 26, 'semantic_cycles': 2,
        'source_owner_accepted_whole_translations': 0, 'whole_definition_proofs': 0, 'remaining_current_identities_without_per_definition_T_draft': 175,
        'semantic_ready': False, 'goal_status': 'active', 'next_independent_unit': 'I04.1'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
