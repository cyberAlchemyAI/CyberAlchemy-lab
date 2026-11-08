"""Build a disjoint API39/T06 successor with selected live import closure."""
import hashlib
import json
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = INTERFACE / 'api-integration-v38-current-t06-0001'
NEW = INTERFACE / 'api-integration-v39-current-t06-0001'
GOV = INTERFACE / 'api-governance-integration-v5-current-t12-0001'
ACTION = INTERFACE / 'api-action-integration-v6-current-t06-0001'
ACTION_SOURCE_SHA = '59c87d33d5d762ea55a80ef941002fd2beace66ed233ecb917fdc5c829de3f1a'
ACTION_PROFILE_SHA = 'b3767b2b1ececc73ce24ea7d55924956feab8a5f3b563c3359391122a95b3576'
SDK = INTERFACE / 'composite-operator-v1-current-api39-0001/revision-0001'
BRANCH = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api39-0001/revision-0001'
OLD_SOURCE_SHA = '71f5ba4008ce1955265e949bb5250a5af6d9cc5da046d40c8fa7c6a765f774a7'
GOV_SOURCE_SHA = '8a215ad66e94179385bcb4dcac79eab5267ee6ac50e12e7b1dac21645301d337'
GOV_PROFILE_SHA = '7798fda1f9e7e4038425bc8aa6f227f2e22612affa4acb2c28c9a12d31531af3'
INSTALL = ROOT / 'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001'
INSTALL_METADATA_SHA = '5821d37ce536e08c639493ceb8d165949e65cf5dd9771af5576a724082cca13b'

def digest(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError(f'missing or linked input: {path}')
    return hashlib.sha256(path.read_bytes()).hexdigest()

def relative(path):
    return path.relative_to(ROOT).as_posix()

def row(path):
    return {'path': relative(path), 'sha256': digest(path)}

def read(path):
    return json.loads(path.read_bytes())

def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n')

def selected(path, expected):
    if digest(path) != expected:
        raise ValueError(f'independently selected input changed: {path}')
    return read(path)

def add(rows, value):
    prior = rows.get(value['path'])
    if prior is not None and prior != value:
        raise ValueError(f'conflicting selected source: {value["path"]}')
    rows[value['path']] = value

def main():
    selected(OLD / 'source-manifest.json', OLD_SOURCE_SHA)
    governance = selected(GOV / 'source-manifest.json', GOV_SOURCE_SHA)
    selected(GOV / 'contract-profile.json', GOV_PROFILE_SHA)
    action = selected(ACTION / 'source-manifest.json', ACTION_SOURCE_SHA)
    selected(ACTION / 'contract-profile.json', ACTION_PROFILE_SHA)
    sdk = read(SDK / 'source-manifest.json')
    branch = read(BRANCH / 'driver-selection.json')

    members = read(NEW / 'integration-members.json')
    members['members']['actions']['directory'] = ACTION.name
    members['members']['actions']['source_sha256'] = ACTION_SOURCE_SHA
    members['members']['actions']['profile_sha256'] = ACTION_PROFILE_SHA
    members['members']['governance']['directory'] = GOV.name
    members['members']['governance']['source_sha256'] = GOV_SOURCE_SHA
    members['members']['governance']['profile_sha256'] = GOV_PROFILE_SHA
    write(NEW / 'integration-members.json', members)

    profile = read(NEW / 'contract-profile.json')
    rows = {}
    old_prefix = relative(OLD) + '/'
    for item in profile['files']:
        if item['path'].startswith(old_prefix):
            name = item['path'][len(old_prefix):]
            add(rows, row(NEW / name))
        else:
            add(rows, item)
    for item in governance['files']:
        add(rows, item)
    for item in action['files']:
        add(rows, item)
    for path in [ACTION / 'source-manifest.json', ACTION / 'contract-profile.json']:
        add(rows, row(path))
    for path in [GOV / 'source-manifest.json', GOV / 'contract-profile.json', SDK / 'source-manifest.json', BRANCH / 'driver-selection.json']:
        add(rows, row(path))
    for item in sdk['files']:
        add(rows, item)
    for item in branch['files']:
        add(rows, item)
    # The Action guard inspects every already-loaded repository module during
    # same-process dispatch. Select the exact current API package code here,
    # including __init__, protocol, guard, and other generated own modules.
    for path in NEW.glob('*.py'):
        add(rows, row(path))
    overlay_path = ROOT / 'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/source-manifest.json'
    overlay = selected(overlay_path, '574bd9f1fc976755eb0bf075b2ec7c14d8c378e8c6b074fa4df0e50af3951bd7')
    add(rows, row(overlay_path))
    for item in overlay['files']:
        add(rows, {'path': item['path'], 'sha256': item['sha256']})
    # The Action guard enumerates every loaded repository Python module. The
    # installed interpreter is inside this repository, so select its entire
    # already-pinned installation instead of exempting stdlib imports.
    metadata = selected(INSTALL / 'installation.json', INSTALL_METADATA_SHA)
    if len(metadata['installed_files']) != 1010:
        raise ValueError('installed closure count differs')
    for name, binding in metadata['installed_files'].items():
        relative_name = Path(name)
        if relative_name.is_absolute() or '..' in relative_name.parts or relative_name.as_posix() != name:
            raise ValueError('installed relative path differs')
        path = INSTALL / relative_name
        observed = path.lstat()
        if not stat.S_ISREG(observed.st_mode) or stat.S_IMODE(observed.st_mode) != binding['mode'] or observed.st_size != binding['size_bytes'] or digest(path) != binding['sha256']:
            raise ValueError('installed file binding differs: ' + name)
        add(rows, row(path))
    add(rows, row(INSTALL / 'installation.json'))
    profile['files'] = [rows[name] for name in sorted(rows)]
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    write(NEW / 'contract-profile.json', profile)

    source = read(NEW / 'source-manifest.json')
    source['environment']['jsonschema'] = '4.19.2'
    source['predecessor_source_manifest_binding'] = {'path': relative(OLD / 'source-manifest.json'), 'sha256': OLD_SOURCE_SHA}
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['files'] = [row(NEW / item['path'][len(old_prefix):]) if item['path'].startswith(old_prefix) else item for item in source['files']]
    source['files'].sort(key=lambda item: item['path'])
    write(NEW / 'source-manifest.json', source)
    release = {'successor_package': relative(NEW), 'successor_manifest_sha256': digest(NEW / 'source-manifest.json'), 'predecessor_source_manifest_binding': source['predecessor_source_manifest_binding'], 'profile_binding': source['profile_binding'], 'authority_effect': 'none', 'claim_ceiling': 'disjoint API39/T06 local candidate; live branch and whole-class tests pending'}
    write(NEW / 'rebind-receipt.json', release)
    print(json.dumps({'source_manifest_sha256': release['successor_manifest_sha256'], 'profile_sha256': source['profile_binding']['sha256'], 'member_sha256': digest(NEW / 'integration-members.json'), 'profile_file_count': len(profile['files']), 'source_file_count': len(source['files'])}, sort_keys=True))

if __name__ == '__main__':
    main()
