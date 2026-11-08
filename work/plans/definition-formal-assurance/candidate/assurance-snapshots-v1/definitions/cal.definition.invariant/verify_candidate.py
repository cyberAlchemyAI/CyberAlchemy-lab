"""Independent denotation separates invariant requirement from actual satisfaction."""
import copy
import json
import build_candidate as b
import verifier as v


def load(name): return json.loads((b.UNIT / name).read_bytes())
def base_model():
    predicates = {name: [] for name in b.SIGNATURE}
    predicates.update(Invariant=[['i']], Checkable=[['i']], OwnSystemCondition=[['i']],
        SingleCondition=[['i']], StatePoint=[['p0']], InScope=[['i', 'p0']],
        MustHold=[['i', 'p0']], Holds=[['i', 'p0']])
    return {'domains': {'Specification': ['i'], 'System': ['sys0', 'sys1'], 'Point': ['p0'], 'OwnerRoute': ['o']},
        'constants': {}, 'functions': {'subjectOf': [{'args': ['i'], 'value': 'sys0'}],
            'pointSubject': [{'args': ['p0'], 'value': 'sys0'}]}, 'predicates': predicates}
def breach(model, diagnosis='Defect'):
    model['predicates'].update(Holds=[], Violation=[['i', 'p0']])
    model['predicates'][diagnosis] = [['i', 'p0']]
def controls():
    rows = []
    def add(name, change, T=True, I=True, error=None):
        model = base_model(); change(model)
        rows.append({'case_id': name, 'model': model, 'expected_T': T, 'expected_I': I, 'expected_error': error})
    add('required-and-satisfied-without-governance', lambda m: None)
    for name in ['Checkable', 'OwnSystemCondition', 'SingleCondition']:
        add('missing-' + name, lambda m, name=name: m['predicates'].__setitem__(name, []), T=False, I=False)
    add('missing-MustHold-is-not-supplied-by-Holds', lambda m: m['predicates'].update(MustHold=[]), T=False)
    add('empty-scope-vacuous-theory-fails-required-witness', lambda m: m['predicates'].update(InScope=[]), I=False)
    add('empty-Invariant-vacuous-theory-fails-required-witness', lambda m: m['predicates'].update(Invariant=[]), I=False)
    add('foreign-system-point-cannot-supply-owned-scope', lambda m: m['functions']['pointSubject'][0].update(value='sys1'), T=False)
    add('scoped-point-needs-a-declared-kind', lambda m: m['predicates'].update(StatePoint=[]), T=False)
    for name in b.POINT_FLAGS[1:]:
        add('only-point-kind-' + name, lambda m, name=name: m['predicates'].update(StatePoint=[], **{name: [['p0']]}))
    add('point-kinds-may-overlap-in-this-candidate', lambda m: m['predicates'].update(TransitionPoint=[['p0']]))
    for name in ['AxiomRole', 'ConstitutionRole', 'ValidatorRole', 'GateRole']:
        add('same-carrier-role-contrast-' + name, lambda m, name=name: m['predicates'].__setitem__(name, [['i']]), T=False)
    add('governance-active-without-route-rejected', lambda m: m['predicates'].update(GovernanceActive=[['i']]), T=False)
    add('governance-active-with-declared-route-is-only-metadata', lambda m: m['predicates'].update(GovernanceActive=[['i']], RoutedThrough=[['i', 'o']]))
    add('route-alone-does-not-force-governance', lambda m: m['predicates'].update(RoutedThrough=[['i', 'o']]))
    add('requirement-remains-valid-with-defect', lambda m: breach(m))
    add('requirement-remains-valid-with-drift', lambda m: breach(m, 'Drift'))
    def both(m): breach(m); m['predicates']['Drift'] = [['i', 'p0']]
    add('drift-and-defect-inclusive-or', both)
    add('unsatisfied-scope-without-breach-tag-rejected', lambda m: m['predicates'].update(Holds=[]), T=False)
    add('breach-without-diagnostic-tag-rejected', lambda m: m['predicates'].update(Holds=[], Violation=[['i', 'p0']]), T=False)
    add('satisfied-point-cannot-be-labelled-scoped-breach', lambda m: m['predicates'].update(Violation=[['i', 'p0']], Defect=[['i', 'p0']]), T=False)
    def outside(m):
        m['domains']['Point'].append('outside')
        m['functions']['pointSubject'].append({'args': ['outside'], 'value': 'sys1'})
    add('out-of-scope-unsatisfaction-is-not-a-scoped-breach', outside)
    def wrong(m): outside(m); m['predicates'].update(Violation=[['i', 'outside']], Defect=[['i', 'outside']])
    add('out-of-scope-breach-label-rejected', wrong, T=False)
    add('ill-sorted-system-function-result-rejected', lambda m: m['functions']['subjectOf'][0].update(value='p0'), error='ill-sorted-function-result')
    add('non-total-point-subject-rejected', lambda m: m['functions']['pointSubject'].clear(), error='nontotal-function')
    add('wrong-InScope-arity-rejected', lambda m: m['predicates'].update(InScope=[['i']]), error='ill-sorted-model-tuple')
    add('duplicate-Invariant-tuple-rejected', lambda m: m['predicates']['Invariant'].append(['i']), error='duplicate-predicate-tuple')
    return rows
