"""Read-only selected predispatch plus synthetic effect dispatch tests only."""
import datetime as dt
import importlib.util
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('context_stage_release_candidate',
                                             HERE / 'release.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
obs_spec = importlib.util.spec_from_file_location('context_stage_release_observer',
                                                 HERE / 'observer.py')
O = importlib.util.module_from_spec(obs_spec)
obs_spec.loader.exec_module(O)


class ReleaseCandidateTests(unittest.TestCase):
    def test_selected_public_predispatch_and_expired_period(self):
        proof = R.predispatch()
        self.assertEqual(proof['public_rehashed'], 1569)
        self.assertEqual(len(proof['rows']), 1570)
        self.assertEqual(proof['rows'][-1]['path'], R.ARCHIVE)
        self.assertEqual(proof['rows'][-1]['size'], R.ARCHIVE_SIZE)
        self.assertEqual(proof['protected_body'], 'UNOPENED')
        self.assertEqual(proof['security_profile'], 'trusted_local_fixture')
        expired = dt.datetime.fromisoformat(proof['period']['expires_at'])
        with self.assertRaises(R.Refused):
            R.predispatch(expired)

    def test_effect_enabled_without_real_dispatch(self):
        self.assertTrue(R.RELEASE_EFFECT_ENABLED)
        before = (os.path.lexists(R.ATTEMPT), os.path.lexists(R.MARKER))
        with self.assertRaises(R.Refused):
            R.launch_context()
        self.assertEqual(before, (os.path.lexists(R.ATTEMPT),
                                  os.path.lexists(R.MARKER)))

    def test_full_public_predispatch_never_opens_archive_leaf(self):
        real_open = R.os.open
        def reject_private_leaf(path, *args, **kwargs):
            if path == 'branch.snapshot' or str(path).endswith('/branch.snapshot'):
                raise AssertionError('protected archive body opened')
            return real_open(path, *args, **kwargs)
        with mock.patch.object(R.os, 'open', side_effect=reject_private_leaf):
            proof = R.predispatch()
        self.assertEqual(proof['protected_body'], 'UNOPENED')

    def test_synthetic_effect_order_and_private_last(self):
        events = []
        private = {'path': R.ARCHIVE, 'sha256': R.ARCHIVE_SHA,
                   'size': R.ARCHIVE_SIZE, 'mode': '0600', 'protected': True}
        public = {'path': 'public.txt', 'sha256': 'a'*64,
                  'size': 1, 'mode': '0600'}
        native = {'path': 'input/lab-context-native-reader',
                  'sha256': R.NATIVE_SHA, 'size': 20243600, 'mode': '0755'}
        def call(name, value=None):
            def wrapped(*args, **kwargs):
                events.append(name)
                return value
            return wrapped
        def copy(row, *_args, **_kwargs):
            events.append(('copy', row['path']))
            return {'sha256': row['sha256']}
        stage = {'REAL_EFFECT_ENABLED': False,
                 'mkdir_held': call('mkdir'), 'create_dirs': call('dirs'),
                 '_copy_one_core': copy,
                 'verify_namespace': call('verify',
                    {'files':1570,'private_digest_checked':1,'directories':30}),
                 'terminal_receipt': call('receipt','b'*64)}
        other_public = [{'path': 'public-%04d.txt' % i, 'sha256': 'a'*64,
                         'size': 1, 'mode': '0600'} for i in range(1568)]
        proof = {'stage': stage, 'rows': [public] + other_public + [private],
                 'native': native,
                 'selected': {'future_exclusive_stage_root': str(R.ATTEMPT / 'root')}}
        with mock.patch.object(R, 'RELEASE_EFFECT_ENABLED', True), \
             mock.patch.object(R, 'current_period', return_value={'current':True}):
            result = R._materialize_after_claim(proof, (8,9))
        self.assertEqual(result['status'], 'STAGE_ONLY_PASS')
        self.assertTrue(stage['REAL_EFFECT_ENABLED'])
        self.assertLess(events.index(('copy', 'public.txt')),
                        events.index(('copy', R.ARCHIVE)))
        self.assertLess(events.index(('copy', R.ARCHIVE)), events.index('verify'))
        self.assertEqual(events[-1], 'receipt')

    def test_incomplete_stage_after_claim_is_unknown_without_copy(self):
        events = []
        proof = {'rows': [{'path': R.ARCHIVE, 'protected': True}],
                 'selected': {'future_exclusive_stage_root': str(R.ATTEMPT / 'root')},
                 'stage': {'mkdir_held': lambda *_: events.append('mkdir')}}
        with mock.patch.object(R, 'RELEASE_EFFECT_ENABLED', True):
            with self.assertRaises(R.Unknown) as caught:
                R._materialize_after_claim(proof, (3, 4))
        self.assertEqual(caught.exception.outcome, 'UNKNOWN')
        self.assertEqual(events, [])

    def test_release_dispatch_orders_predispatch_claim_copy(self):
        events = []
        def prepared():
            events.append('predispatch')
            return {'synthetic': True, 'stage': {}}
        def claimed():
            events.append('claim')
            return (1,2)
        def copied(proof, inode):
            self.assertEqual(proof, {'synthetic': True, 'stage': {}})
            self.assertEqual(inode, (1,2))
            events.append('copy')
            return {'status': 'SYNTHETIC_ONLY'}
        with mock.patch.object(R, 'RELEASE_EFFECT_ENABLED', True), \
             mock.patch.object(R, 'predispatch', side_effect=prepared), \
             mock.patch.object(R, 'current_period', return_value={'current':True}), \
             mock.patch.object(R, '_reserve_and_claim', side_effect=claimed), \
             mock.patch.object(R, '_materialize_after_claim', side_effect=copied):
            self.assertEqual(R.release_effect()['status'], 'SYNTHETIC_ONLY')
        self.assertEqual(events, ['predispatch','claim','copy'])

    def test_disposable_one_shot_claim_and_consumed_marker(self):
        tmp = Path(tempfile.mkdtemp(prefix='cal-context-stage-release-fixture-'))
        attempt = Path('/tmp') / (tmp.name + '-attempt')
        marker = Path('/tmp') / ('.' + tmp.name + '-marker')
        try:
            with mock.patch.object(R, 'ATTEMPT', attempt), \
                 mock.patch.object(R, 'MARKER', marker), \
                 mock.patch.object(R, 'RELEASE_EFFECT_ENABLED', True):
                claimed = R._reserve_and_claim()
                self.assertEqual(claimed, (attempt.stat().st_dev,
                                           attempt.stat().st_ino))
                self.assertEqual(json.loads(marker.read_bytes())['status'],
                                 'RESERVED_NO_RETRY')
                with self.assertRaises(R.Refused):
                    R._reserve_and_claim()
        finally:
            shutil.rmtree(attempt, ignore_errors=True)
            marker.unlink(missing_ok=True)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_claim_failure_after_marker_is_unknown_and_no_retry(self):
        tmp = Path(tempfile.mkdtemp(prefix='cal-context-stage-release-fixture-'))
        attempt = Path('/tmp') / (tmp.name + '-attempt')
        marker = Path('/tmp') / ('.' + tmp.name + '-marker')
        real_mkdir = R.os.mkdir
        def fail_attempt(name, *args, **kwargs):
            if name == attempt.name:
                raise OSError('injected attempt creation failure')
            return real_mkdir(name, *args, **kwargs)
        try:
            with mock.patch.object(R, 'ATTEMPT', attempt), \
                 mock.patch.object(R, 'MARKER', marker), \
                 mock.patch.object(R, 'RELEASE_EFFECT_ENABLED', True):
                with mock.patch.object(R.os, 'mkdir', side_effect=fail_attempt):
                    with self.assertRaises(R.Unknown) as caught:
                        R._reserve_and_claim()
                self.assertEqual(caught.exception.outcome, 'UNKNOWN')
                self.assertFalse(caught.exception.retry_allowed)
                self.assertTrue(marker.exists())
                self.assertFalse(attempt.exists())
                with self.assertRaises(R.Refused):
                    R._reserve_and_claim()
        finally:
            shutil.rmtree(attempt, ignore_errors=True)
            marker.unlink(missing_ok=True)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_observer_exact_effect_dispatch_pins_without_spawn(self):
        with mock.patch.object(O.subprocess, 'Popen', side_effect=AssertionError('spawned')):
            selected = O.pin_dispatch()
        self.assertEqual(selected['one_shot_attempt'], str(R.ATTEMPT))
        self.assertEqual(O.EFFECT_ARGV,
                         ['/usr/bin/python3','-B',str(O.RELEASE),'--effect'])
        self.assertFalse(O.OBSERVATION.exists())

    def test_observer_refuses_consumed_paths_before_any_child(self):
        with mock.patch.object(O.os.path, 'lexists', return_value=True), \
             mock.patch.object(O.subprocess, 'Popen', side_effect=AssertionError('spawned')):
            with self.assertRaises(RuntimeError):
                O.pin_dispatch()

    def test_effect_rechecks_live_period_before_claim(self):
        events = []
        proof = {'stage': {'sentinel':True}}
        with mock.patch.object(R, 'predispatch', return_value=proof), \
             mock.patch.object(R, 'current_period', side_effect=lambda *_: events.append('period')), \
             mock.patch.object(R, '_reserve_and_claim', side_effect=lambda: events.append('claim') or (1,2)), \
             mock.patch.object(R, '_materialize_after_claim', side_effect=lambda *_: events.append('copy') or {'status':'SYNTHETIC'}):
            self.assertEqual(R.release_effect()['status'], 'SYNTHETIC')
        self.assertEqual(events, ['period','claim','copy'])

    def test_synthetic_external_os_observer_matches_receipt_once(self):
        attempt = Path(tempfile.mkdtemp(prefix='cal-context-stage-observer-attempt-fixture-'))
        observation = Path('/tmp') / ('.cal-context-stage-observer-fixture-' + attempt.name)
        stage = {'schema_version':'lab-context-stage-release-receipt/v1-candidate',
                 'status':'STAGE_ONLY_PASS', 'selection_sha256':O.STAGE_SELECTION_SHA,
                 'archive_sha256':O.ARCHIVE_SHA, 'archive_size':23550300,
                 'stage_files':1570, 'security_profile':'trusted_local_fixture',
                 'original_protected_G01_G02':'UNSATISFIED',
                 'context_launch':'REFUSED'}
        raw = O.canonical(stage)
        (attempt / 'stage-receipt.json').write_bytes(raw)
        stdout = O.canonical({'status':'STAGE_ONLY_PASS',
                              'receipt_sha256':hashlib.sha256(raw).hexdigest()})
        argv = [sys.executable, '-B', '-c',
                'import os; os.write(1, bytes.fromhex("'+stdout.hex()+'"))']
        try:
            with mock.patch.object(O, 'pin_dispatch', return_value={}), \
                 mock.patch.object(O, 'ATTEMPT', attempt), \
                 mock.patch.object(O, 'OBSERVATION', observation), \
                 mock.patch.object(O, 'EFFECT_ARGV', argv):
                result = O.observe_effect(timeout=10)
                self.assertEqual(result['status'], 'OS_EXIT0_STAGE_RECEIPT_MATCHED')
                self.assertEqual(result['os_exit_code'], 0)
                self.assertFalse(result['retry_allowed'])
                self.assertEqual(json.loads((observation/'result.json').read_bytes()),
                                 result)
                with self.assertRaises(FileExistsError):
                    O.observe_effect(timeout=10)
        finally:
            shutil.rmtree(attempt, ignore_errors=True)
            shutil.rmtree(observation, ignore_errors=True)

    def test_synthetic_observer_exit_zero_without_receipt_is_unknown(self):
        attempt = Path(tempfile.mkdtemp(prefix='cal-context-stage-observer-no-receipt-'))
        observation = Path('/tmp') / ('.cal-context-stage-observer-fixture-' + attempt.name)
        argv = [sys.executable, '-B', '-c', 'print("synthetic-only")']
        try:
            with mock.patch.object(O, 'pin_dispatch', return_value={}), \
                 mock.patch.object(O, 'ATTEMPT', attempt), \
                 mock.patch.object(O, 'OBSERVATION', observation), \
                 mock.patch.object(O, 'EFFECT_ARGV', argv):
                result = O.observe_effect(timeout=10)
            self.assertEqual(result['os_exit_code'], 0)
            self.assertEqual(result['status'], 'OS_OBSERVED_STAGE_UNKNOWN')
            self.assertFalse(result['retry_allowed'])
        finally:
            shutil.rmtree(attempt, ignore_errors=True)
            shutil.rmtree(observation, ignore_errors=True)

    def test_synthetic_observer_timeout_is_consumed_unknown(self):
        attempt = Path(tempfile.mkdtemp(prefix='cal-context-stage-observer-timeout-'))
        observation = Path('/tmp') / ('.cal-context-stage-observer-fixture-' + attempt.name)
        class TimedOutChild:
            def __init__(self): self.killed = False
            def wait(self, timeout=None):
                if not self.killed:
                    raise subprocess.TimeoutExpired(['synthetic'], timeout)
                return -9
            def kill(self): self.killed = True
        child = TimedOutChild()
        try:
            with mock.patch.object(O, 'pin_dispatch', return_value={}), \
                 mock.patch.object(O, 'ATTEMPT', attempt), \
                 mock.patch.object(O, 'OBSERVATION', observation), \
                 mock.patch.object(O.subprocess, 'Popen', return_value=child):
                result = O.observe_effect(timeout=0.01)
            self.assertTrue(child.killed)
            self.assertEqual(result['status'], 'OS_OBSERVED_STAGE_UNKNOWN')
            self.assertEqual(result['process_error'], 'TIMEOUT_KILLED_UNKNOWN')
            self.assertFalse(result['retry_allowed'])
        finally:
            shutil.rmtree(attempt, ignore_errors=True)
            shutil.rmtree(observation, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
