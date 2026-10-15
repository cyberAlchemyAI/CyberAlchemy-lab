"""Independent Schema structures retain shape/outcome and level-role distinctions."""
import json
import build_candidate as b
import verifier as v


def load(name): return json.loads((b.UNIT / name).read_bytes())
def base_model():
    domains = {'Entity': ['s', 'x'], 'Level': ['data', 'meta'], 'Kind': ['k', 'other-k'],
        'LocalConstraint': ['c'], 'RelationKind': ['r'], 'ConnectionRule': ['n']}
    predicates = {name: [] for name in b.SIGNATURE}
    predicates.update(Schema=[['s']], ExplicitDeclaration=[['s']], InspectionDecidable=[['s']], OccupantIndependent=[['s']],
        SchemaUse=[['s', 'data']], OccupantAt=[['s', 'meta'], ['x', 'data']], LevelBelow=[['data', 'meta']],
        Conforms=[['x', 's', 'data']], ShapeEvidence=[['x', 's', 'data']])
    return {'domains': domains, 'constants': {}, 'functions': {
        'constraintKind': [{'args': ['c'], 'value': 'k'}], 'relationSourceKind': [{'args': ['r'], 'value': 'k'}],
        'relationTargetKind': [{'args': ['r'], 'value': 'k'}]}, 'predicates': predicates}
def local_constraint(m):
    m['predicates'].update(HasConstraint=[['s', 'c']], DecidableConstraint=[['c']], SingleOccupantConstraint=[['c']], HasKind=[['s', 'k']])
def relation(m): m['predicates'].update(HasRelation=[['s', 'r']], HasKind=[['s', 'k']])
def connection(m):
    relation(m); m['predicates'].update(HasConnectionRule=[['s', 'n']], EndpointRule=[['n']], RuleReferences=[['n', 'r']])
def controls():
    rows = []
    def add(name, change, T=True, I=True, error=None):
        model = base_model(); change(model)
        rows.append({'case_id': name, 'model': model, 'expected_T': T, 'expected_I': I, 'expected_error': error})
    add('shape-witness-without-authority-promotion-truth-ownership-or-execution', lambda m: None)
    for name in ['ExplicitDeclaration', 'InspectionDecidable', 'OccupantIndependent']:
        add('missing-' + name, lambda m, name=name: m['predicates'].__setitem__(name, []), T=False, I=False)
    add('Schema-must-declare-use-level', lambda m: m['predicates'].update(SchemaUse=[]), T=False, I=False)
    add('conformance-needs-same-declared-level', lambda m: m['predicates'].update(Conforms=[['x', 's', 'meta']], ShapeEvidence=[['x', 's', 'meta']]), T=False)
    add('conformance-needs-subject-at-governed-level', lambda m: m['predicates'].update(OccupantAt=[['s', 'meta']]), T=False)
    add('conformance-needs-shape-evidence-tag', lambda m: m['predicates'].update(ShapeEvidence=[]), T=False)
    add('no-particular-conforming-subject-required-by-primary-T', lambda m: m['predicates'].update(Conforms=[], ShapeEvidence=[], OccupantAt=[['s', 'meta']]))
    add('self-level-does-not-supply-a-distinct-upper-level', lambda m: m['predicates'].update(LevelBelow=[['data', 'data']]), T=False)
    add('unreviewed-level-cycle-not-rejected-by-static-slice', lambda m: m['predicates']['LevelBelow'].append(['meta', 'data']))
    for name in b.ROLE_USES:
        add('same-use-role-contrast-' + name, lambda m, name=name: m['predicates'].__setitem__(name, [['s', 'data']]), T=False)
    for name in ['Authoritative', 'Promoted', 'ActuallyTrue', 'Owned', 'ExecutionProven']:
        add('separate-outcome-may-coexist-' + name, lambda m, name=name: m['predicates'].__setitem__(name, [['x']]))
    add('kind-membership-owner-must-be-a-Schema', lambda m: m['predicates'].update(HasKind=[['x', 'k']]), T=False)
    add('local-constraint-with-no-relations-or-connection-rules', local_constraint)
    for name in ['DecidableConstraint', 'SingleOccupantConstraint']:
        def missing(m, name=name): local_constraint(m); m['predicates'][name] = []
        add('local-constraint-needs-' + name, missing, T=False)
    def wrong_local(m): local_constraint(m); m['functions']['constraintKind'][0]['value'] = 'other-k'
    add('constraint-kind-must-belong-to-schema', wrong_local, T=False)
    add('relation-with-no-local-constraints', relation)
    def wrong_endpoint(m): relation(m); m['functions']['relationTargetKind'][0]['value'] = 'other-k'
    add('relation-endpoint-kind-must-belong-to-schema', wrong_endpoint, T=False)
    add('connection-rule-with-declared-relation', connection)
    def no_rule_kind(m): connection(m); m['predicates']['EndpointRule'] = []
    add('connection-rule-needs-declared-rule-kind', no_rule_kind, T=False)
    def no_relation(m): connection(m); m['predicates']['HasRelation'] = []
    add('connection-reference-needs-schema-relation', no_relation, T=False)
    for name in ['MultiplicityRule', 'PathEquationRule']:
        def alone(m, name=name): connection(m); m['predicates']['EndpointRule'] = []; m['predicates'][name] = [['n']]
        add('primitive-rule-kind-' + name, alone)
    def dual(m):
        m['domains']['Entity'].append('upper'); m['domains']['Level'].append('meta-meta')
        for name in ['Schema', 'ExplicitDeclaration', 'InspectionDecidable', 'OccupantIndependent']: m['predicates'][name].append(['upper'])
        m['predicates']['SchemaUse'].append(['upper', 'meta']); m['predicates']['LevelBelow'].append(['meta', 'meta-meta'])
        m['predicates']['OccupantAt'].append(['upper', 'meta-meta'])
        m['predicates']['Conforms'].append(['s', 'upper', 'meta']); m['predicates']['ShapeEvidence'].append(['s', 'upper', 'meta'])
        m['predicates']['MetaTypeUse'] = [['s', 'meta']]
    add('same-Entity-is-schema-for-data-and-occupant-of-upper-schema', dual)
    def vacuous(m):
        for name in ['Schema', 'ExplicitDeclaration', 'InspectionDecidable', 'OccupantIndependent', 'SchemaUse', 'Conforms', 'ShapeEvidence']: m['predicates'][name] = []
    add('empty-Schema-extension-is-vacuous-T-not-required-I', vacuous, I=False)
    add('ill-sorted-relation-endpoint-function-result-rejected', lambda m: m['functions']['relationTargetKind'][0].update(value='x'), error='ill-sorted-function-result')
    add('non-total-constraint-kind-function-rejected', lambda m: m['functions']['constraintKind'].clear(), error='nontotal-function')
    add('wrong-conformance-arity-rejected', lambda m: m['predicates'].update(Conforms=[['x', 's']]), error='ill-sorted-model-tuple')
    add('duplicate-Schema-tuple-rejected', lambda m: m['predicates']['Schema'].append(['s']), error='duplicate-predicate-tuple')
    return rows
