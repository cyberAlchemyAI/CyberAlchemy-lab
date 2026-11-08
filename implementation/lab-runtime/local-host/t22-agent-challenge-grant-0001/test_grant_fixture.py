"""Causal fixture checks; no API operation or real Agent Session is created."""
from datetime import datetime, timedelta, timezone
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


HERE = Path(__file__).absolute().parent
SPEC = importlib.util.spec_from_file_location('t22_agent_challenge_grant', HERE / 'grant_fixture.py')
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def fixture():
    by, period = G.source_records()
    agent = json.loads((G.ROOT / 'implementation/lab-runtime/local-host/t31-workflow-stream-0003/run-0007/draft/actor-agent-instance.json').read_bytes())
    session = json.loads((G.ROOT / 'implementation/lab-runtime/local-host/t31-workflow-stream-0003/run-0007/draft/actor-agent-session.json').read_bytes())
    aid = 'agent-instance:R03-live:' + 'a' * 32
    sid = 'agent-session:R03-live:' + 'b' * 32
    view = 'context-view:R03-test@derived.test'
    agent['node_id'] = aid
    agent['scope_ref'] = G.SCOPE
    agent['payload'].update(session_ref=sid, profile_ref=by['agent-profile']['version_ref'],
                            implementation_ref=by['implementation']['version_ref'],
                            capability_refs=[by['agent-capability']['version_ref']],
                            accountable_principal_ref=by['principal']['body']['node_id'])
    session['node_id'] = sid
    session['scope_ref'] = G.SCOPE
    session['payload'].update(agent_instance_ref=aid,
                              assignment_ref=by['agent-assignment']['version_ref'],
                              context_view_ref=view, termination_state='active')
    cut = G.native_cut()
    now = datetime.now(timezone.utc)
    until = min(now + timedelta(minutes=5), G.utc(period['expires_at']))
    live = {'agent_record': agent, 'session_record': session,
            'context_view_header': {'identity_ref': 'context-view:R03-test',
                                    'version_ref': view,
                                    'carrier_ref': 'cal.artifact-type.context-view/v1',
                                    'scope_ref': G.SCOPE, 'byte_sha256': 'e' * 64},
            'context_delivery_binding': {'ref': 'context-delivery:R03-test', 'sha256': 'f' * 64},
            'session_result': {'schema_version': 'lab-agent-session-result/v1-candidate',
                               'posture': 'active', 'authority_effect': 'none',
                               'source_cut': cut, 'session_ref': sid,
                               'agent_instance_ref': aid,
                               'assignment': {'version_ref': by['agent-assignment']['version_ref']},
                               'context_delivery_binding': {'ref': 'context-delivery:R03-test',
                                                            'sha256': 'f' * 64},
                               'expires_at': until.isoformat()}}
    key = Ed25519PrivateKey.generate()
    public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return live, cut, now, until, key, public


def grant(live=None, cut=None, now=None, until=None, key=None, public=None, guard=None):
    base = fixture()
    live = copy.deepcopy(live if live is not None else base[0])
    cut = copy.deepcopy(cut if cut is not None else base[1])
    now = now if now is not None else base[2]
    until = until if until is not None else base[3]
    key = key if key is not None else base[4]
    public = public if public is not None else key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    payload = G.project_live(live, cut, now, os.getuid(), until.isoformat(),
                             'grant:R03-0005:' + '1' * 32, public, guard or (lambda: True))
    return payload, G.sign(payload, key), public, now, key


