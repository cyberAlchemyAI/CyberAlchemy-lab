"""Synthetic-only JIT custody and versioned stage-topology tests."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import effect_adapter as e


class EffectAdapterTests(unittest.TestCase):
    def base(self):
        return tempfile.TemporaryDirectory(prefix='cal-jit-effect-fixture-', dir='/tmp')

    def events(self, base):
        return [json.loads(path.read_text())['event']
                for path in sorted((Path(base) / 'journal').glob('*.json'))]

    def test_exact_reviewed_preimages_and_guard_shape(self):
        proof = e.reviewed_preimages()
        self.assertEqual(proof['count'], 18)
        self.assertEqual(proof['effect'], 'NOT_RUN')
        self.assertEqual(proof['source_signed_view'], 'NOT_OPENED')

    def test_versioned_topology_amendment_is_explicitly_unselected(self):
        value = e.topology_contract()
        self.assertEqual(value['predecessor_file_count'], 1570)
        self.assertEqual(value['proposed_file_count_after_exact_auth_leaf'], 1571)
        self.assertEqual(value['source_role']['required_mode'], '0700')
        self.assertEqual(value['source_role']['predecessor_observed_mode'], '0755')
        self.assertEqual(value['authorization_leaf']['sha256'], 'UNMINTED_UNSELECTED')
        self.assertEqual(value['selection_effect'], 'NOT_RUN')
        self.assertEqual(len(value['role_replacements']), 2)

    def test_effect_plan_orders_signed_scope_before_authority_and_challenge(self):
        plan = e.effect_plan()
        steps = plan['steps']
        self.assertLess(steps.index('OPEN_EXACT_READER_SIGNED_SOURCE_AND_GUARD'),
                        steps.index('OBTAIN_APPROVED_ISSUER_AUTHORIZATION_FOR_EXACT_CONTEXT_FAMILY'))
        self.assertLess(steps.index('WRITE_AUTH_EXCLUSIVE_0600_NOFOLLOW_FSYNC_AND_HELD_READBACK'),
                        steps.index('GENERATE_ONE_USE_IN_MEMORY_ED25519_PRIVATE_KEY'))
        self.assertLess(steps.index('WRITE_POLICY_EXCLUSIVE_0600_NOFOLLOW_FSYNC_AND_HELD_READBACK'),
                        steps.index('OPEN_HOSTCHANNEL_AND_AUTHENTICATE_EXACT_CHALLENGE_ONCE'))
        self.assertLess(steps.index('PROVE_RACE_SAFE_CLEANUP_OR_EXPLICIT_TRUSTED_UID_EXCLUSIVITY'),
                        steps.index('REMOVE_ONLY_VERIFIED_OWNED_AUTH_AND_PRIVATE_POLICY_OBJECTS'))
        self.assertEqual(plan['effect'], 'NOT_RUN')
        self.assertEqual(plan['unknown_rule'], 'PRESERVE_EVIDENCE_AND_NEVER_REUSE_ATTEMPT')

    def test_signed_scope_contract_refuses_wrong_or_unguarded_view(self):
        self.assertEqual(e.signed_scope_contract(
            'scope:cyberalchemy-lab-first-agent-episode', True, True)['claim'],
            'SYNTHETIC_ONLY')
        for scope, source, package in (
                ('scope:other', True, True),
                ('scope:cyberalchemy-lab-first-agent-episode', False, True),
                ('scope:cyberalchemy-lab-first-agent-episode', True, False),
                ('scope:cyberalchemy-lab-first-agent-episode', 1, True)):
            with self.subTest(scope=scope, source=source, package=package), \
                 self.assertRaises(e.Refused):
                e.signed_scope_contract(scope, source, package)

    def test_fixture_one_shot_held_readback_and_custody_preserved(self):
        with self.base() as base:
            result = e.fixture_one_shot(base)
            self.assertEqual(result['status'], 'CUSTODY_PRESERVED')
            self.assertFalse(result['attempt_reusable'])
            self.assertTrue(result['private_root_present'])
            self.assertTrue((Path(base) / 'source-role').is_dir())
            self.assertTrue((Path(base) / 'source-role/authorization/context-development.json').is_file())
            self.assertTrue((Path(base) / 'private-root/permission.json').is_file())
            self.assertIn('HELD_DUMMY_READBACK_CONFIRMED', self.events(base))
            self.assertEqual(self.events(base)[-1], 'ATTEMPT_CONSUMED_CUSTODY_PRESERVED')
            before = self.events(base)
            with self.assertRaises(e.Refused):
                e.fixture_one_shot(base)
            self.assertEqual(self.events(base), before)

    def test_failure_preserves_objects_and_consumes_attempt(self):
        with self.base() as base:
            result = e.fixture_one_shot(base, 'fail_after_policy')
            self.assertEqual(result['status'], 'FAILED_PRESERVED')
            self.assertFalse(result['attempt_reusable'])
            self.assertTrue((Path(base) / 'private-root/permission.json').is_file())
            self.assertEqual(self.events(base)[-1], 'ATTEMPT_CONSUMED_CUSTODY_PRESERVED')

    def test_unknown_preserves_owned_objects_and_attempt(self):
        with self.base() as base:
            result = e.fixture_one_shot(base, 'unknown_after_policy')
            self.assertEqual(result['status'], 'UNKNOWN_PRESERVED')
            self.assertFalse(result['attempt_reusable'])
            self.assertTrue((Path(base) / 'private-root/permission.json').is_file())
            self.assertTrue((Path(base) / 'source-role/authorization/context-development.json').is_file())
            self.assertEqual(self.events(base)[-1], 'UNKNOWN_PRESERVE_OBJECTS_REFUSE_REUSE')
            before = self.events(base)
            with self.assertRaises(e.Refused):
                e.fixture_one_shot(base)
            self.assertEqual(self.events(base), before)

    def test_unexpected_disposition_observation_failure_records_unknown(self):
        with self.base() as base:
            with mock.patch.object(e, '_same', side_effect=OSError('synthetic identity uncertainty')):
                with self.assertRaises(e.Unknown):
                    e.fixture_one_shot(base)
            self.assertTrue((Path(base) / 'private-root/permission.json').is_file())
            self.assertEqual(self.events(base)[-1], 'UNKNOWN_PRESERVE_EVIDENCE_REFUSE_REUSE')

    def test_file_rename_replacement_preserves_foreign_and_detached_owned(self):
        with self.base() as base:
            with self.assertRaises(e.Unknown):
                e.fixture_one_shot(base, 'replace_policy_name')
            self.assertEqual((Path(base) / 'private-root/permission.json').read_bytes(),
                             b'foreign replacement; preserve\n')
            self.assertEqual((Path(base) / 'detached-owned-policy').read_bytes(),
                             e.FIXTURE_POLICY)
            self.assertEqual(self.events(base)[-1], 'UNKNOWN_PRESERVE_EVIDENCE_REFUSE_REUSE')

    def test_directory_rename_replacement_preserves_foreign_and_detached_owned(self):
        with self.base() as base:
            with self.assertRaises(e.Unknown):
                e.fixture_one_shot(base, 'replace_private_dir_name')
            self.assertTrue((Path(base) / 'private-root').is_dir())
            self.assertEqual(list((Path(base) / 'private-root').iterdir()), [])
            self.assertEqual((Path(base) / 'detached-owned-private/permission.json').read_bytes(),
                             e.FIXTURE_POLICY)
            self.assertEqual(self.events(base)[-1], 'UNKNOWN_PRESERVE_EVIDENCE_REFUSE_REUSE')

    def test_preoccupied_detached_file_is_never_overwritten(self):
        with self.base() as base:
            target = Path(base) / 'detached-owned-policy'
            target.write_bytes(b'FOREIGN_COLLISION\n')
            before = target.stat().st_ino
            with self.assertRaises(e.Unknown):
                e.fixture_one_shot(base, 'replace_policy_name')
            self.assertEqual(target.read_bytes(), b'FOREIGN_COLLISION\n')
            self.assertEqual(target.stat().st_ino, before)
            self.assertEqual((Path(base) / 'private-root/permission.json').read_bytes(),
                             e.FIXTURE_POLICY)
            self.assertEqual(self.events(base)[-1], 'UNKNOWN_PRESERVE_EVIDENCE_REFUSE_REUSE')

    def test_preoccupied_detached_directory_is_never_overwritten(self):
        with self.base() as base:
            target = Path(base) / 'detached-owned-private'
            target.mkdir(mode=0o700)
            before = target.stat().st_ino
            with self.assertRaises(e.Unknown):
                e.fixture_one_shot(base, 'replace_private_dir_name')
            self.assertEqual(target.stat().st_ino, before)
            self.assertEqual(list(target.iterdir()), [])
            self.assertEqual((Path(base) / 'private-root/permission.json').read_bytes(),
                             e.FIXTURE_POLICY)
            self.assertEqual(self.events(base)[-1], 'UNKNOWN_PRESERVE_EVIDENCE_REFUSE_REUSE')

    def test_adapter_has_no_name_deletion_calls(self):
        source = Path(e.__file__).read_bytes()
        self.assertNotIn(b'os.unlink(', source)
        self.assertNotIn(b'os.rmdir(', source)
        self.assertNotIn(b'os.rename(', source)

    def test_no_replace_refuses_preexisting_foreign_root(self):
        with self.base() as base:
            foreign = Path(base) / 'source-role'
            foreign.mkdir(mode=0o700)
            (foreign / 'foreign.txt').write_text('retain')
            with self.assertRaises(e.Refused):
                e.fixture_one_shot(base)
            self.assertEqual((foreign / 'foreign.txt').read_text(), 'retain')
            self.assertFalse((Path(base) / 'journal').exists())

    def test_no_replace_refuses_symlink(self):
        with self.base() as base:
            (Path(base) / 'source-role').symlink_to('/tmp')
            with self.assertRaises(e.Refused):
                e.fixture_one_shot(base)
            self.assertTrue((Path(base) / 'source-role').is_symlink())
            self.assertFalse((Path(base) / 'journal').exists())

    def test_wrong_fixture_base_and_mode_refused(self):
        with tempfile.TemporaryDirectory(prefix='other-', dir='/tmp') as base:
            with self.assertRaises(e.Refused):
                e.fixture_one_shot(base)
        with self.base() as base:
            os.chmod(base, 0o755)
            with self.assertRaises(e.Refused):
                e.fixture_one_shot(base)
            self.assertFalse((Path(base) / 'journal').exists())

    def test_guard_rejects_wrong_fixture_file_mode(self):
        with self.base() as base:
            result = e.fixture_one_shot(base, 'unknown_after_policy')
            self.assertEqual(result['status'], 'UNKNOWN_PRESERVED')
            auth = Path(base) / 'source-role/authorization/context-development.json'
            os.chmod(auth, 0o644)
            guard = e.load_guard('_fixture_test_auth', e.LOCAL / 'context-auth-guard-0004/held_auth.py', e.AUTH_GUARD)
            with self.assertRaises(ValueError):
                guard.read_auth_bytes(auth, auth.parent.parent, result['auth_sha256'], os.geteuid())

    def test_actual_effect_entrypoints_unconditionally_refuse(self):
        self.assertFalse(e.EFFECT_ENABLED)
        for action in (e.actual_one_shot, e.create_actual_authorization,
                       e.generate_actual_key):
            with self.subTest(action=action.__name__), self.assertRaises(e.Refused):
                action()


if __name__ == '__main__':
    unittest.main()
