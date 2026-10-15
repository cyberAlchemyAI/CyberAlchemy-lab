"""Invariant requirement metadata, observed satisfaction and proof targets remain separate."""
import copy
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

SCOPE = 'scope:candidate:invariant-requirement-v1'
SORTS = ['Specification', 'System', 'Point', 'OwnerRoute']
FIELDS = {'subjectOf': ('Specification', 'System'), 'pointSubject': ('Point', 'System')}
SPEC_FLAGS = ['Invariant', 'Checkable', 'OwnSystemCondition', 'SingleCondition', 'AxiomRole', 'ConstitutionRole', 'ValidatorRole', 'GateRole', 'GovernanceActive']
POINT_FLAGS = ['StatePoint', 'TransitionPoint', 'DecisionPoint', 'TransformationPoint']
SIGNATURE = {name: ['Specification'] for name in SPEC_FLAGS}
SIGNATURE.update({name: ['Point'] for name in POINT_FLAGS})
SIGNATURE.update({name: ['Specification', 'Point'] for name in ['InScope', 'MustHold', 'Holds', 'Violation', 'Drift', 'Defect']})
SIGNATURE['RoutedThrough'] = ['Specification', 'OwnerRoute']

def var(name): return {'op': 'var', 'name': name}
def fn(name, arg): return {'op': 'fn', 'name': name, 'args': [var(arg)]}
def pred(name, *args): return {'op': 'pred', 'name': name, 'args': [var(x) if isinstance(x, str) else x for x in args]}
def both(*args): return {'op': 'and', 'args': list(args)}
def either(*args): return {'op': 'or', 'args': list(args)}
def neg(arg): return {'op': 'not', 'arg': arg}
def implies(left, right): return {'op': 'implies', 'left': left, 'right': right}
def iff(left, right): return {'op': 'iff', 'left': left, 'right': right}
def eq(left, right): return {'op': 'eq', 'left': left, 'right': right}
def quant(op, sort, name, body): return {'op': op, 'sort': sort, 'var': name, 'body': body}
def all_spec(body): return quant('forall', 'Specification', 'i', body)
def all_point(body): return quant('forall', 'Point', 'p', body)
def exists_spec(body): return quant('exists', 'Specification', 'i', body)
def exists_point(body): return quant('exists', 'Point', 'p', body)

SCOPE_REQUIREMENT = all_spec(implies(pred('Invariant', 'i'), both(pred('OwnSystemCondition', 'i'),
    all_point(implies(pred('InScope', 'i', 'p'), both(
        eq(fn('subjectOf', 'i'), fn('pointSubject', 'p')),
        either(*(pred(name, 'p') for name in POINT_FLAGS)), pred('MustHold', 'i', 'p')))))))
BREACH = all_spec(all_point(iff(pred('Violation', 'i', 'p'), both(pred('Invariant', 'i'), pred('InScope', 'i', 'p'), neg(pred('Holds', 'i', 'p'))))))
FAULT = all_spec(all_point(implies(pred('Violation', 'i', 'p'), either(pred('Drift', 'i', 'p'), pred('Defect', 'i', 'p')))))
GENUS = both(SCOPE_REQUIREMENT, BREACH, FAULT)
CHECKABLE = all_spec(implies(pred('Invariant', 'i'), pred('Checkable', 'i')))
NOT_AXIOM = all_spec(implies(pred('Invariant', 'i'), neg(pred('AxiomRole', 'i'))))
NOT_CONSTITUTION = all_spec(implies(pred('Invariant', 'i'), both(pred('SingleCondition', 'i'), neg(pred('ConstitutionRole', 'i')))))
NOT_CHECKER = all_spec(implies(pred('Invariant', 'i'), both(neg(pred('ValidatorRole', 'i')), neg(pred('GateRole', 'i')))))
ROUTE = all_spec(implies(pred('GovernanceActive', 'i'), both(pred('Invariant', 'i'),
    quant('exists', 'OwnerRoute', 'o', pred('RoutedThrough', 'i', 'o')))))
ACTUAL_SCOPE = all_spec(all_point(implies(both(pred('Invariant', 'i'), pred('InScope', 'i', 'p')), pred('Holds', 'i', 'p'))))

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
    offsets = [0, *[text.index(m) for m in markers], len(text)]
    if sorted(set(offsets)) != offsets: raise ValueError('Unordered or duplicate source cuts')
    return list(zip(offsets, offsets[1:]))

