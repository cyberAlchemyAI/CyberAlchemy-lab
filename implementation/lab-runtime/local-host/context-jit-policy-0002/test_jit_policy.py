"""Synthetic-only policy, authorization and lifecycle negative tests."""
import base64
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import jit_policy as j


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True,
                       ensure_ascii=False, allow_nan=False) + '\n').encode()


class JitPolicyTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 10, 20, 12, 0, tzinfo=dt.timezone.utc)
        self.period = Path(__file__).with_name('selected-period.json').read_bytes()
        self.spec = {
            'family_ref': '/tmp/cal-context-jit-synthetic/family',
            'source_root': '/tmp/cal-context-jit-synthetic/snapshot',
            'private_root': '/tmp/cal-context-jit-synthetic/private',
            'uid': os.getuid(), 'gid': os.getgid(),
            'principal_ref': 'principal:R03-docker-source-20261020-0001',
            'scope_ref': 'scope:synthetic-local',
            'reader_code_sha256': j.READER_CODE_SHA,
            'reader_manifest_sha256': j.READER_MANIFEST_SHA,
            'source_package_sha256': j.SOURCE_PACKAGE_SHA,
            'mapper_package_sha256': j.MAPPER_PACKAGE_SHA,
            'period_sha256': j.PERIOD_SHA,
        }
        self.selected = j.select(self.spec, self.period, self.now)
        self.auth = {
            'schema_version': 'lab-context-development-authorization/v1-candidate',
            'family_ref': self.selected['family_ref'],
            'episode_ref': self.selected['period_ref'],
            'scope_ref': self.selected['scope_ref'],
            'period_binding': {'path': j.PERIOD_REL, 'sha256': j.PERIOD_SHA},
            'not_before': '2026-10-20T11:59:00+00:00',
            'expires_at': '2026-10-20T12:15:00+00:00',
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'claim_ceiling': j.CLAIM,
        }
        self.auth_raw = encoded(self.auth)
        self.auth_result = j.validate_authorization(self.auth_raw, self.selected, self.now)
        self.auth_sha = hashlib.sha256(self.auth_raw).hexdigest()
        self.policy = {
            'schema_version': 'lab-context-host-policy/v1-candidate',
            'host_uid': os.getuid(),
            'principal_ref': self.selected['principal_ref'],
            'scope_ref': self.selected['scope_ref'],
            'reader_public_key': base64.b64encode(b'\x02' * 32).decode(),
            'not_before': '2026-10-20T11:59:00+00:00',
            'expires_at': '2026-10-20T12:10:00+00:00',
            'max_input_bytes': 1048576,
            'max_output_bytes': 2097152,
            'max_session_seconds': 900,
            'period_binding': {'path': j.PERIOD_REL, 'sha256': j.PERIOD_SHA},
            'allowed_operations': ['context.get', 'session.open'],
            'authority_effect': 'none', 'actual_owner_outcome': None,
        }

    def auth_change(self, key, value):
        changed = copy.deepcopy(self.auth)
        changed[key] = value
        return j.validate_authorization(encoded(changed), self.selected, self.now)

    def policy_change(self, key, value):
        changed = copy.deepcopy(self.policy)
        changed[key] = value
        return j.validate_policy(encoded(changed), self.selected,
                                 self.auth_raw, self.auth_sha, self.now)

    def test_exact_public_preimages(self):
        self.assertEqual(j.reviewed_preimages()['status'], 'EXACT_PUBLIC_PREIMAGES')

    def test_selected_contract_is_inert_and_scoped(self):
        self.assertEqual(self.selected['effect'], 'NOT_RUN')
        self.assertEqual(self.selected['authorization_path'],
                         self.selected['source_root'] + '/authorization/context-development.json')
        self.assertEqual(self.selected['policy_path'],
                         self.selected['private_root'] + '/permission.json')
        self.assertEqual(self.selected['reader_code_sha256'], j.READER_CODE_SHA)

    def test_selected_period_bytes_must_match(self):
        with self.assertRaises(j.Refused):
            j.select(self.spec, self.period + b' ', self.now)

    def test_expired_and_future_selection_refused(self):
        for when in (dt.datetime(2026, 10, 20, 8, 0, tzinfo=dt.timezone.utc),
                     dt.datetime(2026, 10, 21, 8, 20, tzinfo=dt.timezone.utc)):
            with self.subTest(when=when), self.assertRaises(j.Refused):
                j.select(self.spec, self.period, when)

    def test_reader_mapper_and_period_pin_changes_refused(self):
        for name in ('reader_code_sha256', 'reader_manifest_sha256',
                     'mapper_package_sha256', 'source_package_sha256', 'period_sha256'):
            changed = dict(self.spec, **{name: 'a' * 64})
            with self.subTest(name=name), self.assertRaises(j.Refused):
                j.select(changed, self.period, self.now)

    def test_principal_must_join_current_source_period(self):
        with self.assertRaises(j.Refused):
            j.select(dict(self.spec, principal_ref='principal:unrelated'),
                     self.period, self.now)

    def test_source_private_and_family_aliases_refused(self):
        for name, value in (
            ('private_root', self.spec['source_root']),
            ('private_root', self.spec['source_root'] + '/private'),
            ('source_root', self.spec['private_root'] + '/source'),
            ('family_ref', self.spec['source_root'] + '/family'),
            ('source_root', self.spec['family_ref'] + '/source')):
            changed = dict(self.spec, **{name: value})
            with self.subTest(name=name, value=value), self.assertRaises(j.Refused):
                j.select(changed, self.period, self.now)

    def test_path_traversal_and_non_tmp_refused(self):
        for name, value in (('family_ref', '/tmp/x/../y'),
                            ('source_root', '/var/lib/source'),
                            ('private_root', '/tmp//bad')):
            with self.subTest(name=name), self.assertRaises(j.Refused):
                j.select(dict(self.spec, **{name: value}), self.period, self.now)

    def test_effective_uid_and_gid_split_refused(self):
        with mock.patch.object(j.os, 'geteuid', return_value=os.getuid() + 1), \
             self.assertRaises(j.Refused):
            j.select(self.spec, self.period, self.now)
        with mock.patch.object(j.os, 'getegid', return_value=os.getgid() + 1), \
             self.assertRaises(j.Refused):
            j.select(self.spec, self.period, self.now)

    def test_effective_identity_drift_during_validation_refused(self):
        uid = os.getuid()
        with mock.patch.object(j.os, 'geteuid', side_effect=[uid, uid + 1]), \
             self.assertRaises(j.Refused):
            j.validate_authorization(encoded(self.auth), self.selected, self.now)
        with mock.patch.object(j.os, 'geteuid', side_effect=[uid, uid + 1]), \
             self.assertRaises(j.Refused):
            j.validate_policy(encoded(self.policy), self.selected,
                              self.auth_raw, self.auth_sha, self.now)

    def test_authorization_synthetic_pass(self):
        self.assertEqual(self.auth_result['authority_effect'], 'none')
        self.assertEqual(self.auth_result['scope_ref'], self.selected['scope_ref'])

    def test_authorization_wrong_family_episode_scope_or_period_refused(self):
        for name, value in (('family_ref', '/tmp/other'),
                            ('episode_ref', 'episode:old'),
                            ('scope_ref', 'scope:other'),
                            ('period_binding', {'path': j.PERIOD_REL, 'sha256': 'a' * 64})):
            with self.subTest(name=name), self.assertRaises(j.Refused):
                self.auth_change(name, value)

    def test_authorization_expired_future_or_overlong_refused(self):
        for name, value in (('expires_at', '2026-10-20T12:00:00+00:00'),
                            ('not_before', '2026-10-20T12:01:00+00:00'),
                            ('expires_at', '2026-10-20T12:30:00+00:00')):
            with self.subTest(name=name, value=value), self.assertRaises(j.Refused):
                self.auth_change(name, value)

    def test_authorization_protected_claim_or_owner_refused(self):
        for name, value in (('authority_effect', 'issuer'),
                            ('actual_owner_outcome', 'approved'),
                            ('claim_ceiling', 'protected Source8')):
            with self.subTest(name=name), self.assertRaises(j.Refused):
                self.auth_change(name, value)

    def test_authorization_extra_field_and_noncanonical_bytes_refused(self):
        with self.assertRaises(j.Refused):
            self.auth_change('issuer_key', 'fake')
        with self.assertRaises(j.Refused):
            j.validate_authorization(json.dumps(self.auth).encode(), self.selected, self.now)

    def test_host_policy_synthetic_pass(self):
        result = j.validate_policy(encoded(self.policy), self.selected,
                                   self.auth_raw, self.auth_sha, self.now)
        self.assertEqual(result['authority_effect'], 'none')
        self.assertEqual(result['authorization_sha256'], self.auth_sha)

    def test_host_policy_scope_uid_period_and_ops_refused(self):
        for name, value in (('scope_ref', 'scope:other'),
                            ('principal_ref', 'principal:other'),
                            ('host_uid', os.getuid() + 1),
                            ('period_binding', {'path': 'old', 'sha256': j.PERIOD_SHA}),
                            ('allowed_operations', ['context.get', 'session.open', 'external.write'])):
            with self.subTest(name=name), self.assertRaises(j.Refused):
                self.policy_change(name, value)

    def test_host_policy_expired_future_overlong_and_beyond_auth_refused(self):
        for name, value in (('expires_at', '2026-10-20T12:00:00+00:00'),
                            ('not_before', '2026-10-20T12:01:00+00:00'),
                            ('expires_at', '2026-10-20T12:30:00+00:00'),
                            ('not_before', '2026-10-20T11:35:00+00:00')):
            with self.subTest(name=name, value=value), self.assertRaises(j.Refused):
                self.policy_change(name, value)

    def test_host_policy_budget_and_key_refused(self):
        for name, value in (('max_input_bytes', 0), ('max_input_bytes', True),
                            ('max_output_bytes', 2097153), ('max_session_seconds', 901),
                            ('reader_public_key', 'not base64!'),
                            ('reader_public_key', base64.b64encode(b'\x02' * 31).decode())):
            with self.subTest(name=name), self.assertRaises(j.Refused):
                self.policy_change(name, value)

    def test_host_policy_protected_claim_and_auth_join_refused(self):
        with self.assertRaises(j.Refused):
            self.policy_change('authority_effect', 'issuer')
        changed_auth = encoded(dict(self.auth, scope_ref='scope:other'))
        with self.assertRaises(j.Refused):
            j.validate_policy(encoded(self.policy), self.selected,
                              changed_auth, hashlib.sha256(changed_auth).hexdigest(), self.now)

    def test_policy_refuses_forged_authorization_result_and_missing_bytes(self):
        forged = dict(self.auth_result, authorization_sha256='0' * 64,
                      expires_at='2026-10-20T12:30:00+00:00')
        for supplied in (forged, None, b''):
            with self.subTest(supplied=type(supplied).__name__), self.assertRaises(j.Refused):
                j.validate_policy(encoded(self.policy), self.selected,
                                  supplied, '0' * 64, self.now)

    def test_policy_refuses_authorization_digest_mismatch(self):
        with self.assertRaises(j.Refused):
            j.validate_policy(encoded(self.policy), self.selected,
                              self.auth_raw, '0' * 64, self.now)

    def test_policy_revalidates_expired_authorization_bytes(self):
        expired = encoded(dict(self.auth, expires_at='2026-10-20T12:00:00+00:00'))
        with self.assertRaises(j.Refused):
            j.validate_policy(encoded(self.policy), self.selected,
                              expired, hashlib.sha256(expired).hexdigest(), self.now)

    def test_policy_refuses_malformed_authorization_bytes(self):
        malformed = b'{'
        with self.assertRaises(j.Refused):
            j.validate_policy(encoded(self.policy), self.selected,
                              malformed, hashlib.sha256(malformed).hexdigest(), self.now)

    def test_policy_start_before_authorization_start_refused(self):
        changed = encoded(dict(self.policy, not_before='2026-10-20T11:50:00+00:00'))
        with self.assertRaises(j.Refused):
            j.validate_policy(changed, self.selected,
                              self.auth_raw, self.auth_sha, self.now)

    def test_policy_exact_authorization_window_boundaries(self):
        changed = encoded(dict(self.policy, expires_at=self.auth['expires_at']))
        result = j.validate_policy(changed, self.selected,
                                   self.auth_raw, self.auth_sha, self.now)
        self.assertEqual(result['authorization_sha256'], self.auth_sha)

    def test_policy_end_after_authorization_end_refused(self):
        changed = encoded(dict(self.policy, not_before='2026-10-20T12:00:00+00:00',
                               expires_at='2026-10-20T12:16:00+00:00'))
        with self.assertRaises(j.Refused):
            j.validate_policy(changed, self.selected,
                              self.auth_raw, self.auth_sha, self.now)

    def test_synthetic_private_root_lifecycle(self):
        result = j.synthetic_lifecycle(list(j.ORDER))
        self.assertEqual(result['status'], 'SYNTHETIC_ORDER_ONLY')
        self.assertFalse(result['key_generated'])

    def test_reviewed_guards_read_only_synthetic_layout_and_owned_cleanup(self):
        host = Path(__file__).resolve().parent.parent
        def load(name, path):
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        auth = load('synthetic_reviewed_auth', host / 'context-auth-guard-0004/held_auth.py')
        policy = load('synthetic_reviewed_policy', host / 'context-policy-0002/held_policy.py')
        with tempfile.TemporaryDirectory(prefix='cal-jit-synthetic-', dir='/tmp') as temp:
            base = Path(temp)
            snapshot = base / 'snapshot'
            snapshot.mkdir(mode=0o700)
            auth_dir = snapshot / 'authorization'
            auth_dir.mkdir(mode=0o700)
            auth_leaf = auth_dir / 'context-development.json'
            auth_raw = b'synthetic bytes; no authorization schema or authority\n'
            fd = os.open(auth_leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(auth_raw)
                stream.flush()
                os.fsync(stream.fileno())
            self.assertEqual(auth.read_auth_bytes(auth_leaf, snapshot,
                                                   hashlib.sha256(auth_raw).hexdigest(),
                                                   os.geteuid()), auth_raw)
            foreign = base / 'foreign'
            foreign.write_bytes(b'keep')
            private = base / 'private'
            private.mkdir(mode=0o700)
            policy_leaf = private / 'permission.json'
            policy_raw = b'synthetic bytes; no policy schema or key\n'
            fd = os.open(policy_leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(policy_raw)
                stream.flush()
                os.fsync(stream.fileno())
            self.assertEqual(policy.read_policy_bytes(policy_leaf, private, snapshot,
                                                       hashlib.sha256(policy_raw).hexdigest(),
                                                       os.geteuid(), os.getegid()), policy_raw)
            policy_leaf.unlink()
            private.rmdir()
            self.assertFalse(private.exists())
            self.assertEqual(foreign.read_bytes(), b'keep')

    def test_incomplete_reordered_or_duplicate_lifecycle_refused(self):
        for events in ([], list(j.ORDER[:-1]),
                       [j.ORDER[1], j.ORDER[0]] + list(j.ORDER[2:]),
                       list(j.ORDER) + [j.ORDER[-1]]):
            with self.subTest(events=events), self.assertRaises(j.Refused):
                j.synthetic_lifecycle(events)

    def test_actual_effect_entrypoints_refuse(self):
        self.assertFalse(j.EFFECT_ENABLED)
        with self.assertRaises(j.Refused):
            j.provision_actual()
        with self.assertRaises(j.Refused):
            j.launch_context()


if __name__ == '__main__':
    unittest.main()
