"""Synthetic stage and module checks. Never imports the selected private Reader."""
from __future__ import annotations

import datetime as dt
from contextlib import contextmanager
import builtins
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

import reader_once as r


class SyntheticStage(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='cal-synthetic-reader-entry-')
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.root = self.base / 'root'
        self.tool = self.base / 'tool'
        self.output = self.base / 'output'
        self.snapshot_parent = self.base / 'container-tmp'
        for path in (self.root, self.tool, self.output, self.snapshot_parent):
            path.mkdir()
        self.now = dt.datetime.now(dt.timezone.utc)
        self.period = {'not_before': (self.now - dt.timedelta(hours=12)).isoformat(),
                       'expires_at': (self.now + dt.timedelta(hours=12)).isoformat()}
        self.patches = [mock.patch.multiple(r, ROOT=self.root, STAGE_ROOT=self.root,
                                            TOOL=self.tool, OUT=self.output,
                                            SNAPSHOT_PARENT=self.snapshot_parent,
                                            REQUIRE_SEPARATE_DEVICE=False,
                                            EFFECT_ENABLED=True),
                        mock.patch.object(r, 'container_topology')]
        for patch in self.patches:
            patch.start()
            self.addCleanup(patch.stop)

    def write(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return {'path': name, 'sha256': r.sha(raw)}

    def make_stage(self):
        source_code = [self.write(r.PRODUCER + '/' + name + '.py', b'# synthetic producer\n')
                       for name in ('__init__', 'base', 'cold', 'records')]
        source = {'files': source_code}
        source_row = self.write(r.PRODUCER + '/source-manifest.json', r.encoded(source))
        package_rows = [self.write(r.PRODUCER + '/packages/0001/period.json', r.encoded(self.period)),
                        self.write(r.PRODUCER + '/packages/0001/expected-replay.json',
                                   r.encoded({'expected_head': 'h' * 64}))]
        for n in range(34):
            package_rows.append(self.write(r.PRODUCER + f'/packages/0001/filler-{n:02d}', b'fixture'))
        package = {'files': package_rows, 'source_manifest_binding': source_row,
                   'period_binding': package_rows[0], 'expected_replay_binding': package_rows[1]}
        package_row = self.write(r.PRODUCER + '/packages/0001/manifest.json', r.encoded(package))
        reader_code = [self.write(r.READER + '/' + name + '.py',
                                  b"FLAG='selected'\n" if name == 'reader'
                                  else b'# synthetic reader\n')
                       for name in ('__init__', 'adapter', 'base', 'eligibility', 'inspection', 'model', 'reader')]
        rows = source_code + [source_row] + reader_code
        for n in range(948 - len(rows)):
            rows.append(self.write(f'synthetic/public/filler-{n:04d}', b'fixture'))
        reader = {'files': rows, 'producer_source_binding': source_row,
                  'producer_package_binding': package_row,
                  'authority_effect': 'none', 'actual_owner_outcome': None}
        reader_row = self.write(r.READER + '/source-manifest.json', r.encoded(reader))
        (self.root / r.PRODUCER / 'receipts').mkdir()
        selection = {'effect': 'NOT_RUN', 'reader_manifest_binding': reader_row,
                     'source_manifest_binding': source_row, 'source_package_binding': package_row,
                     'episode_expires_at': self.period['expires_at'], 'expected_head': 'h' * 64}
        raw = r.encoded(selection)
        (self.tool / 'selection.json').write_bytes(raw)
        all_rows = reader['files'] + package['files'] + [reader_row, package_row]
        plan = {'schema_version': 'lab-reader-stage-copy-plan/v1-inert',
                'effect': 'NOT_RUN', 'archive_body_opened': False,
                'selection_sha256': r.sha(raw),
                'files': [{'path': item['path'], 'sha256': item['sha256'],
                           'target_mode': '0600'} for item in sorted(all_rows,
                                                                      key=lambda row: row['path'])]}
        plan_raw = r.encoded(plan)
        (self.tool / 'stage-plan.json').write_bytes(plan_raw)
        (self.root / r.PRODUCER / 'receipts').chmod(0o700)
        for path in self.root.rglob('*'):
            if path.is_file():
                path.chmod(0o600)
            elif path.is_dir():
                relative = path.relative_to(self.root).as_posix()
                private = relative == r.PRODUCER + '/receipts' or relative.startswith(r.PRODUCER + '/packages')
                path.chmod(0o700 if private else 0o755)
        self.root.chmod(0o755)
        pins = mock.patch.multiple(r, SELECTION_SHA=r.sha(raw), READER_SHA=reader_row['sha256'],
                                   STAGE_PLAN_SHA=r.sha(plan_raw))
        pins.start()
        self.addCleanup(pins.stop)
        return selection, source, reader

    def test_shipped_gate_precedes_stage_or_private_read(self):
        with mock.patch.object(r, 'EFFECT_ENABLED', False), \
             mock.patch.object(r, 'regular', side_effect=AssertionError('stage read')):
            with self.assertRaisesRegex(ValueError, 'effect disabled'):
                r.run()

    def test_selected_private_single_process_topology(self):
        selected = types.SimpleNamespace(st_uid=1000, st_gid=1000,
                                         st_mode=0o40700, st_dev=7)
        root = types.SimpleNamespace(st_dev=8)
        mount = b'51 47 0:42 / /attempt/tmp rw,nosuid,nodev - tmpfs tmpfs rw\n'
        r.validate_topology(1000, 1000, 1, {'1'}, selected, root, mount)
        cases = [
            (1001, 1000, 1, {'1'}, selected, root, mount),
            (1000, 1000, 1, {'1', '2'}, selected, root, mount),
            (1000, 1000, 1, {'1'}, selected,
             types.SimpleNamespace(st_dev=7), mount),
            (1000, 1000, 1, {'1'}, selected, root,
             b'51 47 0:42 / /attempt/tmp rw - ext4 /dev/sda rw\n'),
        ]
        for args in cases:
            with self.subTest(args=args[:4]), self.assertRaises(ValueError):
                r.validate_topology(*args)

    def test_exact_986_synthetic_selection_and_postreceipt(self):
        self.make_stage()
        selected, period, expected, source, reader, rows = r.selected()
        self.assertEqual(selected['expected_head'], expected['expected_head'])
        self.assertEqual(len(reader['files']) + 36 + 2, 986)
        self.assertEqual(len(rows), 986)
        self.assertEqual(period, self.period)
        (self.output / 'receipt.json').write_bytes(b'{}\n')
        r.selected(output_empty=False)
        with self.assertRaisesRegex(ValueError, 'output is not fresh'):
            r.selected()

    def test_mutated_binding_and_extra_entry_rejected(self):
        self.make_stage()
        victim = self.root / 'synthetic/public/filler-0000'
        victim.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'selected input differs'):
            r.selected()
        victim.write_bytes(b'fixture')
        (self.root / 'unexpected').write_bytes(b'extra')
        with self.assertRaisesRegex(ValueError, 'inventory differs'):
            r.selected()

    def test_stage_private_mode_change_rejected_with_identical_bytes(self):
        self.make_stage()
        period = self.root / r.PRODUCER / 'packages/0001/period.json'
        original = period.read_bytes()
        period.chmod(0o777)
        self.assertEqual(period.read_bytes(), original)
        with self.assertRaisesRegex(ValueError, 'unsafe or oversized staged file'):
            r.selected()

    def test_wrong_carrier_and_aggregate_body_exclusion(self):
        carrier = 'cal.artifact-type.goal/v1'
        required = {'cal.artifact-type.goal/v1',
                    'cal.artifact-type.coordination-context/v2',
                    'cal.artifact-type.project-state/v2'}
        loaded = types.SimpleNamespace(adapter=types.SimpleNamespace(CARRIERS={key: None for key in required}))
        signed = types.SimpleNamespace(records=[types.SimpleNamespace(artifact={'carrier_ref': carrier})],
                                       dispositions=[object()], schemas=[])
        report = {'carrier_counts': {key: int(key == carrier) for key in required},
                  'missing_current_carriers': sorted(required - {carrier}),
                  'accounted_subjects': 1, 'included_current_instances': 1,
                  'authority_effect': 'none', 'actual_owner_outcome': None,
                  'private_detail': {'body': 'never in aggregate receipt'}}
        summary = r.aggregate(signed, report, loaded)
        self.assertNotIn('private_detail', summary)
        self.assertNotIn('body', r.encoded(summary).decode())
        signed.records[0].artifact['carrier_ref'] = 'wrong-carrier'
        with self.assertRaisesRegex(ValueError, 'carrier accounting differs'):
            r.aggregate(signed, report, loaded)

    def test_stale_module_prefix_and_alias_rejected(self):
        source, _, _ = self.make_stage()
        sys.modules[r.MODULE] = object()
        try:
            with self.assertRaisesRegex(ValueError, 'stale Reader/Source module namespace'):
                r.fresh_module_namespace()
        finally:
            del sys.modules[r.MODULE]
        alias = types.ModuleType('synthetic_alias')
        alias.__file__ = str(self.root / r.READER / 'reader.py')
        sys.modules['synthetic_alias'] = alias
        try:
            with self.assertRaisesRegex(ValueError, 'stale Reader/Source module alias'):
                r.fresh_module_namespace()
        finally:
            del sys.modules['synthetic_alias']

    def test_module_origins_reject_wrong_origin_and_changed_bytes(self):
        _, source, reader = self.make_stage()
        created = []
        for prefix, stem, names in ((r.MODULE, r.READER,
                                      ('__init__', 'adapter', 'base', 'eligibility', 'inspection', 'model', 'reader')),
                                     (r.PRODUCER_MODULE, r.PRODUCER,
                                      ('__init__', 'base', 'cold', 'records'))):
            for name in names:
                key = prefix if name == '__init__' else prefix + '.' + name
                module = types.ModuleType(key)
                module.__file__ = str(self.root / stem / (name + '.py'))
                if name == '__init__':
                    module.__path__ = [str(self.root / stem)]
                sys.modules[key] = module
                created.append(key)
        self.addCleanup(lambda: [sys.modules.pop(key, None) for key in created])
        r.module_origins(source, reader)
        sys.modules[r.MODULE + '.reader'].__file__ = str(self.base / 'wrong.py')
        with self.assertRaisesRegex(ValueError, 'origin or bytes differ'):
            r.module_origins(source, reader)
        sys.modules[r.MODULE + '.reader'].__file__ = str(self.root / r.READER / 'reader.py')
        (self.root / r.READER / 'reader.py').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'origin or bytes differ'):
            r.module_origins(source, reader)

    def test_expired_period_rejected(self):
        with self.assertRaisesRegex(ValueError, 'not current'):
            r.period_current(self.period, self.now + dt.timedelta(hours=12))

    def test_synthetic_one_shot_checks_period_at_every_boundary(self):
        class Inspection:
            pass
        class SignedSources:
            def __init__(self):
                self.view = Inspection()
                self.source_cut = {'head': 'synthetic-digest'}
            def guard(self):
                return True
            def closure_report(self):
                return {}
        class Reader:
            def __init__(self, _reader_pin, source_pin, package_pin):
                self.source_pin, self.package_pin = source_pin, package_pin
            @contextmanager
            def open_signed(self, _source_pin, _package_pin):
                yield SignedSources()
        loaded = types.SimpleNamespace(
            SelectedReader=Reader, Inspection=Inspection,
            adapter=types.SimpleNamespace(SignedSources=SignedSources))
        selection = {'source_manifest_binding': {'sha256': 's' * 64},
                     'source_package_binding': {'sha256': 'p' * 64}}
        selected = (selection, self.period, {'expected_head': 'h' * 64}, {}, {}, [])
        real_import = builtins.__import__
        def synthetic_import(name, *args, **kwargs):
            return loaded if name == r.MODULE + '.reader' else real_import(name, *args, **kwargs)
        fake_spec = types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda _module: None))
        fake_package = types.ModuleType(r.MODULE)
        @contextmanager
        def fake_snapshot(_source, _reader):
            yield {}
        @contextmanager
        def fake_stage(_rows):
            yield self.root
        @contextmanager
        def fake_sealed(_snapshot):
            yield None
        calls = []
        def check_period(_value):
            calls.append('period')
            if len(calls) == 4:
                raise ValueError('synthetic period expired before PASS')
        with mock.patch.object(r, 'selected', return_value=selected) as select, \
             mock.patch.object(r, 'fresh_module_namespace'), \
             mock.patch.object(r, 'module_origins'), \
             mock.patch.object(r, 'held_code_snapshot', side_effect=fake_snapshot), \
             mock.patch.object(r, 'stage_snapshot', side_effect=fake_stage), \
             mock.patch.object(r, 'sealed_imports', side_effect=fake_sealed), \
             mock.patch.object(r.importlib.util, 'spec_from_file_location', return_value=fake_spec), \
             mock.patch.object(r.importlib.util, 'module_from_spec', return_value=fake_package), \
             mock.patch.object(builtins, '__import__', side_effect=synthetic_import), \
             mock.patch.object(r, 'regular', return_value=r.encoded(self.period)), \
             mock.patch.object(r, 'period_current', side_effect=check_period), \
             mock.patch.object(r, 'aggregate', return_value={'accounted_subjects': 0,
                 'current_records': 0, 'schemas': 0, 'missing_current_carriers': [],
                 'private_closure_report_sha256': 'd' * 64}):
            try:
                with self.assertRaisesRegex(ValueError, 'expired before PASS'):
                    r.run()
            finally:
                sys.modules.pop(r.MODULE, None)
        self.assertEqual(len(calls), 4)
        self.assertEqual(select.call_count, 4)
        self.assertTrue((self.output / 'receipt.json').is_file())

    def test_swap_and_restore_cannot_change_executed_snapshot(self):
        _, source, reader = self.make_stage()
        path = self.root / r.READER / 'reader.py'
        original = path.read_bytes()
        self.assertEqual(original, b"FLAG='selected'\n")
        with r.held_code_snapshot(source, reader) as snapshot:
            path.write_bytes(b"FLAG='altered!'\n")
            try:
                with r.sealed_imports(snapshot):
                    spec = r.importlib.util.spec_from_file_location(r.MODULE + '.reader', path)
                    module = r.importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.assertEqual(module.FLAG, 'selected')
                    self.assertEqual(snapshot[r.MODULE + '.reader']['executed_sha256'],
                                     r.sha(original))
            finally:
                path.write_bytes(original)
        self.assertEqual(path.read_bytes(), original)

    def test_explicit_producer_spec_and_normal_import_use_sealed_loader(self):
        _, source, reader = self.make_stage()
        with r.held_code_snapshot(source, reader) as snapshot:
            with r.sealed_imports(snapshot):
                producer_path = self.root / r.PRODUCER / '__init__.py'
                spec = r.importlib.util.spec_from_file_location(
                    r.PRODUCER_MODULE, producer_path,
                    submodule_search_locations=[str(producer_path.parent)])
                package = r.importlib.util.module_from_spec(spec)
                sys.modules[r.PRODUCER_MODULE] = package
                try:
                    spec.loader.exec_module(package)
                    loaded = __import__(r.PRODUCER_MODULE + '.base', fromlist=['*'])
                    self.assertIs(loaded.__loader__, snapshot[r.PRODUCER_MODULE + '.base']['loader'])
                    self.assertEqual(snapshot[r.PRODUCER_MODULE]['executed_sha256'],
                                     snapshot[r.PRODUCER_MODULE]['sha256'])
                finally:
                    sys.modules.pop(r.PRODUCER_MODULE + '.base', None)
                    sys.modules.pop(r.PRODUCER_MODULE, None)

    def test_oversized_report_string_refused_before_encoder(self):
        with mock.patch.object(json.JSONEncoder, 'iterencode',
                               side_effect=AssertionError('serialized first')):
            with self.assertRaisesRegex(ValueError, 'string bound exceeded'):
                r.bounded_encoded({'private': 'x' * 100}, 16)

    def test_symlinked_source_ancestor_refused(self):
        outside = self.base / 'outside'
        outside.mkdir()
        (outside / 'member').write_bytes(b'fixed')
        (self.base / 'linked').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(OSError):
            r.regular(self.base / 'linked' / 'member')

    def test_host_swap_during_synthetic_cold_open_consumes_tmpfs_snapshot(self):
        self.make_stage()
        rows = r.selected()[5]
        source_file = self.root / 'synthetic/public/filler-0000'
        original = source_file.read_bytes()
        snapshot_path = self.snapshot_parent / r.SNAPSHOT_NAME
        with r.stage_snapshot(rows) as snapshot:
            self.assertEqual(snapshot, snapshot_path)
            selected_snapshot = snapshot / 'synthetic/public/filler-0000'
            source_file.write_bytes(b'changed')
            try:
                # This block models a same-UID host edit while the cold-open
                # consumes only the owned container snapshot.
                with mock.patch.object(r, 'ROOT', snapshot):
                    self.assertEqual(r.regular(selected_snapshot), original)
                    self.assertEqual(len(r.selected()[5]), 986)
                self.assertEqual(source_file.read_bytes(), b'changed')
            finally:
                source_file.write_bytes(original)
        self.assertFalse(snapshot_path.exists())

    def test_bad_source_byte_aborts_and_cleans_snapshot(self):
        self.make_stage()
        rows = r.selected()[5]
        source_file = self.root / 'synthetic/public/filler-0000'
        source_file.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'captured source bytes differ'):
            with r.stage_snapshot(rows):
                self.fail('bad source reached cold-open')
        self.assertFalse((self.snapshot_parent / r.SNAPSHOT_NAME).exists())

    def test_existing_snapshot_name_is_never_replaced(self):
        self.make_stage()
        selected_root = self.snapshot_parent / r.SNAPSHOT_NAME
        selected_root.mkdir()
        marker = selected_root / 'preserved'
        marker.write_bytes(b'preexisting')
        with self.assertRaises(FileExistsError):
            with r.stage_snapshot(r.selected()[5]):
                self.fail('preexisting snapshot was entered')
        self.assertEqual(marker.read_bytes(), b'preexisting')

    def test_separate_tmpfs_device_gate_refuses_same_device_fixture(self):
        self.make_stage()
        with mock.patch.object(r, 'REQUIRE_SEPARATE_DEVICE', True), \
             self.assertRaisesRegex(ValueError, 'separate selected tmpfs'):
            with r.stage_snapshot(r.selected()[5]):
                self.fail('same-device fixture reached cold-open')
        self.assertFalse((self.snapshot_parent / r.SNAPSHOT_NAME).exists())

    def test_held_directory_interrupt_after_close_attempts_all_fds(self):
        real_open, real_close = os.open, os.close
        opened, closed = [], []
        def opening(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd
        def closing(fd):
            closed.append(fd)
            real_close(fd)
            if len(closed) == 1:
                raise KeyboardInterrupt('synthetic close after real close')
        primary = ValueError('inside held scope')
        with mock.patch.object(r.os, 'open', side_effect=opening), \
             mock.patch.object(r.os, 'close', side_effect=closing):
            with self.assertRaises(ValueError) as caught:
                with r.held_directory(self.snapshot_parent):
                    raise primary
        self.assertIs(caught.exception, primary)
        self.assertEqual(closed, list(reversed(opened)))
        self.assertEqual(len(primary.secondary_close_errors), 1)
        for fd in opened:
            with self.assertRaises(OSError): os.fstat(fd)

    def test_snapshot_replacement_before_held_root_open_preserves_foreign_child(self):
        snapshot = self.snapshot_parent / r.SNAPSHOT_NAME
        snapshot.mkdir()
        (snapshot / 'victim').write_bytes(b'owned')
        identity = (snapshot.stat().st_dev, snapshot.stat().st_ino)
        moved = self.snapshot_parent / 'retained-original'
        real_open = os.open
        swapped = []
        def opening(path, *args, **kwargs):
            if path == snapshot.name and not swapped:
                snapshot.rename(moved)
                snapshot.mkdir()
                (snapshot / 'victim').write_bytes(b'foreign')
                swapped.append(True)
            return real_open(path, *args, **kwargs)
        with mock.patch.object(r.os, 'open', side_effect=opening), \
             self.assertRaisesRegex(ValueError, 'root attachment differs'):
            r.cleanup_snapshot(snapshot, identity)
        self.assertTrue(swapped)
        self.assertEqual((snapshot / 'victim').read_bytes(), b'foreign')
        self.assertEqual((moved / 'victim').read_bytes(), b'owned')

    def test_snapshot_replacement_after_held_root_open_never_deletes_foreign(self):
        snapshot = self.snapshot_parent / r.SNAPSHOT_NAME
        snapshot.mkdir()
        (snapshot / 'victim').write_bytes(b'owned')
        identity = (snapshot.stat().st_dev, snapshot.stat().st_ino)
        moved = self.snapshot_parent / 'retained-original'
        real_listdir = os.listdir
        swapped = []
        def listing(fd):
            if isinstance(fd, int) and os.fstat(fd).st_ino == identity[1] and not swapped:
                snapshot.rename(moved)
                snapshot.mkdir()
                (snapshot / 'victim').write_bytes(b'foreign')
                swapped.append(True)
            return real_listdir(fd)
        with mock.patch.object(r.os, 'listdir', side_effect=listing), \
             self.assertRaisesRegex(ValueError, 'root changed during cleanup'):
            r.cleanup_snapshot(snapshot, identity)
        self.assertTrue(swapped)
        self.assertEqual((snapshot / 'victim').read_bytes(), b'foreign')
        self.assertFalse((moved / 'victim').exists())


if __name__ == '__main__':
    unittest.main()
