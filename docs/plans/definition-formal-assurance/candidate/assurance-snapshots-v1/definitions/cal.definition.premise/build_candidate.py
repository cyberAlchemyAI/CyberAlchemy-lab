"""Premise concept, contextual adoption and selected reasoning assumptions stay distinct."""
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

SCOPE = 'scope:candidate:premise-role-v1'
SORTS = ['RoleInstance', 'Proposition', 'ReasoningContext', 'EvidencePosture', 'ConvictionPosture', 'RevisionRoute', 'RetirementCondition']
FIELDS = {'propositionOf': 'Proposition', 'contextOf': 'ReasoningContext'}
UNARY = {name: 'RoleInstance' for name in ['Premise', 'LoadBearing', 'AxiomRole', 'InvariantRole', 'DisposableHypothesis', 'HypothesisRole', 'Stated']}
UNARY['ActuallyTrue'] = 'Proposition'
STATUS = ['AdoptedToProceed', 'EstablishedTrue', 'Defeasible', 'VeracityLow', 'ConvictionHigh']
METADATA = {'HasEvidencePosture': 'EvidencePosture', 'HasConviction': 'ConvictionPosture', 'HasRevisionRoute': 'RevisionRoute', 'HasRetirementCondition': 'RetirementCondition'}
SIGNATURE = {name: [sort] for name, sort in UNARY.items()}
SIGNATURE.update({name: ['Proposition', 'ReasoningContext'] for name in STATUS})
SIGNATURE.update({name: ['RoleInstance', sort] for name, sort in METADATA.items()})


def var(name): return {'op': 'var', 'name': name}
def fn(name, subject='r'): return {'op': 'fn', 'name': name, 'args': [var(subject)]}
def pred(name, *args): return {'op': 'pred', 'name': name, 'args': [var(x) if isinstance(x, str) else x for x in args]}
def state(name): return pred(name, fn('propositionOf'), fn('contextOf'))
def both(*args): return {'op': 'and', 'args': list(args)}
def neg(arg): return {'op': 'not', 'arg': arg}
def implies(left, right): return {'op': 'implies', 'left': left, 'right': right}
def quant(op, sort, name, body): return {'op': op, 'sort': sort, 'var': name, 'body': body}
def every_role(body): return quant('forall', 'RoleInstance', 'r', body)
def witness(body): return quant('exists', 'RoleInstance', 'r', body)
WORKING = both(state('AdoptedToProceed'), neg(state('EstablishedTrue')), state('Defeasible'))
CARRIES = both(*[quant('exists', sort, 'x', pred(name, 'r', 'x')) for name, sort in METADATA.items()])
PREMISE = every_role(implies(pred('Premise', 'r'), WORKING))
TARGET = every_role(implies(pred('Premise', 'r'), both(WORKING, CARRIES)))
NOT_AXIOM = every_role(implies(pred('Premise', 'r'), neg(pred('AxiomRole', 'r'))))
NOT_INVARIANT = every_role(implies(pred('Premise', 'r'), neg(pred('InvariantRole', 'r'))))
LOAD_BEARING = every_role(implies(pred('Premise', 'r'), both(pred('LoadBearing', 'r'), neg(pred('DisposableHypothesis', 'r')))))


