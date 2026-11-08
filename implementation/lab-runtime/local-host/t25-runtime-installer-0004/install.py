"""Install the selected public fixture and API status-guard slice into one clean root.

This is a bounded T25 prototype. The API Service itself is not installed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import types
import zipfile


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CANDIDATE_CODE = ROOT / 'implementation/lab-runtime/local-host/t25-local-candidate-0001/package.py'
CANDIDATE_CODE_SHA = '891bc19939b719728039447519f0d127805dbca360df533f2459201b42efb4d7'
CANDIDATE_ARCHIVE_SHA = '020f2755bd2687003f15d93a49a1e3bd6a49d838e3efe1398d6731881edce448'
STATUS_CODE = ROOT / 'implementation/lab-runtime/local-host/t25-api40-status-runtime-guard-0002/package.py'
STATUS_CODE_SHA = '0ea1ef5874dc1c1e39e36c2928103d60495fc607000ddb8241d378454e4872b3'
STATUS_ARCHIVE = STATUS_CODE.parent / 'STATUS-RUNTIME-GUARD.zip'
STATUS_ARCHIVE_SHA = '4318ef5de10c3c364b222b8978c896377db5b8a8664ddef27cc7a873887578fe'
HISTORICAL_RECONCILIATION = ROOT / 'implementation/lab-runtime/local-host/t25-original-member-reconciliation-0002/RECONCILIATION.json'
HISTORICAL_RECONCILIATION_SHA = '9956ad0286f6d86c9c124122f077f2eb5442eced8f86c6e0837f150e68c3888b'
SCRATCH = HERE / 'scratch'
NAME = 'runtime'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                       allow_nan=False) + '\n').encode()


def selected_code(path, expected):
    need(path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink(),
         'selected installer dependency absent or redirected')
    current = ROOT
    for part in path.relative_to(ROOT).parts:
        current = current / part
        need(not current.is_symlink(), 'selected installer dependency has a linked ancestor')
    raw = path.read_bytes()
    need(sha(raw) == expected, 'selected installer dependency changed')
    module = types.ModuleType('_cal_t25_selected_' + path.parent.name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def historical_inventory():
    path = HISTORICAL_RECONCILIATION
    need(path.is_file() and not path.is_symlink(), 'historical member inventory unavailable')
    raw = path.read_bytes()
    need(sha(raw) == HISTORICAL_RECONCILIATION_SHA,
         'historical member inventory bytes changed')
    value = json.loads(raw)
    members = value['members']
    need(value['original_member_count'] == len(members) == 363
         and len({member['original_member_ref'] for member in members}) == 363
         and value['unresolved_member_count'] == 363
         and value['original_member_dispositions_complete'] is False
         and value['authority_effect'] == 'none',
         'historical member inventory boundary changed')
    return HISTORICAL_RECONCILIATION_SHA


def selected_inputs():
    historical_inventory()
    candidate = selected_code(CANDIDATE_CODE, CANDIDATE_CODE_SHA)
    status = selected_code(STATUS_CODE, STATUS_CODE_SHA)
    candidate_blob = candidate.build()
    need(sha(candidate_blob) == CANDIDATE_ARCHIVE_SHA,
         'selected candidate archive changed')
    guard_blob = STATUS_ARCHIVE.read_bytes()
    need(sha(guard_blob) == STATUS_ARCHIVE_SHA,
         'selected status guard archive changed')
    return candidate, status, candidate_blob, guard_blob


def status_members(blob, status):
    """Validate the exact retained guard archive before writing any member."""
    need(sha(blob) == STATUS_ARCHIVE_SHA, 'status guard archive bytes changed')
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        infos = archive.infolist()
        expected = ['META/technical-profile.json', 'runtime/status_guard.py'] + [
            'files/' + name for name, _ in status.selected_guard()[1].ROWS]
        names = [info.filename for info in infos]
        need(names == expected and len(set(names)) == len(names),
             'status guard member selection changed')
        need(all(not info.is_dir() and info.compress_type == zipfile.ZIP_STORED
                 and info.create_system == 3 and info.external_attr >> 16 == 0o100644
                 for info in infos), 'unsafe status guard archive member')
        rows = {name: archive.read(name) for name in names}
    guard_raw, guard = status.selected_guard()
    need(rows['runtime/status_guard.py'] == guard_raw
         and rows['META/technical-profile.json'] == status.canonical(status.technical_profile(guard)),
         'status guard control bytes changed')
    for name, digest in guard.ROWS:
        need(sha(rows['files/' + name]) == digest,
             'status guard selected material changed')
    return rows


def private_root(root):
    root = Path(root)
    need(root.is_absolute() and '..' not in root.parts,
         'installer requires an absolute unredirected root')
    current = root
    while True:
        state = current.lstat()
        need(stat.S_ISDIR(state.st_mode) and not stat.S_ISLNK(state.st_mode),
             'installer root ancestry is redirected or not a directory')
        if current == current.parent:
            break
        current = current.parent
    mode = root.lstat()
    need(stat.S_ISDIR(mode.st_mode) and not root.is_symlink()
         and mode.st_uid == os.getuid() and stat.S_IMODE(mode.st_mode) == 0o700,
         'installer requires an owned mode-0700 directory')
    return root


def clean_root(root):
    root = private_root(root)
    need(not any(root.iterdir()), 'installer requires an owned empty mode-0700 directory')
    return root


def private_member(path, directory, mode):
    state = path.lstat()
    need((stat.S_ISDIR(state.st_mode) if directory else stat.S_ISREG(state.st_mode))
         and state.st_uid == os.getuid() and stat.S_IMODE(state.st_mode) == mode,
         'installed runtime control mode or owner changed')


def closure(base):
    rows = []
    for path in sorted(base.rglob('*')):
        relative = path.relative_to(base).as_posix()
        state = path.lstat()
        if stat.S_ISDIR(state.st_mode):
            continue
        need(stat.S_ISREG(state.st_mode) and not path.is_symlink(),
             'installed closure has an unsafe member')
        rows.append({'path': relative, 'sha256': sha(path.read_bytes()),
                     'size': state.st_size})
    return sorted(rows, key=lambda row: row['path'])


def exact_directories(base, file_rows):
    """Reject extra empty directories as well as redirected directory members."""
    expected = set()
    for row in file_rows:
        parent = Path(row['path']).parent
        while parent != Path('.'):
            expected.add(parent.as_posix())
            parent = parent.parent
    actual = set()
    for path in base.rglob('*'):
        need(not path.is_symlink(), 'installed closure has a linked member')
        if path.is_dir():
            actual.add(path.relative_to(base).as_posix())
    need(actual == expected, 'installed directory closure differs')


def archive_closure(candidate_blob, guard_rows):
    """Derive every installed byte expectation from the selected archives."""
    with zipfile.ZipFile(io.BytesIO(candidate_blob)) as archive:
        candidate = [{'path': 'candidate/' + name,
                      'sha256': sha(archive.read(name)),
                      'size': len(archive.read(name))}
                     for name in archive.namelist()]
    status = [{'path': 'status/' + name.removeprefix('files/'),
               'sha256': sha(raw), 'size': len(raw)}
              for name, raw in guard_rows.items()]
    result = sorted(candidate + status, key=lambda row: row['path'])
    need(len({row['path'] for row in result}) == len(result),
         'selected install archives collide')
    return result


def selected_manifest(candidate_blob, guard_blob, files):
    """The entire allowed manifest, derived from exact selected inputs."""
    return {
        'schema_version': 'lab-T25-public-runtime-install/v4',
        'candidate_archive_sha256': sha(candidate_blob),
        'status_archive_sha256': sha(guard_blob),
        'original_historical_member_ids_inventoried': 363,
        'historical_reconciliation_sha256': HISTORICAL_RECONCILIATION_SHA,
        'original_public_file_count': 681,
        'local_candidate_additions': 799,
        'status_selected_files': 7,
        'original_service_executed': False,
        'portable_api_closure_complete': False,
        'authority_effect': 'none',
        'files': files,
    }


def run_guard(status, root, profile_sha, guard_sha):
    guard_path = root / 'status/runtime/status_guard.py'
    raw = guard_path.read_bytes()
    need(sha(raw) == guard_sha, 'installed guard code changed')
    process = subprocess.run(
        [sys.executable, '-I', '-B', '-c', status.BOOT, guard_sha,
         str(guard_path), str(root / 'status'), profile_sha],
        input=raw, cwd=root, capture_output=True, timeout=30)
    need(not process.stderr, 'installed status guard emitted stderr')
    try:
        result = json.loads(process.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError('installed status guard returned invalid JSON') from error
    need(process.returncode == 0 and result == {
        'schema_version': 'lab-api40-status-runtime-guard-result/v1',
        'status': 'PASS', 'operation': 'lab.status', 'verified_file_count': 7,
        'original_service_executed': False,
        'portable_api40_closure_complete': False, 'authority_effect': 'none'},
        'installed status guard refused')
    return result


def install(root):
    """Publish a verified immutable snapshot in one attributed empty root."""
    root = clean_root(root)
    candidate, status, candidate_blob, guard_blob = selected_inputs()
    need(sha(candidate_blob) == CANDIDATE_ARCHIVE_SHA,
         'selected candidate archive bytes changed')
    rows = status_members(guard_blob, status)
    need(not (root / NAME).exists(), 'installed runtime already exists')
    stage = root / '.runtime-staging'
    stage.mkdir(mode=0o700)
    try:
        candidate_root = stage / 'candidate'
        candidate_root.mkdir(mode=0o700)
        prior = os.environ.get('TMPDIR')
        SCRATCH.mkdir(mode=0o700, exist_ok=True)
        need(SCRATCH.is_dir() and not SCRATCH.is_symlink()
             and stat.S_IMODE(SCRATCH.stat().st_mode) == 0o700
             and SCRATCH.stat().st_uid == os.getuid(), 'owned main-filesystem scratch required')
        os.environ['TMPDIR'] = str(SCRATCH)
        tempfile.tempdir = None
        try:
            candidate_result = candidate.extract_verified(candidate_blob, candidate_root)
        finally:
            if prior is None:
                os.environ.pop('TMPDIR', None)
            else:
                os.environ['TMPDIR'] = prior
            tempfile.tempdir = None
        need(candidate_result['original_members'] == 363
             and candidate_result['replayed_additions'] == 799
             and candidate_result['extracted_fixture_context_verified'] is True,
             'selected public candidate did not install')
        status_root = stage / 'status'
        for name, raw in rows.items():
            target = status_root / name.removeprefix('files/')
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(raw)
            target.chmod(0o644)
        guard_result = run_guard(status, stage,
                                 sha(rows['META/technical-profile.json']),
                                 sha(rows['runtime/status_guard.py']))
        files = closure(stage)
        expected_files = archive_closure(candidate_blob, rows)
        exact_directories(stage, expected_files)
        need(files == expected_files,
             'installed files differ from exact selected archives')
        need(guard_result['verified_file_count'] == 7,
             'selected status guard coverage changed')
        manifest = selected_manifest(candidate_blob, guard_blob, files)
        manifest_path = stage / 'install-manifest.json'
        manifest_path.write_bytes(encode(manifest))
        manifest_path.chmod(0o600)
        stage.chmod(0o700)
        private_member(stage, directory=True, mode=0o700)
        private_member(manifest_path, directory=False, mode=0o600)
        os.rename(stage, root / NAME)
        return {'status': 'PASS', 'installed_file_count': len(files),
                'install_manifest_sha256': sha(encode(manifest)),
                'candidate_archive_sha256': sha(candidate_blob),
                'status_archive_sha256': sha(guard_blob),
                'status_guard': guard_result,
                'fixture_context_verified': True,
                'original_service_executed': False,
                'portable_api_closure_complete': False,
                'authority_effect': 'none'}
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def replay(root):
    """Cold-check the complete installed file set and execute the status slice."""
    root = private_root(root)
    base = root / NAME
    private_member(base, directory=True, mode=0o700)
    manifest_path = base / 'install-manifest.json'
    private_member(manifest_path, directory=False, mode=0o600)
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    need(encode(manifest) == manifest_raw, 'installed manifest is not canonical')
    _, status, candidate_blob, guard_blob = selected_inputs()
    need(sha(candidate_blob) == CANDIDATE_ARCHIVE_SHA,
         'selected candidate archive bytes changed')
    expected = selected_manifest(candidate_blob, guard_blob,
                                 archive_closure(candidate_blob, status_members(guard_blob, status)))
    need(manifest == expected,
         'installed manifest differs from selected archive bytes')
    observed = [r for r in closure(base) if r['path'] != 'install-manifest.json']
    need(observed == expected['files'], 'installed byte closure changed')
    exact_directories(base, expected['files'] + [{'path': 'install-manifest.json'}])
    profile = base / 'status/META/technical-profile.json'
    guard = base / 'status/runtime/status_guard.py'
    selected_guard_raw, selected_guard = status.selected_guard()
    need(sha(guard.read_bytes()) == sha(selected_guard_raw), 'installed guard differs from selected code')
    profile_sha = sha(status.canonical(status.technical_profile(selected_guard)))
    need(sha(profile.read_bytes()) == profile_sha, 'installed profile differs from selected bytes')
    result = run_guard(status, base, profile_sha, sha(selected_guard_raw))
    return {'status': 'PASS', 'installed_file_count': len(observed),
            'install_manifest_sha256': sha(manifest_raw),
            'status_guard': result, 'original_service_executed': False,
            'portable_api_closure_complete': False, 'authority_effect': 'none'}


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ('install', 'replay'):
        raise SystemExit('usage: install.py install|replay EXISTING_ROOT')
    result = install(sys.argv[2]) if sys.argv[1] == 'install' else replay(sys.argv[2])
    print(json.dumps(result, sort_keys=True, indent=2))
