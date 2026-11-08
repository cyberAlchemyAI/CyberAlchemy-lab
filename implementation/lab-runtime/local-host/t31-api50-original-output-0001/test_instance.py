"""Cold causal checks for the narrowly selected agent-context instance."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import types
import unittest

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v50-t31-agent-context-instance-0001'
SOURCE = '7412a2363cfa3cefdaf642ead146044ce7a83ad23fdaeb78b943b1d1921645a8'
PROFILE = '74f0da0ebefb4ffcba5d2551914aa5b154d3a83006d4b936aa8db71975e477c1'
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
        self.assertEqual(len(source['files']), 208)
        self.assertEqual(len(profile['files']), 33425)
        for row in source['files']:
            with self.subTest(path=row['path']):
                self.assertEqual(digest((ROOT / row['path']).read_bytes()), row['sha256'])

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
