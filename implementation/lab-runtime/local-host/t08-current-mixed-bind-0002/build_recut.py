"""Create one disjoint API33-derived technical Source/profile/host-schema cut."""

import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
OLD = Path('product/lab/release-candidates/v1/interface/api-integration-v33-current-0001')
NEW = Path('product/lab/release-candidates/v1/interface/api-integration-v33-t08-mixed-0002')
PORT = Path('implementation/lab-runtime/local-host/t08-current-mixed-bind-0001/current_content.py')
OLD_SOURCE_SHA = 'e400703a2ace9ea1899d7abf15023632a83235e1e15f5459970b1ed8d12a37dd'
OLD_PROFILE_SHA = 'c86a04159a99d607f15f42078ae64b108ef5007e121f830d54174f0167b8813a'
PORT_SHA = '89e676278d50dc91dc0fb975ca7ae3107635a19bed7b7580e3ec0955ea485e9e'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(value, reason):
    if not value:
        raise ValueError(reason)


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def new_file(path, raw):
    path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def main():
    old_source_raw = (ROOT / OLD / 'source-manifest.json').read_bytes()
    old_profile_raw = (ROOT / OLD / 'contract-profile.json').read_bytes()
    need(sha(old_source_raw) == OLD_SOURCE_SHA and sha(old_profile_raw) == OLD_PROFILE_SHA,
         'selected API33 predecessor differs')
    need(sha((ROOT / PORT).read_bytes()) == PORT_SHA, 'selected current-content successor differs')
    source = json.loads(old_source_raw)
    profile = json.loads(old_profile_raw)
    need(len(source['files']) == 207 and len(profile['files']) == 32019,
         'selected predecessor domain differs')
    need(not (ROOT / NEW).exists(), 'disjoint API33 technical successor already exists')
    (ROOT / NEW).mkdir(mode=0o755)
    old_prefix, new_prefix = OLD.as_posix() + '/', NEW.as_posix() + '/'
    omitted = {'contract-profile.json', 'host-bridge.schema.json'}
    new_rows = []
    for row in source['files']:
        name = row['path']
        if not name.startswith(old_prefix):
            new_rows.append(row)
            continue
        relative = name[len(old_prefix):]
        target = ROOT / NEW / relative
        if relative in omitted:
            new_rows.append({'path': new_prefix + relative, 'sha256': None})
            continue
        raw = (ROOT / name).read_bytes()
        need(sha(raw) == row['sha256'], 'selected predecessor file changed: ' + name)
        new_file(target, raw)
        new_rows.append({'path': new_prefix + relative, 'sha256': row['sha256']})
    schema = json.loads((ROOT / OLD / 'host-bridge.schema.json').read_bytes())
    bindings = schema['properties']['module_bindings']['const']
    need(bindings['private_content']['sha256'] ==
         'e751847f53ea257b5ce7ba2fb7d4c9b5e9fd29d4f978281b69c5f21879d6f3ac',
         'old private-content schema pin differs')
    bindings['private_content'] = {'path': PORT.as_posix(), 'sha256': PORT_SHA}
    # The original bridge schema required 0700 for every root, including
    # immutable public repo/host dependency roots. Keep the private root at
    # 0700 and admit only 0700/0755 for explicitly named read-only roots.
    roots = schema['properties']['protected_inputs']['anyOf'][1]['properties']['control_roots']['items']
    need(roots['properties']['mode'] == {'const': 0o700},
         'predecessor bridge root mode schema differs')
    roots['properties']['mode'] = {'enum': [0o700, 0o755]}
    roots['allOf'] = [{'if': {'properties': {'id': {'const': 'private'}}, 'required': ['id']},
                       'then': {'properties': {'mode': {'const': 0o700}}},
                       'else': {'properties': {
                           'id': {'pattern': '^(repo|absolute:[a-f0-9]{20})$'}}}}]
    schema_raw = encoded(schema)
    schema_sha = sha(schema_raw)
    new_file(ROOT / NEW / 'host-bridge.schema.json', schema_raw)
    profile['files'].extend([
        {'path': PORT.as_posix(), 'sha256': PORT_SHA},
        {'path': new_prefix + 'host-bridge.schema.json', 'sha256': schema_sha},
    ])
    need(len({row['path'] for row in profile['files']}) == 32021,
         'recut profile path collision')
    profile['claim_ceiling'] = ('API33-derived T08 mixed technical profile; old original-locator '
                                'physical closure and original full proof remain REFUSED; no release effect.')
    profile_raw = encoded(profile)
    profile_sha = sha(profile_raw)
    new_file(ROOT / NEW / 'contract-profile.json', profile_raw)
    for row in new_rows:
        if row['path'] == new_prefix + 'host-bridge.schema.json':
            row['sha256'] = schema_sha
        elif row['path'] == new_prefix + 'contract-profile.json':
            row['sha256'] = profile_sha
    need(len(new_rows) == 207 and all(row['sha256'] for row in new_rows),
         'recut Source rows differ')
    source['files'] = new_rows
    source['profile_binding'] = {'path': new_prefix + 'contract-profile.json',
                                 'sha256': profile_sha}
    source['predecessor_source_manifest_binding'] = {
        'path': OLD.as_posix() + '/source-manifest.json', 'sha256': OLD_SOURCE_SHA}
    source['claim_ceiling'] = ('API33-derived T08 mixed technical Source selecting a current historical '
                               'content port; no old-locator proof, admission, release or owner effect.')
    source_raw = encoded(source)
    source_sha = sha(source_raw)
    new_file(ROOT / NEW / 'source-manifest.json', source_raw)
    new_file(ROOT / NEW / 'rebind-receipt.json', encoded({
        'schema_version': 'lab-T08-current-mixed-technical-rebind/v2-candidate',
        'source_package': OLD.as_posix(), 'successor_package': NEW.as_posix(),
        'successor_manifest_sha256': source_sha,
        'successor_profile_sha256': profile_sha,
        'original_locator_physical_closure': 'REFUSED',
        'original_full_proof_status': 'REFUSED',
        'authority_effect': 'none', 'T08_complete': False,
    }))
    actual = {p.relative_to(ROOT / NEW).as_posix() for p in (ROOT / NEW).rglob('*') if p.is_file()}
    expected = ({row['path'][len(new_prefix):] for row in new_rows
                 if row['path'].startswith(new_prefix)} |
                {'source-manifest.json', 'rebind-receipt.json'})
    need(actual == expected, 'recut physical package differs from closed Source')
    print(json.dumps({'source_path': NEW.as_posix() + '/source-manifest.json',
                      'source_sha256': source_sha, 'profile_sha256': profile_sha,
                      'host_schema_sha256': schema_sha, 'profile_rows': len(profile['files']),
                      'source_rows': len(new_rows), 'package_files': len(actual),
                      'authority_effect': 'none'}, sort_keys=True))


if __name__ == '__main__':
    main()