def main():
    context = json.loads((UNIT / 'context.json').read_bytes())
    for x in context['sources']:
        if ref(ROOT / x['path']) != x: raise ValueError('Changed declared input')
    external_current(context); snap = snapshot(); r.verify(snap, ROOT)
    source = source_ref(snap, 'cal.definition.invariant'); document = co.source_document(snap, source)
    units = co.inventory(document); texts = dict(co.string_leaves(document)); clauses, links, views = [], [], []
    N = '/voices/scientific_formal/normative_statement'; F = '/voices/scientific_formal/formal_expression'
    boundaries = ['/boundaries/0', '/voices/scientific_formal/boundary_conditions/0']
    for unit in units:
        selector = unit['selector']; text = texts[selector]; spans = [(0, len(text))]
        if selector in boundaries: spans = cuts(text, ['It is **not** a constitution', 'It is **not** a validator or gate', 'It is **not**\nautomatically authority'])
        if selector == N: spans = cuts(text, ['Bound source-semantic basis:', 'Its defining subject', 'An invariant is\nthe checkable', 'that a constitution rule'])
        if selector == F: spans = cuts(text, ['subject(I)', 'system can violate I?', 'grounded-by:', 'operationalized-by:', 'enforced-by:', 'CyberAlchemy v2 already carries specific invariants'])
        for index, (start, end) in enumerate(spans):
            excerpt = text[start:end]; formula = None
            disposition, roles, forms = 'deferred', ['proof-obligation'], ['non-definitional']
            rationale = 'Metadata/carrier, scope classification, possibility, grounding/enforcement, child inclusion or authority/behavior claim retained without assuming its implementation or proof.'
            if selector in boundaries:
                formula = [NOT_AXIOM, NOT_CONSTITUTION, NOT_CHECKER, ROUTE][index]
                disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Candidate same-carrier role contrast or necessary owner-route condition. Private role tags and route references require actual counterpart/carrier alignment; routing is not authorization or successful execution.'
            elif selector == N and index == 1:
                formula = GENUS; disposition, roles, forms = 'encoded', ['definition'], ['genus-differentia', 'axiomatic-implicit']
                rationale = 'System-owned scoped requirement metadata, scoped breach abbreviation and drift/defect classification. MustHold is a normative-requirement relation, not observed Holds or a lowered deontic necessity operator.'
            elif selector == N and index == 3:
                formula = CHECKABLE; disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Checkable is a necessary primitive property; no correct/complete validator, passing result or working enforcement is established.'
            elif selector == F and index == 0:
                formula = SCOPE_REQUIREMENT; disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Every declared point of the system subject in scope has a required condition; actual satisfaction and preservation targets remain outside T. Point kind and scope mapping remain candidate decisions.'
            elif selector.startswith('/voices/plain_language/') or selector.startswith('/voices/domain_context/') or selector.startswith('/voices/scientific_formal/notation/'):
                disposition, roles, forms = 'explanatory', ['explanation-example'], ['non-definitional']
                rationale = 'Non-normative intuition, quoted context, consumer example, workspace metadata or notation is not a selected assumption or current runtime fact.'
            cid = 'INV-' + str(len(clauses) + 1).zfill(3)
            clauses.append({'clause_id': cid, 'source_selector': selector, 'excerpt_sha256': hashlib.sha256(excerpt.encode()).hexdigest(),
                'start_character': start, 'disposition': disposition, 'forms': forms, 'roles': roles, 'formal_statement': formula, 'rationale': rationale})
            links.append({'unit_id': unit['unit_id'], 'clause_id': cid, 'end_character': end, 'excerpt': excerpt})
            views.append({'clause_id': cid, 'source_selector': selector, 'start_character': start, 'end_character': end, 'disposition': disposition, 'rationale': rationale})
    def clause(selector, index=0): return [x['clause_id'] for x in clauses if x['source_selector'] == selector][index]
    uses = [('cal.definition.axiom', F, 3, 'Grounding answers why the requirement holds; no current Axiom proposition or settled world truth is adopted here.'),
        ('cal.definition.constitution', F, 4, 'Operationalization by a scoped rulebook is distinct from a single requirement or proved preservation.'),
        ('cal.definition.gate', F, 5, 'Enforcer/gate use requires an actual selected validator contract; Gate source semantics and runtime checks are not conflated.'),
        ('cal.definition.definition', N, 0, 'Normalized Definition artifact and operational requirement/specification are separate layers.'),
        ('cal.definition.typed-coupling-invariant', F, 6, 'Exact D16 successor is a candidate generic-parent comparison, not an automatic inclusion theorem.'),
        ('cal.definition.root-axis-independence-invariant', F, 6, 'Exact D29 successor requires reviewed generic-parent carrier mapping.'),
        ('cal.definition.claim-support-compatibility-invariant', F, 6, 'Exact D38 claim/proof compatibility meaning remains separate from this generic requirement.'),
        ('cal.definition.closed-authority-kind-invariant', F, 6, 'Exact D49 closed enumeration is not imported or proved by the generic definition label.')]
    dependencies, dependency_links = [], []
    for identity, selector, index, rationale in uses:
        dependency = source_ref(snap, identity); dependencies.append(dependency)
        dependency_links.append({'clause_id': clause(selector, index), 'dependency_ref': dependency, 'kind': 'semantic-use', 'rationale': rationale})
    declarations = [{'kind': 'sort', 'symbol_id': n, 'scope': SCOPE, 'domain_policy': 'nonempty'} for n in SORTS]
    declarations += [{'kind': 'total-function', 'symbol_id': n, 'scope': SCOPE, 'argument_sorts': [a], 'result_sort': z, 'definedness_policy': None} for n, (a, z) in FIELDS.items()]
    declarations += [{'kind': 'predicate' if len(a) == 1 else 'relation', 'symbol_id': n, 'scope': SCOPE, 'argument_sorts': a} for n, a in SIGNATURE.items()]
    populations = []
    for name in SPEC_FLAGS + POINT_FLAGS:
        required = name in ['Invariant', 'OwnSystemCondition', 'Checkable', 'SingleCondition']; carrier = SIGNATURE[name][0]
        populations.append({'population_id': 'POP-' + name, 'carrier': carrier, 'predicate_ref': name,
            'requirement': 'required' if required else 'unresolved', 'statement': quant('exists', carrier, 'x', pred(name, 'x')) if required else None,
            'scope': SCOPE, 'rationale': 'Hypothetical invariant and its entailed necessary attributes prevent vacuity.' if required else 'Auxiliary role/point-kind existence or exemption requires explicit review; no actual governance or every-kind population is invented.', 'review_ref': None})
    populations.append({'population_id': 'POP-ScopedInvariantPoint', 'carrier': 'Specification', 'predicate_ref': None,
        'requirement': 'required', 'statement': exists_spec(both(pred('Invariant', 'i'), exists_point(pred('InScope', 'i', 'p')))),
        'scope': SCOPE, 'rationale': 'Declared scope has a hypothetical evaluation point; no actual violation or passing implementation is required as an axiom.', 'review_ref': None})
    core = {'interpretation_id': 'interpretation:invariant-requirement-v1', 'source': source, 'scope': SCOPE,
        'declarations': declarations, 'clauses': clauses, 'depends_on': dependencies, 'relations': [], 'assumptions': [],
        'populations': populations, 'logic_features': ['first-order', 'equality'], 'semantic_status': 'candidate',
        'source_fidelity': 'pending', 'profile_ref': 'profile:static-first-order-requirement-candidate'}
    findings = [{'finding_id': 'INV-MUST-001', 'selectors': [N, F], 'description': 'MustHold denotes an explicit normative requirement, while Holds denotes assigned satisfaction. Static metadata is not deontic necessity, actual compliance, temporal preservation or a selected premise asserting every target.', 'status': 'unresolved', 'owner_route': 'role:definition-owner must confirm normative denotation and the exact compliance/preservation profile.'},
        {'finding_id': 'INV-SCOPE-002', 'selectors': [N, F, '/scope/applicability'], 'description': 'System-owned state/transition/decision/transformation points and their scope are a candidate abstraction. Declared points, reachable states, transition closure and actual program/artifact binding are distinct denominators.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and system owners must select subject, scope, initial states, transitions and frame/exit policy.'},
        {'finding_id': 'INV-BREACH-003', 'selectors': [N, F, '/scope/applicability'], 'description': 'Can violate requires a possible countermodel/behavior interpretation, not an existential actual breach in T. Scoped unsatisfaction is a candidate breach abbreviation; drift versus defect diagnosis needs an admitted evaluator.', 'status': 'unresolved', 'owner_route': 'role:definition-owner must confirm possibility and diagnostic mappings without making correct implementations impossible.'},
        {'finding_id': 'INV-ENFORCER-004', 'selectors': [N, F], 'description': 'Grounded/operationalized/enforced relationships are retained as open contracts. Should-trace guidance, declared enforcers, actual enforcement and selected Gate meanings are not interchangeable.', 'status': 'unresolved', 'owner_route': 'role:definition-owner, Constitution and Gate owners must decide required references and actual enforcer/owner contracts.'},
        {'finding_id': 'INV-PARENT-005', 'selectors': [F, '/boundaries/0'], 'description': 'Source claims four specific generic children and distinguishes other roles. Private candidate tags do not prove cross-source type exclusions, subtype inclusions or real carrier compatibility.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and the exact four child owners must review carrier alignments, scope and inclusion obligations.'}]
    encoded = [x['clause_id'] for x in clauses if x['formal_statement'] is not None]
    packet = {'schema_version': 'definition-assurance-correspondence/v1-candidate', 'authority_effect': 'none',
        'upstream_schema_sha256': r.digest((IMPL / 'schemas/input-envelope.json').read_bytes()), 'source_selection': 'current',
        'inventory_policy': 'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1', 'interpretation': core,
        'source_units': units, 'correspondence': links, 'dependency_links': dependency_links,
        'dependency_closure': {'status': 'unresolved', 'review_ref': None, 'unresolved_notes': ['Eight authored semantic uses; available partial Axiom/Definition counterparts do not establish closure or fidelity.', 'Point/system and role-tag mappings are candidate choices.', 'No current cal.definition.validator identity or runtime validator is invented.']},
        'assumption_links': [], 'source_precedence': {'normative_voice': '/voices/scientific_formal', 'conflicts': findings, 'review_ref': None},
        'review_packet': {'instances': [{'case_id': 'reproducibility-requirement', 'scenario': 'A system declares a same-input/same-output condition, its subject and scope, and an owner route. Whether an implementation satisfies that condition is a separate check.', 'expected_interpretation': 'Requirement remains meaningful with a compliant model or a defective implementation; no runtime validator or actual authority is inferred.', 'rationale': 'Source intuition separates must from does.', 'related_clause_ids': encoded}],
            'counterexamples': [{'case_id': 'bad-reachable-step', 'scenario': 'A finite authored system starts good and reaches a state violating the selected condition through a permitted step.', 'expected_interpretation': 'The specification metadata can hold while the preservation and reachable-satisfaction targets fail.', 'rationale': 'Targets are evaluated outside T rather than assumed.', 'related_clause_ids': encoded}],
            'known_losses': ['No full deontic/temporal interpretation or implemented condition evaluator.', 'Actual grounding, operationalization, enforcement and four-child inclusions remain open.', 'Point scope and private role tags need real counterpart/carrier alignment.', 'Finite authored transitions are explanatory evidence, not a proof about a live implementation.'], 'review_status': 'pending', 'review_ref': None}}
    report = co.check(packet, snap, required_dependencies=[x['version_ref'] for x in dependencies], required_conflicts=[x['finding_id'] for x in findings])
    if not report.get('character_accounting_complete') or report['status'] != 'correspondence-pending': raise ValueError(json.dumps(report))
    typed = ir.compile_interpretation(core, snap); ir.verify_ir(typed)
    queries = [{'query_id': 'non-entailment:Invariant:GovernanceActive', 'target': all_spec(implies(pred('Invariant', 'i'), pred('GovernanceActive', 'i'))),
        'witness_condition': exists_spec(both(pred('Invariant', 'i'), neg(pred('GovernanceActive', 'i'))))},
        {'query_id': 'non-entailment:Invariant-required:actual-satisfaction', 'target': ACTUAL_SCOPE,
         'witness_condition': exists_spec(exists_point(both(pred('Invariant', 'i'), pred('InScope', 'i', 'p'), neg(pred('Holds', 'i', 'p')))))}]
    for x in queries: x.update(kind='countermodel-of-implication', minimum_strength='independently-checked-model', selected_in_T=False)
    put('t.json', {'schema_version': 'definition-assurance-input/v1-candidate', 'kind': 'interpretation', 'authority_effect': 'none', 'payload': core})
    put('correspondence.json', packet); put('static-ir.json', typed); put('correspondence-check.json', report)
    put('clause-analysis.json', {'authority_effect': 'none', 'source': source, 'source_units': len(units), 'clauses': views, 'findings': findings, 'whole_definition_translation': 'pending', 'source_fidelity': 'pending'})
    put('query-policy.json', {'authority_effect': 'none', 'queries': queries, 'selected_in_T': False, 'unbounded_proof': False})
    print(json.dumps({'result': 'candidate-authored-and-typed', 'source_units': len(units), 'mapped_clauses': len(clauses), 'encoded_clauses': len(encoded),
        'deferred_clauses': len(report['unresolved_clauses']), 'declarations': len(declarations), 'required_populations': 5,
        'unresolved_populations': 9, 'selected_assumptions': 0, 'direct_semantic_uses': 8, 'semantic_ready': False, 'whole_translation': 'pending'}, indent=2, sort_keys=True))

if __name__ == '__main__': main()
