"""Synthetic controller checks; no Bubblewrap or selected native execution."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import secrets
import sys
import tempfile
import time
import unittest
from unittest import mock
from contextlib import contextmanager

from t35_external_v1.phase_scoped_v2 import historical_mapper_replay_effect_0001 as effect
from t35_external_v1.held_paths import HeldCanonicalDirectory


class HistoricalReplayEffect(unittest.TestCase):
    def test_code_bindings_and_read_only_selection(self):
        bindings = effect.code_bindings()
        self.assertEqual(set(bindings),
                         {'controller', 'plan', 'custody', 'held_paths', 'test'})
        rows = effect.package_rows()
        self.assertEqual(len(rows), 55)
        self.assertEqual(sum(size for size, _ in rows.values()), 781575)
        self.assertEqual(rows['native-output.json'],
                         (effect.plan.EXPECTED_STDOUT_BYTES,
                          effect.plan.EXPECTED_STDOUT_SHA256))

    def test_two_replays_use_one_exact_argv_and_refuse_mismatch(self):
        root = Path('/tmp/lc-u02-05-historical-mapper-replay-synthetic')
        argv = list(effect.plan.replay_argv(root))
        self.assertEqual(len(argv), 37)
        self.assertEqual(argv.count('--ro-bind'), 5)
        effect.plan.validate_replay_argv(root, argv)
        altered = list(argv)
        altered[-1] = '/protected/request.json'
        with self.assertRaises(effect.plan.ContractError):
            effect.plan.validate_replay_argv(root, altered)

    def test_synthetic_child_output_ceiling_and_closed_fd_timeout(self):
        row = {}
        rc, out, err = effect.run_child(
            [sys.executable, '-c',
             'import os,time;os.write(1,b"x"*300);time.sleep(3)'],
            timeout=2, stdout_cap=256, observation=row)
        self.assertNotEqual(rc, 0)
        self.assertLessEqual(len(out), 256)
        self.assertEqual(err, b'')
        self.assertTrue(row['forced_output_limit'])
        self.assertTrue(row['forced_cleanup'])
        self.assertTrue(row['reaped_observed'])
        self.assertTrue(row['group_absent_observed'])
        row = {}
        started = time.monotonic()
        effect.run_child([sys.executable, '-c',
                          'import os,time;os.close(1);os.close(2);time.sleep(3)'],
                         timeout=1, stdout_cap=256, observation=row)
        self.assertLess(time.monotonic() - started, 2.8)
        self.assertTrue(row['forced_timeout'])
        self.assertTrue(row['forced_cleanup'])

    def test_exited_leader_with_live_group_member_forces_cleanup(self):
        row = {}
        rc, out, err = effect.run_child(
            [sys.executable, '-c',
             'import os,time;p=os.fork();os._exit(0) if p else '
             '(os.close(1),os.close(2),time.sleep(5))'],
            timeout=2, stdout_cap=256, observation=row)
        self.assertEqual((rc, out, err), (0, b'', b''))
        self.assertTrue(row['forced_cleanup'])
        self.assertTrue(row['reaped_observed'])
        self.assertTrue(row['group_absent_observed'])

    def test_attempt_no_replace_and_retained_temp_refusal(self):
        with tempfile.TemporaryDirectory(prefix='replay-publication-test-') as tmp:
            with HeldCanonicalDirectory(tmp) as held:
                root = Path('/tmp/lc-u02-05-historical-mapper-replay-' +
                            secrets.token_hex(16))
                raw = effect.attempt_bytes({'controller': '0' * 64},
                                           {'package_inventory_sha256': 'a' * 64},
                                           root)
                self.assertNotIn(b'private', raw)
                self.assertEqual(json.loads(raw)['native_argv_sha256'],
                                 effect.sha(json.dumps(
                                     list(effect.plan.replay_argv(root)),
                                     separators=(',', ':')).encode()))
                identity = effect._write_exclusive(held, effect.ATTEMPT, raw)
                effect.custody._readback_leaf(held, effect.ATTEMPT, raw, identity, 1)
                with self.assertRaises(FileExistsError):
                    effect._write_exclusive(held, effect.ATTEMPT, raw)
                (Path(tmp) / (effect.TEMP_PREFIX + 'uncertain')).write_bytes(b'')
                with self.assertRaises(effect.Refusal):
                    effect.refuse_temp(held)
                result = {'status': 'FAIL', 'raw_diagnostics_published': False}
                (Path(tmp) / (effect.TEMP_PREFIX + 'uncertain')).unlink()
                effect.publish_result(held, result)
                self.assertEqual(json.loads((Path(tmp) / effect.RESULT).read_bytes()),
                                 result)
                with self.assertRaises(FileExistsError):
                    effect.publish_result(held, result)

    def test_failed_attempt_publication_never_enters_effect(self):
        with tempfile.TemporaryDirectory(prefix='replay-attempt-gate-') as tmp:
            evidence = Path(tmp)
            @contextmanager
            def held_scope():
                with HeldCanonicalDirectory(str(evidence)) as held:
                    yield held
            with mock.patch.object(effect, 'EVIDENCE', evidence):
                with mock.patch.object(effect.custody, 'controller_scope', held_scope):
                    with mock.patch.object(effect.plan, 'static_preflight',
                                           return_value={'fixture': True}):
                        with mock.patch.object(effect, 'package_rows',
                                               return_value={}):
                            with mock.patch.object(effect, '_write_exclusive',
                                                   side_effect=OSError('synthetic marker failure')):
                                with mock.patch.object(effect, 'effect') as launch:
                                    with self.assertRaises(OSError):
                                        effect.run_and_publish(evidence / effect.RESULT)
                                    launch.assert_not_called()

    def test_synthetic_capture_exact_copies_and_modes(self):
        with tempfile.TemporaryDirectory(prefix='replay-capture-test-') as tmp:
            base = Path(tmp)
            package = base / 'source-package'
            package.mkdir(mode=0o700)
            (package / 'semantic').mkdir(mode=0o700)
            (package / 'governance').mkdir(mode=0o700)
            rows = {}
            for name in sorted(effect.plan.expected_names()):
                raw = name.encode()
                path = package / name
                path.write_bytes(raw)
                path.chmod(0o600)
                rows[name] = (len(raw), effect.sha(raw))
            install = base / 'installation'
            (install / 'bin').mkdir(parents=True)
            (install / 'lib/abi').mkdir(parents=True)
            bwrap = base / 'bwrap'
            runtime = {
                bwrap: (b'bwrap', 0o755),
                install / 'bin/lab-context-native-reader': (b'native', 0o755),
                install / 'lib/abi/ld-linux-x86-64.so.2': (b'loader', 0o755),
                install / 'lib/abi/libgcc_s.so.1': (b'libgcc', 0o644),
                install / 'lib/abi/libc.so.6': (b'libc', 0o644),
            }
            for path, (raw, mode) in runtime.items():
                path.write_bytes(raw)
                path.chmod(mode)
            selected = {path: (len(raw), mode, effect.sha(raw))
                        for path, (raw, mode) in runtime.items()}
            scratch = base / 'scratch'
            scratch.mkdir(mode=0o700)
            state = {}
            with mock.patch.multiple(effect.plan, PACKAGE=package,
                                     INSTALL=install, BWRAP=bwrap,
                                     SELECTED_RUNTIME=selected):
                with mock.patch.object(effect, 'package_rows', return_value=rows):
                    copied_bwrap, specs = effect.capture(scratch, rows, state)
                self.assertEqual(copied_bwrap, scratch / 'selected/bwrap')
                self.assertEqual(len(specs), 60)
                with effect.custody.held_copies(scratch, specs) as held:
                    self.assertEqual(len(effect.custody.verify_copies(held)), 60)
                self.assertEqual((scratch / 'package/semantic').stat().st_mode & 0o777,
                                 0o500)
                self.assertEqual((scratch / 'package/request.json').stat().st_mode & 0o777,
                                 0o400)
                with HeldCanonicalDirectory(str(scratch)) as held_root:
                    effect.prepare_scratch_cleanup(scratch, held_root)
                self.assertEqual((scratch / 'package/semantic').stat().st_mode & 0o777,
                                 0o700)
                shutil.rmtree(scratch)
                self.assertFalse(scratch.exists())

    def test_unknown_child_retains_scratch_and_receipt_claim_ceiling(self):
        state = {'status': 'FAIL', 'stage': 'preflight', 'failure_code': None,
                 'children': {}, 'scratch_root': None,
                 'scratch_cleanup_observed': False,
                 'scratch_retained_unknown': False}
        def uncertain(root, bwrap, specs, rows, held, state):
            state['children']['replay_1'] = {'launch_attempted': True}
            raise OSError('synthetic uncertain child')
        try:
            root = Path('/tmp/lc-u02-05-historical-mapper-replay-' +
                        secrets.token_hex(16))
            with mock.patch.object(effect, 'capture', return_value=(Path('/tmp/bwrap'), {})):
                with mock.patch.object(effect, 'invoke', side_effect=uncertain):
                    with self.assertRaises(OSError):
                        effect.effect(state, {}, root)
            self.assertTrue(state['scratch_retained_unknown'])
            self.assertFalse(state['scratch_cleanup_observed'])
            self.assertTrue(state['scratch_root'].is_dir())
            result = effect.receipt(state)
            self.assertFalse(result['protected_source8_qualified'])
            self.assertFalse(result['fresh_same_scratch_mapper_qualified'])
            self.assertFalse(result['lc_u02_05_accepted'])
            self.assertFalse(result['escaped_session_absence_proven'])
            self.assertFalse(result['raw_diagnostics_published'])
            self.assertNotIn('synthetic uncertain child', str(result))
        finally:
            if state['scratch_root'] is not None:
                shutil.rmtree(state['scratch_root'])


if __name__ == '__main__':
    unittest.main()
