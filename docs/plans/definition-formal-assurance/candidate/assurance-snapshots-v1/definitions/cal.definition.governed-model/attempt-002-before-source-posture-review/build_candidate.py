"""Source-bound Governed Model necessary conditions and separate non-entailment targets."""
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

SCOPE = 'scope:candidate:governed-model-static-v1'
FLAGS = ['Versioned', 'ExplicitRepresentation', 'ScopeDeclared', 'OwnerDeclared',
         'SourcesDeclared', 'AssumptionsDeclared', 'ValidationDeclared',
         'LifecycleDeclared', 'ChallengeRouteDeclared', 'GovernedIdentityOrRecord', 'BoundedScope']
CONTENT = ['RepresentsConcepts', 'RepresentsRules', 'RepresentsStructures', 'RepresentsBehavior']
OUTCOMES = ['Ontology', 'Runtime', 'Implementation', 'TruthClaim', 'Decision',
            'AdmittedAuthority', 'AuthorityEffect']
PREDICATES = ['GovernedModel', *FLAGS, *CONTENT, *OUTCOMES]


def var(name):
    return {'op': 'var', 'name': name}


def pred(name, subject='x'):
    return {'op': 'pred', 'name': name, 'args': [var(subject)]}


def both(*args):
    return {'op': 'and', 'args': list(args)}


def either(*args):
    return {'op': 'or', 'args': list(args)}


def implies(left, right):
    return {'op': 'implies', 'left': left, 'right': right}


def neg(arg):
    return {'op': 'not', 'arg': arg}


def quant(op, body):
    return {'op': op, 'var': 'x', 'sort': 'Subject', 'body': body}


GENUS = quant('forall', implies(pred('GovernedModel'), both(
    *(pred(name) for name in FLAGS[:9]), either(*(pred(name) for name in CONTENT)))))
FORMAL = quant('forall', implies(pred('GovernedModel'), both(
    pred('GovernedIdentityOrRecord'), pred('BoundedScope'))))


