"""Conditional reasoning method illustration; content and rule are not source premises."""
import copy
import itertools
import json
import build_candidate as b
import verifier as v
import verify_candidate as m


def interface(core):
    result = copy.deepcopy(core)
    result.update(interpretation_id='interface:premise-conditional-reasoning-v1', profile_ref='profile:authored-two-atom-conditional-example')
    result['declarations'] += [{'kind': 'predicate', 'symbol_id': name, 'scope': b.SCOPE, 'argument_sorts': ['Proposition']}
        for name in ['ContentA', 'ContentB']]
    return {'schema_version': 'definition-assurance-input/v1-candidate', 'kind': 'interpretation', 'authority_effect': 'none', 'payload': result}
def formulas():
    A = b.every_role(b.pred('ContentA', b.fn('propositionOf')))
    B = b.every_role(b.pred('ContentB', b.fn('propositionOf')))
    rule = b.implies(A, B)
    return {'working-content-A': A, 'candidate-rule-A-implies-B': rule, 'consequence-B': B,
        'conditional-modus-ponens': b.implies(b.both(A, rule), B)}


def verify(write=False):
    context = m.load('context.json'); b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    for ref in context['sources']:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Input drift')
    bindings = [b.ref(path) for path in [b.UNIT / 'verify_reasoning_example.py', b.UNIT / 'verify_candidate.py',
        b.UNIT / 'build_candidate.py', b.IMPL / 'verifier.py', b.IMPL / 'ir.py']]
    runtime = v.f.current_bindings(); core = m.load('t.json')['payload']; primary = m.load('static-ir.json')
    envelope = interface(core); typed = b.ir.compile_interpretation(envelope['payload'], snap); b.ir.verify_ir(typed)
    if envelope['payload']['assumptions'] or not b.r.same_json(envelope['payload']['clauses'], core['clauses']) or not b.r.same_json(envelope['payload']['populations'], core['populations']):
        raise ValueError('Synthetic reasoning altered selected source theory')
    composed = b.ir.compose([typed]); ids = {x['symbol_id']: b.ir.qualified(core['source'], core['scope'], x['symbol_id']) for x in envelope['payload']['declarations']}
    selected = {name: v.renamed(formula, ids) for name, formula in formulas().items()}
    for formula in selected.values(): b.ir.check_composed_formula(composed, formula)
    T = [x for x in primary['clauses'] if x['disposition'] == 'encoded']; I = [x for x in primary['populations'] if x['requirement'] == 'required']
    results = []
    for truth_A, truth_B in itertools.product([False, True], repeat=2):
        local = m.base_model(); local['predicates']['ContentA'] = [['p']] if truth_A else []
        local['predicates']['ContentB'] = [['p']] if truth_B else []
        model = m.qualify(local, ids); evaluator = v.Denotation(typed['declarations'], model)
        theory = all(evaluator.truth(x['formal_statement']) for x in T); inhabited = all(evaluator.truth(x['statement']) for x in I)
        outcomes = {name: evaluator.truth(formula) for name, formula in selected.items()}
        expected_rule = (not truth_A) or truth_B
        if not theory or not inhabited or outcomes['working-content-A'] != truth_A or outcomes['consequence-B'] != truth_B or outcomes['candidate-rule-A-implies-B'] != expected_rule or not outcomes['conditional-modus-ponens']:
            raise ValueError('Wrong two-atom conditional outcome')
        premises = outcomes['working-content-A'] and outcomes['candidate-rule-A-implies-B']
        if premises and not outcomes['consequence-B']: raise ValueError('Invalid conditional inference')
        results.append({'case_id': 'A-' + str(truth_A).lower() + '-B-' + str(truth_B).lower(), 'model': model, 'model_sha256': b.ir.digest(model),
            'primary_theory_satisfied': theory, 'required_population_satisfied': inhabited,
            'formula_results': outcomes, 'synthetic_conditional_premise_set_satisfied': premises})
    absent = next(x for x in results if x['case_id'] == 'A-false-B-false')
    if absent['formula_results']['candidate-rule-A-implies-B'] is not True or absent['formula_results']['consequence-B'] is not False:
        raise ValueError('Unconditioned consequence countermodel lost')
    selection = {'authority_effect': 'none', 'primary_source': core['source'], 'auxiliary_predicates': ['ContentA', 'ContentB'],
        'primary_theory_extended_with_content_premises': False, 'actual_project_content_binding': None, 'actual_owner_assumption_selection': None,
        'synthetic_conditional_premises': [selected['working-content-A'], selected['candidate-rule-A-implies-B']],
        'conditional_target': selected['consequence-B'], 'logical_validity_query': selected['conditional-modus-ponens'],
        'formulas': selected, 'scope': 'Method illustration over exactly two Boolean atoms represented in a one-proposition authored structure. Retains exact primary T/I; no new source clauses.',
        'claim_ceiling': 'Four complete Boolean assignments for this propositional method illustration; no whole FOL enumeration, source proposition interpreter, actual reasoning context, premise truth, world observation or promotion.'}
    if write:
        b.put('reasoning-interface-input.json', envelope); b.put('reasoning-interface-ir.json', typed); b.put('reasoning-selection.json', selection)
    else:
        for name, value in [('reasoning-interface-input.json', envelope), ('reasoning-interface-ir.json', typed), ('reasoning-selection.json', selection)]:
            if not b.r.same_json(m.load(name), value): raise ValueError('Reasoning input/target substitution')
    prior = json.loads((b.BASE / 'definitions/cal.definition.invariant/delivery-manifest.json').read_bytes())
    for ref in prior['files'] + context['sources'] + bindings:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing prior/input/checker drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Closing runtime drift')
    report = {'schema_version': 'definition-assurance-premise-conditional-example/v1-candidate',
        'status': 'PASS-for-four-authored-two-atom-conditional-reasoning-rows', 'authority_effect': 'none',
        'input_refs': [b.ref(b.UNIT / name) for name in ['t.json', 'static-ir.json', 'reasoning-interface-input.json', 'reasoning-interface-ir.json', 'reasoning-selection.json']],
        'checker_bindings': bindings, 'runtime_bindings': runtime, 'results': results, 'boolean_rows': len(results),
        'rows_satisfying_synthetic_conditional_premises': sum(x['synthetic_conditional_premise_set_satisfied'] for x in results),
        'conditional_rule_valid_in_all_four_rows': True, 'unconditioned_consequence_countermodel_sha256': absent['model_sha256'],
        'actual_content_or_assumptions_selected': False, 'semantic_ready': False, 'mechanized_proof': False,
        'claim_ceiling': selection['claim_ceiling']}
    if write: b.put('reasoning-checks.json', report)
    elif not b.r.same_json(m.load('reasoning-checks.json'), report): raise ValueError('Fresh reasoning evidence differs')
    return report


def main():
    report = verify('--write' in b.sys.argv)
    print(json.dumps({'result': report['status'], 'boolean_rows': report['boolean_rows'],
        'rows_satisfying_synthetic_conditional_premises': report['rows_satisfying_synthetic_conditional_premises'],
        'conditional_rule_valid_in_all_four_rows': True, 'primary_content_assumptions_added': False,
        'actual_content_or_assumptions_selected': False, 'semantic_ready': False}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
