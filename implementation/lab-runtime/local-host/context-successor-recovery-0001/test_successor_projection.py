import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


P = load('prepare_successor')
T = load('project_tool')
C = load('project_controller')
S = load('source_controller')


class SuccessorProjectionTests(unittest.TestCase):
    def test_fresh_public_identity_and_exact_materialized_bytes(self):
        plan, generated, raw = P.construct()
        self.assertEqual(raw, (HERE / 'public-cut.json').read_bytes())
        self.assertEqual(plan['identity_prefix'], P.NEW_ID)
        self.assertEqual(plan['new_family'], P.NEW_FAMILY)
        self.assertEqual(len(plan['public_inputs']) + len(generated), 941)
        self.assertFalse(plan['private_archive_bodies_read'])
        for name, value in generated.items():
            self.assertEqual(value, (HERE / 'generated' / name).read_bytes())
        role = generated[P.NEW_FAMILY + '/base.py']
        self.assertIn(P.NEW_ENGINE_ALIAS.encode(), role)
        self.assertNotIn(P.OLD_ENGINE_ALIAS.encode(), role)

    def test_public_tool_and_controller_projections_are_exact(self):
        for name, value in T.project().items():
            self.assertEqual(value, (HERE / 'tool' / name).read_bytes())
        self.assertEqual(C.project(), (HERE / 'source_controller.py').read_bytes())
        freeze = json.loads((HERE / 'tool/freeze.json').read_bytes())
        for row in freeze['file_bindings']:
            self.assertEqual(T.sha((HERE / 'tool' / row['path']).read_bytes()), row['sha256'])

    def test_controller_effects_refuse_before_touching_host(self):
        for fn in (S.run, S.recover_consumed):
            with self.subTest(fn=fn.__name__), self.assertRaisesRegex(
                    RuntimeError, 'EFFECT_DISABLED_PENDING_SUCCESSOR_REVIEW'):
                fn()

    def test_docker_vector_uses_persistent_new_family(self):
        argv = S.docker_create_argv('test-label')
        joined = '\n'.join(argv)
        self.assertIn(str(S.ATTEMPT), joined)
        self.assertIn('docker-source-20261020-0002', joined)
        self.assertIn('cal-source-only-20261020-0002-successor1', joined)
        self.assertIn('type=bind,src=' + str(HERE / 'tool') + ',dst=/tool,readonly', joined)
        self.assertNotIn('/tmp/cal-source-only-dev-20261020-0001-exact1', joined)
        self.assertNotIn('docker-source-20261020-0001', joined)
        self.assertIn('--network', argv)
        self.assertIn('none', argv)


if __name__ == '__main__':
    unittest.main()
