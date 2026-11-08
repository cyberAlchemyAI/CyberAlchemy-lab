"""Read-only independent audit of one consumed trusted-local Context stage."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import stat
from pathlib import Path

BASE = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = BASE / 'implementation/lab-runtime/local-host'
ATTEMPT = Path('/tmp/cal-context-family-20261020-0001')
SOURCE = Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/root')
OBS = Path('/tmp/.cal-context-family-20261020-0002-os-observation')
MARKER = Path('/tmp/.cal-context-family-20261020-0001-one-shot.json')
SELECT = LOCAL / 'context-stage-0001/selection.json'
RELEASE = LOCAL / 'context-stage-release-0002'
PERIOD = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/period.json'
ARCHIVE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001/packages/0001/branch.snapshot'
PINS = {
    'selection': '6721210d076da6462f904b2836a9e3ff5853be92f395a05ee2b141b517e078bf',
    'release_freeze': 'de88e11ec9f81a9954075314106ca7c6ac22d40496a33a3ad3c11525381c9764',
    'static_review': '7468b93b04b442a00baa68b66ffd5cade7cd30716d77bff815d4c63cec522537',
    'archive': '6d3cfc3f721b9be4fb8a1df14d4f43214709887213eaeae543927f214fdb9323',
    'native': 'fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c',
    'period': 'f2633ba3d6c9868740749a3e7d8f288ea7abb461246f964e64c5dc9bf8b14bca',
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def measured(path: Path, limit: int, expected_mode: int | None = None) -> dict:
    """No-follow, one-inode bounded hash; never returns body bytes."""
    before_name = path.lstat()
    need(stat.S_ISREG(before_name.st_mode) and before_name.st_nlink == 1,
         f'nonregular or multilink leaf: {path}')
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        before = os.fstat(fd)
        need((before.st_dev, before.st_ino) == (before_name.st_dev, before_name.st_ino),
             f'name/inode race: {path}')
        need(0 <= before.st_size <= limit, f'size bound: {path}')
        if expected_mode is not None:
            need(before.st_mode & 0o777 == expected_mode, f'mode: {path}')
        h = hashlib.sha256()
        count = 0
        while count < before.st_size:
            chunk = os.read(fd, min(65536, before.st_size - count))
            need(bool(chunk), f'short read: {path}')
            h.update(chunk)
            count += len(chunk)
        need(os.read(fd, 1) == b'', f'file grew: {path}')
        after = os.fstat(fd)
        after_name = path.lstat()
        fields = ('st_dev', 'st_ino', 'st_mode', 'st_uid', 'st_gid', 'st_nlink', 'st_size')
        need(all(getattr(before, x) == getattr(after, x) == getattr(after_name, x)
                 for x in fields), f'file changed: {path}')
        return {'sha256': h.hexdigest(), 'size': count,
                'mode': format(before.st_mode & 0o777, '04o'),
                'uid': before.st_uid, 'gid': before.st_gid,
                'inode': [before.st_dev, before.st_ino]}
    finally:
        os.close(fd)


def compact_json(path: Path, limit=1048576):
    info = measured(path, limit)
    return json.loads(path.read_bytes()), info


def inventory(root: Path):
    files, dirs = set(), set()
    for base, child_dirs, leaves in os.walk(root, topdown=True, followlinks=False):
        base_path = Path(base)
        for name in child_dirs:
            p = base_path / name
            st = p.lstat()
            need(stat.S_ISDIR(st.st_mode) and st.st_mode & 0o777 == 0o700,
                 f'directory type/mode: {p}')
            need(st.st_uid == os.geteuid() and st.st_gid == os.getegid(),
                 f'directory owner: {p}')
            dirs.add(p.relative_to(root).as_posix())
        for name in leaves:
            p = base_path / name
            st = p.lstat()
            need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1,
                 f'file type/links: {p}')
            files.add(p.relative_to(root).as_posix())
    return files, dirs


def source_names(root: Path):
    files = set()
    for base, child_dirs, leaves in os.walk(root, topdown=True, followlinks=False):
        base_path = Path(base)
        for name in child_dirs:
            need(stat.S_ISDIR((base_path / name).lstat().st_mode),
                 f'source directory type: {base_path / name}')
        for name in leaves:
            p = base_path / name
            need(stat.S_ISREG(p.lstat().st_mode), f'source file type: {p}')
            files.add(p.relative_to(root).as_posix())
    return files


def main():
    selected, selected_info = compact_json(SELECT, 1024 * 1024)
    need(selected_info['sha256'] == PINS['selection'], 'selected stage manifest drift')
    freeze, freeze_info = compact_json(RELEASE / 'freeze.json')
    need(freeze_info['sha256'] == PINS['release_freeze'], 'release freeze drift')
    for name, pin in freeze['files_sha256'].items():
        need(measured(RELEASE / name, 1024 * 1024)['sha256'] == pin,
             f'release member drift: {name}')
    need(measured(LOCAL / 'CONTEXT-STAGE-RELEASE-INDEPENDENT-STATIC-REVIEW-0002.md',
                  1024 * 1024)['sha256'] == PINS['static_review'],
         'independent static review drift')
    need(ATTEMPT.lstat().st_mode & 0o777 == 0o700 and
         stat.S_ISDIR(ATTEMPT.lstat().st_mode), 'attempt custody')
    receipt, receipt_info = compact_json(ATTEMPT / 'stage-receipt.json', 32768)
    intent, intent_info = compact_json(OBS / 'intent.json', 32768)
    result, result_info = compact_json(OBS / 'result.json', 32768)
    marker, marker_info = compact_json(MARKER, 32768)
    stdout, stdout_info = compact_json(OBS / 'stdout.bin', 1048576)
    stderr_info = measured(OBS / 'stderr.bin', 1048576)
    need(stat.S_ISDIR(OBS.lstat().st_mode) and OBS.lstat().st_mode & 0o777 == 0o700
         and {p.name for p in OBS.iterdir()} ==
         {'intent.json', 'result.json', 'stdout.bin', 'stderr.bin'},
         'observation custody or namespace differs')
    need(all(x['mode'] == '0600' for x in
             (receipt_info, intent_info, result_info, marker_info, stdout_info,
              stderr_info)), 'receipt/observer/marker mode differs')
    need(stderr_info['size'] == 0, 'nonempty stderr')
    need(marker == {'schema_version': 'lab-context-stage-release-claim/v1',
                    'attempt': str(ATTEMPT), 'selection_sha256': PINS['selection'],
                    'security_profile': 'trusted_local_fixture',
                    'status': 'RESERVED_NO_RETRY'}, 'one-shot marker differs')
    need(intent['status'] == 'CONSUMED_NO_RETRY' and
         intent['release_sha256'] == freeze['files_sha256']['release.py'] and
         intent['selection_sha256'] == freeze['files_sha256']['selection.json'] and
         intent['argv'] == ['/usr/bin/python3', '-B', str(RELEASE / 'release.py'), '--effect'],
         'OS intent differs')
    need(result['status'] == 'OS_EXIT0_STAGE_RECEIPT_MATCHED' and
         result['os_exit_code'] == 0 and result['process_error'] is None and
         result['argv'] == intent['argv'] and result['retry_allowed'] is False and
         result['stage_receipt_match'] is True and
         result['stage_receipt_sha256'] == receipt_info['sha256'] and
         result['stdout_sha256'] == stdout_info['sha256'] and
         result['stderr_sha256'] == stderr_info['sha256'] and
         result['stdout_size'] == stdout_info['size'] and
         result['stderr_size'] == stderr_info['size'] and
         result['started_ns'] < result['ended_ns'] and
         stdout == {'status': 'STAGE_ONLY_PASS',
                    'receipt_sha256': receipt_info['sha256'],
                    'attempt_inode': receipt['attempt_inode']},
         'OS result/stdout/receipt join differs')
    need(result['stdout_bounded'] is True and result['stderr_bounded'] is True,
         'unbounded OS output')
    need(receipt['status'] == 'STAGE_ONLY_PASS' and
         receipt['selection_sha256'] == PINS['selection'] and
         receipt['attempt_inode'] == [ATTEMPT.lstat().st_dev, ATTEMPT.lstat().st_ino] and
         receipt['security_profile'] == 'trusted_local_fixture' and
         receipt['context_launch'] == 'REFUSED' and
         receipt['original_protected_G01_G02'] == 'UNSATISFIED' and
         receipt['archive_body_opened_after_claim'] is True and
         receipt['archive_sha256'] == PINS['archive'] and
         receipt['archive_size'] == 23550300 and
         receipt['native_sha256'] == PINS['native'], 'stage receipt fields differ')
    rows = []
    for field, root, projection in (
        ('existing_family_public', SOURCE, None),
        ('exact_public_checkout_additions', BASE, None),
        ('projected_api_additions', LOCAL / 'context-family-0001/generated', 'api-v25'),
        ('projected_context_additions', LOCAL / 'context-stage-0001/generated', 'context'),
    ):
        for row in selected[field]:
            name = row['path']
            source_name = f'{projection}/{Path(name).name}' if projection else name
            rows.append((name, root / source_name, row, field))
    private = selected['protected_archive_metadata']
    need(private['path'] == ARCHIVE and private['sha256'] == PINS['archive'] and
         private['size'] == 23550300 and private['mode'] == '0600',
         'archive selected metadata differs')
    rows.append((ARCHIVE, SOURCE / ARCHIVE, private, 'protected_archive'))
    need(len(rows) == 1570 and len({r[0] for r in rows}) == 1570,
         'selected row count or duplicate')
    stage_files, stage_dirs = inventory(ATTEMPT / 'root')
    expected_files = {row[0] for row in rows}
    expected_dirs = {parent.as_posix() for name in expected_files
                     for parent in Path(name).parents if parent.as_posix() != '.'}
    need(stage_files == expected_files and stage_dirs == expected_dirs,
         'staged namespace missing/surplus file or directory')
    need(len(stage_files) == receipt['stage_files'] == 1570 and
         len(stage_dirs) == receipt['stage_directories'] == 1021,
         'stage receipt namespace counts differ')
    source_categories = {}
    total_stage_size = 0
    for name, source_path, row, field in rows:
        source_info = measured(source_path, 32 * 1024 * 1024)
        stage_info = measured(ATTEMPT / 'root' / name, 32 * 1024 * 1024)
        expected_mode = row.get('mode') or source_info['mode']
        need(source_info['sha256'] == stage_info['sha256'] == row['sha256'] and
             source_info['size'] == stage_info['size'] and
             stage_info['size'] == row.get('size', stage_info['size']) and
             source_info['mode'] == stage_info['mode'] == expected_mode and
             stage_info['uid'] == os.geteuid() and
             stage_info['gid'] == os.getegid(), f'row differs: {name}')
        source_categories[field] = source_categories.get(field, 0) + 1
        total_stage_size += stage_info['size']
    need(source_categories == {'existing_family_public': 1045,
                               'exact_public_checkout_additions': 512,
                               'projected_api_additions': 5,
                               'projected_context_additions': 7,
                               'protected_archive': 1}, 'row partition differs')
    source_expected = {name for name, _, _, field in rows
                       if field in {'existing_family_public', 'protected_archive'}}
    need(source_names(SOURCE) == source_expected and len(source_expected) == 1046,
         'original Source/Reader/Mapper family namespace differs')
    native_source = measured(Path(selected['native_source_path']), 32 * 1024 * 1024)
    native_stage = measured(ATTEMPT / 'input/lab-context-native-reader', 32 * 1024 * 1024)
    need(native_source['sha256'] == native_stage['sha256'] == PINS['native'] and
         native_source['size'] == native_stage['size'] and
         native_source['mode'] == native_stage['mode'] == '0755',
         'native executable differs')
    attempt_files, attempt_dirs = inventory(ATTEMPT)
    need(attempt_files == {'stage-receipt.json', 'input/lab-context-native-reader'} |
         {'root/' + p for p in expected_files} and
         attempt_dirs == {'root', 'input'} | {'root/' + p for p in expected_dirs},
         'attempt has surplus/missing names')
    period, period_info = compact_json(ATTEMPT / 'root' / PERIOD, 16384)
    need(period_info['sha256'] == PINS['period'], 'Source period differs')
    start = dt.datetime.fromisoformat(period['not_before'])
    end = dt.datetime.fromisoformat(period['expires_at'])
    observed_start = dt.datetime.fromtimestamp(result['started_ns'] / 1e9, dt.timezone.utc)
    observed_end = dt.datetime.fromtimestamp(result['ended_ns'] / 1e9, dt.timezone.utc)
    need(start <= observed_start < observed_end < end and
         end - start == dt.timedelta(hours=24) and
         period['authority_effect'] == 'none' and
         period['actual_owner_outcome'] is None, 'period not current during effect')
    print(json.dumps({
        'verdict': 'PASS_TRUSTED_LOCAL_STAGE_EFFECT',
        'release_freeze_sha256': freeze_info['sha256'],
        'static_review_sha256': PINS['static_review'],
        'selected_stage_sha256': selected_info['sha256'],
        'observer_intent_sha256': intent_info['sha256'],
        'observer_result_sha256': result_info['sha256'],
        'observer_stdout_sha256': stdout_info['sha256'],
        'observer_stderr_sha256': stderr_info['sha256'],
        'one_shot_marker_sha256': marker_info['sha256'],
        'stage_receipt_sha256': receipt_info['sha256'],
        'attempt_inode': receipt['attempt_inode'],
        'stage_files': len(stage_files), 'stage_directories': len(stage_dirs),
        'source_categories': source_categories,
        'stage_bytes_total': total_stage_size,
        'archive_sha256': PINS['archive'], 'archive_size': 23550300,
        'native_sha256': PINS['native'], 'native_size': native_stage['size'],
        'os_exit_code': result['os_exit_code'],
        'observed_start_utc': observed_start.isoformat(),
        'observed_end_utc': observed_end.isoformat(),
        'source_period_start_utc': start.isoformat(),
        'source_period_end_utc': end.isoformat(),
        'retry_allowed': False,
        'protected_body_emitted': False,
        'context_launch': 'REFUSED',
        'original_protected_G01_G02': 'UNSATISFIED',
    }, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
