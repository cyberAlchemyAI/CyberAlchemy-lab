"""Typed targets and independent BFS for authored finite operational examples only."""
from collections import deque
import copy
import json
import build_candidate as b
import verifier as v
import verify_candidate as m


def interface(core):
    result = copy.deepcopy(core)
    result.update(interpretation_id='interface:invariant-finite-scenario-v1', profile_ref='profile:authored-finite-scenario-interface')
    result['declarations'] += [
        {'kind': 'predicate', 'symbol_id': 'InitialPoint', 'scope': b.SCOPE, 'argument_sorts': ['Point']},
        {'kind': 'relation', 'symbol_id': 'Next', 'scope': b.SCOPE, 'argument_sorts': ['Point', 'Point']}]
    return {'schema_version': 'definition-assurance-input/v1-candidate', 'kind': 'interpretation', 'authority_effect': 'none', 'payload': result}
def targets():
    initial = b.all_spec(b.all_point(b.implies(b.both(b.pred('Invariant', 'i'), b.pred('InScope', 'i', 'p'),
        b.pred('InitialPoint', 'p')), b.pred('Holds', 'i', 'p'))))
    step = b.all_spec(b.all_point(b.quant('forall', 'Point', 'q', b.implies(b.both(
        b.pred('Invariant', 'i'), b.pred('InScope', 'i', 'p'), b.pred('Holds', 'i', 'p'), b.pred('Next', 'p', 'q')),
        b.both(b.pred('InScope', 'i', 'q'), b.pred('Holds', 'i', 'q'))))))
    return {'initial-satisfaction': initial, 'step-preservation-and-scope': step, 'all-declared-scope-satisfaction': b.ACTUAL_SCOPE}
def cases():
    return [
        {'case_id': 'bad-reachable-last-step', 'initial': ['p0'], 'next': [['p0', 'p1'], ['p1', 'p2']], 'holds': ['p0', 'p1'],
            'scope': ['p0', 'p1', 'p2'], 'expected': [True, False, False, False], 'expected_path': ['p0', 'p1', 'p2']},
        {'case_id': 'bad-unreachable-declared-point', 'initial': ['p0'], 'next': [['p0', 'p1']], 'holds': ['p0', 'p1'],
            'scope': ['p0', 'p1', 'p2'], 'expected': [True, True, True, False], 'expected_path': None},
        {'case_id': 'all-declared-points-good', 'initial': ['p0'], 'next': [['p0', 'p1'], ['p1', 'p2']], 'holds': ['p0', 'p1', 'p2'],
            'scope': ['p0', 'p1', 'p2'], 'expected': [True, True, True, True], 'expected_path': None},
        {'case_id': 'bad-initial-point', 'initial': ['p2'], 'next': [], 'holds': ['p0', 'p1'],
            'scope': ['p0', 'p1', 'p2'], 'expected': [False, True, False, False], 'expected_path': ['p2']},
        {'case_id': 'empty-initial-set-no-positive-reachability-claim', 'initial': [], 'next': [['p0', 'p1']], 'holds': ['p0', 'p1', 'p2'],
            'scope': ['p0', 'p1', 'p2'], 'expected': [True, True, None, True], 'expected_path': None},
        {'case_id': 'step-exits-declared-scope', 'initial': ['p0'], 'next': [['p0', 'p1'], ['p1', 'p2']], 'holds': ['p0', 'p1', 'p2'],
            'scope': ['p0', 'p1'], 'expected': [True, False, None, True], 'expected_path': None}]
def make_model(case):
    model = m.base_model(); model['domains']['Point'] = ['p0', 'p1', 'p2']
    model['functions']['pointSubject'] = [{'args': [p], 'value': 'sys0'} for p in model['domains']['Point']]
    predicates = model['predicates']; predicates['StatePoint'] = [[p] for p in model['domains']['Point']]
    predicates['InScope'] = [['i', p] for p in case['scope']]
    predicates['MustHold'] = [['i', p] for p in case['scope']]
    predicates['Holds'] = [['i', p] for p in case['holds']]
    predicates['Violation'] = [['i', p] for p in case['scope'] if p not in case['holds']]
    predicates['Defect'] = copy.deepcopy(predicates['Violation'])
    predicates['InitialPoint'] = [[p] for p in case['initial']]; predicates['Next'] = copy.deepcopy(case['next'])
    return model
def bfs(points, initial, edges, scope, holds):
    # Inspect only supplied finite graph data; no recursive predicate interpretation is trusted.
    if not initial: return {'status': 'invalid-profile-empty-initial', 'reachable': [], 'satisfied': None, 'counterexample_path': None}
    if not set(initial) <= set(scope) or any(a in scope and z not in scope for a, z in edges):
        return {'status': 'invalid-profile-scope-not-closed', 'reachable': None, 'satisfied': None, 'counterexample_path': None}
    if not set(initial) <= set(points) or any(a not in points or z not in points for a, z in edges): raise ValueError('Unknown finite point')
    predecessor = {p: None for p in initial}; queue = deque(initial)
    while queue:
        p = queue.popleft()
        for left, right in edges:
            if left == p and right not in predecessor: predecessor[right] = p; queue.append(right)
    bad = next((p for p in predecessor if p not in holds), None); path = None
    if bad is not None:
        path = [bad]
        while predecessor[path[-1]] is not None: path.append(predecessor[path[-1]])
        path.reverse()
    return {'status': 'independently-traversed-authored-finite-graph', 'reachable': sorted(predecessor),
        'satisfied': bad is None, 'counterexample_path': path}


