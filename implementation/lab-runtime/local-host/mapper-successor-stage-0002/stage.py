"""Effect-disabled, consumed-once Mapper stage for the reviewed 991-row cut.

Selection and preflight never open the protected Source branch.snapshot body.
The copying route remains disabled until a separate independent static review
and a disjoint effect release. No Docker or native execution is present here.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

from anchored_copy import (LEAF_FLAGS, close_all, identity,
                           parent_chain, reattached)
from held_stage import HeldAttempt

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
ADAPTER = LOCAL / 'mapper-successor-stage-adapter-0002'
ADAPTER_FREEZE_SHA = 'c4a15d25587623ec4b73408d2e3e51f767d0d33e4943262b491bae435eabef0e'
ADAPTER_REVIEW = LOCAL / 'MAPPER-SUCCESSOR-STAGE-ADAPTER-INDEPENDENT-STATIC-REVIEW-0002.md'
ADAPTER_REVIEW_SHA = '1be51f0fac1d9a2cdf7780dbc7ffd4bd50aef7448d43358712248bba0e8e93be'
PLAN_SHA = '9041aeedc8b349f6d7315e7ac2544aabda85afdb748663010e00af25e0b9ca2e'
COPY_SHA = '76bfc24841d652cbae039d666bcde80d7899b3b978ebd0291443705543d3dd95'
VERIFIER_SHA = 'e45ba0c5ba2797b2e7ed564caa4528fbf8d79c8b1f42d95f36783ec59cf94416'
NATIVE = (HERE.parents[3] / 'product/lab/release-candidates/v1/interface/'
          'runtime-dependencies-v2-completion-0001/installations/0004/bin/'
          'lab-context-native-reader')
NATIVE_SHA = 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
STAGE_EFFECT_ENABLED = False


class Refused(ValueError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok:
        raise Refused(code)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def _reviewed_adapter():
    freeze_raw = (ADAPTER / 'freeze.json').read_bytes()
    need(sha(freeze_raw) == ADAPTER_FREEZE_SHA and
         sha(ADAPTER_REVIEW.read_bytes()) == ADAPTER_REVIEW_SHA,
         'ADAPTER_FREEZE_OR_REVIEW_DRIFT')
    freeze = json.loads(freeze_raw)
    need(freeze['effect_enabled'] is False and len(freeze['file_bindings']) == 7,
         'ADAPTER_FREEZE_CONTRACT_DRIFT')
    checked_source = None
    for row in freeze['file_bindings']:
        member = LOCAL.parent.parent.parent / row['path']
        need(member.is_file() and not member.is_symlink(), 'ADAPTER_MEMBER_TYPE_DRIFT')
        raw = member.read_bytes()
        need(member.stat().st_size == row['size'] and
             len(raw) == row['size'] and sha(raw) == row['sha256'],
             'ADAPTER_MEMBER_DRIFT')
        if row['path'] == str(ADAPTER.relative_to(LOCAL.parent.parent.parent) / 'adapter.py'):
            checked_source = raw
    # Compile checked source bytes directly; do not select an existing pyc.
    need(checked_source is not None, 'ADAPTER_SOURCE_BINDING_MISSING')
    module = types.ModuleType('cal_reviewed_mapper_adapter_0002')
    module.__file__ = str(ADAPTER / 'adapter.py')
    exec(compile(checked_source, module.__file__, 'exec'), module.__dict__)
    return module


def selected(now: datetime | None = None) -> tuple[dict, dict, dict]:
    adapter = _reviewed_adapter()
    actual = adapter.select_actual(now=datetime.now(timezone.utc) if now is None else now)
    expected = (("stage-plan.json", PLAN_SHA, actual['stage_plan']),
                ("copy-plan.json", COPY_SHA, actual['copy_plan']),
                ("verifier-plan.json", VERIFIER_SHA, actual['verifier_plan']))
    for name, digest, value in expected:
        raw = (HERE / name).read_bytes()
        need(sha(raw) == digest and encoded(value) == raw,
             'PLAN_OR_DYNAMIC_SELECTION_DRIFT')
    plan, copy, verifier = (actual['stage_plan'], actual['copy_plan'],
                            actual['verifier_plan'])
    need(len(plan['files']) == 991 and len({r['path'] for r in plan['files']}) == 991 and
         sum(r['source_kind'] == 'reviewed-reader-stage' for r in plan['files']) == 986 and
         sum(r['source_kind'] == 'generated-mapper' for r in plan['files']) == 5 and
         sum(r['target_mode'] == '0600' for r in plan['files']) == 37 and
         copy['target_directories'] == len(copy['target_directory_names']) == 933 and
         copy['private_source_package_rows'] == 37 and
         len(verifier['expected_package_members']) == 55 and
         copy['source_plan_sha256'] == PLAN_SHA and
         plan['native_sha256'] == copy['native_executable_sha256'] ==
         verifier['native_sha256'] == NATIVE_SHA,
         'STAGE_CLOSURE_DRIFT')
    for name, raw in actual['generated_mapper_bytes'].items():
        item = HERE / 'generated' / name
        need(item.is_file() and not item.is_symlink() and
             item.read_bytes() == raw and stat.S_IMODE(item.stat().st_mode) == 0o644,
             'GENERATED_MAPPER_DRIFT')
    return plan, copy, verifier


def entries(root: Path) -> tuple[set[str], set[str]]:
    need(root.is_dir() and not root.is_symlink(), 'ROOT_TYPE_DRIFT')
    files, dirs = set(), set()
    for current, children, leaves in os.walk(root, followlinks=False):
        parent = Path(current)
        for name in children + leaves:
            item = parent / name
            info = item.lstat()
            rel = item.relative_to(root).as_posix()
            need(stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode),
                 'NONREGULAR_ENTRY')
            (dirs if stat.S_ISDIR(info.st_mode) else files).add(rel)
    return files, dirs


def dir_mode(name: str) -> int:
    # Source private packages and both intentionally empty receipts/packages
    # namespaces are owner-only. Other input directories are read-only exposed.
    source = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
    mapper = 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002'
    return (0o700 if name == source + '/receipts' or
            name.startswith(source + '/packages') or
            name == mapper + '/packages' else 0o755)


def metadata(path: Path, mode: int, directory: bool = False) -> os.stat_result:
    with parent_chain(path) as (parent, chain):
        info = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        need((stat.S_ISDIR(info.st_mode) if directory else
              stat.S_ISREG(info.st_mode) and info.st_nlink == 1) and
             info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == mode,
             'MEMBER_METADATA_DRIFT')
        reattached(path, chain, identity(info))
        return info


def hash_exact(path: Path, digest: str, mode: int) -> None:
    before = metadata(path, mode)
    with parent_chain(path) as (parent, chain):
        fd = os.open(path.name, LEAF_FLAGS, dir_fd=parent)
        try:
            need(identity(os.fstat(fd)) == identity(before), 'HASH_OPEN_DRIFT')
            h = hashlib.sha256()
            while True:
                block = os.read(fd, 1024 * 1024)
                if not block:
                    break
                h.update(block)
            need(h.hexdigest() == digest and identity(os.fstat(fd)) == identity(before),
                 'HASH_BYTES_OR_IDENTITY_DRIFT')
            reattached(path, chain, identity(before))
        finally:
            close_all([fd], sys.exception())


def source_inventory(plan: dict, copy: dict, *, hash_private: bool) -> dict[str, tuple[int, ...]]:
    source_root = Path(copy['source_root'])
    metadata(source_root, 0o755, directory=True)
    source_rows = [r for r in plan['files'] if r['source_kind'] == 'reviewed-reader-stage']
    names = {r['path'] for r in source_rows}
    expected_dirs = set(copy['target_directory_names']) - {
        'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002',
        'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002/packages'}
    files, dirs = entries(source_root)
    need(files == names and dirs == expected_dirs and len(files) == 986 and
         len(dirs) == 931, 'READER_STAGE_INVENTORY_DRIFT')
    for name in sorted(dirs):
        metadata(source_root / name, dir_mode(name), directory=True)
    identities = {}
    for row in source_rows:
        mode = int(row['source_mode'], 8)
        source = source_root / row['path']
        need(row['source_path'] == str(source) and row['target_mode'] == row['source_mode'],
             'READER_SOURCE_ROW_DRIFT')
        identities[row['path']] = identity(metadata(source, mode))
        if hash_private or mode != 0o600:
            hash_exact(source, row['sha256'], mode)
    return identities


def verify_stage(plan: dict, copy: dict, claim: HeldAttempt) -> None:
    claim.directory('root', 0o755)
    files, dirs = claim.inventory()
    need(files == {r['path'] for r in plan['files']} and
         dirs == set(copy['target_directory_names']) and
         len(files) == 991 and len(dirs) == 933,
         'MAPPER_STAGE_INVENTORY_DRIFT')
    for name in dirs:
        claim.directory('root/' + name, dir_mode(name))
    for row in plan['files']:
        claim.file_hash('root/' + row['path'], row['sha256'],
                        int(row['target_mode'], 8))
    mapper = 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002'
    need(not claim.exists('root/' + mapper + '/packages/0001'),
         'MAPPER_OUTPUT_PACKAGE_PRECREATED')


def preflight(now: datetime | None = None) -> dict:
    plan, copy, _ = selected(now)
    attempt = Path(copy['attempt'])
    need(attempt == Path(plan['mapper_attempt']) and
         Path(copy['destination_root']) == attempt / 'root' and
         not os.path.lexists(attempt), 'MAPPER_ATTEMPT_CONSUMED_OR_PATH_DRIFT')
    metadata(attempt.parent, 0o700, directory=True)
    source_inventory(plan, copy, hash_private=False)
    selected_bytes = 0
    for row in plan['files']:
        source = (Path(copy['source_root']) / row['path'] if
                  row['source_kind'] == 'reviewed-reader-stage' else
                  HERE / 'generated' / row['path'])
        mode = int(row['source_mode'], 8) if row['source_mode'] else 0o644
        selected_bytes += metadata(source, mode).st_size
    hash_exact(NATIVE, NATIVE_SHA, 0o755)
    native_size = metadata(NATIVE, 0o755).st_size
    fs = os.statvfs(attempt.parent)
    need(fs.f_bavail * fs.f_frsize >= 2 * (selected_bytes + native_size) +
         16 * 1024 * 1024 and fs.f_favail >= 2 * 991 + 933 + 128,
         'MAPPER_STAGE_CAPACITY')
    return {'schema': 'lab-mapper-successor-stage-predispatch/v1',
            'status': 'READY_FOR_INDEPENDENT_DISPATCH_REVIEW',
            'effect': 'NOT_RUN', 'attempt': str(attempt), 'input_files': 991,
            'source_directories': 931, 'target_directories': 933,
            'private_inventory_rows_metadata_only': 37,
            'archive_body_opened': False,
            'selected_bytes': selected_bytes, 'native_bytes': native_size,
            'stage_plan_sha256': PLAN_SHA, 'copy_plan_sha256': COPY_SHA,
            'adapter_review_sha256': ADAPTER_REVIEW_SHA, 'no_retry': True}


def execute() -> dict:
    need(STAGE_EFFECT_ENABLED, 'MAPPER_STAGE_EFFECT_DISABLED_PENDING_STATIC_REVIEW')
    preflight()
    plan, copy, _ = selected()
    attempt = Path(copy['attempt'])
    root = Path(copy['destination_root'])
    before = source_inventory(plan, copy, hash_private=False)
    native_before = identity(metadata(NATIVE, 0o755))
    claim = HeldAttempt(attempt)
    try:
        claim.claim()
        claim.write('consumed.json', encoded({
            'schema': 'lab-mapper-successor-stage-consumed/v1',
            'attempt': str(attempt), 'stage_plan_sha256': PLAN_SHA,
            'copy_plan_sha256': COPY_SHA, 'no_retry': True}))
        claim.mkdir('root', 0o755)
        claim.bind_root()
        for name in sorted(copy['target_directory_names'],
                           key=lambda s: (len(Path(s).parts), s)):
            claim.mkdir('root/' + name, dir_mode(name))
        for row in plan['files']:
            source = (Path(copy['source_root']) / row['path'] if
                      row['source_kind'] == 'reviewed-reader-stage' else
                      HERE / 'generated' / row['path'])
            source_mode = int(row['source_mode'], 8) if row['source_mode'] else 0o644
            claim.copy(source, 'root/' + row['path'], row['sha256'],
                       int(row['target_mode'], 8), source_mode)
        claim.mkdir('input', 0o700)
        need(Path(copy['native_copy_target']) == attempt / 'input/lab-context-native-reader',
             'NATIVE_TARGET_PATH_DRIFT')
        claim.copy(NATIVE, 'input/lab-context-native-reader', NATIVE_SHA, 0o755, 0o755)
        claim.mkdir('evidence', 0o700)
        verify_stage(plan, copy, claim)
        claim.file_hash('input/lab-context-native-reader', NATIVE_SHA, 0o755)
        claim.attached()
        need(source_inventory(plan, copy, hash_private=True) == before and
             identity(metadata(NATIVE, 0o755)) == native_before,
             'MAPPER_SOURCE_POSTCOPY_DRIFT')
        claim.attached()
        selected()
        terminal = {'schema': 'lab-mapper-successor-stage-terminal/v1',
                    'overall': 'OBSERVED_STAGE_ONLY',
                    'effect': 'PRIVATE_STAGE_COPY_ONLY',
                    'attempt': str(attempt), 'input_files': 991,
                    'source_directories': 931, 'target_directories': 933,
                    'private_rows': 37, 'native_sha256': NATIVE_SHA,
                    'stage_plan_sha256': PLAN_SHA, 'copy_plan_sha256': COPY_SHA,
                    'reader_effect_review_sha256': plan['reader_effect_review_sha256'],
                    'mapper_effect': 'NOT_RUN', 'no_retry': True,
                    'requires_external_exit_zero_and_independent_stage_review': True}
        claim.write('evidence/stage-terminal.json', encoded(terminal))
        verify_stage(plan, copy, claim)
        claim.file_hash('input/lab-context-native-reader', NATIVE_SHA, 0o755)
        claim.attached()
        need(source_inventory(plan, copy, hash_private=True) == before,
             'MAPPER_SOURCE_POSTTERMINAL_DRIFT')
        claim.attached()
        return terminal
    except BaseException as error:
        unknown = {'schema': 'lab-mapper-successor-stage-terminal/v1',
                   'overall': 'UNKNOWN', 'effect': 'PRIVATE_STAGE_COPY_MAY_HAVE_STARTED',
                   'attempt': str(attempt), 'stage_plan_sha256': PLAN_SHA,
                   'no_retry': True, 'error_class': type(error).__name__}
        if claim.claimed and claim.fd is not None:
            try:
                claim.write('stage-unknown.json', encoded(unknown), attached=False)
            except BaseException as secondary:
                error.add_note('UNKNOWN receipt write failed: ' + repr(secondary))
        elif claim.claimed:
            error.add_note('Claim succeeded but no owned attempt FD; UNKNOWN retained by external exit only')
        raise
    finally:
        claim.close(sys.exception())


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True))
    elif sys.argv[1:] == ['--stage-once']:
        print(json.dumps(execute(), sort_keys=True))
    else:
        raise SystemExit('expected --preflight or --stage-once')
