"""No-replace API53 recut: select two exact public challenge evidence originals."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v52-t16-metadata-current-0001'
NEW = BASE / 'api-integration-v53-t16-challenge-source-0001'
OLD_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t16-api52-bootstrap-0001/bootstrap.py'
NEW_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t16-api53-bootstrap-0001/bootstrap.py'
OLD_SOURCE_SHA = '060b501c32bb9cc3292f0e2a3124a89770ab5f69c6a749a823c466660dc96020'
OLD_PROFILE_SHA = '5da736d675d92e9fc72b1a197eea27d449610b2be8c621075aec81380fcb9c12'
EVIDENCE = (
    'product/lab/release-candidates/v1/interface/checkpoint-owner-verification-v3/receipts/checks-0001.json',
    'authority/admissions/governance-transaction-surface/v1/instances/governance/decisions/decision-0074a.json',
)
CLAIM = ('Current signed fixture with exact public challenge receipt and decision originals in source closure; '
         'no full inherited regression, owner effect, or canonical admission.')


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def raw(path: Path) -> bytes:
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute closed selected path required')
    handles = []
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for part in path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(parent)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise ValueError('selected regular file required')
            chunks = []
            while block := os.read(fd, 1024 * 1024):
                chunks.append(block)
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
            if stamp(before) != stamp(after) or stamp(after) != stamp(named):
                raise ValueError('selected file changed during capture')
            return b''.join(chunks)
        finally:
            os.close(fd)
    finally:
        for handle in reversed(handles):
            os.close(handle)


def row(path: Path) -> dict:
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(raw(path))}


def replace(text: str, old: str, new: str, count: int) -> str:
    if text.count(old) != count:
        raise ValueError('exact recut anchor differs: ' + old[:100])
    return text.replace(old, new)


def create(path: Path, data: bytes) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as output:
        output.write(data)
        output.flush()
        os.fsync(output.fileno())


def save(path: Path, data: dict) -> None:
    create(path, (json.dumps(data, indent=2, sort_keys=True) + '\n').encode())


def main() -> dict:
    if digest(raw(OLD / 'source-manifest.json')) != OLD_SOURCE_SHA or digest(raw(OLD / 'contract-profile.json')) != OLD_PROFILE_SHA:
        raise ValueError('frozen API52 source/profile changed')
    if NEW.exists() or NEW_ADAPTER.exists():
        raise ValueError('API53 successor already exists')
    source = json.loads(raw(OLD / 'source-manifest.json'))
    profile = json.loads(raw(OLD / 'contract-profile.json'))
    old_prefix = OLD.relative_to(ROOT).as_posix() + '/'
    new_prefix = NEW.relative_to(ROOT).as_posix() + '/'
    own = [item for item in source['files'] if item['path'].startswith(old_prefix)]
    if len(source['files']) != 208 or len(own) != 201 or len(profile['files']) != 33425:
        raise ValueError('frozen API52 row counts differ')
    for item in source['files']:
        if digest(raw(ROOT / item['path'])) != item['sha256']:
            raise ValueError('frozen API52 selected byte differs: ' + item['path'])
    profile_rows = {item['path']: item['sha256'] for item in profile['files']}
    for name in EVIDENCE:
        if name in {item['path'] for item in source['files']} or profile_rows.get(name) != digest(raw(ROOT / name)):
            raise ValueError('challenge evidence is not an exact profile-selected addition: ' + name)

    adapter = replace(raw(OLD_ADAPTER).decode(), OLD.name, NEW.name, 1)
    create(NEW_ADAPTER, adapter.encode())
    changes = {}
    schema_name = 'workflow-output-plan.schema.json'
    changes[schema_name] = replace(raw(OLD / schema_name).decode(), old_prefix + 'service.py', new_prefix + 'service.py', 2).encode()
    registry_name = 'workflow_output_registry.py'
    changes[registry_name] = replace(raw(OLD / registry_name).decode(), old_prefix + 'workflow_', new_prefix + 'workflow_', 7).encode()
    bridge_name = 'source_bridge.py'
    bridge = raw(OLD / bridge_name).decode()
    bridge = replace(bridge, '_cal_api52_t16_legacy_local_20261023_0001', '_cal_api53_t16_legacy_local_20261023_0001', 1)
    bridge = replace(bridge, '_cal_api52_t16_source8_local_20261023_0001', '_cal_api53_t16_source8_local_20261023_0001', 1)
    changes[bridge_name] = bridge.encode()
    guard_name = 'guard.py'
    guard = raw(OLD / guard_name).decode()
    guard = replace(guard, OLD_ADAPTER.relative_to(ROOT).as_posix(), NEW_ADAPTER.relative_to(ROOT).as_posix(), 1)
    anchor = "    helper_paths.add('implementation/lab-runtime/local-host/t16-api53-bootstrap-0001/bootstrap.py')\n"
    guard = replace(guard, anchor, anchor +
        "    evidence_paths = {\n" + ''.join("        '" + name + "',\n" for name in EVIDENCE) + "    }\n", 1)
    guard = replace(guard,
        "        elif not row['path'].startswith(package):\n            raise ValueError('foreign successor byte row')",
        "        elif row['path'] not in evidence_paths and not row['path'].startswith(package):\n"
        "            raise ValueError('foreign successor byte row')", 1)
    guard = replace(guard,
        "    if actual_helpers != helper_paths:\n        raise ValueError('external Machine helper closure differs')",
        "    if actual_helpers != helper_paths or {r['path'] for r in rows if r['path'] in evidence_paths} != evidence_paths:\n"
        "        raise ValueError('external Machine/challenge evidence closure differs')", 1)
    changes[guard_name] = guard.encode()

    NEW.mkdir(mode=0o700)
    for item in own:
        name = item['path'][len(old_prefix):]
        if name == 'contract-profile.json':
            continue
        create(NEW / name, changes.get(name, raw(OLD / name)))
    mapped_profile = []
    for item in profile['files']:
        name = item['path']
        if name.startswith(old_prefix):
            mapped_profile.append(row(NEW / name[len(old_prefix):]))
        elif name == OLD_ADAPTER.relative_to(ROOT).as_posix():
            mapped_profile.append(row(NEW_ADAPTER))
        else:
            mapped_profile.append(item)
    if len(mapped_profile) != 33425 or len({item['path'] for item in mapped_profile}) != 33425:
        raise ValueError('API53 profile row uniqueness differs')
    profile['files'] = sorted(mapped_profile, key=lambda item: item['path'])
    profile['integration_members_binding'] = row(NEW / 'integration-members.json')
    profile['claim_ceiling'] = CLAIM
    save(NEW / 'contract-profile.json', profile)

    mapped_source = []
    for item in source['files']:
        name = item['path']
        if name.startswith(old_prefix):
            mapped_source.append(row(NEW / name[len(old_prefix):]))
        elif name == OLD_ADAPTER.relative_to(ROOT).as_posix():
            mapped_source.append(row(NEW_ADAPTER))
        else:
            mapped_source.append(item)
    mapped_source.extend(row(ROOT / name) for name in EVIDENCE)
    if len(mapped_source) != 210 or len({item['path'] for item in mapped_source}) != 210:
        raise ValueError('API53 source row uniqueness differs')
    source['files'] = sorted(mapped_source, key=lambda item: item['path'])
    source['profile_binding'] = row(NEW / 'contract-profile.json')
    source['predecessor_source_manifest_binding'] = row(OLD / 'source-manifest.json')
    source['claim_ceiling'] = CLAIM
    save(NEW / 'source-manifest.json', source)
    receipt = {'schema_version': 'lab-T16-API53-current-challenge-evidence-rebind/v1-candidate',
               'predecessor_source_binding': row(OLD / 'source-manifest.json'),
               'successor_source_binding': row(NEW / 'source-manifest.json'),
               'successor_manifest_sha256': digest(raw(NEW / 'source-manifest.json')),
               'successor_profile_binding': row(NEW / 'contract-profile.json'),
               'adapter_binding': row(NEW_ADAPTER),
               'added_source_rows': [row(ROOT / name) for name in EVIDENCE],
               'source_row_count': 210, 'profile_row_count': 33425,
               'successor_package': NEW.relative_to(ROOT).as_posix(),
               'authority_effect': 'none', 'lesson_applied': False}
    save(NEW / 'rebind-receipt.json', receipt)
    return receipt


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True))
