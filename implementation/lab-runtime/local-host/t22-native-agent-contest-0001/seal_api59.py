"""Seal the disjoint complete-source successor from API58 bytes."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v58-t22-single-dispatch-0001'
NEW = BASE / 'api-integration-v59-t22-complete-source-freshness-0001'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def main():
    old_source = json.loads((OLD / 'source-manifest.json').read_bytes())
    old_profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    old_prefix = rel(OLD) + '/'
    new_prefix = rel(NEW) + '/'
    new_local = {rel(p): p for p in NEW.rglob('*') if p.is_file()
                 and p.name not in ('source-manifest.json', 'rebind-receipt.json')
                 and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    old_local = {r['path'] for r in old_source['files'] if r['path'].startswith(old_prefix)}
    expected = {new_prefix + p[len(old_prefix):] for p in old_local}
    if set(new_local) != expected:
        raise ValueError('API59 inventory differs from exact API58 successor')

    def rebind(row):
        path = row['path']
        if path.startswith(old_prefix):
            local = new_prefix + path[len(old_prefix):]
            return {'path': local, 'sha256': sha(new_local[local])}
        return row

    old_profile['files'] = sorted([rebind(r) for r in old_profile['files']],
                                  key=lambda r: r['path'])
    old_profile['integration_members_binding'] = {
        'path': new_prefix + 'integration-members.json',
        'sha256': sha(NEW / 'integration-members.json')}
    old_profile['claim_ceiling'] = (
        'T22 local complete source freshness and native Agent challenge candidate; actual submission '
        'requires a live signed grant and exact candidate evidence. No owner '
        'resolution, canonical admission or authority effect is conferred.')
    save(NEW / 'contract-profile.json', old_profile)

    old_source['files'] = sorted([rebind(r) for r in old_source['files']],
                                 key=lambda r: r['path'])
    profile_path = new_prefix + 'contract-profile.json'
    for row in old_source['files']:
        if row['path'] == profile_path:
            row['sha256'] = sha(NEW / 'contract-profile.json')
    old_source['profile_binding'] = {'path': profile_path,
                                     'sha256': sha(NEW / 'contract-profile.json')}
    old_source['predecessor_source_manifest_binding'] = {
        'path': old_prefix + 'source-manifest.json',
        'sha256': sha(OLD / 'source-manifest.json')}
    old_source['claim_ceiling'] = old_profile['claim_ceiling']
    save(NEW / 'source-manifest.json', old_source)
    receipt = {
        'schema_version': 'lab-T22-Agent-native-API59-successor/v1-candidate',
        'successor_package': rel(NEW),
        'successor_manifest_sha256': sha(NEW / 'source-manifest.json'),
        'predecessor_source_manifest_binding': old_source['predecessor_source_manifest_binding'],
        'successor_source_manifest_binding': {'path': new_prefix + 'source-manifest.json',
                                              'sha256': sha(NEW / 'source-manifest.json')},
        'successor_profile_binding': old_source['profile_binding'],
        'signed_family_chain_binding': {
            'path': rel(Path(__file__).parent / 'CHAIN-0001.json'),
            'sha256': sha(Path(__file__).parent / 'CHAIN-0001.json')},
        'source_files': len(old_source['files']),
        'profile_files': len(old_profile['files']),
        'authority_effect': 'none',
        'challenge_submitted': False,
        'challenge_resolved': False,
        'claim_ceiling': old_source['claim_ceiling'],
    }
    save(NEW / 'rebind-receipt.json', receipt)
    print(json.dumps({'source_sha256': sha(NEW / 'source-manifest.json'),
                      'profile_sha256': sha(NEW / 'contract-profile.json'),
                      'source_files': len(old_source['files']),
                      'profile_files': len(old_profile['files'])}, sort_keys=True))


if __name__ == '__main__':
    main()
