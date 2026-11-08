"""Pure Context private-root AST and synthetic IPC model tests."""
from __future__ import annotations

import ast
import base64
import datetime as dt
import hashlib
import pathlib
import sys
import unittest
from pathlib import PurePosixPath

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / 'implementation/lab-runtime/candidates/runtime-completion-0001'))

from t35_external_v1 import phase_rebind, role_stage
from t35_external_v1.phase_scoped_v2 import context_package_adapter_0001 as first
from t35_external_v1.phase_scoped_v2 import context_private_adapter_0002 as adapter
from t35_external_v1.phase_scoped_v2 import context_ipc_model_0001 as ipc


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class PrivateAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        instance = 'legacy-context-private-0001'
        layout = role_stage.DisposableLayout(
            PurePosixPath('/tmp/' + instance),
            PurePosixPath('/tmp/context-private-snapshot-0001'), instance)
        origin = ROOT / ('product/lab/release-candidates/v1/interface/'
                         'legacy-session-fixture-context-v1-action-0148')
        rendered = {name: role_stage.render_python(
            (origin / name).read_bytes(), layout=layout, role='context', name=name)
            for name in phase_rebind.PHASE_FILES['context']}
        predecessor = {name: {'path': str(layout.family / phase_rebind.PIN_PATHS[name]),
                              'sha256': sha(('fresh-' + name).encode())}
                       for name in phase_rebind.PHASE_PREDECESSORS['context']}
        rebound = phase_rebind.rebind(layout, 'context', rendered, predecessor)
        cls.v1, _ = first.adapt(rebound['build.py'], role='build',
                                expected_preimage_sha256=sha(rebound['build.py']))

    def test_exact_private_root_spans_and_inverse(self):
        out, record = adapter.adapt(self.v1,
                                    expected_preimage_sha256=sha(self.v1))
        self.assertEqual(record['remaining_direct_effect_refusals'], 0)
        self.assertFalse(record['effect_ready'])
        self.assertEqual(record['postimage_sha256'], sha(out))
        self.assertEqual(first.count_calls(ast.parse(out), '_t35_effect_refused'), 0)
        self.assertIn(b'_ctx_private_root_context()', out)
        self.assertIn(b'_ctx_private_root_guard(root)', out)
        self.assertIn(b'_ctx_private_root_absent(root)', out)
        self.assertIn(b'channel.close()', out)
        self.assertEqual(adapter.verify_postimage(
            self.v1, out, expected_preimage_sha256=sha(self.v1)), record)
        with self.assertRaisesRegex(adapter.Refusal, 'POSTIMAGE_DRIFT'):
            adapter.verify_postimage(self.v1, out + b'\n',
                                     expected_preimage_sha256=sha(self.v1))

    def test_private_root_preimage_mutations_refuse(self):
        variants = [
            (b'with reader.open_signed(SOURCE_PIN, SOURCE_PACKAGE) as source, _t35_effect_refused() as tmp:',
             b'with reader.open_signed(SOURCE_PIN, SOURCE_PACKAGE) as source, other() as tmp:'),
            (b'root = Path(tmp)', b'root = Path("/tmp/other")'),
            (b"policy_path = root / 'permission.json'",
             b"policy_path = root / 'wrong.json'"),
            (b"require(not root.exists(), 'private host permission root remains')",
             b"require(root.exists(), 'private host permission root remains')"),
            (b'channel.close()', b'channel = None'),
        ]
        for before, after in variants:
            with self.subTest(before=before):
                self.assertIn(before, self.v1)
                mutated = self.v1.replace(before, after, 1)
                with self.assertRaises(adapter.Refusal):
                    adapter.adapt(mutated,
                                  expected_preimage_sha256=sha(mutated))
        with self.assertRaisesRegex(adapter.Refusal, 'PREIMAGE_DRIFT'):
            adapter.adapt(self.v1, expected_preimage_sha256='0' * 64)


