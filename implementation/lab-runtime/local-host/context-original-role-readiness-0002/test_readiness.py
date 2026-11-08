import copy
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('context_readiness_0001', HERE / 'readiness.py')
readiness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readiness)


class ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selected = json.loads((HERE / 'selection.json').read_bytes())
        cls.final = readiness.checked_json(cls.selected['selection_path'],
                                           cls.selected['selection_sha256'])
        cls.stage = readiness.checked_json(cls.selected['stage_review_path'],
                                           cls.selected['stage_review_sha256'])
        cls.roles = readiness.checked_json(cls.selected['historical_role_selection_path'],
                                           cls.selected['historical_role_selection_sha256'])
        cls.components = {}
        for key, pin in cls.selected['components'].items():
            freeze = readiness.checked_json(pin['freeze_path'], pin['freeze_sha256'])
            cls.components[key] = {'freeze': freeze,
                                   'selection': readiness._frozen_selection(pin, freeze)}

    def causal(self, which, change):
        vals = {k: copy.deepcopy(getattr(self, k))
                for k in ('selected', 'final', 'stage', 'roles', 'components')}
        change(vals[which])
        with self.assertRaises(readiness.Refused):
            readiness.validate_selection(vals['selected'], vals['final'], vals['stage'],
                                         vals['roles'], vals['components'])

    def test_actual_public_only_readiness(self):
        result = readiness.inspect()
        self.assertEqual(result['public_closure_rows_checked'], 102)
        self.assertEqual(result['status'], 'WAIT_AUTH_CURRENT_ROLE_AND_REAL_TRANSPORT')
        self.assertEqual(result['current_role_local_protocols'], 'FIVE_MISSING')
        self.assertEqual(result['effect'], 'NONE')

    def test_default_inspection_never_uses_path_read_bytes(self):
        with mock.patch.object(pathlib.Path, 'read_bytes',
                               side_effect=AssertionError('path reread')):
            self.assertEqual(readiness.inspect()['public_closure_rows_checked'], 102)

    def test_false_outer_os_cannot_become_zero(self):
        self.causal('stage', lambda x: x.__setitem__('external_os_exit', False))

    def test_auth_placeholder_cannot_be_fabricated(self):
        self.causal('final', lambda x: x['auth_placeholder'].__setitem__('sha256', '0' * 64))

    def test_cross_family_pin_refused(self):
        self.causal('final', lambda x: x['pins'].__setitem__('mapper_package', '0' * 64))

    def test_public_row_digest_refused(self):
        self.causal('selected', lambda x: x['public_closure']['api'][0].__setitem__('sha256', '0' * 64))

    def test_context_subset_loss_refused(self):
        self.causal('selected', lambda x: x['public_closure']['current_context_role'].pop())

    def test_42_frame_drift_refused(self):
        self.causal('components', lambda x: x['integration']['selection'].__setitem__('wire_request_count', 41))

    def test_40_leaf_drift_refused(self):
        self.causal('components', lambda x: x['validator']['selection'].__setitem__('package_leaves', 39))

    def test_real_effect_refused(self):
        with self.assertRaises(readiness.Refused):
            readiness.launch()

    def test_public_reader_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            (root / 'real').write_bytes(b'public')
            (root / 'link').symlink_to('real')
            row = {'path': 'link', 'mode': '0600', 'sha256': readiness.sha(b'public')}
            with self.assertRaises(readiness.Refused):
                readiness.read_public_at(root, row)

    def test_public_reader_detects_hash_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            p = root / 'public'
            p.write_bytes(b'other')
            os.chmod(p, 0o600)
            row = {'path': 'public', 'mode': '0600', 'sha256': readiness.sha(b'expected')}
            with self.assertRaises(readiness.Refused):
                readiness.read_public_at(root, row)

    def test_public_fifo_refuses_promptly(self):
        with tempfile.TemporaryDirectory() as temp:
            os.mkfifo(pathlib.Path(temp) / 'selected')
            script = (
                'import importlib.util,pathlib; '
                f'p={str(HERE / "readiness.py")!r}; '
                's=importlib.util.spec_from_file_location("fifo_reader",p); '
                'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                f'm.read_public_at({temp!r},'
                '{"path":"selected","mode":"0600","sha256":"' + '0' * 64 + '"})'
            )
            result = subprocess.run([sys.executable, '-B', '-c', script],
                                    capture_output=True, timeout=2)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'Refused', result.stderr)

    def test_own_selection_fifo_refuses_promptly(self):
        with tempfile.TemporaryDirectory() as temp:
            os.mkfifo(pathlib.Path(temp) / 'selection.json')
            script = (
                'import importlib.util,pathlib; '
                f'p={str(HERE / "readiness.py")!r}; '
                's=importlib.util.spec_from_file_location("fifo_selection",p); '
                'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                f'm.HERE=pathlib.Path({temp!r}); m.inspect()'
            )
            result = subprocess.run([sys.executable, '-B', '-c', script],
                                    capture_output=True, timeout=2)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'Refused', result.stderr)

    def test_metadata_oversize_and_symlink_refuse(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            big = root / 'selection.json'
            big.write_bytes(b'x' * (readiness.MAX_METADATA + 1))
            with self.assertRaises(readiness.Refused):
                readiness.checked_json(big, '0' * 64)
            (root / 'link').symlink_to(big)
            with self.assertRaises(readiness.Refused):
                readiness.checked_json(root / 'link', '0' * 64)

    def test_public_oversize_refuses_before_read(self):
        with tempfile.TemporaryDirectory() as temp:
            leaf = pathlib.Path(temp) / 'large'
            with leaf.open('wb') as out:
                out.truncate(readiness.MAX_PUBLIC_LEAF + 1)
            with self.assertRaises(readiness.Refused):
                readiness.read_public_at(temp, {'path': 'large', 'mode': '0644',
                                                'sha256': '0' * 64})

    def test_public_directory_leaf_refuses(self):
        with tempfile.TemporaryDirectory() as temp:
            (pathlib.Path(temp) / 'directory').mkdir()
            with self.assertRaises(readiness.Refused):
                readiness.read_public_at(temp, {'path': 'directory', 'mode': '0700',
                                                'sha256': '0' * 64})


if __name__ == '__main__':
    unittest.main()
