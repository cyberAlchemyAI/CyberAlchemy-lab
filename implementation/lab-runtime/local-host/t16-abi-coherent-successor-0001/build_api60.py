"""Build a focused API53 successor for the new local 4.23 family.

This recuts source/profile and current-family path/hash selectors. It does not
claim that all inherited API53 fixtures have been semantically reconciled.
"""
import ast
import hashlib
import json
import os
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
OLD = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v53-t16-challenge-source-0001'
NEW = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v60-t16-abi423-0001'
OLD_FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5'
FAMILY = ROOT / 'implementation/lab-runtime/local-host/t16-abi-coherent-successor-0001/instances/legacy-local-e084574c6d149cf0'
OLD_SOURCE = '7944431236ce9437516104b33ed04024994e0d9d45a2c2152eacf71612fd09ff'
OLD_PROFILE = '7480e7bf7d848a16d50bf7f56d6c4a24bd6175b0fa61d35fa796f9bf76c99f7d'
ENVIRONMENT = {'python': '3.14.4', 'jsonschema': '4.23.0', 'cryptography': '46.0.5'}
FAMILY_BINDINGS = {
    'family_source_manifest_binding': 'source/source-manifest.json',
    'family_source_package_binding': 'source/packages/0001/manifest.json',
    'family_reader_manifest_binding': 'reader/source-manifest.json',
    'family_mapped_package_binding': 'mapped/packages/0001/manifest.json',
    'family_mapping_binding': 'mapped/packages/0001/mapping.json',
    'family_context_manifest_binding': 'context/source-manifest.json',
    'family_context_package_binding': 'context/packages/0001/manifest.json',
}
HISTORICAL_FILES = {'INPUT-ACCOUNTING.json', 'SCHEMA-EXECUTION-DEPENDENCIES.json'}
CLAIM = ('Focused local Python 3.14.4/jsonschema 4.23.0 source-family and one-method '
         'smoke candidate; no 345-method T16 qualification, protected Source8, or authority effect.')


def sha(raw): return hashlib.sha256(raw).hexdigest()


