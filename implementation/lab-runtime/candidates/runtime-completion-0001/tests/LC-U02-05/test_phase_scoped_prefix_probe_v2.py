"""Pure guards for the disposable 15-leaf Source/Reader prefix probe."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1 import scratch_source_probe as source
from t35_external_v1.phase_scoped_v2 import plan as phase
from t35_external_v1.phase_scoped_v2 import prefix_probe as prefix
import test_phase_scoped_plan_v2 as plan_test


class PhaseScopedPrefixProbeTests(unittest.TestCase):
    def test_bridge_is_exactly_pinned_and_reader_overlay_is_disjoint(self):
        bridge = prefix._prefix_bridge('1'*64, '2'*64, '3'*64, '4'*64)
        self.assertIn(b'len(rows)!=15', bridge)
        self.assertNotIn(b'len(rows)!=30', bridge)
        self.assertNotIn(b'__SOURCE_SHA__', bridge)
        for digest in (b'1'*64, b'2'*64, b'3'*64, b'4'*64):
            self.assertIn(digest, bridge)
        with self.assertRaises(ValueError):
            prefix._prefix_bridge('wrong', '2'*64, '3'*64, '4'*64)
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            snapshot, family = root / 'snapshot', root / 'family'
            snapshot.mkdir(); family.mkdir()
            source_bridge = snapshot / '_t35_external_runtime_capture.py'
            source_bridge.write_bytes(b'selected source bridge')
            reader_bridge = snapshot / '_t35_reader_bridge.py'
            reader_bridge.write_bytes(bridge)
            argv = prefix._reader_argv(snapshot, family, reader_bridge)
            target = str(prefix.SNAPSHOT / '_t35_external_runtime_capture.py')
            self.assertEqual(argv.count(target), 1)
            self.assertEqual(argv[argv.index(target)-2:argv.index(target)+1],
                             ['--ro-bind', str(reader_bridge), target])
            self.assertEqual(source_bridge.read_bytes(), b'selected source bridge')

    def test_source_manifest_selects_only_early_leaves(self):
        layout, staged = plan_test.PhaseScopedPlanTests().fixture()
        planned = phase.plan(layout, staged, episode_raw=b'episode\n', role_raw=b'role\n')
        repository = {f'fixture/input-{i:04d}.json':
                      {'path': f'fixture/input-{i:04d}.json',
                       'sha256': hashlib.sha256(str(i).encode()).hexdigest()}
                      for i in range(1703)}
        control, source_raw = prefix._source_selection(planned, repository)
        stage = json.loads(control)
        manifest = json.loads(source_raw)
        self.assertEqual(len(stage), 15)
        self.assertEqual(len(manifest['files']), 1718)
        self.assertEqual({row['path'] for row in stage},
                         {row['path'] for row in manifest['files'] if row['path'].startswith('/')})
        self.assertTrue({row['path'] for row in stage}.isdisjoint(
            row['path'] for row in planned.deferred_bindings()))
        with self.assertRaises(ValueError):
            prefix._source_selection(planned, dict(list(repository.items())[:-1]))
        bad = dict(repository)
        bad['/absolute/unselected'] = {'path': '/absolute/unselected', 'sha256': '0'*64}
        with self.assertRaises(ValueError):
            prefix._source_selection(planned, bad)

    def test_inventory_rejects_future_role_and_aliases(self):
        with tempfile.TemporaryDirectory() as scratch:
            family = Path(scratch) / 'family'
            (family / 'source').mkdir(parents=True)
            (family / 'reader').mkdir()
            (family / 'source/base.py').write_bytes(b'base')
            files, dirs = prefix._inventory(family)
            self.assertEqual(files, {'source/base.py': source._sha(b'base')})
            self.assertEqual(dirs, {'source', 'reader'})
            (family / 'mapped').mkdir()
            with self.assertRaises(ValueError):
                prefix._inventory(family)
            (family / 'mapped').rmdir()
            (family / 'reader/alias.py').symlink_to(family / 'source/base.py')
            with self.assertRaises(ValueError):
                prefix._inventory(family)
            (family / 'reader/alias.py').unlink()
            (family / 'reader/alias.py').hardlink_to(family / 'source/base.py')
            with self.assertRaises(ValueError):
                prefix._inventory(family)


if __name__ == '__main__':
    unittest.main()
