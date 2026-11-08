"""Synthetic-only causal tests. No private stage bytes or Docker calls."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock
import subprocess
import json

import controller
import docker_protocol
import mapper_once


CID = 'a' * 64
LABEL = 'b' * 32
NAME = 'cal-mapper-only-20261020-0001-controller4'


class FakeDocker:
    def __init__(self, image: str, label: str, *, wrong_exit=False,
                 wrong_label=False, retained=False, wrong_id=False,
                 create_timeout=False, malformed_cid=False, collision=False,
                 daemon_unavailable=False, remove_error=False, wrong_image=False):
        self.image, self.label = image, label
        self.wrong_exit, self.wrong_label = wrong_exit, wrong_label
        self.retained, self.wrong_id = retained, wrong_id
        self.create_timeout, self.malformed_cid = create_timeout, malformed_cid
        self.collision, self.daemon_unavailable = collision, daemon_unavailable
        self.remove_error, self.wrong_image = remove_error, wrong_image
        self.created = False
        self.started = False
        self.removed = False
        self.force_used = False
        self.create_calls = 0

    def create(self, args, *, deadline):
        self.create_calls += 1
        self.created = True
        if self.create_timeout:
            raise TimeoutError('create client timed out after daemon acceptance')
        if self.malformed_cid:
            return 'malformed'
        return CID

    def inspect(self, cid, *, deadline):
        return {'Id': 'c' * 64 if self.wrong_id else cid,
                'Name': '/' + NAME,
                'Image': '0' * 64 if self.wrong_image else self.image,
                'Config': {'Image': '0' * 64 if self.wrong_image else self.image,
                           'Labels': {'cal.mapper.attempt':
                                      'bad' if self.wrong_label else self.label}},
                'State': {'Status': 'exited' if self.started else 'created',
                          'ExitCode': 1 if self.wrong_exit else 0}}

    def lookup_name(self, name, *, deadline):
        if self.daemon_unavailable:
            raise ConnectionError('Cannot connect to Docker daemon')
        if self.collision:
            return [self.inspect(CID, deadline=deadline)]
        if self.created and not self.removed:
            return [self.inspect(CID, deadline=deadline)]
        return []

    def start_wait(self, cid, *, deadline):
        self.started = True
        return 1 if self.wrong_exit else 0

    def remove(self, cid, *, force, deadline):
        if self.remove_error:
            raise OSError('synthetic remove failed')
        self.removed = True
        self.force_used = force

    def absent(self, cid, *, deadline):
        if self.daemon_unavailable:
            raise ConnectionError('Cannot connect to Docker daemon')
        return self.removed and not self.retained


class ControllerTests(unittest.TestCase):
    def test_exact_preflight_holds_before_private_effect(self):
        result = controller.preflight()
        self.assertEqual(result['result'], 'HOLD_EFFECT_DISABLED_PRIVATE_PREDISPATCH')
        self.assertEqual(result['reader_predecessor'], 'PASS_REVIEWED_READER_PREDECESSOR')
        self.assertEqual(result['native_image_load'], 'PASS_LOAD_ONLY')
        self.assertFalse(result['archive_body_opened'])
        self.assertFalse(Path(result['attempt']).exists())
        with self.assertRaisesRegex(ValueError, 'effect disabled'):
            controller.execute_reviewed_one_shot()
        with self.assertRaisesRegex(ValueError, 'effect disabled'):
            mapper_once.execute(mapper_once.SOURCE_SHA)
        with self.assertRaisesRegex(ValueError, 'private copy disabled'):
            controller.prepare_exact_attempt(controller.trusted_selection(),
                                             controller.exact_stage_plan(), '0' * 64)
        with self.assertRaisesRegex(ValueError, 'output inspection disabled'):
            controller.verify_mapped_output(controller.trusted_selection())

    def test_archive_size_pin_is_causal_without_archive_read(self):
        selection = controller.trusted_selection()
        info = SimpleNamespace(st_mode=0o100600, st_uid=1000, st_gid=1000,
                               st_nlink=1, st_size=23550300)
        controller.selected_archive_metadata(info, selection)
        changed = SimpleNamespace(**{**vars(info), 'st_size': 23550299})
        with self.assertRaisesRegex(ValueError, 'metadata differs'):
            controller.selected_archive_metadata(changed, selection)

    def test_fake_docker_reconciliation_and_causal_failures(self):
        args = controller.docker_create_argv(controller.trusted_selection(), label=LABEL)
        docker_protocol.exact_create_argv(args, LABEL)
        with tempfile.TemporaryDirectory(prefix='cal-mapper-docker-fake-') as temp:
            fake = FakeDocker(controller.IMAGE, LABEL)
            result = docker_protocol.reconcile_once(
                fake, args, image=controller.IMAGE,
                label=LABEL, name=NAME, evidence_dir=Path(temp))
            self.assertEqual(result['overall'], 'PASS')
            self.assertTrue(result['container_absent'] and fake.removed)
            self.assertFalse(fake.force_used)
            self.assertEqual(json.loads((Path(temp) / 'terminal.json').read_text())['overall'], 'PASS')
        for options in ({'wrong_exit': True}, {'wrong_label': True},
                        {'retained': True}, {'wrong_id': True},
                        {'wrong_image': True}, {'create_timeout': True},
                        {'malformed_cid': True}, {'collision': True},
                        {'daemon_unavailable': True}, {'remove_error': True},
                        {'wrong_exit': True, 'remove_error': True}):
            with self.subTest(options=options):
                with tempfile.TemporaryDirectory(prefix='cal-mapper-docker-fake-') as temp:
                    failed = FakeDocker(controller.IMAGE, LABEL, **options)
                    with self.assertRaises(docker_protocol.OneShotUnknown) as caught:
                        docker_protocol.reconcile_once(
                            failed, args, image=controller.IMAGE,
                            label=LABEL, name=NAME, evidence_dir=Path(temp))
                    evidence = json.loads((Path(temp) / 'terminal.json').read_text())
                    self.assertEqual(evidence['overall'], 'UNKNOWN')
                    self.assertFalse(evidence['retry_allowed'])
                    self.assertEqual(failed.create_calls, 0 if
                                     options.get('collision') or options.get('daemon_unavailable') else 1)
                    if options.get('create_timeout') or options.get('malformed_cid'):
                        self.assertTrue(failed.removed and failed.force_used)
                        self.assertTrue(evidence['container_absent'])
                    if options.get('collision'):
                        self.assertEqual(evidence['observed_object'][0]['id'], CID)
                        self.assertFalse(evidence['cleanup_attempted'])
                    if options.get('wrong_exit') and options.get('remove_error'):
                        self.assertIsNotNone(caught.exception.cleanup)
                        self.assertIn('synthetic remove failed', str(caught.exception))
                        self.assertIsNotNone(evidence['cleanup_error'])

    def test_closed_docker_vector_rejects_injected_privilege_and_mount_drift(self):
        args = controller.docker_create_argv(controller.trusted_selection(), label=LABEL)
        for token in ('--privileged', '--pid=host',
                      '--security-opt=seccomp=unconfined', '--device=/dev/kvm'):
            with self.subTest(token=token):
                changed = args[:]
                changed.insert(changed.index('--entrypoint'), token)
                with self.assertRaises(ValueError):
                    docker_protocol.exact_create_argv(changed, LABEL)
        for old, new in (('1000:1000', '20001:20001'),
                         ('--pids-limit', '--pid-limit'),
                         ('/attempt/scratch:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000',
                          '/attempt/scratch:rw,size=512m'),
                         (',dst=/attempt/input,readonly', ',dst=/attempt/input'),
                         ('src=/tmp/cal-mapper-only-dev-20261020-0001-controller4/root',
                          'src=/tmp/foreign/root')):
            with self.subTest(old=old):
                changed = [part.replace(old, new) for part in args]
                with self.assertRaises(ValueError):
                    docker_protocol.exact_create_argv(changed, LABEL)

    def test_daemon_unavailable_is_not_absence(self):
        adapter = docker_protocol.SubprocessDocker()
        args = ['/usr/bin/docker', 'inspect', '--type', 'container', CID]
        unavailable = subprocess.CompletedProcess(args, 1, b'',
                                                  b'Cannot connect to Docker daemon\n')
        with mock.patch.object(adapter, '_run', return_value=unavailable):
            with self.assertRaises(docker_protocol.DockerCommandError) as caught:
                adapter.absent(CID, deadline=10**20)
        self.assertEqual(caught.exception.returncode, 1)
        self.assertIn(b'Cannot connect', caught.exception.stderr)
        missing = subprocess.CompletedProcess(args, 1, b'',
                                              ('Error: No such object: ' + CID + '\n').encode())
        with mock.patch.object(adapter, '_run', return_value=missing):
            self.assertTrue(adapter.absent(CID, deadline=10**20))

    def test_global_deadline_stops_dispatch_and_uses_bounded_recovery(self):
        args = controller.docker_create_argv(controller.trusted_selection(), label=LABEL)
        now = [0.0]
        fake = FakeDocker(controller.IMAGE, LABEL)
        original_create = fake.create
        def slow_create(args, *, deadline):
            result = original_create(args, deadline=deadline)
            now[0] = 181.0
            return result
        fake.create = slow_create
        with tempfile.TemporaryDirectory(prefix='cal-mapper-deadline-fake-') as temp:
            with self.assertRaises(docker_protocol.OneShotUnknown) as caught:
                docker_protocol.reconcile_once(
                    fake, args, image=controller.IMAGE, label=LABEL,
                    name=NAME, evidence_dir=Path(temp), clock=lambda: now[0])
            self.assertIn('deadline elapsed', str(caught.exception.primary))
            self.assertTrue(fake.removed and fake.force_used)
            self.assertTrue(caught.exception.evidence['container_absent'])
            self.assertFalse(caught.exception.evidence['retry_allowed'])

    def test_durable_evidence_rejects_symlinked_or_open_parent(self):
        with tempfile.TemporaryDirectory(prefix='cal-mapper-evidence-fake-') as temp:
            base = Path(temp)
            private = base / 'private'
            private.mkdir(mode=0o700)
            alias = base / 'alias'
            alias.symlink_to(private, target_is_directory=True)
            with self.assertRaises(docker_protocol.EvidenceAttachmentUnknown):
                docker_protocol.durable_json(alias / 'forbidden.json', {'x': 1})
            self.assertFalse((private / 'forbidden.json').exists())
            private.chmod(0o755)
            with self.assertRaisesRegex(docker_protocol.EvidenceAttachmentUnknown,
                                        'owner/group/mode differs'):
                docker_protocol.durable_json(private / 'forbidden.json', {'x': 1})
            self.assertFalse((private / 'forbidden.json').exists())

    def test_real_directory_rename_during_receipt_write_is_unknown(self):
        with tempfile.TemporaryDirectory(prefix='cal-mapper-evidence-race-') as temp:
            base = Path(temp)
            selected = base / 'selected'
            moved = base / 'moved'
            selected.mkdir(mode=0o700)
            original_write = os.write
            changed = [False]
            def rename_after_write(fd, data):
                count = original_write(fd, data)
                if not changed[0]:
                    changed[0] = True
                    selected.rename(moved)
                    selected.mkdir(mode=0o700)
                return count
            with mock.patch.object(docker_protocol.os, 'write', side_effect=rename_after_write):
                with self.assertRaises(docker_protocol.EvidenceAttachmentUnknown) as caught:
                    docker_protocol.durable_json(selected / 'terminal.json', {'overall': 'UNKNOWN'})
            self.assertEqual(caught.exception.overall, 'UNKNOWN')
            self.assertFalse((selected / 'terminal.json').exists())
            self.assertTrue((moved / 'terminal.json').is_file())
            self.assertIn('ancestor pathname custody changed', str(caught.exception))

    def test_real_terminal_rename_never_returns_fake_docker_pass(self):
        args = controller.docker_create_argv(controller.trusted_selection(), label=LABEL)
        fake = FakeDocker(controller.IMAGE, LABEL)
        with tempfile.TemporaryDirectory(prefix='cal-mapper-terminal-race-') as temp:
            base = Path(temp)
            selected = base / 'selected'
            moved = base / 'moved'
            selected.mkdir(mode=0o700)
            original_durable = docker_protocol.durable_json
            original_write = os.write
            def hooked_durable(path, value):
                if path.name != 'terminal.json':
                    return original_durable(path, value)
                changed = [False]
                def rename_after_write(fd, data):
                    count = original_write(fd, data)
                    if not changed[0]:
                        changed[0] = True
                        selected.rename(moved)
                        selected.mkdir(mode=0o700)
                    return count
                with mock.patch.object(docker_protocol.os, 'write', side_effect=rename_after_write):
                    return original_durable(path, value)
            with mock.patch.object(docker_protocol, 'durable_json', side_effect=hooked_durable):
                with self.assertRaises(docker_protocol.OneShotUnknown) as caught:
                    docker_protocol.reconcile_once(fake, args, image=controller.IMAGE,
                                                   label=LABEL, name=NAME,
                                                   evidence_dir=selected)
            self.assertEqual(caught.exception.evidence['overall'], 'UNKNOWN')
            self.assertEqual(caught.exception.evidence['terminal_attachment'], 'UNKNOWN')
            self.assertFalse(caught.exception.evidence['retry_allowed'])
            self.assertTrue(fake.removed)
            self.assertFalse((selected / 'terminal.json').exists())
            self.assertTrue((moved / 'precreate.json').is_file())
            self.assertTrue((moved / 'terminal.json').is_file())

    def test_real_midwrite_evidence_custody_matrix_is_unknown(self):
        def exercise(change):
            with tempfile.TemporaryDirectory(prefix='cal-mapper-custody-race-') as temp:
                outer = Path(temp)
                selected = outer / 'selected'
                moved = outer / 'moved'
                selected.mkdir(mode=0o700)
                original_write = os.write
                changed = [False]
                def injected(fd, data):
                    count = original_write(fd, data)
                    if not changed[0]:
                        changed[0] = True
                        change(outer, selected, moved)
                    return count
                with mock.patch.object(docker_protocol.os, 'write', side_effect=injected):
                    with self.assertRaises(docker_protocol.EvidenceAttachmentUnknown) as caught:
                        docker_protocol.durable_json(selected / 'terminal.json',
                                                     {'overall': 'UNKNOWN'})
                self.assertTrue(changed[0])
                self.assertEqual(caught.exception.overall, 'UNKNOWN')
        def parent_mode(outer, selected, moved):
            selected.chmod(0o755)
        def ancestor_mode(outer, selected, moved):
            outer.chmod(0o755)
        def leaf_mode(outer, selected, moved):
            (selected / 'terminal.json').chmod(0o644)
        def leaf_replace(outer, selected, moved):
            leaf = selected / 'terminal.json'
            leaf.unlink()
            leaf.write_bytes(b'synthetic-replacement')
            leaf.chmod(0o600)
        def symlink_swap(outer, selected, moved):
            selected.rename(moved)
            selected.symlink_to(moved, target_is_directory=True)
        for name, change in (('parent chmod 0700 to 0755', parent_mode),
                             ('ancestor chmod 0700 to 0755', ancestor_mode),
                             ('leaf chmod 0600 to 0644', leaf_mode),
                             ('leaf inode replacement', leaf_replace),
                             ('directory symlink swap', symlink_swap)):
            with self.subTest(name=name):
                exercise(change)

    def test_verified_precreate_anchor_rejects_postwrite_mode_drift(self):
        with tempfile.TemporaryDirectory(prefix='cal-mapper-anchor-mode-') as temp:
            selected = Path(temp) / 'selected'
            selected.mkdir(mode=0o700)
            anchor = docker_protocol.durable_json(selected / 'precreate.json',
                                                  {'phase': 'BEFORE_CREATE'})
            docker_protocol.verify_evidence_anchor(anchor)
            selected.chmod(0o755)
            with self.assertRaisesRegex(docker_protocol.EvidenceAttachmentUnknown,
                                        'custody changed|owner/group/mode differs'):
                docker_protocol.verify_evidence_anchor(anchor)

    def test_synthetic_uid_gid_drift_is_causal_without_chown(self):
        for field in ('st_uid', 'st_gid'):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory(prefix='cal-mapper-owner-drift-') as temp:
                    selected = Path(temp) / 'selected'
                    selected.mkdir(mode=0o700)
                    anchor = docker_protocol.durable_json(selected / 'precreate.json',
                                                          {'phase': 'BEFORE_CREATE'})
                    selected_inode = selected.stat().st_ino
                    original_fstat = os.fstat
                    # A stat-result substitution exercises owner drift without
                    # changing any real host UID/GID or requiring root.
                    def drifted_fstat(fd):
                        actual = original_fstat(fd)
                        if actual.st_ino == selected_inode and actual.st_dev == selected.stat().st_dev:
                            values = list(actual[:10])
                            values[4 if field == 'st_uid' else 5] += 1
                            return os.stat_result(values)
                        return actual
                    with mock.patch.object(docker_protocol.os, 'fstat', side_effect=drifted_fstat):
                        with self.assertRaisesRegex(docker_protocol.EvidenceAttachmentUnknown,
                                                    'custody changed|owner/group/mode differs'):
                            docker_protocol.verify_evidence_anchor(anchor)

    def test_synthetic_midwrite_uid_gid_drift_is_unknown_without_chown(self):
        for field in ('st_uid', 'st_gid'):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory(prefix='cal-mapper-owner-write-') as temp:
                    selected = Path(temp) / 'selected'
                    selected.mkdir(mode=0o700)
                    selected_info = selected.stat()
                    original_fstat, original_write = os.fstat, os.write
                    changed = [False]
                    def drifted_fstat(fd):
                        actual = original_fstat(fd)
                        if changed[0] and actual.st_ino == selected_info.st_ino and \
                           actual.st_dev == selected_info.st_dev:
                            values = list(actual[:10])
                            values[4 if field == 'st_uid' else 5] += 1
                            return os.stat_result(values)
                        return actual
                    def mark_after_write(fd, data):
                        count = original_write(fd, data)
                        changed[0] = True
                        return count
                    with mock.patch.object(docker_protocol.os, 'fstat', side_effect=drifted_fstat), \
                         mock.patch.object(docker_protocol.os, 'write', side_effect=mark_after_write):
                        with self.assertRaisesRegex(docker_protocol.EvidenceAttachmentUnknown,
                                                    'custody changed|owner/group/mode differs'):
                            docker_protocol.durable_json(selected / 'terminal.json',
                                                         {'overall': 'UNKNOWN'})
                    self.assertTrue(changed[0])

    def test_synthetic_held_copy_and_inventory_negatives(self):
        with tempfile.TemporaryDirectory(prefix='cal-mapper-controller-test-') as temp:
            base = Path(temp)
            source = base / 'source'
            source.mkdir(mode=0o755)
            first = source / 'a'
            first.mkdir(mode=0o755)
            public = first / 'public.json'
            private = first / 'private.bin'
            public.write_bytes(b'{"synthetic":true}\n')
            private.write_bytes(b'synthetic-private')
            public.chmod(0o444)
            private.chmod(0o600)
            rows = [{'path': 'a/' + path.name,
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'target_mode': '0444' if path == public else '0600'}
                    for path in (public, private)]
            target = base / 'target'
            controller.copy_rows_nofollow(source, target, rows, {'a'})
            self.assertEqual((target / 'a/public.json').read_bytes(), public.read_bytes())
            self.assertEqual((target / 'a/private.bin').read_bytes(), private.read_bytes())
            self.assertEqual((target / 'a/private.bin').stat().st_mode & 0o777, 0o600)
            with self.assertRaises(ValueError):
                controller.copy_rows_nofollow(source, base / 'duplicate', rows, {'a', 'z'})
            public.chmod(0o644)
            with self.assertRaises(ValueError):
                controller.copy_rows_nofollow(source, base / 'wrong-mode', rows, {'a'})
            public.chmod(0o444)
            public.unlink()
            public.symlink_to(private)
            with self.assertRaises(ValueError):
                controller.copy_rows_nofollow(source, base / 'symlink', rows, {'a'})

    def test_entrypoint_topology_causal_negatives(self):
        base = dict(st_mode=0o40700, st_uid=1000, st_gid=1000, st_dev=2)
        package = SimpleNamespace(**base)
        scratch = SimpleNamespace(**{**base, 'st_dev': 3})
        archive = SimpleNamespace(st_mode=0o100600, st_uid=1000, st_gid=1000)
        native = SimpleNamespace(st_mode=0o100755, st_uid=1000, st_gid=1000)
        mountinfo = b'0 0 0:1 / /attempt/scratch rw - tmpfs tmpfs rw\n'
        def selected(**kwargs):
            options = {'uid': 1000, 'gid': 1000, 'pid': 1,
                       'env': {'TMPDIR': '/attempt/scratch'},
                       'package_stat': package, 'scratch_stat': scratch,
                       'archive_stat': archive, 'native_stat': native,
                       'root_device': 2, 'scratch_mountinfo': mountinfo}
            options.update(kwargs)
            mapper_once.selected_topology(**options)
        selected()
        for options in ({'uid': 20001}, {'pid': 2}, {'env': {'TMPDIR': '/tmp'}},
                        {'package_stat': SimpleNamespace(**{**base, 'st_mode': 0o40755})},
                        {'scratch_stat': SimpleNamespace(**base)},
                        {'archive_stat': SimpleNamespace(st_mode=0o100644, st_uid=1000, st_gid=1000)},
                        {'mountinfo': b''}):
            with self.subTest(options=options):
                if 'mountinfo' in options:
                    options['scratch_mountinfo'] = options.pop('mountinfo')
                with self.assertRaises(ValueError):
                    selected(**options)

    def test_synthetic_native_attachment_exact_hash_and_no_replace(self):
        with tempfile.TemporaryDirectory(prefix='cal-mapper-native-test-') as temp:
            destination = Path(temp) / 'native'
            raw = b'synthetic-elf-placeholder'
            digest = hashlib.sha256(raw).hexdigest()
            controller.write_executable_nofollow(destination, raw, digest)
            self.assertEqual(destination.read_bytes(), raw)
            self.assertEqual(destination.stat().st_mode & 0o777, 0o755)
            with self.assertRaises(FileExistsError):
                controller.write_executable_nofollow(destination, raw, digest)
            with self.assertRaisesRegex(ValueError, 'bytes differ'):
                controller.write_executable_nofollow(Path(temp) / 'wrong', raw,
                                                     '0' * 64)

    def test_exact_public_mapper_projection_has_five_files(self):
        projected = controller.selected_projected_files(controller.trusted_selection())
        self.assertEqual(len(projected), 5)
        self.assertEqual(projected[controller.MAPPER + '/source-manifest.json'],
                         '0bd6696a1e33750bca01cdeae65d3a5ae977b433c0e0b608009422161b3c1358')


if __name__ == '__main__':
    unittest.main()
