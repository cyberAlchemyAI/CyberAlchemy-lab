import datetime as dt
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('authority_release_0001', HERE / 'authority_release.py')
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
NOW = dt.datetime(2026, 10, 20, 14, 0, tzinfo=dt.timezone.utc)


class AuthorityReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.period_raw = A.public_selection()
        cls.baseline_files, cls.baseline_dirs = A.stage_names()

    @classmethod
    def tearDownClass(cls):
        if (cls.baseline_files, cls.baseline_dirs) != A.stage_names():
            raise AssertionError('staged namespace changed during inert tests')

    def test_exact_staged_metadata_without_archive_body(self):
        self.assertEqual(len(self.baseline_files), 1570)
        self.assertEqual(len(self.baseline_dirs), 1021)
        self.assertNotIn(A.AUTH_REL, self.baseline_files)
        self.assertNotIn(A.AUTH_DIR_REL, self.baseline_dirs)
        with self.assertRaises(A.Refused):
            A.pinned(A.SOURCE / 'packages/0001/branch.snapshot')

    def test_exact_topology_delta_and_modes(self):
        result = A.topology_projection(self.baseline_files, self.baseline_dirs)
        self.assertEqual((result['projected_files'], result['projected_directories']),
                         (1571, 1022))
        self.assertEqual((result['added_file'], result['added_directory']),
                         (A.AUTH_REL, A.AUTH_DIR_REL))
        self.assertEqual((result['source_mode'], result['authorization_directory_mode'],
                          result['authorization_leaf_mode']), ('0700', '0700', '0600'))
        self.assertEqual(result['actual_namespace_effect'], 'NOT_RUN')

    def test_topology_refuses_preexisting_auth_file_and_dir(self):
        with self.assertRaises(A.Refused):
            A.topology_projection(self.baseline_files | {A.AUTH_REL}, self.baseline_dirs)
        with self.assertRaises(A.Refused):
            A.topology_projection(self.baseline_files, self.baseline_dirs | {A.AUTH_DIR_REL})

    def test_topology_refuses_changed_baseline_counts(self):
        with self.assertRaises(A.Refused):
            A.topology_projection(self.baseline_files - {next(iter(self.baseline_files))},
                                  self.baseline_dirs)

    def test_selected_public_scope_and_exact_period(self):
        period, end = A.period_window(self.period_raw, NOW)
        self.assertEqual(period['period_ref'],
                         'protocol:R03-docker-source-20261020-0001-period/v1')
        self.assertEqual(end - NOW, dt.timedelta(minutes=20))

    def test_expired_and_early_period_refused(self):
        for now in (dt.datetime(2026, 10, 20, 8, 19, tzinfo=dt.timezone.utc),
                    dt.datetime(2026, 10, 21, 8, 20, tzinfo=dt.timezone.utc)):
            with self.subTest(now=now), self.assertRaises(A.Refused):
                A.period_window(self.period_raw, now)

    def test_interval_truncated_at_period_end(self):
        now = dt.datetime(2026, 10, 21, 8, 19, 59, tzinfo=dt.timezone.utc)
        _, end = A.period_window(self.period_raw, now)
        self.assertEqual(end - now, dt.timedelta(seconds=1))

    def test_mutated_period_and_wrong_scope_refused(self):
        value = json.loads(self.period_raw)
        value['expires_at'] = '2026-10-22T08:20:00+00:00'
        with self.assertRaises(A.Refused):
            A.period_window(A.wire(value), NOW)
        with self.assertRaises(A.Refused):
            A.selected_jit(self.period_raw, NOW, 'scope:forged')

    def test_projected_auth_validates_exact_schema_and_window(self):
        raw, proof = A.project_authorization(self.period_raw, NOW, A.EXPECTED_SCOPE)
        self.assertEqual(proof['sha256'], A.sha(raw))
        self.assertEqual(proof['claim'], 'SYNTHETIC_PROJECTION_UNISSUED')
        self.assertEqual(json.loads(raw)['family_ref'], str(A.CONTEXT))
        self.assertEqual(json.loads(raw)['expires_at'], '2026-10-20T14:20:00Z')
        self.assertFalse(A.AUTH_LEAF.exists())

    def test_actual_effects_refuse(self):
        for function in (A.issue_actual, A.mutate_stage, A.create_runtime_key):
            with self.subTest(function=function.__name__), self.assertRaises(A.Refused):
                function()
        with self.assertRaises(A.Refused):
            A.effect_time_signed_scope(object(), NOW)

    def test_fixture_marker_durable_and_no_retry(self):
        with tempfile.TemporaryDirectory(prefix='cal-authority-release-fixture-', dir='/tmp') as base:
            result = A.fixture_reserve(base)
            self.assertEqual(result['status'], 'FIXTURE_INTENT_DURABLE')
            self.assertFalse(result['retry_allowed'])
            self.assertEqual(json.loads(Path(result['marker']).read_bytes())['event'], 'INTENT')
            with self.assertRaises(FileExistsError):
                A.fixture_reserve(base)

    def test_fixture_uncertain_write_and_close_consume_attempt(self):
        for point in ('write', 'close'):
            with self.subTest(point=point), tempfile.TemporaryDirectory(
                    prefix='cal-authority-release-fixture-', dir='/tmp') as base:
                result = A.fixture_reserve(base, inject=point)
                self.assertEqual(result['status'], 'UNKNOWN_PRESERVE_NO_RETRY')
                self.assertTrue(Path(result['marker']).exists())
                with self.assertRaises(FileExistsError):
                    A.fixture_reserve(base)

    def test_real_release_order_has_close_before_authority(self):
        order = A.future_release_contract()
        self.assertLess(order.index('RESERVE_EXCLUSIVE_DURABLE_ONE_SHOT_MARKER_OUTSIDE_AUTH_DIRECTORY'),
                        order.index('OPEN_READER_OPEN_SIGNED_ON_EXACT_STAGED_FAMILY'))
        self.assertLess(order.index('CLOSE_SIGNED_VIEW_AND_REQUIRE_SUCCESSFUL_FINAL_GUARD_AND_CLOSE'),
                        order.index('CREATE_AUTH_DIRECTORY_EXCLUSIVE_OWNER_0700_NOFOLLOW_AND_FSYNC_SOURCE'))
        self.assertLess(order.index('WRITE_VERSIONED_FINAL_SELECTION_AND_DURABLE_AUTHORITY_RECEIPT'),
                        order.index('CHILD_GENERATES_ONE_USE_KEY_IN_ITS_EXCLUSIVE_0700_PRIVATE_ROOT'))
        self.assertIn('NO_BY_NAME_CLEANUP_AFTER_UNCERTAINTY_OR_SAME_UID_INTERFERENCE', order)


if __name__ == '__main__':
    unittest.main()
