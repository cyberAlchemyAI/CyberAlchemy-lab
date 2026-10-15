"""Schema shape, local constraints, connections, relative levels and claim limits."""
import hashlib
import json
import sys
from pathlib import Path
UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[6]; BASE = UNIT.parents[1]
IMPL = ROOT / 'craft/formalization/candidates/definition-assurance-v1'
sys.path[:0] = [str(IMPL), str(BASE / 'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co

SCOPE = 'scope:candidate:schema-structure-v1'
SORTS = ['Entity', 'Level', 'Kind', 'LocalConstraint', 'RelationKind', 'ConnectionRule']
FIELDS = {'constraintKind': ('LocalConstraint', 'Kind'), 'relationSourceKind': ('RelationKind', 'Kind'), 'relationTargetKind': ('RelationKind', 'Kind')}
UNARY = {n: 'Entity' for n in ['Schema', 'ExplicitDeclaration', 'InspectionDecidable', 'OccupantIndependent', 'Authoritative', 'Promoted', 'ActuallyTrue', 'Owned', 'ExecutionProven']}
UNARY.update({n: 'LocalConstraint' for n in ['DecidableConstraint', 'SingleOccupantConstraint']})
UNARY.update({n: 'ConnectionRule' for n in ['EndpointRule', 'MultiplicityRule', 'PathEquationRule']})
ROLE_USES = ['AxiomUse', 'InvariantUse', 'TruthLawUse', 'AuthorityUse', 'PromotionUse', 'ExecutionProofUse', 'ContractUse', 'ClassificationFacetUse', 'PrimitiveTypeUse', 'MetaTypeUse']
RELATIONS = {'SchemaUse': ['Entity', 'Level'], 'OccupantAt': ['Entity', 'Level'], 'LevelBelow': ['Level', 'Level'],
    'HasKind': ['Entity', 'Kind'], 'HasConstraint': ['Entity', 'LocalConstraint'], 'HasRelation': ['Entity', 'RelationKind'],
    'HasConnectionRule': ['Entity', 'ConnectionRule'], 'RuleReferences': ['ConnectionRule', 'RelationKind'],
    'Conforms': ['Entity', 'Entity', 'Level'], 'ShapeEvidence': ['Entity', 'Entity', 'Level']}
RELATIONS.update({n: ['Entity', 'Level'] for n in ROLE_USES})
SIGNATURE = {n: [sort] for n, sort in UNARY.items()}; SIGNATURE.update(RELATIONS)


def var(name): return {'op': 'var', 'name': name}
def fn(name, arg): return {'op': 'fn', 'name': name, 'args': [var(arg)]}
def pred(name, *args): return {'op': 'pred', 'name': name, 'args': [var(x) if isinstance(x, str) else x for x in args]}
def both(*args): return {'op': 'and', 'args': list(args)}
def either(*args): return {'op': 'or', 'args': list(args)}
def neg(arg): return {'op': 'not', 'arg': arg}
def implies(left, right): return {'op': 'implies', 'left': left, 'right': right}
def eq(left, right): return {'op': 'eq', 'left': left, 'right': right}
def quant(op, sort, name, body): return {'op': op, 'sort': sort, 'var': name, 'body': body}
def forall(sort, name, body): return quant('forall', sort, name, body)
def exists(sort, name, body): return quant('exists', sort, name, body)
GENUS = forall('Entity', 's', implies(pred('Schema', 's'), both(pred('ExplicitDeclaration', 's'), pred('InspectionDecidable', 's'),
    pred('OccupantIndependent', 's'), exists('Level', 'l', pred('SchemaUse', 's', 'l')))))
LOCAL = forall('Entity', 's', forall('LocalConstraint', 'c', implies(pred('HasConstraint', 's', 'c'), both(pred('Schema', 's'),
    pred('DecidableConstraint', 'c'), pred('SingleOccupantConstraint', 'c'), pred('HasKind', 's', fn('constraintKind', 'c'))))))
ENDPOINTS = forall('Entity', 's', forall('RelationKind', 'r', implies(pred('HasRelation', 's', 'r'), both(pred('Schema', 's'),
    pred('HasKind', 's', fn('relationSourceKind', 'r')), pred('HasKind', 's', fn('relationTargetKind', 'r'))))))
CONNECTIONS = forall('Entity', 's', forall('ConnectionRule', 'n', implies(pred('HasConnectionRule', 's', 'n'), both(pred('Schema', 's'),
    either(*(pred(name, 'n') for name in ['EndpointRule', 'MultiplicityRule', 'PathEquationRule'])),
    forall('RelationKind', 'r', implies(pred('RuleReferences', 'n', 'r'), pred('HasRelation', 's', 'r')))))))
KIND_PART = forall('Entity', 's', forall('Kind', 'k', implies(pred('HasKind', 's', 'k'), pred('Schema', 's'))))
STRUCTURE = both(GENUS, KIND_PART, LOCAL, ENDPOINTS, CONNECTIONS)
LEVEL_USE = forall('Entity', 's', forall('Level', 'l', implies(pred('SchemaUse', 's', 'l'), both(pred('Schema', 's'),
    exists('Level', 'h', both(pred('LevelBelow', 'l', 'h'), neg(eq(var('l'), var('h'))), pred('OccupantAt', 's', 'h')))))))
CONFORMANCE = forall('Entity', 'x', forall('Entity', 's', forall('Level', 'l', implies(pred('Conforms', 'x', 's', 'l'),
    both(pred('SchemaUse', 's', 'l'), pred('OccupantAt', 'x', 'l'), pred('ShapeEvidence', 'x', 's', 'l'))))))
def excludes(names):
    return forall('Entity', 's', forall('Level', 'l', implies(pred('SchemaUse', 's', 'l'), both(*(neg(pred(n, 's', 'l')) for n in names)))))
BOUNDARIES = [excludes(ROLE_USES[:3]), excludes(ROLE_USES[3:6]), excludes(['ContractUse']), excludes(['ClassificationFacetUse']), excludes(ROLE_USES[8:])]


def ref(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def put(name, value):
    with (UNIT / name).open('x') as stream: json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')
    return ref(UNIT / name)
def snapshot(): return json.loads((BASE / 'current-snapshot.json').read_bytes())
def source_ref(snap, identity):
    x = next(x for x in snap['current_entries'] if x['definition_id'] == identity)
    return {k: x[k] for k in ['definition_id', 'version_ref', 'path', 'sha256']}
def external_current(context):
    for x in context['external_sources']:
        path = Path(x['absolute_path'])
        if r.digest(r.read_bytes(path.parents[2], 'authority/definitions/DEFINITIONS.md')) != x['sha256']: raise ValueError('Selected external source drift')
def cuts(text, markers):
    offsets = [0, *[text.index(marker) for marker in markers], len(text)]
    if sorted(set(offsets)) != offsets: raise ValueError('Unordered/nonunique source cuts')
    return list(zip(offsets, offsets[1:]))


def main():
    context = json.loads((UNIT / 'context.json').read_bytes())
    for x in context['sources']:
        if ref(ROOT / x['path']) != x: raise ValueError('Changed declared task input')
    external_current(context); snap = snapshot(); r.verify(snap, ROOT)
    source = source_ref(snap, 'cal.definition.schema'); document = co.source_document(snap, source); units = co.inventory(document)
    texts = dict(co.string_leaves(document)); clauses, links, views = [], [], []
    N = '/voices/scientific_formal/normative_statement'; F = '/voices/scientific_formal/formal_expression'; Bs = ['/boundaries/0', '/voices/scientific_formal/boundary_conditions/0']
    for unit in units:
        selector = unit['selector']; text = texts[selector]; spans = [(0, len(text))]
        if selector == N: spans = cuts(text, ['Bound source-semantic basis:', 'Constraints and connection rules', 'A schema is stated **independently', 'Conformance is therefore'])
        elif selector == F: spans = cuts(text, ['conforms(x, S)   decidable', 'conforms(x, S)  =/=>', 'The parts are independent.', 'A schema is **relative to a level**'])
        elif selector in Bs: spans = cuts(text, ['A schema is not authority', 'It is not a\n**contract**', 'It is not the\n**classification facet**', 'It\nis not a `CAV2-D31`'])
        for index, (start, end) in enumerate(spans):
            excerpt = text[start:end]; formula = None
            disposition, roles, forms = 'deferred', ['proof-obligation'], ['non-definitional']
            rationale = 'Artifact/carrier, complete decidability, C/N nonreduction/independence, non-entailment, scope or operational/profile requirement remains explicit without assuming universal proof or authority.'
            if selector in Bs:
                formula = BOUNDARIES[index]; disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Candidate same-use role contrast at the declared governed level. Private role tags require counterpart/level alignment; schema use is not a truth-law, authority, proof, contract, classifier or kind use. Outcome truth/ownership/approval are not universally forbidden.'
            elif selector == N and index in [1, 3, 4]:
                formula = {1: STRUCTURE, 3: GENUS, 4: CONFORMANCE}[index]
                disposition, roles, forms = 'encoded', ['definition'], ['genus-differentia', 'axiomatic-implicit']
                rationale = 'Candidate explicit occupant-independent structural declaration, typed optional component memberships, primitive inspection-decidability metadata and shape-evidence conformance. No implemented general decider or truth/authority inference follows.'
            elif selector == F and index in [0, 1, 4]:
                formula = {0: STRUCTURE, 1: CONFORMANCE, 4: LEVEL_USE}[index]
                disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Typed structure/conformance or declared relative-level use with an upper-level occupant. Levels and kind/function/rule contents are candidate abstractions; strict hierarchy, full path algebra and actual evaluator correctness remain open.'
            elif selector.startswith('/voices/plain_language/') or selector.startswith('/voices/domain_context/') or selector.startswith('/voices/scientific_formal/notation/'):
                disposition, roles, forms = 'explanatory', ['explanation-example'], ['non-definitional']
                rationale = 'Non-normative intuition, context examples, metadata and notation retained without runtime observations, authority or selected assumptions.'
            cid = 'SCH-' + str(len(clauses) + 1).zfill(3)
            clauses.append({'clause_id': cid, 'source_selector': selector, 'excerpt_sha256': hashlib.sha256(excerpt.encode()).hexdigest(),
                'start_character': start, 'disposition': disposition, 'forms': forms, 'roles': roles, 'formal_statement': formula, 'rationale': rationale})
            links.append({'unit_id': unit['unit_id'], 'clause_id': cid, 'end_character': end, 'excerpt': excerpt})
            views.append({'clause_id': cid, 'source_selector': selector, 'start_character': start, 'end_character': end, 'disposition': disposition, 'rationale': rationale})
    def clause(selector, index=0): return [x['clause_id'] for x in clauses if x['source_selector'] == selector][index]
    uses = [('cal.definition.definition', N, 0, 'Definition artifact and declared schema instance are different layers.'),
        ('cal.definition.axiom', Bs[0], 0, 'Schema-use shape conditions do not assert foundational truth laws.'),
        ('cal.definition.invariant', Bs[0], 0, 'An inspection schema can be used by a checker but is not an implementation preservation invariant.'),
        ('cal.definition.authority', Bs[0], 1, 'Conformance/shape evidence does not establish authority or grant ownership.'),
        ('cal.definition.authority-promotion', Bs[0], 1, 'A passing shape check is not a promotion event.'),
        ('cal.definition.contract', Bs[0], 2, 'Contract meaning, owner and claim commitments are distinct from structural shape.'),
        ('cal.definition.classification-axis', Bs[0], 3, 'Exact D22 classification-axis counterpart; naming a kind is not specifying its admissible shape.'),
        ('cal.definition.semantic-primitive', Bs[0], 4, 'Exact D31 primitive counterpart concerns kinds within schemas; relative levels/carriers require review.'),
        ('cal.definition.root-axis-independence-invariant', F, 3, 'Exact D29 source use requires C/N independence review rather than assuming complete canonical orthogonality.'),
        ('cal.definition.typed-coupling-invariant', '/scope/applicability', 0, 'An apparent authority coupling requires typed coupling review; shape alone supplies no promotion.'),
        ('cal.definition.schema-evolution-invariant', '/voices/domain_context/explanation', 0, 'Source context distinguishes schema content from amendment witnessing; finite acceptance differences do not authorize a revision.')]
    dependencies, dependency_links = [], []
    for identity, selector, index, rationale in uses:
        dependency = source_ref(snap, identity); dependencies.append(dependency)
        dependency_links.append({'clause_id': clause(selector, index), 'dependency_ref': dependency, 'kind': 'semantic-use', 'rationale': rationale})
    declarations = [{'kind': 'sort', 'symbol_id': name, 'scope': SCOPE, 'domain_policy': 'nonempty'} for name in SORTS]
    declarations += [{'kind': 'total-function', 'symbol_id': name, 'scope': SCOPE, 'argument_sorts': [arg], 'result_sort': result, 'definedness_policy': None} for name, (arg, result) in FIELDS.items()]
    declarations += [{'kind': 'predicate' if len(sorts) == 1 else 'relation', 'symbol_id': name, 'scope': SCOPE, 'argument_sorts': sorts} for name, sorts in SIGNATURE.items()]
    populations = []
    for name, sort in UNARY.items():
        required = name in ['Schema', 'ExplicitDeclaration', 'InspectionDecidable', 'OccupantIndependent']
        populations.append({'population_id': 'POP-' + name, 'carrier': sort, 'predicate_ref': name,
            'requirement': 'required' if required else 'unresolved', 'statement': exists(sort, 'x', pred(name, 'x')) if required else None,
            'scope': SCOPE, 'rationale': 'Hypothetical Schema declaration prevents vacuity.' if required else 'Actual outcomes, component/constraint or rule populations/exemptions remain explicit review questions; empty C/N and no particular occupant are not prohibited.', 'review_ref': None})
    for name, sorts in RELATIONS.items():
        required = name in ['SchemaUse', 'OccupantAt', 'LevelBelow']
        statement = pred(name, *['x' + str(i) for i in range(len(sorts))])
        for i in reversed(range(len(sorts))): statement = exists(sorts[i], 'x' + str(i), statement)
        populations.append({'population_id': 'POP-' + name, 'carrier': sorts[0], 'predicate_ref': None,
            'requirement': 'required' if required else 'unresolved', 'statement': statement if required else None, 'scope': SCOPE,
            'rationale': 'Required Schema use has an explicit governed level and an upper-level occupant.' if required else 'Relational or role-use population needs reviewed existence/exemption; no actual conforming subject, populated graph or outcome is invented.', 'review_ref': None})
    core = {'interpretation_id': 'interpretation:schema-structure-v1', 'source': source, 'scope': SCOPE, 'declarations': declarations,
        'clauses': clauses, 'depends_on': dependencies, 'relations': [], 'assumptions': [], 'populations': populations,
        'logic_features': ['first-order', 'equality'], 'semantic_status': 'candidate', 'source_fidelity': 'pending', 'profile_ref': 'profile:static-structure-and-relative-level-candidate'}
    findings = [{'finding_id': 'SCH-CONTENT-001', 'selectors': [N, F], 'description': 'Typed memberships and primitive decidability/single-occupant flags are not complete K/C/R/N payload semantics, an implemented general decider, path algebra or proof of schema-language expressiveness. A bounded inspection profile is a separate candidate.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and schema/profile owners must select content language, total decidable inspections and operator boundaries.'},
        {'finding_id': 'SCH-INDEPENDENCE-002', 'selectors': [N, F, '/scope/applicability'], 'description': 'Local occupant constraints C and connection rules N are separate dimensions. Four finite controls and empty-C/empty-N examples do not prove complete canonical independence or nonreduction across arbitrary schemas.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and D29 owner must review common carriers, variation denominators and independence obligations.'},
        {'finding_id': 'SCH-LEVEL-003', 'selectors': [F, '/boundaries/0'], 'description': 'Relative schema use and upper-level occupancy share Entity to permit dual roles. LevelBelow, strict hierarchy and role-use contexts require reviewed mappings; kind-at-one-level is not automatic semantic identity or type collapse.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and level/metamodel owners must review governed versus representation levels, allowed role contrasts and hierarchy semantics.'},
        {'finding_id': 'SCH-CLAIM-004', 'selectors': [N, F, '/boundaries/0'], 'description': 'Shape conformance entails assigned ShapeEvidence only in the candidate slice; truth, ownership, authority, promotion and execution proof remain separate targets. An actually valid implementation/result needs exact evaluator and source bindings.', 'status': 'unresolved', 'owner_route': 'role:definition-owner, authority and contract owners must confirm evidence semantics, non-entailment and actual outcome contracts.'},
        {'finding_id': 'SCH-EVOLUTION-005', 'selectors': ['/voices/domain_context/explanation', '/scope/applicability'], 'description': 'Schema content is distinct from schema amendment witnessing. Comparing finite acceptance examples does not prove universal migration compatibility, semantic preservation, source-owner approval or authority to mutate a schema.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and Schema Evolution Invariant owner must select revision/migration obligations and exact acceptance denominator.'}]
    encoded = [x['clause_id'] for x in clauses if x['formal_statement'] is not None]
    packet = {'schema_version': 'definition-assurance-correspondence/v1-candidate', 'authority_effect': 'none',
        'upstream_schema_sha256': r.digest((IMPL / 'schemas/input-envelope.json').read_bytes()), 'source_selection': 'current',
        'inventory_policy': 'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1', 'interpretation': core,
        'source_units': units, 'correspondence': links, 'dependency_links': dependency_links,
        'dependency_closure': {'status': 'unresolved', 'review_ref': None, 'unresolved_notes': ['Eleven authored semantic uses; available partial counterparts do not close payload/level/profile/role contracts.', 'No current DS-D1 meta-type identity or registered external DomainSpec source is invented.', 'Source owner must review role contrast and level mappings, C/N variation and amendment boundaries.']},
        'assumption_links': [], 'source_precedence': {'normative_voice': '/voices/scientific_formal', 'conflicts': findings, 'review_ref': None},
        'review_packet': {'instances': [{'case_id': 'local-value-and-connection-checks', 'scenario': 'A declared structural profile checks integer fields per occupant and endpoint/multiplicity/path conditions over an explicitly supplied finite graph.', 'expected_interpretation': 'Local C and connection N outcomes are reported independently without executing, populating or interpreting the subject.', 'rationale': 'Source separates occupant structure from connectivity.', 'related_clause_ids': encoded}],
            'counterexamples': [{'case_id': 'valid-shape-without-authority', 'scenario': 'An occupant conforms structurally but has no assigned authority, promotion, truth, ownership or execution-proof outcome.', 'expected_interpretation': 'A hypothetical conformance witness satisfies T/I while separate outcome implications fail.', 'rationale': 'Non-entailment targets stay outside the schema theory.', 'related_clause_ids': encoded}],
            'known_losses': ['No full schema-language semantics or universal decidability proof.', 'Relative-level and counterpart role alignment remain candidate decisions.', 'Finite C/N controls do not prove universal independence or migration compatibility.', 'Current source acceptance, formal shape tags and actual authority are separate.'], 'review_status': 'pending', 'review_ref': None}}
    report = co.check(packet, snap, required_dependencies=[x['version_ref'] for x in dependencies], required_conflicts=[x['finding_id'] for x in findings])
    if not report['character_accounting_complete'] or report['status'] != 'correspondence-pending': raise ValueError(json.dumps(report))
    typed = ir.compile_interpretation(core, snap); ir.verify_ir(typed)
    queries = []
    for name in ['Authoritative', 'Promoted', 'ActuallyTrue', 'Owned', 'ExecutionProven']:
        premise = pred('Conforms', 'x', 's', 'l'); conclusion = pred(name, 'x')
        target = forall('Entity', 'x', forall('Entity', 's', forall('Level', 'l', implies(premise, conclusion))))
        witness = exists('Entity', 'x', exists('Entity', 's', exists('Level', 'l', both(premise, neg(conclusion)))))
        queries.append({'query_id': 'non-entailment:Conforms:' + name, 'target': target, 'witness_condition': witness,
            'kind': 'countermodel-of-implication', 'minimum_strength': 'independently-checked-model', 'selected_in_T': False})
    put('t.json', {'schema_version': 'definition-assurance-input/v1-candidate', 'kind': 'interpretation', 'authority_effect': 'none', 'payload': core})
    put('correspondence.json', packet); put('static-ir.json', typed); put('correspondence-check.json', report)
    put('clause-analysis.json', {'authority_effect': 'none', 'source': source, 'source_units': len(units), 'clauses': views, 'findings': findings, 'whole_definition_translation': 'pending', 'source_fidelity': 'pending'})
    put('query-policy.json', {'authority_effect': 'none', 'queries': queries, 'selected_in_T': False, 'unbounded_proof': False})
    print(json.dumps({'result': 'candidate-authored-and-typed', 'source_units': len(units), 'mapped_clauses': len(clauses),
        'encoded_clauses': len(encoded), 'deferred_clauses': len(report['unresolved_clauses']), 'declarations': len(declarations),
        'required_populations': sum(x['requirement'] == 'required' for x in populations), 'unresolved_populations': sum(x['requirement'] == 'unresolved' for x in populations),
        'selected_assumptions': 0, 'direct_semantic_uses': len(dependencies), 'semantic_ready': False, 'whole_translation': 'pending'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
