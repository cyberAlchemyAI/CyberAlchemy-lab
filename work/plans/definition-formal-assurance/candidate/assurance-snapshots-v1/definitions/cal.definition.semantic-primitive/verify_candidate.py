"""Independent primitive-role models do not grant label or external authority."""
import json
import build_candidate as b
import verifier as v


def load(name): return json.loads((b.UNIT / name).read_bytes())
def base_model():
    domains = {'SemanticRole': ['t', 'u'], 'DeclaredName': ['name'], 'AuthorityScope': ['cav2', 'foreign'],
        'OwnerRole': ['governance', 'other-owner'], 'ConsumerSurface': ['consumer'], 'SourceBoundary': ['boundary'],
        'SpecializationCondition': ['rule'], 'ExternalTerm': ['external']}
    predicates = {name: [] for name in b.SIGNATURE}
    predicates.update(Primitive=[['t']], LocalBaseKind=[['t']], AuthorityScopeDeclared=[['t']], ExternalRelationDeclared=[['t']],
        NamedPrimitive=[['t'], ['u']], BorrowedFrom=[['t', 'external']], LocalRoleBoundary=[['t', 'external']])
    for name, value in zip(b.METADATA, ['name', 'consumer', 'boundary', 'rule']): predicates[name] = [['t', value]]
    return {'domains': domains, 'constants': {'CAV2Scope': 'cav2', 'DefinitionsGovernance': 'governance'},
        'functions': {'authorityScope': [{'args': ['t'], 'value': 'cav2'}, {'args': ['u'], 'value': 'foreign'}],
            'ownerRole': [{'args': ['t'], 'value': 'governance'}, {'args': ['u'], 'value': 'other-owner'}]}, 'predicates': predicates}
def controls():
    rows = []
    def add(name, change, T=True, I=True, error=None):
        model = base_model(); change(model)
        rows.append({'case_id': name, 'model': model, 'expected_T': T, 'expected_I': I, 'expected_error': error})
    add('admissible-local-role-and-unqualified-primitive-label-differ', lambda m: None)
    for name in ['LocalBaseKind', 'AuthorityScopeDeclared', 'ExternalRelationDeclared']:
        add('missing-' + name, lambda m, name=name: m['predicates'].__setitem__(name, []), T=False, I=False)
    add('narrower-derived-role-fails-admissibility', lambda m: m['predicates'].update(DerivedFromNarrower=[['t']]), T=False)
    add('foreign-scope-fails-legacy-local-condition', lambda m: m['functions']['authorityScope'][0].update(value='foreign'), T=False)
    add('other-owner-label-fails-legacy-governance-condition', lambda m: m['functions']['ownerRole'][0].update(value='other-owner'), T=False)
    for name in b.METADATA:
        add('missing-carried-' + name, lambda m, name=name: m['predicates'].__setitem__(name, []), T=False, I=False)
        add('unrelated-role-cannot-supply-' + name, lambda m, name=name: m['predicates'][name][0].__setitem__(0, 'u'), T=False, I=False)
    for name in b.BOUNDARY_ROLES:
        add('same-local-role-contrast-' + name, lambda m, name=name: m['predicates'].__setitem__(name, [['t']]), T=False)
    add('borrowed-role-needs-local-boundary', lambda m: m['predicates'].update(LocalRoleBoundary=[]), T=False)
    add('borrowed-role-cannot-claim-whole-external-meaning', lambda m: m['predicates'].update(WholeExternalMeaningClaim=[['t', 'external']]), T=False)
    add('unborrowed-local-role-does-not-require-real-external-term-use', lambda m: m['predicates'].update(BorrowedFrom=[], LocalRoleBoundary=[]))
    for name in ['Authoritative', 'ActuallyTrue', 'OwnerAuthenticated', 'LocallyReauthored']:
        add('separate-status-may-coexist-' + name, lambda m, name=name: m['predicates'].__setitem__(name, [['t']]))
    add('same-declared-name-does-not-merge-local-roles', lambda m: m['predicates']['HasStableName'].append(['u', 'name']))
    def multiple_metadata(m):
        for name, sort in b.METADATA.items():
            value = 'second-' + sort; m['domains'][sort].append(value); m['predicates'][name].append(['t', value])
    add('declared-metadata-does-not-invent-uniqueness', multiple_metadata)
    def two_external(m):
        m['domains']['ExternalTerm'].append('second-external'); m['predicates']['BorrowedFrom'].append(['t', 'second-external'])
        m['predicates']['LocalRoleBoundary'].append(['t', 'second-external'])
    add('each-borrowed-reference-has-its-local-boundary', two_external)
    add('empty-Primitive-extension-is-vacuous-theory-not-required-population', lambda m: m['predicates'].update(Primitive=[]), I=False)
    add('ill-sorted-scope-constant-rejected', lambda m: m['constants'].update(CAV2Scope='governance'), error='ill-sorted-constant')
    add('ill-sorted-scope-function-result-rejected', lambda m: m['functions']['authorityScope'][0].update(value='governance'), error='ill-sorted-function-result')
    add('non-total-owner-function-rejected', lambda m: m['functions']['ownerRole'].pop(), error='nontotal-function')
    add('wrong-borrowing-arity-rejected', lambda m: m['predicates'].update(BorrowedFrom=[['t']]), error='ill-sorted-model-tuple')
    add('duplicate-Primitive-tuple-rejected', lambda m: m['predicates']['Primitive'].append(['t']), error='duplicate-predicate-tuple')
    return rows
