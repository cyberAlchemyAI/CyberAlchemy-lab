"""Pure observed child and allowlisted partial-output tests; no bwrap runs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1.path_contract import ContractError
from t35_external_v1.phase_scoped_v2 import prefix_pair_observed_0001 as observed


def vector():
    captured = {f'fixture/input-{i:04d}.json': str(i).encode() for i in range(1702)}
    captured[observed.source.HISTORICAL_SOURCE_PACKAGE['path']] = b'{}\n'
    rows = {name: {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}
            for name, raw in captured.items()}
    return observed.FrozenVector.from_selected(rows, captured,
        b'{"not_before":"2026-10-19T00:00:00+00:00","expires_at":"2026-10-21T00:00:00+00:00"}\n',
        b'role\n')


class ObservedBoundaryTests(unittest.TestCase):
    def test_observed_child_success_nonzero_timeout_and_output_limit(self):
        commands = [
            ([sys.executable, '-c', 'print("ok")'], 0, b'ok\n'),
            ([sys.executable, '-c', 'raise SystemExit(7)'], 7, b''),
            ([sys.executable, '-c', 'import time;time.sleep(3)'], 124, b''),
            ([sys.executable, '-c', 'print("x"*200000)'], 125, b''),
        ]
        for argv, expected_rc, expected_prefix in commands:
            state = observed.DiagnosticState()
            rc, stdout, stderr = observed._run_observed(argv, state, 'source', timeout=1)
            self.assertEqual(rc, expected_rc)
            self.assertTrue(stdout.startswith(expected_prefix))
            self.assertEqual(stderr, b'')
            self.assertLessEqual(len(stdout), 128*1024)
            record = state.process_observations['source']
            self.assertGreater(record['pid'], 0)
            self.assertEqual(record['pgid'], record['pid'])
            self.assertTrue(record['reaped_observed'])
            self.assertTrue(record['process_group_absent_observed'])
            self.assertEqual(record['forced_timeout'], rc == 124)
            self.assertEqual(record['forced_output_limit'], rc == 125)
            self.assertGreaterEqual(record['elapsed_milliseconds'], 0)
            published = observed._safe_process_observations(
                state.process_observations)['source']
            self.assertNotIn('pid', published)
            self.assertNotIn('pgid', published)
            self.assertTrue(published['pid_recorded'])
            self.assertTrue(published['pgid_matches_pid'])
            self.assertEqual(published['elapsed_milliseconds'],
                             record['elapsed_milliseconds'])
            self.assertGreaterEqual(published['group_wait_milliseconds'], 0)

    def test_delayed_group_absence_is_observed_with_bounded_wait(self):
        with patch.object(observed, '_group_absent', side_effect=[False, False, True]) as probe:
            absent, elapsed = observed._wait_group_absent(123)
        self.assertTrue(absent)
        self.assertEqual(probe.call_count, 3)
        self.assertGreaterEqual(elapsed, 0)
        self.assertLess(elapsed, 2000)
        with patch.object(observed, '_group_absent', return_value=False):
            absent, elapsed = observed._wait_group_absent(123)
        self.assertFalse(absent)
        self.assertGreaterEqual(elapsed, 2000)

    def test_natural_exit_124_and_125_are_not_forced_codes(self):
        for natural_code in (124, 125):
            state = observed.DiagnosticState()
            state.step('source_child_postreturn')
            rc, stdout, stderr = observed._run_observed(
                [sys.executable, '-c', f'raise SystemExit({natural_code})'],
                state, 'source', timeout=1)
            self.assertEqual(rc, natural_code)
            state.child('source', rc, stdout, stderr)
            self.assertFalse(state.process_observations['source']['forced_timeout'])
            self.assertFalse(state.process_observations['source']['forced_output_limit'])
            failure = observed.sanitized_failure(state, ContractError('private'))
            self.assertEqual(failure['failure_code'], 'CHILD_NONZERO')

    def test_selector_setup_failure_reaps_spawned_child(self):
        state = observed.DiagnosticState()
        with patch.object(observed.selectors, 'DefaultSelector', side_effect=RuntimeError('setup')):
            with self.assertRaises(RuntimeError):
                observed._run_observed(
                    [sys.executable, '-c', 'import time;time.sleep(3)'],
                    state, 'source', timeout=1)
        self.assertEqual(state.child_launch_attempted, ['source'])
        self.assertTrue(state.process_observations['source']['reaped_observed'])
        self.assertTrue(state.process_observations['source']['process_group_absent_observed'])

    def test_stream_map_setup_failure_reaps_spawned_child(self):
        real_popen = observed.subprocess.Popen
        class BadHashStream:
            def __init__(self, raw):
                self.raw = raw
            def __hash__(self):
                raise RuntimeError('stream map setup')
            def close(self):
                self.raw.close()
        class BrokenStreams:
            def __init__(self, child):
                self.child = child
                self.pid = child.pid
                self.stdout = BadHashStream(child.stdout)
                self.stderr = child.stderr
            def poll(self):
                return self.child.poll()
            def wait(self, **kwargs):
                return self.child.wait(**kwargs)
        def spawn(*args, **kwargs):
            return BrokenStreams(real_popen(*args, **kwargs))
        state = observed.DiagnosticState()
        with patch.object(observed.subprocess, 'Popen', side_effect=spawn):
            with self.assertRaises(RuntimeError):
                observed._run_observed(
                    [sys.executable, '-c', 'import time;time.sleep(3)'],
                    state, 'source', timeout=1)
        self.assertEqual(state.child_launch_attempted, ['source'])
        self.assertTrue(state.process_observations['source']['reaped_observed'])
        self.assertTrue(state.process_observations['source']['process_group_absent_observed'])

    def test_popen_failure_records_incomplete_launch_and_stops_pair(self):
        state = observed.DiagnosticState()
        with patch.object(observed.subprocess, 'Popen', side_effect=OSError('private')):
            with self.assertRaises(OSError):
                observed._run_observed(['/usr/bin/false'], state, 'source', timeout=1)
        self.assertEqual(state.child_launch_attempted, ['source'])
        self.assertEqual(state.process_observations, {})
        with tempfile.TemporaryDirectory() as scratch:
            state.scratch_root = Path(scratch)
        state.step('source_child_running')
        failure = observed.sanitized_failure(state, OSError('private'))
        selected = vector()
        failure['input_vector_sha256'] = selected.sha256
        with patch.object(observed, 'diagnose', side_effect=[failure]) as invoked:
            result = observed.pair(selected)
        self.assertEqual(invoked.call_count, 1)
        self.assertEqual(result['attempts'][1]['status'], 'SKIPPED-unclosed-prior-attempt')
        self.assertNotIn('private', json.dumps(result))

    def test_partial_package_only_names_selected_members_and_counts_unknown(self):
        with tempfile.TemporaryDirectory() as scratch:
            family = Path(scratch)/'family'
            package = family/'source/packages'
            (package/'0001/artifacts').mkdir(parents=True)
            (family/'source/base.py').write_bytes(b'staged')
            pre = observed.source._tree_files(family)
            (package/'0001/artifacts/00').write_bytes(b'partial')
            (package/'0001/unknown').write_bytes(b'unselected')
            (package/'unexpected-dir').mkdir()
            row = observed._partial_package(package, {'artifacts/00'}, family, pre)
            self.assertEqual(row['present_expected_package_leaf_names'],
                             ['0001/artifacts/00'])
            self.assertEqual(row['unexpected_package_leaf_count'], 1)
            self.assertEqual(row['unexpected_package_directory_count'], 1)
            self.assertTrue(row['preexisting_family_leaves_unchanged'])
            self.assertNotIn('unknown', json.dumps(row))
            with patch.object(observed.source, '_historical_package_names',
                              return_value={'artifacts/00'}):
                with self.assertRaises(ContractError):
                    observed._safe_partial_package({**row,
                        'present_expected_package_leaf_names':['0001/unknown']}, vector())
                self.assertEqual(observed._safe_partial_package(row, vector()), row)
            (family/'source/base.py').write_bytes(b'changed')
            changed = observed._partial_package(package, {'artifacts/00'}, family, pre)
            self.assertFalse(changed['preexisting_family_leaves_unchanged'])

    def test_partial_package_symlink_and_hardlink_refuse(self):
        with tempfile.TemporaryDirectory() as scratch:
            family = Path(scratch)/'family'
            package = family/'source/packages'
            (package/'0001').mkdir(parents=True)
            pre = observed.source._tree_files(family)
            target = package/'0001/manifest.json'
            target.write_bytes(b'partial')
            alias = package/'0001/alias'
            alias.symlink_to(target.name)
            with self.assertRaises(ContractError):
                observed._partial_package(package, set(), family, pre)
            alias.unlink()
            import os
            os.link(target, alias)
            with self.assertRaises(ContractError):
                observed._partial_package(package, set(), family, pre)

    def test_safe_projection_refuses_unknown_process_or_inventory_fields(self):
        record = {'pid': 100, 'pgid': 100, 'elapsed_milliseconds': 180000,
                  'reaped_observed': True, 'process_group_absent_observed': True,
                  'group_wait_milliseconds': 500,
                  'timeout_cap_seconds': 180, 'forced_timeout': True,
                  'forced_output_limit': False}
        published = observed._safe_process_observations({'source': record})['source']
        self.assertNotIn('pid', published)
        self.assertNotIn('pgid', published)
        self.assertTrue(published['reaped_observed'])
        with self.assertRaises(ContractError):
            observed._safe_process_observations({'source': {**record,
                'argv': '/private/path'}})
        with self.assertRaises(ContractError):
            observed._safe_process_observations({'source': {**record,
                'process_group_absent_observed': 'yes'}})
        self.assertEqual(observed._safe_partial_package({'inventory_refused': True}, vector()),
                         {'inventory_refused': True})

    def test_unclosed_process_group_prevents_second_attempt(self):
        selected = vector()
        record = {'pid': 100, 'pgid': 100, 'elapsed_milliseconds': 180000,
                  'reaped_observed': True, 'process_group_absent_observed': False,
                  'group_wait_milliseconds': 2000,
                  'timeout_cap_seconds': 180, 'forced_timeout': True,
                  'forced_output_limit': False}
        child = {'return_code': 124, 'stdout_bytes': 0,
                 'stdout_sha256': observed.source._sha(b''),
                 'stderr_bytes': 0, 'stderr_sha256': observed.source._sha(b'')}
        failure = {
            'status': 'FAIL-disposable-prefix-diagnostic',
            'input_vector_sha256': selected.sha256,
            'failure_stage': 'source_child_postreturn',
            'failure_code': 'CONTRACT_REFUSAL',
            'child_results': {'source': child},
            'child_launch_attempted': ['source'],
            'process_observations': {'source': record},
            'partial_package': {'inventory_refused': True},
            'selection_sha256': {'plan_leaf': 'a'*64},
            'scratch_root_sha256': 'b'*64,
            'scratch_cleanup_observed': True,
            'raw_stdout_stderr_or_exception_published': False,
            'actual_host_qualification': False, 'activation_allowed': False,
        }
        with patch.object(observed, 'diagnose', side_effect=[failure]) as invoked:
            result = observed.pair(selected)
        self.assertEqual(invoked.call_count, 1)
        self.assertEqual(result['attempts'][0]['status'], 'FAIL-disposable-prefix-diagnostic')
        self.assertEqual(result['attempts'][1]['status'], 'SKIPPED-unclosed-prior-attempt')
        self.assertIsNone(result['derived_selection_equal_when_both_observed'])
        self.assertNotIn('"pid":', json.dumps(result))
        self.assertNotIn('"pgid":', json.dumps(result))

        failure['process_observations']['source']['process_group_absent_observed'] = True
        failure['partial_package'] = {
            'inventory_refused': False,
            'present_expected_package_leaf_names': [],
            'unexpected_package_leaf_count': 1,
            'unexpected_package_directory_count': 0,
            'preexisting_family_leaves_unchanged': True,
            'package_leaf_count': 1,
        }
        with patch.object(observed.source, '_historical_package_names', return_value=set()), \
             patch.object(observed, 'diagnose', side_effect=[failure]) as invoked:
            result = observed.pair(selected)
        self.assertEqual(invoked.call_count, 1)
        self.assertEqual(result['attempts'][1]['status'], 'SKIPPED-unclosed-prior-attempt')


if __name__ == '__main__':
    unittest.main()