def qualify(model, ids):
    return {'domains': {ids[n]: x for n, x in model['domains'].items()}, 'constants': {},
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
    if len(T) != 16 or len(I) != 7: raise ValueError('Theory/population denominator changed')
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
    prior = json.loads((b.BASE / 'definitions/cal.definition.premise/delivery-manifest.json').read_bytes())
    for ref in prior['files'] + context['sources'] + bindings:
        if b.ref(b.ROOT / ref['path']) != ref: raise ValueError('Closing prior/input/checker drift')
    b.external_current(context); b.r.verify(snap, b.ROOT)
    if runtime != v.f.current_bindings(): raise ValueError('Runtime drift')
    report = {'schema_version': 'definition-assurance-schema-controls/v1-candidate',
        'status': 'PASS-for-exact-authored-Schema-components-levels-and-shape-models', 'authority_effect': 'none',
        'semantic_ready': False, 'mechanized_proof': False, 'whole_definition_translation': 'pending', 'source_fidelity': 'pending',
        'input_refs': [b.ref(b.UNIT / name) for name in ['t.json', 'correspondence.json', 'static-ir.json', 'query-policy.json']],
        'checker_bindings': bindings, 'runtime_bindings': runtime, 'source_units': len(packet['source_units']), 'mapped_clauses': len(core['clauses']),
        'encoded_clause_ids': [x['clause_id'] for x in T], 'required_population_ids': [x['population_id'] for x in I],
        'deferred_clause_ids': correspondence['unresolved_clauses'], 'unresolved_population_ids': [x['population_id'] for x in core['populations'] if x['requirement'] == 'unresolved'],
        'results': results, 'control_count': len(results), 'nonentailment_countermodels': queries,
        'prior_candidate_files_preserved': len(prior['files']), 'source_files_current': 201, 'external_source_files_current': 1,
        'claim_ceiling': 'Independent authored denotation and five targets outside T. Primitive decidability/shape tags are not universal inspector correctness, admitted level or role alignment, complete C/N independence, hierarchy acyclicity, migration compatibility, actual authority/truth or unbounded proof.'}
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