def ref(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(name, value):
    with (UNIT / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return ref(UNIT / name)


def snapshot():
    return json.loads((BASE / 'current-snapshot.json').read_bytes())


def source_ref(snap, identity):
    row = next(row for row in snap['current_entries'] if row['definition_id'] == identity)
    return {key: row[key] for key in ['definition_id', 'version_ref', 'path', 'sha256']}


def main():
    context = json.loads((UNIT / 'context.json').read_bytes())
    for reference in context['sources']:
        if ref(ROOT / reference['path']) != reference:
            raise ValueError('Changed declared input')
    snap = snapshot()
    r.verify(snap, ROOT)
    source = source_ref(snap, 'cal.definition.governed-model')
    document = co.source_document(snap, source)
    units = co.inventory(document)
    texts = dict(co.string_leaves(document))
    clauses, links, views = [], [], []
    N = '/voices/scientific_formal/normative_statement'
    F = '/voices/scientific_formal/formal_expression'
    B = '/voices/scientific_formal/boundary_conditions/'
    for unit in units:
        selector = unit['selector']
        text = texts[selector]
        cuts = [0, len(text)]
        if selector == N:
            cuts = [0, text.index('It is not automatically'), len(text)]
        if selector == F:
            cuts = [0, text.index('GovernedModel(x) =/=>'), len(text)]
        for start, end in zip(cuts, cuts[1:]):
            excerpt = text[start:end]
            formula = None
            disposition, roles, forms = 'deferred', ['proof-obligation'], ['non-definitional']
            rationale = 'Separate carrier/admission/governance, reference-resolution, consumer behavior or source-applicability obligation; static predicates cannot prove execution or owner fidelity.'
            if (selector in [N, '/scope/applicability', B + '0'] and start == 0):
                formula = GENUS
                disposition, roles, forms = 'encoded', ['definition'], ['genus-differentia']
                rationale = 'Necessary versioned explicit representation, inclusive content alternatives and declared governance metadata. Declaration is not successful validation, selected premise truth or an admitted carrier. Sufficiency remains unresolved.'
            elif selector == F and start == 0:
                formula = FORMAL
                disposition, roles, forms = 'encoded', ['definition'], ['axiomatic-implicit']
                rationale = 'Retain governed_identity_or_record and bounded_scope as primitive conditions. No unreviewed disjunction, record layout, carrier constructor or authority grant is invented.'
            elif selector.startswith('/voices/plain_language/') or selector.startswith('/voices/domain_context/') or selector.startswith('/voices/scientific_formal/notation/'):
                disposition, roles, forms = 'explanatory', ['explanation-example'], ['non-definitional']
                rationale = 'Non-normative explanation, sample candidate, workspace metadata or notation is retained without becoming an axiom or actual instance admission.'
            elif 'not automatically' in excerpt or '=/=>' in excerpt:
                rationale = 'Non-entailment requires countermodels outside T, not universal negative membership. Overlap remains possible under separately admitted contracts; process/consumer safety is not proved by these witnesses.'
            cid = 'GM-' + str(len(clauses) + 1).zfill(3)
            clauses.append({'clause_id': cid, 'source_selector': selector,
                'excerpt_sha256': hashlib.sha256(excerpt.encode()).hexdigest(),
                'start_character': start, 'disposition': disposition, 'forms': forms,
                'roles': roles, 'formal_statement': formula, 'rationale': rationale})
            links.append({'unit_id': unit['unit_id'], 'clause_id': cid,
                          'end_character': end, 'excerpt': excerpt})
            views.append({'clause_id': cid, 'source_selector': selector,
                'start_character': start, 'end_character': end, 'disposition': disposition,
                'rationale': rationale})
    def clause(selector):
        return next(row['clause_id'] for row in clauses if row['source_selector'] == selector)
    uses = [
        ('cal.definition.definition', '/voices/scientific_formal/testable_conditions/0', 'Exact Definition-version resolution and admitted-successor semantics; no successor is inferred from a label.'),
        ('cal.definition.source', N, 'Sources are declared governance metadata; admitted evidence, source record and target authority are not conflated.'),
        ('cal.definition.validation', N, 'Validation is a declared model responsibility; declaring it does not prove its checks passed.'),
        ('cal.definition.ontology', '/boundaries/0', 'Ontology comparison is a metalevel non-entailment target, not a disjointness axiom.'),
        ('cal.definition.implementation', '/boundaries/0', 'Implementation comparison requires the exact counterpart meaning and its independent carrier contract.'),
        ('cal.definition.decision', '/boundaries/0', 'Decision is a separate semantic status; describing a model does not make a decision.'),
        ('cal.definition.authority', '/boundaries/0', 'Admitted authority and authority effect require separate contracts and owner decisions.'),
        ('cal.definition.artifact-type', '/scope/exclusions/1', 'The Definition does not create an Artifact Type or its carrier shape.'),
        ('cal.definition.typed-relation', '/boundaries/1', 'Relation availability and effects are separately governed; counterpart applicability to this source requires review.'),
        ('cal.definition.policy', '/scope/exclusions/1', 'Policy creation/admission remains separate from a model concept definition.')]
    dependencies, dependency_links = [], []
    for identity, selector, rationale in uses:
        dependency = source_ref(snap, identity)
        dependencies.append(dependency)
        dependency_links.append({'clause_id': clause(selector), 'dependency_ref': dependency,
                                 'kind': 'semantic-use', 'rationale': rationale})
    declarations = [{'kind': 'sort', 'symbol_id': 'Subject', 'scope': SCOPE, 'domain_policy': 'nonempty'}]
    declarations += [{'kind': 'predicate', 'symbol_id': name, 'scope': SCOPE,
                      'argument_sorts': ['Subject']} for name in PREDICATES]
    populations = []
    for name in PREDICATES:
        required = name == 'GovernedModel' or name in FLAGS
        populations.append({'population_id': 'POP-' + name, 'carrier': 'Subject',
            'predicate_ref': name, 'requirement': 'required' if required else 'unresolved',
            'statement': quant('exists', pred(name)) if required else None, 'scope': SCOPE,
            'rationale': ('Hypothetical Governed Model witness and its necessary attributes prevent vacuity without claiming actual admission.'
                          if required else 'No population requirement or owner exemption for this individual content category/status is invented; inclusive content choice does not require every category.'),
            'review_ref': None})
    populations.append({'population_id': 'POP-RepresentedContentChoice', 'carrier': 'Subject',
        'predicate_ref': None, 'requirement': 'required',
        'statement': quant('exists', both(pred('GovernedModel'), either(*(pred(name) for name in CONTENT)))),
        'scope': SCOPE, 'rationale': 'The same hypothetical Governed Model must represent at least one named content alternative; individual alternatives need not all be inhabited.', 'review_ref': None})
    core = {'interpretation_id': 'interpretation:governed-model-static-v1', 'source': source,
        'scope': SCOPE, 'declarations': declarations, 'clauses': clauses,
        'depends_on': dependencies, 'relations': [], 'assumptions': [], 'populations': populations,
        'logic_features': ['first-order'], 'semantic_status': 'candidate',
        'source_fidelity': 'pending', 'profile_ref': 'profile:static-first-order-structural-candidate'}
    findings = [
        {'finding_id': 'GM-CARRIER-001', 'selectors': [F, '/boundaries/1'],
         'description': 'governed_identity_or_record remains one primitive condition. Source carrier shape and relation availability require separate admitted contracts; no fixed JSON record, identity/record disjunction or constructor follows.',
         'status': 'unresolved', 'owner_route': 'role:definition-owner and the selected Artifact Type/carrier owners must bind exact carrier and identity contracts.'},
        {'finding_id': 'GM-REPRESENTATION-002', 'selectors': [N, '/scope/applicability'],
         'description': 'Content alternatives use inclusive or, and governance attributes mean declared responsibilities rather than successful validation or nonempty true premises. A necessary-condition projection does not settle full membership sufficiency.',
         'status': 'unresolved', 'owner_route': 'role:definition-owner must confirm content alternatives, metadata semantics and the full membership characterization.'},
        {'finding_id': 'GM-AUTHORITY-003', 'selectors': [F, '/boundaries/0', '/scope/exclusions/1', '/claim_ceiling'],
         'description': 'Non-entailment is distinct from disjointness; an admitted Ontology may also be a Governed Model. Object statuses, source provenance, definitions and causal admission/external effects need separate evidence.',
         'status': 'unresolved', 'owner_route': 'role:definition-owner and authority/decision owners must confirm exact status meanings and transition/effect obligations.'},
        {'finding_id': 'GM-USE-004', 'selectors': ['/voices/scientific_formal/testable_conditions/0', '/voices/scientific_formal/testable_conditions/1', '/voices/scientific_formal/testable_conditions/2', B + '2'],
         'description': 'Universal use resolution, applicability and consumer non-inference require an independently selected use/consumer inventory and operational contracts. Static finite countermodels cannot establish those universal behavior claims.',
         'status': 'unresolved', 'owner_route': 'role:definition-owner and primary consumers must select the complete use denominator and exact admitted reference/effect contracts.'}]
    encoded = [row['clause_id'] for row in clauses if row['formal_statement'] is not None]
    packet = {'schema_version': 'definition-assurance-correspondence/v1-candidate',
        'authority_effect': 'none', 'upstream_schema_sha256': r.digest((IMPL / 'schemas/input-envelope.json').read_bytes()),
        'source_selection': 'current', 'inventory_policy': 'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1',
        'interpretation': core, 'source_units': units, 'correspondence': links,
        'dependency_links': dependency_links, 'dependency_closure': {'status': 'unresolved',
            'review_ref': None, 'unresolved_notes': ['Ten authored direct semantic uses; counterpart fidelity and transitive closure remain unresolved.', 'Definition counterpart packet is available as a partial candidate; source-owner acceptance is absent.', 'No exact source versions for generic runtime/truth claim/lifecycle/challenge-role wording are invented.']},
        'assumption_links': [], 'source_precedence': {'normative_voice': '/voices/scientific_formal',
            'conflicts': findings, 'review_ref': None},
        'review_packet': {'instances': [{'case_id': 'scoped-reviewable-model',
            'scenario': 'A versioned explicit representation of workspace review rules declares scope, an owner, source posture, an assumptions declaration, a validation plan, lifecycle and challenge route; it has a governed identity/record and bounded scope.',
            'expected_interpretation': 'Qualifies for the necessary-condition draft with a hypothetical content witness; metadata alone does not establish actual validation, authority or runtime execution.',
            'rationale': 'Separates representation and governance responsibility from implementation and approval.', 'related_clause_ids': encoded}],
            'counterexamples': [{'case_id': 'missing-challenge-route', 'scenario': 'An otherwise declared model lacks a challenge route.', 'expected_interpretation': 'Cannot satisfy the selected Governed Model necessary conditions.', 'rationale': 'Checks a governance responsibility omitted by a plain representation.', 'related_clause_ids': encoded},
                {'case_id': 'term-alone-promotes', 'scenario': 'A consumer treats the label Governed Model as an admission decision or permission to execute.', 'expected_interpretation': 'The label does not establish that outcome; consumer behavior requires separately checked operational constraints.', 'rationale': 'The authority-effect target is outside T; consumer compliance is deferred.', 'related_clause_ids': encoded}],
            'known_losses': ['No carrier shape or generic record validator is implied by the Subject sort.', 'Declared metadata and primitive scope/identity conditions do not validate their actual contracts.', 'Content choice, membership sufficiency and individual auxiliary populations remain unresolved.', 'Static non-entailment controls do not prove consumer behavior, universal use resolution or absence of external effects.'], 'review_status': 'pending', 'review_ref': None}}
    report = co.check(packet, snap, required_dependencies=[row['version_ref'] for row in dependencies],
                      required_conflicts=[row['finding_id'] for row in findings])
    if not report.get('character_accounting_complete') or report['status'] != 'correspondence-pending':
        raise ValueError(json.dumps(report))
    typed = ir.compile_interpretation(core, snap)
    ir.verify_ir(typed)
    queries = [{'query_id': 'non-entailment:GovernedModel:' + name,
        'kind': 'countermodel-of-implication',
        'target': quant('forall', implies(pred('GovernedModel'), pred(name))),
        'witness_condition': quant('exists', both(pred('GovernedModel'), neg(pred(name)))),
        'minimum_strength': 'independently-checked-model', 'selected_in_T': False}
        for name in OUTCOMES]
    put('t.json', {'schema_version': 'definition-assurance-input/v1-candidate',
                  'kind': 'interpretation', 'authority_effect': 'none', 'payload': core})
    put('correspondence.json', packet)
    put('static-ir.json', typed)
    put('correspondence-check.json', report)
    put('clause-analysis.json', {'authority_effect': 'none', 'source': source,
        'source_units': len(units), 'clauses': views, 'findings': findings,
        'whole_definition_translation': 'pending', 'source_fidelity': 'pending'})
    put('query-policy.json', {'authority_effect': 'none', 'queries': queries,
        'whole_source_nonentailment_coverage': 'pending source fidelity, counterpart contracts and operational consumer-use denominator',
        'unbounded_proof': False})
    print(json.dumps({'result': 'candidate-authored-and-typed', 'source_units': len(units),
        'mapped_clauses': len(clauses), 'encoded_clauses': len(encoded),
        'deferred_clauses': len(report['unresolved_clauses']), 'declarations': len(declarations),
        'required_populations': 13, 'unresolved_populations': 11, 'selected_assumptions': 0,
        'direct_semantic_uses': len(dependencies), 'semantic_ready': False,
        'whole_translation': 'pending'}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
