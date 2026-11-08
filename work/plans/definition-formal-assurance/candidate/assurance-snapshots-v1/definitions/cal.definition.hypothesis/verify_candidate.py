"""Independent Hypothesis models and inherited Premise comparisons with separate theories."""
import copy
import itertools
import json
import build_candidate as b
import verifier as v


def load(name): return json.loads((b.UNIT / name).read_bytes())
def base_model():
    predicates = {name: [] for name in b.SIGNATURE}
    predicates.update(Hypothesis=[['h']], Stated=[['h']], Provisional=[['p', 'c']],
        Falsifiable=[['p', 'c']], ForInvestigation=[['p', 'c']],
        DeclaredTest=[['p', 'c', 't']], CouldReject=[['p', 'c', 't']])
    return {'domains': {'RoleInstance': ['h'], 'Proposition': ['p'], 'ReasoningContext': ['c'], 'TestCondition': ['t']},
        'constants': {}, 'functions': {'propositionOf': [{'args': ['h'], 'value': 'p'}],
            'contextOf': [{'args': ['h'], 'value': 'c'}]}, 'predicates': predicates}
def add_premise(model, same_role=False):
    record, context = ('h', 'c') if same_role else ('w', 'other-context')
    if not same_role:
        model['domains']['RoleInstance'].append(record); model['domains']['ReasoningContext'].append(context)
        model['functions']['propositionOf'].append({'args': [record], 'value': 'p'})
        model['functions']['contextOf'].append({'args': [record], 'value': context})
    model['predicates']['WorkingPremise'] = [[record]]; model['predicates']['LoadBearing'] = [[record]]
    for name in ['AdoptedToProceed', 'Defeasible', 'VeracityLow', 'ConvictionHigh']:
        model['predicates'][name] = [['p', context]]
    return record, context
def controls():
    rows = []
    def add(name, change, T=True, I=True, C=True, error=None):
        model = base_model(); change(model)
        rows.append({'case_id': name, 'model': model, 'expected_T': T, 'expected_I': I, 'expected_C': C, 'expected_error': error})
    add('stated-investigation-does-not-adopt-or-establish-truth', lambda model: None)
    for name in ['Provisional', 'Falsifiable']:
        add('missing-' + name, lambda model, name=name: model['predicates'].__setitem__(name, []), T=False, I=False)
    add('no-investigation-mode', lambda model: model['predicates'].update(ForInvestigation=[], ForExperiment=[]), T=False, I=False)
    add('experiment-mode-alone', lambda model: model['predicates'].update(ForInvestigation=[], ForExperiment=[['p', 'c']]))
    add('both-investigation-modes', lambda model: model['predicates'].update(ForExperiment=[['p', 'c']]))
    add('missing-declared-test', lambda model: model['predicates'].update(DeclaredTest=[]), T=False, I=False)
    add('no-potential-response', lambda model: model['predicates'].update(CouldReject=[]), T=False, I=False)
    def responses(model, names):
        for name in b.TESTS[1:]: model['predicates'][name] = [['p', 'c', 't']] if name in names else []
    for name in b.TESTS[1:]: add('only-' + name, lambda model, name=name: responses(model, [name]))
    for names in itertools.combinations(b.TESTS[1:], 2):
        add('response-overlap-' + '-'.join(names), lambda model, names=names: responses(model, names))
    def unrelated(model, name):
        model['domains']['Proposition'].append('other-proposition')
        model['predicates'][name] = [['other-proposition', 'c', 't']] if name == 'DeclaredTest' else [['other-proposition', 'c']]
    add('unrelated-test-cannot-supply-Hypothesis-response', lambda model: unrelated(model, 'DeclaredTest'), T=False, I=False)
    add('unrelated-falsifiability-status-cannot-supply-Hypothesis-condition', lambda model: unrelated(model, 'Falsifiable'), T=False, I=False)
    add('empty-Hypothesis-role-is-vacuous-T-but-fails-required-I', lambda model: model['predicates'].update(Hypothesis=[]), I=False)
    add('investigated-proposition-may-actually-be-true-without-establishment', lambda model: model['predicates'].update(ActuallyTrue=[['p']]))
    add('high-conviction-low-veracity-do-not-establish-truth', lambda model: model['predicates'].update(VeracityLow=[['p', 'c']], ConvictionHigh=[['p', 'c']]))
    add('same-proposition-investigated-and-adopted-in-distinct-contexts', lambda model: add_premise(model))
    add('separately-adopted-Hypothesis-role-is-not-universally-forbidden', lambda model: add_premise(model, same_role=True))
    def low_conviction(model): add_premise(model); model['predicates']['ConvictionHigh'] = []
    add('working-comparison-does-not-require-often-high-conviction', low_conviction)
    def true_working(model): add_premise(model); model['predicates']['ActuallyTrue'] = [['p']]
    add('unestablished-working-proposition-is-not-required-actually-false', true_working)
    for name in ['AdoptedToProceed', 'Defeasible', 'LoadBearing']:
        def missing(model, name=name): add_premise(model); model['predicates'][name] = []
        add('working-comparison-missing-' + name, missing, C=False)
    def established(model): add_premise(model); model['predicates']['EstablishedTrue'] = [['p', 'other-context']]
    add('working-comparison-established-status-rejected', established, C=False)
    for name in ['AxiomRole', 'InvariantRole', 'DisposableHypothesis']:
        def incompatible(model, name=name): record, _ = add_premise(model); model['predicates'][name] = [[record]]
        add('working-comparison-conflicts-with-' + name, incompatible, C=False)
    add('ill-sorted-context-accessor-rejected', lambda model: model['functions']['contextOf'][0].update(value='p'), error='ill-sorted-function-result')
    add('non-total-proposition-accessor-rejected', lambda model: model['functions']['propositionOf'].clear(), error='nontotal-function')
    add('wrong-Hypothesis-predicate-arity-rejected', lambda model: model['predicates'].update(Hypothesis=[['h', 'h']]), error='ill-sorted-model-tuple')
    add('duplicate-Hypothesis-tuple-rejected', lambda model: model['predicates']['Hypothesis'].append(['h']), error='duplicate-predicate-tuple')
    return rows
