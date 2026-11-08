"""Enabled release controller: fake-daemon lifecycle and fault tests only."""
from __future__ import annotations

import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import controller as c


class FakeDocker:
    CID = 'a' * 64

    def __init__(self, mode: str, output: Path, plan: dict):
        self.mode, self.output, self.plan = mode, output, plan
        self.info = None
        self.calls = []

    def inspected(self, name):
        self.calls.append(('inspect', name))
        if self.mode == 'daemon_unavailable_on_observation' and self.info is not None:
            raise OSError('synthetic daemon unavailable')
        return copy.deepcopy(self.info)

    def cli(self, argv, *, seconds=12.0):
        self.calls.append(tuple(argv[:3]))
        action = argv[1]
        if action == 'create':
            if self.mode == 'lost_create':
                return subprocess.CompletedProcess(argv, 1, b'', b'create response lost')
            label = argv[argv.index('--label') + 1].split('=', 1)[1]
            self.info = {'Id': self.CID, 'Name': '/' + c.NAME, 'Image': c.IMAGE,
                         'Config': {'Image': c.IMAGE, 'Labels': {'cal.reader.attempt': label}},
                         'State': {'Running': False, 'Status': 'created', 'ExitCode': 0}}
            if self.mode == 'nonzero_with_created':
                return subprocess.CompletedProcess(argv, 1, b'', b'invalid mount config: private path')
            if self.mode == 'malformed_with_created':
                return subprocess.CompletedProcess(argv, 0, b'bad id\n', b'')
            if self.mode == 'lost_stdout_with_created':
                return subprocess.CompletedProcess(argv, 0, b'', b'')
            if self.mode == 'create_exception_with_created':
                error = TimeoutError('synthetic create timeout')
                error.bounded_stdout = b'partial'
                error.bounded_stderr = b'private diagnostic omitted'
                error.child_returncode = None
                raise error
            if self.mode == 'wrong_label_after_create':
                self.info['Config']['Labels']['cal.reader.attempt'] = 'wrong'
            return subprocess.CompletedProcess(argv, 0, (self.CID + '\n').encode(), b'')
        if action in ('stop', 'kill'):
            if self.mode == 'lost_cleanup':
                return subprocess.CompletedProcess(argv, 1, b'', b'daemon unavailable')
            self.info['State'].update(Running=False, Status='exited', ExitCode=137)
            return subprocess.CompletedProcess(argv, 0, (self.CID + '\n').encode(), b'')
        if action == 'wait':
            return subprocess.CompletedProcess(argv, 0,
                                               (str(self.info['State']['ExitCode']) + '\n').encode(), b'')
        if action == 'rm':
            if self.mode == 'rm_lost':
                raise OSError('rm unavailable after pre-removal receipt')
            self.info = None
            return subprocess.CompletedProcess(argv, 0, (self.CID + '\n').encode(), b'')
        raise AssertionError(argv)

    def capture(self, cid, stdout, stderr):
        self.calls.append(('start', cid))
        if self.mode == 'never_started':
            raise TimeoutError('start response lost')
        self.info['State'].update(Running=True, Status='running')
        if self.mode in ('client_lost', 'lost_cleanup'):
            raise TimeoutError('client lost')
        if self.mode == 'deadline':
            return None, True
        receipt = {'schema_version': 'lab-disposable-reader-receipt/v1-private',
                   'reader_manifest_sha256': c.READER_SHA,
                   'source_package_manifest_sha256': self.plan['source_package_manifest_sha256'],
                   'expected_head': self.plan['selection']['expected_head'],
                   'authority_effect': 'none', 'actual_owner_outcome': None}
        raw = c.json_bytes(receipt)
        (self.output / 'receipt.json').write_bytes(raw)
        stdout.write_bytes(c.json_bytes({'result': 'PASS_READER_PRIVATE',
                                        'receipt_sha256': c.sha(raw),
                                        'reader_manifest_sha256': c.READER_SHA,
                                        'source_package_manifest_sha256': self.plan['source_package_manifest_sha256']}))
        self.info['State'].update(Running=False, Status='exited', ExitCode=0)
        return 0, self.mode == 'overflow'


