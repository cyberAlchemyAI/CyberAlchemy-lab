"""Cold exact-byte check for the disjoint preclaim diagnostic cut."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0002'
NEW = BASE / 'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0003'
PACKAGE = NEW.name


def sha(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected file absent or linked: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check():
    manifest = json.loads((NEW / 'source-manifest.json').read_bytes())
    profile = json.loads((NEW / 'contract-profile.json').read_bytes())
    receipt = json.loads((NEW / 'rebind-receipt.json').read_bytes())
    old_profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    if len(manifest['files']) != 211 or len(profile['files']) != len(old_profile['files']):
        raise ValueError('wrong selected closure count')
    for selected in manifest['files']:
        if sha(ROOT / selected['path']) != selected['sha256']:
            raise ValueError('selected file differs: ' + selected['path'])
    if manifest['profile_binding']['sha256'] != sha(NEW / 'contract-profile.json'):
        raise ValueError('profile binding differs')
    if receipt['successor_manifest_sha256'] != sha(NEW / 'source-manifest.json'):
        raise ValueError('receipt binding differs')
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    changed = []
    for selected in manifest['files']:
        if selected['path'].startswith(new_prefix):
            leaf = selected['path'][len(new_prefix):]
            predecessor = OLD / leaf
            if sha(predecessor) != selected['sha256']:
                changed.append(leaf)
    if changed != ['contract-profile.json','service.py']:
        raise ValueError('diagnostic source delta differs: ' + repr(changed))
    guard = importlib.import_module(PACKAGE + '.guard')
    guard.verify(sha(NEW / 'source-manifest.json'))
    schemas = importlib.import_module(PACKAGE + '.protocol').Schemas(sha(NEW / 'contract-profile.json'))
    schemas.guard()
    return {'manifest_sha256':sha(NEW / 'source-manifest.json'),
            'profile_sha256':sha(NEW / 'contract-profile.json'),
            'selected_rows':len(manifest['files']),'changed_own_files':changed,
            'selected_guard':'passed','schema_guard':'passed'}


if __name__ == '__main__':
    print(json.dumps(check(),sort_keys=True))
