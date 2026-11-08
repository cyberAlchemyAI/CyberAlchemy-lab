"""Build a disjoint Action member accepting only the selected API45 profile."""

import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = INTERFACE / 'api-action-integration-v7-current-t06-0001'
NEW = INTERFACE / 'api-action-integration-v8-current-t17-0001'
OLD_SOURCE = '9f8fdb8dea1545fd7767853ba867f6d10c83ea7c8c50df047c054632eed15900'
OLD_PROFILE = 'b3767b2b1ececc73ce24ea7d55924956feab8a5f3b563c3359391122a95b3576'
OLD_API_PROFILE_REF = 'product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json'
NEW_API_PROFILE_REF = 'product/lab/release-candidates/v1/interface/api-integration-v45-r03-0005-coverage-0001/contract-profile.json'


def sha(path):
    if not path.is_file() or path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('selected Action origin differs: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def main():
    if NEW.exists():
        raise ValueError('versioned Action successor already exists')
    if sha(OLD / 'source-manifest.json') != OLD_SOURCE or sha(OLD / 'contract-profile.json') != OLD_PROFILE:
        raise ValueError('frozen Action predecessor differs')
    old_manifest = json.loads((OLD / 'source-manifest.json').read_bytes())
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    own = [row for row in old_manifest['files'] if row['path'].startswith(old_prefix)]
    if len(own) != 16 or len(old_manifest['files']) != 39:
        raise ValueError('Action source inventory differs')
    actual = {p.relative_to(OLD).as_posix() for p in OLD.iterdir() if p.is_file() and p.name != 'source-manifest.json'}
    if actual != {row['path'][len(old_prefix):] for row in own}:
        raise ValueError('Action package has unselected or missing files')
    old_deps = (OLD / 'dependencies.py').read_text()
    if old_deps.count(OLD_API_PROFILE_REF) != 1 or NEW_API_PROFILE_REF in old_deps:
        raise ValueError('Action profile selector premise differs')
    stage = ROOT / 'implementation/lab-runtime/local-host/t22-api-selector-recut-0001/working/action-v8-stage'
    if stage.exists():
        raise ValueError('Action stage already exists')
    stage.mkdir(parents=True, mode=0o700)
    try:
        for row in own:
            name = row['path'][len(old_prefix):]
            src = OLD / name
            if sha(src) != row['sha256']:
                raise ValueError('frozen Action row differs: ' + name)
            shutil.copy2(src, stage / name, follow_symlinks=False)
        (stage / 'dependencies.py').write_text(old_deps.replace(OLD_API_PROFILE_REF, NEW_API_PROFILE_REF))
        old_manifest['files'] = sorted([
            {'path': row['path'].replace(old_prefix, new_prefix, 1),
             'sha256': sha(stage / row['path'][len(old_prefix):])}
            if row['path'].startswith(old_prefix) else row
            for row in old_manifest['files']
        ], key=lambda row: row['path'])
        old_manifest['predecessor_source_manifest_binding'] = {
            'path': (OLD / 'source-manifest.json').relative_to(ROOT).as_posix(),
            'sha256': OLD_SOURCE,
        }
        old_manifest['schema_version'] = 'lab-action-integration-v8-current-t17-source/v1-candidate'
        write(stage / 'source-manifest.json', old_manifest)
        os.rename(stage, NEW)
    except BaseException:
        shutil.rmtree(stage)
        raise
    print(json.dumps({'action_v8_source_sha256': sha(NEW / 'source-manifest.json'),
                      'action_v8_profile_sha256': sha(NEW / 'contract-profile.json'),
                      'source_rows': len(old_manifest['files'])}, sort_keys=True))


if __name__ == '__main__':
    main()
