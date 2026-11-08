"""Disposable public fixtures only; no retained Source archive is opened."""
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name('controller.py')
spec = importlib.util.spec_from_file_location('context_stage_effect_fixture', SCRIPT)
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
obs_spec = importlib.util.spec_from_file_location('context_stage_effect_observer',
                                                 SCRIPT.with_name('observer.py'))
O = importlib.util.module_from_spec(obs_spec)
obs_spec.loader.exec_module(O)


class StageFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='cal-context-stage-fixture-test-'))
        self.source = self.tmp / 'source'
        self.source.mkdir(mode=0o700)
        self.name = 'family/public.txt'
        (self.source / 'family').mkdir(mode=0o700)
        self.raw = b'public-fixture-stage-bytes\n'
        (self.source / self.name).write_bytes(self.raw)
        os.chmod(self.source / self.name, 0o600)
        self.row = {'path': self.name, 'sha256': hashlib.sha256(self.raw).hexdigest(),
                    'size': len(self.raw), 'mode': '0600',
                    'source_root': self.source, 'source_name': self.name}
        self.attempt = Path('/tmp') / ('cal-context-stage-fixture-' + self.tmp.name)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        shutil.rmtree(self.attempt, ignore_errors=True)

    def test_complete_and_one_shot(self):
        out = C.run_fixture(self.attempt, [self.row])
        self.assertEqual(out['status'], 'PASS_FIXTURE')
        self.assertEqual(out['files'], 1)
        self.assertEqual((self.attempt / 'root' / self.name).read_bytes(), self.raw)
        with self.assertRaises(C.Poisoned):
            C.run_fixture(self.attempt, [self.row])

    def test_source_digest_mismatch_retains_attempt(self):
        (self.source / self.name).write_bytes(b'x' * len(self.raw))
        with self.assertRaises(C.Poisoned):
            C.run_fixture(self.attempt, [self.row])
        self.assertTrue(self.attempt.exists())
        with self.assertRaises(C.Poisoned):
            C.run_fixture(self.attempt, [self.row])

    def test_symlink_and_fifo_refuse_without_blocking(self):
        leaf = self.source / self.name
        leaf.unlink()
        leaf.symlink_to('/etc/passwd')
        with self.assertRaises(C.Poisoned):
            C.run_fixture(self.attempt, [self.row])
        shutil.rmtree(self.attempt)
        leaf.unlink()
        os.mkfifo(leaf)
        with self.assertRaises(C.Poisoned):
            C.run_fixture(self.attempt, [self.row])

    def test_foreign_replacement_survives(self):
        def replace(phase, parent, leaf, created):
            if phase == 'precheck':
                os.rename(leaf, 'owned-detached', src_dir_fd=parent, dst_dir_fd=parent)
                fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600,
                             dir_fd=parent)
                try:
                    os.write(fd, b'foreign')
                finally:
                    os.close(fd)
        with self.assertRaises(C.Poisoned):
            C.run_fixture(self.attempt, [self.row], fault=replace)
        self.assertEqual((self.attempt / 'root' / self.name).read_bytes(), b'foreign')
        self.assertEqual((self.attempt / 'root/family/owned-detached').read_bytes(), self.raw)

    def test_ambiguous_close_attempts_every_fd_once(self):
        for failing_index in (0, 1, 2):
            fds = [os.open('/dev/null', os.O_RDONLY) for _ in range(3)]
            order = []
            def after_release(fd):
                order.append(fd)
                os.close(fd)
                if len(order) == failing_index + 1:
                    raise OSError('injected close-after-release')
            with mock.patch.object(C, '_close_once', side_effect=after_release):
                errors = C.close_all_once(fds)
            self.assertEqual(len(order), 3)
            self.assertEqual(len(set(order)), 3)
            self.assertEqual(len(errors), 1)
            self.assertEqual(fds, [])

    def test_private_row_refused_before_claim(self):
        row = self.row.copy(); row['protected'] = True
        with self.assertRaises(C.Refused):
            C.run_fixture(self.attempt, [row])
        self.assertFalse(self.attempt.exists())

    def test_forged_public_flag_cannot_open_protected_archive(self):
        forged = self.row.copy()
        forged['source_root'] = C.REAL_SOURCE
        forged['source_name'] = C.ARCHIVE
        forged['size'] = 23550300
        forged['mode'] = '0600'
        forged['sha256'] = '6d3cfc3f721b9be4fb8a1df14d4f43214709887213eaeae543927f214fdb9323'
        # No source or attempt open of any kind is allowed in this negative case.
        with mock.patch.object(C.os, 'open', side_effect=AssertionError('opened')):
            with self.assertRaises(C.Refused):
                C.run_fixture(self.attempt, [forged])
            with self.assertRaises(C.Refused):
                C.copy_one(forged, self.attempt / 'root')
            with self.assertRaises(C.Refused):
                C.copy_one(forged, self.attempt / 'root', allow_protected=True)
        self.assertFalse(self.attempt.exists())

    def test_archive_named_fixture_source_refused_before_open(self):
        forged = self.row.copy()
        forged['source_name'] = C.ARCHIVE
        with mock.patch.object(C.os, 'open', side_effect=AssertionError('opened')):
            with self.assertRaises(C.Refused):
                C.run_fixture(self.attempt, [forged])
        self.assertFalse(self.attempt.exists())

    def test_real_family_root_rejected_even_for_public_named_row(self):
        forged = self.row.copy()
        forged['source_root'] = C.REAL_SOURCE
        with mock.patch.object(C.os, 'open', side_effect=AssertionError('opened')):
            with self.assertRaises(C.Refused):
                C.run_fixture(self.attempt, [forged])
            with self.assertRaises(C.Refused):
                C.copy_one(forged, self.attempt / 'root')
        self.assertFalse(self.attempt.exists())

    def test_fixture_symlink_root_refused_before_attempt_claim(self):
        self.source.rename(self.tmp / 'source-real')
        self.source.symlink_to(self.tmp / 'source-real', target_is_directory=True)
        with self.assertRaises((C.Refused, OSError)):
            C.run_fixture(self.attempt, [self.row])
        self.assertFalse(self.attempt.exists())

    def _assert_source_swap_refused_before_leaf_open(self, direct):
        (self.source / self.name).write_bytes(b'x' * len(self.raw))
        replacement = self.tmp / 'replacement'
        (replacement / 'family').mkdir(parents=True, mode=0o700)
        (replacement / self.name).write_bytes(self.raw)
        os.chmod(replacement, 0o700)
        os.chmod(replacement / self.name, 0o600)
        old_open = C.os.open
        leaf_opens = []
        old_core = C._copy_one_core
        swapped = []

        def tracked_open(path, *args, **kwargs):
            if path == 'public.txt':
                leaf_opens.append(kwargs.get('dir_fd'))
            return old_open(path, *args, **kwargs)

        def swap_then_copy(*args, **kwargs):
            if not swapped:
                self.source.rename(self.tmp / 'original-detached')
                replacement.rename(self.source)
                swapped.append(True)
            return old_core(*args, **kwargs)

        with mock.patch.object(C.os, 'open', side_effect=tracked_open), \
             mock.patch.object(C, '_copy_one_core', side_effect=swap_then_copy):
            with self.assertRaises(C.Poisoned):
                if direct:
                    C.copy_one(self.row, self.attempt / 'root')
                else:
                    C.run_fixture(self.attempt, [self.row])
        self.assertEqual(leaf_opens, [], 'detached source leaf must never be opened')
        self.assertEqual((self.source / self.name).read_bytes(), self.raw)
        self.assertEqual((self.tmp / 'original-detached' / self.name).read_bytes(),
                         b'x' * len(self.raw))
        self.assertEqual(self.attempt.exists(), not direct)

    def test_run_fixture_root_swap_refused_before_source_leaf_open(self):
        self._assert_source_swap_refused_before_leaf_open(direct=False)

    def test_direct_copy_root_swap_refused_before_source_leaf_open(self):
        with mock.patch.object(C.os, 'open', side_effect=AssertionError('opened')):
            with self.assertRaises(C.Refused):
                C.copy_one(self.row, self.attempt / 'root')
        self.assertFalse(self.attempt.exists())

    def test_direct_copy_out_of_envelope_target_refused_before_write(self):
        unrelated = self.tmp / 'writable-unrelated-target'
        (unrelated / 'family').mkdir(parents=True, mode=0o700)
        with mock.patch.object(C.os, 'open', side_effect=AssertionError('opened')):
            for target in (unrelated, C.REPO, C.REAL_SOURCE):
                with self.assertRaises(C.Refused):
                    C.copy_one(self.row, target)
        self.assertFalse((unrelated / self.name).exists())
        self.assertFalse(self.attempt.exists())

    def test_core_refuses_unheld_out_of_envelope_target(self):
        unrelated = self.tmp / 'writable-unrelated-target'
        (unrelated / 'family').mkdir(parents=True, mode=0o700)
        custody = C.acquire_fixture_source(self.source)
        try:
            with mock.patch.object(C.os, 'open', side_effect=AssertionError('opened')):
                with self.assertRaises(C.Refused):
                    C._copy_one_core(self.row, unrelated, custody=custody)
        finally:
            self.assertEqual(custody.close(), [])
        self.assertFalse((unrelated / self.name).exists())

    def test_claimed_target_swap_refused_before_write(self):
        old_create = C.create_dirs
        swapped = []
        def replace_target(stage, names, **kwargs):
            if not swapped:
                self.attempt.rename(self.tmp / 'detached-attempt')
                (self.attempt / 'root').mkdir(parents=True, mode=0o700)
                swapped.append(True)
            return old_create(stage, names, **kwargs)
        with mock.patch.object(C, 'create_dirs', side_effect=replace_target):
            with self.assertRaises(C.Poisoned):
                C.run_fixture(self.attempt, [self.row])
        self.assertFalse((self.attempt / 'root' / self.name).exists())
        self.assertFalse((self.tmp / 'detached-attempt/root' / self.name).exists())

    def test_move_after_created_is_unknown_and_one_shot(self):
        moved = []
        def detach(phase, _parent, _leaf, _created):
            if phase == 'created' and not moved:
                self.attempt.rename(self.tmp / 'detached-attempt')
                moved.append(True)
        with self.assertRaises(C.Poisoned) as caught:
            C.run_fixture(self.attempt, [self.row], fault=detach)
        failure = caught.exception
        detached = self.tmp / 'detached-attempt'
        self.assertEqual(failure.outcome, 'UNKNOWN')
        self.assertEqual(failure.disposition, 'RETAIN_OWNED_INODE_NO_NAME_UNLINK')
        self.assertFalse(failure.retry_allowed)
        self.assertEqual(failure.owned_inode, C.inode(detached.stat()))
        self.assertIsNone(failure.observed_name_inode)
        self.assertEqual((detached / 'root' / self.name).read_bytes(), self.raw)
        self.assertTrue(Path(failure.claim_marker_path).exists())
        self.assertFalse(self.attempt.exists())
        with self.assertRaises(C.Poisoned):
            C.run_fixture(self.attempt, [self.row])
        self.assertFalse(self.attempt.exists())

    def test_move_between_attachment_check_and_create_is_unknown(self):
        old_open = C.os.open
        moved = []
        def rename_at_create(path, flags, *args, **kwargs):
            if path == 'public.txt' and flags & os.O_CREAT and not moved:
                self.attempt.rename(self.tmp / 'detached-attempt')
                moved.append(True)
            return old_open(path, flags, *args, **kwargs)
        with mock.patch.object(C.os, 'open', side_effect=rename_at_create):
            with self.assertRaises(C.Poisoned) as caught:
                C.run_fixture(self.attempt, [self.row])
        failure = caught.exception
        detached = self.tmp / 'detached-attempt'
        self.assertEqual(failure.outcome, 'UNKNOWN')
        self.assertEqual(failure.owned_inode, C.inode(detached.stat()))
        self.assertEqual((detached / 'root' / self.name).read_bytes(), self.raw)
        self.assertTrue(Path(failure.claim_marker_path).exists())
        self.assertFalse(self.attempt.exists())

    def test_root_detachment_during_copy_poisoned_after_held_read(self):
        replacement = self.tmp / 'replacement'
        (replacement / 'family').mkdir(parents=True, mode=0o700)
        (replacement / self.name).write_bytes(self.raw)
        os.chmod(replacement, 0o700)
        os.chmod(replacement / self.name, 0o600)
        swapped = []
        def detach(phase, _parent, _leaf, _created):
            if phase == 'created' and not swapped:
                self.source.rename(self.tmp / 'original-detached')
                replacement.rename(self.source)
                swapped.append(True)
        with self.assertRaises(C.Poisoned):
            C.run_fixture(self.attempt, [self.row], fault=detach)
        self.assertTrue(self.attempt.exists())
        self.assertEqual((self.attempt / 'root' / self.name).read_bytes(), self.raw)
        with self.assertRaises(C.Poisoned):
            C.run_fixture(self.attempt, [self.row])

    def test_real_effect_and_launch_refused(self):
        with self.assertRaises(C.Refused):
            C.real_stage()
        with self.assertRaises(C.Refused):
            C.launch_context()
        self.assertFalse(C.REAL_EFFECT_ENABLED)

    def test_selected_metadata_no_private_body(self):
        selected, rows = C.closed_selection()
        self.assertEqual(len(rows), 1570)
        self.assertEqual(sum(x.get('protected', False) for x in rows), 1)
        self.assertEqual(selected['protected_archive_metadata']['body'],
                         'UNOPENED_UNCOPIED')

    def test_trusted_profile_binds_disposable_archive_metadata_only(self):
        profile = json.loads(SCRIPT.with_name('trusted-local-profile.json').read_bytes())
        selected, _ = C.closed_selection()
        archive = profile['eventual_local_archive']
        self.assertEqual(archive['path'], C.ARCHIVE)
        self.assertEqual(archive['sha256'],
                         selected['protected_archive_metadata']['sha256'])
        self.assertEqual(archive['size'], 23550300)
        self.assertEqual(archive['body_this_unit'], 'UNOPENED_UNCOPIED')
        self.assertEqual(profile['adversarial_same_uid_write_envelope'], 'NOT_CLAIMED')
        self.assertEqual(profile['real_protected_qualification'],
                         'SEPARATE_UNSATISFIED_G01_G02')

    def test_public_preflight_and_external_os_receipt(self):
        _, rows = C.closed_selection()
        bound = C.preflight_public(rows)
        self.assertEqual(sum(x['size'] is None or x['mode'] is None for x in bound), 0)
        self.assertEqual(sum(x.get('protected', False) for x in bound), 1)
        native = C.native_binding(C.closed_selection()[0])
        self.assertEqual(native['size'], 20243600)
        self.attempt.mkdir(mode=0o700)
        receipt = self.attempt / 'observation.json'
        argv = [O.sys.executable, '-B', str(O.CONTROLLER), '--preflight-public']
        result = O.observe(receipt, argv)
        self.assertEqual(result['os_exit_code'], 0)
        self.assertEqual(json.loads(receipt.read_bytes())['argv'], argv)
        with self.assertRaises(FileExistsError):
            O.observe(receipt, argv)
        with self.assertRaises(ValueError):
            O.observe(self.attempt / 'other.json',
                      [O.sys.executable, '-B', str(O.CONTROLLER), '--real-stage'])


if __name__ == '__main__':
    unittest.main()
