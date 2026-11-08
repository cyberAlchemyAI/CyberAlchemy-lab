"""Pure schema probe for the exact signed T22 Work and Contract originals."""

import importlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v56-t22-native-agent-challenge-0001'
FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-d3537e8c3cb77a71'
sys.path.insert(0, str(API.parent))
P = importlib.import_module(API.name + '.protocol')
G = importlib.import_module(API.name + '.agent_challenge_grant')
schemas = P.Schemas('d1c8711410326ad38910e80cab32ac8c158999d9be5d044dc3cbb07cc0e276e6')
index = json.loads((FAMILY / 'source/packages/0001/record-index.json').read_bytes())


def selected(kind):
    row = next(x for x in index if x['kind'] == kind)
    body = json.loads((ROOT / row['original_binding']['path']).read_bytes())
    header = {'scope_ref': body['scope_ref'], 'identity_ref': body['node_id'],
              'version_ref': row['version_ref'], 'carrier_ref': row['carrier_ref'],
              'byte_sha256': row['original_binding']['sha256']}
    return header, body


work, _ = selected('work')
contract, contract_body = selected('challenge-contract')
principal, _ = selected('principal')
now = datetime.now(timezone.utc)
receipt_path = API / 't22-validation-receipt.json'
receipt_binding = P.binding(str(receipt_path.relative_to(ROOT)), receipt_path.read_bytes())
agent = {'scope_ref': work['scope_ref'], 'identity_ref': 'agent-instance:static-schema-probe',
         'version_ref': 'agent-instance:static-schema-probe@ephemeral.1',
         'carrier_ref': 'cal.artifact-type.agent-instance/v1', 'byte_sha256': 'a' * 64}
project = {'scope_ref': work['scope_ref'], 'identity_ref': 'project:cyberalchemy-v2-to-lab-migration',
           'version_ref': 'project:cyberalchemy-v2-to-lab-migration@1.0.0',
           'carrier_ref': 'cal.artifact-type.project-identity/v1', 'byte_sha256': 'b' * 64}
accepted = [
    {'kind': 'source', 'binding': {'ref': work['version_ref'], 'sha256': work['byte_sha256']},
     'artifact': work, 'receipt_binding': None, 'original_binding': None,
     'source_posture': 'signed-source'},
    {'kind': 'validation-receipt', 'binding': receipt_binding, 'artifact': None,
     'receipt_binding': {'path': str(receipt_path.relative_to(ROOT)),
                         'sha256': receipt_binding['sha256']},
     'original_binding': None, 'source_posture': 'completed-validation'},
]
payload = contract_body['payload']
route = {
    'schema_version': 'lab-independent-challenge-submit-routing/v1-candidate',
    'principal_ref': principal['identity_ref'], 'storage_scope_ref': work['scope_ref'],
    'candidate_scope_ref': work['scope_ref'], 'challenge_contract': contract,
    'challenger': agent, 'evidence_project': project, 'source_cut': G.native_cut(),
    'subjects': [work], 'grounds': ['scope-error'], 'accepted_evidence': accepted,
    'policy_ref': payload['policy_ref'], 'owner_route': payload['owner_route'],
    'resolution_gate_ref': payload['resolution_gate_ref'],
    'residue_route_ref': payload['unresolved_residue_route'], 'response_mode': 'evidence',
    'not_before': (now - timedelta(seconds=60)).isoformat(),
    'expires_at': (now + timedelta(minutes=5)).isoformat(), 'revoked': False,
    'development_authorization_binding': {
        'ref': 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json',
        'sha256': 'd' * 64},
    'actual_owner_outcome': None, 'authority_effect': 'none',
}
from jsonschema import Draft202012Validator
schema = json.loads((API / 'challenge-routing.schema.json').read_bytes())
errors = list(Draft202012Validator(schema, registry=schemas.registry,
                                   format_checker=schemas.checker).iter_errors(route))
print('routing_schema_errors', len(errors))
for error in errors:
    print(error.json_path, error.message)

event = json.loads((ROOT / 'authority/artifact-types/challenge-event/v1/fixtures/valid/record.json').read_bytes())
event.update(node_id='challenge-event:R03-agent:static-schema-probe',
             name='Agent challenge of exact API30 Work revision',
             owner_ref=contract_body['owner_ref'], scope_ref=work['scope_ref'],
             lifecycle_state='candidate', evidence_refs=[x['binding']['ref'] for x in accepted],
             relation_refs=[{'relation_kind_ref': 'relation.challenges',
                             'counterpart_kind': 'work', 'counterpart_ref': work['version_ref'],
                             'direction': 'source'}], successor_refs=[],
             challenge_route=payload['owner_route'],
             claim_ceiling='Local Agent challenge candidate; no factual ground decision or admission.')
event['payload'].update(challenge_contract_ref=contract['version_ref'],
                        subject_ref=work['identity_ref'], subject_version_ref=work['version_ref'],
                        challenger_ref=agent['identity_ref'], ground='scope-error',
                        evidence_refs=event['evidence_refs'], response_state='open',
                        resolution_decision_ref='none', residue_refs=[],
                        submitted_at=now.isoformat())
event_schema = json.loads((ROOT / 'authority/artifact-types/challenge-event/v1/schema.json').read_bytes())
event_errors = list(Draft202012Validator(event_schema).iter_errors(event))
print('event_schema_errors', len(event_errors))
for error in event_errors:
    print(error.json_path, error.message)

actor = {'principal_ref': principal['identity_ref'], 'agent_instance_ref': agent['identity_ref'],
         'assignment_ref': 'agent-assignment:static@1.0.0-candidate.1',
         'session_ref': 'agent-session:static', 'role_assignment_refs': []}
request = {'schema_version': 'lab-challenge-request/v1-candidate',
           'request_ref': 'request:R03-agent:static', 'actor': actor, 'subject': work,
           'challenge_contract': contract, 'ground': 'scope-error',
           'evidence_bindings': [x['binding'] for x in accepted],
           'eligibility_evaluation_binding': {'ref': 'workspace-object:static:' + 'e'*64,
                                               'sha256': 'e'*64},
           'challenge_candidate_binding': {'ref': 'workspace-object:static:' + 'f'*64,
                                           'sha256': 'f'*64},
           'source_cut': G.native_cut(), 'authority_effect': 'none'}
print('request_schema_valid', schemas.protocol_valid('urn:cyberalchemy-lab:protocol:challenge-request:v1-candidate', request))
