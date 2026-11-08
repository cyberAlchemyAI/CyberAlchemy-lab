"""One-shot disjoint API41 current reader-origin repair; no predecessor mutation."""
import hashlib
import json
from pathlib import Path


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v40-current-t06-0001'
NEW = BASE / 'api-integration-v41-current-source8-0001'
OLD_SOURCE_SHA = '45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219'
OLD_PROFILE_SHA = 'cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614'
OLD_MEMBERS_SHA = '625ccd27d3a18166dbdaa837c3ec9395491853cb28cef5ff4e05392c99365732'


def sha(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing or linked selected input: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def row(path):
    return {'path': rel(path), 'sha256': sha(path)}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def main():
    if (sha(OLD / 'source-manifest.json') != OLD_SOURCE_SHA or
            sha(OLD / 'contract-profile.json') != OLD_PROFILE_SHA or
            sha(OLD / 'integration-members.json') != OLD_MEMBERS_SHA):
        raise ValueError('frozen API40 predecessor changed')
    if (sha(NEW / 'source-manifest.json') != OLD_SOURCE_SHA or
            sha(NEW / 'contract-profile.json') != OLD_PROFILE_SHA or
            sha(NEW / 'integration-members.json') != OLD_MEMBERS_SHA):
        raise ValueError('API41 is not an untouched copied predecessor')
    old_prefix = rel(OLD) + '/'
    actual = {p.relative_to(NEW).as_posix() for p in NEW.rglob('*')
              if p.is_file() and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    source = json.loads((OLD / 'source-manifest.json').read_bytes())
    own = {item['path'][len(old_prefix):] for item in source['files'] if item['path'].startswith(old_prefix)}
    if own != actual or not own:
        raise ValueError('API41 copied executable closure differs')
    profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    mapped = []
    for item in profile['files']:
        if item['path'].startswith(old_prefix):
            mapped.append(row(NEW / item['path'][len(old_prefix):]))
        else:
            mapped.append(item)
    if len({item['path'] for item in mapped}) != len(mapped):
        raise ValueError('API41 profile path closure not unique')
    profile['files'] = mapped
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = 'Current Source8 guarded-read successor only; historical Source5 and current T06 composite unqualified.'
    write(NEW / 'contract-profile.json', profile)
    changed = []
    for item in source['files']:
        if item['path'].startswith(old_prefix):
            changed.append(row(NEW / item['path'][len(old_prefix):]))
        else:
            changed.append(item)
    source['files'] = sorted(changed, key=lambda item: item['path'])
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = {'path': rel(OLD / 'source-manifest.json'), 'sha256': OLD_SOURCE_SHA}
    source['claim_ceiling'] = 'Current Source8 guarded-read successor only; historical Source5 and current T06 composite unqualified.'
    write(NEW / 'source-manifest.json', source)
    receipt = {
        'schema_version': 'lab-API41-current-Source8-reader-origin-rebind/v1-candidate',
        'predecessor_source_manifest_binding': source['predecessor_source_manifest_binding'],
        'successor_source_manifest_binding': row(NEW / 'source-manifest.json'),
        'successor_profile_binding': source['profile_binding'],
        'source_bridge_binding': row(NEW / 'source_bridge.py'),
        'authority_effect': 'none',
        'actual_owner_outcome': None,
        'claim_ceiling': source['claim_ceiling'],
        'current_native_guarded_read_tested': False,
    }
    write(NEW / 'rebind-receipt.json', receipt)
    print(json.dumps({'source_manifest_sha256': sha(NEW / 'source-manifest.json'),
                      'profile_sha256': sha(NEW / 'contract-profile.json'),
                      'source_bridge_sha256': sha(NEW / 'source_bridge.py'),
                      'source_files': len(source['files']), 'profile_files': len(profile['files'])}, sort_keys=True))


if __name__ == '__main__':
    main()
