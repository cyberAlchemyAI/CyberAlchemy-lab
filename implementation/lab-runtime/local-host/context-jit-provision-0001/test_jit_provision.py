"""Synthetic, effect-disabled Context JIT construction tests."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest import mock

import jit_provision as p


class JitProvisionTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 10, 20, 12, 0, tzinfo=dt.timezone.utc)
        self.period = Path(__file__).with_name('selected-period.json').read_bytes()
        self.selected = p.select_context(self.period, self.now, p.SCOPE)
        self.jit = p.jit_module()
        self.auth = {
            'schema_version': 'lab-context-development-authorization/v1-candidate',
            'family_ref': str(p.CONTEXT_FAMILY),
            'episode_ref': self.selected['period_ref'], 'scope_ref': p.SCOPE,
            'period_binding': {'path': self.jit.PERIOD_REL, 'sha256': self.jit.PERIOD_SHA},
            'not_before': '2026-10-20T11:59:00Z',
            'expires_at': '2026-10-20T12:15:00Z',
            'authority_effect': 'none', 'actual_owner_outcome': None,
            'claim_ceiling': self.jit.CLAIM,
        }
        self.auth_raw = p.wire(self.auth)
        self.auth_sha = hashlib.sha256(self.auth_raw).hexdigest()
        self.public_key = b'\x02' * 32

    def test_exact_public_preimages_and_scope_binding(self):
        proof = p.reviewed_inputs()
        self.assertEqual(proof['source_scope_ref'], p.SCOPE)
        self.assertEqual(proof['stage_effect'], 'NOT_RUN')
        self.assertEqual(proof['preimages'], 9)

    def test_sibling_topology_accepted_by_reviewed_jit_v2(self):
        self.assertEqual(self.selected['family_ref'], str(p.CONTEXT_FAMILY))
        self.assertEqual(self.selected['authorization_path'],
                         str(p.SOURCE_FAMILY / 'authorization/context-development.json'))
        self.assertEqual(self.selected['policy_path'], str(p.PRIVATE_ROOT / 'permission.json'))
        self.assertEqual(p.CONTEXT_FAMILY.parent, p.SOURCE_FAMILY.parent)
        self.assertFalse(p.CONTEXT_FAMILY.is_relative_to(p.SOURCE_FAMILY))
        self.assertFalse(p.SOURCE_FAMILY.is_relative_to(p.CONTEXT_FAMILY))

    def test_common_interface_family_would_be_refused(self):
        spec = {'family_ref': str(p.CONTEXT_FAMILY.parent),
                'source_root': str(p.SOURCE_FAMILY), 'private_root': str(p.PRIVATE_ROOT),
                'uid': os.getuid(), 'gid': os.getgid(),
                'principal_ref': self.selected['principal_ref'], 'scope_ref': p.SCOPE,
                'reader_code_sha256': self.jit.READER_CODE_SHA,
                'reader_manifest_sha256': self.jit.READER_MANIFEST_SHA,
                'source_package_sha256': self.jit.SOURCE_PACKAGE_SHA,
                'mapper_package_sha256': self.jit.MAPPER_PACKAGE_SHA,
                'period_sha256': self.jit.PERIOD_SHA}
        with self.assertRaises(ValueError):
            self.jit.select(spec, self.period, self.now)

    def test_wrong_signed_scope_and_period_refused(self):
        with self.assertRaises(p.Refused):
            p.select_context(self.period, self.now, 'scope:other')
        with self.assertRaises(ValueError):
            p.select_context(self.period + b' ', self.now, p.SCOPE)

    def test_selected_identity_drift_refused(self):
        with mock.patch.object(p.os, 'geteuid', return_value=os.getuid() + 1), \
             self.assertRaises(ValueError):
            p.select_context(self.period, self.now, p.SCOPE)

    def test_real_ed25519_public_key_policy_schema_construction(self):
        raw, proof = p.construct_policy(self.selected, self.auth_raw,
                                        self.auth_sha, self.public_key, self.now)
        policy = json.loads(raw)
        self.assertEqual(proof['authorization_sha256'], self.auth_sha)
        self.assertEqual(policy['scope_ref'], p.SCOPE)
        self.assertEqual(policy['expires_at'], self.auth['expires_at'])
        self.assertEqual(policy['max_session_seconds'], 900)
        self.assertEqual(policy['authority_effect'], 'none')
        self.assertEqual(proof['policy_sha256'], hashlib.sha256(raw).hexdigest())

    def test_policy_caps_at_twenty_minutes(self):
        auth = dict(self.auth, not_before='2026-10-20T12:00:00Z',
                    expires_at='2026-10-20T12:20:00Z')
        raw = p.wire(auth)
        policy_raw, _ = p.construct_policy(self.selected, raw, hashlib.sha256(raw).hexdigest(),
                                            self.public_key, self.now)
        self.assertEqual(json.loads(policy_raw)['expires_at'], '2026-10-20T12:20:00Z')

    def test_wrong_authorization_digest_and_scope_refused(self):
        with self.assertRaises(p.Refused):
            p.construct_policy(self.selected, self.auth_raw, '0' * 64,
                               self.public_key, self.now)
        wrong = p.wire(dict(self.auth, scope_ref='scope:other'))
        with self.assertRaises(ValueError):
            p.construct_policy(self.selected, wrong, hashlib.sha256(wrong).hexdigest(),
                               self.public_key, self.now)

    def test_expired_authorization_and_wrong_public_key_refused(self):
        expired = p.wire(dict(self.auth, expires_at='2026-10-20T12:00:00Z'))
        with self.assertRaises(ValueError):
            p.construct_policy(self.selected, expired, hashlib.sha256(expired).hexdigest(),
                               self.public_key, self.now)
        with self.assertRaises(p.Refused):
            p.construct_policy(self.selected, self.auth_raw, self.auth_sha,
                               b'\x00' * 31, self.now)

    def test_non_whole_second_time_refused_for_policy_output(self):
        now = self.now.replace(microsecond=1)
        with self.assertRaises(p.Refused):
            p.construct_policy(self.selected, self.auth_raw, self.auth_sha,
                               self.public_key, now)

    def test_projected_build_and_control_use_held_guards(self):
        projected = p.project_roles()
        build, control = projected['build.py'], projected['control.py']
        self.assertIn(b'def provision(path, source):\n    _t35_effect_refused()', build)
        self.assertIn(("JIT_PRIVATE_ROOT = Path('" + str(p.PRIVATE_ROOT) + "')").encode(), build)
        self.assertIn(b'def _jit_private_root():\n    _t35_effect_refused()', build)
        self.assertIn(b'_jit_private_root() as tmp:', build)
        self.assertIn(b'require(root == JIT_PRIVATE_ROOT', build)
        self.assertIn(b'read_policy_bytes(path, path.parent, ROOT', build)
        self.assertIn(b"EL.parse(read_policy_bytes(policy_path, policy_path.parent, ROOT", build)
        self.assertIn(b"AUTH = ROOT / 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001'", control)
        self.assertIn(b"value['family_ref'] == str(HERE)", control)
        self.assertIn(b"read_auth_bytes(AUTH, ROOT / 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001'", control)
        self.assertNotIn(b'AUTH.read_bytes()', control)
        self.assertNotIn(b'load(policy_path)', build)

    def test_projection_preimage_mutation_refused(self):
        with mock.patch.object(p, 'STAGE_BUILD_SHA', '0' * 64), \
             self.assertRaises(p.Refused):
            p.project_roles()

    def test_synthetic_success_and_failure_rollback_order(self):
        self.assertEqual(p.synthetic_lifecycle(list(p.LIFECYCLE))['effect'], 'NOT_RUN')
        for failure in p.LIFECYCLE:
            prefix = p.LIFECYCLE[:p.LIFECYCLE.index(failure)]
            suffix = ('ROLLBACK_CLOSE_CHANNEL_IF_OPEN', 'ROLLBACK_DROP_KEY_IF_CREATED',
                      'ROLLBACK_REMOVE_ONLY_OWNED_PRIVATE_ROOT_IF_CREATED',
                      'ROLLBACK_VERIFY_OWNED_ROOT_ABSENT', 'RECORD_ATTEMPT_CONSUMED')
            self.assertEqual(p.synthetic_lifecycle(list(prefix + ('FAIL:' + failure,) + suffix),
                                                   failure)['status'],
                             'SYNTHETIC_ROLLBACK_ORDER')

    def test_uncertain_cleanup_preserves_evidence_and_refuses_reuse(self):
        failure = 'HELD_POLICY_READBACK_AND_PIN'
        prefix = p.LIFECYCLE[:p.LIFECYCLE.index(failure)]
        suffix = ('ROLLBACK_CLOSE_CHANNEL_IF_OPEN', 'ROLLBACK_DROP_KEY_IF_CREATED',
                  'PRESERVE_UNKNOWN_EFFECT_EVIDENCE', 'RECORD_UNKNOWN_REFUSE_REUSE')
        result = p.synthetic_lifecycle(list(prefix + ('FAIL:' + failure,) + suffix),
                                       failure, cleanup='uncertain')
        self.assertEqual(result['status'], 'SYNTHETIC_UNKNOWN_PRESERVED')
        self.assertFalse(result['attempt_reusable'])

    def test_wrong_lifecycle_or_foreign_cleanup_refused(self):
        with self.assertRaises(p.Refused):
            p.synthetic_lifecycle(list(p.LIFECYCLE[:-1]))
        failure = p.LIFECYCLE[4]
        prefix = p.LIFECYCLE[:4]
        with self.assertRaises(p.Refused):
            p.synthetic_lifecycle(list(prefix + ('FAIL:' + failure,
                'ROLLBACK_REMOVE_FOREIGN_ROOT')), failure)

    def test_all_effect_entrypoints_refuse(self):
        for action in (p.generate_private_key, p.write_authorization_or_policy,
                       p.launch_context):
            with self.subTest(action=action.__name__), self.assertRaises(p.Refused):
                action()


if __name__ == '__main__':
    unittest.main()
