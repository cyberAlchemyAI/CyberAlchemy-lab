"""Consumed-once 986-file Reader stage from the independently reviewed Source.

Import and preflight never open the protected branch.snapshot body. A separate
independent static review must release this exact frozen candidate before its
--stage-once route is called. Any attempted effect consumes its own directory.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

from anchored_copy import (LEAF_FLAGS, close_all, copy_exact, identity,
                           mkdir_exact, parent_chain, reattached, write_exact)

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
sys.path.insert(0, str(LOCAL / 'reader-successor-release-0001'))
import release as R  # noqa: E402

RELEASE_FREEZE_SHA = '9505c5b890003b087c8c9f7065cf38b4cd7f9b8d43f3f06ecdf61b69829e092c'
RELEASE_REVIEW_SHA = 'a593c8fbedb44c0941d578c2afb5b401f878f7d1990a1a86b4a0a788d3fd8b58'
RELEASE_REVIEW = LOCAL / 'READER-SUCCESSOR-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md'
SELECTION_SHA = '0891c30ec2af6017233d0ec17ce8b4ae167f9f588eb333a91c0f37a268b7c582'
PLAN_SHA = 'a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b'
REVIEW_SHA = '599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440'
REVIEW = LOCAL / 'context-successor-source-independent-effect-review-0001/review.json'
STAGE_RELEASE_ENABLED = False  # changed only in an independently reviewed successor


class Refused(ValueError):
    pass


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise Refused(reason)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def release_basis() -> None:
    freeze_path = LOCAL / 'reader-successor-release-0001/freeze.json'
    raw = freeze_path.read_bytes()
    need(sha(raw) == RELEASE_FREEZE_SHA, 'READER_RELEASE_FREEZE_DRIFT')
    need(sha(RELEASE_REVIEW.read_bytes()) == RELEASE_REVIEW_SHA,
         'READER_RELEASE_REVIEW_DRIFT')
    freeze = json.loads(raw)
    need(freeze['effect_enabled'] is False, 'READER_RELEASE_EFFECT_DRIFT')
    for row in freeze['file_bindings']:
        item = R.HERE / Path(row['path']).name
        need(item.is_file() and not item.is_symlink() and
             item.stat().st_size == row['size'] and sha(item.read_bytes()) == row['sha256'],
             'READER_RELEASE_MEMBER_DRIFT')


def selected(now: datetime | None = None) -> dict:
    """Read-only exact binding; skips only the protected archive body."""
    release_basis()
    selection_raw = (HERE / 'selection.json').read_bytes()
    plan_raw = (HERE / 'stage-plan.json').read_bytes()
    need(sha(selection_raw) == SELECTION_SHA and sha(plan_raw) == PLAN_SHA,
         'STAGE_SELECTION_DRIFT')
    selection, plan = json.loads(selection_raw), json.loads(plan_raw)
    review_raw = REVIEW.read_bytes()
    need(sha(review_raw) == REVIEW_SHA and
         selection['source_effect_review_sha256'] == REVIEW_SHA and
         selection['source_effect_review_path'] == str(REVIEW.resolve()),
         'SOURCE_EFFECT_REVIEW_DRIFT')
    a = R.frozen_selector()
    root = R.SOURCE_ROOT
    source_raw = (root / a.SOURCE / 'source-manifest.json').read_bytes()
    package_raw = (root / a.SOURCE / 'packages/0001/manifest.json').read_bytes()
    period_raw = (root / a.SOURCE / 'packages/0001/period.json').read_bytes()
    terminal_raw = (root.parent / 'evidence/source-once.terminal.json').read_bytes()
    actual = R.select_stage(source_raw, package_raw, terminal_raw, period_raw,
                            review_raw, REVIEW_SHA,
                            datetime.now(timezone.utc) if now is None else now)
    need(actual['plan_sha256'] == PLAN_SHA and R.encoded(actual['plan']) == plan_raw and
         selection['stage_plan_sha256'] == PLAN_SHA and
         selection['source_package_manifest_sha256'] == sha(package_raw) and
         selection['source_terminal_sha256'] == sha(terminal_raw) and
         selection['source_manifest_sha256'] == sha(source_raw) and
         selection['reader_manifest_sha256'] == plan['reader_manifest_sha256'] and
         selection['archive_sha256'] == plan['source_archive_sha256'] and
         selection['stage_attempt'] == str(R.STAGE_ATTEMPT) and
         selection['reader_attempt'] == str(R.READER_ATTEMPT) and
         selection['no_retry'] is True and selection['effect'] == 'NOT_RUN',
         'STAGE_BINDING_DRIFT')
    need(len(plan['files']) == 986 and
         len({r['path'] for r in plan['files']}) == 986,
         'STAGE_CLOSURE_DRIFT')
    for name, raw in actual['generated_reader_bytes'].items():
        item = HERE / 'generated' / name
        need(item.is_file() and not item.is_symlink() and item.read_bytes() == raw,
             'GENERATED_READER_DRIFT')
    return plan


def entries(root: Path) -> tuple[set[str], set[str]]:
    need(root.is_dir() and not root.is_symlink(), 'STAGE_ROOT_TYPE')
    files, dirs = set(), set()
    for current, children, leaves in os.walk(root, followlinks=False):
        parent = Path(current)
        for name in children + leaves:
            item = parent / name
            info = item.lstat()
            rel = item.relative_to(root).as_posix()
            need(stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode),
                 'STAGE_NONREGULAR_ENTRY')
            if stat.S_ISDIR(info.st_mode):
                dirs.add(rel)
            else:
                files.add(rel)
    return files, dirs


def expected_dirs(names: set[str], source_role: str) -> set[str]:
    dirs = {p.as_posix() for name in names for p in Path(name).parents
            if p.as_posix() != '.'}
    dirs.add(source_role + '/receipts')
    return dirs


def metadata(path: Path, mode: int) -> os.stat_result:
    with parent_chain(path) as (parent, chain):
        info = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
             info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == mode,
             'SOURCE_OR_STAGE_METADATA_DRIFT')
        reattached(path, chain, identity(info))
        return info


def hash_exact(path: Path, digest: str, mode: int) -> None:
    with parent_chain(path) as (parent, chain):
        before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.getuid() and stat.S_IMODE(before.st_mode) == mode,
             'HASH_METADATA_DRIFT')
        fd = os.open(path.name, LEAF_FLAGS, dir_fd=parent)
        try:
            need(identity(os.fstat(fd)) == identity(before), 'HASH_OPEN_DRIFT')
            h = hashlib.sha256()
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
            need(h.hexdigest() == digest and identity(os.fstat(fd)) == identity(before),
                 'HASH_BYTES_DRIFT')
            reattached(path, chain, identity(before))
        finally:
            close_all([fd], sys.exception())


def verify_stage(plan: dict) -> None:
    root = R.STAGE_ROOT
    info = root.lstat()
    need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
         stat.S_IMODE(info.st_mode) == 0o755, 'STAGE_ROOT_MODE')
    names = {r['path'] for r in plan['files']}
    a = R.frozen_selector()
    files, dirs = entries(root)
    need(files == names and dirs == expected_dirs(names, a.SOURCE),
         'STAGE_NAMESPACE_DRIFT')
    for row in plan['files']:
        hash_exact(root / row['path'], row['sha256'], int(row['target_mode'], 8))
    for name in dirs:
        path = root / name
        mode = 0o700 if name == a.SOURCE + '/receipts' or name.startswith(
            a.SOURCE + '/packages') else 0o755
        info = path.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
             stat.S_IMODE(info.st_mode) == mode, 'STAGE_DIRECTORY_MODE')


def preflight(now: datetime | None = None) -> dict:
    plan = selected(now)
    need(not os.path.lexists(R.STAGE_ATTEMPT), 'STAGE_ATTEMPT_CONSUMED')
    state = R.STAGE_ATTEMPT.parent.lstat()
    need(stat.S_ISDIR(state.st_mode) and state.st_uid == os.getuid() and
         stat.S_IMODE(state.st_mode) == 0o700, 'STATE_OWNER_MODE')
    archive = R.frozen_selector().SOURCE + '/packages/0001/branch.snapshot'
    selected_bytes = 0
    for row in plan['files']:
        source = (R.SOURCE_ROOT / row['path'] if row['source_kind'] == 'source-attempt'
                  else HERE / 'generated' / row['path'])
        source_mode = 0o644 if row['source_kind'] == 'generated-reader' else int(
            row['source_mode'], 8)
        info = metadata(source, source_mode)
        selected_bytes += info.st_size
        if row['path'] != archive:
            hash_exact(source, row['sha256'], source_mode)
    fs = os.statvfs(R.STAGE_ATTEMPT.parent)
    need(fs.f_bavail * fs.f_frsize >= selected_bytes * 2 + 16 * 1024 * 1024 and
         fs.f_favail >= 2 * len(plan['files']) + 128, 'STAGE_CAPACITY')
    return {'schema': 'lab-reader-successor-stage-predispatch/v1',
            'status': 'READY_FOR_INDEPENDENT_DISPATCH_REVIEW',
            'effect': 'NOT_RUN', 'attempt': str(R.STAGE_ATTEMPT),
            'files': 986, 'selected_bytes': selected_bytes,
            'archive_declared_sha256': plan['source_archive_sha256'],
            'archive_body_opened': False, 'stage_plan_sha256': PLAN_SHA,
            'source_effect_review_sha256': REVIEW_SHA, 'no_retry': True}


def execute() -> dict:
    need(STAGE_RELEASE_ENABLED, 'STAGE_EFFECT_DISABLED_PENDING_INDEPENDENT_REVIEW')
    preflight()
    plan = selected()
    a = R.frozen_selector()
    archive = a.SOURCE + '/packages/0001/branch.snapshot'
    archive_before = metadata(R.SOURCE_ROOT / archive, 0o600)
    try:
        mkdir_exact(R.STAGE_ATTEMPT, 0o700)
        marker = {'schema': 'lab-reader-successor-stage-consumed/v1',
                  'attempt': str(R.STAGE_ATTEMPT), 'stage_plan_sha256': PLAN_SHA,
                  'source_effect_review_sha256': REVIEW_SHA, 'no_retry': True}
        write_exact(R.STAGE_ATTEMPT / 'consumed.json', encoded(marker))
        mkdir_exact(R.STAGE_ROOT, 0o755)
        names = {r['path'] for r in plan['files']}
        dirs = expected_dirs(names, a.SOURCE)
        for name in sorted(dirs, key=lambda x: (len(Path(x).parts), x)):
            mode = 0o700 if name == a.SOURCE + '/receipts' or name.startswith(
                a.SOURCE + '/packages') else 0o755
            mkdir_exact(R.STAGE_ROOT / name, mode)
        for row in plan['files']:
            source = (R.SOURCE_ROOT / row['path'] if row['source_kind'] == 'source-attempt'
                      else HERE / 'generated' / row['path'])
            source_mode = 0o644 if row['source_kind'] == 'generated-reader' else int(
                row['source_mode'], 8)
            copy_exact(source, R.STAGE_ROOT / row['path'], row['sha256'],
                       int(row['target_mode'], 8), source_mode)
        mkdir_exact(R.STAGE_ATTEMPT / 'evidence', 0o700)
        verify_stage(plan)
        need(identity(metadata(R.SOURCE_ROOT / archive, 0o600)) ==
             identity(archive_before), 'SOURCE_ARCHIVE_ATTACHMENT_DRIFT')
        selected()
        terminal = {'schema': 'lab-reader-successor-stage-terminal/v1',
                    'overall': 'OBSERVED_STAGE_ONLY',
                    'effect': 'PRIVATE_STAGE_COPY_ONLY',
                    'attempt': str(R.STAGE_ATTEMPT), 'input_files': 986,
                    'archive_sha256': plan['source_archive_sha256'],
                    'source_package_manifest_sha256': plan['source_package_manifest_sha256'],
                    'source_terminal_sha256': plan['source_terminal_sha256'],
                    'source_effect_review_sha256': REVIEW_SHA,
                    'reader_manifest_sha256': plan['reader_manifest_sha256'],
                    'stage_plan_sha256': PLAN_SHA, 'reader_effect': 'NOT_RUN',
                    'no_retry': True, 'reader_input_released': False,
                    'requires_external_exit_zero_and_independent_stage_review': True}
        write_exact(R.STAGE_ATTEMPT / 'evidence/stage-terminal.json', encoded(terminal))
        verify_stage(plan)
        need(identity(metadata(R.SOURCE_ROOT / archive, 0o600)) ==
             identity(archive_before), 'SOURCE_ARCHIVE_POST_TERMINAL_DRIFT')
        selected()
        return terminal
    except BaseException as error:
        failure = {'schema': 'lab-reader-successor-stage-terminal/v1',
                   'overall': 'UNKNOWN', 'attempt': str(R.STAGE_ATTEMPT),
                   'effect': 'PRIVATE_STAGE_COPY_MAY_HAVE_STARTED',
                   'stage_plan_sha256': PLAN_SHA, 'no_retry': True,
                   'error_class': type(error).__name__}
        try:
            attempt = R.STAGE_ATTEMPT.lstat()
            if (stat.S_ISDIR(attempt.st_mode) and attempt.st_uid == os.getuid() and
                    stat.S_IMODE(attempt.st_mode) == 0o700):
                write_exact(R.STAGE_ATTEMPT / 'stage-unknown.json', encoded(failure))
        except FileNotFoundError:
            pass
        except BaseException as secondary:
            error.add_note('UNKNOWN receipt write failed: ' + repr(secondary))
        raise


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True))
    elif sys.argv[1:] == ['--stage-once']:
        print(json.dumps(execute(), sort_keys=True))
    else:
        raise SystemExit('expected --preflight or --stage-once')
