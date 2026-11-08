"""Independent Governed Model denotation; premises exclude all non-entailment targets."""
import copy
import itertools
import json
import build_candidate as b
import verifier as v


def load(name):
    return json.loads((b.UNIT / name).read_bytes())


def base_model():
    predicates = {name: [] for name in b.PREDICATES}
    for name in ['GovernedModel', *b.FLAGS, 'RepresentsConcepts']:
        predicates[name] = [['m']]
    return {'domains': {'Subject': ['m']}, 'constants': {}, 'functions': {}, 'predicates': predicates}


def controls():
    results = []
    def add(name, change, T=True, I=True, error=None):
        model = base_model()
        change(model)
        results.append({'case_id': name, 'model': model,
                        'expected_T': T, 'expected_I': I, 'expected_error': error})
    add('declared-model-has-no-automatic-status-or-effect', lambda model: None)
    for name in b.FLAGS:
        add('missing-' + name, lambda model, name=name: model['predicates'].__setitem__(name, []), T=False, I=False)
    def content(model, names):
        for name in b.CONTENT:
            model['predicates'][name] = [['m']] if name in names else []
    add('no-represented-content-is-rejected', lambda model: content(model, []), T=False, I=False)
    for name in b.CONTENT:
        add('only-' + name + '-can-satisfy-the-inclusive-choice', lambda model, name=name: content(model, [name]))
    for names in itertools.combinations(b.CONTENT, 2):
        add('content-overlap-' + '-'.join(names), lambda model, names=names: content(model, names))
    for name in b.OUTCOMES:
        add('abstract-overlap-with-' + name + '-is-not-forbidden',
            lambda model, name=name: model['predicates'].__setitem__(name, [['m']]))
    add('metadata-alone-does-not-force-GovernedModel',
        lambda model: model['predicates'].__setitem__('GovernedModel', []), I=False)
    def unrelated_content(model):
        model['domains']['Subject'].append('other')
        model['predicates']['RepresentsConcepts'] = [['other']]
    add('content-on-an-unrelated-subject-cannot-supply-model-content', unrelated_content, T=False, I=False)
    def unrelated_challenge(model):
        model['domains']['Subject'].append('other')
        model['predicates']['ChallengeRouteDeclared'] = [['other']]
    add('unrelated-challenge-population-does-not-satisfy-the-model-condition', unrelated_challenge, T=False)
    add('predicate-value-outside-Subject-rejected',
        lambda model: model['predicates'].__setitem__('GovernedModel', [['outside']]), error='ill-sorted-model-tuple')
    add('wrong-predicate-arity-rejected',
        lambda model: model['predicates'].__setitem__('GovernedModel', [['m', 'm']]), error='ill-sorted-model-tuple')
    add('duplicate-predicate-row-rejected',
        lambda model: model['predicates']['GovernedModel'].append(['m']), error='duplicate-predicate-tuple')
    return results


def qualify(model, ids):
    return {'domains': {ids[name]: values for name, values in model['domains'].items()},
            'constants': {}, 'functions': {},
            'predicates': {ids[name]: values for name, values in model['predicates'].items()}}


