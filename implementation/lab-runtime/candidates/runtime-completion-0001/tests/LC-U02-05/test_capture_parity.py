"""Exact T03 held capture over disposable snapshot and external stage paths."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
import unittest

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
sys.path.insert(0, str(REPO / 'implementation/lab-runtime/candidates/runtime-completion-0001'))
from t35_external_v1 import capture_parity, constructor_paths, role_stage


def binding(path: str, raw: bytes) -> dict:
    return {'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}


class T03ExternalParityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='lc-u02-05-t03-')
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.layout = role_stage.DisposableLayout(
            PurePosixPath(str(root / 'out/legacy-parity')),
            PurePosixPath(str(root / 'snapshot')), 'legacy-parity')
        snapshot = Path(self.layout.snapshot)
        self.inputs = []
        for selected in (capture_parity.CAPTURE, capture_parity.CALLER):
            source = REPO / selected['path']
            target = snapshot / selected['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            self.inputs.append(selected.copy())
        source_data = b'{"selected":"snapshot-only"}\n'
        path = 'api/selected.json'
        leaf = snapshot / path
        leaf.parent.mkdir(parents=True)
        leaf.write_bytes(source_data)
        self.source_row = binding(path, source_data)
        self.inputs.append(self.source_row)
        rows = role_stage.stage_rows(self.layout, lambda name: (REPO / name).read_bytes())
        episode = b'{"schema_version":"disposable-episode"}\n'
        role = b'{"schema_version":"disposable-role"}\n'
        controls = {'episode_contract': episode, 'context_native_role': role}
        construction = {
            'schema_version': 'lab-T35-external-root-stage-selection/v1-inactive',
            'authority_effect': 'none', 'instance': self.layout.instance,
            'output_family_path': str(self.layout.family),
            'template_rows': [{key: item[key] for key in ('role', 'input', 'output')}
                              for item in rows],
            'episode_binding': binding(str(self.layout.family / 'source/episode-contract.json'), episode),
            'current_role_binding': binding(str(self.layout.family / 'source/context-native-role.json'), role),
            'status': 'staged-unqualified',
        }
        controls['construction_selection'] = (json.dumps(construction, sort_keys=True) + '\n').encode()
        self.outputs = constructor_paths.stage_30_membership(self.layout, rows, controls)
        for item in rows:
            leaf = Path(item['output']['path'])
            leaf.parent.mkdir(parents=True, exist_ok=True)
            leaf.write_bytes(item['bytes'])
        for name, suffix in constructor_paths.STAGE_CONTROLS.items():
            leaf = Path(self.layout.family / suffix)
            leaf.parent.mkdir(parents=True, exist_ok=True)
            leaf.write_bytes(controls[name])

    def capture(self):
        return capture_parity.DisposableT03Parity(self.layout, self.inputs, self.outputs)

    def test_exact_t03_snapshot_and_external_stage_capture(self):
        selected = self.capture()
        self.assertEqual(selected.read_input(self.source_row), b'{"selected":"snapshot-only"}\n')
        row = self.outputs[str(self.layout.family / 'source/base.py')]
        self.assertEqual(hashlib.sha256(selected.read_stage(row)).hexdigest(), row['sha256'])
        self.assertEqual(selected.verify_stage(), 30)

    def test_unselected_alias_and_mutated_stage_refused(self):
        selected = self.capture()
        for path in ('/etc/passwd', str(self.layout.family / 'source/../reader/reader.py'),
                     str(self.layout.family) + '2/source/base.py'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                selected.read_stage(binding(path, b'x'))
        unknown = binding('api/unselected.json', b'x')
        with self.assertRaises(ValueError):
            selected.read_input(unknown)
        leaf = Path(self.layout.family / 'source/base.py')
        leaf.write_bytes(b'changed')
        with self.assertRaises(ValueError):
            selected.verify_stage()

    def test_kernel_caller_mutation_and_output_symlink_refused(self):
        selected = self.capture()
        selected._kernel.capture_one = lambda *_args, **_kwargs: b'forged'
        with self.assertRaises(ValueError):
            selected.read_input(self.source_row)
        selected._caller.check = lambda *_args, **_kwargs: None
        with self.assertRaises(ValueError):
            selected.read_input(self.source_row)
        selected = self.capture()
        selected._caller_check.__code__ = (lambda *_args, **_kwargs: None).__code__
        selected._capture_one.__code__ = (lambda *_args, **_kwargs: b'forged').__code__
        with self.assertRaises(ValueError):
            selected.read_input(self.source_row)
        selected = self.capture()
        leaf = Path(self.layout.family / 'reader/reader.py')
        leaf.unlink()
        leaf.symlink_to(Path(self.layout.family / 'source/base.py'))
        with self.assertRaises((ValueError, OSError)):
            selected.verify_stage()

    def test_selection_copy_and_on_disk_kernel_mutation_refused(self):
        selected = self.capture()
        original = self.source_row.copy()
        stage_path = str(self.layout.family / 'source/base.py')
        original_stage = self.outputs[stage_path].copy()
        self.inputs[-1]['sha256'] = '0' * 64
        self.outputs[stage_path]['sha256'] = '0' * 64
        self.assertEqual(selected.read_input(original), b'{"selected":"snapshot-only"}\n')
        selected._outputs[stage_path]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            selected.verify_stage()
        self.inputs[-1] = original
        self.outputs[stage_path] = original_stage
        selected = self.capture()
        kernel = Path(self.layout.snapshot / capture_parity.CAPTURE['path'])
        kernel.write_bytes(kernel.read_bytes() + b'\n# changed\n')
        with self.assertRaises(ValueError):
            selected.read_input(original)

    def test_caller_file_mutation_after_acquisition_refused(self):
        selected = self.capture()
        caller = Path(self.layout.snapshot / capture_parity.CALLER['path'])
        caller.write_bytes(caller.read_bytes() + b'\n# changed\n')
        with self.assertRaises(ValueError):
            selected.read_input(self.source_row)

    def test_wrong_selected_kernel_or_caller_refused(self):
        for selected_name in ('capture', 'caller'):
            rows = [row.copy() for row in self.inputs]
            path = capture_parity.CAPTURE['path'] if selected_name == 'capture' else capture_parity.CALLER['path']
            next(row for row in rows if row['path'] == path)['sha256'] = '0' * 64
            with self.subTest(selected_name=selected_name), self.assertRaises(ValueError):
                capture_parity.DisposableT03Parity(self.layout, rows, self.outputs)

    def test_hardlink_alias_outside_family_refused(self):
        selected = self.capture()
        stage = Path(self.layout.family / 'source/base.py')
        alias = Path(self.temporary.name) / 'outside-alias'
        os.link(stage, alias)
        with self.assertRaises(ValueError):
            selected.verify_stage()


if __name__ == '__main__':
    unittest.main()