def ref(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def put(name, value):
    with (UNIT / name).open('x') as stream: json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')
    return ref(UNIT / name)
def snapshot(): return json.loads((BASE / 'current-snapshot.json').read_bytes())
def source_ref(snap, identity):
    row = next(x for x in snap['current_entries'] if x['definition_id'] == identity)
    return {key: row[key] for key in ['definition_id', 'version_ref', 'path', 'sha256']}
def external_current(context):
    for row in context['external_sources']:
        path = Path(row['absolute_path'])
        if r.digest(r.read_bytes(path.parents[2], 'authority/definitions/DEFINITIONS.md')) != row['sha256']: raise ValueError('Selected external source drift')
def cuts(text, markers):
    offsets = [0, *[text.index(marker) for marker in markers], len(text)]
    if sorted(set(offsets)) != offsets: raise ValueError('Nonunique/unordered source cuts')
    return list(zip(offsets, offsets[1:]))


def main():
    context = json.loads((UNIT / 'context.json').read_bytes())
    for x in context['sources']:
        if ref(ROOT / x['path']) != x: raise ValueError('Changed declared task input')
    external_current(context); snap = snapshot(); r.verify(snap, ROOT)
    source = source_ref(snap, 'cal.definition.premise'); document = co.source_document(snap, source)
    units = co.inventory(document); texts = dict(co.string_leaves(document)); clauses, links, views = [], [], []
    N = '/voices/scientific_formal/normative_statement'; F = '/voices/scientific_formal/formal_expression'
    boundaries = ['/boundaries/0', '/voices/scientific_formal/boundary_conditions/0']
    for unit in units:
        selector = unit['selector']; text = texts[selector]; spans = [(0, len(text))]
        if selector == N: spans = cuts(text, ['Target-specific normative meaning:', 'Bound source-semantic basis:', 'characteristically held', 'that is expected', 'A premise may complement', 'It can provisionally ground'])
        elif selector == F: spans = cuts(text, ['typically veracity', 'lifecycle:', 'distinguished-from:', 'The premise is exactly'])
        elif selector in boundaries: spans = cuts(text, ['It\nis **not** an invariant', 'It is **not** a disposable hypothesis', 'Promotion premise'])
        for index, (start, end) in enumerate(spans):
            excerpt = text[start:end]; formula = None
            disposition, roles, forms = 'deferred', ['proof-obligation'], ['non-definitional']
            rationale = 'Source artifact/carrier, qualitative posture, hedge classifier, evidence-gated lifecycle, provisional grounding or authority contract retained without assuming truth or runtime behavior.'
            if selector == N and index in [1, 2]:
                formula = TARGET if index == 1 else PREMISE
                disposition, roles, forms = 'encoded', ['definition'], ['genus-differentia', 'axiomatic-implicit']
                rationale = 'Candidate contextual working-role necessary conditions: deliberate adoption, unestablished status and defeasibility. Target-specific clause also requires four carried metadata witnesses; their contents/behavior remain open. No membership converse or proposition truth is inferred.'
            elif selector == F and index == 0:
                formula = PREMISE; disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Explicit working-role conjunction agrees with target/source basis. EstablishedTrue is selected epistemic status, distinct from ActuallyTrue; no underlying proposition is adopted into the metatheory.'
            elif selector in boundaries and index < 3:
                formula = [NOT_AXIOM, NOT_INVARIANT, LOAD_BEARING][index]
                disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Candidate same-carrier Axiom/Invariant role contrast and load-bearing exclusion of disposable investigation. These private tags do not prove source-qualified counterpart alignment or disjointness from every Hypothesis.'
            elif selector.startswith('/voices/plain_language/') or selector.startswith('/voices/domain_context/') or selector.startswith('/voices/scientific_formal/notation/'):
                disposition, roles, forms = 'explanatory', ['explanation-example'], ['non-definitional']
                rationale = 'Non-normative intuition, examples, notation or workspace metadata retained without actual observations, selected reasoning assumptions or source-owner acceptance.'
            cid = 'PRE-' + str(len(clauses) + 1).zfill(3)
            clauses.append({'clause_id': cid, 'source_selector': selector, 'excerpt_sha256': hashlib.sha256(excerpt.encode()).hexdigest(),
                'start_character': start, 'disposition': disposition, 'forms': forms, 'roles': roles, 'formal_statement': formula, 'rationale': rationale})
            links.append({'unit_id': unit['unit_id'], 'clause_id': cid, 'end_character': end, 'excerpt': excerpt})
            views.append({'clause_id': cid, 'source_selector': selector, 'start_character': start, 'end_character': end, 'disposition': disposition, 'rationale': rationale})
    def clause(selector, index=0): return [x['clause_id'] for x in clauses if x['source_selector'] == selector][index]
    uses = [('cal.definition.definition', N, 0, 'Definition artifact identity is distinct from a contextual working role and its represented proposition.'),
        ('cal.definition.axiom', N, 6, 'Settled foundational posture is contrasted with provisional grounding; no proposition truth or promotion is imported.'),
        ('cal.definition.invariant', boundaries[0], 1, 'System must-hold conditions and adopted propositions have different role contracts; private tags need reviewed carrier alignment.'),
        ('cal.definition.hypothesis', '/boundaries/1', 0, 'Explicit sibling-target distinction and shared source do not prove alias equality or universally disjoint extensions.'),
        ('cal.definition.authority-promotion', F, 2, 'Promotion is evidence-gated lifecycle work, distinct from high conviction or current working adoption.'),
        ('cal.definition.governance-axis-independence-invariant', F, 1, 'Exact D23 source counterpart preserves independent axes; no nonexistent Conviction or Veracity Definition identity is manufactured.'),
        ('cal.definition.evidence', F, 2, 'Evidence accumulation/promotion requires actual evidence contracts; carried posture alone does not substantiate a proposition.')]
    dependencies, dependency_links = [], []
    for identity, selector, index, rationale in uses:
        dependency = source_ref(snap, identity); dependencies.append(dependency)
        dependency_links.append({'clause_id': clause(selector, index), 'dependency_ref': dependency, 'kind': 'semantic-use', 'rationale': rationale})
    declarations = [{'kind': 'sort', 'symbol_id': name, 'scope': SCOPE, 'domain_policy': 'nonempty'} for name in SORTS]
    declarations += [{'kind': 'total-function', 'symbol_id': name, 'scope': SCOPE, 'argument_sorts': ['RoleInstance'], 'result_sort': sort, 'definedness_policy': None} for name, sort in FIELDS.items()]
    declarations += [{'kind': 'predicate' if len(sorts) == 1 else 'relation', 'symbol_id': name, 'scope': SCOPE, 'argument_sorts': sorts} for name, sorts in SIGNATURE.items()]
    populations = []
    for name, sort in UNARY.items():
        required = name in ['Premise', 'LoadBearing']
        populations.append({'population_id': 'POP-' + name, 'carrier': sort, 'predicate_ref': name,
            'requirement': 'required' if required else 'unresolved', 'statement': quant('exists', sort, 'x', pred(name, 'x')) if required else None,
            'scope': SCOPE, 'rationale': 'Hypothetical working-role witness prevents vacuity.' if required else 'Auxiliary role, statement or actual truth existence/exemption requires reviewed meaning; no world truth or canonical role instance is invented.', 'review_ref': None})
    for name in STATUS:
        required = name in ['AdoptedToProceed', 'Defeasible']
        populations.append({'population_id': 'POP-' + name, 'carrier': 'RoleInstance', 'predicate_ref': None,
            'requirement': 'required' if required else 'unresolved', 'statement': witness(both(pred('Premise', 'r'), state(name))) if required else None,
            'scope': SCOPE, 'rationale': 'Same Premise witness has its required contextual working status.' if required else 'Establishment and typical veracity/conviction values are not mandatory actual populations or fake owner exemptions.', 'review_ref': None})
    for name, sort in METADATA.items():
        populations.append({'population_id': 'POP-' + name, 'carrier': 'RoleInstance', 'predicate_ref': None, 'requirement': 'required',
            'statement': witness(both(pred('Premise', 'r'), quant('exists', sort, 'x', pred(name, 'r', 'x')))),
            'scope': SCOPE, 'rationale': 'Carried source-required metadata must belong to a hypothetical Premise; nonempty value sorts or unrelated records cannot supply it.', 'review_ref': None})
    core = {'interpretation_id': 'interpretation:premise-role-v1', 'source': source, 'scope': SCOPE, 'declarations': declarations,
        'clauses': clauses, 'depends_on': dependencies, 'relations': [], 'assumptions': [], 'populations': populations,
        'logic_features': ['first-order', 'equality'], 'semantic_status': 'candidate', 'source_fidelity': 'pending', 'profile_ref': 'profile:static-contextual-working-role-candidate'}
    findings = [{'finding_id': 'PRE-ROLE-001', 'selectors': [N, F, '/boundaries/1'], 'description': 'Definition artifact, contextual working role and proposition content are distinct. Working adoption status does not assert proposition truth in the metatheory; sibling lineage/aliases do not establish semantic equivalence or global disjointness.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and reasoning-context owners must review carrier, role identity and explicit assumption selection.'},
        {'finding_id': 'PRE-STATUS-002', 'selectors': [N, F, boundaries[0]], 'description': 'Unestablished epistemic status is distinct from actual falsity. Characteristically/typically low veracity and often high conviction require qualitative or quantitative semantics and cannot become universal values by removing their qualifiers.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and D23 owner must confirm epistemic, truth and axis denotations.'},
        {'finding_id': 'PRE-METADATA-003', 'selectors': [N], 'description': 'Four carried metadata relations enforce presence only, without selecting admitted data types, uniqueness, policy contents, route liveness, satisfied retirement guards or actual evidence.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and artifact/route owners must review carrier contracts, cardinalities and operational obligations.'},
        {'finding_id': 'PRE-LIFECYCLE-004', 'selectors': [N, F, boundaries[0], '/scope/applicability'], 'description': 'Evidence-gated promotion, revision and retirement require guarded state transitions and selected authority. Conviction, posture metadata and adoption do not establish a promotion event or successful lifecycle execution.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and Authority Promotion owner must decide source guards, evidence strength and actual route/consumer preservation.'},
        {'finding_id': 'PRE-GROUNDING-005', 'selectors': [N, '/scope/applicability'], 'description': 'Provisional grounding, may-complement/stand-alone alternatives and hedge-marker classification remain open operational/inference contracts. Mutual Axiom, Hypothesis and Invariant references require joint semantic review without fixed-point inference.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and counterpart owners must select actual dependency/carrier mappings and jointly review semantic cycles.'}]
    encoded = [x['clause_id'] for x in clauses if x['formal_statement'] is not None]
    packet = {'schema_version': 'definition-assurance-correspondence/v1-candidate', 'authority_effect': 'none',
        'upstream_schema_sha256': r.digest((IMPL / 'schemas/input-envelope.json').read_bytes()), 'source_selection': 'current',
        'inventory_policy': 'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1', 'interpretation': core,
        'source_units': units, 'correspondence': links, 'dependency_links': dependency_links,
        'dependency_closure': {'status': 'unresolved', 'review_ref': None, 'unresolved_notes': ['Seven authored semantic uses and available partial counterparts do not settle denominator completeness, carrier mappings or fidelity.', 'D23 uses its actual Governance-Axis Independence Invariant identity; qualitative statuses do not select numeric scales.', 'Mutual working/foundational/invariant/investigation references require reviewed joint cycle interpretation.']},
        'assumption_links': [], 'source_precedence': {'normative_voice': '/voices/scientific_formal', 'conflicts': findings, 'review_ref': None},
        'review_packet': {'instances': [{'case_id': 'conditional-project-bet', 'scenario': 'A project provisionally adopts a proposition to proceed, with a recorded evidence posture, conviction, revision route and retirement condition. It remains defeasible and not established as true.', 'expected_interpretation': 'A load-bearing working role with carried metadata; its content is not thereby proved or promoted.', 'rationale': 'Target and source formal conjunction agree on working adoption.', 'related_clause_ids': encoded}],
            'counterexamples': [{'case_id': 'conviction-is-not-truth', 'scenario': 'The working role has high conviction and low veracity posture while its proposition has no established or assigned actual truth.', 'expected_interpretation': 'Valid candidate working-role metadata; no truth or authority conclusion follows merely from conviction.', 'rationale': 'Epistemic status, commitment and world truth are different channels.', 'related_clause_ids': encoded}],
            'known_losses': ['No formal proposition-content evaluator or selected context premise set.', 'Carried metadata presence is not its schema, policy correctness or working lifecycle.', 'Typicality, numeric confidence, hedge classifier and provisional grounding remain unresolved.', 'Cross-source role/carrier alignment, semantic-cycle meaning and actual authority transitions remain pending.'], 'review_status': 'pending', 'review_ref': None}}
    report = co.check(packet, snap, required_dependencies=[x['version_ref'] for x in dependencies], required_conflicts=[x['finding_id'] for x in findings])
    if not report['character_accounting_complete'] or report['status'] != 'correspondence-pending': raise ValueError(json.dumps(report))
    typed = ir.compile_interpretation(core, snap); ir.verify_ir(typed)
    queries = []
    for name in ['ActuallyTrue', 'ConvictionHigh', 'VeracityLow', 'HypothesisRole']:
        outcome = pred(name, fn('propositionOf')) if name == 'ActuallyTrue' else pred(name, 'r') if name == 'HypothesisRole' else state(name)
        queries.append({'query_id': 'non-entailment:Premise:' + name, 'target': every_role(implies(pred('Premise', 'r'), outcome)),
            'witness_condition': witness(both(pred('Premise', 'r'), neg(outcome))), 'kind': 'countermodel-of-implication',
            'minimum_strength': 'independently-checked-model', 'selected_in_T': False})
    put('t.json', {'schema_version': 'definition-assurance-input/v1-candidate', 'kind': 'interpretation', 'authority_effect': 'none', 'payload': core})
    put('correspondence.json', packet); put('static-ir.json', typed); put('correspondence-check.json', report)
    put('clause-analysis.json', {'authority_effect': 'none', 'source': source, 'source_units': len(units), 'clauses': views, 'findings': findings, 'whole_definition_translation': 'pending', 'source_fidelity': 'pending'})
    put('query-policy.json', {'authority_effect': 'none', 'queries': queries, 'selected_in_T': False, 'unbounded_proof': False})
    print(json.dumps({'result': 'candidate-authored-and-typed', 'source_units': len(units), 'mapped_clauses': len(clauses),
        'encoded_clauses': len(encoded), 'deferred_clauses': len(report['unresolved_clauses']), 'declarations': len(declarations),
        'required_populations': sum(x['requirement'] == 'required' for x in populations), 'unresolved_populations': sum(x['requirement'] == 'unresolved' for x in populations),
        'selected_assumptions': 0, 'direct_semantic_uses': len(dependencies), 'semantic_ready': False, 'whole_translation': 'pending'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
