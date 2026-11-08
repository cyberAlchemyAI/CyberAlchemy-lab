import hashlib
import importlib.util
import ast
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('t31_api46_bootstrap', HERE / 'bootstrap.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
ROOT = Path(__file__).resolve().parents[4]
FACTORY = ROOT / MODULE.API_REL / 'workflow_output_factory.py'


def reader(binding):
    return (ROOT / binding['path']).read_bytes()


class BootstrapOrigin(unittest.TestCase):
    def test_selected_current_factory_uses_its_actual_bytes(self):
        digest = hashlib.sha256(FACTORY.read_bytes()).hexdigest()
        rows = {(str(FACTORY.relative_to(ROOT)), digest)}
        root, api = MODULE.selected_api_factory(SimpleNamespace(__file__=str(FACTORY)), reader, rows)
        self.assertEqual((root, api), (ROOT, ROOT / MODULE.API_REL))

    def test_other_api_and_changed_byte_refused(self):
        digest = hashlib.sha256(FACTORY.read_bytes()).hexdigest()
        rows = {(str(FACTORY.relative_to(ROOT)), digest)}
        other = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v45-r03-0005-coverage-0002/workflow_output_factory.py'
        with self.assertRaisesRegex(ValueError, 'true selected API46 factory origin'):
            MODULE.selected_api_factory(SimpleNamespace(__file__=str(other)), reader, rows)
        wrong = {(str(FACTORY.relative_to(ROOT)), '0' * 64)}
        with self.assertRaisesRegex(ValueError, 'exact selected API46 factory bytes'):
            MODULE.selected_api_factory(SimpleNamespace(__file__=str(FACTORY)), reader, wrong)

    def test_symlinked_ancestor_refused_even_when_bytes_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            actual = root / 'actual' / 'lab/release-candidates/v1/interface' / MODULE.API_REL.name
            actual.mkdir(parents=True)
            (actual / 'workflow_output_factory.py').write_bytes(FACTORY.read_bytes())
            (root / 'product').symlink_to(root / 'actual', target_is_directory=True)
            linked = root / MODULE.API_REL / 'workflow_output_factory.py'
            rows = {(str(MODULE.API_REL / 'workflow_output_factory.py'), hashlib.sha256(FACTORY.read_bytes()).hexdigest())}
            with self.assertRaisesRegex(ValueError, 'true selected API46 factory origin'):
                MODULE.selected_api_factory(SimpleNamespace(__file__=str(linked)), lambda binding: linked.read_bytes(), rows)

    def test_all_28_groups_and_true_origin_modules_are_selected(self):
        source = ast.parse((HERE / 'bootstrap.py').read_text())
        groups = []
        for node in ast.walk(source):
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'groups' for target in node.targets):
                groups = ast.literal_eval(node.value)
        refs = ['transition:' + key for _, _, keys in groups for key in keys]
        self.assertEqual(len(refs), 28)
        self.assertEqual(len(set(refs)), 28)
        registry = ast.parse((ROOT / MODULE.API_REL / 'workflow_output_registry.py').read_text())
        selected = next(ast.literal_eval(node.value) for node in registry.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'REGISTRY' for target in node.targets))
        self.assertEqual(set(refs), set(selected))
        manifest = json.loads((ROOT / MODULE.API_REL / 'source-manifest.json').read_text())
        rows = {row['path']: row['sha256'] for row in manifest['files']}
        for name in ('api_outputs','stage_producers','native_outputs','ontology_outputs','migration_outputs','product_outputs','original_resolvers','response_outputs','output_factory','lesson_consumer'):
            path = ROOT / MODULE.API_REL / ('workflow_' + name + '.py')
            self.assertEqual(rows[str(path.relative_to(ROOT))], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