def verify(write=False):
    context = m.load('context.json'); b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    for ref in context['sources']:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Input drift')
    refs = [b.ref(path) for path in [b.UNIT / 'verify_scenarios.py', b.UNIT / 'verify_candidate.py', b.UNIT / 'build_candidate.py', b.IMPL / 'verifier.py', b.IMPL / 'ir.py']]
    runtime = v.f.current_bindings(); core = m.load('t.json')['payload']; primary = m.load('static-ir.json')
    envelope = interface(core); typed = b.ir.compile_interpretation(envelope['payload'], snap); b.ir.verify_ir(typed)
    if envelope['payload']['assumptions'] or not b.r.same_json(envelope['payload']['clauses'], core['clauses']) or not b.r.same_json(envelope['payload']['populations'], core['populations']):
        raise ValueError('Scenario targets or policy added as premises')
    composed = b.ir.compose([typed]); ids = {x['symbol_id']: b.ir.qualified(core['source'], core['scope'], x['symbol_id']) for x in envelope['payload']['declarations']}
    selected_targets = {name: v.renamed(node, ids) for name, node in targets().items()}
    for formula in selected_targets.values(): b.ir.check_composed_formula(composed, formula)
    theory = [x for x in primary['clauses'] if x['disposition'] == 'encoded']; populations = [x for x in primary['populations'] if x['requirement'] == 'required']
    results = []
    for case in cases():
        local = make_model(case); model = m.qualify(local, ids); evaluator = v.Denotation(typed['declarations'], model)
        T = all(evaluator.truth(x['formal_statement']) for x in theory); I = all(evaluator.truth(x['statement']) for x in populations)
        if (T, I) != (True, True): raise ValueError('Operational example rejects primary metadata: ' + case['case_id'])
        truth = {name: evaluator.truth(formula) for name, formula in selected_targets.items()}
        reachable = bfs(local['domains']['Point'], case['initial'], case['next'], case['scope'], case['holds'])
        actual = [truth['initial-satisfaction'], truth['step-preservation-and-scope'], reachable['satisfied'], truth['all-declared-scope-satisfaction']]
        if actual != case['expected'] or reachable['counterexample_path'] != case['expected_path']:
            raise ValueError('Wrong finite target outcome: ' + case['case_id'])
        results.append({'case_id': case['case_id'], 'selected_input': case, 'model': model, 'model_sha256': b.ir.digest(model),
            'primary_theory_satisfied': T, 'required_population_satisfied': I, 'target_results': truth, 'reachability': reachable,
            'synthetic_profile': 'nonempty-initial-and-closed-declared-state-scope', 'actual_program_binding': None})
    selection = {'authority_effect': 'none', 'source': core['source'], 'interface_input_ref': b.ref(b.UNIT / 'scenario-interface-input.json') if not write else None,
        'profile_is_source_fidelity_approved': False, 'assembled_into_primary_T': False, 'targets_are_premises': False,
        'targets': selected_targets, 'method': 'Independent finite BFS and typed first-order denotation over explicitly authored examples',
        'scope': 'Exact primary clauses, populations and symbols are retained; InitialPoint and Next extend only the signature as auxiliary method declarations, not additional source clauses.'}
    if write:
        b.put('scenario-interface-input.json', envelope); b.put('scenario-interface-ir.json', typed)
        selection['interface_input_ref'] = b.ref(b.UNIT / 'scenario-interface-input.json'); b.put('scenario-selection.json', selection)
    elif not b.r.same_json(m.load('scenario-interface-input.json'), envelope) or not b.r.same_json(m.load('scenario-interface-ir.json'), typed) or not b.r.same_json(m.load('scenario-selection.json'), selection):
        raise ValueError('Scenario interface/targets substituted')
    for ref in context['sources'] + refs:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing scenario-input drift')
    prior = json.loads((b.BASE / 'definitions/cal.definition.hypothesis/delivery-manifest.json').read_bytes())
    for ref in prior['files']:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Predecessor drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Runtime drift')
    report = {'schema_version': 'definition-assurance-invariant-finite-scenarios/v1-candidate',
        'status': 'PASS-for-six-authored-finite-scenarios-with-separate-targets', 'authority_effect': 'none',
        'input_refs': [b.ref(b.UNIT / name) for name in ['t.json', 'static-ir.json', 'scenario-interface-input.json', 'scenario-interface-ir.json', 'scenario-selection.json']],
        'checker_bindings': refs, 'runtime_bindings': runtime, 'results': results, 'scenario_count': len(results),
        'valid_synthetic_profiles': sum(x['reachability']['satisfied'] is not None for x in results), 'invalid_synthetic_profiles': sum(x['reachability']['satisfied'] is None for x in results),
        'targets_assembled_into_primary_T': False, 'semantic_ready': False, 'mechanized_proof': False,
        'claim_ceiling': 'Six authored finite graphs only; four valid profile cases and two explicitly invalid profiles. Good reachable states do not establish every declared point. No recursive/fixed-point theory, exhaustive solver search, actual implementation, deontic/temporal proof or source-owner fidelity.'}
    if write: b.put('scenario-checks.json', report)
    elif not b.r.same_json(m.load('scenario-checks.json'), report): raise ValueError('Fresh scenario evidence differs')
    return report


def main():
    report = verify('--write' in b.sys.argv)
    print(json.dumps({'result': report['status'], 'scenarios': report['scenario_count'],
        'valid_synthetic_profiles': report['valid_synthetic_profiles'], 'invalid_synthetic_profiles': report['invalid_synthetic_profiles'],
        'targets_assembled_into_primary_T': False, 'actual_implementation_checked': False, 'semantic_ready': False}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
