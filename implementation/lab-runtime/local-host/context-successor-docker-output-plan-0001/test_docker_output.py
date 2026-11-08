"""Causal public-contract tests; no real Context or Docker effect."""
import datetime as dt
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

SOURCE = Path(__file__).with_name('docker_output.py')
spec = importlib.util.spec_from_file_location('docker_output_tested',SOURCE)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class DockerOutputPlanTests(unittest.TestCase):
    def rows(self):
        current = adapter.plan()
        return [{'path':current['logical_output_root']+'/'+leaf,
                 'sha256':format(i+1,'064x')}
                for i,leaf in enumerate(current['output_leaves'][:-1])]

    def test_durable_successor_and_original_protocol(self):
        result = adapter.plan()
        self.assertEqual(result['status'],'WAIT_MAPPER_STAGE_AUTH_AND_CONTEXT_SOURCE')
        self.assertEqual(result['physical_stage_files_required'],1571)
        self.assertEqual((result['output_leaf_count'],result['manifest_member_rows']),
                         (40,39))
        self.assertEqual(result['emit_ordinals'],list(range(1,41)))
        self.assertEqual((result['writer_private_release_ordinal'],
                          result['finish_ordinal'],result['wire_request_count']),
                         (38,41,42))
        self.assertNotIn('20261020-0001',result['context_role'])
        self.assertNotIn('/tmp/',result['physical_output_root'])
        self.assertEqual(result['output_parent_access'],
                         'HOST_WRITER_RW_CHILD_WORKSPACE_RO')
        self.assertEqual(result['authorization'],'UNMINTED')
        self.assertEqual(result['context_source_manifest'],'UNCREATED')
        self.assertEqual(result['controller_projection'],
                         'IN_MEMORY_SYNTHETIC_ONLY_NOT_RUNNABLE_REAL_CONTEXT')

    def test_exact_inert_controller_and_child_role_rebind(self):
        runner,child = adapter.project_inert_controller()
        self.assertIn(b'docker-context-20261020-0002',runner)
        self.assertIn(b'docker-context-20261020-0002',child)
        self.assertNotIn(b'docker-context-20261020-0001',runner+child)
        self.assertIn(b'EFFECT_ENABLED = False',runner)
        self.assertIn(b'synthetic_public_body',child)
        self.assertEqual(adapter.sha(runner),adapter.plan()['inert_controller_sha256'])

    def test_original_39_row_dual_view_projection_only(self):
        rows = self.rows()
        result = adapter.structural_manifest_rows(rows)
        self.assertEqual(result['status'],'STRUCTURAL_39_ROW_PROJECTION_ONLY')
        self.assertEqual(len(result['physical_rows']),39)
        self.assertEqual([r['sha256'] for r in result['physical_rows']],
                         [r['sha256'] for r in rows])
        self.assertFalse(result['real_output_validated'])

    def test_missing_extra_reordered_and_bad_digest_refuse(self):
        original = self.rows()
        cases = (original[:-1],original+[original[-1]],
                 [original[1],original[0]]+original[2:],
                 [dict(original[0],sha256='0')]+original[1:])
        for i,rows in enumerate(cases):
            with self.subTest(case=i), self.assertRaisesRegex(
                    adapter.Refused,'STRUCTURAL_39_LOGICAL_ROWS_ONLY'):
                adapter.structural_manifest_rows(rows)

    def test_original_static_pin_drift_refuses(self):
        changed = dict(adapter.PINS)
        changed[adapter.VALIDATOR_REVIEW] = '0'*64
        with mock.patch.object(adapter,'PINS',changed):
            with self.assertRaisesRegex(adapter.Refused,'ORIGINAL_PREIMAGE_DRIFT'):
                adapter.plan()

    def test_period_expiry_refuses_before_output_plan(self):
        with self.assertRaises(ValueError):
            adapter.plan(dt.datetime(2026,10,21,15,0,tzinfo=dt.timezone.utc))

    def test_absence_and_unknown_contract(self):
        result = adapter.plan()
        required = result['terminal_required']
        self.assertEqual(required['os_exit'],required['daemon_exit'])
        self.assertTrue(all(required[key] for key in
                            ('cid_absent','name_absent','writer_closed',
                             'mediator_joined','postclose_readback')))
        self.assertEqual(result['writer_private_release_scope'],
                         'EMPTY_WRITER_SCRATCH_ONLY_NOT_JIT_PRIVATE_ROOT')
        self.assertEqual(result['uncertainty'],
                         'UNKNOWN_PRESERVE_MARKER_OUTPUT_PRIVATE_EVIDENCE_NO_RETRY')

    def test_all_real_entrypoints_refuse(self):
        for entry in (adapter.select_mapper_stage_or_auth,
                      adapter.issue_auth_or_write_policy,
                      adapter.run_docker_or_context,
                      adapter.validate_real_output_or_cleanup):
            with self.subTest(entry=entry.__name__), self.assertRaises(adapter.Refused):
                entry()


if __name__ == '__main__':
    unittest.main()
