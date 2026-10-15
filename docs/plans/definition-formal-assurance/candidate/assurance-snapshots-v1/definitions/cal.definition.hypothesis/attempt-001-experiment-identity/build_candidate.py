"""Hypothesis target interpretation; inherited Premise is a separate candidate comparison."""
import copy
import hashlib
import json
import sys
from pathlib import Path
UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[6]
BASE = UNIT.parents[1]
IMPL = ROOT / 'craft/formalization/candidates/definition-assurance-v1'
sys.path[:0] = [str(IMPL), str(BASE / 'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co

SCOPE = 'scope:candidate:hypothesis-role-v1'
SORTS = ['RoleInstance', 'Proposition', 'ReasoningContext', 'TestCondition']
FIELDS = {'propositionOf': 'Proposition', 'contextOf': 'ReasoningContext'}
UNARY = {'Hypothesis': 'RoleInstance', 'Stated': 'RoleInstance', 'WorkingPremise': 'RoleInstance',
    'AxiomRole': 'RoleInstance', 'InvariantRole': 'RoleInstance', 'DisposableHypothesis': 'RoleInstance',
    'LoadBearing': 'RoleInstance', 'ActuallyTrue': 'Proposition'}
STATUS = ['Provisional', 'Falsifiable', 'ForInvestigation', 'ForExperiment', 'AdoptedToProceed',
          'EstablishedTrue', 'Defeasible', 'VeracityLow', 'ConvictionHigh']
TESTS = ['DeclaredTest', 'CouldSupport', 'CouldRefine', 'CouldReject']
SIGNATURE = {name: [sort] for name, sort in UNARY.items()}
SIGNATURE.update({name: ['Proposition', 'ReasoningContext'] for name in STATUS})
SIGNATURE.update({name: ['Proposition', 'ReasoningContext', 'TestCondition'] for name in TESTS})


def var(name): return {'op': 'var', 'name': name}
def fn(name, subject='r'): return {'op': 'fn', 'name': name, 'args': [var(subject)]}
def pred(name, *args): return {'op': 'pred', 'name': name, 'args': [var(x) if isinstance(x, str) else x for x in args]}
def state(name): return pred(name, fn('propositionOf'), fn('contextOf'))
def test(name): return pred(name, fn('propositionOf'), fn('contextOf'), var('t'))
def both(*args): return {'op': 'and', 'args': list(args)}
def either(*args): return {'op': 'or', 'args': list(args)}
def neg(arg): return {'op': 'not', 'arg': arg}
def implies(left, right): return {'op': 'implies', 'left': left, 'right': right}
def quant(op, sort, name, body): return {'op': op, 'sort': sort, 'var': name, 'body': body}
def every_role(body): return quant('forall', 'RoleInstance', 'r', body)
def witness(body): return quant('exists', 'RoleInstance', 'r', body)
MODE = either(state('ForInvestigation'), state('ForExperiment'))
RESPONSE = quant('exists', 'TestCondition', 't', both(test('DeclaredTest'),
    either(test('CouldSupport'), test('CouldRefine'), test('CouldReject'))))
TARGET = every_role(implies(pred('Hypothesis', 'r'), both(state('Provisional'), state('Falsifiable'), MODE, RESPONSE)))
PREMISE = every_role(implies(pred('WorkingPremise', 'r'), both(state('AdoptedToProceed'), neg(state('EstablishedTrue')), state('Defeasible'))))
NOT_AXIOM = every_role(implies(pred('WorkingPremise', 'r'), neg(pred('AxiomRole', 'r'))))
NOT_INVARIANT = every_role(implies(pred('WorkingPremise', 'r'), neg(pred('InvariantRole', 'r'))))
LOAD_BEARING = every_role(implies(pred('WorkingPremise', 'r'), both(pred('LoadBearing', 'r'), neg(pred('DisposableHypothesis', 'r')))))


def ref(path): return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def put(name, value):
    with (UNIT / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')
    return ref(UNIT / name)
def snapshot(): return json.loads((BASE / 'current-snapshot.json').read_bytes())
def source_ref(snap, identity):
    row = next(x for x in snap['current_entries'] if x['definition_id'] == identity)
    return {k: row[k] for k in ['definition_id', 'version_ref', 'path', 'sha256']}
def external_current(context):
    for row in context['external_sources']:
        path = Path(row['absolute_path'])
        if r.digest(r.read_bytes(path.parents[2], 'authority/definitions/DEFINITIONS.md')) != row['sha256']:
            raise ValueError('External selected-source drift')
def cuts(text, markers):
    offsets = [0, *[text.index(marker) for marker in markers], len(text)]
    if sorted(set(offsets)) != offsets: raise ValueError('Nonunique or unordered source spans')
    return list(zip(offsets, offsets[1:]))


def main():
    context = json.loads((UNIT / 'context.json').read_bytes())
    for reference in context['sources']:
        if ref(ROOT / reference['path']) != reference: raise ValueError('Changed declared input')
    external_current(context)
    snap = snapshot(); r.verify(snap, ROOT)
    source = source_ref(snap, 'cal.definition.hypothesis')
    document = co.source_document(snap, source); units = co.inventory(document)
    texts = dict(co.string_leaves(document)); clauses, links, views, comparison_clauses = [], [], [], []
    N = '/voices/scientific_formal/normative_statement'; F = '/voices/scientific_formal/formal_expression'
    boundary_markers = ['It\nis **not** an invariant', 'It is **not** a disposable hypothesis', 'Promotion premise']
    for unit in units:
        selector = unit['selector']; text = texts[selector]; spans = [(0, len(text))]
        if selector == N:
            spans = cuts(text, ['Target-specific normative meaning:', '; it is not adopted',
                'Bound source-semantic basis:', 'characteristically held', 'that is expected',
                'A premise may complement', 'It can provisionally ground'])
        elif selector == F:
            spans = cuts(text, ['typically veracity', 'lifecycle:', 'distinguished-from:', 'The premise is exactly'])
        elif selector in ['/boundaries/0', '/voices/scientific_formal/boundary_conditions/0']:
            spans = cuts(text, boundary_markers)
        for index, (start, end) in enumerate(spans):
            excerpt = text[start:end]; formula = None
            disposition, roles, forms = 'deferred', ['proof-obligation'], ['non-definitional']
            rationale = 'Source classification, scope/authority, inherited Premise comparison, qualitative weights or lifecycle obligation remains explicit; no owner precedence or modal/temporal semantics is invented.'
            if selector == N and index == 1:
                formula = TARGET; disposition, roles, forms = 'encoded', ['definition'], ['genus-differentia']
                rationale = 'Candidate target-specific necessary conditions on a role instance and its proposition/context, with inclusive investigation modes and declared potential responses. No membership converse, world truth, adopted assumption or real testability proof.'
            elif selector.startswith('/voices/plain_language/') or selector.startswith('/voices/domain_context/') or selector.startswith('/voices/scientific_formal/notation/'):
                disposition, roles, forms = 'explanatory', ['explanation-example'], ['non-definitional']
                rationale = 'Non-normative explanation, examples, workspace metadata or notation retained; no observed outcome, adopted premise or owner approval is inferred.'
            elif selector == N and index == 2:
                rationale = 'Statement alone does not establish working adoption: separate countermodel target outside T, not a prohibition on every later or separately adopted Hypothesis.'
            cid = 'HYP-' + str(len(clauses) + 1).zfill(3)
            row = {'clause_id': cid, 'source_selector': selector, 'excerpt_sha256': hashlib.sha256(excerpt.encode()).hexdigest(),
                'start_character': start, 'disposition': disposition, 'forms': forms, 'roles': roles,
                'formal_statement': formula, 'rationale': rationale}
            clauses.append(row); links.append({'unit_id': unit['unit_id'], 'clause_id': cid, 'end_character': end, 'excerpt': excerpt})
            views.append({'clause_id': cid, 'source_selector': selector, 'start_character': start,
                          'end_character': end, 'disposition': disposition, 'rationale': rationale})
            projection = None
            if selector == F and index == 0: projection = PREMISE
            if selector == '/boundaries/0' and index < 3: projection = [NOT_AXIOM, NOT_INVARIANT, LOAD_BEARING][index]
            if projection is not None:
                alternative = copy.deepcopy(row)
                alternative.update(disposition='encoded', forms=['axiomatic-implicit'], roles=['definition'],
                    formal_statement=projection, rationale='Separate typed inherited-Premise comparison slice, outside primary Hypothesis T. Local WorkingPremise is not an admitted alias or a fidelity-approved translation of cal.definition.premise.')
                comparison_clauses.append(alternative)
    def clause(selector): return next(x['clause_id'] for x in clauses if x['source_selector'] == selector)
    uses = [('cal.definition.premise', N, 'Compare the exact split Premise target; shared CAV2-D55 source does not merge identities.'),
        ('cal.definition.axiom', '/boundaries/0', 'Axiom comparison and evidence-gated promotion need the exact counterpart; veracity posture is not actual world truth.'),
        ('cal.definition.invariant', '/boundaries/0', 'Must-hold invariant role is distinct from an unproved proposition used for reasoning.'),
        ('cal.definition.authority-promotion', F, 'CAV2-D48 staged evidence/owner path is separately defined; no actual promotion transition follows from this static slice.'),
        ('cal.definition.evidence', N, 'Declared potential evidence responses are not evidence sufficiency or an observed claim.'),
        ('cal.definition.observation', N, 'A prospective observation/test condition is not an actual attributable Observation record.'),
        ('cal.definition.experiment', N, 'Experiment is one candidate investigation mode; no Experiment Run or execution is asserted.'),
        ('cal.definition.definition', N, 'Normalized Definition artifact identity/classification and proposition-role identity require separate contracts.')]
    dependencies, dependency_links = [], []
    for identity, selector, rationale in uses:
        dependency = source_ref(snap, identity); dependencies.append(dependency)
        dependency_links.append({'clause_id': clause(selector), 'dependency_ref': dependency, 'kind': 'semantic-use', 'rationale': rationale})
    declarations = [{'kind': 'sort', 'symbol_id': name, 'scope': SCOPE, 'domain_policy': 'nonempty'} for name in SORTS]
    declarations += [{'kind': 'total-function', 'symbol_id': name, 'scope': SCOPE, 'argument_sorts': ['RoleInstance'], 'result_sort': sort, 'definedness_policy': None} for name, sort in FIELDS.items()]
    declarations += [{'kind': 'predicate' if len(args) == 1 else 'relation', 'symbol_id': name, 'scope': SCOPE, 'argument_sorts': args} for name, args in SIGNATURE.items()]
    populations = []
    for name, carrier in UNARY.items():
        required = name == 'Hypothesis'
        populations.append({'population_id': 'POP-' + name, 'carrier': carrier, 'predicate_ref': name,
            'requirement': 'required' if required else 'unresolved',
            'statement': quant('exists', carrier, 'x', pred(name, 'x')) if required else None,
            'scope': SCOPE, 'rationale': 'Hypothetical Hypothesis witness prevents vacuity.' if required else 'Auxiliary status/role/world-truth population policy unresolved; no actual adoption, truth, owner exemption or counterpart instance is invented.', 'review_ref': None})
    for name, formula in [('Provisional', state('Provisional')), ('Falsifiable', state('Falsifiable')), ('InvestigationModeChoice', MODE), ('DeclaredResponseChoice', RESPONSE)]:
        populations.append({'population_id': 'POP-Hypothesis-' + name, 'carrier': 'RoleInstance', 'predicate_ref': None,
            'requirement': 'required', 'statement': witness(both(pred('Hypothesis', 'r'), formula)), 'scope': SCOPE,
            'rationale': 'The same hypothetical Hypothesis subject must satisfy the selected target condition; this follows from T and its required Hypothesis witness.', 'review_ref': None})
    core = {'interpretation_id': 'interpretation:hypothesis-role-v1', 'source': source, 'scope': SCOPE,
        'declarations': declarations, 'clauses': clauses, 'depends_on': dependencies, 'relations': [],
        'assumptions': [], 'populations': populations, 'logic_features': ['first-order'],
        'semantic_status': 'candidate', 'source_fidelity': 'pending', 'profile_ref': 'profile:static-first-order-role-candidate'}
    findings = [{'finding_id': 'FID-HYP-001', 'selectors': [N, F], 'description': 'Preserve the earlier A04 conflict: target-specific investigation without automatic adoption versus the inherited adopted-to-proceed Premise formula. Primary target slice and inherited comparison remain separate, not owner-resolved precedence.', 'status': 'unresolved', 'owner_route': 'role:definition-owner must issue an attributable versioned source-precedence/correspondence decision.'},
        {'finding_id': 'HYP-LAYER-002', 'selectors': [N, '/boundaries/1'], 'description': 'Definition artifact, contextual proposition-role instance and proposition are different layers. Hypothesis and Premise have distinct normalized identities despite common source lineage and aliases. Abstract role accessors do not select a stored carrier.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and selected carrier owners must confirm the exact layer and role-context mapping.'},
        {'finding_id': 'HYP-STATUS-003', 'selectors': [N, F, '/scope/applicability'], 'description': 'Typical low veracity and often high conviction are not universal classical constraints. Hedge markers belong to candidate-axiom classification in an exact workflow. Unestablished is not actually false; high conviction does not establish truth or promotion.', 'status': 'unresolved', 'owner_route': 'role:definition-owner must bind qualitative/typical status and hedge-routing semantics separately from source labels.'},
        {'finding_id': 'HYP-OUTCOMES-004', 'selectors': [N], 'description': 'Investigation/experiment and support/refine/reject use inclusive alternatives. Could-response predicates are static primitive conditions, not a modal possibility proof, executed experiment or generic falsifiability verifier.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and Experiment/Observation owners must confirm test conditions, falsifiability and evidence-response contracts.'},
        {'finding_id': 'HYP-LIFECYCLE-005', 'selectors': [F, '/boundaries/0'], 'description': 'Evidence-gated promote/revise/retire describes lifecycle and authority behavior. Static role comparisons do not establish guards, reachable states, preserved consumers, liveness or actual owner promotion.', 'status': 'unresolved', 'owner_route': 'role:definition-owner and Authority Promotion owner must select transition, evidence and stopping/demotion contracts.'}]
    encoded = [x['clause_id'] for x in clauses if x['formal_statement'] is not None]
    packet = {'schema_version': 'definition-assurance-correspondence/v1-candidate', 'authority_effect': 'none',
        'upstream_schema_sha256': r.digest((IMPL / 'schemas/input-envelope.json').read_bytes()), 'source_selection': 'current',
        'inventory_policy': 'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1',
        'interpretation': core, 'source_units': units, 'correspondence': links, 'dependency_links': dependency_links,
        'dependency_closure': {'status': 'unresolved', 'review_ref': None, 'unresolved_notes': ['Eight authored uses and available partial Axiom/Definition counterparts do not close semantic dependencies.', 'Inherited Premise comparison is separately typed and never assembled into the primary Hypothesis T.', 'Earlier FID-HYP-001 remains pending; source acceptance does not resolve interpretation fidelity.']}, 'assumption_links': [],
        'source_precedence': {'normative_voice': '/voices/scientific_formal', 'conflicts': findings, 'review_ref': None},
        'review_packet': {'instances': [{'case_id': 'queue-latency-investigation', 'scenario': 'A team frames the proposition that a request queue causes latency and declares a measurement that could reject it. The proposition has not been adopted as the operational baseline.', 'expected_interpretation': 'Candidate Hypothesis role and conditional test response; no actual measurement, truth, working adoption or authority is implied.', 'rationale': 'Target-specific source intuition with a reviewable countermodel of adoption.', 'related_clause_ids': encoded}],
            'counterexamples': [{'case_id': 'unproved-baseline-adopted-to-proceed', 'scenario': 'A project deliberately relies on an unproved latency baseline to proceed and keeps a revision/retirement route.', 'expected_interpretation': 'Working Premise comparison is relevant; no automatic identity merge with the separate Hypothesis target.', 'rationale': 'Preserves the inherited adopted-to-proceed source rather than replacing it.', 'related_clause_ids': encoded}],
            'known_losses': ['Whole source-precedence and carrier mapping pending.', 'Primitive testability/response statuses do not establish actual empirical possibilities or falsifiability.', 'Typicality, hedge classifiers, lifecycle and promotion remain deferred.', 'No investigated proposition becomes a selected assumption, actual truth or adopted working basis merely by its record.'], 'review_status': 'pending', 'review_ref': None}}
    report = co.check(packet, snap, required_dependencies=[x['version_ref'] for x in dependencies], required_conflicts=[x['finding_id'] for x in findings])
    if not report.get('character_accounting_complete') or report['status'] != 'correspondence-pending': raise ValueError(json.dumps(report))
    typed = ir.compile_interpretation(core, snap); ir.verify_ir(typed)
    comparison_core = copy.deepcopy(core)
    comparison_core.update(interpretation_id='interpretation:hypothesis-inherited-premise-comparison-v1', clauses=comparison_clauses, populations=[])
    comparison_ir = ir.compile_interpretation(comparison_core, snap); ir.verify_ir(comparison_ir)
    queries = []
    for name, consequent in [('AdoptedToProceed', state('AdoptedToProceed')), ('EstablishedTrue', state('EstablishedTrue')),
                             ('ActuallyTrue', pred('ActuallyTrue', fn('propositionOf'))), ('WorkingPremise', pred('WorkingPremise', 'r'))]:
        antecedent = both(pred('Hypothesis', 'r'), pred('Stated', 'r'))
        queries.append({'query_id': 'non-entailment:stated-Hypothesis:' + name, 'kind': 'countermodel-of-implication',
            'target': every_role(implies(antecedent, consequent)), 'witness_condition': witness(both(antecedent, neg(consequent))),
            'minimum_strength': 'independently-checked-model', 'selected_in_T': False})
    put('t.json', {'schema_version': 'definition-assurance-input/v1-candidate', 'kind': 'interpretation', 'authority_effect': 'none', 'payload': core})
    put('correspondence.json', packet); put('static-ir.json', typed); put('correspondence-check.json', report)
    put('clause-analysis.json', {'authority_effect': 'none', 'source': source, 'source_units': len(units), 'clauses': views,
        'findings': findings, 'whole_definition_translation': 'pending', 'source_fidelity': 'pending'})
    put('query-policy.json', {'authority_effect': 'none', 'queries': queries, 'whole_source_nonentailment_coverage': 'pending source fidelity and actual adoption/promotion semantics', 'unbounded_proof': False})
    put('comparison-input.json', {'schema_version': 'definition-assurance-input/v1-candidate', 'kind': 'interpretation', 'authority_effect': 'none', 'payload': comparison_core})
    put('comparison-ir.json', comparison_ir)
    put('comparison-selection.json', {'authority_effect': 'none', 'source': source,
        'primary_interpretation_ref': ref(UNIT / 't.json'), 'comparison_input_ref': ref(UNIT / 'comparison-input.json'),
        'selected_clause_ids': [x['clause_id'] for x in comparison_clauses], 'assembled_into_primary_T': False,
        'full_source_correspondence': 'not-claimed for selected four-clause inherited slice', 'owner_precedence': 'pending',
        'source_fidelity': 'pending', 'claim_ceiling': 'Typed inherited Premise comparison only; neither primary Hypothesis T nor a whole fidelity-approved cal.definition.premise translation.'})
    print(json.dumps({'result': 'candidate-authored-and-typed', 'source_units': len(units), 'mapped_clauses': len(clauses),
        'encoded_clauses': len(encoded), 'deferred_clauses': len(report['unresolved_clauses']), 'declarations': len(declarations),
        'required_populations': 5, 'unresolved_populations': 7, 'separate_comparison_clauses': len(comparison_clauses),
        'selected_assumptions': 0, 'direct_semantic_uses': 8, 'semantic_ready': False, 'whole_translation': 'pending'}, indent=2, sort_keys=True))


if __name__ == '__main__': main()
