"""Check exact new challenge originals against the unchanged public reader."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
API = ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
PINS = json.loads((HERE/'PINS.json').read_bytes())
NEW = PINS['required_flat_rows'][-2:]


def need(value, message):
    if not value:
        raise ValueError(message)


def bound_reader(root, api):
    tree = ast.parse((API/'challenge_submission.py').read_text())
    owner = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'ChallengeSubmission')
    method = next(node for node in owner.body if isinstance(node, ast.FunctionDef) and node.name == 'bound_original')
    def original(binding):
        raw = (root/binding['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == binding['sha256'], 'original byte digest differs')
        return raw
    space = {'ROOT': root, 'HERE': api, 'Path': Path, 'require': need,
             'P': SimpleNamespace(source=SimpleNamespace(parse=lambda raw: json.loads(raw), original=original),
                                  frame_parse=lambda raw: json.loads(raw)),
             'W': SimpleNamespace(privacy=lambda body: None)}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(API/'challenge_submission.py'), 'exec'), space)
    return lambda selected: space['bound_original'](None, selected)


class ChallengeFlatSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        prior = HERE.parent/'test_flat_constructor_source.py'
        spec = importlib.util.spec_from_file_location('_cal_flat_predecessor_test', prior)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.POST = HERE/'guard.py'
        module.FlatConstructorSource.setUpClass()
        cls.flat = module.FlatConstructorSource('test_actual_four_rows_meet_both_original_constructors_and_closed_guard')
        cls.rows = module.FlatConstructorSource.rows

    def test_exact_two_rows_and_closed_guard(self):
        self.assertEqual(len(PINS['required_flat_rows']), 7)
        for row in NEW:
            self.assertEqual(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest(), row['sha256'])
        self.flat.guard(self.rows)
        for row in NEW:
            with self.subTest(path=row['path']), self.assertRaisesRegex(ValueError, 'closure differs'):
                self.flat.guard([candidate for candidate in self.rows if candidate['path'] != row['path']])

    def test_unchanged_challenge_reader_requires_both_originals(self):
        with tempfile.TemporaryDirectory(prefix='cal-challenge-flat-source-') as folder:
            root = Path(folder);api = root/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
            api.mkdir(parents=True)
            for row in NEW:
                target = root/row['path'];target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT/row['path']).read_bytes())
            manifest = api/'source-manifest.json'
            read = bound_reader(root, api)
            manifest.write_text(json.dumps({'files': NEW}))
            for row in NEW:
                self.assertEqual(read(row), (ROOT/row['path']).read_bytes())
                manifest.write_text(json.dumps({'files': [other for other in NEW if other != row]}))
                with self.assertRaisesRegex(ValueError, 'not bound to actual selected host source'):
                    read(row)
                manifest.write_text(json.dumps({'files': NEW}))

    def test_wrong_byte_pin_and_foreign_guard_row_refuse(self):
        with tempfile.TemporaryDirectory(prefix='cal-challenge-flat-wrong-') as folder:
            root = Path(folder);api = root/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001'
            api.mkdir(parents=True)
            row = dict(NEW[0]);target = root/row['path'];target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT/row['path']).read_bytes())
            row['sha256'] = '0'*64
            (api/'source-manifest.json').write_text(json.dumps({'files': [row]}))
            with self.assertRaisesRegex(ValueError, 'original byte digest differs'):
                bound_reader(root, api)(row)
        with self.assertRaisesRegex(ValueError, 'foreign successor'):
            self.flat.guard(self.rows + [{'path': 'product/foreign-challenge.json', 'sha256': 'f'*64}])


if __name__ == '__main__':
    unittest.main()
