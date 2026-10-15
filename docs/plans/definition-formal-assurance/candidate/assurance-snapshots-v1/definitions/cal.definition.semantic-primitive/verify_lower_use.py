"""Exact candidate references and separate typed specialization targets; no execution."""
import copy
import json
import build_candidate as b
import verifier as v
import verify_candidate as m


class ReferenceFault(ValueError):
    def __init__(self, code): self.code = code; super().__init__(code)
def guard_reference(request, selection, snap):
    if not isinstance(request, dict) or set(request) != {'source', 'scope', 'ir_ref', 'export'}: raise ReferenceFault('reference-extra-or-missing-fields')
    if not b.r.same_json(request['source'], selection['source']): raise ReferenceFault('reference-source-mismatch')
    if request['scope'] != selection['scope']: raise ReferenceFault('reference-scope-mismatch')
    if not b.r.same_json(request['ir_ref'], selection['ir_ref']): raise ReferenceFault('reference-IR-mismatch')
    if request['export'] != selection['export']: raise ReferenceFault('reference-export-mismatch')
    b.r.verify(snap, b.ROOT)
    raw = b.r.read_bytes(b.ROOT, request['ir_ref']['path'])
    if b.r.digest(raw) != request['ir_ref']['sha256']: raise ReferenceFault('reference-selected-IR-drift')
    typed = b.r.parse(raw, 'selected-candidate-IR'); b.ir.verify_ir(typed)
    if not b.r.same_json(typed['source'], request['source']) or typed['scope'] != request['scope'] or request['export'] not in {x['symbol_id'] for x in typed['declarations']}:
        raise ReferenceFault('reference-signature-substitution')
    return {'status': 'PASS-for-exact-selected-candidate-reference', 'source_fidelity': 'pending', 'semantic_ready': False,
        'lower_behavior_executed': False, 'semantic_preservation_proved': False, 'authority_effect': 'none'}
def interface(core):
    result = copy.deepcopy(core); result.update(interpretation_id='interface:primitive-lower-specialization-example', profile_ref='profile:typed-hypothetical-lower-specialization')
    result['declarations'] += [{'kind': 'predicate', 'symbol_id': name, 'scope': b.SCOPE, 'argument_sorts': ['SemanticRole']}
        for name in ['SpecializedRole', 'SpecializationConditionSatisfied']]
    return {'schema_version': 'definition-assurance-input/v1-candidate', 'kind': 'interpretation', 'authority_effect': 'none', 'payload': result}


