"""Read-only and synthetic tests; no grant, key, private body or Docker effect."""
import base64
import datetime as dt
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

MODULE_PATH = Path(__file__).with_name('jit_successor.py')
SPEC = importlib.util.spec_from_file_location('jit_successor_candidate', MODULE_PATH)
J = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(J)


class SuccessorJitTests(unittest.TestCase):
    def test_actual_source_public_review_and_current_period(self):
        real_leaf = J.public_leaf
        def no_archive(path, pin, maximum=2 * 1024 * 1024):
            self.assertNotEqual(Path(path).name, 'branch.snapshot')
            return real_leaf(path, pin, maximum)
        with mock.patch.object(J, 'public_leaf', side_effect=no_archive):
            state = J.wait_for_mapper()
        self.assertEqual(state['status'], 'WAIT_INDEPENDENT_MAPPER_EFFECT_AND_SIGNED_SCOPE')
        self.assertEqual(state['source']['source_effect_review_sha256'], J.SOURCE_REVIEW_SHA)
        self.assertEqual(state['source']['period_sha256'], J.SOURCE_PERIOD_SHA)
        self.assertEqual(state['source']['protected_archive_body'], 'UNREAD')
        self.assertEqual(state['source']['scope_attestation'], 'NOT_OPENED_SIGNED_SOURCE_VIEW')

    def test_source_review_or_period_expiry_cannot_be_assumed(self):
        with mock.patch.object(J, 'SOURCE_REVIEW_SHA', '0'*64):
            with self.assertRaisesRegex(J.Refused, 'PUBLIC_LEAF_PIN'):
                J.source_preflight()
        with self.assertRaisesRegex(J.Refused, 'CURRENT_SOURCE_PERIOD_JOIN'):
            J.source_preflight(dt.datetime(2026, 10, 21, 15, 0, tzinfo=dt.timezone.utc))

    def test_current_source_manifest_body_drift_refused(self):
        original = J.SOURCE_MANIFEST.read_bytes()
        self.assertEqual(J.sha(original), J.SOURCE_MANIFEST_SHA)
        with tempfile.TemporaryDirectory(prefix='cal-jit-manifest-fixture-', dir='/tmp') as temp:
            altered = Path(temp) / 'source-manifest.json'
            altered.write_bytes(original[:-2] + b'!\n')
            with mock.patch.object(J, 'SOURCE_MANIFEST', altered):
                with self.assertRaisesRegex(J.Refused, 'PUBLIC_LEAF_PIN'):
                    J.source_preflight()

    def test_durable_topology_and_guarded_reprojection(self):
        paths = J.topology()
        self.assertTrue(paths['stage_root'].startswith('/home/vlad_/.local/state/'))
        self.assertFalse(paths['private_root'].startswith('/tmp/'))
        self.assertNotIn(paths['private_root'], paths['stage_root'])
        predecessor = (J.LOCAL / 'context-jit-provision-0001/projected-build.py').read_bytes()
        projected = J.rebind_guarded_build(predecessor)
        self.assertIn(str(J.PRIVATE_ROOT).encode(), projected)
        self.assertNotIn(b'/tmp/cal-context-jit-private-', projected)
        self.assertIn(b'_t35_effect_refused()', projected)
        with self.assertRaisesRegex(J.Refused, 'PREDECESSOR_JIT_PRIVATE_ROOT_SPAN'):
            J.rebind_guarded_build(projected)

    def test_synthetic_mapper_review_does_not_join_actual_source_package(self):
        selector_dir = J.LOCAL / 'context-successor-selector-0001'
        sys.path.insert(0, str(selector_dir))
        try:
            spec = importlib.util.spec_from_file_location('context_selector_fixture',
                                                           selector_dir / 'test_adapter.py')
            fixture_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(fixture_module)
            data = fixture_module.fixture()
        finally:
            sys.path.remove(str(selector_dir))
        with self.assertRaisesRegex(J.Refused, 'CURRENT_MAPPER_CONTEXT_SELECTION_JOIN'):
            J.select_after_mapper(data)

    def test_pure_policy_candidate_byte_bound_and_20_minute_cap(self):
        source = J.source_preflight()
        now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
        selected = {'status':'MAPPER_SELECTED_JIT_AUTHORITY_HOLD',
                    'signed_scope_attestation':'NOT_OPENED',
                    'source':source,'topology':J.topology()}
        auth = {'schema_version':'lab-context-development-authorization/v1-candidate',
                'family_ref':J.topology()['context_family_ref'],
                'episode_ref':J.PERIOD_REF,'scope_ref':J.EXPECTED_SCOPE,
                'period_binding':{'path':J.SOURCE_ROLE+'/packages/0001/period.json',
                                  'sha256':J.SOURCE_PERIOD_SHA},
                'not_before':now.isoformat(),
                'expires_at':(now+dt.timedelta(minutes=19)).isoformat(),
                'authority_effect':'none','actual_owner_outcome':None,
                'claim_ceiling':'Local disposable development episode only; no protected Source8 issuer grant or owner outcome.'}
        raw = J.canonical(auth)
        dummy_public = base64.b64encode(bytes(32)).decode()
        policy = J.construct_policy_candidate(selected=selected,
                    authorization_raw=raw,authorization_sha256=J.sha(raw),
                    reader_public_key=dummy_public,now=now)
        self.assertEqual(policy['status'], 'SYNTHETIC_POLICY_BYTES_ONLY')
        self.assertEqual(policy['effect'], 'NOT_RUN')
        self.assertEqual(J.parse(policy['policy_raw'])['expires_at'], auth['expires_at'])
        with self.assertRaisesRegex(J.Refused, 'EXACT_AUTHORIZATION_BYTES_REQUIRED'):
            J.construct_policy_candidate(selected=selected,
                authorization_raw=raw,authorization_sha256='0'*64,
                reader_public_key=dummy_public,now=now)
        auth['expires_at'] = (now+dt.timedelta(minutes=21)).isoformat()
        overlong = J.canonical(auth)
        with self.assertRaisesRegex(J.Refused, 'AUTHORIZATION_SCOPE_PERIOD_POSTURE'):
            J.construct_policy_candidate(selected=selected,
                authorization_raw=overlong,authorization_sha256=J.sha(overlong),
                reader_public_key=dummy_public,now=now)

    def test_forged_caller_period_cannot_extend_actual_source(self):
        actual = J.source_preflight()
        after_end = dt.datetime(2026, 10, 21, 15, 1, tzinfo=dt.timezone.utc)
        forged = dict(actual, period_end='2026-10-22T15:00:00+00:00')
        selected = {'status':'MAPPER_SELECTED_JIT_AUTHORITY_HOLD',
                    'signed_scope_attestation':'NOT_OPENED',
                    'source':forged,'topology':J.topology()}
        auth = {'schema_version':'lab-context-development-authorization/v1-candidate',
                'family_ref':J.topology()['context_family_ref'],
                'episode_ref':J.PERIOD_REF,'scope_ref':J.EXPECTED_SCOPE,
                'period_binding':{'path':J.SOURCE_ROLE+'/packages/0001/period.json',
                                  'sha256':J.SOURCE_PERIOD_SHA},
                'not_before':after_end.isoformat(),
                'expires_at':(after_end+dt.timedelta(minutes=19)).isoformat(),
                'authority_effect':'none','actual_owner_outcome':None,
                'claim_ceiling':'Local disposable development episode only; no protected Source8 issuer grant or owner outcome.'}
        raw = J.canonical(auth)
        dummy_public = base64.b64encode(bytes(32)).decode()
        with self.assertRaisesRegex(J.Refused, 'CURRENT_SOURCE_PERIOD_JOIN'):
            J.construct_policy_candidate(selected=selected,authorization_raw=raw,
                authorization_sha256=J.sha(raw),reader_public_key=dummy_public,
                now=after_end)
        within = dt.datetime(2026, 10, 20, 16, 0, tzinfo=dt.timezone.utc)
        with self.assertRaisesRegex(J.Refused, 'CURRENT_SELECTED_SOURCE_PERIOD_REQUIRED'):
            J.construct_policy_candidate(selected=selected,authorization_raw=raw,
                authorization_sha256=J.sha(raw),reader_public_key=dummy_public,
                now=within)

    def test_all_effect_entrypoints_refuse(self):
        for operation in (J.issue_authorization, J.generate_key,
                          J.create_private_root_or_policy, J.launch_context):
            with self.assertRaisesRegex(J.Refused, 'EFFECT_DISABLED'):
                operation()


if __name__ == '__main__':
    unittest.main()