class SyntheticProtocol(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 10, 19, 12, 0, 0, tzinfo=dt.timezone.utc)
        self.key = Ed25519PrivateKey.from_private_bytes(b'\x01' * 32)
        self.public = base64.b64encode(self.key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
        self.period = {
            'not_before': '2026-10-19T11:00:00Z',
            'expires_at': '2026-10-19T13:00:00Z',
            'binding': {'path': '/tmp/family/source/packages/0001/period.json',
                        'sha256': sha(b'period')},
        }
        self.package_path = '/tmp/family/context/packages/0001'
        self.private_path = '/tmp/lc-context-private-0001'
        self.peer = (321, 1, 1001, 1001)
        self.model = self.make_model()

    def make_model(self, *, period=None):
        return ipc.ProtocolModel(
            attempt_id='context-attempt-0001', selection_sha256=sha(b'selection'),
            predecessor={name: sha(name.encode()) for name in
                         ('source', 'source_package', 'mapped', 'mapped_package')},
            package_path=self.package_path,
            private_root_path=self.private_path, uid=1001,
            source_period=self.period if period is None else period,
            source_scope_ref='scope:synthetic', principal_ref='principal:synthetic',
            mapped_output_sha256=sha(b'mapped-native-output'),
            peer=self.peer, now=self.now)

    def send(self, verb, payload, *, ordinal=None, peer=None):
        raw = ipc.message(self.model, verb, payload, ordinal=ordinal)
        return self.model.receive(raw, peer=self.peer if peer is None else peer)

    def receipt(self, *, private=False, absent=True):
        return {'path': self.private_path if private else self.package_path,
                'absent_before': absent, 'empty_after': True,
                'readonly_visible': True, 'nonsymlink': True,
                'uid': 1001, 'mode': 0o700,
                'identity_sha256': sha(b'private' if private else b'package')}

    def policy(self):
        return {'schema_version': 'lab-context-host-policy/v1-candidate',
                'host_uid': 1001, 'principal_ref': 'principal:synthetic',
                'scope_ref': 'scope:synthetic', 'reader_public_key': self.public,
                'not_before': '2026-10-19T11:59:59Z',
                'expires_at': '2026-10-19T12:20:00Z',
                'max_input_bytes': ipc.REQUEST_MAX,
                'max_output_bytes': ipc.ARTIFACT_TOTAL_MAX,
                'max_session_seconds': 900,
                'period_binding': self.period['binding'],
                'allowed_operations': ['context.get', 'session.open'],
                'authority_effect': 'none', 'actual_owner_outcome': None}

    def provision(self, policy=None, extra=None):
        policy = self.policy() if policy is None else policy
        payload = {'path': self.private_path + '/permission.json',
                   'policy': policy, 'policy_sha256': sha(ipc.encoded(policy))}
        if extra:
            payload.update(extra)
        return self.send('PROVISION', payload)

    def initial(self):
        self.send('PREPARE', self.receipt())
        self.send('PRIVATE_ROOT', self.receipt(private=True))
        self.provision()

    def proof(self):
        challenge = {'schema_version': 'lab-context-host-challenge/v1-candidate',
                     'host_instance_ref': 'host:synthetic',
                     'connection_ref': 'connection:synthetic',
                     'nonce': 'a' * 64,
                     'policy_sha256': sha(ipc.encoded(self.policy())),
                     'expires_at': self.policy()['expires_at'],
                     'authority_effect': 'none'}
        return {'challenge': challenge,
                'signature': base64.b64encode(self.key.sign(
                    ipc.compact(challenge))).decode()}

    def emit(self, leaf):
        if leaf == 'authentication-proof.json':
            proof = self.proof()
            raw = ipc.compact(proof)
            payload = {'leaf': leaf, 'sha256': sha(raw),
                       'size_bytes': len(raw), 'proof': proof}
        elif leaf == 'host-permission-public.json':
            raw = ipc.encoded(self.policy())
            payload = {'leaf': leaf, 'sha256': sha(raw),
                       'size_bytes': len(raw)}
        else:
            raw = ('synthetic:' + leaf).encode()
            payload = {'leaf': leaf, 'sha256': sha(raw),
                       'size_bytes': len(raw)}
        self.send('EMIT', payload)

    def test_complete_40_leaf_39_row_schedule_is_synthetic_only(self):
        self.initial()
        for leaf in ('request.json', 'authentication-proof.json',
                     'trusted-context.json', 'host-permission-public.json'):
            self.emit(leaf)
        self.send('NATIVE_READ', {
            'mapped_package_sha256': sha(b'mapped_package'),
            'output_sha256': sha(b'mapped-native-output'),
            'size_bytes': 256})
        for i in range(30):
            self.emit('artifacts/' + str(i).zfill(2) + '.json')
        for leaf in ('artifact-index.json', 'delivery.json',
                     'lesson-selection.json', 'delivery-provenance.json'):
            self.emit(leaf)
        self.send('RELEASE_PRIVATE', {
            'path': self.private_path, 'identity_sha256': sha(b'private'),
            'policy_absent': True, 'root_absent': True, 'owner_uid': 1001})
        self.emit('build-result.json')
        self.emit('manifest.json')
        rows = [{'path': self.package_path + '/' + leaf,
                 'sha256': self.model.bindings[leaf][0]}
                for leaf in sorted(self.model.bindings) if leaf != 'manifest.json']
        self.send('FINISH', {'manifest_rows': rows, 'package_closed': True})
        self.assertTrue(self.model.finished)
        self.assertFalse(self.model.failed)
        self.assertEqual(len(self.model.bindings), 40)
        self.assertEqual(len(rows), 39)
        self.assertEqual(len(self.model.trace), len(ipc.schedule()))
        self.assertEqual(len(ipc.schedule()), 46)

    def test_wrong_ordinal_poison_and_retention(self):
        with self.assertRaisesRegex(ipc.Refusal, 'ORDINAL'):
            self.send('PREPARE', self.receipt(), ordinal=1)
        self.assertTrue(self.model.failed)
        self.assertTrue(self.model.retain_attempt)
        self.assertEqual(self.model.first_failure, 'ORDINAL')
        with self.assertRaisesRegex(ipc.Refusal, 'POISONED'):
            self.send('PREPARE', self.receipt())

    def test_private_key_field_refuses_without_disclosure(self):
        self.send('PREPARE', self.receipt())
        self.send('PRIVATE_ROOT', self.receipt(private=True))
        with self.assertRaisesRegex(ipc.Refusal, 'CLOSED_FIELDS'):
            self.provision(extra={'private_key': 'SENSITIVE-TEST-MARKER'})
        self.assertTrue(self.model.retain_attempt)
        self.assertNotIn('SENSITIVE-TEST-MARKER', self.model.first_failure)
        self.assertIsNone(self.model.policy)

    def test_stale_policy_refuses_and_retains(self):
        self.send('PREPARE', self.receipt())
        self.send('PRIVATE_ROOT', self.receipt(private=True))
        policy = self.policy()
        policy['expires_at'] = '2026-10-19T11:59:59Z'
        with self.assertRaisesRegex(ipc.Refusal, 'POLICY_STALE'):
            self.provision(policy=policy)
        self.assertTrue(self.model.retain_attempt)

    def test_preexisting_empty_package_refuses_and_retains(self):
        with self.assertRaisesRegex(ipc.Refusal, 'PACKAGE_PREEXISTS'):
            self.send('PREPARE', self.receipt(absent=False))
        self.assertTrue(self.model.retain_attempt)
        self.assertEqual(self.model.step, 0)

    def test_bad_nonce_signature_and_failure_retention(self):
        self.initial()
        self.emit('request.json')
        proof = self.proof()
        proof['challenge']['nonce'] = 'b' * 64
        raw = ipc.compact(proof)
        with self.assertRaisesRegex(ipc.Refusal, 'NONCE_PROOF'):
            self.send('EMIT', {'leaf': 'authentication-proof.json',
                               'sha256': sha(raw), 'size_bytes': len(raw),
                               'proof': proof})
        self.assertTrue(self.model.retain_attempt)
        self.model.disconnect()
        self.assertEqual(self.model.first_failure, 'NONCE_PROOF')

    def test_disconnection_is_sticky(self):
        self.send('PREPARE', self.receipt())
        self.model.disconnect()
        self.assertTrue(self.model.retain_attempt)
        with self.assertRaisesRegex(ipc.Refusal, 'POISONED'):
            self.send('PRIVATE_ROOT', self.receipt(private=True))


if __name__ == '__main__':
    unittest.main()