class ControllerTests(unittest.TestCase):
    def setUp(self):
        c.STOP_REQUESTED = False
        self.addCleanup(lambda: setattr(c, 'STOP_REQUESTED', False))
        temp = tempfile.TemporaryDirectory(prefix='cal-reader-controller-fake-')
        self.addCleanup(temp.cleanup)
        self.attempt = Path(temp.name)
        self.root = self.attempt / 'root'
        (self.root / c.SOURCE / 'packages/0001').mkdir(parents=True)
        (self.root / c.SOURCE / 'packages/0001/period.json').write_text('{}\n')
        self.output = self.attempt / 'reader-output'
        self.output.mkdir(mode=0o700)
        self.evidence = self.attempt / 'evidence'
        self.evidence.mkdir(mode=0o700)
        self.base = self.attempt / 'tool'
        self.base.mkdir()
        self.plan = {'selection': {'expected_head': 'h' * 64},
                     'source_package_manifest_sha256': 'b' * 64,
                     'reader_manifest_sha256': c.READER_SHA, 'rows': []}

    def execute_fake(self, mode, *, post_plan=None, period_effect=None):
        fake = FakeDocker(mode, self.output, self.plan)
        self.last_fake = fake
        reads = [self.plan, self.plan if post_plan is None else post_plan]
        with mock.patch.multiple(c, EFFECT_ENABLED=True, BASE=self.base, ATTEMPT=self.attempt,
                                 ROOT=self.root, OUT=self.output, EVIDENCE=self.evidence), \
             mock.patch.object(c, 'frozen_inputs', side_effect=reads), \
             mock.patch.object(c, 'period_current', side_effect=period_effect), \
             mock.patch.object(c, 'inspected', side_effect=fake.inspected), \
             mock.patch.object(c, 'cli', side_effect=fake.cli), \
             mock.patch.object(c, 'capture_start', side_effect=fake.capture):
            result = c.run()
        return fake, result

    def test_release_selection_is_disjoint(self):
        self.assertTrue(c.EFFECT_ENABLED)
        self.assertEqual(c.NAME, 'cal-reader-only-20261020-0001-unified-0006')
        self.assertEqual(c.ATTEMPT, Path('/tmp/cal-reader-only-dev-20261020-0001-unified6'))
        self.assertEqual(c.BASE.name, 'reader-only-unified-0006')

    def test_selected_create_mounts_and_command(self):
        argv = c.docker_create_argv('nonce')
        self.assertNotIn('--pid', argv)  # Docker's default is private; "private" is invalid.
        self.assertEqual(argv[argv.index('--ipc') + 1], 'private')
        self.assertNotIn('--uts', argv)  # Docker's default is private; "private" is invalid.
        self.assertEqual(argv[argv.index('--pids-limit') + 1], '1')
        self.assertIn('--env', argv)
        self.assertEqual(argv[argv.index('--env') + 1],
                         f'CAL_READER_STAGE_ID={c.ROOT.stat().st_dev}:{c.ROOT.stat().st_ino}')
        self.assertIn('/attempt/tmp:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000',
                      argv)
        self.assertIn(f'type=bind,src={c.ROOT},dst=/attempt/root,readonly', argv)
        self.assertIn(f'type=bind,src={c.BASE},dst=/tool,readonly', argv)
        self.assertIn(f'type=bind,src={c.OUT},dst=/attempt/reader-output', argv)
        self.assertEqual(argv[-4:], ['python', '-B', '/tool/reader_once.py', '--execute-reviewed-one-shot'])
        self.assertIn('1000:1000', argv)
        self.assertEqual(argv.count('--tmpfs'), 2)

    def test_stage_unknown_at_attempt_root_supersedes_neutral(self):
        stage = self.attempt / 'stage'
        (stage / 'evidence').mkdir(parents=True)
        c.stage_unknown_absent(stage)
        (stage / 'stage-unknown.json').write_text('{"overall":"UNKNOWN"}\n')
        with self.assertRaisesRegex(ValueError, 'UNKNOWN supersedes neutral'):
            c.stage_unknown_absent(stage)
        (stage / 'stage-unknown.json').unlink()
        (stage / 'stage-unknown.json').symlink_to('missing-target')
        with self.assertRaisesRegex(ValueError, 'UNKNOWN supersedes neutral'):
            c.stage_unknown_absent(stage)

    def test_stage_metadata_rejects_mode_and_link_with_identical_bytes(self):
        stage = self.attempt / 'synthetic-stage-root'
        stage.mkdir(mode=0o755)
        stage.chmod(0o755)
        name = c.SOURCE + '/packages/0001/period.json'
        expected = c.expected_directories({name})
        for directory in sorted(expected, key=lambda item: (len(Path(item).parts), item)):
            path = stage / directory
            path.mkdir(exist_ok=True)
            private = directory == c.SOURCE + '/receipts' or directory.startswith(c.SOURCE + '/packages')
            path.chmod(0o700 if private else 0o755)
        leaf = stage / name
        leaf.write_bytes(b'synthetic period\n')
        leaf.chmod(0o600)
        row = {'path': name, 'sha256': c.sha(leaf.read_bytes()), 'target_mode': '0600'}
        c.verify_stage_metadata(stage, {name: row}, expected)
        leaf.chmod(0o777)
        with self.assertRaisesRegex(ValueError, 'mode or link changed'):
            c.verify_stage_metadata(stage, {name: row}, expected)
        leaf.chmod(0o600)
        outside_link = self.attempt / 'second-link'
        outside_link.hardlink_to(leaf)
        with self.assertRaisesRegex(ValueError, 'mode or link changed'):
            c.verify_stage_metadata(stage, {name: row}, expected)
        outside_link.unlink()
        (stage / c.SOURCE / 'packages').chmod(0o777)
        with self.assertRaisesRegex(ValueError, 'directory owner or mode changed'):
            c.verify_stage_metadata(stage, {name: row}, expected)

    def test_clean_fake_exit_persists_identity_and_pre_removal(self):
        fake, result = self.execute_fake('success')
        self.assertEqual(result['overall'], 'PASS')
        self.assertIsNone(fake.info)
        self.assertEqual(result['receipt_sha256'], c.sha((self.output / 'receipt.json').read_bytes()))
        self.assertTrue((self.evidence / 'reader-attempt-consumed.json').is_file())
        self.assertTrue((self.evidence / 'reader-container-id.json').is_file())
        self.assertTrue((self.evidence / 'reader-create-response.json').is_file())
        self.assertTrue((self.evidence / 'reader-create-observation.json').is_file())
        self.assertTrue((self.evidence / 'reader-pre-removal.json').is_file())
        provisional = json.loads((self.evidence / 'reader-once.terminal.json').read_bytes())
        self.assertEqual(provisional['overall'], 'UNKNOWN')
        self.assertEqual(provisional['candidate_overall'], 'PASS')
        self.assertEqual(provisional['finalization'], 'PENDING_OUTER_CLOSES')
        self.assertEqual(json.loads((self.evidence / 'reader-once.final.json').read_bytes()), result)
        self.assertTrue((self.evidence / 'reader-once.finalized').is_dir())
        with self.assertRaises(FileExistsError):
            c.exclusive(self.evidence / 'reader-attempt-consumed.json', b'again')

    def test_lost_create_is_consumed_no_retry(self):
        fake, result = self.execute_fake('lost_create')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertTrue(result['no_retry'])
        self.assertIsNone(fake.info)
        self.assertFalse(any(call[0] == 'start' for call in fake.calls))
        response = json.loads((self.evidence / 'reader-create-response.json').read_bytes())
        observation = json.loads((self.evidence / 'reader-create-observation.json').read_bytes())
        self.assertEqual(response['returncode'], 1)
        self.assertEqual(response['stderr_sha256'], c.sha(b'create response lost'))
        self.assertEqual(response['stderr_diagnostic'], 'OTHER_REDACTED')
        self.assertEqual(observation['state'], 'ABSENT')

    def assert_failed_create_with_owned_object(self, mode, diagnostic):
        fake, result = self.execute_fake(mode)
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertTrue(result['absent'])
        self.assertEqual(result['cleanup'], 'removed_unstarted')
        self.assertFalse(any(call[0] == 'start' for call in fake.calls))
        response = json.loads((self.evidence / 'reader-create-response.json').read_bytes())
        observation = json.loads((self.evidence / 'reader-create-observation.json').read_bytes())
        self.assertEqual(observation['identity'], 'MATCH')
        self.assertEqual(observation['daemon_status'], 'created')
        self.assertEqual(observation['container_id'], FakeDocker.CID)
        self.assertEqual(response['stderr_diagnostic'], diagnostic)
        self.assertTrue((self.evidence / 'reader-pre-removal.json').is_file())

    def test_nonzero_create_with_daemon_object(self):
        self.assert_failed_create_with_owned_object('nonzero_with_created',
                                                    'INVALID_MOUNT_CONFIG')

    def test_malformed_create_with_daemon_object(self):
        self.assert_failed_create_with_owned_object('malformed_with_created', 'EMPTY')

    def test_lost_stdout_with_daemon_object(self):
        self.assert_failed_create_with_owned_object('lost_stdout_with_created', 'EMPTY')

    def test_exception_with_daemon_object(self):
        self.assert_failed_create_with_owned_object('create_exception_with_created',
                                                    'OTHER_REDACTED')

    def test_unavailable_daemon_after_create_does_not_cleanup_or_start(self):
        fake, result = self.execute_fake('daemon_unavailable_on_observation')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertEqual(result['cleanup'], 'NOT_ATTEMPTED_WITHOUT_CREATE_OBSERVATION')
        self.assertIsNotNone(fake.info)
        self.assertFalse(any(call[0] == 'start' or call[1] == 'rm' for call in fake.calls))
        observation = json.loads((self.evidence / 'reader-create-observation.json').read_bytes())
        self.assertEqual(observation['state'], 'INSPECT_UNKNOWN')

    def test_wrong_identity_after_create_refuses_start_and_mutating_cleanup(self):
        fake, result = self.execute_fake('wrong_label_after_create')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertFalse(any(call[0] == 'start' or call[1] in ('rm', 'stop', 'kill')
                             for call in fake.calls if len(call) > 1))
        observation = json.loads((self.evidence / 'reader-create-observation.json').read_bytes())
        self.assertEqual(observation['identity'], 'DIFFERS')
        self.assertIsNotNone(fake.info)

    def test_client_loss_stops_only_owned_container(self):
        fake, result = self.execute_fake('client_lost')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertEqual(result['daemon_exit'], 137)
        self.assertTrue(result['absent'])
        self.assertIsNone(fake.info)
        self.assertIn((c.DOCKER, 'stop', '--time'), fake.calls)

    def test_never_started_does_not_wait(self):
        fake, result = self.execute_fake('never_started')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertEqual(result['cleanup'], 'removed_unstarted')
        self.assertNotIn((c.DOCKER, 'wait', FakeDocker.CID), fake.calls)

    def test_deadline_does_not_pass(self):
        fake, result = self.execute_fake('deadline')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertTrue(result['stream_or_deadline_failure'])
        self.assertIsNone(fake.info)

    def test_overflow_does_not_pass(self):
        fake, result = self.execute_fake('overflow')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertTrue(result['stream_or_deadline_failure'])
        self.assertIsNone(fake.info)

    def test_changed_postclose_inputs_do_not_pass(self):
        fake, result = self.execute_fake('success', post_plan={'changed': True})
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertIn('postclose_error_class', result)
        self.assertIsNone(fake.info)

    def test_lost_cleanup_preserves_unknown_and_container(self):
        fake, result = self.execute_fake('lost_cleanup')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertIsNotNone(fake.info)
        self.assertIn('cleanup_error_class', result)

    def test_pre_removal_receipt_survives_rm_loss(self):
        fake, result = self.execute_fake('rm_lost')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertIsNotNone(fake.info)
        self.assertTrue((self.evidence / 'reader-pre-removal.json').is_file())
        self.assertEqual(json.loads((self.evidence / 'reader-pre-removal.json').read_bytes())
                         ['container']['id'], FakeDocker.CID)

    def test_recovery_after_rm_loss_is_cleanup_only(self):
        fake, result = self.execute_fake('rm_lost')
        self.assertEqual(result['overall'], 'UNKNOWN')
        fake.mode = 'success'
        fake.calls.clear()
        with mock.patch.multiple(c, EFFECT_ENABLED=True, BASE=self.base, ATTEMPT=self.attempt,
                                 ROOT=self.root, OUT=self.output, EVIDENCE=self.evidence), \
             mock.patch.object(c, 'inspected', side_effect=fake.inspected), \
             mock.patch.object(c, 'cli', side_effect=fake.cli):
            recovered = c.recover_consumed()
        self.assertTrue(recovered['absent'])
        self.assertEqual(recovered['operation'], 'UNKNOWN')
        self.assertIsNone(fake.info)
        self.assertFalse(any(call[0] == 'start' or call[:2] == (c.DOCKER, 'create')
                             for call in fake.calls))

    def test_wrong_owned_label_prevents_stop(self):
        fake = FakeDocker('client_lost', self.output, self.plan)
        fake.info = {'Id': FakeDocker.CID, 'Name': '/' + c.NAME, 'Image': c.IMAGE,
                     'Config': {'Image': c.IMAGE, 'Labels': {'cal.reader.attempt': 'wrong'}},
                     'State': {'Running': True, 'Status': 'running', 'ExitCode': 0}}
        with mock.patch.object(c, 'inspected', side_effect=fake.inspected), \
             mock.patch.object(c, 'cli', side_effect=fake.cli), \
             self.assertRaisesRegex(ValueError, 'identity differs'):
            c.settle('right', FakeDocker.CID)
        self.assertFalse(any(call[1] in ('stop', 'kill', 'rm') for call in fake.calls if len(call) > 1))

    def test_nonregular_output_refused_without_reading(self):
        os.mkfifo(self.output / 'receipt.json')
        with mock.patch.object(c, 'OUT', self.output), \
             self.assertRaisesRegex(ValueError, 'bounded evidence leaf differs'):
            c.output_inventory()

    def test_real_bounded_stream_without_docker(self):
        real_popen = subprocess.Popen
        def local_child(_argv, **kwargs):
            return real_popen([sys.executable, '-B', '-c',
                               "import sys;sys.stdout.write('x'*100);sys.stderr.write('y'*100)"], **kwargs)
        out, err = self.evidence / 'out', self.evidence / 'err'
        out.write_bytes(b'')
        err.write_bytes(b'')
        out.chmod(0o600)
        err.chmod(0o600)
        with mock.patch.object(c.subprocess, 'Popen', side_effect=local_child), \
             mock.patch.object(c, 'MAX_STREAM', 16):
            code, overflow = c.capture_start(FakeDocker.CID, out, err)
        self.assertEqual(code, 0)
        self.assertTrue(overflow)
        self.assertEqual(len(out.read_bytes()), 16)
        self.assertEqual(len(err.read_bytes()), 16)

    def test_symlinked_evidence_ancestor_does_not_redirect_write(self):
        outside = self.attempt / 'outside'
        outside.mkdir()
        (self.attempt / 'linked').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(OSError):
            c.exclusive(self.attempt / 'linked' / 'marker', b'private')
        self.assertFalse((outside / 'marker').exists())

    def test_swapped_log_symlink_is_not_followed_by_local_child(self):
        outside = self.attempt / 'outside-log'
        outside.write_bytes(b'fixed')
        out, err = self.evidence / 'out', self.evidence / 'err'
        out.write_bytes(b'')
        err.write_bytes(b'')
        out.chmod(0o600)
        err.chmod(0o600)
        identity = (out.stat().st_dev, out.stat().st_ino)
        out.unlink()
        out.symlink_to(outside)
        real_popen = subprocess.Popen
        child = []
        def local_child(_argv, **kwargs):
            proc = real_popen([sys.executable, '-B', '-c', "print('would-be-log')"], **kwargs)
            child.append(proc)
            return proc
        with mock.patch.dict(c.LOG_IDENTITIES, {'out': identity}), \
             mock.patch.object(c.subprocess, 'Popen', side_effect=local_child), \
             self.assertRaises(OSError):
            c.capture_start(FakeDocker.CID, out, err)
        self.assertEqual(outside.read_bytes(), b'fixed')
        self.assertIsNotNone(child[0].poll())

    def test_replaced_regular_log_identity_rejected(self):
        out = self.evidence / 'out'
        out.write_bytes(b'')
        out.chmod(0o600)
        identity = (out.stat().st_dev, out.stat().st_ino)
        out.unlink()
        out.write_bytes(b'')
        out.chmod(0o600)
        with mock.patch.dict(c.LOG_IDENTITIES, {'out': identity}), \
             self.assertRaisesRegex(ValueError, 'log leaf attachment changed'):
            with c.open_log_append(out):
                pass

    def test_oversize_receipt_refused_before_read(self):
        (self.output / 'receipt.json').write_bytes(b'x' * 128)
        with mock.patch.object(c, 'OUT', self.output), \
             mock.patch.object(c, 'MAX_RECEIPT', 16), \
             self.assertRaisesRegex(ValueError, 'bounded evidence leaf differs'):
            c.output_inventory()

    def test_docker_cli_stream_is_bounded_and_child_reaped(self):
        real_popen = subprocess.Popen
        child = []
        def local_child(_argv, **kwargs):
            proc = real_popen([sys.executable, '-B', '-c',
                               "import sys;sys.stdout.write('x'*100000)"], **kwargs)
            child.append(proc)
            return proc
        with mock.patch.object(c.subprocess, 'Popen', side_effect=local_child), \
             mock.patch.object(c, 'MAX_CLI', 16), \
             self.assertRaisesRegex(ValueError, 'stream exceeds bound'):
            c.cli([c.DOCKER, 'inspect', c.NAME])
        self.assertIsNotNone(child[0].poll())

    def test_late_stop_at_terminal_writer_downgrades_durable_result(self):
        real_exclusive = c.exclusive
        def late_stop(path, raw, **kwargs):
            if path.name == 'reader-once.terminal.json':
                c.STOP_REQUESTED = True
            return real_exclusive(path, raw, **kwargs)
        with mock.patch.object(c, 'exclusive', side_effect=late_stop):
            fake, result = self.execute_fake('success')
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertTrue(result['interrupted'])
        self.assertEqual(json.loads((self.evidence / 'reader-once.terminal.json').read_bytes())
                         ['overall'], 'UNKNOWN')
        self.assertIsNone(fake.info)

    def test_period_expiry_at_terminal_commit_downgrades(self):
        calls = []
        def expire_at_commit(_period):
            calls.append(1)
            if len(calls) >= 2:
                raise ValueError('synthetic period expiry')
        fake, result = self.execute_fake('success', period_effect=expire_at_commit)
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertTrue(result['period_expired_at_commit'])
        self.assertEqual(json.loads((self.evidence / 'reader-once.terminal.json').read_bytes())
                         ['overall'], 'UNKNOWN')
        self.assertIsNone(fake.info)

    def test_stop_during_terminal_file_fsync_rewrites_unknown(self):
        real_fsync = os.fsync
        injected = []
        def interrupting_fsync(fd):
            target = os.readlink(f'/proc/self/fd/{fd}')
            if target.endswith('/reader-once.terminal.json') and not injected:
                injected.append(True)
                c.STOP_REQUESTED = True
            return real_fsync(fd)
        with mock.patch.object(c.os, 'fsync', side_effect=interrupting_fsync):
            fake, result = self.execute_fake('success')
        self.assertTrue(injected)
        self.assertEqual(result['overall'], 'UNKNOWN')
        self.assertEqual(json.loads((self.evidence / 'reader-once.terminal.json').read_bytes())
                         ['overall'], 'UNKNOWN')
        self.assertIsNone(fake.info)

    def test_changed_held_mount_ancestor_refused(self):
        source = self.attempt / 'selected-mount'
        source.mkdir()
        with self.assertRaisesRegex(ValueError, 'attachment changed'):
            with c.held_directory(source) as chain:
                moved = self.attempt / 'moved-mount'
                source.rename(moved)
                source.symlink_to(moved, target_is_directory=True)
                c.check_chain(chain)

    def test_cli_preserves_primary_and_attempts_all_cleanup(self):
        class Child:
            def __init__(self):
                self.stdout, self.stderr, self.calls = io.BytesIO(), io.BytesIO(), []
            def poll(self):
                self.calls.append('poll')
                return None
            def terminate(self):
                self.calls.append('terminate')
                raise OSError('synthetic terminate failure')
            def wait(self, **_):
                self.calls.append('wait')
                if self.calls.count('wait') == 1:
                    raise subprocess.TimeoutExpired('fake', 3)
                return 0
            def kill(self):
                self.calls.append('kill')
                raise OSError('synthetic kill failure')
        child = Child()
        primary = ValueError('synthetic selector setup')
        with mock.patch.object(c.subprocess, 'Popen', return_value=child), \
             mock.patch.object(c.selectors, 'DefaultSelector', side_effect=primary):
            with self.assertRaises(ValueError) as caught:
                c.cli(['fake-unexecuted'])
        self.assertIs(caught.exception, primary)
        self.assertEqual(child.calls, ['poll', 'terminate', 'wait', 'kill', 'wait'])
        self.assertEqual([name for name, _ in primary.secondary_cleanup_errors],
                         ['terminate', 'wait_after_terminate', 'kill'])
        self.assertTrue(child.stdout.closed and child.stderr.closed)

    def test_client_cleanup_attempts_selector_and_both_pipes_after_wait_fault(self):
        class FaultStream(io.BytesIO):
            def close(self):
                super().close()
                raise OSError('synthetic pipe close after real close')
        class Child:
            def __init__(self):
                self.stdout, self.stderr, self.calls = FaultStream(), FaultStream(), []
            def poll(self): return None
            def terminate(self): self.calls.append('terminate')
            def wait(self, **_):
                self.calls.append('wait')
                raise OSError('synthetic wait failure')
            def kill(self): self.calls.append('kill')
        class Selector:
            def __init__(self): self.closed = False
            def close(self):
                self.closed = True
                raise OSError('synthetic selector close failure')
        child, selector = Child(), Selector()
        primary = ValueError('primary')
        result = c.cleanup_owned_client(child, selector, primary)
        self.assertIs(result, primary)
        self.assertEqual(child.calls, ['terminate', 'wait', 'kill', 'wait'])
        self.assertTrue(selector.closed and child.stdout.closed and child.stderr.closed)
        self.assertEqual([name for name, _ in primary.secondary_cleanup_errors],
                         ['wait_after_terminate', 'wait_after_kill', 'selector_close',
                          'stdout_close', 'stderr_close'])

    def test_held_directory_closes_every_fd_and_preserves_primary(self):
        real_open, real_close = os.open, os.close
        opened, attempts = [], []
        def opening(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd
        def closing(fd):
            attempts.append(fd)
            real_close(fd)
            if len(attempts) in (1, 3):
                raise OSError('synthetic close after real close')
        primary = ValueError('inside held scope')
        with mock.patch.object(c.os, 'open', side_effect=opening), \
             mock.patch.object(c.os, 'close', side_effect=closing):
            with self.assertRaises(ValueError) as caught:
                with c.held_directory(self.evidence):
                    raise primary
        self.assertIs(caught.exception, primary)
        self.assertEqual(attempts, list(reversed(opened)))
        self.assertEqual(len(primary.secondary_close_errors), 2)
        for fd in opened:
            with self.assertRaises(OSError): os.fstat(fd)

    def test_postterminal_close_failure_does_not_return_pass(self):
        real_close = os.close
        triggered = []
        def closing(fd):
            target = os.readlink(f'/proc/self/fd/{fd}')
            real_close(fd)
            if target == str(self.evidence) and not triggered:
                triggered.append(True)
                raise OSError('synthetic evidence dir close after real close')
        with mock.patch.object(c.os, 'close', side_effect=closing):
            with self.assertRaises(BaseExceptionGroup) as caught:
                self.execute_fake('success')
        self.assertTrue(triggered)
        self.assertTrue((self.evidence / 'reader-once.terminal.json').is_file())
        self.assertEqual(json.loads((self.evidence / 'reader-once.terminal.json').read_bytes())
                         ['overall'], 'UNKNOWN')
        self.assertFalse((self.evidence / 'reader-once.final.json').exists())
        self.assertFalse((self.evidence / 'reader-once.finalized').exists())
        self.assertIn('custody is UNKNOWN', str(caught.exception))

    def test_outer_close_failure_recovery_treats_provisional_pass_as_unknown(self):
        real_close = os.close
        triggered = []
        def closing(fd):
            target = os.readlink(f'/proc/self/fd/{fd}')
            real_close(fd)
            if target == str(self.evidence) and not triggered:
                triggered.append(True)
                raise OSError('synthetic evidence close after real close')
        with mock.patch.object(c.os, 'close', side_effect=closing), \
             self.assertRaises(BaseExceptionGroup):
            self.execute_fake('success')
        self.assertTrue(triggered)
        fake = self.last_fake
        fake.calls.clear()
        with mock.patch.multiple(c, EFFECT_ENABLED=True, BASE=self.base, ATTEMPT=self.attempt,
                                 ROOT=self.root, OUT=self.output, EVIDENCE=self.evidence), \
             mock.patch.object(c, 'inspected', side_effect=fake.inspected):
            recovered = c.recover_consumed()
        self.assertEqual(recovered['operation'], 'UNKNOWN')
        self.assertEqual(recovered['finalization'], 'MISSING_OR_FAILED')
        self.assertTrue(recovered['absent'])
        self.assertFalse(any(call[0] == 'start' for call in fake.calls))

    def test_final_file_close_failure_cannot_commit_pass_marker(self):
        real_close = os.close
        evidence_closes = []
        def closing(fd):
            target = os.readlink(f'/proc/self/fd/{fd}')
            final_written = (self.evidence / 'reader-once.final.json').is_file()
            real_close(fd)
            if target == str(self.evidence) and final_written:
                evidence_closes.append(True)
                if len(evidence_closes) == 1:
                    raise OSError('synthetic final-file evidence close after real close')
        with mock.patch.object(c.os, 'close', side_effect=closing), \
             self.assertRaises(BaseExceptionGroup):
            self.execute_fake('success')
        self.assertEqual(len(evidence_closes), 1)
        self.assertEqual(json.loads((self.evidence / 'reader-once.final.json').read_bytes())
                         ['overall'], 'PASS')
        self.assertFalse((self.evidence / 'reader-once.finalized').exists())
        fake = self.last_fake
        with mock.patch.multiple(c, EFFECT_ENABLED=True, BASE=self.base, ATTEMPT=self.attempt,
                                 ROOT=self.root, OUT=self.output, EVIDENCE=self.evidence), \
             mock.patch.object(c, 'inspected', side_effect=fake.inspected):
            recovered = c.recover_consumed()
        self.assertEqual(recovered['finalization'], 'MISSING_OR_FAILED')
        self.assertEqual(recovered['operation'], 'UNKNOWN')

    def test_final_marker_absence_overrides_written_pass(self):
        fake, result = self.execute_fake('success')
        self.assertEqual(result['overall'], 'PASS')
        (self.evidence / 'reader-once.finalized').rmdir()
        with mock.patch.multiple(c, EFFECT_ENABLED=True, BASE=self.base, ATTEMPT=self.attempt,
                                 ROOT=self.root, OUT=self.output, EVIDENCE=self.evidence), \
             mock.patch.object(c, 'inspected', side_effect=fake.inspected):
            recovered = c.recover_consumed()
        self.assertEqual(recovered['finalization'], 'MISSING_OR_FAILED')
        self.assertEqual(recovered['operation'], 'UNKNOWN')

    def test_closed_and_committed_pass_refuses_cleanup_recovery(self):
        fake, result = self.execute_fake('success')
        self.assertEqual(result['overall'], 'PASS')
        with mock.patch.multiple(c, EFFECT_ENABLED=True, BASE=self.base, ATTEMPT=self.attempt,
                                 ROOT=self.root, OUT=self.output, EVIDENCE=self.evidence), \
             mock.patch.object(c, 'inspected', side_effect=fake.inspected), \
             self.assertRaisesRegex(ValueError, 'successful consumed attempt'):
            c.recover_consumed()
        self.assertFalse((self.evidence / 'reader-recovery-0001.json').exists())

    def test_swapped_final_attachment_cannot_commit_pass_marker(self):
        outside = self.attempt / 'outside-final'
        outside.write_bytes(b'fixed')
        original_exclusive = c.exclusive
        def swap_after_final(path, raw, **kwargs):
            result = original_exclusive(path, raw, **kwargs)
            if path.name == 'reader-once.final.json':
                path.rename(self.evidence / 'moved-final.json')
                path.symlink_to(outside)
            return result
        with mock.patch.object(c, 'exclusive', side_effect=swap_after_final), \
             self.assertRaises(OSError):
            self.execute_fake('success')
        self.assertEqual(outside.read_bytes(), b'fixed')
        self.assertFalse((self.evidence / 'reader-once.finalized').exists())

    def test_final_marker_creation_failure_leaves_written_pass_uncommitted(self):
        original_mkdir = os.mkdir
        def fail_marker(path, *args, **kwargs):
            if str(path).endswith('/reader-once.finalized'):
                raise OSError('synthetic marker failure')
            return original_mkdir(path, *args, **kwargs)
        with mock.patch.object(c.os, 'mkdir', side_effect=fail_marker), \
             self.assertRaisesRegex(OSError, 'synthetic marker failure'):
            self.execute_fake('success')
        self.assertEqual(json.loads((self.evidence / 'reader-once.final.json').read_bytes())
                         ['overall'], 'PASS')
        self.assertFalse((self.evidence / 'reader-once.finalized').exists())


if __name__ == '__main__':
    unittest.main()