class GrantTests(unittest.TestCase):
    def test_exact_input_rejects_changed_bytes_and_linked_ancestor(self):
        with tempfile.TemporaryDirectory() as home:
            real = Path(home) / 'real'
            real.mkdir()
            file = real / 'input.json'
            file.write_bytes(b'{}')
            self.assertEqual(G.exact(file, G.sha(b'{}')), b'{}')
            with self.assertRaisesRegex(G.Refused, 'selected bytes changed'):
                G.exact(file, '0' * 64)
            linked = Path(home) / 'linked'
            linked.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(G.Refused, 'selected path missing or linked'):
                G.exact(linked / 'input.json', G.sha(b'{}'))

    def test_exact_signed_fixture_positive_and_guard_twice(self):
        calls = []
        payload, envelope, public, now, _ = grant(guard=lambda: calls.append(1) or True)
        self.assertEqual(len(calls), 2)
        self.assertEqual(payload['host_uid'], os.getuid())
        self.assertEqual(payload['max_actions'], 1)
        self.assertEqual(payload['required_evidence_kinds'], ['source', 'validation-receipt'])
        self.assertTrue(G.verify(envelope, public, payload, now))

    def test_prior_family_cut_refused(self):
        live, cut, now, until, key, public = fixture()
        cut['store_ref'] = 'completion-legacy-local-710362c855a8a11c'
        cut['branch_ref'] = 'branch:' + cut['store_ref']
        live['session_result']['source_cut'] = cut
        with self.assertRaisesRegex(G.Refused, 'wrong current Source cut'):
            G.project_live(live, cut, now, os.getuid(), until.isoformat(),
                           'grant:R03-0005:' + '1' * 32, public, lambda: True)

    def test_same_family_different_commit_refused(self):
        live, cut, now, until, key, public = fixture()
        cut['commit_sha256'] = 'a' * 64
        live['session_result']['source_cut'] = cut
        with self.assertRaisesRegex(G.Refused, 'wrong current Source cut'):
            G.project_live(live, cut, now, os.getuid(), until.isoformat(),
                           'grant:R03-0005:' + '1' * 32, public, lambda: True)
        payload, _, public, now, key = grant()
        payload['source_cut']['commit_sha256'] = 'a' * 64
        with self.assertRaisesRegex(G.Refused, 'source, Work or Contract binding differs'):
            G.verify(G.sign(payload, key), public, payload, now)

    def test_wrong_agent_assignment_and_context_refused(self):
        for mutate in (
            lambda v: v['agent_record']['payload'].__setitem__('profile_ref', 'agent-profile:other@1'),
            lambda v: v['session_record']['payload'].__setitem__('assignment_ref', 'agent-assignment:other@1'),
            lambda v: v['context_view_header'].__setitem__('version_ref', 'context-view:other@1'),
        ):
            with self.subTest(mutate=mutate):
                live, cut, now, until, key, public = fixture()
                mutate(live)
                with self.assertRaisesRegex(G.Refused, 'live Agent, Session, Assignment or Context join differs'):
                    G.project_live(live, cut, now, os.getuid(), until.isoformat(),
                                   'grant:R03-0005:' + '1' * 32, public, lambda: True)

    def test_expiry_uid_and_live_guard_refused(self):
        live, cut, now, until, key, public = fixture()
        live['session_result']['expires_at'] = (now - timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(G.Refused, 'lease expired'):
            G.project_live(live, cut, now, os.getuid(), until.isoformat(),
                           'grant:R03-0005:' + '1' * 32, public, lambda: True)
        live, cut, now, until, key, public = fixture()
        with self.assertRaisesRegex(G.Refused, 'host identity'):
            G.project_live(live, cut, now, os.getuid() + 1, until.isoformat(),
                           'grant:R03-0005:' + '1' * 32, public, lambda: True)
        calls = []
        with self.assertRaisesRegex(G.Refused, 'changed during'):
            G.project_live(live, cut, now, os.getuid(), until.isoformat(),
                           'grant:R03-0005:' + '1' * 32, public,
                           lambda: (calls.append(1) or len(calls) == 1))

    def test_changed_work_contract_and_signature_refused(self):
        payload, envelope, public, now, key = grant()
        for field in ('work_binding', 'contract_binding', 'assignment_binding'):
            changed = copy.deepcopy(payload)
            changed[field]['sha256'] = '0' * 64
            changed_envelope = G.sign(changed, key)
            with self.subTest(field=field), self.assertRaisesRegex(G.Refused, 'source, Work or Contract binding differs'):
                G.verify(changed_envelope, public, changed, now)
        changed_signature = copy.deepcopy(envelope)
        changed_signature['signature'] = envelope['signature'][:-4] + 'AAAA'
        with self.assertRaisesRegex(G.Refused, 'signature differs'):
            G.verify(changed_signature, public, payload, now)

    def test_revocation_budget_and_legacy_grant_refused(self):
        payload, _, public, now, key = grant()
        for field, value in (('revoked', True), ('max_actions', 2),
                             ('schema_version', 'lab-local-agent-challenge-grant/v2-candidate')):
            changed = copy.deepcopy(payload)
            changed[field] = value
            envelope = G.sign(changed, key)
            with self.subTest(field=field), self.assertRaisesRegex(G.Refused, 'selected technical grant differs'):
                G.verify(envelope, public, changed, now)


if __name__ == '__main__':
    unittest.main()
