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

from t35_external_v1.phase_scoped_v2 import native_seal_smoke_0005 as smoke


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
        bwrap = scratch / 'selected/bwrap'
        argv[0] = str(bwrap)
        smoke.validate_sandbox_argv(scratch, argv, bwrap)
        altered = list(argv)
        bind = altered.index('--ro-bind')
        altered[bind + 1] = '/home/vlad_/protected'
        with self.assertRaises(smoke.Refusal):
            smoke.validate_sandbox_argv(scratch, altered, bwrap)
        for extra in ('--ro-bind-try', '--proc'):
            altered = list(argv)
            altered.insert(4, extra)
            with self.assertRaises(smoke.Refusal):
                smoke.validate_sandbox_argv(scratch, altered, bwrap)
        specs = smoke.copy_specs(scratch)
        self.assertEqual(specs[scratch / 'selected/abi/ld-linux-x86-64.so.2'][1],
                         0o500)
        self.assertEqual(specs[scratch / 'selected/abi/libc.so.6'][1], 0o400)
        with tempfile.TemporaryDirectory(prefix='native-smoke-modes-') as folder:
            modes = {}
            capture_state = {}
            def record(path, raw, mode):
                modes[path.name] = mode
            with mock.patch.object(smoke, 'held_selected', return_value=b'bytes'):
                with mock.patch.object(smoke, 'write_exact', side_effect=record):
                    smoke.capture(Path(folder), capture_state)
            self.assertEqual(modes['ld-linux-x86-64.so.2'], 0o500)
            self.assertEqual(modes['libc.so.6'], 0o400)
            self.assertEqual(modes['libgcc_s.so.1'], 0o400)
            self.assertEqual(len(capture_state['selected_capture_sha256']), 5)
            self.assertEqual(set(capture_state['selected_capture_sha256'].values()),
                             {hashlib.sha256(b'bytes').hexdigest()})
        state = {'status': 'FAIL', 'stage': 'native_smoke',
                 'failure_code': 'native_observation',
                 'children': {'native_smoke': {'launch_attempted': True,
                     'leader_started': True, 'forced_cleanup': True}},
                 'scratch_root': Path('/tmp/lc-u02-05-native-seal-example'),
                 'scratch_cleanup_observed': False,
                 'scratch_retained_unknown': True}
        receipt = smoke.receipt(state)
        self.assertEqual(receipt['expected_selected_leaf_sha256'],
                         {str(path): row[2]
                          for path, row in smoke.plan.SELECTED.items()})
        self.assertIsNone(receipt['selected_capture_sha256'])
        self.assertEqual(receipt['failure_stage'], 'native_smoke')
        self.assertEqual(receipt['claim_ceiling'],
                         'disposable_empty_native_serialization_only')
        self.assertFalse(receipt['escaped_session_absence_proven'])
        self.assertFalse(receipt['lc_u02_05_accepted'])
        self.assertNotIn('fixture-data', str(receipt))
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
            self.assertEqual(row['stdout_sha256'], hashlib.sha256(b'').hexdigest())
            self.assertIsInstance(row['elapsed_milliseconds'], int)
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
        def uncertain(root, bwrap, held, state):
            state['stage'] = 'bwrap_version'
            state['children']['bwrap_version'] = {'launch_attempted': True}
            raise OSError('synthetic launch uncertainty')
        try:
            with mock.patch.object(smoke, 'capture', return_value=Path('/tmp/inert-bwrap')):
                with mock.patch.object(smoke, 'invoke_children', side_effect=uncertain):
                    with self.assertRaises(OSError):
                        smoke.effect(state)
            self.assertTrue(state['scratch_retained_unknown'])
            self.assertFalse(state['scratch_cleanup_observed'])
            self.assertEqual(state['stage'], 'bwrap_version')
            self.assertTrue(state['scratch_root'].is_dir())
        finally:
            if state['scratch_root'] is not None:
                shutil.rmtree(state['scratch_root'])

    def test_copy_mutation_and_replacement_are_detected(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-copy-') as folder:
            root = Path(folder)
            path = root / 'copy'
            raw = b'copy-bytes'
            smoke.write_exact(path, raw, 0o400)
            specs = {path: (len(raw), 0o400, hashlib.sha256(raw).hexdigest())}
            with smoke.held_copies(root, specs) as rows:
                self.assertEqual(smoke.verify_copies(rows)[str(path)],
                                 specs[path][2])
                replacement = root / 'replacement'
                smoke.write_exact(replacement, raw, 0o400)
                os.replace(replacement, path)
                with self.assertRaises(smoke.Refusal):
                    smoke.verify_copies(rows)

    def test_copy_replacement_during_child_is_caught_after_launch(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-launch-') as folder:
            root = Path(folder)
            path = root / 'copy'
            raw = b'copy-bytes'
            smoke.write_exact(path, raw, 0o400)
            specs = {path: (len(raw), 0o400, hashlib.sha256(raw).hexdigest())}
            original = smoke.held_copies
            def replace(argv, *, timeout, observation):
                replacement = root / 'replacement'
                smoke.write_exact(replacement, raw, 0o400)
                os.replace(replacement, path)
                return 0, smoke.EXPECTED_BWRAP_VERSION, b''
            state = {'stage': 'capture', 'children': {}}
            with mock.patch.object(smoke, 'held_copies',
                                   side_effect=lambda root: original(root, specs)):
                with mock.patch.object(smoke, 'run_child', side_effect=replace):
                    with self.assertRaises(smoke.Refusal):
                        smoke.invoke_children(root, path,
                                              mock.Mock(attached=lambda: True),
                                              state)
            self.assertEqual(state['stage'], 'bwrap_version')

    def test_attachment_exception_defaults_to_retained_scratch(self):
        state = {'status': 'FAIL', 'stage': 'preflight', 'failure_code': None,
                 'children': {}, 'scratch_root': None,
                 'scratch_cleanup_observed': False,
                 'scratch_retained_unknown': False}
        try:
            with mock.patch.object(smoke.HeldCanonicalDirectory, 'attached',
                                   side_effect=OSError('synthetic attachment failure')):
                with self.assertRaises(OSError):
                    smoke.effect(state)
            self.assertTrue(state['scratch_retained_unknown'])
            self.assertFalse(state['scratch_cleanup_observed'])
            self.assertTrue(state['scratch_root'].is_dir())
        finally:
            if state['scratch_root'] is not None:
                shutil.rmtree(state['scratch_root'])

    def test_held_no_replace_receipt_and_duplicate_runner(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-receipt-') as folder:
            root = Path(folder)
            destination = root / smoke.RECEIPT_NAME
            calls = []
            def inert(state):
                calls.append(1)
                raise smoke.Refusal('synthetic_refusal')
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with mock.patch.object(smoke, 'effect', side_effect=inert):
                    first = smoke.run_and_publish(destination)
                    self.assertEqual(first['status'], 'FAIL')
                    self.assertEqual(first['failure_code'], 'synthetic_refusal')
                    self.assertTrue(destination.is_file())
                    self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
                    marker_path = root / smoke.ATTEMPT_NAME
                    self.assertTrue(marker_path.is_file())
                    self.assertEqual(first['attempt_marker']['sha256'],
                                     hashlib.sha256(marker_path.read_bytes()).hexdigest())
                    self.assertEqual(first['attempt_marker']['name'],
                                     smoke.ATTEMPT_NAME)
                    with self.assertRaises(smoke.Refusal):
                        smoke.run_and_publish(destination)
            self.assertEqual(calls, [1])

    def test_cooperating_lock_blocks_second_runner(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-lock-') as folder:
            with mock.patch.object(smoke, 'RECEIPT_DIR', Path(folder)):
                with smoke.controller_scope():
                    with self.assertRaises(smoke.Refusal):
                        with smoke.controller_scope():
                            pass

    def test_aggregate_watchdog_publishes_sanitized_failure(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-timeout-') as folder:
            root = Path(folder)
            destination = root / smoke.RECEIPT_NAME
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with mock.patch.object(smoke, 'AGGREGATE_CAP_SECONDS', 0.05):
                    with mock.patch.object(smoke, 'effect',
                                           side_effect=lambda state: time.sleep(0.2)):
                        result = smoke.run_and_publish(destination)
            self.assertEqual(result['status'], 'FAIL')
            self.assertEqual(result['failure_code'], 'WATCHDOG_EXHAUSTED')
            self.assertEqual(result['failure_stage'], 'preflight')
            self.assertTrue(destination.exists())
            self.assertFalse(result['raw_diagnostics_published'])

    def test_atomic_publisher_handles_short_writes_before_link(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-atomic-') as folder:
            root = Path(folder)
            destination = root / smoke.RECEIPT_NAME
            real_write = os.write
            def short(fd, raw):
                return real_write(fd, raw[:3])
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with smoke.HeldCanonicalDirectory(str(root)) as held:
                    with mock.patch.object(smoke.os, 'write', side_effect=short):
                        smoke.publish_no_replace({'status': 'FAIL'}, destination, held)
            self.assertEqual(smoke.json.loads(destination.read_text()),
                             {'status': 'FAIL'})
            self.assertEqual(list(root.glob('.*.tmp-*')), [])

    def test_atomic_publisher_write_and_fsync_errors_leave_no_final(self):
        for failure in ('write', 'fsync'):
            with self.subTest(failure=failure):
                with tempfile.TemporaryDirectory(
                        prefix='native-smoke-atomic-') as folder:
                    root = Path(folder)
                    destination = root / smoke.RECEIPT_NAME
                    real_write = os.write
                    calls = [0]
                    def break_write(fd, raw):
                        calls[0] += 1
                        if calls[0] == 1:
                            return real_write(fd, raw[:4])
                        raise OSError('synthetic write failure')
                    with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                        with smoke.HeldCanonicalDirectory(str(root)) as held:
                            if failure == 'write':
                                patcher = mock.patch.object(
                                    smoke.os, 'write', side_effect=break_write)
                            else:
                                patcher = mock.patch.object(
                                    smoke.os, 'fsync',
                                    side_effect=OSError('synthetic fsync failure'))
                            with patcher:
                                with self.assertRaises(OSError):
                                    smoke.publish_no_replace(
                                        {'status': 'FAIL'}, destination, held)
                    self.assertFalse(destination.exists())
                    self.assertEqual(len(list(root.glob('.*.tmp-*'))), 1)

    def test_atomic_publisher_readback_failure_leaves_no_final(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-atomic-') as folder:
            root = Path(folder)
            destination = root / smoke.RECEIPT_NAME
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with smoke.HeldCanonicalDirectory(str(root)) as held:
                    with mock.patch.object(
                            smoke, '_readback_leaf',
                            side_effect=smoke.Refusal('synthetic_readback')):
                        with self.assertRaises(smoke.Refusal):
                            smoke.publish_no_replace(
                                {'status': 'FAIL'}, destination, held)
            self.assertFalse(destination.exists())
            self.assertEqual(len(list(root.glob('.*.tmp-*'))), 1)

    def test_atomic_publisher_real_byte_mismatch_leaves_no_final(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-atomic-') as folder:
            root = Path(folder)
            destination = root / smoke.RECEIPT_NAME
            real_write = os.write
            def corrupt(fd, raw):
                return real_write(fd, b'X' + raw[1:])
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with smoke.HeldCanonicalDirectory(str(root)) as held:
                    with mock.patch.object(smoke.os, 'write', side_effect=corrupt):
                        with self.assertRaises(smoke.Refusal):
                            smoke.publish_no_replace(
                                {'status': 'FAIL'}, destination, held)
            self.assertFalse(destination.exists())
            self.assertEqual(len(list(root.glob('.*.tmp-*'))), 1)

    def test_atomic_publisher_collision_never_replaces_final(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-atomic-') as folder:
            root = Path(folder)
            destination = root / smoke.RECEIPT_NAME
            destination.write_bytes(b'existing')
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with smoke.HeldCanonicalDirectory(str(root)) as held:
                    with self.assertRaises(FileExistsError):
                        smoke.publish_no_replace(
                            {'status': 'FAIL'}, destination, held)
            self.assertEqual(destination.read_bytes(), b'existing')
            self.assertEqual(len(list(root.glob('.*.tmp-*'))), 1)

    def test_atomic_publisher_postlink_failure_preserves_final_and_temp(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-atomic-') as folder:
            root = Path(folder)
            destination = root / smoke.RECEIPT_NAME
            actual = smoke._readback_leaf
            calls = [0]
            def fail_final(*args):
                calls[0] += 1
                if calls[0] == 2:
                    raise smoke.Refusal('synthetic_final_readback')
                return actual(*args)
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with smoke.HeldCanonicalDirectory(str(root)) as held:
                    with mock.patch.object(smoke, '_readback_leaf',
                                           side_effect=fail_final):
                        with self.assertRaises(smoke.Refusal):
                            smoke.publish_no_replace(
                                {'status': 'FAIL'}, destination, held)
                    first = destination.read_bytes()
                    with self.assertRaises(FileExistsError):
                        smoke.publish_no_replace(
                            {'status': 'PASS'}, destination, held)
            self.assertEqual(destination.read_bytes(), first)
            self.assertEqual(smoke.json.loads(first), {'status': 'FAIL'})
            self.assertEqual(len(list(root.glob('.*.tmp-*'))), 2)

    def test_atomic_publisher_postlink_fsync_failure_keeps_full_final(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-atomic-') as folder:
            root = Path(folder)
            destination = root / smoke.RECEIPT_NAME
            real_fsync = os.fsync
            calls = [0]
            def fail_directory(fd):
                calls[0] += 1
                if calls[0] == 2:
                    raise OSError('synthetic directory fsync failure')
                return real_fsync(fd)
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with smoke.HeldCanonicalDirectory(str(root)) as held:
                    with mock.patch.object(smoke.os, 'fsync',
                                           side_effect=fail_directory):
                        with self.assertRaises(OSError):
                            smoke.publish_no_replace(
                                {'status': 'FAIL'}, destination, held)
            self.assertEqual(smoke.json.loads(destination.read_text()),
                             {'status': 'FAIL'})
            self.assertEqual(len(list(root.glob('.*.tmp-*'))), 1)

    def test_restrictive_umask_still_yields_0600_marker_and_result(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-umask-') as folder:
            root = Path(folder)
            destination = root / smoke.RECEIPT_NAME
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with smoke.HeldCanonicalDirectory(str(root)) as held:
                    old = os.umask(0o777)
                    try:
                        marker, raw, identity = smoke.publish_attempt_marker(
                            held, smoke.code_bindings())
                        smoke.publish_no_replace(
                            {'status': 'FAIL', 'attempt_marker': marker},
                            destination, held)
                    finally:
                        os.umask(old)
            self.assertEqual((root / smoke.ATTEMPT_NAME).stat().st_mode & 0o777,
                             0o600)
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), marker['sha256'])

    def test_existing_marker_refuses_without_effect(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-marker-') as folder:
            root = Path(folder)
            (root / smoke.ATTEMPT_NAME).write_bytes(b'partial prior marker')
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with mock.patch.object(smoke, 'effect') as effect:
                    with self.assertRaises(smoke.Refusal):
                        smoke.run_and_publish(root / smoke.RECEIPT_NAME)
                    effect.assert_not_called()
            self.assertFalse((root / smoke.RECEIPT_NAME).exists())

    def test_retained_temp_of_unexpected_type_refuses_before_marker(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-temp-') as folder:
            root = Path(folder)
            (root / (smoke.TEMP_PREFIX + 'retained')).mkdir()
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with mock.patch.object(smoke, 'effect') as effect:
                    with self.assertRaises(smoke.Refusal):
                        smoke.run_and_publish(root / smoke.RECEIPT_NAME)
                    effect.assert_not_called()
            self.assertFalse((root / smoke.ATTEMPT_NAME).exists())

    def test_marker_creation_failure_never_starts_effect(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-marker-') as folder:
            root = Path(folder)
            real_open = os.open
            def fail_marker(path, *args, **kwargs):
                if path == smoke.ATTEMPT_NAME:
                    raise OSError('synthetic marker creation')
                return real_open(path, *args, **kwargs)
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with mock.patch.object(smoke, 'effect') as effect:
                    with mock.patch.object(smoke.os, 'open',
                                           side_effect=fail_marker):
                        with self.assertRaises(OSError):
                            smoke.run_and_publish(root / smoke.RECEIPT_NAME)
                    effect.assert_not_called()
            self.assertFalse((root / smoke.ATTEMPT_NAME).exists())
            self.assertFalse((root / smoke.RECEIPT_NAME).exists())

    def test_marker_write_or_fsync_failure_blocks_replay_without_effect(self):
        for failure in ('write', 'fsync'):
            with self.subTest(failure=failure):
                with tempfile.TemporaryDirectory(
                        prefix='native-smoke-marker-') as folder:
                    root = Path(folder)
                    real_write, real_fsync = os.write, os.fsync
                    calls = [0]
                    def fail_write(fd, raw):
                        calls[0] += 1
                        if calls[0] == 1:
                            return real_write(fd, raw[:3])
                        raise OSError('synthetic marker write')
                    def fail_fsync(fd):
                        raise OSError('synthetic marker fsync')
                    with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                        with mock.patch.object(smoke, 'effect') as effect:
                            patcher = (
                                mock.patch.object(smoke.os, 'write',
                                                  side_effect=fail_write)
                                if failure == 'write' else
                                mock.patch.object(smoke.os, 'fsync',
                                                  side_effect=fail_fsync))
                            with patcher:
                                with self.assertRaises(OSError):
                                    smoke.run_and_publish(
                                        root / smoke.RECEIPT_NAME)
                            effect.assert_not_called()
                            with self.assertRaises(smoke.Refusal):
                                smoke.run_and_publish(
                                    root / smoke.RECEIPT_NAME)
                            effect.assert_not_called()
                    self.assertTrue((root / smoke.ATTEMPT_NAME).exists())
                    self.assertFalse((root / smoke.RECEIPT_NAME).exists())

    def test_marker_readback_failure_never_starts_effect(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-marker-') as folder:
            root = Path(folder)
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with mock.patch.object(smoke, 'effect') as effect:
                    with mock.patch.object(
                            smoke, '_readback_leaf',
                            side_effect=smoke.Refusal('synthetic_marker_readback')):
                        with self.assertRaises(smoke.Refusal):
                            smoke.run_and_publish(root / smoke.RECEIPT_NAME)
                    effect.assert_not_called()
                    with self.assertRaises(smoke.Refusal):
                        smoke.run_and_publish(root / smoke.RECEIPT_NAME)
                    effect.assert_not_called()
            self.assertTrue((root / smoke.ATTEMPT_NAME).exists())
            self.assertFalse((root / smoke.RECEIPT_NAME).exists())

    def test_crash_after_marker_before_receipt_cannot_repeat_effect(self):
        with tempfile.TemporaryDirectory(prefix='native-smoke-crash-') as folder:
            root = Path(folder)
            calls = []
            def synthetic_effect(state):
                calls.append(1)
                raise smoke.Refusal('synthetic_effect_failure')
            with mock.patch.object(smoke, 'RECEIPT_DIR', root):
                with mock.patch.object(smoke, 'effect',
                                       side_effect=synthetic_effect):
                    with mock.patch.object(
                            smoke, 'publish_no_replace',
                            side_effect=OSError('synthetic pre-receipt crash')):
                        with self.assertRaises(OSError):
                            smoke.run_and_publish(root / smoke.RECEIPT_NAME)
                    self.assertFalse((root / smoke.RECEIPT_NAME).exists())
                    marker = smoke.json.loads(
                        (root / smoke.ATTEMPT_NAME).read_text())
                    self.assertEqual(marker['result_name'], smoke.RECEIPT_NAME)
                    self.assertEqual(marker['controller_plan_test_sha256'],
                                     smoke.code_bindings())
                    with self.assertRaises(smoke.Refusal):
                        smoke.run_and_publish(root / smoke.RECEIPT_NAME)
            self.assertEqual(calls, [1])

    def test_closed_pass_receipt_requires_actual_child_bindings(self):
        root = Path('/tmp/lc-u02-05-native-seal-absent-synthetic')
        self.assertFalse(root.exists())
        bwrap = root / 'selected/bwrap'
        version = [str(bwrap), '--version']
        native = smoke.expected_sandbox_argv(root, bwrap)
        def observed(argv, timeout, stdout):
            return {
                'launch_attempted': True, 'leader_started': True,
                'reaped_observed': True, 'group_absent_observed': True,
                'forced_cleanup': False, 'forced_timeout': False,
                'forced_output_limit': False, 'timeout_seconds': timeout,
                'exit_code': 0, 'elapsed_milliseconds': 10,
                'stdout_bytes': len(stdout), 'stderr_bytes': 0,
                'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
                'stderr_sha256': hashlib.sha256(b'').hexdigest(),
                'argv_count': len(argv),
                'argv_sha256': hashlib.sha256(
                    smoke.json.dumps(argv, separators=(',', ':')).encode()
                ).hexdigest(),
            }
        state = {
            'status': 'PASS', 'stage': 'complete', 'failure_code': None,
            'scratch_root': root, 'scratch_cleanup_observed': True,
            'scratch_retained_unknown': False, 'version_argv': version,
            'native_argv': native,
            'copy_sha256': {str(path.relative_to(root)): row[2]
                            for path, row in smoke.copy_specs(root).items()},
            'selected_capture_sha256': {
                str(path): row[2] for path, row in smoke.plan.SELECTED.items()},
            'children': {
                'bwrap_version': observed(
                    version, 5, smoke.EXPECTED_BWRAP_VERSION),
                'native_smoke': observed(
                    native, 15, smoke.plan.EXPECTED_STDOUT),
            },
        }
        bindings = smoke.code_bindings()
        marker_raw = smoke.attempt_bytes(bindings)
        state['code_bindings'] = bindings
        state['attempt_marker'] = {
            'name': smoke.ATTEMPT_NAME,
            'sha256': hashlib.sha256(marker_raw).hexdigest(),
            'size_bytes': len(marker_raw),
        }
        smoke.validate_pass_state(state)
        result = smoke.receipt(state)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['native_argv_actual'], native)
        self.assertEqual(result['child_observations']['native_smoke']['stdout_bytes'],
                         32)
        state['children']['native_smoke']['stdout_sha256'] = '0' * 64
        with self.assertRaises(smoke.Refusal):
            smoke.validate_pass_state(state)


if __name__ == '__main__':
    unittest.main()

