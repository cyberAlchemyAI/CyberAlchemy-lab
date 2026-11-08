"""One-shot disjoint API46 recut of the selected T31 native family."""

import hashlib
import json
import os
from pathlib import Path
import stat


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v42-r03-0005-current-0001'
NEW = BASE / 'api-integration-v46-t31-workflow-current-0002'
OLD_SOURCE_SHA = '41aab1ef39fd93c33e2313a19466f4755a8ea14389c1d6abcfdb4ce461be3f50'
OLD_PROFILE_SHA = '043138382a4f3bc94e7c5ad00c957e6b1f91d0dd80cbb335941ade05ef942e4d'
OLD_MEMBERS_SHA = '625ccd27d3a18166dbdaa837c3ec9395491853cb28cef5ff4e05392c99365732'
OLD_ID = 'legacy-local-710362c855a8a11c'
NEW_ID = 'legacy-local-ce4d53a6479188a5'
STORE = 'completion-legacy-local-' + NEW_ID.removeprefix('legacy-local-')
FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances' / NEW_ID
SELECTION = ROOT / 'implementation/lab-runtime/local-host/t31-api-selector-recut-0001/SELECTION-0001.json'
OLD_FAMILY_PREFIX = 'implementation/lab-runtime/local-host/source8-current-fixture/instances/' + OLD_ID + '/'
NEW_FAMILY_PREFIX = 'implementation/lab-runtime/local-host/source8-current-fixture/instances/' + NEW_ID + '/'
OLD_SELECTION = 'implementation/lab-runtime/local-host/source8-current-fixture/selections/' + OLD_ID + '.json'
NEW_SELECTION = 'implementation/lab-runtime/local-host/source8-current-fixture/selections/' + NEW_ID + '.json'
FAMILY_SUFFIXES = {
    'family_source_manifest_binding': 'source/source-manifest.json',
    'family_source_package_binding': 'source/packages/0001/manifest.json',
    'family_reader_manifest_binding': 'reader/source-manifest.json',
    'family_mapped_package_binding': 'mapped/packages/0001/manifest.json',
    'family_mapping_binding': 'mapped/packages/0001/mapping.json',
    'family_context_manifest_binding': 'context/source-manifest.json',
    'family_context_package_binding': 'context/packages/0001/manifest.json',
}
REBOUND_FILES = (
    'source_bridge.py', 'current_context_sessions.py', 'current_legacy_context_sessions.py',
    'legacy_fixture_selection.py', 'native_dispositions.py', 'authentication.schema.json',
    'machine_auth_scope.py',
)
CLAIM = ('T31 local signed workflow-source ReaderChannel/Service candidate only; native '
         'workflow.transition, output producer/later consumer, independent private grant, '
         'authority effect, and Product qualification remain unproved.')