def verify(write=False):
    context = m.load('context.json'); b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    bindings = [b.ref(path) for path in [b.UNIT / 'verify_lower_use.py', b.UNIT / 'verify_candidate.py', b.UNIT / 'build_candidate.py',
        b.IMPL / 'ir.py', b.IMPL / 'verifier.py', b.IMPL / 'resolver.py']]
    runtime = v.f.current_bindings(); core = m.load('t.json')['payload']; primary = m.load('static-ir.json')
    selection = {'source': core['source'], 'scope': core['scope'], 'ir_ref': b.ref(b.UNIT / 'static-ir.json'),
        'export': b.ir.qualified(core['source'], core['scope'], 'Primitive')}
    cases = []
    def reference_case(name, change, expected=None):
        request = copy.deepcopy(selection); change(request); cases.append({'case_id': name, 'request': request, 'expected_error': expected})
    reference_case('exact-selected-candidate-reference', lambda x: None)
    reference_case('source-digest-substitution-rejected', lambda x: x['source'].update(sha256='0' * 64), 'reference-source-mismatch')
    reference_case('source-version-substitution-rejected', lambda x: x['source'].update(version_ref='cal.definition.semantic-primitive@stale'), 'reference-source-mismatch')
    reference_case('scope-substitution-rejected', lambda x: x.update(scope='scope:foreign'), 'reference-scope-mismatch')
    reference_case('IR-digest-substitution-rejected', lambda x: x['ir_ref'].update(sha256='0' * 64), 'reference-IR-mismatch')
    reference_case('same-printed-name-other-scope-rejected', lambda x: x.update(export=b.ir.qualified(core['source'], 'scope:foreign', 'Primitive')), 'reference-export-mismatch')
    reference_case('unqualified-name-rejected', lambda x: x.update(export='Primitive'), 'reference-export-mismatch')
    reference_case('silent-replacement-payload-rejected', lambda x: x.update(replacement_primary_clauses=[]), 'reference-extra-or-missing-fields')
    reference_results = []
    for case in cases:
        before = copy.deepcopy(case['request'])
        try:
            result = guard_reference(case['request'], selection, snap)
            if case['expected_error'] is not None: raise ValueError('Bad candidate reference accepted')
            row = {'case_id': case['case_id'], 'request': case['request'], 'result': result}
        except ReferenceFault as error:
            if error.code != case['expected_error']: raise
            row = {'case_id': case['case_id'], 'request': case['request'], 'status': 'rejected-candidate-reference', 'code': error.code}
        if before != case['request']: raise ValueError('Reference guard mutated request')
        reference_results.append(row)
    envelope = interface(core); typed = b.ir.compile_interpretation(envelope['payload'], snap); b.ir.verify_ir(typed)
    if envelope['payload']['assumptions'] or not b.r.same_json(envelope['payload']['clauses'], core['clauses']) or not b.r.same_json(envelope['payload']['populations'], core['populations']):
        raise ValueError('Specialization target added to primary theory')
    ids = {x['symbol_id']: b.ir.qualified(core['source'], core['scope'], x['symbol_id']) for x in envelope['payload']['declarations']}
    target = v.renamed(b.every_role(b.implies(b.pred('SpecializedRole', 't'), b.both(b.pred('Primitive', 't'), b.pred('SpecializationConditionSatisfied', 't')))), ids)
    population = v.renamed(b.witness(b.pred('SpecializedRole', 't')), ids)
    composed = b.ir.compose([typed]); b.ir.check_composed_formula(composed, target); b.ir.check_composed_formula(composed, population)
    specialized = []
    for name, role, satisfies, expected in [('same-base-role-and-condition', 't', True, [True, True]),
        ('not-a-base-role', 'u', True, [False, True]), ('declared-condition-not-satisfied', 't', False, [False, True]),
        ('empty-specialization-is-vacuous-target-not-inhabitation', None, False, [True, False])]:
        local = m.base_model(); local['predicates']['SpecializedRole'] = [[role]] if role else []
        local['predicates']['SpecializationConditionSatisfied'] = [[role]] if role and satisfies else []
        model = m.qualify(local, ids); evaluator = v.Denotation(typed['declarations'], model)
        theory = all(evaluator.truth(x['formal_statement']) for x in primary['clauses'] if x['disposition'] == 'encoded')
        inhabited = all(evaluator.truth(x['statement']) for x in primary['populations'] if x['requirement'] == 'required')
        outcome = [evaluator.truth(target), evaluator.truth(population)]
        if not theory or not inhabited or outcome != expected: raise ValueError('Wrong separate specialization outcome: ' + name)
        specialized.append({'case_id': name, 'model': model, 'model_sha256': b.ir.digest(model), 'primary_theory_satisfied': theory,
            'required_primary_population_satisfied': inhabited, 'specialization_target_satisfied': outcome[0],
            'specialization_population_satisfied': outcome[1], 'actual_condition_evaluator': None, 'lower_behavior_executed': False})
    method = {'authority_effect': 'none', 'candidate_reference_selection': selection, 'specialization_target': target,
        'specialization_population': population, 'targets_added_to_primary_T': False, 'actual_consumer_or_condition_binding': None,
        'claim_ceiling': 'Exact reference guard and four hypothetical typed specialization models. No full lower-layer semantic preservation, actual rule evaluator, condition execution, admitted reauthoring or authority.'}
    if write:
        b.put('lower-interface-input.json', envelope); b.put('lower-interface-ir.json', typed); b.put('lower-selection.json', method)
    else:
        for name, value in [('lower-interface-input.json', envelope), ('lower-interface-ir.json', typed), ('lower-selection.json', method)]:
            if not b.r.same_json(m.load(name), value): raise ValueError('Lower interface/selection substituted')
    prior = json.loads((b.BASE / 'definitions/cal.definition.schema/delivery-manifest.json').read_bytes())
    for ref in prior['files'] + context['sources'] + bindings + [selection['ir_ref']]:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing source/checker/prior drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Runtime drift')
    report = {'schema_version': 'definition-assurance-primitive-lower-use/v1-candidate',
        'status': 'PASS-for-exact-candidate-reference-and-separate-specialization-controls', 'authority_effect': 'none',
        'checker_bindings': bindings, 'runtime_bindings': runtime,
        'input_refs': [b.ref(b.UNIT / name) for name in ['t.json', 'static-ir.json', 'lower-interface-input.json', 'lower-interface-ir.json', 'lower-selection.json']],
        'reference_controls': len(reference_results), 'rejected_reference_controls': sum(x.get('status') == 'rejected-candidate-reference' for x in reference_results),
        'reference_results': reference_results, 'specialization_controls': len(specialized), 'specialization_results': specialized,
        'targets_added_to_primary_T': False, 'actual_lower_layer_semantic_preservation': 'not-established',
        'semantic_ready': False, 'source_fidelity': 'pending', 'mechanized_proof': False, 'claim_ceiling': method['claim_ceiling']}
    if write: b.put('lower-use-checks.json', report)
    elif not b.r.same_json(m.load('lower-use-checks.json'), report): raise ValueError('Fresh lower-use evidence differs')
    return report


def main():
    report = verify('--write' in b.sys.argv)
    print(json.dumps({'result': report['status'], 'reference_controls': report['reference_controls'], 'rejected_reference_controls': report['rejected_reference_controls'],
        'specialization_controls': report['specialization_controls'], 'targets_added_to_primary_T': False,
        'actual_lower_layer_semantic_preservation': 'not-established', 'semantic_ready': False}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
