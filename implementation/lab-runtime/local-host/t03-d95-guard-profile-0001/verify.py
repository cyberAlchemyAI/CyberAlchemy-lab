"""Cold exact-byte and behavioral-guard check for one profiling cut."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0003'
NEW = BASE / 'api-integration-v33-t03-one-lesson-native-v4-guard-profile-0001'
PACKAGE = NEW.name
EXPECTED_MANIFEST = 'd2cc82418a643118d27bd5c539a0aca794cde1018856c0ac99bf381b3e875eb7'
EXPECTED_PROFILE = 'e509e783065ce9650756b8a40a1bb6c0dcc31d84393b16c137bba95ff46f47d5'


def sha(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected file absent or linked: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check():
    if sha(NEW / 'source-manifest.json') != EXPECTED_MANIFEST:
        raise ValueError('manifest changed')
    if sha(NEW / 'contract-profile.json') != EXPECTED_PROFILE:
        raise ValueError('profile changed')
    manifest = json.loads((NEW / 'source-manifest.json').read_bytes())
    profile = json.loads((NEW / 'contract-profile.json').read_bytes())
    receipt = json.loads((NEW / 'rebind-receipt.json').read_bytes())
    if len(manifest['files']) != 211 or len(profile['files']) != len(json.loads((OLD / 'contract-profile.json').read_bytes())['files']):
        raise ValueError('selected closure count differs')
    for selected in manifest['files']:
        if sha(ROOT / selected['path']) != selected['sha256']:
            raise ValueError('selected row differs: ' + selected['path'])
    if manifest['profile_binding']['sha256'] != EXPECTED_PROFILE:
        raise ValueError('profile binding differs')
    if receipt['successor_manifest_sha256'] != EXPECTED_MANIFEST:
        raise ValueError('receipt binding differs')
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    changed = []
    for selected in manifest['files']:
        if selected['path'].startswith(new_prefix):
            leaf = selected['path'][len(new_prefix):]
            if sha(OLD / leaf) != selected['sha256']:
                changed.append(leaf)
    if sorted(changed) != ['contract-profile.json', 't03_lesson_host.py']:
        raise ValueError('profile source delta differs: ' + repr(changed))
    guard = importlib.import_module(PACKAGE + '.guard')
    guard.verify(EXPECTED_MANIFEST)
    schemas = importlib.import_module(PACKAGE + '.protocol').Schemas(EXPECTED_PROFILE)
    schemas.guard()
    return {'manifest_sha256': EXPECTED_MANIFEST, 'profile_sha256': EXPECTED_PROFILE,
            'selected_rows': len(manifest['files']), 'changed_own_files': changed,
            'selected_guard': 'passed', 'schema_guard': 'passed'}


if __name__ == '__main__':
    print(json.dumps(check(), sort_keys=True))
