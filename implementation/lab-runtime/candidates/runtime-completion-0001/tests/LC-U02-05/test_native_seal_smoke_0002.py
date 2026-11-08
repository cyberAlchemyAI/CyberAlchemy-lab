"""Synthetic-only checks; never execute Bubblewrap or the selected native ELF."""
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest
from unittest import mock

from t35_external_v1.phase_scoped_v2 import native_seal_smoke_0002 as smoke


class NativeSmokeController(unittest.TestCase):
    def test_exact_capture_and_refuse_alias(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-test-') as folder:
            root = Path(folder)
            leaf = root / 'leaf'
            raw = b'fixture-data'
            leaf.write_bytes(raw)
            leaf.chmod(0o400)
            expected = (len(raw), 0o400, hashlib.sha256(raw).hexdigest())
            self.assertEqual(smoke.held_selected(leaf, expected), raw)
            with self.assertRaises(smoke.Refusal):
                smoke.held_selected(leaf, (len(raw), 0o400, '0' * 64))
            (root / 'alias').symlink_to(leaf)
            with self.assertRaises(OSError):
                smoke.held_selected(root / 'alias', expected)
            smoke.write_exact(root / 'copy', raw, 0o400)
            self.assertEqual((root / 'copy').read_bytes(), raw)
            with self.assertRaises(FileExistsError):
                smoke.write_exact(root / 'copy', raw, 0o400)

    def test_exact_plan_and_sanitized_receipt(self):
        self.assertEqual(len(smoke.plan.SYNTHETIC_INPUT), 32)
        self.assertEqual(smoke.plan.SYNTHETIC_INPUT,
                         b'{"semantic":[],"governance":[]}\n')
        scratch = Path('/tmp/lc-u02-05-native-seal-synthetic')
        argv = smoke.plan.render_argv(scratch)
        smoke.validate_sandbox_argv(scratch, argv)
        altered = list(argv)
        bind = altered.index('--ro-bind')
        altered[bind + 1] = '/home/vlad_/protected'
        with self.assertRaises(smoke.Refusal):
            smoke.validate_sandbox_argv(scratch, altered)
        state = {'status': 'FAIL', 'stage': 'native_smoke',
                 'failure_code': 'native_observation',
                 'children': {'native_smoke': {'launch_attempted': True,
                     'leader_started': True, 'forced_cleanup': True}},
                 'scratch_root': Path('/tmp/lc-u02-05-native-seal-example'),
                 'scratch_cleanup_observed': False,
                 'scratch_retained_unknown': True}
        receipt = smoke.receipt(state)
        self.assertEqual(receipt['failure_stage'], 'native_smoke')
        self.assertEqual(receipt['claim_ceiling'],
                         'disposable_empty_native_serialization_only')
        self.assertFalse(receipt['escaped_session_absence_proven'])
        self.assertFalse(receipt['lc_u02_05_accepted'])
        self.assertNotIn('stdout', str(receipt))
        with mock.patch.object(smoke, 'run_and_publish', return_value={'status': 'FAIL'}):
            self.assertEqual(smoke.main(), 1)

    def test_closed_fd_sleeping_leader_keeps_original_deadline(self):
        code = 'import os,time;os.close(1);os.close(2);time.sleep(3)'
        row = {}
        start = time.monotonic()
        rc, out, err = smoke.run_child([sys.executable, '-c', code],
                                        timeout=1, observation=row)
        self.assertLess(time.monotonic() - start, 2.8)
        self.assertNotEqual(rc, 0)
        self.assertEqual((out, err), (b'', b''))
        self.assertTrue(row['forced_timeout'])
        self.assertTrue(row['forced_cleanup'])
        self.assertTrue(row['reaped_observed'])
        self.assertTrue(row['group_absent_observed'])

    def test_exited_leader_with_surviving_original_group_descendant(self):
        code = ('import os,time;pid=os.fork();'
                'os._exit(0) if pid else (os.close(1),os.close(2),time.sleep(5))')
        row = {}
        rc, out, err = smoke.run_child([sys.executable, '-c', code],
                                        timeout=2, observation=row)
        self.assertEqual(rc, 0)
        self.assertEqual((out, err), (b'', b''))
        self.assertTrue(row['forced_cleanup'])
        self.assertTrue(row['reaped_observed'])
        self.assertTrue(row['group_absent_observed'])

    def test_permanent_signal_failure_retains_unreaped_identity(self):
        code = 'import os,time;os.close(1);os.close(2);time.sleep(30)'
        row = {}
        original = smoke.signal_held_group
        try:
            with mock.patch.object(smoke, 'signal_held_group',
                                   side_effect=PermissionError):
                with self.assertRaises(PermissionError):
                    smoke.run_child([sys.executable, '-c', code],
                                    timeout=1, observation=row)
            self.assertTrue(row['forced_cleanup'])
            self.assertFalse(row['reaped_observed'])
            self.assertFalse(row['group_absent_observed'])
            self.assertFalse(smoke.scratch_closed(
                {'children': {'synthetic': row}}))
        finally:
            for pid, process in tuple(smoke._UNCLOSED_CHILDREN.items()):
                try:
                    original(pid)
                    process.wait(timeout=3)
                finally:
                    smoke._UNCLOSED_CHILDREN.pop(pid, None)

    def test_one_shot_group_scan_failure_forces_refusal(self):
        code = 'import os,time;os.close(1);os.close(2);time.sleep(0.1)'
        row = {}
        real = smoke.live_group_members
        seen = {'once': False}
        def once(pid):
            if not seen['once']:
                seen['once'] = True
                raise OSError('synthetic scan failure')
            return real(pid)
        with mock.patch.object(smoke, 'live_group_members', side_effect=once):
            with self.assertRaises(OSError):
                smoke.run_child([sys.executable, '-c', code],
                                timeout=2, observation=row)
        self.assertTrue(row['reaped_observed'])
        self.assertTrue(row['group_absent_observed'])
        self.assertTrue(row['forced_cleanup'])

    def test_output_ceiling_forces_group_cleanup(self):
        row = {}
        rc, out, err = smoke.run_child(
            [sys.executable, '-c', "import os,time;os.write(1,b'x'*257);time.sleep(2)"],
            timeout=3, observation=row)
        self.assertNotEqual(rc, 0)
        self.assertLessEqual(len(out), 256)
        self.assertEqual(err, b'')
        self.assertTrue(row['forced_output_limit'])
        self.assertTrue(row['forced_cleanup'])

    def test_unknown_child_retains_owned_scratch(self):
        state = {'status': 'FAIL', 'stage': 'preflight', 'failure_code': None,
                 'children': {}, 'scratch_root': None,
                 'scratch_cleanup_observed': False,
                 'scratch_retained_unknown': False}
        def uncertain(argv, *, timeout, observation):
            observation['launch_attempted'] = True
            raise OSError('synthetic launch uncertainty')
        try:
            with mock.patch.object(smoke, 'capture', return_value=Path('/tmp/inert-bwrap')):
                with mock.patch.object(smoke, 'run_child', side_effect=uncertain):
                    with self.assertRaises(OSError):
                        smoke.effect(state)
            self.assertTrue(state['scratch_retained_unknown'])
            self.assertFalse(state['scratch_cleanup_observed'])
            self.assertEqual(state['stage'], 'bwrap_version')
            self.assertTrue(state['scratch_root'].is_dir())
        finally:
            if state['scratch_root'] is not None:
                shutil.rmtree(state['scratch_root'])


if __name__ == '__main__':
    unittest.main()

