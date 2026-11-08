"""Effect-disabled Mapper one-shot candidate. No private archive body is opened.

The reviewed Reader PASS is a predecessor, not a Mapper release. A later
disjoint review must select and enable the Mapper effect route.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import importlib.util
import secrets

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = LOCAL.parents[2]
V3 = LOCAL / 'mapper-only-docker-0003'
V1_CONTROLLER = LOCAL / 'mapper-only-docker-controller-0001'
V1_CONTROLLER_FREEZE_SHA = 'ab9c8eb50a69c4c5b18b73c34902931fba8a7bff6de21f1b09ddcf6653b65f86'
V1_CONTROLLER_REVIEW = LOCAL / 'MAPPER-ONLY-DOCKER-CONTROLLER-INDEPENDENT-STATIC-REVIEW-0001.md'
V1_CONTROLLER_REVIEW_SHA = '24f0cf0fd53a2b078442f822c25221ace56f93c6ef7497227c1420eebfa930d5'
V2_CONTROLLER = LOCAL / 'mapper-only-docker-controller-0002'
V2_CONTROLLER_FREEZE_SHA = '25d0f5a144a2a63ca3f74845e08bf27d79434fc8813497578ce362e66fdee93c'
V2_CONTROLLER_REVIEW = LOCAL / 'MAPPER-ONLY-DOCKER-CONTROLLER-INDEPENDENT-STATIC-REVIEW-0002.md'
V2_CONTROLLER_REVIEW_SHA = 'e96b33f616b1c2bcce3644e40da79690ce1d277355f5bc7f38f190c9bf29cfe9'
V3_CONTROLLER = LOCAL / 'mapper-only-docker-controller-0003'
V3_CONTROLLER_FREEZE_SHA = '32a136d4e9c002676f4b6e967e7bbc8a0cc4b8e27126914130e8c8a7aeb3b6ad'
V3_CONTROLLER_REVIEW = LOCAL / 'MAPPER-ONLY-DOCKER-CONTROLLER-INDEPENDENT-STATIC-REVIEW-0003.md'
V3_CONTROLLER_REVIEW_SHA = '495bd5b54adf53ee047888312028aa93c9bec23b57edd309df9311fff57c9e46'
V3_FREEZE_SHA = 'f5636b70cb33ac19e7acf0cf93f54d636f57db3e3a35e4dcda103ab85cb04e55'
V3_REVIEW = LOCAL / 'MAPPER-ONLY-DOCKER-INDEPENDENT-STATIC-REVIEW-0003.md'
V3_REVIEW_SHA = '1be207316e3bc0ad12b6f13210d7fd9bc85a711983ef4b943e8c580e362af510'
STAGE_PLAN = LOCAL / 'fresh-reader-docker-0008/stage-plan.json'
STAGE_PLAN_SHA = '82ddcf898953881d49cfb1b99ba0b91f4f9c7393cfde5ae3bb9549b5a769e524'
STAGE_ROOT = Path('/tmp/cal-reader-stage-20261020-0001-0008/root')
ATTEMPT = Path('/tmp/cal-mapper-only-dev-20261020-0001-controller4')
SOURCE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001'
READER = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0001'
MAPPER = 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0001'
IMAGE = 'sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874'
EFFECT_ENABLED = False
READER_SUCCESSOR = {
    'review_path': str(LOCAL / 'READER-ONLY-UNIFIED-INDEPENDENT-EFFECT-REVIEW-0006.md'),
    'review_sha256': '80886da75c0849f123365d1ac6adcc5b0eea4927d9b268352c4c7c2261c2be39',
    'final_path': '/tmp/cal-reader-only-dev-20261020-0001-unified6/evidence/reader-once.final.json',
    'final_sha256': '42550aa40ea1b3a69e97809f3ba91e36f2fb8aa193636c98d3f99e725e184b6c',
    'provisional_path': '/tmp/cal-reader-only-dev-20261020-0001-unified6/evidence/reader-once.terminal.json',
    'provisional_sha256': '61a3825c99060d18aab1cb04e88bd738d3105144666696cd86147703c9b3ef0f',
    'receipt_path': '/tmp/cal-reader-only-dev-20261020-0001-unified6/reader-output/receipt.json',
    'receipt_sha256': '51a06890a9b5d120409127989578fdb944fccc2f02776fcd89b1713041cd978d',
    'external_path': str(LOCAL / 'reader-only-unified-0006-effect-observation/external-exec.json'),
    'external_sha256': '68035fae0b759b635c6ae8b3d0d686dc92be98c88eb60fec30b7512cecbcb6b3',
    'external_exit': 0,
    'result': 'PASS_REVIEWED_BOUND_TO_DISPOSABLE_FIXTURE',
}
NATIVE_LOAD_PROBE = {
    'path': str(HERE / 'native-probe-observation.json'),
    'sha256': '73c56214a5f095497adf6f4586a7861eb32d677d0ec586f51cbfb4a67540ddea',
    'result': 'PASS_LOAD_ONLY',
}


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def trusted_selection() -> dict:
    require(sha((V3_CONTROLLER / 'freeze.json').read_bytes()) == V3_CONTROLLER_FREEZE_SHA and
            sha(V3_CONTROLLER_REVIEW.read_bytes()) == V3_CONTROLLER_REVIEW_SHA,
            'controller0003 freeze or independent findings changed')
    require(sha((V2_CONTROLLER / 'freeze.json').read_bytes()) == V2_CONTROLLER_FREEZE_SHA and
            sha(V2_CONTROLLER_REVIEW.read_bytes()) == V2_CONTROLLER_REVIEW_SHA,
            'controller0002 freeze or independent findings changed')
    require(sha((V1_CONTROLLER / 'freeze.json').read_bytes()) == V1_CONTROLLER_FREEZE_SHA and
            sha(V1_CONTROLLER_REVIEW.read_bytes()) == V1_CONTROLLER_REVIEW_SHA,
            'controller predecessor freeze or independent findings changed')
    require(sha((V3 / 'freeze.json').read_bytes()) == V3_FREEZE_SHA and
            sha(V3_REVIEW.read_bytes()) == V3_REVIEW_SHA,
            'independently reviewed Mapper construction changed')
    frozen = json.loads((V3 / 'freeze.json').read_bytes())
    for row in frozen['file_bindings']:
        path = V3 / row['path']
        require(path.is_file() and not path.is_symlink() and
                path.stat().st_size == row['size'] and sha(path.read_bytes()) == row['sha256'],
                'reviewed Mapper input changed: ' + row['path'])
    original = json.loads((V3 / 'selection.json').read_bytes())
    current = json.loads((HERE / 'controller-selection.json').read_bytes())
    old_attempt = original['fresh_attempt']
    expected = json.loads(canonical(original))
    fresh = str(ATTEMPT)
    expected['fresh_attempt'] = fresh
    expected['copy_to'] = fresh + '/root'
    expected['copy_and_mount_plan']['output_package_host'] = expected['copy_and_mount_plan']['output_package_host'].replace(old_attempt, fresh)
    for row in expected['copy_and_mount_plan']['container_mounts']:
        if 'source' in row:
            row['source'] = row['source'].replace(old_attempt, fresh)
    expected['effect'] = 'NOT_RUN'
    expected['reader_predecessor']['reader_cold_open_pass_receipt'] = None
    expected['controller_status'] = 'EFFECT_DISABLED_READER_REVIEWED_PASS_HOLD_DISPATCH'
    expected['controller_image_native_load_proved'] = True
    expected['reviewed_reader_successor'] = READER_SUCCESSOR
    expected['native_load_probe'] = NATIVE_LOAD_PROBE
    expected['selected_archive_size_bytes'] = 23550300
    require(current == expected and current['fresh_attempt'] == fresh and
            current['copy_from'] == str(STAGE_ROOT),
            'controller selection changed from reviewed construction')
    return current


def bounded_nofollow_bytes(path: Path, expected_sha: str, limit: int) -> bytes:
    require(path.is_absolute() and '..' not in path.parts, 'unsafe evidence path')
    copy = anchored_copy_module()
    with copy.parent_chain(path) as (parent, chain):
        info = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(info.st_mode) and info.st_size <= limit and
                info.st_nlink == 1 and info.st_uid == os.getuid(),
                'selected evidence type/owner/size differs')
        fd = os.open(path.name, copy.LEAF_FLAGS, dir_fd=parent)
        try:
            require(copy.identity(os.fstat(fd)) == copy.identity(info),
                    'selected evidence detached')
            raw = bytearray()
            while len(raw) <= limit:
                chunk = os.read(fd, min(1024 * 1024, limit + 1 - len(raw)))
                if not chunk:
                    break
                raw.extend(chunk)
            require(len(raw) <= limit and sha(raw) == expected_sha and
                    copy.identity(os.fstat(fd)) == copy.identity(info),
                    'selected evidence bytes or identity differ')
            copy.reattached(path, chain, copy.identity(info))
            return bytes(raw)
        finally:
            copy.close_all([fd], sys.exception())


def exact_stage_plan() -> dict:
    raw = STAGE_PLAN.read_bytes()
    require(sha(raw) == STAGE_PLAN_SHA, 'stage plan changed')
    plan = json.loads(raw)
    rows = plan['files']
    paths = {row['path'] for row in rows}
    require(len(rows) == len(paths) == 986 and
            sum(path.endswith('/branch.snapshot') for path in paths) == 1 and
            all('..' not in Path(path).parts and not path.startswith('/') for path in paths),
            'private copy inventory differs')
    return plan


def reader_predecessor_gate(selection: dict, now: dt.datetime | None = None) -> dict:
    """Read exact private aggregate receipt, never the Source archive body."""
    require(selection['reviewed_reader_successor'] == READER_SUCCESSOR,
            'Reader successor selection differs')
    b = READER_SUCCESSOR
    raw = {key: bounded_nofollow_bytes(Path(b[key + '_path']), b[key + '_sha256'],
                                      1024 * 1024)
           for key in ('review', 'final', 'provisional', 'receipt', 'external')}
    final = json.loads(raw['final'])
    provisional = json.loads(raw['provisional'])
    receipt = json.loads(raw['receipt'])
    external = json.loads(raw['external'])
    require(final['overall'] == final['operation'] == final['cleanup'] == 'PASS' and
            final['finalization'] == 'CLOSED_AND_COMMITTED' and
            final['reader_effect'] == 'DISPOSABLE_READER_DIAGNOSTIC' and
            final['receipt_sha256'] == b['receipt_sha256'] and
            final['client_exit'] == final['daemon_exit'] == 0 and
            final['daemon_exit_consistent'] is True and
            final['absent'] is True and final['forced_cleanup'] is False and
            final['postclose_inputs'] == final['output_attachment'] == 'PASS' and
            final['stream_or_deadline_failure'] is False,
            'Reader final is not selected PASS')
    require(provisional['overall'] == 'UNKNOWN' and
            provisional['candidate_overall'] == 'PASS' and
            final['provisional_sha256'] == b['provisional_sha256'] and
            external['tool_exit_code'] == b['external_exit'] == 0 and
            external['final_sha256'] == b['final_sha256'] and
            external['reader_receipt_sha256'] == b['receipt_sha256'] and
            receipt['schema_version'] == 'lab-disposable-reader-receipt/v1-private' and
            receipt['reader_manifest_sha256'] ==
            selection['manifest']['adapter_source_binding']['sha256'] and
            receipt['source_manifest_sha256'] ==
            selection['manifest']['original_source_binding']['sha256'] and
            receipt['source_package_manifest_sha256'] ==
            selection['manifest']['original_package_binding']['sha256'] and
            receipt['authority_effect'] == 'none' and
            receipt['actual_owner_outcome'] is None,
            'Reader review, external exit or exact predecessor receipt differs')
    selected_time = dt.datetime.now(dt.timezone.utc) if now is None else now
    period_path = STAGE_ROOT / SOURCE / 'packages/0001/period.json'
    plan = exact_stage_plan()
    period_rel = SOURCE + '/packages/0001/period.json'
    period_sha = next(row['sha256'] for row in plan['files'] if row['path'] == period_rel)
    period = json.loads(bounded_nofollow_bytes(period_path, period_sha, 4096))
    require(selected_time.tzinfo is not None and
            dt.datetime.fromisoformat(period['not_before']) <= selected_time <
            dt.datetime.fromisoformat(period['expires_at']),
            'selected Source episode expired')
    return {'result': 'PASS_REVIEWED_READER_PREDECESSOR',
            'receipt_sha256': b['receipt_sha256'],
            'final_sha256': b['final_sha256'],
            'external_exit': 0,
            'episode_expires_at': period['expires_at'],
            'archive_body_opened': False}


def native_load_gate(selection: dict) -> dict:
    require(selection['native_load_probe'] == NATIVE_LOAD_PROBE and
            selection['controller_image_native_load_proved'] is True,
            'native image load selection differs')
    raw = bounded_nofollow_bytes(Path(NATIVE_LOAD_PROBE['path']),
                                 NATIVE_LOAD_PROBE['sha256'], 4096)
    observed = json.loads(raw)
    require(observed['result'] == 'PASS_LOAD_ONLY' and
            observed['image'] == IMAGE and
            observed['native_sha256'] == selection['native']['sha256'] and
            observed['effective_user'] == '1000:1000' and
            observed['userns'] == 'host' and
            observed['container_absent'] is True and
            observed['private_source_mounted'] is False and
            observed['mapper_effect'] is False,
            'native image load-only evidence differs')
    return {'result': 'PASS_LOAD_ONLY', 'native_sha256': observed['native_sha256'],
            'functional_native_protocol_proved': False}


def selected_archive_metadata(info: os.stat_result, selection: dict) -> None:
    require(stat.S_ISREG(info.st_mode) and info.st_uid == 1000 and
            info.st_gid == 1000 and stat.S_IMODE(info.st_mode) == 0o600 and
            info.st_nlink == 1 and info.st_size ==
            selection['selected_archive_size_bytes'] == 23550300,
            'selected private archive metadata differs')


def stage_metadata_gate(selection: dict, plan: dict) -> dict:
    """No archive body read; actual 986-file hash scan belongs to effect dispatch."""
    archive = STAGE_ROOT / plan['archive_path']
    info = archive.lstat()
    selected_archive_metadata(info, selection)
    require(not os.path.lexists(ATTEMPT), 'selected Mapper attempt is occupied')
    require(selection['copy_and_mount_plan']['source_copy_inventory_files'] == 986 and
            selection['copy_and_mount_plan']['source_copy_inventory_directories'] == 931,
            'selected private copy size differs')
    return {'archive_declared_sha256': next(row['sha256'] for row in plan['files']
                                             if row['path'] == plan['archive_path']),
            'archive_size': info.st_size, 'archive_body_opened': False,
            'fresh_attempt_absent': True}


def copy_plan(selection: dict, plan: dict) -> list[dict]:
    """Exact paths/modes for future held-descriptor copy; no bytes opened."""
    rows = []
    for row in plan['files']:
        mode = int(row['target_mode'], 8)
        require(mode in (0o444, 0o600) and row['path'] != MAPPER and
                len(row['sha256']) == 64,
                'copy member mode/path/hash differs')
        rows.append({'source': str(STAGE_ROOT / row['path']),
                     'destination': str(ATTEMPT / 'root' / row['path']),
                     'sha256': row['sha256'], 'mode': mode})
    require(len(rows) == 986 and len({row['destination'] for row in rows}) == 986 and
            all(row['destination'].startswith(str(ATTEMPT / 'root') + '/') for row in rows),
            'Mapper private copy destination escaped')
    return rows


def stage_inventory(root: Path) -> tuple[set[str], set[str]]:
    require(stat.S_ISDIR(root.lstat().st_mode) and not root.is_symlink(),
            'stage root type changed')
    files, directories = set(), set()
    pending = [root]
    while pending:
        parent = pending.pop()
        with os.scandir(parent) as entries:
            for item in entries:
                relative = str(Path(item.path).relative_to(root))
                require(not item.is_symlink(), 'stage contains symlink')
                if item.is_dir(follow_symlinks=False):
                    directories.add(relative)
                    pending.append(Path(item.path))
                elif item.is_file(follow_symlinks=False):
                    files.add(relative)
                else:
                    raise ValueError('stage contains nonregular entry')
    return files, directories


def expected_stage_directories(paths: set[str]) -> set[str]:
    parents = {parent.as_posix() for name in paths for parent in Path(name).parents
               if parent.as_posix() != '.'}
    parents.add(SOURCE + '/receipts')
    return parents


def anchored_copy_module():
    source = LOCAL / 'fresh-reader-docker-0008/anchored_copy.py'
    require(sha(source.read_bytes()) ==
            '0ada376b91b42651bec89602f2318ae39d369773e05b19eab0e1134fd8335259',
            'reviewed no-follow copy primitive changed')
    spec = importlib.util.spec_from_file_location('_cal_mapper_anchored_copy_v1', source)
    require(spec is not None and spec.loader is not None, 'selected copy primitive unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def hash_nofollow(path: Path, copy_module) -> str:
    with copy_module.parent_chain(path) as (parent, chain):
        before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                'selected copy input type changed')
        fd = os.open(path.name, copy_module.LEAF_FLAGS, dir_fd=parent)
        try:
            require(copy_module.identity(os.fstat(fd)) == copy_module.identity(before),
                    'selected copy input detached')
            digest = hashlib.sha256()
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
            require(copy_module.identity(os.fstat(fd)) == copy_module.identity(before),
                    'selected copy input changed during hash')
            copy_module.reattached(path, chain, copy_module.identity(before))
            return digest.hexdigest()
        finally:
            copy_module.close_all([fd], sys.exception())


def copy_rows_nofollow(source_root: Path, target_root: Path, rows: list[dict],
                       expected_dirs: set[str]) -> None:
    """Future effect-only held-descriptor copy; tests use synthetic roots."""
    require(source_root != target_root and not target_root.exists() and
            source_root.is_absolute() and target_root.is_absolute(),
            'private copy source/target collision')
    names = {row['path'] for row in rows}
    require(len(names) == len(rows) and
            all(not name.startswith('/') and '..' not in Path(name).parts for name in names),
            'private copy row path differs')
    require(stage_inventory(source_root) == (names, expected_dirs),
            'selected source stage inventory changed')
    copy = anchored_copy_module()
    copy.mkdir_exact(target_root, 0o755)
    for name in sorted(expected_dirs, key=lambda value: (len(Path(value).parts), value)):
        source_dir = source_root / name
        info = source_dir.lstat()
        mode = stat.S_IMODE(info.st_mode)
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
                info.st_gid == os.getgid() and mode in (0o700, 0o755) and
                not source_dir.is_symlink(), 'selected source directory mode/owner differs')
        copy.mkdir_exact(target_root / name, mode)
    for row in sorted(rows, key=lambda value: value['path']):
        mode = int(row['target_mode'], 8)
        copy.copy_exact(source_root / row['path'], target_root / row['path'],
                        row['sha256'], mode, mode)
    require(stage_inventory(source_root) == (names, expected_dirs) and
            stage_inventory(target_root) == (names, expected_dirs),
            'private source/destination inventory changed after copy')
    for row in rows:
        require(hash_nofollow(source_root / row['path'], copy) == row['sha256'] and
                hash_nofollow(target_root / row['path'], copy) == row['sha256'],
                'private source/destination member changed after copy')


def write_executable_nofollow(path: Path, raw: bytes, expected_sha: str) -> None:
    """Effect-only exact native attachment; no checkout directory is mounted."""
    require(sha(raw) == expected_sha and len(raw) <= 32 * 1024 * 1024,
            'native attachment bytes differ')
    copy = anchored_copy_module()
    with copy.parent_chain(path) as (parent, chain):
        fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     os.O_NOFOLLOW | os.O_CLOEXEC, 0o700, dir_fd=parent)
        try:
            view = memoryview(raw)
            while view:
                count = os.write(fd, view)
                require(count > 0, 'native attachment write stalled')
                view = view[count:]
            os.fchmod(fd, 0o755)
            os.fsync(fd)
            written = os.fstat(fd)
            require(stat.S_ISREG(written.st_mode) and written.st_uid == os.getuid() and
                    written.st_gid == os.getgid() and written.st_nlink == 1 and
                    stat.S_IMODE(written.st_mode) == 0o755 and
                    written.st_size == len(raw), 'native attachment metadata differs')
            os.fsync(parent)
            copy.reattached(path, chain, copy.identity(written))
        finally:
            copy.close_all([fd], sys.exception())
    require(hash_nofollow(path, copy) == expected_sha,
            'native attachment readback differs')


def selected_projected_files(selection: dict) -> dict[str, str]:
    projected = {row['path']: row['sha256'] for row in selection['manifest']['files']
                 if row['path'].startswith(MAPPER + '/')}
    projected[MAPPER + '/source-manifest.json'] = selection['mapper_manifest_sha256']
    require(set(projected) == {MAPPER + '/' + name for name in
                              ('__init__.py', 'base.py', 'build.py', 'policy.json',
                               'source-manifest.json')} and
            all(hash_nofollow(V3 / 'generated' / relative, anchored_copy_module()) == digest
                for relative, digest in projected.items()),
            'Mapper public projection differs')
    return projected


def prepare_exact_attempt(selection: dict, plan: dict, entrypoint_sha: str) -> dict:
    """Effect-only path, unreachable from this candidate's CLI guard.

    The consumed Reader stage remains source-only. This makes a separate 0700
    attempt, copies the exact held stage, then adds the reviewed public Mapper.
    """
    require(EFFECT_ENABLED, 'Mapper private copy disabled in this frozen candidate')
    require(not os.path.lexists(ATTEMPT), 'selected Mapper attempt already exists')
    copy = anchored_copy_module()
    copy.mkdir_exact(ATTEMPT, 0o700)
    rows = plan['files']
    source_names = {row['path'] for row in rows}
    require(len(source_names) == 986 and
            len(expected_stage_directories(source_names)) == 931,
            'selected stage directory graph differs')
    copy_rows_nofollow(STAGE_ROOT, ATTEMPT / 'root', rows,
                       expected_stage_directories(source_names))
    mapper_dir = ATTEMPT / 'root' / MAPPER
    package_dir = mapper_dir / 'packages'
    copy.mkdir_exact(mapper_dir, 0o755)
    copy.mkdir_exact(package_dir, 0o700)
    generated = V3 / 'generated' / MAPPER
    projected = selected_projected_files(selection)
    for relative, digest in sorted(projected.items()):
        copy.copy_exact(V3 / 'generated' / relative,
                        ATTEMPT / 'root' / relative, digest, 0o444, 0o644)
    require(not os.path.lexists(package_dir / '0001') and
            stage_inventory(package_dir) == (set(), set()),
            'selected Mapper package mount is not empty')
    copy.mkdir_exact(ATTEMPT / 'input', 0o755)
    native = REPO / selection['native']['original_path']
    native_raw = bounded_nofollow_bytes(native, selection['native']['sha256'],
                                       32 * 1024 * 1024)
    require(stat.S_IMODE(native.lstat().st_mode) == 0o755,
            'selected native source mode differs')
    write_executable_nofollow(ATTEMPT / 'input/lab-context-native-reader',
                              native_raw, selection['native']['sha256'])
    copy.mkdir_exact(ATTEMPT / 'tool', 0o755)
    entrypoint = HERE / 'mapper_once.py'
    require(hash_nofollow(entrypoint, copy) == entrypoint_sha,
            'reviewed Mapper entrypoint bytes differ')
    copy.copy_exact(entrypoint, ATTEMPT / 'tool/mapper_once.py',
                    entrypoint_sha, 0o444, 0o644)
    return {'attempt': str(ATTEMPT), 'stage_files': 986,
            'projected_mapper_files': 5, 'native_sha256': selection['native']['sha256'],
            'entrypoint_sha256': entrypoint_sha, 'source_stage_modified': False}


def verify_mapped_output(selection: dict) -> dict:
    """Effect-only exact candidate output gate; no authority qualification."""
    require(EFFECT_ENABLED, 'Mapper output inspection disabled in this frozen candidate')
    package = ATTEMPT / 'root' / MAPPER / 'packages/0001'
    expected = set(selection['copy_and_mount_plan']['expected_package_members'])
    files, dirs = stage_inventory(package)
    require(files == expected and dirs == {'semantic', 'governance'} and
            len(files) == 55, 'Mapper output inventory differs')
    copy = anchored_copy_module()
    sizes = 0
    observed = {}
    for name in sorted(files):
        path = package / name
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and
                info.st_gid == os.getgid() and info.st_nlink == 1 and
                stat.S_IMODE(info.st_mode) == 0o600,
                'Mapper output member owner/type/mode differs')
        sizes += info.st_size
        require(sizes <= 268435456, 'Mapper output exceeds selected byte ceiling')
        observed[name] = hash_nofollow(path, copy)
    manifest_sha = observed['manifest.json']
    manifest = json.loads(bounded_nofollow_bytes(package / 'manifest.json',
                                                manifest_sha, 1024 * 1024))
    result = json.loads(bounded_nofollow_bytes(package / 'build-result.json',
                                              observed['build-result.json'], 1024 * 1024))
    expected_bindings = [{'path': MAPPER + '/packages/0001/' + name,
                          'sha256': observed[name]}
                         for name in sorted(files - {'manifest.json'})]
    require(manifest['schema_version'] == 'lab-mapped-context-package/v1-candidate' and
            manifest['files'] == expected_bindings and
            manifest['source_manifest_binding'] ==
            {'path': MAPPER + '/source-manifest.json',
             'sha256': selection['mapper_manifest_sha256']} and
            manifest['authority_effect'] == 'none' and
            manifest['actual_owner_outcome'] is None and
            result['result'] == 'PASS' and result['node_count'] == 15 and
            result['edge_count'] == 10 and result['exact_governance_joins'] == 25 and
            result['cold_native_replay_byte_parity'] is True and
            result['same_signed_source_cut'] is True and
            result['source_sha256'] ==
            selection['manifest']['original_source_binding']['sha256'] and
            result['authority_effect'] == 'none' and
            result['actual_owner_outcome'] is None and result['task_complete'] is False,
            'Mapper output manifest or bounded result differs')
    return {'result': 'PASS_CANDIDATE_OUTPUT_ONLY', 'manifest_sha256': manifest_sha,
            'files': len(files), 'total_bytes': sizes, 'authority_effect': 'none'}


def docker_create_argv(selection: dict, *, label: str) -> list[str]:
    require(len(label) == 32 and all(c in '0123456789abcdef' for c in label),
            'selected attempt label differs')
    name = 'cal-mapper-only-20261020-0001-controller4'
    mounts = selection['copy_and_mount_plan']['container_mounts']
    require(len(mounts) == 4 and mounts[0]['mode'] == 'ro' and
            mounts[1]['target'].endswith('/' + MAPPER + '/packages') and
            mounts[1]['mode'] == 'rw' and mounts[2]['mode'] == 'ro' and
            mounts[3] == {'type': 'tmpfs', 'target': '/attempt/scratch',
                          'size_bytes': 536870912, 'mode': '0700', 'uid': 1000, 'gid': 1000},
            'selected Mapper mount graph differs')
    args = ['/usr/bin/docker', 'create', '--name', name,
            '--label', 'cal.mapper.attempt=' + label,
            '--user', '1000:1000', '--userns', 'host', '--network', 'none',
            '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
            '--pids-limit', '16', '--memory', '1g', '--cpus', '1',
            '-e', 'TMPDIR=/attempt/scratch']
    for mount in mounts[:3]:
        args += ['--mount', 'type=bind,src=' + mount['source'] +
                 ',dst=' + mount['target'] +
                 (',readonly' if mount['mode'] == 'ro' else '')]
    args += ['--tmpfs', '/attempt/scratch:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000',
             '--mount', 'type=bind,src=' + str(ATTEMPT / 'tool') + ',dst=/tool,readonly',
             '--entrypoint', 'python', IMAGE,
             '/tool/mapper_once.py', '--source-sha256',
             selection['manifest']['original_source_binding']['sha256']]
    # The entrypoint tool mount is selected separately; no checkout mount is allowed.
    return args


def preflight() -> dict:
    selection = trusted_selection()
    plan = exact_stage_plan()
    metadata = stage_metadata_gate(selection, plan)
    copy_plan(selection, plan)
    reader = reader_predecessor_gate(selection)
    native = native_load_gate(selection)
    return {'schema_version': 'lab-mapper-one-shot-inert-preflight/v1',
            'result': 'HOLD_EFFECT_DISABLED_PRIVATE_PREDISPATCH', 'effect': 'NOT_RUN',
            'attempt': str(ATTEMPT), 'stage_files': 986,
            'source_manifest_sha256': selection['manifest']['original_source_binding']['sha256'],
            'mapper_manifest_sha256': selection['mapper_manifest_sha256'],
            'reader_predecessor': reader['result'],
            'reader_receipt_sha256': reader['receipt_sha256'],
            'native_image_load': native['result'],
            **metadata,
            'claim_ceiling': 'Controller construction only; native image load-only probe occurred, but no private archive body, Mapper protocol or Mapper Docker effect.'}


def execute_reviewed_one_shot() -> None:
    require(EFFECT_ENABLED, 'Mapper effect disabled in this frozen candidate')
    selection = trusted_selection()
    reader_predecessor_gate(selection, dt.datetime.now(dt.timezone.utc))
    raise RuntimeError('No Mapper effect release or daemon controller is selected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--execute-reviewed-one-shot', action='store_true')
    args = parser.parse_args()
    require(args.preflight != args.execute_reviewed_one_shot, 'select one route')
    if args.preflight:
        print(json.dumps(preflight(), sort_keys=True))
    else:
        execute_reviewed_one_shot()
