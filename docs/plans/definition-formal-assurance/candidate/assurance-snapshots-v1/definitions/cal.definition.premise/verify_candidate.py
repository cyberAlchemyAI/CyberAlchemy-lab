"""Independent Premise denotation: contextual adoption is not proposition truth."""
import json
import build_candidate as b
import verifier as v


def load(name): return json.loads((b.UNIT / name).read_bytes())
def base_model():
    domains = {'RoleInstance': ['m'], 'Proposition': ['p'], 'ReasoningContext': ['c'],
        'EvidencePosture': ['ep'], 'ConvictionPosture': ['cv'], 'RevisionRoute': ['rr'], 'RetirementCondition': ['rc']}
    predicates = {name: [] for name in b.SIGNATURE}
    predicates.update(Premise=[['m']], LoadBearing=[['m']], Stated=[['m']],
        AdoptedToProceed=[['p', 'c']], Defeasible=[['p', 'c']])
    for name, value in zip(b.METADATA, ['ep', 'cv', 'rr', 'rc']): predicates[name] = [['m', value]]
    return {'domains': domains, 'constants': {}, 'functions': {'propositionOf': [{'args': ['m'], 'value': 'p'}],
        'contextOf': [{'args': ['m'], 'value': 'c'}]}, 'predicates': predicates}
def add_role(model, name='h', context='c'):
    model['domains']['RoleInstance'].append(name)
    if context not in model['domains']['ReasoningContext']: model['domains']['ReasoningContext'].append(context)
    model['functions']['propositionOf'].append({'args': [name], 'value': 'p'})
    model['functions']['contextOf'].append({'args': [name], 'value': context})
def controls():
    rows = []
    def add(name, change, T=True, I=True, error=None):
        model = base_model(); change(model)
        rows.append({'case_id': name, 'model': model, 'expected_T': T, 'expected_I': I, 'expected_error': error})
    add('working-adoption-without-assigned-truth-or-typical-values', lambda m: None)
    for name in ['AdoptedToProceed', 'Defeasible', 'LoadBearing']:
        add('missing-' + name, lambda m, name=name: m['predicates'].__setitem__(name, []), T=False, I=False)
    add('established-status-conflicts-with-unestablished-role', lambda m: m['predicates'].update(EstablishedTrue=[['p', 'c']]), T=False)
    for name in b.METADATA:
        add('missing-carried-' + name, lambda m, name=name: m['predicates'].__setitem__(name, []), T=False, I=False)
        def unrelated(m, name=name):
            add_role(m); m['predicates'][name][0][0] = 'h'
        add('unrelated-role-cannot-supply-' + name, unrelated, T=False, I=False)
    for name in ['AxiomRole', 'InvariantRole', 'DisposableHypothesis']:
        add('same-carrier-role-contrast-' + name, lambda m, name=name: m['predicates'].__setitem__(name, [['m']]), T=False)
    add('Premise-may-be-actually-true-without-establishment', lambda m: m['predicates'].update(ActuallyTrue=[['p']]))
    add('high-conviction-alone-does-not-establish-truth', lambda m: m['predicates'].update(ConvictionHigh=[['p', 'c']]))
    add('low-veracity-alone-without-high-conviction', lambda m: m['predicates'].update(VeracityLow=[['p', 'c']]))
    add('typical-low-veracity-high-conviction-without-truth', lambda m: m['predicates'].update(VeracityLow=[['p', 'c']], ConvictionHigh=[['p', 'c']]))
    add('private-investigation-role-tag-is-not-universally-excluded', lambda m: m['predicates'].update(HypothesisRole=[['m']]))
    def investigation_elsewhere(m): add_role(m, context='investigation'); m['predicates']['HypothesisRole'] = [['h']]
    add('same-proposition-has-different-contextual-role-instances', investigation_elsewhere)
    def moved_status(m, name):
        m['domains']['ReasoningContext'].append('other'); m['predicates'][name] = [['p', 'other']]
    for name in ['AdoptedToProceed', 'Defeasible']:
        add('other-context-does-not-supply-' + name, lambda m, name=name: moved_status(m, name), T=False, I=False)
    add('established-in-other-context-does-not-set-current-status', lambda m: moved_status(m, 'EstablishedTrue'))
    add('empty-Premise-population-is-vacuous-theory-not-required-inhabitation', lambda m: m['predicates'].update(Premise=[]), I=False)
    add('Stated-tag-does-not-select-content-as-metatheory-assumption', lambda m: m['predicates'].update(Stated=[]))
    def multiple_metadata(m):
        for name, sort in b.METADATA.items():
            value = 'second-' + sort; m['domains'][sort].append(value); m['predicates'][name].append(['m', value])
    add('metadata-presence-does-not-invent-uniqueness', multiple_metadata)
    add('ill-sorted-context-function-result-rejected', lambda m: m['functions']['contextOf'][0].update(value='p'), error='ill-sorted-function-result')
    add('non-total-proposition-function-rejected', lambda m: m['functions']['propositionOf'].clear(), error='nontotal-function')
    add('wrong-revision-route-relation-arity-rejected', lambda m: m['predicates'].update(HasRevisionRoute=[['m']]), error='ill-sorted-model-tuple')
    add('duplicate-Premise-tuple-rejected', lambda m: m['predicates']['Premise'].append(['m']), error='duplicate-predicate-tuple')
    return rows
def qualify(model, ids):
    return {'domains': {ids[n]: x for n, x in model['domains'].items()}, 'constants': {},
        'functions': {ids[n]: x for n, x in model['functions'].items()}, 'predicates': {ids[n]: x for n, x in model['predicates'].items()}}


