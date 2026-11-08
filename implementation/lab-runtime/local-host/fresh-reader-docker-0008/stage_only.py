"""One-shot Reader stage-only release candidate.

Import, preflight and tests never open the selected private branch.snapshot.
The --stage-once route is a consumed one-shot and must follow independent
same-state predispatch review of this exact frozen candidate.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

from anchored_copy import (LEAF_FLAGS, close_all, copy_exact, identity,
                           mkdir_exact, parent_chain, reattached, write_exact)
from audit_stage import audit, entries, expected_dirs
from prepare_reader import (HERE, NEW, PACKAGE_SHA, PRODUCER, SOURCE_ROOT,
                            SOURCE_SHA, TERMINAL_SHA, parse, require, sha)
from reader_once import period_current
from stage_reader import source_modes

PREDECESSOR = HERE.parent / 'fresh-reader-docker-0005'
PREDECESSOR_FREEZE_SHA = '28d97810e1c3ac77aceee504a49a4e3e0c57fe08c520053b1c46b62c61e326a1'
RELEASE_BASE = HERE.parent / 'fresh-reader-docker-0007'
RELEASE_BASE_FREEZE_SHA = '3391cd37a4457472534768b9483cab97dbfb375536687684ca44d88d8724f41f'
RELEASE_REVIEW = HERE.parent / 'independent-fresh-reader-docker-review-0007/review.json'
RELEASE_REVIEW_SHA = '8866f60edd3336b2b783c1d54b211060bda008ea3e22a7f818d30bff79041aad'
RELEASE_REVIEW_MD = HERE.parent / 'FRESH-READER-DOCKER-INDEPENDENT-STATIC-REVIEW-0007.md'
RELEASE_REVIEW_MD_SHA = '1fdf79f37aeb3a0b74f4cf632d7f0343fe765db1e5a55028336f4c8841845340'
SELECTION_SHA = '073bc2938e30d6d108ed8b22205eed551d3879c1eab4379d0200c4e9f2d90b22'
READER_SHA = '4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251'
ARCHIVE_SHA = '6d3cfc3f721b9be4fb8a1df14d4f43214709887213eaeae543927f214fdb9323'
BASE_STAGE_PLAN_SHA = 'b062d2fabd9e3881e3918873cf0b5b1b40ed36f08ce27aa22ed7300b932660ae'
STAGE_PLAN_SHA = '82ddcf898953881d49cfb1b99ba0b91f4f9c7393cfde5ae3bb9549b5a769e524'
ATTEMPT = Path('/tmp/cal-reader-stage-20261020-0001-0008')
STAGE_RELEASE_ENABLED = True


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def predecessor() -> None:
    raw = (PREDECESSOR / 'freeze.json').read_bytes()
    require(sha(raw) == PREDECESSOR_FREEZE_SHA, '0005 freeze changed')
    frozen = parse(raw)
    require(frozen['effect'] == 'NOT_RUN' and frozen['selection_sha256'] == SELECTION_SHA and
            frozen['reader_manifest_sha256'] == READER_SHA and
            frozen['source_terminal_sha256'] == TERMINAL_SHA,
            '0005 selected freeze differs')
    for row in frozen['file_bindings']:
        path = Path('/home/vlad_/projects/CyberAlchemy-lab') / row['path']
        require(path.is_file() and not path.is_symlink() and
                path.stat().st_size == row['size'] and sha(path.read_bytes()) == row['sha256'],
                '0005 member changed: ' + row['path'])


def release_basis() -> None:
    """Require the exact frozen neutral controller and both independent reviews."""
    raw = (RELEASE_BASE / 'freeze.json').read_bytes()
    require(sha(raw) == RELEASE_BASE_FREEZE_SHA, '0007 release base freeze changed')
    frozen = parse(raw)
    require(frozen['effect'] == 'NOT_RUN' and
            frozen['selection_sha256'] == SELECTION_SHA and
            frozen['stage_plan_sha256'] == BASE_STAGE_PLAN_SHA and
            frozen['source_terminal_sha256'] == TERMINAL_SHA and
            frozen['status'] == 'READY_FOR_INDEPENDENT_STATIC_REVIEW_HOLD_PRIVATE_STAGE_EFFECT',
            '0007 release base differs')
    for row in frozen['file_bindings']:
        path = Path('/home/vlad_/projects/CyberAlchemy-lab') / row['path']
        require(path.is_file() and not path.is_symlink() and
                path.stat().st_size == row['size'] and sha(path.read_bytes()) == row['sha256'],
                '0007 release base member changed: ' + row['path'])
    require(sha(RELEASE_REVIEW.read_bytes()) == RELEASE_REVIEW_SHA and
            sha(RELEASE_REVIEW_MD.read_bytes()) == RELEASE_REVIEW_MD_SHA,
            '0007 independent review changed')
    review = parse(RELEASE_REVIEW.read_bytes())
    require(review['verdict'] == 'PASS_BOUNDED_NEUTRAL_STAGE_OBSERVATION' and
            review['freeze']['sha256'] == RELEASE_BASE_FREEZE_SHA and
            review['effect'] == 'NOT_RUN', '0007 independent review does not release basis')


def selected_plan() -> tuple[dict[str, tuple[Path, str, int, int]], str]:
    """Exact 986-file copy plan. Does not open the private archive body."""
    selection_raw = (HERE / 'selection.json').read_bytes()
    require(sha(selection_raw) == SELECTION_SHA, 'selection changed')
    selection = parse(selection_raw)
    source_raw = (SOURCE_ROOT / PRODUCER / 'source-manifest.json').read_bytes()
    package_raw = (SOURCE_ROOT / PRODUCER / 'packages/0001/manifest.json').read_bytes()
    require(sha(source_raw) == SOURCE_SHA and sha(package_raw) == PACKAGE_SHA,
            'selected Source manifests changed')
    source, package = parse(source_raw), parse(package_raw)
    archive = package['archive_binding']['path']
    require(package['archive_binding']['sha256'] == ARCHIVE_SHA and
            archive.endswith('/packages/0001/branch.snapshot'), 'archive selection differs')
    rows = source['files'] + package['files'] + [
        {'path': PRODUCER + '/source-manifest.json', 'sha256': SOURCE_SHA},
        {'path': PRODUCER + '/packages/0001/manifest.json', 'sha256': PACKAGE_SHA},
    ]
    require(len(rows) == 978 and len({r['path'] for r in rows}) == 978,
            'Source input inventory differs')
    plan = {}
    for row in rows:
        source_mode, target_mode = source_modes(row['path'])
        plan[row['path']] = (SOURCE_ROOT / row['path'], row['sha256'], source_mode, target_mode)
    role = parse((HERE / 'generated' / NEW / 'source-manifest.json').read_bytes())
    require(sha((HERE / 'generated' / NEW / 'source-manifest.json').read_bytes()) == READER_SHA,
            'Reader manifest changed')
    selected_role = selection['projected_reader_bindings'] + [selection['reader_manifest_binding']]
    require(len(selected_role) == 8 and len({r['path'] for r in selected_role}) == 8 and
            {r['path']: r['sha256'] for r in role['files'] if r['path'].startswith(NEW + '/')}
            == {r['path']: r['sha256'] for r in selection['projected_reader_bindings']},
            'Reader copy closure differs')
    for row in selected_role:
        require(row['path'] not in plan, 'duplicate Source/Reader path')
        plan[row['path']] = (HERE / 'generated' / row['path'], row['sha256'], 0o644, 0o444)
    require(len(plan) == 986 and archive in plan, 'stage inventory differs')
    return plan, archive


def plan_receipt(plan: dict[str, tuple[Path, str, int, int]], archive: str) -> None:
    raw = (HERE / 'stage-plan.json').read_bytes()
    require(sha(raw) == STAGE_PLAN_SHA, 'selected stage-plan bytes changed')
    receipt = parse(raw)
    expected_rows = [{'path': name, 'source_path': str(source), 'sha256': digest,
                      'source_mode': format(source_mode, '04o'),
                      'target_mode': format(target_mode, '04o')}
                     for name, (source, digest, source_mode, target_mode) in sorted(plan.items())]
    require(receipt['effect'] == 'NOT_RUN' and receipt['archive_body_opened'] is False and
            receipt['archive_path'] == archive and receipt['files'] == expected_rows and
            receipt['predecessor_freeze_sha256'] == PREDECESSOR_FREEZE_SHA and
            receipt['selection_sha256'] == SELECTION_SHA,
            'stage plan does not join executed selection')


def private_identity(path: Path) -> tuple[int, ...]:
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
            info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o600,
            'private source attachment differs')
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def preflight(*, now: dt.datetime | None = None, attempt: Path = ATTEMPT) -> dict:
    """Read-only same-state check; never opens branch.snapshot."""
    current = dt.datetime.now(dt.timezone.utc) if now is None else now
    require(current.tzinfo is not None, 'aware UTC time required')
    predecessor()
    release_basis()
    observed = audit(now=current)
    plan, archive = selected_plan()
    plan_receipt(plan, archive)
    period_raw = (SOURCE_ROOT / PRODUCER / 'packages/0001/period.json').read_bytes()
    period = parse(period_raw)
    period_current(period, current)
    require(period['expires_at'] == parse((HERE / 'selection.json').read_bytes())['episode_expires_at'],
            'selected period differs')
    archive_info = private_identity(SOURCE_ROOT / archive)
    require(not os.path.lexists(attempt), 'stage attempt already exists; consumed or occupied')
    require(attempt == ATTEMPT and attempt.parent == Path('/tmp') and attempt.is_absolute(),
            'selected attempt differs')
    fs = os.statvfs(attempt.parent)
    selected_bytes = 0
    for name, (source, _, source_mode, _) in plan.items():
        info = source.lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == source_mode,
                'selected source type/owner/mode differs: ' + name)
        selected_bytes += info.st_size
    require(fs.f_bavail * fs.f_frsize >= selected_bytes * 2 + 16 * 1024 * 1024 and
            fs.f_favail >= len(plan) * 2 + 128, 'insufficient stage blocks or inodes')
    return {'schema_version': 'lab-reader-stage-predispatch/v1',
            'result': 'READY_FOR_INDEPENDENT_REVIEW', 'effect': 'NOT_RUN',
            'attempt': str(attempt), 'selected_files': len(plan),
            'selected_bytes': selected_bytes, 'archive_path': archive,
            'archive_declared_sha256': ARCHIVE_SHA,
            'archive_metadata': {'size': archive_info[6], 'mode': '0600', 'uid': archive_info[3]},
            'archive_current_bytes_checked': False, 'source_terminal_sha256': TERMINAL_SHA,
            'source_manifest_sha256': SOURCE_SHA, 'source_package_sha256': PACKAGE_SHA,
            'reader_manifest_sha256': READER_SHA, 'selection_sha256': SELECTION_SHA,
            'stage_plan_sha256': STAGE_PLAN_SHA,
            'predecessor_freeze_sha256': PREDECESSOR_FREEZE_SHA,
            'release_base_freeze_sha256': RELEASE_BASE_FREEZE_SHA,
            'release_review_sha256': RELEASE_REVIEW_SHA,
            'release_review_md_sha256': RELEASE_REVIEW_MD_SHA,
            'episode_expires_at': period['expires_at'],
            'source_audit': observed['result'],
            'claim_ceiling': 'Read-only selected stage preflight; no private archive body read or Reader effect.'}


def verify_stage(root: Path, plan: dict[str, tuple[Path, str, int, int]]) -> None:
    root_info = root.lstat()
    require(stat.S_ISDIR(root_info.st_mode) and root_info.st_uid == os.getuid() and
            stat.S_IMODE(root_info.st_mode) == 0o755,
            'stage root owner/mode differs')
    intended = set(plan)
    files, dirs = entries(root)
    require(files == intended and dirs == expected_dirs(intended), 'stage file/directory inventory differs')
    for name, (_, digest, _, target_mode) in plan.items():
        item = root / name
        with parent_chain(item) as (parent, chain):
            before = os.stat(item.name, dir_fd=parent, follow_symlinks=False)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                    before.st_uid == os.getuid() and stat.S_IMODE(before.st_mode) == target_mode,
                    'staged bytes/mode/owner differ: ' + name)
            fd = os.open(item.name, LEAF_FLAGS, dir_fd=parent)
            try:
                require(identity(os.fstat(fd)) == identity(before),
                        'staged leaf changed before read: ' + name)
                observed = hashlib.sha256()
                while True:
                    chunk = os.read(fd, 1024 * 1024)
                    if not chunk:
                        break
                    observed.update(chunk)
                require(observed.hexdigest() == digest and
                        identity(os.fstat(fd)) == identity(before),
                        'staged bytes/mode/owner differ: ' + name)
                reattached(item, chain, identity(before))
            finally:
                close_all([fd], sys.exception())
    for name in dirs:
        info = (root / name).lstat()
        private = name == PRODUCER + '/receipts' or name.startswith(PRODUCER + '/packages')
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
                stat.S_IMODE(info.st_mode) == (0o700 if private else 0o755),
                'stage directory owner/mode differs: ' + name)


def execute(*, attempt: Path = ATTEMPT) -> dict:
    """Selected consumed one-shot stage; never call before independent dispatch."""
    require(STAGE_RELEASE_ENABLED, 'private stage disabled pending independent release')
    require(attempt == ATTEMPT, 'selected attempt differs')
    preflight(attempt=attempt)
    plan, archive = selected_plan()
    original = private_identity(SOURCE_ROOT / archive)
    mkdir_exact(attempt, 0o700)
    try:
        marker = {'schema_version': 'lab-reader-stage-consumed/v1',
                  'attempt': str(attempt), 'selection_sha256': SELECTION_SHA,
                  'stage_plan_sha256': STAGE_PLAN_SHA,
                  'predecessor_freeze_sha256': PREDECESSOR_FREEZE_SHA,
                  'release_base_freeze_sha256': RELEASE_BASE_FREEZE_SHA,
                  'source_terminal_sha256': TERMINAL_SHA,
                  'stage_only': True, 'no_retry': True}
        # Durable, no-replace marker precedes the first private read/copy.
        write_exact(attempt / 'consumed.json', encoded(marker))
        attempt_info = attempt.lstat()
        require(stat.S_ISDIR(attempt_info.st_mode) and attempt_info.st_uid == os.getuid() and
                stat.S_IMODE(attempt_info.st_mode) == 0o700,
                'stage attempt owner/mode differs')
        root = attempt / 'root'
        mkdir_exact(root, 0o755)
        dirs = expected_dirs(set(plan))
        for name in sorted(dirs, key=lambda n: (len(Path(n).parts), n)):
            private = name == PRODUCER + '/receipts' or name.startswith(PRODUCER + '/packages')
            mkdir_exact(root / name, 0o700 if private else 0o755)
        for name, (source, digest, source_mode, target_mode) in sorted(plan.items()):
            copy_exact(source, root / name, digest, target_mode, source_mode)
        mkdir_exact(attempt / 'reader-output', 0o700)
        mkdir_exact(attempt / 'evidence', 0o700)
        verify_stage(root, plan)
        require(entries(attempt / 'reader-output') == (set(), set()) and
                entries(attempt / 'evidence') == (set(), set()),
                'Reader output/evidence is not fresh')
        require(private_identity(SOURCE_ROOT / archive) == original,
                'original private archive attachment changed')
        require(audit()['result'] == 'PASS_INERT', 'Source predecessor changed after stage')
        period = parse((root / PRODUCER / 'packages/0001/period.json').read_bytes())
        period_current(period)
        # A durable receipt records an observation, not continuing custody of
        # a same-UID mutable tree. Reader use must independently revalidate.
        terminal = {'schema_version': 'lab-reader-stage-terminal/v1',
                    'overall': 'OBSERVED_STAGE_ONLY', 'effect': 'PRIVATE_STAGE_COPY_ONLY',
                    'attempt': str(attempt), 'input_files': len(plan),
                    'archive_sha256': ARCHIVE_SHA, 'reader_effect': 'NOT_RUN',
                    'source_archive_retained': True, 'no_retry': True,
                    'observation_only': True, 'reader_input_released': False,
                    'requires_external_exit_zero_and_fresh_reader_attachment_check': True,
                    'unknown_receipt_takes_precedence': True,
                    'selection_sha256': SELECTION_SHA,
                    'stage_plan_sha256': STAGE_PLAN_SHA,
                    'source_manifest_sha256': SOURCE_SHA,
                    'source_package_sha256': PACKAGE_SHA,
                    'reader_manifest_sha256': READER_SHA,
                    'source_terminal_sha256': TERMINAL_SHA,
                    'predecessor_freeze_sha256': PREDECESSOR_FREEZE_SHA,
                    'release_base_freeze_sha256': RELEASE_BASE_FREEZE_SHA,
                    'claim_ceiling': 'Observed disposable Reader stage copy only; retained stage is not certified for Reader use without a fresh check. No cold-open, Docker, protected Source8 or original-plan acceptance.'}
        write_exact(attempt / 'evidence' / 'stage-terminal.json', encoded(terminal))
        # These are post-persistence checks. Expiry or mutation while writing
        # the receipt yields UNKNOWN, which supersedes that neutral receipt.
        verify_stage(root, plan)
        require(entries(attempt / 'reader-output') == (set(), set()),
                'Reader output changed after terminal persistence')
        require(private_identity(SOURCE_ROOT / archive) == original,
                'original private archive attachment changed after terminal persistence')
        require(audit()['result'] == 'PASS_INERT',
                'Source predecessor changed after terminal persistence')
        period_current(period)
        return terminal
    except BaseException as error:
        # Retain the consumed attempt and any private partial under its 0700
        # owner directory. Never reuse, delete, rename over, or retry it.
        failure = {'schema_version': 'lab-reader-stage-terminal/v1', 'overall': 'UNKNOWN',
                   'effect': 'PRIVATE_STAGE_COPY_MAY_HAVE_STARTED', 'attempt': str(attempt),
                   'no_retry': True, 'source_archive_not_written_by_controller': True,
                   'partial_stage_retained_for_review': True,
                   'selection_sha256': SELECTION_SHA,
                   'stage_plan_sha256': STAGE_PLAN_SHA,
                   'error_class': type(error).__name__}
        try:
            write_exact(attempt / 'stage-unknown.json', encoded(failure))
        except BaseException as receipt_error:
            error.add_note('UNKNOWN receipt write failed: ' + repr(receipt_error))
        raise


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True))
    elif sys.argv[1:] == ['--stage-once']:
        print(json.dumps(execute(), sort_keys=True))
    else:
        raise SystemExit('expected --preflight or --stage-once')
