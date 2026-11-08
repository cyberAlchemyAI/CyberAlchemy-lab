"""Local Semantic Primitive admissibility; labels, external meanings and preservation differ."""
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

SCOPE = 'scope:candidate:legacy-local-semantic-primitive-v1'
SORTS = ['SemanticRole', 'DeclaredName', 'AuthorityScope', 'OwnerRole', 'ConsumerSurface', 'SourceBoundary', 'SpecializationCondition', 'ExternalTerm']
FIELDS = {'authorityScope': 'AuthorityScope', 'ownerRole': 'OwnerRole'}
CONSTANTS = {'CAV2Scope': 'AuthorityScope', 'DefinitionsGovernance': 'OwnerRole'}
UNARY = ['Primitive', 'LocalBaseKind', 'DerivedFromNarrower', 'AuthorityScopeDeclared', 'ExternalRelationDeclared',
    'ProgrammingPrimitiveRole', 'DatabaseFieldRole', 'SchemaClassRole', 'MetaTypeRole', 'GlossaryLabelRole',
    'NamedPrimitive', 'Authoritative', 'ActuallyTrue', 'OwnerAuthenticated', 'LocallyReauthored']
METADATA = {'HasStableName': 'DeclaredName', 'HasConsumerSurface': 'ConsumerSurface', 'HasSourceBoundary': 'SourceBoundary', 'HasSpecializationRule': 'SpecializationCondition'}
SIGNATURE = {name: ['SemanticRole'] for name in UNARY}
SIGNATURE.update({name: ['SemanticRole', sort] for name, sort in METADATA.items()})
SIGNATURE.update({name: ['SemanticRole', 'ExternalTerm'] for name in ['BorrowedFrom', 'LocalRoleBoundary', 'WholeExternalMeaningClaim']})


def var(name): return {'op': 'var', 'name': name}
def fn(name): return {'op': 'fn', 'name': name, 'args': [var('t')]}
def const(name): return {'op': 'const', 'name': name}
def pred(name, *args): return {'op': 'pred', 'name': name, 'args': [var(x) if isinstance(x, str) else x for x in args]}
def both(*args): return {'op': 'and', 'args': list(args)}
def neg(arg): return {'op': 'not', 'arg': arg}
def implies(left, right): return {'op': 'implies', 'left': left, 'right': right}
def eq(left, right): return {'op': 'eq', 'left': left, 'right': right}
def quant(op, sort, name, body): return {'op': op, 'sort': sort, 'var': name, 'body': body}
def every_role(body): return quant('forall', 'SemanticRole', 't', body)
def witness(body): return quant('exists', 'SemanticRole', 't', body)
def carries(name): return quant('exists', METADATA[name], 'x', pred(name, 't', 'x'))
BASE_KIND = every_role(implies(pred('Primitive', 't'), both(pred('LocalBaseKind', 't'), neg(pred('DerivedFromNarrower', 't')))))
DECLARATIONS = every_role(implies(pred('Primitive', 't'), both(pred('AuthorityScopeDeclared', 't'), pred('ExternalRelationDeclared', 't'),
    *[carries(name) for name in METADATA])))
LEGACY_CONDITIONS = every_role(implies(pred('Primitive', 't'), both(eq(fn('authorityScope'), const('CAV2Scope')),
    eq(fn('ownerRole'), const('DefinitionsGovernance')), neg(pred('DerivedFromNarrower', 't')),
    carries('HasSourceBoundary'), carries('HasConsumerSurface'), carries('HasSpecializationRule'))))
BORROWING = every_role(quant('forall', 'ExternalTerm', 'e', implies(both(pred('Primitive', 't'), pred('BorrowedFrom', 't', 'e')),
    both(pred('LocalRoleBoundary', 't', 'e'), neg(pred('WholeExternalMeaningClaim', 't', 'e'))))))
def not_role(name): return every_role(implies(pred('Primitive', 't'), neg(pred(name, 't'))))
BOUNDARY_ROLES = ['ProgrammingPrimitiveRole', 'DatabaseFieldRole', 'SchemaClassRole', 'MetaTypeRole', 'GlossaryLabelRole']


