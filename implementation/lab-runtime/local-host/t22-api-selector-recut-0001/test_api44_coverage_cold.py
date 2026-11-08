"""Cold checks for the disjoint API44 same-child coverage candidate."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v43-r03-0005-composite-0001'
API = BASE / 'api-integration-v44-r03-0005-coverage-0001'
SDK = BASE / 'composite-operator-v1-current-api44-t17-0001/revision-0001'
BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api44-t17-0001/revision-0001'
OLD_SDK = BASE / 'composite-operator-v1-current-api43-t22-0001/revision-0001'
OLD_BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api43-t22-0001/revision-0001'
SOURCE_SHA = '70e23e3cb1b3abe32ac59803ed70fc00485cc0f3531c85eb3d5168331cac3d60'
PROFILE_SHA = '28dbdca0d88a7b38e7e384a4f6ef48ecde3476cac8cf006a174197cd668d011f'
SDK_SHA = '22c70d2ff977741b5a7043fa826dfb754c50542be7b4d1f6477db7dcd3ef9bcd'
BRANCH_SHA = 'ea8e887427340cf52974c55b921c9fc1d405973a106e1742f6ea54283c4dd1f9'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


class API44Cold(unittest.TestCase):
    def test_01_exact_source_profile_and_closed_local_copy(self):
        self.assertEqual(sha(API / 'source-manifest.json'), SOURCE_SHA)
        self.assertEqual(sha(API / 'contract-profile.json'), PROFILE_SHA)
        source = json.loads((API / 'source-manifest.json').read_bytes())
        self.assertEqual(source['profile_binding'], {'path': relative(API / 'contract-profile.json'), 'sha256': PROFILE_SHA})
        self.assertEqual(len(source['files']), 207)
        self.assertEqual(len({row['path'] for row in source['files']}), 207)
        for row in source['files']:
            p = ROOT / row['path']
            self.assertEqual(sha(p), row['sha256'])
        old = json.loads((OLD / 'source-manifest.json').read_bytes())
        old_prefix, new_prefix = relative(OLD) + '/', relative(API) + '/'
        old_local = {row['path'][len(old_prefix):]: row['sha256'] for row in old['files'] if row['path'].startswith(old_prefix)}
        new_local = {row['path'][len(new_prefix):]: row['sha256'] for row in source['files'] if row['path'].startswith(new_prefix)}
        self.assertEqual(len(old_local), 201)
        self.assertEqual(new_local.keys(), old_local.keys())
        self.assertEqual({k: v for k, v in new_local.items() if k != 'contract-profile.json'},
                         {k: v for k, v in old_local.items() if k != 'contract-profile.json'})

    def test_02_profile_replaces_exact_ten_t06_rows(self):
        new = json.loads((API / 'contract-profile.json').read_bytes())
        old = json.loads((OLD / 'contract-profile.json').read_bytes())
        old_sdk = json.loads((OLD_SDK / 'source-manifest.json').read_bytes())
        old_branch = json.loads((OLD_BRANCH / 'driver-selection.json').read_bytes())
        obsolete = {relative(OLD_SDK / 'source-manifest.json'), *(row['path'] for row in old_sdk['files']),
                    relative(OLD_BRANCH / 'driver-selection.json'),
                    relative(OLD_BRANCH / 'prepare_branches.py'), relative(OLD_BRANCH / 'drive_operator.py')}
        sdk = json.loads((SDK / 'source-manifest.json').read_bytes())
        branch = json.loads((BRANCH / 'driver-selection.json').read_bytes())
        additions = {relative(SDK / 'source-manifest.json'), *(row['path'] for row in sdk['files']),
                     relative(BRANCH / 'driver-selection.json'), relative(BRANCH / 'prepare_branches.py'),
                     relative(BRANCH / 'drive_operator.py')}
        self.assertEqual(len(obsolete), 10)
        self.assertEqual(len(additions), 10)
        old_paths = {row['path'] for row in old['files']}
        new_paths = {row['path'] for row in new['files']}
        old_prefix, new_prefix = relative(OLD) + '/', relative(API) + '/'
        translated = {new_prefix + p[len(old_prefix):] if p.startswith(old_prefix) else p
                      for p in old_paths - obsolete}
        self.assertEqual(new_paths, translated | additions)
        self.assertEqual(len(new['files']), 33434)
        self.assertEqual(len(new_paths), 33434)
        for row in new['files']:
            if row['path'] in additions:
                self.assertEqual(sha(ROOT / row['path']), row['sha256'])

    def test_03_sdk_and_branch_are_closed_and_current(self):
        self.assertEqual(sha(SDK / 'source-manifest.json'), SDK_SHA)
        self.assertEqual(sha(BRANCH / 'driver-selection.json'), BRANCH_SHA)
        sdk = json.loads((SDK / 'source-manifest.json').read_bytes())
        branch = json.loads((BRANCH / 'driver-selection.json').read_bytes())
        self.assertEqual({Path(row['path']).name for row in sdk['files']},
                         {'bootstrap.py', 'composite.py', 'control.py', 'framing.py', 'launch.py', 'composite.config.schema.json'})
        self.assertEqual(len(branch['files']), 7)
        for row in sdk['files'] + branch['files']:
            self.assertEqual(sha(ROOT / row['path']), row['sha256'])
        self.assertIn(relative(BRANCH / 'drive_operator.py'), {row['path'] for row in branch['files']})

    def test_04_driver_literal_coverage_plan_and_no_false_completion(self):
        raw = (BRANCH / 'drive_operator.py').read_text()
        self.assertIn("('artifact.query', 'positive')", raw)
        self.assertIn("('artifact.inspect', 'wrong-context')", raw)
        self.assertIn("('lab.status', 'wrong-scope')", raw)
        self.assertIn("('catalog.get', 'wrong-context')", raw)
        self.assertIn("'case':'wrong-context-refusal'", raw)
        self.assertIn("'whole_API_qualified': False", raw)
        self.assertNotIn('api-integration-v40-current-t06-0001', raw)
        self.assertNotIn('api-integration-v43-r03-0005-composite-0001', raw)

if __name__ == '__main__':
    unittest.main()
