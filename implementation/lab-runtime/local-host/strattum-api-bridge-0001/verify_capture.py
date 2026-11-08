"""Cold, read-only verifier for one private authenticated API capture.

This verifies retained public proof and envelope consistency. It does not
replay the installed source or independently validate its signed cut.
"""

import argparse
import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


EXPECTED_API_SOURCE = 'a002cb11cdfd498750ccf822e2892755284b37d144edad82df1be4a59eaa7e9a'
EXPECTED_PROFILE = '5eb69bef2fd99ba07addb9460d30337673c4d3771ad7aa6ccb8002e5ea02846a'
EXPECTED_LOCAL_SNAPSHOT = 'e800599f3bfba16c4e995dd578b8cf49f25323ef884c0d0206c63576eb56ac50'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def verify(directory, private_snapshot=None):
    directory = Path(directory)
    raw = (directory / 'CAPTURE.json').read_bytes()
    capture = json.loads(raw)
    receipt = json.loads((directory / 'AUDIT-COMPLETED.json').read_bytes())
    intent = json.loads((directory / 'AUDIT-INTENT.json').read_bytes())
    require(receipt['status'] == 'complete' and receipt['capture_sha256'] == digest(raw),
            'capture receipt mismatch')
    require(capture['schema_version'] == 'lab-strattum-api-read-capture/v1'
            and capture['authority_effect'] == 'none'
            and capture['lab_mutations_requested'] == 0, 'capture posture mismatch')
    require(capture['api_source_sha256'] == intent['api_source_sha256'] == EXPECTED_API_SOURCE
            and capture['profile_sha256'] == intent['profile_sha256'] == EXPECTED_PROFILE
            and intent['status'] == 'started' and intent['authority_effect'] == 'none',
            'selected source or audit intent mismatch')

    auth = capture['reader_authentication']
    policy, challenge, proof = auth['policy'], auth['challenge'], auth['proof']
    context = auth['result']['context']
    require(digest(canonical(policy)) == capture['policy_sha256'] == challenge['policy_sha256']
            == receipt['policy_sha256'], 'policy digest mismatch')
    require(proof['challenge'] == challenge and context['principal_ref'] == policy['principal_ref']
            == capture['authenticated_principal'] == receipt['principal_ref'],
            'reader identity/challenge mismatch')
    Ed25519PublicKey.from_public_bytes(base64.b64decode(policy['reader_public_key'], validate=True)).verify(
        base64.b64decode(proof['signature'], validate=True), canonical(challenge))
    require(context['authentication_evidence_binding']['sha256'] == digest(canonical(proof)),
            'authentication proof binding mismatch')
    trusted = auth['result']['trusted_context_binding']
    require(trusted == {'ref': context['context_ref'], 'sha256': digest(canonical(context))},
            'trusted context binding mismatch')

    rows = capture['reads']
    require(len(rows) == 2 and len({row['source_cut']['commit_sha256'] for row in rows}) == 2,
            'distinct signed cut rows required')
    require(receipt['cut_sha256s'] == [digest(canonical(row['source_cut'])) for row in rows],
            'cut receipt mismatch')
    require(receipt['query_sha256s'] == [digest(canonical(row['query_call'])) for row in rows],
            'query receipt mismatch')
    require(receipt['reply_sha256s'] == [digest(canonical(row['query_reply'])) for row in rows],
            'reply receipt mismatch')
    for index, row in enumerate(rows):
        cut, artifact = row['source_cut'], row['artifact']
        expected_actor = {'principal_ref': context['principal_ref'],
                          'agent_instance_ref': context['agent_instance_ref'],
                          'assignment_ref': context['assignment_ref'],
                          'session_ref': context['session_ref'],
                          'role_assignment_refs': context['role_assignment_bindings']}
        for operation in ('query', 'inspect'):
            call, reply = row[operation + '_call'], row[operation + '_reply']
            message = reply['message']
            require(call['operation'] == reply['operation'] == 'artifact.' + operation
                    and call['call_id'] == reply['call_id'] and reply['kind'] == 'result',
                    'operation/call pairing mismatch')
            require(call['caller_context_ref'] == context['context_ref']
                    and call['message']['actor'] == expected_actor
                    and reply['trusted_context_binding'] == trusted
                    and call['expected_contract_profile_binding'] == reply['contract_profile_binding']
                    and reply['contract_profile_binding']['sha256'] == capture['profile_sha256'],
                    'Reader/profile binding mismatch')
            require(reply['request_binding']['sha256'] == digest(canonical(call))
                    and message['request_binding']['sha256'] == digest(canonical(call['message'])),
                    'request hash mismatch')
            require(call['expected_source_cut'] == call['message']['source_cut'] ==
                    message['source_cut'] == cut, 'source cut mismatch')
        query = row['query_reply']['message']
        require(query['requested_source_cut'] == cut and query['query_basis'] == 'canonical'
                and query['freshness'] == ('historical' if index == 0 else 'current')
                and query['next_page_cursor'] is None and query['results'] == [artifact],
                'query result mismatch')
        inspect = row['inspect_reply']['message']
        envelope = inspect['envelope']
        body = envelope['decoded_artifact']['body']
        require(row['inspect_call']['message']['artifact'] == artifact
                and inspect['artifact'] == envelope['artifact'] == artifact
                and envelope['source_cut'] == cut
                and envelope['decoded_artifact']['carrier_ref'] == artifact['carrier_ref']
                and artifact['carrier_ref'] == 'cal.artifact-type.project-state/v2'
                and body['schema_version'] == 'cyberalchemy-lab-project-state/v2'
                and body['node_id'] == artifact['identity_ref']
                and envelope['content']['byte_sha256'] == artifact['byte_sha256']
                and envelope['source_locator'] == envelope['content']['content_ref'],
                'inspect body/content mismatch')
        require(len(inspect['provenance_bindings']) == 1 and
                inspect['provenance_bindings'][0]['ref'] == envelope['source_locator'].split('#', 1)[0]
                and len(inspect['provenance_bindings'][0]['sha256']) == 64,
                'origin provenance missing')
        locator = envelope['source_locator']
        if locator.startswith('authority/') and '#' not in locator:
            root = Path(__file__).resolve().parents[4]
            origin = root / locator
            require(origin.is_file() and origin.resolve().is_relative_to(root)
                    and not origin.is_symlink(), 'repository origin unavailable')
            origin_raw = origin.read_bytes()
            origin_sha = digest(origin_raw)
            require(origin_sha == artifact['byte_sha256'] ==
                    inspect['provenance_bindings'][0]['sha256'],
                    'repository origin bytes mismatch')
            require(json.loads(origin_raw) == body,
                    'repository origin decoded body mismatch')
    denied_call, denied = capture['denied_call'], capture['denied_reply']
    require(denied['kind'] == 'error' and denied['message']['code'] == 'unauthorized'
            and set(denied['message']) == {'authority_effect', 'code', 'evidence_bindings',
                                           'gaps', 'message', 'request_binding',
                                           'retry_policy', 'schema_version'}
            and denied['message']['authority_effect'] == 'none'
            and denied['message']['evidence_bindings'] == []
            and denied['message']['gaps'] == []
            and denied_call['operation'] == denied['operation'] == 'artifact.query'
            and denied_call['caller_context_ref'] == context['context_ref']
            and denied['trusted_context_binding'] == trusted
            and denied_call['message']['scope_refs'] == ['scope:outside']
            and denied_call['message']['identity_refs'] == []
            and denied_call['expected_source_cut'] == rows[-1]['source_cut']
            and denied['request_binding']['sha256'] == digest(canonical(denied_call))
            and denied['message']['request_binding']['sha256'] == digest(canonical(denied_call['message']))
            and 'results' not in denied['message']
            and all(row['artifact']['identity_ref'] not in json.dumps(denied['message']) for row in rows)
            and receipt['denied_reply_sha256'] == digest(canonical(denied)),
            'wrong-scope refusal mismatch')
    snapshot_status = 'not-requested'
    if private_snapshot is not None:
        snapshot_raw = Path(private_snapshot).read_bytes()
        require(digest(snapshot_raw) == EXPECTED_LOCAL_SNAPSHOT,
                'private fixture snapshot pin mismatch')
        snapshot = json.loads(snapshot_raw)
        local = rows[-1]
        require(snapshot['expected_head'] == local['source_cut']['commit_sha256'],
                'private fixture head mismatch')
        transaction_binding = snapshot['files']['transactions/0000000002.json']
        original = base64.b64decode(transaction_binding['base64_original_bytes'], validate=True)
        provenance = local['inspect_reply']['message']['provenance_bindings'][0]
        require(digest(original) == transaction_binding['sha256'] == provenance['sha256'],
                'private transaction bytes mismatch')
        project_state = json.loads(original)['consequences']['project_state']
        require(project_state == local['inspect_reply']['message']['envelope']['decoded_artifact']['body'],
                'private Project State body mismatch')
        native_original = (json.dumps(project_state, sort_keys=True, indent=2,
                                      ensure_ascii=False, allow_nan=False) + '\n').encode()
        require(digest(native_original) == local['artifact']['byte_sha256'],
                'private Project State original bytes mismatch')
        snapshot_status = 'cold-verified'
    return {'result': 'PASS', 'capture_sha256': digest(raw),
            'cut_sequences': [row['source_cut']['commit_sequence'] for row in rows],
            'reader_signature': 'valid-for-retained-policy-key', 'wrong_scope': 'unauthorized',
            'private_fixture_snapshot': snapshot_status,
            'authority_effect': 'none'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('--private-snapshot')
    args = parser.parse_args()
    print(json.dumps(verify(args.directory, args.private_snapshot), sort_keys=True))
