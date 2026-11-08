"""Read-only T22/T06 API43 cut and retained SDK/branch refusal checks."""

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API = BASE / 'api-integration-v43-r03-0005-composite-0001'
SDK = BASE / 'composite-operator-v1-current-api43-t22-0001/revision-0001'
BRANCH = (ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/'
          'branch-fixtures-current-api43-t22-0001/revision-0001')
SOURCE = '22cd380b7544721c6519c869e430a99cbb6b84c3e863a425125f3d9944981560'
PROFILE = 'bc660fbd0ac6055dc49b008c9c46c4b09925e1e3cd8795940a0563348b04a2e6'
SDK_SHA = '39f3593f496dea3e86fb6c152a4853568c39b0bc4b46648bd80cadac965e194a'
BRANCH_SHA = '50572a2db800eb605f4b6f7d6704f55a32838850f157b4c2135da0da79a2d9a4'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CompositeCold(unittest.TestCase):
    def test_01_api43_source_profile_and_wrong_pins(self):
        name = '_cal_api43_t22_t06_cold_test'
        if name not in sys.modules:
            spec = importlib.util.spec_from_file_location(
                name, API / '__init__.py', submodule_search_locations=[str(API)])
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        guard = __import__(name + '.guard', fromlist=['verify'])
        protocol = __import__(name + '.protocol', fromlist=['Schemas'])
        self.assertEqual(len(guard.verify(SOURCE)['files']), 207)
        self.assertEqual(len(protocol.Schemas(PROFILE).profile['files']), 33434)
        with self.assertRaises(ValueError):
            guard.verify('0' * 64)
        with self.assertRaises(ValueError):
            protocol.Schemas('0' * 64)

    def test_02_sdk_manifest_and_captured_bootstrap(self):
        self.assertEqual(sha(SDK / 'source-manifest.json'), SDK_SHA)
        manifest = json.loads((SDK / 'source-manifest.json').read_bytes())
        expected = {row(SDK / name)['path'] for name in
                    ('bootstrap.py', 'composite.py', 'control.py', 'framing.py',
                     'launch.py', 'composite.config.schema.json')}
        self.assertEqual({item['path'] for item in manifest['files']}, expected)
        for item in manifest['files']:
            target = ROOT / item['path']
            self.assertEqual((sha(target), target.stat().st_size),
                             (item['sha256'], item['size_bytes']))
        bootstrap = load(SDK / 'bootstrap.py', '_cal_api43_t22_bootstrap_cold')
        modules = {name: {'path': str(SDK / (name + '.py')),
                          'sha256': sha(SDK / (name + '.py')),
                          'source_base64': base64.b64encode((SDK / (name + '.py')).read_bytes()).decode()}
                   for name in ('bootstrap', 'control', 'framing', 'composite')}
        payload = {'schema_version': 'lab-captured-SDK-bootstrap/v1-candidate',
                   'root': str(SDK), 'modules': modules,
                   'manifest': {'path': str(SDK / 'source-manifest.json'),
                                'sha256': SDK_SHA,
                                'source_base64': base64.b64encode((SDK / 'source-manifest.json').read_bytes()).decode()}}
        self.assertEqual(bootstrap.verify(payload), ROOT)
        changed = copy.deepcopy(payload)
        changed['modules']['composite']['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            bootstrap.verify(changed)

    def test_03_branch_selection_and_wrong_pin(self):
        self.assertEqual(sha(BRANCH / 'driver-selection.json'), BRANCH_SHA)
        selected = json.loads((BRANCH / 'driver-selection.json').read_bytes())
        self.assertEqual(len(selected['files']), 7)
        self.assertEqual({row(BRANCH / name)['path'] for name in
                          ('prepare_branches.py', 'drive_operator.py')} <=
                         {item['path'] for item in selected['files']}, True)
        for item in selected['files']:
            self.assertEqual(sha(ROOT / item['path']), item['sha256'])
        preparer = load(BRANCH / 'prepare_branches.py', '_cal_api43_t22_preparer_cold')
        self.assertEqual(preparer.guard_selection(BRANCH / 'driver-selection.json', BRANCH_SHA), selected)
        with self.assertRaises(ValueError):
            preparer.guard_selection(BRANCH / 'driver-selection.json', '0' * 64)

    def test_04_actual_selected_software_guard_and_wrong_api(self):
        sys.path.insert(0, str(SDK))
        try:
            import composite as sdk
            bindings = [row(path) for path in sorted([
                *SDK.glob('*.py'),
                *(API / name for name in ('guard.py', '__init__.py', 'source-manifest.json',
                                          'contract-profile.json', 'integration-members.json'))])]
            config = {'source': {'directory': str(API), 'source_sha256': SOURCE,
                                 'profile_sha256': PROFILE,
                                 'members_sha256': sha(API / 'integration-members.json'),
                                 'bootstrap_bindings': bindings}, 'dependencies': {}}
            with mock.patch.object(sdk, 'dependency_guard', return_value=1010):
                profile, members = sdk.software_guard(config)
                self.assertEqual((len(profile['implemented_operations']), len(profile['files'])),
                                 (34, 33434))
                self.assertEqual(set(members['members']), {'actions', 'governance'})
                old = copy.deepcopy(config)
                old['source']['directory'] = str(BASE / 'api-integration-v42-r03-0005-current-0001')
                with self.assertRaises(ValueError):
                    sdk.software_guard(old)
        finally:
            sys.path.remove(str(SDK))

    def test_05_driver_exact_sdk_and_config(self):
        driver = load(BRANCH / 'drive_operator.py', '_cal_api43_t22_driver_cold')
        with tempfile.TemporaryDirectory(prefix='cal-T06-branch-fixtures-') as location:
            record = {'root': location, 'source_sha256': SOURCE,
                      'profile_sha256': PROFILE, 'branches': {}, 'issuers': {}}
            args = argparse.Namespace(sdk_directory=str(SDK), sdk_source_sha256=SDK_SHA,
                                      provisioning_path='docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result.json',
                                      provisioning_sha256='c' * 64)
            config, path, digest = driver.configure(record, args)
            self.assertEqual(config['source']['directory'], str(API))
            self.assertEqual(config['source']['members_sha256'], sha(API / 'integration-members.json'))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
        with tempfile.TemporaryDirectory(prefix='cal-T06-branch-fixtures-') as location:
            args.sdk_directory = str(BASE / 'composite-operator-v1-current-api40-0001/revision-0001')
            with self.assertRaises(ValueError):
                driver.configure({**record, 'root': location}, args)
            self.assertFalse((Path(location) / 'operator-config.json').exists())

    def test_06_profile_selects_exact_ten_t06_rows(self):
        profile = json.loads((API / 'contract-profile.json').read_bytes())
        selected = {item['path']: item['sha256'] for item in profile['files']}
        paths = [SDK / 'source-manifest.json',
                 *(SDK / name for name in ('bootstrap.py', 'composite.py', 'control.py',
                                          'framing.py', 'launch.py', 'composite.config.schema.json')),
                 BRANCH / 'driver-selection.json', BRANCH / 'prepare_branches.py',
                 BRANCH / 'drive_operator.py']
        self.assertEqual(len(paths), 10)
        for path in paths:
            self.assertEqual(selected.get(row(path)['path']), sha(path))
        self.assertEqual(profile['integration_members_binding'], row(API / 'integration-members.json'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
