"""Inert Reader construction/refusal tests; no cold-open or Docker call."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

import audit_stage
import anchored_copy
import controller_contract
import prepare_reader
import reader_once
import stage_reader


class FreshReaderInertTests(unittest.TestCase):
    def test_positive_retained_source_and_exact_projection(self):
        result = audit_stage.audit()
        self.assertEqual(result['result'], 'PASS_INERT')
        self.assertFalse(result['archive_current_bytes_checked'])
        self.assertEqual(result['selected_source_static_files'], 941)
        self.assertEqual(result['selected_package_files'], 37)
        self.assertEqual(result['projected_reader_modules'], 7)

    def test_exact_preimage_and_unique_producer_namespace(self):
        for name, expected in prepare_reader.ROLE.items():
            raw = (prepare_reader.REPO / prepare_reader.OLD / name).read_bytes()
            self.assertEqual(prepare_reader.sha(raw), expected)
            projected = (prepare_reader.HERE / 'generated' / prepare_reader.NEW / name).read_bytes()
            self.assertEqual(prepare_reader.projection(name, raw), projected)
        base = (prepare_reader.HERE / 'generated' / prepare_reader.NEW / 'base.py').read_text()
        self.assertIn(prepare_reader.NEW_MODULE, base)
        self.assertIn(prepare_reader.NEW_PRODUCER, base)
        self.assertNotIn(prepare_reader.OLD_MODULE, base)
        self.assertNotIn(prepare_reader.OLD_PRODUCER, base)

    def test_wrong_preimage_rejected(self):
        raw = (prepare_reader.REPO / prepare_reader.OLD / 'base.py').read_bytes()
        with self.assertRaisesRegex(ValueError, 'preimage differs'):
            prepare_reader.projection('base.py', raw + b'\n')

    def test_coherent_selection_substitution_rejected(self):
        selected = json.loads((prepare_reader.HERE / 'selection.json').read_bytes())
        selected['source_manifest_binding']['path'] = 'product/lab/release-candidates/v1/interface/another-valid-source/source-manifest.json'
        selected['source_manifest_binding']['sha256'] = '0' * 64
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'selection.json'
            path.write_bytes(prepare_reader.encoded(selected))
            with self.assertRaisesRegex(ValueError, 'trusted Reader selection changed'):
                audit_stage.audit(selection_path=path)

    def test_projected_module_mutation_rejected(self):
        original = prepare_reader.HERE / 'generated' / prepare_reader.NEW
        with tempfile.TemporaryDirectory() as temp:
            role = Path(temp)
            for name in (*prepare_reader.ROLE, 'source-manifest.json'):
                (role / name).write_bytes((original / name).read_bytes())
            (role / 'base.py').write_bytes((role / 'base.py').read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'Reader projection differs'):
                audit_stage.audit(role_root=role)

    def test_period_boundaries_and_expiration(self):
        period = {'not_before': '2026-10-20T08:20:00+00:00',
                  'expires_at': '2026-10-21T08:20:00+00:00'}
        reader_once.period_current(period, dt.datetime.fromisoformat(period['not_before']))
        reader_once.period_current(period, dt.datetime.fromisoformat(period['expires_at']) - dt.timedelta(microseconds=1))
        for now in (dt.datetime(2026, 10, 20, 8, 19, 59, tzinfo=dt.timezone.utc),
                    dt.datetime.fromisoformat(period['expires_at'])):
            with self.assertRaisesRegex(ValueError, 'not current'):
                reader_once.period_current(period, now)
        with self.assertRaisesRegex(ValueError, 'not current'):
            reader_once.period_current({'not_before': period['not_before'],
                'expires_at': '2026-10-22T08:20:00+00:00'},
                dt.datetime(2026, 10, 20, 9, tzinfo=dt.timezone.utc))

    def test_expired_selection_refused_before_stage_reads(self):
        now = dt.datetime(2026, 10, 21, 8, 20, tzinfo=dt.timezone.utc)
        with self.assertRaisesRegex(ValueError, 'episode expired'):
            audit_stage.audit(now=now)

    def test_stale_module_namespace_refused_before_reader_import(self):
        sys.modules[reader_once.PRODUCER_MODULE] = object()
        try:
            with self.assertRaisesRegex(ValueError, 'stale Reader/Source module'):
                reader_once.fresh_module_namespace()
        finally:
            del sys.modules[reader_once.PRODUCER_MODULE]

    def test_nonregular_tree_entry_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fifo'
            os.mkfifo(path)
            with self.assertRaisesRegex(ValueError, 'nonregular'):
                audit_stage.entries(Path(temp))

    def test_copy_fixture_and_symlink_refusal(self):
        with tempfile.TemporaryDirectory() as temp:
            source, target = Path(temp) / 'source', Path(temp) / 'target'
            source.write_bytes(b'fixed fixture bytes')
            stage_reader.copy_exact(source, target, prepare_reader.sha(source.read_bytes()), 0o444, 0o644)
            self.assertEqual(target.read_bytes(), b'fixed fixture bytes')
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o444)
            another = Path(temp) / 'link'
            another.symlink_to(source)
            with self.assertRaisesRegex(ValueError, 'source member type/owner/mode differs'):
                stage_reader.copy_exact(another, Path(temp) / 'nope',
                                        prepare_reader.sha(source.read_bytes()), 0o444, 0o644)

    def test_source_and_package_manifest_modes_are_distinct(self):
        source_manifest = prepare_reader.PRODUCER + '/source-manifest.json'
        package_manifest = prepare_reader.PRODUCER + '/packages/0001/manifest.json'
        self.assertEqual(stage_reader.source_modes(source_manifest), (0o444, 0o444))
        self.assertEqual(stage_reader.source_modes(package_manifest), (0o600, 0o600))
        self.assertEqual(stat.S_IMODE((prepare_reader.SOURCE_ROOT / source_manifest).stat().st_mode), 0o444)
        self.assertEqual(stat.S_IMODE((prepare_reader.SOURCE_ROOT / package_manifest).stat().st_mode), 0o600)
        package = json.loads((prepare_reader.SOURCE_ROOT / package_manifest).read_bytes())
        self.assertEqual(len(package['files']), 36)
        for row in package['files']:
            self.assertEqual(stage_reader.source_modes(row['path']), (0o600, 0o600))
            self.assertEqual(stat.S_IMODE((prepare_reader.SOURCE_ROOT / row['path']).stat().st_mode), 0o600)

    def test_destination_readback_detects_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            source, target = Path(temp) / 'source', Path(temp) / 'target'
            source.write_bytes(b'fixed fixture bytes')
            real_read = os.read
            def corrupt_read(fd, size):
                raw = real_read(fd, size)
                if raw and os.readlink(f'/proc/self/fd/{fd}') == str(target):
                    return b'X' + raw[1:]
                return raw
            with patch.object(anchored_copy.os, 'read', side_effect=corrupt_read):
                with self.assertRaisesRegex(ValueError, 'destination readback'):
                    anchored_copy.copy_exact(source, target, prepare_reader.sha(source.read_bytes()),
                                             0o444, 0o644)

    def test_directory_names_are_fsynced(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            observed = []
            real_fsync = os.fsync
            def observe(fd):
                observed.append(stat.S_ISDIR(os.fstat(fd).st_mode))
                return real_fsync(fd)
            with patch.object(anchored_copy.os, 'fsync', side_effect=observe):
                anchored_copy.mkdir_exact(root / 'new', 0o700)
                source = root / 'source'; source.write_bytes(b'fixture')
                anchored_copy.copy_exact(source, root / 'new' / 'copied',
                                         prepare_reader.sha(b'fixture'), 0o444, 0o644)
                anchored_copy.write_exact(root / 'new' / 'receipt', b'fixture receipt')
            self.assertGreaterEqual(observed.count(True), 3)
            self.assertEqual((root / 'new' / 'receipt').read_bytes(), b'fixture receipt')

    def test_close_all_continues_after_one_close_fault(self):
        fds = [os.open('/dev/null', os.O_RDONLY) for _ in range(3)]
        called = []
        real_close = os.close
        def faulty_close(fd):
            called.append(fd)
            real_close(fd)
            if len(called) == 1:
                raise OSError('synthetic close fault after close')
        with patch.object(anchored_copy.os, 'close', side_effect=faulty_close):
            with self.assertRaisesRegex(ExceptionGroup, 'failed to close'):
                anchored_copy.close_all(fds)
        self.assertEqual(set(called), set(fds))
        for fd in fds:
            with self.assertRaises(OSError):
                os.fstat(fd)

    def test_parent_chain_closes_every_held_fd_after_close_fault(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'parent').mkdir()
            path = base / 'parent' / 'member'
            called = []
            real_close = os.close
            def faulty_close(fd):
                called.append(fd)
                real_close(fd)
                if len(called) == 1:
                    raise OSError('synthetic first chain close fault')
            with patch.object(anchored_copy.os, 'close', side_effect=faulty_close):
                with self.assertRaisesRegex(ExceptionGroup, 'failed to close'):
                    with anchored_copy.parent_chain(path):
                        pass
            self.assertGreaterEqual(len(called), 3)
            for fd in called:
                with self.assertRaises(OSError):
                    os.fstat(fd)

    def test_keyboard_interrupt_close_fault_still_closes_all_held_fds(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); (base / 'parent').mkdir()
            called = []
            real_close = os.close
            def interrupting_close(fd):
                called.append(fd)
                real_close(fd)
                if len(called) == 1:
                    raise KeyboardInterrupt('synthetic after-real-close interrupt')
            with patch.object(anchored_copy.os, 'close', side_effect=interrupting_close):
                with self.assertRaises(BaseExceptionGroup) as caught:
                    with anchored_copy.parent_chain(base / 'parent' / 'member'):
                        pass
            self.assertTrue(any(isinstance(error, KeyboardInterrupt)
                                for error in caught.exception.exceptions))
            self.assertGreaterEqual(len(called), 3)
            for fd in called:
                with self.assertRaises(OSError):
                    os.fstat(fd)

    def test_primary_failure_survives_secondary_close_fault(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); (base / 'parent').mkdir()
            primary = ValueError('synthetic selected-byte mismatch')
            called = []
            real_close = os.close
            def interrupting_close(fd):
                called.append(fd)
                real_close(fd)
                if len(called) == 1:
                    raise KeyboardInterrupt('synthetic cleanup interrupt')
            with patch.object(anchored_copy.os, 'close', side_effect=interrupting_close):
                with self.assertRaises(ValueError) as caught:
                    with anchored_copy.parent_chain(base / 'parent' / 'member'):
                        raise primary
            self.assertIs(caught.exception, primary)
            self.assertIsNone(primary.__cause__)
            self.assertEqual(len(primary.secondary_close_errors), 1)
            self.assertIsInstance(primary.secondary_close_errors[0][1], KeyboardInterrupt)
            self.assertIn('Secondary owned-FD close failures retained', ' '.join(primary.__notes__))
            self.assertGreaterEqual(len(called), 3)
            for fd in called:
                with self.assertRaises(OSError):
                    os.fstat(fd)

    def test_copy_primary_failure_survives_leaf_close_interrupt(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source, target = base / 'source', base / 'target'
            source.write_bytes(b'fixture bytes')
            primary = ValueError('synthetic copy verification failure')
            called = []
            real_close = os.close
            def interrupting_close(fd):
                called.append(fd)
                real_close(fd)
                if len(called) == 2:
                    raise KeyboardInterrupt('synthetic leaf-close interrupt')
            def fail_after_copy():
                raise primary
            with patch.object(anchored_copy.os, 'close', side_effect=interrupting_close):
                with self.assertRaises(ValueError) as caught:
                    anchored_copy.copy_exact(source, target, prepare_reader.sha(b'fixture bytes'),
                                             0o444, 0o644, after_copy_hook=fail_after_copy)
            self.assertIs(caught.exception, primary)
            self.assertIsNone(primary.__cause__)
            self.assertEqual(len(primary.secondary_close_errors), 1)
            self.assertIsInstance(primary.secondary_close_errors[0][1], KeyboardInterrupt)
            self.assertGreaterEqual(len(called), 3)
            for fd in called:
                with self.assertRaises(OSError):
                    os.fstat(fd)

    def test_two_nested_close_faults_preserve_original_cause_and_details(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source, target = base / 'source', base / 'target'
            source.write_bytes(b'fixture bytes')
            original_cause = RuntimeError('preexisting selected-evidence cause')
            primary = ValueError('synthetic copy verification failure')
            primary.__cause__ = original_cause
            target_closes = 0
            close_calls = []
            injected = []
            real_close = os.close
            def two_faults(fd):
                nonlocal target_closes
                attached = os.readlink(f'/proc/self/fd/{fd}')
                close_calls.append((fd, attached))
                real_close(fd)
                if attached == str(target):
                    target_closes += 1
                    if target_closes == 2:  # writer after successful readback close
                        error = OSError('exact destination close fault')
                        injected.append(error)
                        raise error
                if attached == str(source):
                    error = KeyboardInterrupt('exact source close fault')
                    injected.append(error)
                    raise error
            def fail_after_copy():
                raise primary
            with patch.object(anchored_copy.os, 'close', side_effect=two_faults):
                with self.assertRaises(ValueError) as caught:
                    anchored_copy.copy_exact(source, target, prepare_reader.sha(b'fixture bytes'),
                                             0o444, 0o644, after_copy_hook=fail_after_copy)
            self.assertIs(caught.exception, primary)
            self.assertIs(primary.__cause__, original_cause)
            self.assertEqual(len(injected), 2)
            self.assertEqual([error for _, error in primary.secondary_close_errors], injected)
            self.assertEqual(len(primary.secondary_close_errors), 2)
            self.assertEqual([type(error) for _, error in primary.secondary_close_errors],
                             [OSError, KeyboardInterrupt])
            self.assertIn('exact destination close fault', ' '.join(primary.__notes__))
            self.assertIn('exact source close fault', ' '.join(primary.__notes__))
            for fd, _ in close_calls:
                with self.assertRaises(OSError):
                    os.fstat(fd)

    def test_source_ancestor_swap_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source_parent, moved, target_parent = base / 'src', base / 'moved', base / 'out'
            source_parent.mkdir(); target_parent.mkdir()
            source = source_parent / 'member'; source.write_bytes(b'selected fixture')
            def swap():
                source_parent.rename(moved)
                source_parent.symlink_to(moved, target_is_directory=True)
            with self.assertRaises((ValueError, OSError)):
                anchored_copy.copy_exact(source, target_parent / 'member',
                                         prepare_reader.sha(b'selected fixture'), 0o444, 0o644,
                                         after_copy_hook=swap)
            self.assertEqual((moved / 'member').read_bytes(), b'selected fixture')

    def test_destination_ancestor_swap_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source_parent, target_parent, moved = base / 'src', base / 'out', base / 'moved'
            source_parent.mkdir(); target_parent.mkdir()
            source = source_parent / 'member'; source.write_bytes(b'selected fixture')
            def swap():
                target_parent.rename(moved)
                target_parent.symlink_to(moved, target_is_directory=True)
            with self.assertRaises((ValueError, OSError)):
                anchored_copy.copy_exact(source, target_parent / 'member',
                                         prepare_reader.sha(b'selected fixture'), 0o444, 0o644,
                                         after_copy_hook=swap)
            self.assertEqual((moved / 'member').read_bytes(), b'selected fixture')

    def test_nofollow_directory_creation_and_programmatic_gates(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / 'real').mkdir()
            (base / 'link').symlink_to(base / 'real', target_is_directory=True)
            with self.assertRaises((ValueError, OSError)):
                anchored_copy.mkdir_exact(base / 'link' / 'child', 0o700)
        with self.assertRaisesRegex(ValueError, 'stage disabled'):
            stage_reader.stage()
        with self.assertRaisesRegex(ValueError, 'effect disabled'):
            reader_once.run()
        with self.assertRaisesRegex(ValueError, 'effect disabled'):
            reader_once.selected()

    def test_controller_exact_readonly_contract_and_disabled_effect(self):
        contract = controller_contract.contract()
        args = contract['create_argv']
        self.assertFalse(contract['effect_enabled'])
        self.assertFalse(reader_once.EFFECT_ENABLED)
        self.assertIn('type=bind,src=' + str(controller_contract.ROOT) + ',dst=/attempt/root,readonly', args)
        self.assertIn('type=bind,src=' + str(controller_contract.HERE) + ',dst=/tool,readonly', args)
        self.assertNotIn(str(prepare_reader.SOURCE_ROOT), ' '.join(args))
        self.assertIn('source period checked again immediately before PASS terminal',
                      contract['required_one_shot_lifecycle'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
