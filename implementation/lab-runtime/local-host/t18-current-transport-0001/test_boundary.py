import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path
import types
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t18_transport_boundary', HERE / 'boundary.py')
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)


class BoundaryTests(unittest.TestCase):
    def test_selected_seven_actual_cases(self):
        rows = B.cases()
        self.assertEqual([r['case'] for r in rows], [
            'exact-raw-dispatch', 'partial-frame', 'oversized-frame',
            'wire-budget', 'frame-budget', 'startup-deadline', 'output-budget'])
        self.assertEqual([r['effect_calls'] for r in rows], [2, 0, 0, 0, 1, 0, 0])

    def test_ambient_control_impostor_cannot_replace_selected_bytes(self):
        prior = sys.modules.get('control')
        impostor = types.ModuleType('control')
        impostor.sha = lambda _: 'wrong'
        sys.modules['control'] = impostor
        try:
            self.assertEqual(len(B.cases()), 7)
            self.assertIs(sys.modules['control'], impostor)
        finally:
            if prior is None: sys.modules.pop('control', None)
            else: sys.modules['control'] = prior

    def test_changed_selected_framing_refuses(self):
        with tempfile.TemporaryDirectory(prefix='cal-t18-select-') as temp:
            root = Path(temp)
            for name in (*B.PINS, B.LIVE):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(B.ROOT / name, target)
            selected = root / B.SDK / 'framing.py'
            selected.write_bytes(selected.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'selected bytes changed'):
                B.selected(root)

    def test_equal_byte_symlinked_ancestor_refuses(self):
        with tempfile.TemporaryDirectory(prefix='cal-t18-link-') as temp:
            root = Path(temp)
            (root / 'real').mkdir()
            (root / 'real' / 'x').write_bytes(b'exact')
            (root / 'link').symlink_to('real', target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'unsafe selected path'):
                B.exact(root, 'link/x', B.digest(b'exact'))

    def test_result_claim_ceiling(self):
        value = B.result()
        self.assertTrue(value['local_framing_slice_passed'])
        self.assertFalse(value['cross_branch_proof_qualified'])
        self.assertFalse(value['same_family_t18_complete'])
        self.assertEqual(value['authority_effect'], 'none')

    def test_unrelated_output_error_cannot_count_as_budget_refusal(self):
        def unrelated(_output, _value, _limit):
            raise ValueError('unrelated failure')
        with self.assertRaisesRegex(ValueError, 'output budget refusal not causal'):
            B.output_budget_case(unrelated)


if __name__ == '__main__': unittest.main()