def qualify(model, ids):
    return {'domains': {ids[n]: x for n, x in model['domains'].items()}, 'constants': {},
        'functions': {ids[n]: x for n, x in model['functions'].items()},
        'predicates': {ids[n]: x for n, x in model['predicates'].items()}}


def verify(write=False):
    bindings = [b.ref(path) for path in [b.IMPL / 'verifier.py', b.IMPL / 'ir.py', b.IMPL / 'contracts.py',
        b.BASE / 'units/A04/correspondence.py', b.UNIT / 'build_candidate.py', b.UNIT / 'verify_candidate.py']]
    runtime = v.f.current_bindings(); context = load('context.json')
    for ref in context['sources']:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Declared input drift')
    b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    packet, envelope, typed = load('correspondence.json'), load('t.json'), load('static-ir.json'); core = envelope['payload']
    if b.c.validate(envelope, 'interpretation')['status'] != 'structurally-valid': raise ValueError('Malformed interpretation')
    if not b.r.same_json(packet['interpretation'], core) or not b.r.same_json(typed, b.ir.compile_interpretation(core, snap)):
        raise ValueError('Interpretation/IR substitution')
    correspondence = b.co.check(packet, snap, required_dependencies=[x['version_ref'] for x in core['depends_on']],
        required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
    if not correspondence['character_accounting_complete'] or not b.r.same_json(correspondence, load('correspondence-check.json')):
        raise ValueError('Wrong source denominator')
    if core['assumptions'] or core['source_fidelity'] != 'pending': raise ValueError('Fabricated assumption or fidelity')
    ids = {x['symbol_id']: b.ir.qualified(core['source'], core['scope'], x['symbol_id']) for x in core['declarations']}
    T = [x for x in typed['clauses'] if x['disposition'] == 'encoded']; I = [x for x in typed['populations'] if x['requirement'] == 'required']
    if len(T) != 11 or len(I) != 5: raise ValueError('Theory/population denominator changed')
    def evaluate(model):
        evaluator = v.Denotation(typed['declarations'], model)
        clauses = [{'clause_id': x['clause_id'], 'truth': evaluator.truth(x['formal_statement'])} for x in T]
        populations = [{'population_id': x['population_id'], 'truth': evaluator.truth(x['statement'])} for x in I]
        return all(x['truth'] for x in clauses), all(x['truth'] for x in populations), clauses, populations
    results = []
    for control in controls():
        model = qualify(control['model'], ids)
        try:
            theory, population, clauses, populations = evaluate(model)
            if control['expected_error'] is not None or (theory, population) != (control['expected_T'], control['expected_I']):
                raise ValueError('Wrong control: ' + control['case_id'] + ' ' + str((theory, population)))
            result = {'case_id': control['case_id'], 'model': model, 'model_sha256': b.ir.digest(model),
                'status': 'independently-evaluated-authored-model', 'primary_theory_satisfied': theory,
                'required_population_satisfied': population, 'primary_clause_results': clauses, 'population_results': populations}
        except v.VerificationFault as error:
            if error.code != control['expected_error']: raise
            result = {'case_id': control['case_id'], 'model': model, 'model_sha256': b.ir.digest(model), 'status': 'rejected-model-structure', 'code': error.code}
        results.append(result)
    queries = []
    for index, query in enumerate(load('query-policy.json')['queries']):
        local = base_model()
        if index == 1: breach(local)
        model = qualify(local, ids); evaluator = v.Denotation(typed['declarations'], model)
        if evaluate(model)[:2] != (True, True) or query['selected_in_T'] is not False:
            raise ValueError('Countermodel lacks T/I or target assumed')
        target = v.renamed(query['target'], ids); witness = v.renamed(query['witness_condition'], ids)
        composed = b.ir.compose([typed]); b.ir.check_composed_formula(composed, target); b.ir.check_composed_formula(composed, witness)
        if evaluator.truth(target) is not False or evaluator.truth(witness) is not True: raise ValueError('Countermodel target not witnessed')
        queries.append({'query_id': query['query_id'], 'target_false': True, 'witness_condition_true': True,
            'model_sha256': b.ir.digest(model), 'status': 'independently-evaluated-authored-countermodel', 'mechanized_proof': False})
    prior = json.loads((b.BASE / 'definitions/cal.definition.hypothesis/delivery-manifest.json').read_bytes())
    for ref in prior['files'] + context['sources'] + bindings:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing source/checker/prior drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Closing runtime drift')
    report = {'schema_version': 'definition-assurance-invariant-controls/v1-candidate',
        'status': 'PASS-for-exact-authored-Invariant-requirement-and-breach-models', 'authority_effect': 'none',
        'semantic_ready': False, 'mechanized_proof': False, 'whole_definition_translation': 'pending', 'source_fidelity': 'pending',
        'input_refs': [b.ref(b.UNIT / name) for name in ['t.json', 'correspondence.json', 'static-ir.json', 'query-policy.json']],
        'checker_bindings': bindings, 'runtime_bindings': runtime, 'source_units': len(packet['source_units']), 'mapped_clauses': len(core['clauses']),
        'encoded_clause_ids': [x['clause_id'] for x in T], 'required_population_ids': [x['population_id'] for x in I],
        'deferred_clause_ids': correspondence['unresolved_clauses'], 'unresolved_population_ids': [x['population_id'] for x in core['populations'] if x['requirement'] == 'unresolved'],
        'results': results, 'control_count': len(results), 'nonentailment_countermodels': queries,
        'prior_candidate_files_preserved': len(prior['files']), 'source_files_current': 201, 'external_source_files_current': 1,
        'claim_ceiling': 'Independent authored-structure denotation and two targets outside T. MustHold metadata is not actual satisfaction, deontic necessity, temporal proof, native-provider enumeration, owner authorization or live-system compliance.'}
    if write: b.put('model-controls.json', report)
    return report


def main():
    write = '--write' in b.sys.argv; report = verify(write)
    if not write and not b.r.same_json(report, load('model-controls.json')): raise ValueError('Fresh model evidence differs')
    print(json.dumps({'result': report['status'], 'controls': report['control_count'], 'nonentailment_query_outcomes': len(report['nonentailment_countermodels']),
        'source_units': report['source_units'], 'mapped_clauses': report['mapped_clauses'], 'encoded_clauses': len(report['encoded_clause_ids']),
        'deferred_clauses': len(report['deferred_clause_ids']), 'required_populations': len(report['required_population_ids']),
        'unresolved_populations': len(report['unresolved_population_ids']), 'prior_candidate_files_preserved': report['prior_candidate_files_preserved'],
        'source_files_current': 201, 'external_source_files_current': 1, 'whole_translation': 'pending', 'semantic_ready': False}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
