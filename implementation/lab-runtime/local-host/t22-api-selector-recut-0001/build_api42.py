"""One-shot, disjoint API42 recut of the independently reviewed T22 v4 family."""

import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v41-current-source8-0001'
NEW = BASE / 'api-integration-v42-r03-0005-current-0001'
OLD_SOURCE_SHA = '69c872681c53ff02ba5d38ef0f80d866d75f0b9e8c6b6d5d214b9adc2ba70961'
OLD_PROFILE_SHA = '18ed4a8a577679211ee5f530ea8148fc18cb0dd0a29ef16de73d6ea761eb9860'
OLD_MEMBERS_SHA = '625ccd27d3a18166dbdaa837c3ec9395491853cb28cef5ff4e05392c99365732'
OLD_ID = 'legacy-local-947e6c2a5b3d10f8'
NEW_ID = 'legacy-local-710362c855a8a11c'
STORE = 'completion-legacy-local-' + NEW_ID.removeprefix('legacy-local-')
FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances' / NEW_ID
CHAIN = ROOT / 'implementation/lab-runtime/local-host/t22-native-source8-successor-0004/CHAIN-0001.json'
CHAIN_SHA = '8c4b87eea920d9c1943bafeb0ecdcf087bfd8b5c29b66571d9793829fbe4e8ec'
OLD_FAMILY_PREFIX = 'implementation/lab-runtime/local-host/source8-current-fixture/instances/' + OLD_ID + '/'
NEW_FAMILY_PREFIX = 'implementation/lab-runtime/local-host/source8-current-fixture/instances/' + NEW_ID + '/'
OLD_SELECTION = 'implementation/lab-runtime/local-host/source8-current-fixture/selections/' + OLD_ID + '.json'
NEW_SELECTION = 'implementation/lab-runtime/local-host/source8-current-fixture/selections/' + NEW_ID + '.json'
RESULT_SHA = {
    'source': '9482057361c19b998902822052e6e9de79dc0f8ce761b086364f4d7fbac7f43c',
    'cold': 'a162aab2db2fd106b9108afcafcf1309990f4a2c52643dc7bb7b3ed95bdc2419',
    'reader': 'dfb8953710ba99b248fce96f61abddeeef380f10489a79daffc22a9281083265',
    'mapped': 'c5fd8199aadbc007d1618f1375dc2604fd7b1bc49bbd26b900d2cc4a4dcb4de7',
    'context': 'afe00f57ff3a22f90ca4c7d8068c55cca723b1b824b5669ef7e257e6520d22f2',
}
FAMILY_BINDINGS = {
    'family_source_manifest_binding': ('source/source-manifest.json', 'a519c711b666f72897fcfffebfe63bc01d0b8994367a182e849b1d747bed7037'),
    'family_source_package_binding': ('source/packages/0001/manifest.json', '614b14c45370e0d8b500a2dd7c9d57a38394ca404c09414ad3ad80f10db55839'),
    'family_reader_manifest_binding': ('reader/source-manifest.json', '0862f69e3be084f4da9ce2c4d9646ee5c5e2196f8c0e6a97160b07d8c2eaae3c'),
    'family_mapped_package_binding': ('mapped/packages/0001/manifest.json', '43a4bdbd63485f976d2ffe79026a85711e5e05989d0c38ba6110590410a9c6b3'),
    'family_mapping_binding': ('mapped/packages/0001/mapping.json', '2a5179b97aacf9e6e87d2ee6c41d1692a5f9806511203d53c0d7db96e3598539'),
    'family_context_manifest_binding': ('context/source-manifest.json', '9acba0286ce20363422a60825357ffc1735f8dd975271d57a7020018374d5edc'),
    'family_context_package_binding': ('context/packages/0001/manifest.json', '7d13e5dcc9918d69875e0d7d7da9ae2eb72f402e06e6a136171537b5ef223ac1'),
}
PIN_REPLACEMENTS = {
    '9a7baaf2453bed90a67b7145dd02c21f6e72150759885358e18f643f34899ddd': FAMILY_BINDINGS['family_context_manifest_binding'][1],
    'a0b3299db97cc50cdc1b0200ea4a063296ce6323671bf0052a2121d0fe67a270': FAMILY_BINDINGS['family_mapped_package_binding'][1],
    '6c64958278d3841d6ffe66b4981997ce4b71dfb9dc481fed45d11936db8f2f8c': FAMILY_BINDINGS['family_mapping_binding'][1],
    'da64e865676b7001fc8d5b8dfcfcdbaff8f3a041849649f49afc3df92ab4d901': FAMILY_BINDINGS['family_source_package_binding'][1],
}
REBOUND_FILES = (
    'source_bridge.py', 'current_context_sessions.py', 'current_legacy_context_sessions.py',
    'legacy_fixture_selection.py', 'native_dispositions.py', 'authentication.schema.json',
    'machine_auth_scope.py',
)
CLAIM = ('T22 v4 current R03-0005 ReaderChannel/Service Context and Session candidate only; '
         'Machine-channel, T06 composite installation, 34-operation coverage, contest outcome, '
         'authority effect, and Product qualification remain unproved.')