def qualify(model, ids):
    return {'domains': {ids[n]: x for n, x in model['domains'].items()}, 'constants': {ids[n]: x for n, x in model['constants'].items()},
        'functions': {ids[n]: x for n, x in model['functions'].items()}, 'predicates': {ids[n]: x for n, x in model['predicates'].items()}}


def verify(write=False):
    bindings = [b.ref(path) for path in [b.UNIT / 'build_candidate.py', b.UNIT / 'verify_candidate.py', b.IMPL / 'verifier.py',
        b.IMPL / 'ir.py', b.IMPL / 'contracts.py', b.BASE / 'units/A04/correspondence.py']]
    runtime = v.f.current_bindings(); context = load('context.json')
    for ref in context['sources']:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Input drift')
    b.external_current(context); snap = b.snapshot(); b.r.verify(snap, b.ROOT)
    packet, envelope, typed = load('correspondence.json'), load('t.json'), load('static-ir.json'); core = envelope['payload']
    if b.c.validate(envelope, 'interpretation')['status'] != 'structurally-valid': raise ValueError('Malformed interpretation')
    if not b.r.same_json(packet['interpretation'], core) or not b.r.same_json(typed, b.ir.compile_interpretation(core, snap)):
        raise ValueError('Interpretation/IR substitution')
    correspondence = b.co.check(packet, snap, required_dependencies=[x['version_ref'] for x in core['depends_on']],
        required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
    if not correspondence['character_accounting_complete'] or not b.r.same_json(correspondence, load('correspondence-check.json')):
        raise ValueError('Source accounting differs')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity'] != 'pending': raise ValueError('Assumption/fidelity fabricated')
    ids = {x['symbol_id']: b.ir.qualified(core['source'], core['scope'], x['symbol_id']) for x in core['declarations']}
    T = [x for x in typed['clauses'] if x['disposition'] == 'encoded']; I = [x for x in typed['populations'] if x['requirement'] == 'required']
    if len(T) != 14 or len(I) != 8: raise ValueError('Theory/population denominator changed')
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
            result = {'case_id': case['case_id'], 'model': model, 'model_sha256': b.ir.digest(model), 'status': 'independently-evaluated-authored-model',
                'primary_theory_satisfied': theory, 'required_population_satisfied': population, 'primary_clause_results': clauses, 'population_results': populations}
        except v.VerificationFault as error:
            if error.code != case['expected_error']: raise
            result = {'case_id': case['case_id'], 'model': model, 'model_sha256': b.ir.digest(model), 'status': 'rejected-model-structure', 'code': error.code}
        results.append(result)
    model = qualify(base_model(), ids); evaluator = v.Denotation(typed['declarations'], model); composed = b.ir.compose([typed]); queries = []
    if evaluate(model)[:2] != (True, True): raise ValueError('Countermodel lacks T/I')
    for query in load('query-policy.json')['queries']:
        target = v.renamed(query['target'], ids); witness = v.renamed(query['witness_condition'], ids)
        b.ir.check_composed_formula(composed, target); b.ir.check_composed_formula(composed, witness)
        if query['selected_in_T'] is not False or evaluator.truth(target) is not False or evaluator.truth(witness) is not True:
            raise ValueError('Target assumed or not witnessed')
        queries.append({'query_id': query['query_id'], 'target_false': True, 'witness_condition_true': True,
            'model_sha256': b.ir.digest(model), 'status': 'independently-evaluated-authored-countermodel', 'mechanized_proof': False})
    prior = json.loads((b.BASE / 'definitions/cal.definition.schema/delivery-manifest.json').read_bytes())
    for ref in prior['files'] + context['sources'] + bindings:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing prior/input/checker drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Runtime drift')
    report = {'schema_version': 'definition-assurance-semantic-primitive-controls/v1-candidate',
        'status': 'PASS-for-exact-authored-local-Semantic-Primitive-admissibility-models', 'authority_effect': 'none',
        'semantic_ready': False, 'mechanized_proof': False, 'whole_definition_translation': 'pending', 'source_fidelity': 'pending',
        'input_refs': [b.ref(b.UNIT / name) for name in ['t.json', 'correspondence.json', 'static-ir.json', 'query-policy.json']],
        'checker_bindings': bindings, 'runtime_bindings': runtime, 'source_units': len(packet['source_units']), 'mapped_clauses': len(core['clauses']),
        'encoded_clause_ids': [x['clause_id'] for x in T], 'required_population_ids': [x['population_id'] for x in I],
        'deferred_clause_ids': correspondence['unresolved_clauses'], 'unresolved_population_ids': [x['population_id'] for x in core['populations'] if x['requirement'] == 'unresolved'],
        'results': results, 'control_count': len(results), 'nonentailment_countermodels': queries,
        'prior_candidate_files_preserved': len(prior['files']), 'source_files_current': 201, 'external_source_files_current': 1,
        'claim_ceiling': 'Independent authored denotation and six targets outside T. Legacy scope/owner labels do not authenticate current Lab principals or authority. Nonderivation, actual local reauthoring, lower-layer preservation, external whole meaning, metadata stability/uniqueness, native-provider enumeration and unbounded proof remain unestablished.'}
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
