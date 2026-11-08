"""Exercise the selected API55 Session and the first native contest boundary.

This does not substitute an Agent actor into the ReaderChannel. It proves the
actual Session is live, derives and verifies a scoped one-use technical grant
against its in-process records, then records the native API refusal before a
challenge is dispatched. The grant signature and private key are not retained.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import uuid

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v55-t22-agent-contest-persistent-0001'
SOURCE_SHA = '124bf71052746512b51006ba1ccaf96ee85039e50970ffbf89ceabe0925a6f92'
PROFILE_SHA = '7b3dddab8a291cbc55727f318502e416fad0a063b5a4e77e981a43d5dd790f1b'
CHAIN_SHA = '9463f2cc57a3a7f0ec644e25ce434ba6493dc7e14f431fa53b7b6e71b9eff5cb'
RECEIPT = HERE / 'LIVE-AGENT-PROBE-0001.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def journal(vault):
    return {p.relative_to(vault.root).as_posix(): sha(p.read_bytes())
            for p in (vault.root / 'journal').rglob('*') if p.is_file()}


def run():
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise ValueError('invoke with python3 -I -B')
    if RECEIPT.exists():
        raise ValueError('no-replace live Agent probe receipt already exists')
    if sha((HERE / 'CHAIN-0001.json').read_bytes()) != CHAIN_SHA:
        raise ValueError('selected signed family chain differs')
    sys.path.insert(0, str(API.parent))
    sys.path.insert(0, str(HERE))
    package = API.name
    guard = importlib.import_module(package + '.guard')
    manifest = guard.verify(SOURCE_SHA)
    if manifest['profile_binding']['sha256'] != PROFILE_SHA:
        raise ValueError('selected API55 profile differs')
    test = importlib.import_module(package + '.test_custody_sessions')
    protocol = importlib.import_module(package + '.protocol')
    fixtures = importlib.import_module(package + '.fixtures')
    handlers = importlib.import_module(package + '.handlers')
    import live_grant as grant
    test.PROFILE = PROFILE_SHA
    cls = test.Sessions
    case = cls(methodName='test_01_actual_private_memory_erased')
    class_ready = setup = False
    observations = []
    try:
        cls.setUpClass(); class_ready = True
        case.setUp(); setup = True

        def invoke(call):
            raw = compact(call)
            reply = case.service.call(raw)
            if not case.schemas.valid('api-reply', reply):
                raise ValueError('native API reply contract refused')
            if reply['request_binding']['sha256'] != sha(raw):
                raise ValueError('native API request byte binding differs')
            if reply['contract_profile_binding'] != case.schemas.profile_binding:
                raise ValueError('native API profile binding differs')
            test.privacy(reply)
            observations.append({'operation': call['operation'], 'kind': reply['kind'],
                                 'reply_sha256': sha(compact(reply))})
            return reply

        case.invoke = invoke
        status_call = fixtures.call(case.channel.context, 'lab.status', handlers.cut(case.view))
        status = case.success(status_call)
        if 'challenge.submit' not in status['supported_operations']:
            raise ValueError('challenge.submit absent from selected Lab operation catalog')
        opened, _ = case.opening_success()
        resource = case.service.sessions.live[opened['session_ref']]
        delivery = case.delivery_result
        if opened['source_cut'] != grant.native_cut():
            raise ValueError('actual Agent Session selected another signed source family')
        key = Ed25519PrivateKey.generate()
        public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        moment = datetime.now(timezone.utc)
        live = {'agent_record': resource.agent, 'session_record': resource.session,
                'session_result': opened, 'context_view_header': delivery['context_view'],
                'context_delivery_binding': opened['context_delivery_binding']}
        payload = grant.project_live(live, opened['source_cut'], moment, os.getuid(),
                                     case.channel.policy['expires_at'],
                                     'grant:R03-0005:' + uuid.uuid4().hex, public,
                                     resource.guard)
        envelope = grant.sign(payload, key)
        if grant.verify(envelope, public, payload, moment) is not True:
            raise ValueError('live Agent technical grant refused')
        # The authenticated channel has read/Session permission. The native
        # challenge call is attempted through the real Service, which must
        # refuse before any candidate write because this policy carries no
        # independent challenge transport grant.
        if 'challenge.submit' in case.channel.policy['allowed_operations']:
            raise ValueError('unexpected challenge transport permission')
        call = fixtures.call(case.channel.context, 'lab.status', handlers.cut(case.view))
        call['operation'] = 'challenge.submit'
        call['idempotency_key'] = 'fixture:t22-agent:' + uuid.uuid4().hex
        call['message']['actor'].update(agent_instance_ref=opened['agent_instance_ref'],
                                        assignment_ref=opened['assignment']['version_ref'],
                                        session_ref=opened['session_ref'])
        call['message']['budget']['max_actions'] = 1
        before = journal(case.service.vault)
        refused = case.service.call(compact(call))
        if refused.get('code') != 'unsupported-operation' or journal(case.service.vault) != before:
            raise ValueError('native challenge transport did not refuse before any journal change')
        inspected = case.success(case.inspection(opened['session_ref']))
        closed = case.success(case.closing(opened, inspected))
        if not resource.closed or not closed['discarded_memory']:
            raise ValueError('native Agent Session not disposed')
        result = {
            'schema_version': 'lab-T22-live-Agent-contest-boundary/v1-candidate',
            'status': 'PASS-live-Agent-Session-and-native-contest-refusal',
            'api_source_binding': {'path': str((API / 'source-manifest.json').relative_to(ROOT)),
                                   'sha256': SOURCE_SHA},
            'api_profile_binding': {'path': str((API / 'contract-profile.json').relative_to(ROOT)),
                                    'sha256': PROFILE_SHA},
            'signed_family_chain_sha256': CHAIN_SHA,
            'source_cut': opened['source_cut'],
            'context_delivery_binding': opened['context_delivery_binding'],
            'agent_instance_ref': opened['agent_instance_ref'],
            'session_ref': opened['session_ref'],
            'native_operations': observations,
            'technical_grant_payload_sha256': sha(grant.compact(payload)),
            'technical_grant_verified': True,
            'challenge_operation_advertised': True,
            'challenge_transport_granted': False,
            'challenge_call_refusal_code': refused['code'],
            'challenge_journal_unchanged': True,
            'session_closed': True,
            'challenge_submitted': False,
            'challenge_resolved': False,
            'contest_outcome': None,
            'owner_decision': None,
            'authority_effect': 'none',
        }
    finally:
        if setup:
            try: case.tearDown()
            finally: case.doCleanups()
        if class_ready: cls.doClassCleanups()
    guard.verify(SOURCE_SHA)
    raw = json.dumps(result, sort_keys=True, indent=2).encode() + b'\n'
    fd = os.open(RECEIPT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    return {'status': result['status'], 'sha256': sha(raw),
            'operations': [row['operation'] for row in observations]}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
