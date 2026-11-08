"""Cold causal checks for the narrowly selected agent-context instance."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v52-t31-agent-context-guard-0003'
SOURCE = 'd14fc1c7e1a4bc941873a5b7fc0adb2dcd95ca16383788df25055e6ee5bb9b72'
PROFILE = 'a7d99f8b9188d1b45de96f6f5b13e2ee1f1fa6ede64121abaf0eb88793e7c0a2'
REF = 'transition:agent-context:context-ready'
TEMPLATE = ROOT / 'docs/proposals/0007-lab-integrated-schema-package/workflows/agent-context.json'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_selector():
    path = API / 'workflow_producer_outputs.py'
    tree = ast.parse(path.read_bytes(), filename=str(path))
    node = next(x for x in tree.body if isinstance(x, ast.FunctionDef)
                and x.name == 'selected_workflow_instance')
    namespace = {'copy': copy, 'sha': digest, 'parse': json.loads,
                 'need': lambda ok, reason: None if ok else (_ for _ in ()).throw(ValueError(reason))}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec',
                 dont_inherit=True), namespace)
    return namespace[node.name]


class SelectedInstance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_raw = TEMPLATE.read_bytes()
        cls.template = json.loads(cls.template_raw)
        cls.profile = {'scope_ref': 'project:cyberalchemy-v2-to-lab-migration',
                       'identity_ref': 'workflow-decision-profile:lab-governance-single-checkpoint',
                       'version_ref': 'workflow-decision-profile:lab-governance-single-checkpoint@1.0.0-candidate.1',
                       'carrier_ref': 'cal.artifact-type.workflow-decision-profile/v1',
                       'byte_sha256': '1' * 64}
        cls.instance = copy.deepcopy(cls.template)
        cls.instance['decision_profile'] = copy.deepcopy(cls.profile)
        cls.instance['transitions'][0]['input_carriers'] = ['cal.artifact-type.work/v1']
        cls.raw = json.dumps(cls.instance, sort_keys=True, separators=(',', ':')).encode()
        cls.binding = {'ref': 'workflow-definition:current-agent-context',
                       'sha256': digest(cls.raw)}
        cls.registry = {'definition_binding': {'path': TEMPLATE.relative_to(ROOT).as_posix(),
                                               'sha256': digest(cls.template_raw)}}
        cls.factory = types.SimpleNamespace(
            source_rows={(cls.registry['definition_binding']['path'],
                          cls.registry['definition_binding']['sha256'])},
            read_public=lambda binding: cls.template_raw,
            plan={'scope_ref': cls.profile['scope_ref']})
        cls.host = types.SimpleNamespace(vault=types.SimpleNamespace(material=lambda binding: cls.raw))
        cls.select = staticmethod(load_selector())

    def test_source_and_profile_closure(self):
        self.assertEqual(digest((API / 'source-manifest.json').read_bytes()), SOURCE)
        self.assertEqual(digest((API / 'contract-profile.json').read_bytes()), PROFILE)
        source = json.loads((API / 'source-manifest.json').read_bytes())
        profile = json.loads((API / 'contract-profile.json').read_bytes())
        self.assertEqual(len(source['files']), 209)
        self.assertEqual(len(profile['files']), 33425)
        selected = {row['path']: row['sha256'] for row in source['files']}
        self.assertEqual(selected[TEMPLATE.relative_to(ROOT).as_posix()], digest(self.template_raw))
        for row in source['files']:
            with self.subTest(path=row['path']):
                self.assertEqual(digest((ROOT / row['path']).read_bytes()), row['sha256'])

    def test_selected_full_package_guard(self):
        name = '_cal_t31_api52_cold_guard_test'
        spec = importlib.util.spec_from_file_location(
            name, API / '__init__.py', submodule_search_locations=[str(API)])
        package = importlib.util.module_from_spec(spec)
        sys.modules[name] = package
        spec.loader.exec_module(package)
        guard = __import__(name + '.guard', fromlist=['verify'])
        guard.verify(SOURCE)

    def test_fixture_principal_is_current_signed_source_principal(self):
        fixture = Path(__file__).with_name('fixture_api52.py')
        tree = ast.parse(fixture.read_bytes(), filename=str(fixture))
        assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == 'PRINCIPAL'
                                  for target in node.targets))
        principal = ast.literal_eval(assignment.value)
        signed = ROOT / ('implementation/lab-runtime/local-host/source8-current-fixture/'
                         'instances/legacy-local-ce4d53a6479188a5/source/packages/0001/artifacts/00.json')
        body = json.loads(signed.read_bytes())
        self.assertEqual(body['kind'], 'principal')
        self.assertEqual(body['payload']['status'], 'active')
        self.assertEqual(principal, body['node_id'])

    def test_private_plan_selects_exact_first_producer_custody(self):
        path = Path(__file__).with_name('install_bridge.py')
        spec = importlib.util.spec_from_file_location('_cal_t31_api52_plan_cold_test', path)
        installer = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = installer
        spec.loader.exec_module(installer)
        with tempfile.TemporaryDirectory(prefix='cal-t31-api52-plan-test-') as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            custody = root / 'producer' / 'workspace'
            custody.mkdir(parents=True, mode=0o700)
            (custody / 'objects').mkdir(mode=0o700)
            cut = {'store_ref': 'test-source', 'branch_ref': 'test-branch',
                   'commit_sequence': 1, 'commit_sha256': '0' * 64,
                   'source_profile_sha256': '0' * 64, 'streams': []}
            material, descriptor, plan = installer.prepare_materials(
                owned_root=root, principal_ref='test-principal', scope_ref='test-scope',
                source_cut=cut, first_api_custody=custody)
            self.assertEqual(len(material), 69)
            self.assertIn(descriptor['ref'], material)
            body = json.loads(material[plan['ref']])
            self.assertEqual(len(body['transitions']), 28)
            route = body['transitions'][REF]
            self.assertEqual(route['producer_entrypoint'], 'AuthorizedAPIProducer.invoke')
            self.assertEqual(route['output_custody']['root'], str(custody))
            self.assertEqual(route['output_custody']['output_roots'], ['objects'])
            negative = root / 'negative'
            negative.mkdir(mode=0o700)
            with self.assertRaisesRegex(ValueError, 'actual private bridge root differs'):
                installer.prepare_materials(
                    owned_root=negative, principal_ref='test-principal',
                    scope_ref='test-scope', source_cut=cut,
                    first_api_custody=ROOT)
            altered = root / 'changed-constructor'
            altered.mkdir(mode=0o700)
            with patch.object(installer, 'PLAN_CONSTRUCTOR_SHA', '0' * 64), self.assertRaisesRegex(
                    ValueError, 'selected bridge source byte differs'):
                installer.prepare_materials(
                    owned_root=altered, principal_ref='test-principal',
                    scope_ref='test-scope', source_cut=cut,
                    first_api_custody=custody)

    def test_positive_instance(self):
        self.assertEqual(self.select(self.host, self.factory, REF,
                                     self.binding, self.registry), self.instance)

    def test_public_placeholder_refused(self):
        with self.assertRaisesRegex(ValueError, 'uninstantiated'):
            self.select(self.host, self.factory, REF,
                        self.registry['definition_binding'], self.registry)

    def test_wrong_input_and_state_refused(self):
        for mutation in ('input', 'state', 'output'):
            changed = copy.deepcopy(self.instance)
            transition = changed['transitions'][0]
            if mutation == 'input':
                transition['input_carriers'] = ['cal.artifact-type.agent-assignment/v1']
            elif mutation == 'state':
                transition['to_state'] = 'session-ready'
            else:
                transition['output_carriers'] = ['cal.artifact-type.context-view/v1']
            raw = json.dumps(changed, sort_keys=True, separators=(',', ':')).encode()
            host = types.SimpleNamespace(vault=types.SimpleNamespace(material=lambda binding: raw))
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'differs outside'):
                self.select(host, self.factory, REF, {'ref': 'candidate', 'sha256': digest(raw)}, self.registry)

    def test_wrong_template_or_profile_refused(self):
        factory = copy.copy(self.factory)
        factory.read_public = lambda binding: self.template_raw + b' '
        with self.assertRaisesRegex(ValueError, 'template bytes changed'):
            self.select(self.host, factory, REF, self.binding, self.registry)
        changed = copy.deepcopy(self.instance)
        changed['decision_profile']['scope_ref'] = 'project:foreign'
        raw = json.dumps(changed, sort_keys=True, separators=(',', ':')).encode()
        host = types.SimpleNamespace(vault=types.SimpleNamespace(material=lambda binding: raw))
        with self.assertRaisesRegex(ValueError, 'current decision-profile'):
            self.select(host, self.factory, REF, {'ref': 'candidate', 'sha256': digest(raw)}, self.registry)


if __name__ == '__main__':
    unittest.main()
