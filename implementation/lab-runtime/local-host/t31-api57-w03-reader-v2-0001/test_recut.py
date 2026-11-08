"""Cold causal checks for the two-family API57 source recut."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('_cal_t31_api57_recut_test', HERE / 'build_api57.py')
recut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recut)


class Recut(unittest.TestCase):
    def old(self, leaf):
        return (recut.OLD / leaf).read_text()

    def test_legacy_w03_and_source8_ce4_remain_distinct(self):
        source = recut.recut('source_bridge.py', self.old('source_bridge.py'))
        compile(source, 'selected-source-bridge', 'exec')
        self.assertIn("CURRENT_LEGACY_CONTEXT='implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-62f4c217e8b9a30d/context-w03-0005'", source)
        self.assertIn("CURRENT_SOURCE8_CONTEXT='implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5/context'", source)
        self.assertIn("CURRENT_LEGACY_READER='implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-62f4c217e8b9a30d/reader-w03-0002'", source)
        self.assertIn("CURRENT_SOURCE8_READER='implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5/reader'", source)

    def test_machine_auth_rebinds_only_legacy(self):
        source = recut.recut('machine_auth_scope.py', self.old('machine_auth_scope.py'))
        compile(source, 'selected-machine-auth-scope', 'exec')
        self.assertIn("'current_legacy_context_sessions.py':('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-62f4c217e8b9a30d/context-w03-0005'", source)
        self.assertIn("'current_context_sessions.py':('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5/context'", source)

    def test_native_dispositions_bind_both_distinct_mappings(self):
        source = recut.recut('native_dispositions.py', self.old('native_dispositions.py'))
        compile(source, 'selected-native-dispositions', 'exec')
        self.assertIn(recut.MAPPING_SHA, source)
        self.assertIn('070f0cbf746294221347e520bc6dcd4fddb5c8be172b5834025b35e3dd5a587c', source)
        self.assertIn('661)', source)
        self.assertIn('616)', source)
        template = recut.ROOT / 'implementation/lab-runtime/local-host/t31-api57-w03-reader-v2-0001/native_dispositions_w03.py'
        original = recut.raw
        with patch.object(recut, 'raw', side_effect=lambda path: original(path) + b' ' if path == template else original(path)):
            with self.assertRaisesRegex(ValueError, 'constructor differs'):
                recut.recut('native_dispositions.py', self.old('native_dispositions.py'))

    def test_exact_reader_v2_entrypoint(self):
        source = recut.recut('legacy_fixture_selection.py', self.old('legacy_fixture_selection.py'))
        self.assertIn('legacy-local-62f4c217e8b9a30d/reader-w03-0002/reader.py#SelectedReader.open_signed', source)
        self.assertNotIn('legacy-local-62f4c217e8b9a30d/reader/reader.py#SelectedReader.open_signed', source)

    def test_changed_old_anchor_refuses(self):
        source = self.old('source_bridge.py').replace("CURRENT_LEGACY_NAME='completion-legacy:legacy-local-ce4d53a6479188a5'",
                                                         "CURRENT_LEGACY_NAME='forged'", 1)
        with self.assertRaisesRegex(ValueError, 'exact anchor differs'):
            recut.recut('source_bridge.py', source)


if __name__ == '__main__':
    unittest.main()
