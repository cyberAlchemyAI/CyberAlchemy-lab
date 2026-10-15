"""Attributable candidate Agent Action; this record grants no permission."""
from pathlib import Path
from evaluator import ROOT, byte_sha, encoded, parse, require
from jsonschema import Draft202012Validator


def materialize_action(original_request, receipt, receipt_ref):
    request = parse(original_request)
    require(receipt.get('posture') in {'denied', 'completed', 'failed', 'indeterminate'}, 'unknown observed Action posture')
    action_id = receipt.get('action_id', 'protocol:w02-denied:' + byte_sha(original_request))
    value = {
        'schema_version': 'cyberalchemy-lab-agent-action/v1', 'authority_effect': 'none',
        'kind': 'agent-action', 'node_id': 'agent-action:w02:' + byte_sha(action_id.encode()),
        'name': 'Observed bounded local candidate Action', 'lifecycle_state': 'candidate',
        'owner_ref': request['principal_ref'], 'scope_ref': request['scope_ref'],
        'challenge_route': 'protocol:w02-local-action-challenge',
        'claim_ceiling': 'Isolated candidate Tool observation only; no repository admission or Work satisfaction.',
        'evidence_refs': [receipt_ref], 'successor_refs': [],
        'relation_refs': [{'relation_kind_ref': 'relation.uses-tool', 'direction': 'source',
                           'counterpart_kind': 'tool', 'counterpart_ref': request['tool_ref']}],
        'payload': {'agent_instance_ref': request['instance_record_ref'], 'session_ref': request['session_record_ref'],
            'assignment_ref': request['assignment_ref'], 'action_kind': request['action_kind'],
            'posture': receipt['posture'], 'input_refs': ['protocol:w02-original-input:' + request['input_sha256']],
            'output_refs': ['protocol:w02-counter-output:'+receipt['output_sha256']] if receipt.get('output_sha256') else [],
            'tool_refs': [request['tool_ref']], 'implementation_refs': ['protocol:w02-bounded-dispatch-implementation'],
            'authority_evidence_refs': [r['ref'] for r in receipt.get('evaluation', {}).get('evidence_bindings', [])],
            'receipt_refs': [receipt_ref], 'residue_refs': receipt.get('residue', [])}}
    schema = parse((ROOT/'authority/artifact-types/agent-action/v1/schema.json').read_bytes())
    require(Draft202012Validator(schema).is_valid(value), 'observed Agent Action carrier invalid')
    return value