def ref(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def put(name, value):
    with (UNIT / name).open('x') as stream: json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')
    return ref(UNIT / name)
def snapshot(): return json.loads((BASE / 'current-snapshot.json').read_bytes())
def source_ref(snap, identity):
    x = next(x for x in snap['current_entries'] if x['definition_id'] == identity)
    return {key: x[key] for key in ['definition_id', 'version_ref', 'path', 'sha256']}
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
    source = source_ref(snap, 'cal.definition.semantic-primitive'); document = co.source_document(snap, source); units = co.inventory(document)
    texts = dict(co.string_leaves(document)); clauses, links, views = [], [], []
    N = '/voices/scientific_formal/normative_statement'; F = '/voices/scientific_formal/formal_expression'; Bs = ['/boundaries/0', '/voices/scientific_formal/boundary_conditions/0']
    for unit in units:
        selector = unit['selector']; text = texts[selector]; spans = [(0, len(text))]
        if selector == N: spans = cuts(text, ['Bound source-semantic basis:', 'To count as a primitive type,', 'Lower layers may instantiate'])
        elif selector == F: spans = cuts(text, ['If `t` is borrowed'])
        elif selector in Bs: spans = cuts(text, ['not a database field', 'not a schema class', 'not a DomainSpec', 'not a source', 'and not automatic authority'])
        for index, (start, end) in enumerate(spans):
            excerpt = text[start:end]; formula = None
            disposition, roles, forms = 'deferred', ['proof-obligation'], ['non-definitional']
            rationale = 'Artifact/local-role mapping, true semantic nonderivation, lower-layer preservation, authority or operational admission contract remains explicit without assuming proof or actual ownership.'
            if selector == N and index in [1, 2]:
                formula = BASE_KIND if index == 1 else DECLARATIONS
                disposition, roles, forms = 'encoded', ['definition'], ['genus-differentia', 'axiomatic-implicit']
                rationale = 'Candidate local base kind and nonnarrower status or required declared metadata. Names/boundary/consumer/specialization witnesses denote presence, not actual stability, admissible behavior, semantic minimality or source-owner acceptance.'
            elif selector == F:
                formula = LEGACY_CONDITIONS if index == 0 else BORROWING
                disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Exact legacy local-role scope/owner labels and metadata necessary conditions, or bounded local borrowing without a whole-external-meaning claim. Legacy labels do not authenticate Lab principals or import external authority; no completeness converse is selected.'
            elif selector in Bs and index < 5:
                formula = not_role(BOUNDARY_ROLES[index]); disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Candidate same-local-role contrast; an external/programming/schema object may be referenced without collapsing its whole meaning into this local Semantic Primitive role.'
            elif selector.startswith('/voices/plain_language/') or selector.startswith('/voices/domain_context/') or selector.startswith('/voices/scientific_formal/notation/'):
                disposition, roles, forms = 'explanatory', ['explanation-example'], ['non-definitional']
                rationale = 'Non-normative intuition, context examples, metadata or notation retained without canonical primitive instances, actual reauthoring, owner authority or selected assumptions.'
            cid = 'SPR-' + str(len(clauses) + 1).zfill(3)
            clauses.append({'clause_id': cid, 'source_selector': selector, 'excerpt_sha256': hashlib.sha256(excerpt.encode()).hexdigest(),
                'start_character': start, 'disposition': disposition, 'forms': forms, 'roles': roles, 'formal_statement': formula, 'rationale': rationale})
            links.append({'unit_id': unit['unit_id'], 'clause_id': cid, 'end_character': end, 'excerpt': excerpt})
            views.append({'clause_id': cid, 'source_selector': selector, 'start_character': start, 'end_character': end, 'disposition': disposition, 'rationale': rationale})
    def clause(selector, index=0): return [x['clause_id'] for x in clauses if x['source_selector'] == selector][index]
    uses = [('cal.definition.definition', N, 0, 'Definition artifact identity and a local primitive-role instance are distinct.'),
        ('cal.definition.source', N, 1, 'Source-evidence boundary and narrower-source nonderivation require real source/provenance semantics.'),
        ('cal.definition.implementation', N, 1, 'A primitive must not derive meaning from a narrower implementation; implementation reuse is not semantic reauthoring.'),
        ('cal.definition.schema', Bs[0], 2, 'Schema classes and local primitive roles differ; borrowing and relative levels need explicit counterpart mapping.'),
        ('cal.definition.authority', F, 1, 'Borrowed local scope does not import an external authority whole meaning or grant local authority.'),
        ('cal.definition.constitution', N, 1, 'Named lower consumers may reference the basis without silently redefining it; actual consumer preservation is open.'),
        ('cal.definition.discipline', N, 1, 'Discipline is a lower reference consumer, not an automatic primitive owner/source.'),
        ('cal.definition.ontology', N, 1, 'Ontology records may reference the local basis; a node type or repeated label does not automatically become a primitive.')]
    dependencies, dependency_links = [], []
    for identity, selector, index, rationale in uses:
        dependency = source_ref(snap, identity); dependencies.append(dependency)
        dependency_links.append({'clause_id': clause(selector, index), 'dependency_ref': dependency, 'kind': 'semantic-use', 'rationale': rationale})
    declarations = [{'kind': 'sort', 'symbol_id': n, 'scope': SCOPE, 'domain_policy': 'nonempty'} for n in SORTS]
    declarations += [{'kind': 'total-function', 'symbol_id': n, 'scope': SCOPE, 'argument_sorts': ['SemanticRole'], 'result_sort': sort, 'definedness_policy': None} for n, sort in FIELDS.items()]
    declarations += [{'kind': 'constant', 'symbol_id': n, 'scope': SCOPE, 'result_sort': sort} for n, sort in CONSTANTS.items()]
    declarations += [{'kind': 'predicate' if len(sorts) == 1 else 'relation', 'symbol_id': n, 'scope': SCOPE, 'argument_sorts': sorts} for n, sorts in SIGNATURE.items()]
    populations = []
    for name in UNARY:
        required = name in ['Primitive', 'LocalBaseKind', 'AuthorityScopeDeclared', 'ExternalRelationDeclared']
        populations.append({'population_id': 'POP-' + name, 'carrier': 'SemanticRole', 'predicate_ref': name,
            'requirement': 'required' if required else 'unresolved', 'statement': witness(pred(name, 't')) if required else None, 'scope': SCOPE,
            'rationale': 'Hypothetical local primitive-role witness prevents vacuity.' if required else 'Actual ownership/truth/reauthoring, narrower provenance or contrast-role populations need explicit reviewed existence/exemption; none is invented.', 'review_ref': None})
    for name, sort in METADATA.items():
        populations.append({'population_id': 'POP-' + name, 'carrier': 'SemanticRole', 'predicate_ref': None, 'requirement': 'required',
            'statement': witness(both(pred('Primitive', 't'), carries(name))), 'scope': SCOPE,
            'rationale': 'The same hypothetical primitive role carries required declared metadata; unrelated values/roles cannot supply it.', 'review_ref': None})
    for name in ['BorrowedFrom', 'LocalRoleBoundary', 'WholeExternalMeaningClaim']:
        populations.append({'population_id': 'POP-' + name, 'carrier': 'SemanticRole', 'predicate_ref': None, 'requirement': 'unresolved', 'statement': None,
            'scope': SCOPE, 'rationale': 'No actual borrowed term, reviewed external mapping or whole-meaning claim is required as a population or fake owner exemption.', 'review_ref': None})
    core = {'interpretation_id': 'interpretation:local-semantic-primitive-v1', 'source': source, 'scope': SCOPE, 'declarations': declarations,
        'clauses': clauses, 'depends_on': dependencies, 'relations': [], 'assumptions': [], 'populations': populations,
        'logic_features': ['first-order', 'equality'], 'semantic_status': 'candidate', 'source_fidelity': 'pending', 'profile_ref': 'profile:legacy-local-base-role-candidate'}
    findings = [{'finding_id': 'SPR-SCOPE-001', 'selectors': [N, F], 'description': 'Legacy CAV2/definitions-governance admissibility labels and the current Lab shared-authority Definition artifact concern different layers. Constants authenticate neither current Lab principals nor a scope-transfer/admission decision.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and Lab governance owners must review the exact legacy/local-role/current artifact scope and principal mapping.'},
        {'finding_id': 'SPR-BASIS-002', 'selectors': [N, F, '/scope/applicability'], 'description': 'LocalBaseKind and not-DerivedFromNarrower are primitive statuses, not actual lineage independence, semantic minimality, completeness of the primordial basis or prevention of meaning drift.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and source/consumer owners must select provenance, minimality and basis-membership evidence.'},
        {'finding_id': 'SPR-METADATA-003', 'selectors': [N, F], 'description': 'Stable name, scope, consumers, source boundary, external relation declaration and specialization condition require exact payload/cardinality/temporal contracts. Presence does not prove name uniqueness/stability, boundary completeness or specialization correctness.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and artifact/profile owners must review actual declared carriers, payloads, uniqueness and condition semantics.'},
        {'finding_id': 'SPR-BORROWING-004', 'selectors': [F, '/boundaries/0', '/voices/domain_context/explanation'], 'description': 'A borrowed local role is distinct from external whole meaning or automatic authority. Private contrast tags and local-boundary metadata do not establish admitted external meaning, actual reauthoring or cross-source type alignment.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and external/counterpart owners must review exact references, local reauthoring and common-carrier mappings.'},
        {'finding_id': 'SPR-PRESERVATION-005', 'selectors': [N, '/scope/applicability'], 'description': 'Lower layers may instantiate/specialize/compose under declared conditions but must not silently redefine the basis. Actual semantic preservation is a separate target, not a premise supplied by defining Primitive or a preserved source hash.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and lower consumer owners must select admissibility/condition checks, meaning preservation and extension evidence.'}]
    encoded = [x['clause_id'] for x in clauses if x['formal_statement'] is not None]
    packet = {'schema_version': 'definition-assurance-correspondence/v1-candidate', 'authority_effect': 'none',
        'upstream_schema_sha256': r.digest((IMPL / 'schemas/input-envelope.json').read_bytes()), 'source_selection': 'current',
        'inventory_policy': 'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1', 'interpretation': core,
        'source_units': units, 'correspondence': links, 'dependency_links': dependency_links,
        'dependency_closure': {'status': 'unresolved', 'review_ref': None, 'unresolved_notes': ['Eight authored semantic uses do not establish complete dependency/carrier/meaning closure.', 'No current Method or external DS-D1 meta-type Definition identity is manufactured.', 'Actual source nonderivation, reauthoring, lower-layer preservation and scope/owner mapping remain review obligations.']},
        'assumption_links': [], 'source_precedence': {'normative_voice': '/voices/scientific_formal', 'conflicts': findings, 'review_ref': None},
        'review_packet': {'instances': [{'case_id': 'local-basis-role', 'scenario': 'A hypothetical local role declares a stable name, legacy CAV2 scope, governance owner label, consumer/source boundaries, explicit external relation posture and specialization condition.', 'expected_interpretation': 'Candidate necessary conditions can hold without actual authority, world truth, authenticated owner or complete semantic independence proof.', 'rationale': 'Source role, declaration and authority differ.', 'related_clause_ids': encoded}],
            'counterexamples': [{'case_id': 'label-does-not-import-a-basis', 'scenario': 'Another folder names a role primitive, but its owner/scope/boundary and nonderivation conditions are absent or incompatible.', 'expected_interpretation': 'NamedPrimitive does not entail Primitive or authority; external meaning is not automatically imported.', 'rationale': 'Source explicitly rejects labels and proximity as promotion routes.', 'related_clause_ids': encoded}],
            'known_losses': ['No actual primordial-basis inventory or semantic lineage independence proof.', 'Legacy/current owner/scope mappings and external role meanings remain unreviewed.', 'Declared payloads do not prove temporal stability or specialization behavior.', 'Exact reference/signature preservation is weaker than full lower-layer semantic preservation.'], 'review_status': 'pending', 'review_ref': None}}
    report = co.check(packet, snap, required_dependencies=[x['version_ref'] for x in dependencies], required_conflicts=[x['finding_id'] for x in findings])
    if not report['character_accounting_complete'] or report['status'] != 'correspondence-pending': raise ValueError(json.dumps(report))
    typed = ir.compile_interpretation(core, snap); ir.verify_ir(typed)
    queries = []
    for premise_name, outcome_name in [('NamedPrimitive', 'Primitive'), ('NamedPrimitive', 'Authoritative'), ('Primitive', 'Authoritative'), ('Primitive', 'ActuallyTrue'), ('Primitive', 'OwnerAuthenticated')]:
        premise, outcome = pred(premise_name, 't'), pred(outcome_name, 't')
        queries.append({'query_id': 'non-entailment:' + premise_name + ':' + outcome_name, 'target': every_role(implies(premise, outcome)),
            'witness_condition': witness(both(premise, neg(outcome))), 'kind': 'countermodel-of-implication', 'minimum_strength': 'independently-checked-model', 'selected_in_T': False})
    premise = both(pred('Primitive', 't'), pred('BorrowedFrom', 't', 'e')); outcome = pred('WholeExternalMeaningClaim', 't', 'e')
    queries.append({'query_id': 'non-entailment:BorrowedLocalPrimitive:WholeExternalMeaningClaim',
        'target': every_role(quant('forall', 'ExternalTerm', 'e', implies(premise, outcome))),
        'witness_condition': witness(quant('exists', 'ExternalTerm', 'e', both(premise, neg(outcome)))),
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
