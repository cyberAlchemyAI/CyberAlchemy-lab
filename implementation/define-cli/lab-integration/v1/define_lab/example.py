"""Author a real User Journey candidate against the explicitly selected Lab."""
from pathlib import Path

from define_core.exact import binding, decode, encode, read, sha, write_package
from define_core.materialize import leaves
from define_core.prepare import local_ref
from .bootstrap import REPO

CANDIDATE = 'authority/definitions/candidates/0017-user-journey/definitions/user-journey/v1/definition.json'


def author(host, output):
    context, selected = host.context()
    product = selected[0]
    body_raw = read(REPO / CANDIDATE);body = decode(body_raw)
    body_binding = binding(body_raw, 'user-journey.json')
    product_binding = binding(product['raw'], 'product-definition.json')
    context_raw = encode(context)
    lineage = {'schema_version': 'cal.define.field-lineage/v1', 'authored_by': 'person:<vrondelli>:agent-assisted',
               'fields': [{'target_selector': s, 'source_binding': body_binding, 'source_selector': s} for s in leaves(body)],
               'claim_ceiling': 'Mechanical attribution to the explicit authored candidate; no independent semantic-fidelity acceptance.',
               'authority_effect': 'none'}
    lineage_raw = encode(lineage);lineage_binding = binding(lineage_raw, 'field-lineage.json')
    formal = body['voices']['scientific_formal']
    meaning = {'meaning_id': 'working:user-journey', 'revision': 1, 'statement': formal['normative_statement'],
               'scope': body['scope']['applicability'], 'boundaries': body['boundaries'], 'parameters': [],
               'ownership_posture': 'Candidate for role:definition-owner; local provisioning does not supply repository semantic admission.',
               'lineage': [body_binding], 'status': 'local-proposed', 'authority_effect': 'none'}
    ref = local_ref('define-user-journey', 1, 'working-meaning', 0, meaning)
    product_ref = {'kind': 'external', 'input_id': 'product-definition.json', 'identity': product['identity'],
                   'revision': product['record']['version'], 'carrier_ref': product['carrier_ref'],
                   'selector': '', 'sha256': sha(encode(product['record']))}
    request = {'schema_version': 'cal.define.prepare-request/v3', 'request_id': 'define-user-journey', 'request_revision': 1,
               'goal': 'Define User Journey for Lab product design and test the Define/Lab integration.',
               'originating_intent': 'Make project creation, context selection, team work and agent delegation understandable.',
               'context': 'The six proposed Lab project-lifecycle journeys; one exact signed local Lab context is supplied as evidence.',
               'consumer': 'lab-product-design', 'intended_use': 'inspect-preparation', 'adapter_selection_binding': None,
               'required_concepts': [{'concept_id': 'product', 'question': 'What owns the continuing promise of value?', 'scope': 'Selected Lab Product meaning.'},
                                     {'concept_id': 'user-journey', 'question': 'What constitutes a User Journey?', 'scope': body['scope']['applicability']}],
               'handling': [{'concept_id': 'product', 'disposition': 'reuse', 'payload': {'meaning_ref': product_ref,
                              'applicability': 'Product identity remains distinct from its journeys, work and implementations.'}},
                            {'concept_id': 'user-journey', 'disposition': 'propose', 'payload': {'working_meaning': meaning,
                              'applicability': 'Candidate meaning for human, agent and collaborative journeys.'}}],
               'source_bindings': [product_binding, body_binding, lineage_binding],
               'evidence_bindings': [binding(context_raw, 'lab-context.json')], 'applications': [], 'assessments': [],
               'materialization_selection': [{'meaning_ref': ref, 'purpose': 'Prepare the reusable User Journey candidate for exact local review.',
                    'authority_scope': body['scope']['authority_scope_ref'], 'owner_route': body['semantic_owner_ref'],
                    'identity_intention': 'new-identity', 'parent_ref': None, 'definition_binding': body_binding,
                    'field_lineage_binding': lineage_binding}],
               'validation_scope': {'required_checks': ['signed project context', 'Product source reuse', 'complete Definition/v2 lineage',
                                                       'native review mapping', 'exact retained reconstruction'],
                                    'evidence_scope': 'Structural and real local native integration behavior; no human usefulness study.',
                                    'claim_ceiling': 'Candidate meaning and local integration evidence; no canonical Lab definition admission.'},
               'authority_effect': 'none'}
    write_package(output, {'request.json': encode(request), 'product-definition.json': product['raw'],
                           'user-journey.json': body_raw, 'field-lineage.json': lineage_raw, 'lab-context.json': context_raw})
    return {'definition_id': body['definition_id'], 'project_ref': context['project_ref'],
            'context_head': context['head'], 'posture': 'authored-candidate-with-live-local-context', 'authority_effect': 'none'}