def qualify(model, ids):
    return {'domains': {ids[name]: values for name, values in model['domains'].items()}, 'constants': {},
        'functions': {ids[name]: rows for name, rows in model['functions'].items()},
        'predicates': {ids[name]: rows for name, rows in model['predicates'].items()}}


def verify(write=False):
    files = [b.IMPL / 'verifier.py', b.IMPL / 'ir.py', b.IMPL / 'contracts.py', b.BASE / 'units/A04/correspondence.py', b.UNIT / 'build_candidate.py', b.UNIT / 'verify_candidate.py']
    bindings = [b.ref(path) for path in files]; runtime = v.f.current_bindings(); context = load('context.json')
    for reference in context['sources']:
        if b.ref(b.ROOT / reference['path']) != reference: raise ValueError('Changed declared input')
    b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    packet, envelope, typed = load('correspondence.json'), load('t.json'), load('static-ir.json')
    core = envelope['payload']; comparison = load('comparison-input.json'); comparison_ir = load('comparison-ir.json')
    for selected in [envelope, comparison]:
        if b.c.validate(selected, 'interpretation')['status'] != 'structurally-valid': raise ValueError('Malformed selected slice')
    if not b.r.same_json(packet['interpretation'], core) or not b.r.same_json(typed, b.ir.compile_interpretation(core, snap)) or not b.r.same_json(comparison_ir, b.ir.compile_interpretation(comparison['payload'], snap)):
        raise ValueError('Interpretation/IR substitution')
    if comparison['payload']['assumptions'] or comparison['payload']['populations'] or load('comparison-selection.json')['assembled_into_primary_T'] is not False:
        raise ValueError('Inherited comparison turned into primary premises/population policy')
    correspondence = b.co.check(packet, snap, required_dependencies=[x['version_ref'] for x in core['depends_on']], required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
    if not correspondence['character_accounting_complete'] or not b.r.same_json(correspondence, load('correspondence-check.json')): raise ValueError('Wrong source denominator')
    if core['assumptions'] or core['source_fidelity'] != 'pending': raise ValueError('Fabricated premise or fidelity')
    ids = {x['symbol_id']: b.ir.qualified(core['source'], core['scope'], x['symbol_id']) for x in core['declarations']}
    T = [x for x in typed['clauses'] if x['disposition'] == 'encoded']; I = [x for x in typed['populations'] if x['requirement'] == 'required']; C = comparison_ir['clauses']
    if len(T) != 1 or len(C) != 4: raise ValueError('Comparison and primary theory denominators changed')
    def evaluate(model):
        evaluator = v.Denotation(typed['declarations'], model)
        clauses = [{'clause_id': x['clause_id'], 'truth': evaluator.truth(x['formal_statement'])} for x in T]
        populations = [{'population_id': x['population_id'], 'truth': evaluator.truth(x['statement'])} for x in I]
        comparisons = [{'clause_id': x['clause_id'], 'truth': evaluator.truth(x['formal_statement'])} for x in C]
        return all(x['truth'] for x in clauses), all(x['truth'] for x in populations), all(x['truth'] for x in comparisons), clauses, populations, comparisons
    results = []
    for control in controls():
        model = qualify(control['model'], ids)
        try:
            theory, population, compared, clauses, populations, comparisons = evaluate(model)
            if control['expected_error'] is not None or (theory, population, compared) != (control['expected_T'], control['expected_I'], control['expected_C']):
                raise ValueError('Wrong semantic control: ' + control['case_id'])
            result = {'case_id': control['case_id'], 'model': model, 'model_sha256': b.ir.digest(model), 'status': 'independently-evaluated-authored-model',
                'primary_theory_satisfied': theory, 'required_population_satisfied': population, 'separate_comparison_satisfied': compared,
                'primary_clause_results': clauses, 'population_results': populations, 'comparison_results': comparisons}
        except v.VerificationFault as error:
            if error.code != control['expected_error']: raise
            result = {'case_id': control['case_id'], 'model': model, 'model_sha256': b.ir.digest(model), 'status': 'rejected-model-structure', 'code': error.code}
        results.append(result)
    base = qualify(base_model(), ids)
    if evaluate(base)[:2] != (True, True): raise ValueError('Countermodel lacks joint primary T/I')
    evaluator = v.Denotation(typed['declarations'], base); queries = []
    for query in load('query-policy.json')['queries']:
        if query['selected_in_T'] is not False or evaluator.truth(v.renamed(query['target'], ids)) is not False or evaluator.truth(v.renamed(query['witness_condition'], ids)) is not True:
            raise ValueError('Target assumed or not witnessed')
        queries.append({'query_id': query['query_id'], 'target_false': True, 'witness_condition_true': True, 'model_sha256': b.ir.digest(base), 'status': 'independently-evaluated-authored-countermodel', 'mechanized_proof': False})
    prior = json.loads((b.BASE / 'definitions/cal.definition.governed-model/delivery-manifest.json').read_bytes())
    for reference in prior['files'] + context['sources'] + bindings:
        if b.ref(b.ROOT / reference['path']) != reference: raise ValueError('Closing source/checker/prior-delivery drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Closing runtime drift')
    report = {'schema_version': 'definition-assurance-hypothesis-controls/v1-candidate', 'status': 'PASS-for-exact-authored-Hypothesis-models-and-separate-Premise-comparison',
        'authority_effect': 'none', 'semantic_ready': False, 'mechanized_proof': False, 'whole_definition_translation': 'pending', 'source_fidelity': 'pending',
        'input_refs': [b.ref(b.UNIT / name) for name in ['t.json', 'correspondence.json', 'static-ir.json', 'query-policy.json', 'comparison-input.json', 'comparison-ir.json', 'comparison-selection.json']],
        'checker_bindings': bindings, 'runtime_bindings': runtime, 'source_units': len(packet['source_units']), 'mapped_clauses': len(core['clauses']),
        'encoded_clause_ids': [x['clause_id'] for x in T], 'required_population_ids': [x['population_id'] for x in I],
        'deferred_clause_ids': correspondence['unresolved_clauses'], 'unresolved_population_ids': [x['population_id'] for x in core['populations'] if x['requirement'] == 'unresolved'],
        'separate_comparison_clause_ids': [x['clause_id'] for x in C], 'comparison_assembled_into_primary_T': False,
        'results': results, 'control_count': len(results), 'nonentailment_countermodels': queries,
        'prior_candidate_files_preserved': len(prior['files']), 'source_files_current': 201, 'external_source_files_current': 1,
        'claim_ceiling': 'Independent denotation of authored structures and four countermodel targets; separately typed inherited Premise slice. No native-provider enumeration, world-truth observation, actual investigation/adoption/promotion, whole cal.definition.premise fidelity, resolved source precedence or unbounded theorem.'}
    if write: b.put('model-controls.json', report)
    return report


def main():
    write = '--write' in b.sys.argv; result = verify(write)
    if not write and not b.r.same_json(result, load('model-controls.json')): raise ValueError('Fresh independent replay differs')
    print(json.dumps({'result': result['status'], 'controls': result['control_count'], 'nonentailment_query_outcomes': len(result['nonentailment_countermodels']),
        'source_units': result['source_units'], 'mapped_clauses': result['mapped_clauses'], 'encoded_clauses': len(result['encoded_clause_ids']),
        'deferred_clauses': len(result['deferred_clause_ids']), 'required_populations': len(result['required_population_ids']),
        'unresolved_populations': len(result['unresolved_population_ids']), 'separate_comparison_clauses': len(result['separate_comparison_clause_ids']),
        'comparison_assembled_into_primary_T': False, 'prior_candidate_files_preserved': result['prior_candidate_files_preserved'],
        'source_files_current': 201, 'external_source_files_current': 1, 'whole_translation': 'pending', 'semantic_ready': False}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
