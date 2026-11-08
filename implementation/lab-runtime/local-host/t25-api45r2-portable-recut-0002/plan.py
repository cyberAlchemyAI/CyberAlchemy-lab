"""Exact, incomplete API45r2 Docker-rootfs recut with detached authority.

This produces a reviewable selected-file plan and can materialize only its
non-authority repository bytes plus the T07 ABI. It deliberately cannot launch
the API: the 333 live authority rows have no admitted fixture replacement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FROZEN_PLAN = HERE / 'PLAN.json'
FROZEN_PLAN_SHA = 'e4cbad38d8b0f5dee432aa11a6cc4167645ac3ef8444f4b31467b84688b8315d'
INVENTORY = ROOT / 'implementation/lab-runtime/local-host/t25-api45r2-package-preflight-0001/INVENTORY.json'
INVENTORY_SHA = '318894584561d32076213c12b439562b32221a1d5bd11dcf55c78ea40d08b8a5'
T07 = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
T07_SHA = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
ABI = ROOT / 'implementation/lab-runtime/local-host/t03-d95-margin-api-recut-0001/working/installation-0001'
ABI_RECEIPT = ROOT / 'implementation/lab-runtime/local-host/t03-d95-margin-api-recut-0001/installation-receipt.json'
ABI_RECEIPT_SHA = '7f32ee98bfff06ae68c5c90e5874816b405acfb1d076d5edf33a220f059d54b5'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encode(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                       allow_nan=False) + '\n').encode()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def relative(name: str) -> PurePosixPath:
    need(type(name) is str and name and not name.startswith('/'), 'relative path required')
    path = PurePosixPath(name)
    need(path.as_posix() == name and all(part not in ('', '.', '..') for part in path.parts),
         'unsafe selected path')
    return path


def exact(path: Path, digest: str | None, size: int | None = None,
          mode: int | None = None) -> bytes:
    """Read a selected regular file through no-follow ancestor descriptors."""
    need(path.is_absolute() and '..' not in path.parts, 'absolute selected path required')
    handles: list[int] = []
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for part in path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(parent)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode), 'selected regular file required')
            need(mode is None or stat.S_IMODE(before.st_mode) == mode,
                 'selected file mode differs: ' + str(path))
            raw = bytearray()
            while block := os.read(fd, 1024 * 1024):
                raw.extend(block)
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda item: (item.st_dev, item.st_ino, item.st_size,
                                  item.st_mtime_ns, item.st_ctime_ns)
            need(stamp(before) == stamp(after) == stamp(named), 'selected file changed during read')
            need((digest is None or sha(raw) == digest)
                 and (size is None or len(raw) == size),
                 'selected file bytes differ: ' + str(path))
            return bytes(raw)
        finally:
            os.close(fd)
    finally:
        for handle in reversed(handles):
            os.close(handle)


def abi_target(name: str) -> str:
    relative(name)
    if name.startswith('lib/python3.14/'):
        return 'rootfs/usr/' + name
    need(name.startswith(('bin/', 'lib/abi/', 'deps/', 'wheels/')),
         'T07 destination outside closed Docker mapping')
    return 'rootfs/opt/cal-selected-abi/' + name


def selection() -> tuple[dict, dict[str, dict]]:
    inventory = json.loads(exact(INVENTORY, INVENTORY_SHA))
    t07 = json.loads(exact(T07, T07_SHA))
    receipt = json.loads(exact(ABI_RECEIPT, ABI_RECEIPT_SHA))
    need(inventory.get('schema_version') == 'lab-t25-api45r2-portability-preflight/v1'
         and inventory.get('source_manifest_rows') == 207
         and inventory.get('schema_execution_rows') == 5043
         and inventory.get('union_rows') == 5250
         and inventory.get('top_level_startup_read_count_outside_selected_rows') == 15
         and inventory.get('class_counts') == {
             'absolute_host_dependency': 625, 'live_authority_state': 333,
             'repository_code_or_contract': 2851,
             'repository_evidence_or_documentation': 1441},
         'selected API45r2 inventory differs')
    need(receipt.get('selected_dependency_sha256') == T07_SHA
         and receipt.get('owned_member_count') == 1010
         and receipt.get('owned_root') == ABI.relative_to(ROOT).as_posix(),
         'selected ABI receipt differs')
    need(len(t07.get('inputs', [])) == 720 and len(t07.get('wheel_members', {})) == 290,
         'T07 ABI member counts differ')
    members = {row['destination']: row for row in t07['inputs']}
    members.update(t07['wheel_members'])
    need(len(members) == 1010, 'T07 ABI member collision')
    for name, row in members.items():
        relative(name)
        need(type(row.get('sha256')) is str and len(row['sha256']) == 64
             and type(row.get('size_bytes')) is int and row['size_bytes'] >= 0,
             'invalid selected ABI row')
    return inventory, members


def build_plan() -> dict:
    inventory, members = selection()
    main = inventory['rows']
    startup = inventory['top_level_startup_read_rows']
    extras = inventory['extra_guard_rows']
    main_names = [row['path'] for row in main]
    startup_names = [row['path'] for row in startup]
    need(main_names == sorted(set(main_names)) and len(main_names) == 5250
         and startup_names == sorted(set(startup_names)) and len(startup_names) == 15
         and not set(main_names) & set(startup_names)
         and {row['path'] for row in extras} <= set(startup_names),
         'selected API45r2 row closure differs')
    selected = main + startup
    need(len(selected) == 5265 and all(row['current_byte_status'] == 'matching'
                                      for row in selected),
         'API45r2 selected byte snapshot differs')
    absolute = [row for row in selected if row['class'] == 'absolute_host_dependency']
    authority = [row for row in selected if row['class'] == 'live_authority_state']
    need(len(absolute) == 625 and len(authority) == 333,
         'API45r2 host or authority partition differs')
    for row in absolute:
        name = row['path']
        need(name.startswith('/usr/lib/python3.14/'), 'absolute host path outside T07 mapping')
        dest = name.removeprefix('/usr/')
        need(dest in members and members[dest]['sha256'] == row['sha256'],
             'absolute API row lacks exact T07 ABI member')
    for row in authority:
        name = relative(row['path'])
        need(name.parts[0] == 'authority'
             and not {'private', 'secrets', 'protected'} & set(name.parts),
             'authority selection outside detached fixture boundary')
    files = []
    for name, row in sorted(members.items()):
        files.append({'target': abi_target(name), 'source': str(ABI / name),
                      'sha256': row['sha256'], 'size_bytes': row['size_bytes'],
                      'mode': 0o755 if row.get('kind') in {'interpreter', 'native-executable'}
                      or name == 'lib/abi/ld-linux-x86-64.so.2' else 0o644,
                      'origin': 't07-abi'})
    for row in selected:
        if row['class'] in ('absolute_host_dependency', 'live_authority_state'):
            continue
        name = relative(row['path'])
        need(not {'private', 'secrets', 'protected'} & set(name.parts),
             'repository private path outside package')
        source = ROOT / row['path']
        state = source.lstat()
        mode = stat.S_IMODE(state.st_mode)
        need(stat.S_ISREG(state.st_mode) and mode in (0o600, 0o644),
             'selected repository source mode or kind differs')
        files.append({'target': 'rootfs/workspace/' + row['path'],
                      'source': str(source), 'sha256': row['sha256'],
                      'size_bytes': None, 'mode': mode, 'origin': 'repository'})
    files.sort(key=lambda row: row['target'])
    targets = [row['target'] for row in files]
    need(len(files) == 5317 and targets == sorted(set(targets))
         and all(not name.startswith('rootfs/workspace/authority/') for name in targets),
         'portable stage target collision or authority leak')
    repository_modes = {'0600': sum(row['mode'] == 0o600 for row in files
                                    if row['origin'] == 'repository'),
                        '0644': sum(row['mode'] == 0o644 for row in files
                                    if row['origin'] == 'repository')}
    need(repository_modes == {'0600': 456, '0644': 3851},
         'selected repository source mode vector differs')
    return {
        'schema_version': 'lab-t25-api45r2-portable-recut-plan/v1-candidate',
        'inventory_sha256': INVENTORY_SHA, 't07_selection_sha256': T07_SHA,
        'abi_installation_receipt_sha256': ABI_RECEIPT_SHA,
        'selected_api_rows': 5265, 'absolute_api_rows_satisfied_by_t07': 625,
        'omitted_live_authority_rows': 333,
        'omitted_authority_vector_sha256': sha(encode([
            {'path': row['path'], 'sha256': row['sha256']} for row in authority])),
        'staged_abi_rows': 1010, 'staged_repository_rows': 4307,
        'repository_source_mode_counts': repository_modes,
        'staged_file_count': len(files), 'files': files,
        'full_api_ready': False, 'original_service_executed': False,
        'authority_effect': 'none',
        'claim_ceiling': 'Selected code/data/ABI staging only; detached authority fixture and transitive startup proof remain open.',
    }


def private_root(path: Path, *, empty: bool) -> None:
    need(path.is_absolute() and '..' not in path.parts, 'absolute stage root required')
    current = path
    while True:
        state = current.lstat()
        need(stat.S_ISDIR(state.st_mode) and not stat.S_ISLNK(state.st_mode),
             'stage root ancestry redirected')
        if current == path:
            need(state.st_uid == os.getuid() and stat.S_IMODE(state.st_mode) == 0o700,
                 'owned mode-0700 stage root required')
        if current == current.parent:
            break
        current = current.parent
    if empty:
        need(not any(path.iterdir()), 'empty stage root required')


def verify_package(base: Path, plan: dict) -> dict:
    need(base.is_dir() and not base.is_symlink(), 'partial package absent or redirected')
    state = base.lstat()
    need(state.st_uid == os.getuid() and stat.S_IMODE(state.st_mode) == 0o700,
         'partial package root owner or mode differs')
    manifest_path = base / 'MANIFEST.json'
    state = manifest_path.lstat()
    need(stat.S_ISREG(state.st_mode) and state.st_uid == os.getuid()
         and stat.S_IMODE(state.st_mode) == 0o600,
         'partial package manifest owner or mode differs')
    raw = exact(manifest_path, None)
    manifest = json.loads(raw)
    need(raw == encode(manifest)
         and set(manifest) == {'schema_version', 'plan_sha256', 'file_count', 'files',
                               'full_api_ready', 'omitted_live_authority_rows',
                               'authority_effect'}
         and manifest['schema_version'] == 'lab-t25-api45r2-partial-rootfs/v1-candidate'
         and manifest['plan_sha256'] == sha(encode(plan))
         and manifest['file_count'] == len(plan['files'])
         and manifest['omitted_live_authority_rows'] == plan['omitted_live_authority_rows']
         and manifest['full_api_ready'] is False
         and manifest['authority_effect'] == 'none',
         'partial package manifest differs from selected plan')
    rows = manifest['files']
    need(type(rows) is list and len(rows) == len(plan['files']),
         'partial package file vector differs')
    expected_files = {'MANIFEST.json'}
    expected_directories = set()
    for index, selected in enumerate(plan['files']):
        row = rows[index]
        need(type(row) is dict
             and set(row) == {'target', 'sha256', 'size_bytes', 'mode'}
             and row['target'] == selected['target']
             and row['sha256'] == selected['sha256']
             and row['mode'] == selected['mode']
             and type(row['size_bytes']) is int and row['size_bytes'] >= 0,
             'partial package selected file row differs')
        name = relative(row['target'])
        need(not str(name).startswith('rootfs/workspace/authority/'),
             'live authority bytes entered partial package')
        expected_files.add(name.as_posix())
        parent = Path(name).parent
        while parent != Path('.'):
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    actual_files = set()
    actual_directories = set()
    for path in base.rglob('*'):
        state = path.lstat()
        name = path.relative_to(base).as_posix()
        need(not stat.S_ISLNK(state.st_mode) and state.st_uid == os.getuid(),
             'partial package linked or foreign member')
        if stat.S_ISDIR(state.st_mode):
            need(stat.S_IMODE(state.st_mode) == 0o700,
                 'partial package directory mode differs')
            actual_directories.add(name)
        elif stat.S_ISREG(state.st_mode):
            actual_files.add(name)
        else:
            raise ValueError('partial package special member')
    need(actual_files == expected_files and actual_directories == expected_directories,
         'partial package file or directory closure differs')
    for row in rows:
        path = base / row['target']
        state = path.lstat()
        need(stat.S_IMODE(state.st_mode) == row['mode'],
             'partial package file mode differs')
        exact(path, row['sha256'], row['size_bytes'])
    return {'status': 'PASS', 'file_count': len(rows), 'manifest_sha256': sha(raw),
            'full_api_ready': False, 'authority_effect': 'none'}


def stage_rows(root: Path, plan: dict) -> dict:
    """Materialize only a fresh private partial rootfs, then publish atomically."""
    private_root(root, empty=True)
    old_umask = os.umask(0o077)
    pending = root / '.pending'
    pending.mkdir(mode=0o700)
    copied = []
    try:
        for row in plan['files']:
            target = pending / relative(row['target'])
            body = exact(Path(row['source']), row['sha256'], row['size_bytes'], row['mode'])
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with target.open('xb') as stream:
                stream.write(body)
                stream.flush()
                os.fsync(stream.fileno())
            target.chmod(row['mode'])
            copied.append({'target': row['target'], 'sha256': row['sha256'],
                           'size_bytes': len(body), 'mode': row['mode']})
        manifest = {'schema_version': 'lab-t25-api45r2-partial-rootfs/v1-candidate',
                    'plan_sha256': sha(encode(plan)), 'file_count': len(copied),
                    'files': copied, 'full_api_ready': False,
                    'omitted_live_authority_rows': plan['omitted_live_authority_rows'],
                    'authority_effect': 'none'}
        manifest_path = pending / 'MANIFEST.json'
        with manifest_path.open('xb') as stream:
            stream.write(encode(manifest)); stream.flush(); os.fsync(stream.fileno())
        manifest_path.chmod(0o600)
        verify_package(pending, plan)
        os.rename(pending, root / 'package')
        return {'status': 'PASS', 'staged_file_count': len(copied),
                'manifest_sha256': sha(encode(manifest)),
                'full_api_ready': False, 'authority_effect': 'none'}
    except BaseException:
        shutil.rmtree(pending, ignore_errors=True)
        raise
    finally:
        os.umask(old_umask)


def replay(root: Path) -> dict:
    private_root(root, empty=False)
    return verify_package(root / 'package', build_plan())


def frozen_plan() -> dict:
    plan = build_plan()
    need(exact(FROZEN_PLAN, FROZEN_PLAN_SHA) == encode(plan),
         'externally frozen partial package plan differs')
    return plan


def detached_replay(root: Path, plan_path: Path, plan_sha: str) -> dict:
    """Verify installed bytes using only an externally selected plan, not source files."""
    private_root(root, empty=False)
    raw = exact(plan_path, plan_sha)
    plan = json.loads(raw)
    need(raw == encode(plan)
         and plan.get('schema_version') == 'lab-t25-api45r2-portable-recut-plan/v1-candidate'
         and plan.get('full_api_ready') is False
         and plan.get('authority_effect') == 'none'
         and plan.get('omitted_live_authority_rows') == 333
         and plan.get('staged_file_count') == 5317,
         'detached selected plan differs')
    return verify_package(root / 'package', plan)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('plan', 'check', 'stage', 'replay',
                                               'verify-detached'))
    parser.add_argument('--output', type=Path, help='new plan JSON path for plan operation')
    parser.add_argument('--root', type=Path, help='existing empty owned mode-0700 root for stage')
    parser.add_argument('--plan-file', type=Path, help='selected external plan for detached verification')
    parser.add_argument('--plan-sha256', help='external plan SHA-256 for detached verification')
    args = parser.parse_args()
    if args.operation == 'verify-detached':
        need(args.root is not None and args.plan_file is not None
             and type(args.plan_sha256) is str and len(args.plan_sha256) == 64
             and args.output is None, 'detached verification requires root and selected plan')
        print(json.dumps(detached_replay(args.root, args.plan_file, args.plan_sha256),
                         sort_keys=True))
        return 0
    plan = build_plan() if args.operation == 'plan' else frozen_plan()
    if args.operation == 'plan':
        need(args.output is not None and args.root is None, 'plan requires --output only')
        with args.output.open('xb') as stream:
            stream.write(encode(plan))
        print(json.dumps({'plan_sha256': sha(encode(plan)), 'file_count': len(plan['files']),
                          'omitted_live_authority_rows': 333}, sort_keys=True))
    elif args.operation == 'check':
        need(args.output is None and args.root is None, 'check takes no output or root')
        for row in plan['files']:
            exact(Path(row['source']), row['sha256'], row['size_bytes'], row['mode'])
        print(json.dumps({'status': 'PASS', 'checked_file_count': len(plan['files']),
                          'plan_sha256': sha(encode(plan)), 'full_api_ready': False}, sort_keys=True))
    elif args.operation == 'stage':
        need(args.output is None and args.root is not None, 'stage requires --root only')
        print(json.dumps(stage_rows(args.root, plan), sort_keys=True))
    else:
        need(args.output is None and args.root is not None, 'replay requires --root only')
        print(json.dumps(replay(args.root), sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