def row(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        raise ValueError('selected local regular file required: ' + str(path))
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def save(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as output:
        output.write(raw); output.flush(); os.fsync(output.fileno())


def json_bytes(value): return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def main():
    if sha((OLD / 'source-manifest.json').read_bytes()) != OLD_SOURCE or sha((OLD / 'contract-profile.json').read_bytes()) != OLD_PROFILE:
        raise ValueError('API53 selected source/profile differs')
    if NEW.exists(): raise ValueError('successor path already exists')
    old_source = json.loads((OLD / 'source-manifest.json').read_bytes())
    old_profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    old_family_prefix = OLD_FAMILY.relative_to(ROOT).as_posix() + '/'
    new_family_prefix = FAMILY.relative_to(ROOT).as_posix() + '/'
    if len(old_source['files']) != 210 or len(old_profile['files']) != 33425:
        raise ValueError('API53 source/profile inventory differs')
    own = [r for r in old_source['files'] if r['path'].startswith(old_prefix)]
    if len(own) != 201 or not all(row(ROOT / r['path']) == r for r in own):
        raise ValueError('API53 owned files differ')
    for manifest in ('source', 'reader', 'mapped', 'context'):
        path = FAMILY / manifest / 'source-manifest.json'
        observed = json.loads(path.read_bytes())
        if observed['environment'] != ENVIRONMENT:
            raise ValueError('new family environment differs: ' + manifest)
    for name in ('source', 'cold', 'reader', 'mapped', 'context'):
        phase = json.loads((FAMILY / (name + '-result.json')).read_bytes())
        if phase.get('result') not in ('PASS', 'PASS-native-cold', 'PASS-current-reader', 'PASS-native-mapper', 'PASS-native-Context-construction', None):
            raise ValueError('new family phase differs: ' + name)

    digest_map = {}
    for original in OLD_FAMILY.rglob('*'):
        if not original.is_file() or '__pycache__' in original.parts:
            continue
        successor = FAMILY / original.relative_to(OLD_FAMILY)
        if not successor.is_file():
            continue
        old_digest, new_digest = sha(original.read_bytes()), sha(successor.read_bytes())
        if old_digest in digest_map and digest_map[old_digest] != new_digest:
            raise ValueError('ambiguous old family digest replacement')
        digest_map[old_digest] = new_digest

    NEW.mkdir(mode=0o700)
    for original in own:
        name = original['path'][len(old_prefix):]
        if name == 'contract-profile.json':
            continue
        data = (OLD / name).read_bytes()
        if name not in HISTORICAL_FILES:
            try: text = data.decode('utf-8')
            except UnicodeError: text = None
            if text is not None:
                text = text.replace(old_prefix, new_prefix)
                text = text.replace(old_family_prefix, new_family_prefix)
                text = text.replace(OLD_FAMILY.name, FAMILY.name)
                for before, after in digest_map.items():
                    if before != after: text = text.replace(before, after)
                if name == 'source_bridge.py':
                    text = text.replace('_cal_api53_t16_legacy_local_20261023_0001',
                                        '_cal_api60_t16_legacy_local_20261023_0001')
                    text = text.replace('_cal_api53_t16_source8_local_20261023_0001',
                                        '_cal_api60_t16_source8_local_20261023_0001')
                if name.endswith('.py'): ast.parse(text)
                if name.endswith('.json'): json.loads(text)
                data = text.encode('utf-8')
        save(NEW / name, data)

    def map_row(binding):
        path = binding['path']
        if path.startswith(old_prefix): return row(NEW / path[len(old_prefix):])
        if path.startswith(old_family_prefix):
            return row(FAMILY / path[len(old_family_prefix):])
        return binding

    profile = old_profile
    profile['files'] = sorted((map_row(r) for r in profile['files']), key=lambda r: r['path'])
    if len({r['path'] for r in profile['files']}) != len(profile['files']):
        raise ValueError('successor profile path collision')
    for key, value in list(profile.items()):
        if key != 'files' and isinstance(value, dict) and set(value) == {'path', 'sha256'}:
            profile[key] = map_row(value)
    profile['claim_ceiling'] = CLAIM
    save(NEW / 'contract-profile.json', json_bytes(profile))

    source = old_source
    source['files'] = sorted((map_row(r) for r in source['files']), key=lambda r: r['path'])
    if len({r['path'] for r in source['files']}) != len(source['files']):
        raise ValueError('successor source path collision')
    source['environment'] = ENVIRONMENT
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    for key, relative in FAMILY_BINDINGS.items(): source[key] = row(FAMILY / relative)
    source['claim_ceiling'] = CLAIM
    save(NEW / 'source-manifest.json', json_bytes(source))

    receipt = {'schema_version': 'lab-T16-API60-local-423-rebind/v1-candidate',
               'predecessor_source_binding': row(OLD / 'source-manifest.json'),
               'successor_source_binding': row(NEW / 'source-manifest.json'),
               'successor_manifest_sha256': row(NEW / 'source-manifest.json')['sha256'],
               'successor_profile_binding': row(NEW / 'contract-profile.json'),
               'successor_package': NEW.relative_to(ROOT).as_posix(),
               'family_source_binding': row(FAMILY / 'source/source-manifest.json'),
               'family_context_binding': row(FAMILY / 'context/source-manifest.json'),
               'claim_ceiling': CLAIM, 'authority_effect': 'none'}
    save(NEW / 'rebind-receipt.json', json_bytes(receipt))
    return {'api_source_binding': receipt['successor_source_binding'],
            'api_profile_binding': receipt['successor_profile_binding'],
            'family_context_binding': receipt['family_context_binding']}


if __name__ == '__main__': print(json.dumps(main(), sort_keys=True))
