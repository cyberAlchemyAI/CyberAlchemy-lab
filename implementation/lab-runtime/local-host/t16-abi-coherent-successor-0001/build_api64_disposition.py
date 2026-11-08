"""Rebind the exact signed 604-subject closure without changing inherited methods."""
import ast
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OLD = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v63-t16-abi423-alias-0001'
NEW = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v64-t16-abi423-disposition-0001'
OLD_SOURCE = 'fc079aaf4390c8d523cb4036ef31421d146a663cc135694f492e02387b879edf'
OLD_PROFILE = '022ede7e9c70975bc2aa33d9f99f81b3f16eb7145e6c341734fa3bd5681b2662'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()

def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}

def main():
    os.umask(0o077)
    if NEW.exists() or sha(OLD / 'source-manifest.json') != OLD_SOURCE or sha(OLD / 'contract-profile.json') != OLD_PROFILE:
        raise ValueError('predecessor differs or successor exists')
    profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    source = json.loads((OLD / 'source-manifest.json').read_bytes())
    if len(profile['files']) != 33425 or len(source['files']) != 210:
        raise ValueError('source/profile inventory differs')
    NEW.mkdir(mode=0o700)
    for path in OLD.rglob('*'):
        if not path.is_file() or '__pycache__' in path.parts or path.name in ('source-manifest.json', 'contract-profile.json', 'rebind-receipt.json'):
            continue
        target = NEW / path.relative_to(OLD)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    native = NEW / 'native_dispositions.py'
    body = native.read_text()
    old = "len(rows) == 616 and\n                   len({row['version_ref'] for row in rows}) == 616 and\n                   data['source_closure']['accounted_subjects'] == 616"
    new = old.replace('616', '604')
    if body.count(old) != 1:
        raise ValueError('exact closure assertion changed')
    body = body.replace(old, new)
    ast.parse(body)
    native.write_text(body)
    bridge = NEW / 'source_bridge.py'
    body = bridge.read_text()
    for family in ('legacy_local', 'source8_local'):
        old_tag = '_cal_api63_t16_' + family + '_20261023_0001'
        new_tag = '_cal_api64_t16_' + family + '_20261023_0001'
        if body.count(old_tag) == 0:
            raise ValueError('source bridge namespace absent')
        body = body.replace(old_tag, new_tag)
    ast.parse(body)
    bridge.write_text(body)
    registry = NEW / 'workflow_output_registry.py'
    body = registry.read_text()
    if body.count(OLD.name) == 0:
        raise ValueError('registry package binding absent')
    body = body.replace(OLD.name, NEW.name)
    ast.parse(body)
    registry.write_text(body)
    for path in list(OLD.glob('test_*.py')) + list(OLD.glob('run_*checks.py')):
        if sha(path) != sha(NEW / path.name):
            raise ValueError('inherited test bytes differ: ' + path.name)
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    def recut(row):
        if row['path'].startswith(old_prefix):
            return binding(NEW / row['path'][len(old_prefix):])
        return row
    profile['files'] = sorted((recut(row) for row in profile['files']), key=lambda row: row['path'])
    for key, value in list(profile.items()):
        if key != 'files' and isinstance(value, dict) and set(value) == {'path', 'sha256'}:
            profile[key] = recut(value)
    profile['claim_ceiling'] = 'Local current-family exact signed 604-disposition successor; inherited methods require complete execution and qualification.'
    (NEW / 'contract-profile.json').write_bytes(encoded(profile))
    source['files'] = sorted((recut(row) for row in source['files']), key=lambda row: row['path'])
    source['profile_binding'] = binding(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = binding(OLD / 'source-manifest.json')
    source['claim_ceiling'] = 'Local signed current-family disposition rebind and inherited AST preservation; no complete T16 qualification or authority effect.'
    (NEW / 'source-manifest.json').write_bytes(encoded(source))
    receipt = {
        'schema_version': 'lab-T16-API64-exact-native-disposition/v1-candidate',
        'predecessor_source_binding': binding(OLD / 'source-manifest.json'),
        'successor_source_binding': binding(NEW / 'source-manifest.json'),
        'successor_package': NEW.relative_to(ROOT).as_posix(),
        'successor_manifest_sha256': sha(NEW / 'source-manifest.json'),
        'successor_profile_binding': binding(NEW / 'contract-profile.json'),
        'signed_mapping_binding': {'path': 'implementation/lab-runtime/local-host/t16-abi-coherent-successor-0001/instances/legacy-local-e084574c6d149cf0/mapped/packages/0001/mapping.json', 'sha256': 'eb39145d191985a5674a279f2c8f0feead81b7ee733707243ba3b81074045308'},
        'exact_source_subject_count': 604,
        'inherited_test_files_byte_identical': True,
        'authority_effect': 'none', 't16_qualified': False,
    }
    (NEW / 'rebind-receipt.json').write_bytes(encoded(receipt))
    print(json.dumps({'source': receipt['successor_source_binding'], 'profile': receipt['successor_profile_binding']}, sort_keys=True))

if __name__ == '__main__':
    main()