def verify(write=False):
    paths = [b.IMPL / 'verifier.py', b.IMPL / 'ir.py', b.IMPL / 'contracts.py',
             b.BASE / 'units/A04/correspondence.py', b.UNIT / 'build_candidate.py',
             b.UNIT / 'verify_candidate.py']
    bindings = [b.ref(path) for path in paths]
    runtime = v.f.current_bindings()
    context = load('context.json')
    for reference in context['sources']:
        if b.ref(b.ROOT / reference['path']) != reference:
            raise ValueError('Changed declared input')
    snap = b.snapshot()
    b.r.verify(snap, b.ROOT)
    packet, envelope, typed = load('correspondence.json'), load('t.json'), load('static-ir.json')
    core = envelope['payload']
    if b.c.validate(envelope, 'interpretation')['status'] != 'structurally-valid':
        raise ValueError('Invalid selected interpretation')
    if not b.r.same_json(packet['interpretation'], core) or not b.r.same_json(typed, b.ir.compile_interpretation(core, snap)):
        raise ValueError('Source/IR substitution')
    correspondence = b.co.check(packet, snap,
        required_dependencies=[row['version_ref'] for row in core['depends_on']],
        required_conflicts=[row['finding_id'] for row in packet['source_precedence']['conflicts']])
    if not correspondence['character_accounting_complete'] or not b.r.same_json(correspondence, load('correspondence-check.json')):
        raise ValueError('Wrong source denominator')
    if core['assumptions'] or core['source_fidelity'] != 'pending':
        raise ValueError('Fabricated assumptions or fidelity')
    ids = {row['symbol_id']: b.ir.qualified(core['source'], core['scope'], row['symbol_id']) for row in core['declarations']}
    T = [row for row in typed['clauses'] if row['disposition'] == 'encoded']
    I = [row for row in typed['populations'] if row['requirement'] == 'required']
    def evaluate(model):
        evaluator = v.Denotation(typed['declarations'], model)
        clauses = [{'clause_id': row['clause_id'], 'truth': evaluator.truth(row['formal_statement'])} for row in T]
        populations = [{'population_id': row['population_id'], 'truth': evaluator.truth(row['statement'])} for row in I]
        return all(row['truth'] for row in clauses), all(row['truth'] for row in populations), clauses, populations
    results = []
    for control in controls():
        model = qualify(control['model'], ids)
        try:
            theory, population, clauses, populations = evaluate(model)
            if control['expected_error'] is not None or theory is not control['expected_T'] or population is not control['expected_I']:
                raise ValueError('Wrong semantic control: ' + control['case_id'])
            result = {'case_id': control['case_id'], 'model': model,
                'model_sha256': b.ir.digest(model), 'status': 'independently-evaluated-authored-model',
                'theory_satisfied': theory, 'population_satisfied': population,
                'clause_results': clauses, 'population_results': populations}
        except v.VerificationFault as error:
            if error.code != control['expected_error']:
                raise
            result = {'case_id': control['case_id'], 'model': model,
                'model_sha256': b.ir.digest(model), 'status': 'rejected-model-structure',
                'code': error.code, 'theory_satisfied': None, 'population_satisfied': None}
        results.append(result)
    base = qualify(base_model(), ids)
    if evaluate(base)[:2] != (True, True):
        raise ValueError('Non-entailment base must satisfy joint T and required I')
    evaluator = v.Denotation(typed['declarations'], base)
    queries = []
    for query in load('query-policy.json')['queries']:
        target = v.renamed(query['target'], ids)
        condition = v.renamed(query['witness_condition'], ids)
        if query['selected_in_T'] is not False or evaluator.truth(target) is not False or evaluator.truth(condition) is not True:
            raise ValueError('Non-entailment target assumed or not witnessed')
        queries.append({'query_id': query['query_id'], 'target_false': True,
            'witness_condition_true': True, 'model_sha256': b.ir.digest(base),
            'status': 'independently-evaluated-authored-countermodel', 'mechanized_proof': False})
    prior = json.loads((b.BASE / 'definitions/cal.definition.definition/delivery-manifest.json').read_bytes())
    for reference in prior['files'] + context['sources'] + bindings:
        if b.ref(b.ROOT / reference['path']) != reference:
            raise ValueError('Closing source/checker/prior-delivery drift')
    b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings():
        raise ValueError('Closing runtime drift')
    report = {'schema_version': 'definition-assurance-governed-model-controls/v1-candidate',
        'status': 'PASS-for-exact-authored-subject-models-and-query-separation',
        'authority_effect': 'none', 'semantic_ready': False, 'mechanized_proof': False,
        'whole_definition_translation': 'pending', 'source_fidelity': 'pending',
        'input_refs': [b.ref(b.UNIT / name) for name in ['t.json', 'correspondence.json', 'static-ir.json', 'query-policy.json']],
        'checker_bindings': bindings, 'runtime_bindings': runtime,
        'source_units': len(packet['source_units']), 'mapped_clauses': len(core['clauses']),
        'encoded_clause_ids': [row['clause_id'] for row in T],
        'required_population_ids': [row['population_id'] for row in I],
        'deferred_clause_ids': correspondence['unresolved_clauses'],
        'unresolved_population_ids': [row['population_id'] for row in core['populations'] if row['requirement'] == 'unresolved'],
        'results': results, 'control_count': len(results), 'nonentailment_countermodels': queries,
        'prior_candidate_files_preserved': len(prior['files']), 'source_files_current': 201,
        'claim_ceiling': 'Independent denotation of exact authored finite structures and seven non-entailment targets. No native-provider search, canonical carrier/instance validity, actual model admission, consumer compliance, universal use coverage, fidelity or unbounded theorem.'}
    if write:
        b.put('model-controls.json', report)
    return report


def main():
    write = '--write' in b.sys.argv
    result = verify(write)
    if not write and not b.r.same_json(result, load('model-controls.json')):
        raise ValueError('Fresh independent replay differs')
    print(json.dumps({'result': result['status'], 'controls': result['control_count'],
        'nonentailment_query_outcomes': len(result['nonentailment_countermodels']),
        'source_units': result['source_units'], 'mapped_clauses': result['mapped_clauses'],
        'encoded_clauses': len(result['encoded_clause_ids']),
        'deferred_clauses': len(result['deferred_clause_ids']),
        'required_populations': len(result['required_population_ids']),
        'unresolved_populations': len(result['unresolved_population_ids']),
        'prior_candidate_files_preserved': result['prior_candidate_files_preserved'],
        'source_files_current': 201, 'whole_translation': 'pending',
        'semantic_ready': False}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