def sha(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing or linked selected file: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(ROOT).as_posix()


def row(path):
    return {'path': relative(path), 'sha256': sha(path)}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def preflight():
    if (sha(OLD / 'source-manifest.json') != OLD_SOURCE_SHA or
            sha(OLD / 'contract-profile.json') != OLD_PROFILE_SHA or
            sha(OLD / 'integration-members.json') != OLD_MEMBERS_SHA):
        raise ValueError('frozen API41 predecessor differs')
    if sha(CHAIN) != CHAIN_SHA:
        raise ValueError('selected native chain receipt differs')
    chain = json.loads(CHAIN.read_bytes())
    if (chain['status'] != 'PASS-native-family-construction' or
            chain['family'] != relative(FAMILY) or
            chain['native_session_consumed'] is not False or
            chain['authority_effect'] != 'none' or
            [item['sha256'] for item in chain['phase_result_bindings']] != list(RESULT_SHA.values())):
        raise ValueError('selected native chain scope differs')
    for phase, expected in RESULT_SHA.items():
        result = FAMILY / (phase + '-result.json')
        if sha(result) != expected:
            raise ValueError('native phase receipt differs: ' + phase)
        value = json.loads(result.read_bytes())
        if phase != 'source' and value.get('result') != {
                'cold': 'PASS-native-cold', 'reader': 'PASS-current-reader',
                'mapped': 'PASS-native-mapper',
                'context': 'PASS-native-Context-construction'}[phase]:
            raise ValueError('native phase did not pass: ' + phase)
    for name, (suffix, expected) in FAMILY_BINDINGS.items():
        if sha(FAMILY / suffix) != expected:
            raise ValueError('native family binding differs: ' + name)
    period = json.loads((FAMILY / 'source/packages/0001/period.json').read_bytes())
    if (sha(FAMILY / 'source/packages/0001/period.json') !=
            '3583bec60a5b82f62bbfa3f8420b824315f449d5aa61d2faec18c33a81cde534' or
            period['not_before'] != '2026-10-23T04:52:49.044239+00:00' or
            period['expires_at'] != '2026-10-24T04:52:49.044239+00:00'):
        raise ValueError('selected signed source period differs')
    mapping = json.loads((FAMILY / 'mapped/packages/0001/mapping.json').read_bytes())
    if (mapping['source_cut']['store_ref'] != STORE or
            mapping['source_cut']['branch_ref'] != 'branch:' + STORE or
            len(mapping['projection_dispositions']) !=
            mapping['source_closure']['accounted_subjects'] != 604):
        raise ValueError('selected native source cut or disposition closure differs')
    work = FAMILY / 'source/packages/0001/artifacts/04.json'
    if sha(work) != '863c92ab8fc926e14dbdced13b9140a8d6b3721afb1b530faa02f3b0892f32ba':
        raise ValueError('selected T22 Work differs')


def main():
    preflight()
    if NEW.exists():
        raise ValueError('versioned API42 successor already exists')
    old_manifest = json.loads((OLD / 'source-manifest.json').read_bytes())
    old_profile = json.loads((OLD / 'contract-profile.json').read_bytes())
    old_prefix = relative(OLD) + '/'
    new_prefix = relative(NEW) + '/'
    own = [r for r in old_manifest['files'] if r['path'].startswith(old_prefix)]
    if len(own) != 201 or len(old_manifest['files']) != 207:
        raise ValueError('frozen API41 closure differs')
    actual = {p.relative_to(OLD).as_posix() for p in OLD.rglob('*') if p.is_file()
              and p.name not in ('source-manifest.json', 'rebind-receipt.json')
              and '__pycache__' not in p.parts and 'receipts' not in p.parts and p.suffix != '.pyc'}
    if actual != {r['path'][len(old_prefix):] for r in own}:
        raise ValueError('API41 actual file inventory differs')
    NEW.mkdir(mode=0o700)
    for selected in own:
        name = selected['path'][len(old_prefix):]
        source = OLD / name
        if sha(source) != selected['sha256']:
            raise ValueError('API41 selected source byte differs: ' + name)
        target = NEW / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=False)
    for name in REBOUND_FILES:
        path = NEW / name
        raw = path.read_text()
        if OLD_ID not in raw:
            raise ValueError('expected old family pin missing from ' + name)
        raw = raw.replace(OLD_ID, NEW_ID)
        for old_pin, new_pin in PIN_REPLACEMENTS.items():
            raw = raw.replace(old_pin, new_pin)
        if name == 'legacy_fixture_selection.py':
            raw = raw.replace('2026-10-22T20:31:05.436679+00:00',
                              '2026-10-23T04:52:49.044239+00:00')
            raw = raw.replace('2026-10-23T20:31:05.436679+00:00',
                              '2026-10-24T04:52:49.044239+00:00')
        if name == 'source_bridge.py':
            raw = raw.replace('_cal_api30_current_legacy_local_20261022_0001',
                              '_cal_api42_current_legacy_local_20261023_0001')
            raw = raw.replace('_cal_api30_current_source8_local_20261022_0001',
                              '_cal_api42_current_source8_local_20261023_0001')
        path.write_text(raw)
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
        raise ValueError('API42 profile family replacement differs')
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
    for name, (suffix, expected) in FAMILY_BINDINGS.items():
        old_manifest[name] = {'path': relative(FAMILY / suffix), 'sha256': expected}
    old_manifest['claim_ceiling'] = CLAIM
    write(NEW / 'source-manifest.json', old_manifest)
    receipt = {
        'schema_version': 'lab-API42-T22-v4-native-family-rebind/v1-candidate',
        'successor_package': relative(NEW),
        'successor_manifest_sha256': sha(NEW / 'source-manifest.json'),
        'predecessor_source_manifest_binding': {'path': relative(OLD / 'source-manifest.json'),
                                                'sha256': OLD_SOURCE_SHA},
        'successor_source_manifest_binding': row(NEW / 'source-manifest.json'),
        'successor_profile_binding': row(NEW / 'contract-profile.json'),
        'native_chain_binding': {'path': relative(CHAIN), 'sha256': CHAIN_SHA},
        'native_phase_receipts': [{'path': relative(FAMILY / (phase + '-result.json')),
                                   'sha256': expected} for phase, expected in RESULT_SHA.items()],
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
