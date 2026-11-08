"""Bounded API45/Action v8 source and profile selection checks."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
API = INTERFACE / 'api-integration-v45-r03-0005-coverage-0001'
ACTION = INTERFACE / 'api-action-integration-v8-current-t17-0001'
SOURCE_SHA = 'd5a57418f84729a085a5a4b335ddcf08ec65de912132a9e2327e66c65dae395d'
PROFILE_SHA = '5635f3d3b5f65852aae01cbd85268802aa42d92b3037fbc70a7694116ed4f205'
ACTION_SHA = '3b20c6bf6039c5ebf4e2ea056ac5651b465913b13bc133277e039ed60bc37d53'
OLD_PROFILE = INTERFACE / 'api-integration-v44-r03-0005-coverage-0001/contract-profile.json'


def sha(path):
    if not path.is_file() or path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('selected origin differs')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_dependencies():
    path = ACTION / 'dependencies.py'
    selected = json.loads((ACTION / 'source-manifest.json').read_bytes())
    row = next(row for row in selected['files'] if row['path'] == path.relative_to(ROOT).as_posix())
    if sha(path) != row['sha256'] or sha(ACTION / 'source-manifest.json') != ACTION_SHA:
        raise ValueError('selected Action dependency bytes differ')
    spec = importlib.util.spec_from_file_location('_cal_selected_action_v8_cold_dependencies', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class API45ActionCold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dependencies = selected_dependencies()
        cls.profile_binding = {'ref': (API / 'contract-profile.json').relative_to(ROOT).as_posix(),
                               'sha256': PROFILE_SHA}

    def test_exact_api_source_and_member(self):
        path = API / 'guard.py'
        spec = importlib.util.spec_from_file_location('_cal_selected_api45_cold_guard', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        selected = module.verify(SOURCE_SHA)
        self.assertEqual(len(selected['files']), 207)
        profile = json.loads((API / 'contract-profile.json').read_bytes())
        members = json.loads((API / 'integration-members.json').read_bytes())
        self.assertEqual(sha(API / 'contract-profile.json'), PROFILE_SHA)
        self.assertEqual(members['members']['actions']['directory'], ACTION.name)
        self.assertEqual(members['members']['actions']['source_sha256'], ACTION_SHA)
        self.assertEqual(profile['integration_members_binding']['sha256'], sha(API / 'integration-members.json'))

    def test_selected_action_guard_accepts_current_profile(self):
        # The guard properly refuses this unselected test module when called
        # in-process. Use a code-only child to exercise the selected route.
        code = (
            'import importlib.util;from pathlib import Path;'
            f'p=Path({str(ACTION / "dependencies.py")!r});'
            's=importlib.util.spec_from_file_location("_cal_action_v8_selected",p);'
            'm=importlib.util.module_from_spec(s);s.loader.exec_module(m);'
            f'm.guard({ACTION_SHA!r},integration_profile_binding={self.profile_binding!r})'
        )
        child = subprocess.run([sys.executable, '-B', '-c', code], cwd=ROOT,
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                               capture_output=True, timeout=60)
        self.assertEqual(child.returncode, 0, child.stderr.decode()[-1000:])

    def test_old_profile_origin_refused(self):
        old = {'ref': OLD_PROFILE.relative_to(ROOT).as_posix(), 'sha256': sha(OLD_PROFILE)}
        with self.assertRaisesRegex(ValueError, 'current independently selected Action environment differs'):
            self.dependencies.guard(ACTION_SHA, integration_profile_binding=old)

    def test_current_profile_wrong_digest_refused(self):
        changed = {**self.profile_binding, 'sha256': '0' * 64}
        with self.assertRaisesRegex(ValueError, 'current Action integration profile differs'):
            self.dependencies.guard(ACTION_SHA, integration_profile_binding=changed)


if __name__ == '__main__':
    unittest.main(verbosity=2)
