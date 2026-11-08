from pathlib import Path
import json
import os
import stat
import tempfile
import unittest
from unittest.mock import patch

import stage as S
import release as R
from anchored_copy import copy_exact, mkdir_exact
from held_stage import HeldAttempt


class StageTests(unittest.TestCase):
    def test_live_preflight_skips_private_content_hash_inventory(self):
        plan, copy, verifier = S.selected()
        self.assertEqual((len(plan['files']), copy['source_directories'],
                          copy['target_directories'],
                          copy['private_source_package_rows'],
                          len(verifier['expected_package_members'])),
                         (991, 931, 933, 37, 55))
        private = {Path(copy['source_root']) / r['path'] for r in plan['files']
                   if r['source_kind'] == 'reviewed-reader-stage' and
                   r['source_mode'] == '0600'}
        self.assertEqual(len(private), 37)
        original = S.hash_exact

        def guarded(path, digest, mode):
            self.assertNotIn(path, private)
            return original(path, digest, mode)

        with patch.object(S, 'hash_exact', side_effect=guarded):
            observed = S.preflight()
        self.assertEqual(observed['private_inventory_rows_metadata_only'], 37)
        self.assertFalse(observed['archive_body_opened'])
        self.assertFalse(Path(copy['attempt']).exists())

    def test_effect_disabled_before_attempt_or_copy(self):
        attempt = Path(S.selected()[1]['attempt'])
        with patch.object(HeldAttempt, 'copy', side_effect=AssertionError('copy called')):
            with self.assertRaisesRegex(S.Refused, 'MAPPER_STAGE_EFFECT_DISABLED'):
                S.execute()
        self.assertFalse(attempt.exists())

    def test_release_facade_unconditionally_refuses_effect(self):
        self.assertFalse(R.EFFECT_ENABLED)
        with patch.object(S, 'STAGE_EFFECT_ENABLED', True), \
             patch.object(S, 'execute', side_effect=AssertionError('stage called')):
            with self.assertRaisesRegex(S.Refused, 'MAPPER_STAGE_RELEASE_EFFECT_DISABLED'):
                R.execute_reviewed_one_shot()

    def test_consumed_attempt_refused(self):
        selected = S.selected()
        with patch.object(S, 'selected', return_value=selected), \
             patch.object(S.os.path, 'lexists', return_value=True):
            with self.assertRaisesRegex(S.Refused, 'MAPPER_ATTEMPT_CONSUMED'):
                S.preflight()

    def test_reader_inventory_and_empty_namespaces(self):
        plan, copy, _ = S.selected()
        identities = S.source_inventory(plan, copy, hash_private=False)
        self.assertEqual(len(identities), 986)
        names = set(copy['target_directory_names'])
        source = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
        mapper = 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002'
        self.assertIn(source + '/receipts', names)
        self.assertIn(mapper + '/packages', names)
        self.assertEqual(S.dir_mode(source + '/receipts'), 0o700)
        self.assertEqual(S.dir_mode(mapper + '/packages'), 0o700)
        self.assertNotIn(mapper + '/packages/0001', names)

    def test_symlink_rejected_by_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'regular').write_bytes(b'x')
            (root / 'link').symlink_to(root / 'regular')
            with self.assertRaisesRegex(S.Refused, 'NONREGULAR_ENTRY'):
                S.entries(root)

    def test_held_copy_private_and_native_modes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir, target_dir = root / 'source', root / 'target'
            mkdir_exact(source_dir, 0o700)
            mkdir_exact(target_dir, 0o700)
            for mode, raw in ((0o600, b'protected synthetic'),
                              (0o755, b'public executable synthetic')):
                source = source_dir / f'source-{mode:o}'
                target = target_dir / f'target-{mode:o}'
                source.write_bytes(raw)
                source.chmod(mode)
                copy_exact(source, target, S.sha(raw), mode, mode)
                self.assertEqual(target.read_bytes(), raw)
                self.assertEqual(stat.S_IMODE(target.stat().st_mode), mode)
            link = source_dir / 'link'
            link.symlink_to(source_dir / 'source-600')
            with self.assertRaises(ValueError):
                copy_exact(link, target_dir / 'bad', S.sha(b'protected synthetic'),
                           0o600, 0o600)

    def test_held_copy_rejects_detached_destination_ancestor(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir, target_dir = root / 'source', root / 'target'
            mkdir_exact(source_dir, 0o700)
            mkdir_exact(target_dir, 0o700)
            source = source_dir / 'input'
            source.write_bytes(b'synthetic')
            source.chmod(0o600)
            def detach():
                target_dir.rename(root / 'detached')
                target_dir.mkdir(mode=0o700)
            with self.assertRaisesRegex(ValueError, 'ancestor path was detached'):
                copy_exact(source, target_dir / 'output', S.sha(b'synthetic'),
                           0o600, 0o600, after_copy_hook=detach)
            self.assertFalse((target_dir / 'output').exists())
            self.assertEqual((root / 'detached/output').read_bytes(), b'synthetic')

    def test_post_claim_fault_retains_unknown_and_no_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            attempt = Path(temporary) / 'attempt'
            plan = {'mapper_attempt': str(attempt)}
            copy = {'attempt': str(attempt), 'destination_root': str(attempt / 'root')}
            original = HeldAttempt.claim
            def fail_after_create(claim):
                original(claim)
                raise RuntimeError('after-create fault')
            with patch.object(S, 'STAGE_EFFECT_ENABLED', True), \
                 patch.object(S, 'preflight', return_value={}), \
                 patch.object(S, 'selected', return_value=(plan, copy, {})), \
                 patch.object(S, 'source_inventory', return_value={}), \
                 patch.object(S, 'metadata', return_value=os.stat(__file__)), \
                 patch.object(HeldAttempt, 'claim', fail_after_create):
                with self.assertRaisesRegex(RuntimeError, 'after-create fault'):
                    S.execute()
            unknown = json.loads((attempt / 'stage-unknown.json').read_bytes())
            self.assertEqual(unknown['overall'], 'UNKNOWN')
            self.assertTrue(unknown['no_retry'])
            self.assertTrue(os.path.lexists(attempt))

    def test_checked_adapter_source_is_the_executed_buffer(self):
        original = Path.read_bytes
        reads = []
        expected = S.ADAPTER / 'adapter.py'
        def racing_read(path):
            if path == expected:
                reads.append(path)
                if len(reads) > 1:
                    return b'INDEPENDENT_UNVERIFIED_CODE_EXECUTED = True\n'
            return original(path)
        with patch.object(Path, 'read_bytes', racing_read):
            adapter = S._reviewed_adapter()
        self.assertEqual(len(reads), 1)
        self.assertFalse(hasattr(adapter, 'INDEPENDENT_UNVERIFIED_CODE_EXECUTED'))

    def test_failed_claim_never_marks_foreign_attempt(self):
        with tempfile.TemporaryDirectory() as temporary:
            attempt = Path(temporary) / 'attempt'
            attempt.mkdir(mode=0o700)
            (attempt / 'foreign').write_bytes(b'untouched')
            plan = {'mapper_attempt': str(attempt)}
            copy = {'attempt': str(attempt), 'destination_root': str(attempt / 'root')}
            with patch.object(S, 'STAGE_EFFECT_ENABLED', True), \
                 patch.object(S, 'preflight', return_value={}), \
                 patch.object(S, 'selected', return_value=(plan, copy, {})), \
                 patch.object(S, 'source_inventory', return_value={}), \
                 patch.object(S, 'metadata', return_value=os.stat(__file__)):
                with self.assertRaises(FileExistsError):
                    S.execute()
            self.assertEqual((attempt / 'foreign').read_bytes(), b'untouched')
            self.assertEqual({p.name for p in attempt.iterdir()}, {'foreign'})

    def test_replaced_attempt_cannot_receive_copy_or_unknown(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            attempt, detached = home / 'attempt', home / 'detached'
            plan = {'mapper_attempt': str(attempt)}
            copy = {'attempt': str(attempt), 'destination_root': str(attempt / 'root')}
            original = HeldAttempt.write
            def detach_after_marker(claim, relative, raw, *, attached=True):
                digest = original(claim, relative, raw, attached=attached)
                if relative == 'consumed.json':
                    attempt.rename(detached)
                    attempt.mkdir(mode=0o700)
                    (attempt / 'foreign').write_bytes(b'untouched')
                return digest
            with patch.object(S, 'STAGE_EFFECT_ENABLED', True), \
                 patch.object(S, 'preflight', return_value={}), \
                 patch.object(S, 'selected', return_value=(plan, copy, {})), \
                 patch.object(S, 'source_inventory', return_value={}), \
                 patch.object(S, 'metadata', return_value=os.stat(__file__)), \
                 patch.object(HeldAttempt, 'write', detach_after_marker):
                with self.assertRaisesRegex(ValueError, 'claimed attempt detached'):
                    S.execute()
            self.assertEqual({p.name for p in attempt.iterdir()}, {'foreign'})
            self.assertEqual((attempt / 'foreign').read_bytes(), b'untouched')
            self.assertTrue((detached / 'consumed.json').is_file())
            self.assertEqual(json.loads((detached / 'stage-unknown.json').read_bytes())['overall'],
                             'UNKNOWN')
            self.assertFalse((detached / 'root').exists())

    def test_held_attempt_full_synthetic_copy_and_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            source = home / 'private-input'
            source.write_bytes(b'private synthetic')
            source.chmod(0o600)
            claim = HeldAttempt(home / 'attempt')
            try:
                claim.claim()
                claim.write('consumed.json', b'claimed')
                claim.mkdir('root', 0o755)
                claim.bind_root()
                claim.mkdir('root/private', 0o700)
                claim.copy(source, 'root/private/file', S.sha(b'private synthetic'),
                           0o600, 0o600)
                self.assertEqual(claim.inventory(), ({'private/file'}, {'private'}))
                claim.file_hash('root/private/file', S.sha(b'private synthetic'), 0o600)
                claim.directory('root/private', 0o700)
                claim.attached()
            finally:
                claim.close()

    def test_replaced_root_and_subdirectory_cannot_receive_private_copy(self):
        for target in ('root', 'root/private'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                home = Path(temporary)
                source = home / 'private-input'
                source.write_bytes(b'protected synthetic')
                source.chmod(0o600)
                claim = HeldAttempt(home / 'attempt')
                try:
                    claim.claim()
                    claim.write('consumed.json', b'claimed')
                    claim.mkdir('root', 0o755)
                    claim.bind_root()
                    claim.mkdir('root/private', 0o700)
                    path = home / 'attempt' / target
                    path.rename(path.with_name('detached-' + path.name))
                    path.mkdir(mode=0o755 if target == 'root' else 0o700)
                    if target == 'root':
                        (path / 'private').mkdir(mode=0o700)
                    with self.assertRaisesRegex(ValueError,
                                                'detached or replaced'):
                        claim.copy(source, 'root/private/file',
                                   S.sha(b'protected synthetic'), 0o600, 0o600)
                    self.assertFalse((path / 'private/file' if target == 'root'
                                      else path / 'file').exists())
                    claim.write('stage-unknown.json', b'UNKNOWN', attached=False)
                    self.assertEqual((home / 'attempt/stage-unknown.json').read_bytes(),
                                     b'UNKNOWN')
                finally:
                    claim.close()


if __name__ == '__main__':
    unittest.main()