def verify(write=False):
    refs = [b.ref(path) for path in [b.IMPL / 'verifier.py', b.IMPL / 'ir.py', b.IMPL / 'contracts.py',
        b.BASE / 'units/A04/correspondence.py', b.UNIT / 'build_candidate.py', b.UNIT / 'verify_candidate.py']]
    runtime = v.f.current_bindings(); context = load('context.json')
    for ref in context['sources']:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Input drift')
    b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    packet, envelope, typed = load('correspondence.json'), load('t.json'), load('static-ir.json'); core = envelope['payload']
    if b.c.validate(envelope, 'interpretation')['status'] != 'structurally-valid': raise ValueError('Malformed interpretation')
    if not b.r.same_json(packet['interpretation'], core) or not b.r.same_json(typed, b.ir.compile_interpretation(core, snap)):
        raise ValueError('IR/interpretation substitution')
    correspondence = b.co.check(packet, snap, required_dependencies=[x['version_ref'] for x in core['depends_on']],
        required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
    if not correspondence['character_accounting_complete'] or not b.r.same_json(correspondence, load('correspondence-check.json')):
        raise ValueError('Source accounting differs')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending': raise ValueError('Underlying proposition adopted or fidelity fabricated')
    ids = {x['symbol_id']: b.ir.qualified(core['source'], core['scope'], x['symbol_id']) for x in core['declarations']}
    T = [x for x in typed['clauses'] if x['disposition'] == 'encoded']; I = [x for x in typed['populations'] if x['requirement'] == 'required']
    if len(T) != 9 or len(I) != 8: raise ValueError('Theory/population denominator changed')
    def evaluate(model):
        evaluator = v.Denotation(typed['declarations'], model)
        clauses = [{'clause_id': x['clause_id'], 'truth': evaluator.truth(x['formal_statement'])} for x in T]
        populations = [{'population_id': x['population_id'], 'truth': evaluator.truth(x['statement'])} for x in I]
        return all(x['truth'] for x in clauses), all(x['truth'] for x in populations), clauses, populations
    results = []
    for case in controls():
        model = qualify(case['model'], ids)
        try:
            theory, population, clauses, populations = evaluate(model)
            if case['expected_error'] is not None or (theory, population) != (case['expected_T'], case['expected_I']):
                raise ValueError('Wrong authored control: ' + case['case_id'] + ' ' + str((theory, population)))
            result = {'case_id': case['case_id'], 'model': model, 'model_sha256': b.ir.digest(model),
                'status': 'independently-evaluated-authored-model', 'primary_theory_satisfied': theory,
                'required_population_satisfied': population, 'primary_clause_results': clauses, 'population_results': populations}
        except v.VerificationFault as error:
            if error.code != case['expected_error']: raise
            result = {'case_id': case['case_id'], 'model': model, 'model_sha256': b.ir.digest(model), 'status': 'rejected-model-structure', 'code': error.code}
        results.append(result)
    model = qualify(base_model(), ids); evaluator = v.Denotation(typed['declarations'], model); queries = []
    if evaluate(model)[:2] != (True, True): raise ValueError('Countermodel lacks joint T/I')
    composed = b.ir.compose([typed])
    for query in load('query-policy.json')['queries']:
        target = v.renamed(query['target'], ids); witness = v.renamed(query['witness_condition'], ids)
        b.ir.check_composed_formula(composed, target); b.ir.check_composed_formula(composed, witness)
        if query['selected_in_T'] is not False or evaluator.truth(target) is not False or evaluator.truth(witness) is not True:
            raise ValueError('Target assumed or not witnessed')
        queries.append({'query_id': query['query_id'], 'target_false': True, 'witness_condition_true': True,
            'model_sha256': b.ir.digest(model), 'status': 'independently-evaluated-authored-countermodel', 'mechanized_proof': False})
    prior = json.loads((b.BASE / 'definitions/cal.definition.invariant/delivery-manifest.json').read_bytes())
    for ref in prior['files'] + context['sources'] + refs:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing source/checker/prior drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Runtime drift')
    report = {'schema_version': 'definition-assurance-premise-controls/v1-candidate',
        'status': 'PASS-for-exact-authored-Premise-context-and-carried-metadata-models', 'authority_effect': 'none',
        'semantic_ready': False, 'mechanized_proof': False, 'whole_definition_translation': 'pending', 'source_fidelity': 'pending',
        'input_refs': [b.ref(b.UNIT / name) for name in ['t.json', 'correspondence.json', 'static-ir.json', 'query-policy.json']],
        'checker_bindings': refs, 'runtime_bindings': runtime, 'source_units': len(packet['source_units']), 'mapped_clauses': len(core['clauses']),
        'encoded_clause_ids': [x['clause_id'] for x in T], 'required_population_ids': [x['population_id'] for x in I],
        'deferred_clause_ids': correspondence['unresolved_clauses'], 'unresolved_population_ids': [x['population_id'] for x in core['populations'] if x['requirement'] == 'unresolved'],
        'results': results, 'control_count': len(results), 'nonentailment_countermodels': queries,
        'prior_candidate_files_preserved': len(prior['files']), 'source_files_current': 201, 'external_source_files_current': 1,
        'claim_ceiling': 'Independent authored models and four targets outside T. Concept membership/contextual adoption do not select the represented proposition as a metatheory assumption or prove it true. No admitted metadata schema, working lifecycle, qualitative distribution, global Hypothesis relation, native-provider enumeration or unbounded theorem.'}
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