def read_regular(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('selected path is not absolute and closed')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError('selected file is not regular: ' + str(path))
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                return stream.read()
        finally:
            os.close(fd)
    except OSError as error:
        raise ValueError('selected file missing or linked: ' + str(path)) from error
    finally:
        os.close(directory)


def sha(path):
    return hashlib.sha256(read_regular(path)).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def row(path):
    return {'path': relative(path), 'sha256': sha(path)}


def write_new(path, raw):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def write(path, value):
    write_new(path, (json.dumps(value, sort_keys=True, indent=2) + '\n').encode())


def preflight():
    if (sha(OLD / 'source-manifest.json') != OLD_SOURCE_SHA or
            sha(OLD / 'contract-profile.json') != OLD_PROFILE_SHA or
            sha(OLD / 'integration-members.json') != OLD_MEMBERS_SHA):
        raise ValueError('frozen API42 predecessor differs')
    selection = json.loads(read_regular(SELECTION))
    if (set(selection) != {'schema_version', 'family', 'result_sha256', 'family_bindings',
                           'period_sha256', 'not_before', 'expires_at', 'source_subjects',
                           'authority_effect'} or
            selection['schema_version'] != 'lab-T31-API46-native-family-selection/v1-candidate' or
            selection['family'] != relative(FAMILY) or selection['authority_effect'] != 'none' or
            set(selection['result_sha256']) != {'source', 'cold', 'reader', 'mapped', 'context'} or
            set(selection['family_bindings']) != set(FAMILY_SUFFIXES) or
            selection['source_subjects'] != 616):
        raise ValueError('exact T31 family selection differs')
    for phase, expected in selection['result_sha256'].items():
        result = FAMILY / (phase + '-result.json')
        if sha(result) != expected:
            raise ValueError('native phase receipt differs: ' + phase)
        value = json.loads(read_regular(result))
        if phase != 'source' and value.get('result') != {
                'cold': 'PASS-native-cold', 'reader': 'PASS-current-reader',
                'mapped': 'PASS-native-mapper',
                'context': 'PASS-native-Context-construction'}[phase]:
            raise ValueError('native phase did not pass: ' + phase)
    for name, suffix in FAMILY_SUFFIXES.items():
        expected = selection['family_bindings'][name]
        if sha(FAMILY / suffix) != expected:
            raise ValueError('native family binding differs: ' + name)
    period = json.loads(read_regular(FAMILY / 'source/packages/0001/period.json'))
    if (sha(FAMILY / 'source/packages/0001/period.json') !=
            selection['period_sha256'] or
            period['not_before'] != selection['not_before'] or
            period['expires_at'] != selection['expires_at']):
        raise ValueError('selected signed source period differs')
    mapping = json.loads(read_regular(FAMILY / 'mapped/packages/0001/mapping.json'))
    if (mapping['source_cut']['store_ref'] != STORE or
            mapping['source_cut']['branch_ref'] != 'branch:' + STORE or
            len(mapping['projection_dispositions']) !=
            mapping['source_closure']['accounted_subjects'] != selection['source_subjects']):
        raise ValueError('selected native source cut or disposition closure differs')
    work = FAMILY / 'source/packages/0001/artifacts/04.json'
    if sha(work) != 'a434ab112a9ef0cf1929897a059006d47caba023d903dabc6b84bb5fe0c09dd4':
        raise ValueError('selected T31 Work differs')
    return selection


def main():
    selection = preflight()
    if NEW.exists():
        raise ValueError('versioned API46 successor already exists')
    old_manifest = json.loads(read_regular(OLD / 'source-manifest.json'))
    old_profile = json.loads(read_regular(OLD / 'contract-profile.json'))
    old_prefix = relative(OLD) + '/'
    own = [r for r in old_manifest['files'] if r['path'].startswith(old_prefix)]
    if (len(own) != 201 or len(old_manifest['files']) != 207 or
            len({r['path'] for r in own}) != len(own)):
        raise ValueError('frozen API42 closure differs')
    actual = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
              and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    if actual != {r['path'][len(old_prefix):] for r in own}:
        raise ValueError('API42 actual file inventory differs')
    NEW.mkdir(mode=0o700)
    for selected in own:
        name = selected['path'][len(old_prefix):]
        source = OLD / name
        if sha(source) != selected['sha256']:
            raise ValueError('API42 selected source byte differs: ' + name)
        if name in REBOUND_FILES or name == 'contract-profile.json':
            continue
        target = NEW / name
        target.parent.mkdir(parents=True, exist_ok=True)
        write_new(target, read_regular(source))
    pin_replacements = {old_manifest[name]['sha256']: selection['family_bindings'][name]
                        for name in ('family_context_manifest_binding', 'family_mapped_package_binding',
                                     'family_mapping_binding', 'family_source_package_binding')}
    old_period = json.loads(read_regular(ROOT / (OLD_FAMILY_PREFIX + 'source/packages/0001/period.json')))
    for name in REBOUND_FILES:
        path = NEW / name
        raw = read_regular(OLD / name).decode()
        if OLD_ID not in raw:
            raise ValueError('expected old family pin missing from ' + name)
        raw = raw.replace(OLD_ID, NEW_ID)
        for old_pin, new_pin in pin_replacements.items():
            raw = raw.replace(old_pin, new_pin)
        if name == 'legacy_fixture_selection.py':
            raw = raw.replace(old_period['not_before'], selection['not_before'])
            raw = raw.replace(old_period['expires_at'], selection['expires_at'])
        if name == 'source_bridge.py':
            raw = raw.replace('_cal_api42_current_legacy_local_20261023_0001',
                              '_cal_api46_t31_legacy_local_20261023_0001')
            raw = raw.replace('_cal_api42_current_source8_local_20261023_0001',
                              '_cal_api46_t31_source8_local_20261023_0001')
        if name == 'native_dispositions.py':
            if raw.count('604') != 3:
                raise ValueError('old native disposition count differs')
            raw = raw.replace('604', str(selection['source_subjects']))
        write_new(path, raw.encode())
    profile_rows = []
    old_family_rows = 0
    for selected in old_profile['files']:
        name = selected['path']
        if name.startswith(old_prefix):
            profile_rows.append(row(NEW / name[len(old_prefix):]))
        elif name.startswith(OLD_FAMILY_PREFIX):
            old_family_rows += 1
            profile_rows.append(row(ROOT / (NEW_FAMILY_PREFIX + name[len(OLD_FAMILY_PREFIX):])))
        elif name == OLD_SELECTION:
            old_family_rows += 1
            profile_rows.append(row(ROOT / NEW_SELECTION))
        else:
            profile_rows.append(selected)
    if old_family_rows != 21 or len({r['path'] for r in profile_rows}) != len(profile_rows):
        raise ValueError('API46 profile family replacement differs')
    old_profile['files'] = sorted(profile_rows, key=lambda item: item['path'])
    old_profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    old_profile['claim_ceiling'] = CLAIM
    write(NEW / 'contract-profile.json', old_profile)
    new_files = []
    for selected in old_manifest['files']:
        name = selected['path']
        new_files.append(row(NEW / name[len(old_prefix):]) if name.startswith(old_prefix) else selected)
    old_manifest['files'] = sorted(new_files, key=lambda item: item['path'])
    old_manifest['profile_binding'] = row(NEW / 'contract-profile.json')
    old_manifest['predecessor_source_manifest_binding'] = {'path': relative(OLD / 'source-manifest.json'),
                                                            'sha256': OLD_SOURCE_SHA}
    for name, suffix in FAMILY_SUFFIXES.items():
        old_manifest[name] = {'path': relative(FAMILY / suffix), 'sha256': selection['family_bindings'][name]}
    old_manifest['claim_ceiling'] = CLAIM
    write(NEW / 'source-manifest.json', old_manifest)
    receipt = {
        'schema_version': 'lab-API46-T31-native-family-rebind/v1-candidate',
        'successor_package': relative(NEW),
        'successor_manifest_sha256': sha(NEW / 'source-manifest.json'),
        'predecessor_source_manifest_binding': {'path': relative(OLD / 'source-manifest.json'),
                                                'sha256': OLD_SOURCE_SHA},
        'successor_source_manifest_binding': row(NEW / 'source-manifest.json'),
        'successor_profile_binding': row(NEW / 'contract-profile.json'),
        'native_selection_binding': row(SELECTION),
        'native_phase_receipts': [{'path': relative(FAMILY / (phase + '-result.json')),
                                   'sha256': expected} for phase, expected in selection['result_sha256'].items()],
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'claim_ceiling': CLAIM, 'current_ReaderChannel_Service_tested': False,
    }
    write(NEW / 'rebind-receipt.json', receipt)
    print(json.dumps({'source_sha256': sha(NEW / 'source-manifest.json'),
                      'profile_sha256': sha(NEW / 'contract-profile.json'),
                      'source_files': len(old_manifest['files']),
                      'profile_files': len(old_profile['files'])}, sort_keys=True))


if __name__ == '__main__':
    main()
