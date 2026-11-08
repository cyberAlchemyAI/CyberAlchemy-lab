"""Explicit authored fixtures; the User Journey body is the actual repo candidate."""
import base64
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'standalone'))
from define_core.example import example_members
from define_core.exact import binding, encode
from define_core.prepare import local_ref
from define_core.materialize import leaves

if sys.argv[1] == 'incident':
    members = example_members()
    request = json.loads(members.pop('request.json'))
else:
    repo = Path(__file__).resolve().parents[5]
    raw = (repo / 'authority/definitions/candidates/0017-user-journey/definitions/user-journey/v1/definition.json').read_bytes()
    body = json.loads(raw)
    bound = binding(raw, 'user-journey.json')
    lineage = {'schema_version': 'cal.define.field-lineage/v1', 'authored_by': 'example:alchlang-candidate-author',
               'fields': [{'target_selector': selector, 'source_binding': bound, 'source_selector': selector} for selector in leaves(body)],
               'claim_ceiling': 'Exact authored attribution; no independent semantic acceptance.', 'authority_effect': 'none'}
    lineage_raw = encode(lineage)
    lineage_binding = binding(lineage_raw, 'field-lineage.json')
    meaning = {'meaning_id': 'working:user-journey', 'revision': 1,
               'statement': body['voices']['scientific_formal']['normative_statement'],
               'scope': body['scope']['applicability'], 'boundaries': body['boundaries'], 'parameters': [],
               'ownership_posture': 'Existing repository candidate; independent semantic owner acceptance remains open.',
               'lineage': [bound], 'status': 'local-proposed', 'authority_effect': 'none'}
    request = {'schema_version': 'cal.define.prepare-request/v3', 'request_id': 'user-journey-alch', 'request_revision': 1,
               'goal': 'Define User Journey for the Lab product.', 'originating_intent': 'Make proposed human and agent journeys explicit.',
               'context': 'The six Lab journeys remain proposed; this is candidate preparation.', 'consumer': 'lab-product-team',
               'intended_use': 'inspect-preparation', 'adapter_selection_binding': None,
               'required_concepts': [{'concept_id': 'user-journey', 'question': 'What is a User Journey?', 'scope': body['scope']['applicability']}],
               'handling': [{'concept_id': 'user-journey', 'disposition': 'propose', 'payload': {'working_meaning': meaning, 'applicability': 'Candidate product design'}}],
               'source_bindings': [bound, lineage_binding], 'evidence_bindings': [], 'applications': [], 'assessments': [],
               'materialization_selection': [{'meaning_ref': local_ref('user-journey-alch', 1, 'working-meaning', 0, meaning),
                    'purpose': 'Exercise the existing User Journey Definition/v2 through the AlchLang implementation.',
                    'authority_scope': body['scope']['authority_scope_ref'], 'owner_route': body['semantic_owner_ref'],
                    'identity_intention': 'new-identity', 'parent_ref': None, 'definition_binding': bound, 'field_lineage_binding': lineage_binding}],
               'validation_scope': {'required_checks': ['Exact source bytes', 'Full Definition/v2', 'Field lineage'],
                    'evidence_scope': 'Local executable candidate; no Lab admission.', 'claim_ceiling': 'No independent semantic acceptance or observed journey success.'},
               'authority_effect': 'none'}
    members = {'user-journey.json': raw, 'field-lineage.json': lineage_raw}
print(json.dumps({'request': request, 'members': {name: base64.b64encode(raw).decode() for name, raw in members.items()}}))
