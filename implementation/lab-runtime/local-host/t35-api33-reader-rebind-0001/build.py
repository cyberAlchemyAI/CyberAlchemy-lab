"""Rebind one disjoint API33 successor to the selected current Source8 reader class."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v33-current-0001'
NEW = BASE / 'api-integration-v33-t35-current-reader-0001'
OLD_SOURCE_SHA = 'e400703a2ace9ea1899d7abf15023632a83235e1e15f5459970b1ed8d12a37dd'
OLD_PROFILE_SHA = 'c86a04159a99d607f15f42078ae64b108ef5007e121f830d54174f0167b8813a'
OLD_MEMBERS_SHA = '64931c417e6738d82c1c4cb819bb660237aab038bf6474594d421d8991f6d7d1'
OLD_BRIDGE_SHA = '29c0deed3087e6bd54e5369e227dca87324bb3f7f501cc8b9d666f517f09e085'
NEW_BRIDGE_SHA = '4a69d6f5ef55efc989bc97d4f73084e66f78433fe6dfa7972e679e91bcb98ce2'


def sha(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing or linked selected file: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def row(path):
    return {'path': rel(path), 'sha256': sha(path)}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def verify_bridge_edit(old_bridge, new_bridge):
    if (old_bridge.count(b"class_name='CurrentFixtureReader'") != 1 or
            old_bridge.replace(b"class_name='CurrentFixtureReader'", b"class_name='SelectedReader'") != new_bridge):
        raise ValueError('reader class is not the sole source change')


def main():
    if (sha(OLD / 'source-manifest.json') != OLD_SOURCE_SHA or
            sha(OLD / 'contract-profile.json') != OLD_PROFILE_SHA or
            sha(OLD / 'integration-members.json') != OLD_MEMBERS_SHA):
        raise ValueError('frozen API33 predecessor changed')
    if (sha(NEW / 'source-manifest.json') != OLD_SOURCE_SHA or
            sha(NEW / 'contract-profile.json') != OLD_PROFILE_SHA or
            sha(NEW / 'integration-members.json') != OLD_MEMBERS_SHA):
        raise ValueError('successor is not an otherwise untouched copy')
    old_prefix = rel(OLD) + '/'
    source = json.loads((OLD / 'source-manifest.json').read_bytes())
    own = {item['path'][len(old_prefix):]: item['sha256'] for item in source['files']
           if item['path'].startswith(old_prefix)}
    actual = {p.relative_to(NEW).as_posix() for p in NEW.rglob('*')
              if p.is_file() and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    if set(own) != actual or len(own) == 0:
        raise ValueError('copied successor closure differs')
    for filename, digest in own.items():
        if filename != 'contract-profile.json' and filename != 'source_bridge.py' and sha(NEW / filename) != digest:
            raise ValueError('unexpected copied file changed: ' + filename)
    old_bridge = (OLD / 'source_bridge.py').read_bytes()
    new_bridge = (NEW / 'source_bridge.py').read_bytes()
    if sha(OLD / 'source_bridge.py') != OLD_BRIDGE_SHA or sha(NEW / 'source_bridge.py') != NEW_BRIDGE_SHA:
        raise ValueError('reader bridge pin changed')
    verify_bridge_edit(old_bridge, new_bridge)
    profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    profile['files'] = [row(NEW / item['path'][len(old_prefix):])
                        if item['path'].startswith(old_prefix) else item for item in profile['files']]
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = 'T35 current Source8 one-call reader-class successor; no API33 release admission or complete T35 qualification.'
    write(NEW / 'contract-profile.json', profile)
    source['files'] = sorted((row(NEW / item['path'][len(old_prefix):])
                              if item['path'].startswith(old_prefix) else item for item in source['files']),
                             key=lambda item: item['path'])
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = {'path': rel(OLD / 'source-manifest.json'), 'sha256': OLD_SOURCE_SHA}
    source['claim_ceiling'] = profile['claim_ceiling']
    write(NEW / 'source-manifest.json', source)
    write(NEW / 'rebind-receipt.json', {
        'schema_version': 'lab-T35-api33-current-reader-rebind/v1-candidate',
        'successor_package': rel(NEW),
        'successor_manifest_sha256': sha(NEW / 'source-manifest.json'),
        'predecessor_source_manifest_binding': source['predecessor_source_manifest_binding'],
        'successor_source_manifest_binding': row(NEW / 'source-manifest.json'),
        'successor_profile_binding': source['profile_binding'],
        'source_bridge_binding': row(NEW / 'source_bridge.py'),
        'reader_class': 'SelectedReader', 'authority_effect': 'none',
        'claim_ceiling': source['claim_ceiling'], 'current_native_call_tested': False})
    print(json.dumps({'source_manifest_sha256': sha(NEW / 'source-manifest.json'),
                      'profile_sha256': sha(NEW / 'contract-profile.json'),
                      'source_bridge_sha256': sha(NEW / 'source_bridge.py'),
                      'source_files': len(source['files']), 'profile_files': len(profile['files'])}, sort_keys=True))


if __name__ == '__main__':
    main()
