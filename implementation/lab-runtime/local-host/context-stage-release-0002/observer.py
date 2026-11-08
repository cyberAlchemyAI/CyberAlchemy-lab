"""External one-shot OS observer for exact trusted-local stage effect (unrun)."""
from __future__ import annotations
import hashlib
import json
import os
import stat
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELEASE = HERE / 'release.py'
ATTEMPT = Path('/tmp/cal-context-family-20261020-0001')
MARKER = Path('/tmp/.cal-context-family-20261020-0001-one-shot.json')
OBSERVATION = Path('/tmp/.cal-context-family-20261020-0002-os-observation')
RELEASE_SHA = '83bd7d54352459efb7c949778867e7a66d0beec77b8695aa0ff41dbf67b77981'
SELECTION_SHA = 'c686db8fd070a422cc92a82fb219049bbd1e922a59a4388134ce7fc8e996059c'
ARCHIVE_SHA = '6d3cfc3f721b9be4fb8a1df14d4f43214709887213eaeae543927f214fdb9323'
STAGE_SELECTION_SHA = '6721210d076da6462f904b2836a9e3ff5853be92f395a05ee2b141b517e078bf'
EFFECT_ARGV = ['/usr/bin/python3', '-B', str(RELEASE), '--effect']


def refuse(ok, message):
    if not ok:
        raise RuntimeError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=False, allow_nan=False) + '\n').encode()


def held_small(root, leaf, limit=1024*1024):
    """Read an exact regular leaf in a held no-follow directory."""
    parent = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    fd = None
    try:
        before_parent = os.fstat(parent)
        fd = os.open(leaf, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW |
                     os.O_CLOEXEC, dir_fd=parent)
        before = os.fstat(fd)
        refuse(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
               0 <= before.st_size <= limit, 'observer leaf type or size differs')
        raw = bytearray()
        while True:
            block = os.read(fd, min(65536, before.st_size + 1 - len(raw)))
            if not block:
                break
            raw.extend(block)
            refuse(len(raw) <= before.st_size, 'observer leaf grew')
        after = os.fstat(fd)
        named = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
        final_parent = os.fstat(parent)
        refuse((before.st_dev, before.st_ino, before.st_mode, before.st_uid,
                before.st_gid, before.st_nlink, before.st_size) ==
               (after.st_dev, after.st_ino, after.st_mode, after.st_uid,
                after.st_gid, after.st_nlink, after.st_size) and
               (before.st_dev, before.st_ino) == (named.st_dev, named.st_ino) and
               (before_parent.st_dev, before_parent.st_ino) ==
               (final_parent.st_dev, final_parent.st_ino) and
               len(raw) == before.st_size, 'observer held leaf changed')
        return bytes(raw)
    finally:
        close_errors = []
        for owned in (fd, parent):
            if owned is not None:
                try:
                    os.close(owned)
                except BaseException as exc:
                    close_errors.append(repr(exc))
        if close_errors:
            raise RuntimeError('observer FD cleanup uncertain: '+repr(close_errors))


def pin_dispatch():
    """Read-only dispatch pins; child still repeats complete same-state preflight."""
    refuse(not os.path.lexists(ATTEMPT) and not os.path.lexists(MARKER) and
           not os.path.lexists(OBSERVATION), 'one-shot stage or OS observation consumed')
    release = held_small(HERE, 'release.py', 128*1024)
    selection = held_small(HERE, 'selection.json', 16*1024)
    refuse(hashlib.sha256(release).hexdigest() == RELEASE_SHA and
           hashlib.sha256(selection).hexdigest() == SELECTION_SHA,
           'effect release code or selection digest differs')
    selected = json.loads(selection)
    refuse(selected['status'] == 'EFFECT_ENABLED_ONE_SHOT_NOT_RUN' and
           selected['one_shot_attempt'] == str(ATTEMPT) and
           selected['one_shot_marker'] == str(MARKER) and
           selected['one_shot_observation'] == str(OBSERVATION) and
           selected['security_profile'] == 'trusted_local_fixture' and
           selected['archive']['sha256'] == ARCHIVE_SHA,
           'exact effect selection differs')
    return selected


def _write_once(parent_fd, leaf, value):
    raw = canonical(value)
    fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
                 os.O_CLOEXEC, 0o600, dir_fd=parent_fd)
    primary = None
    try:
        view = memoryview(raw)
        while view:
            count = os.write(fd, view)
            refuse(type(count) is int and count > 0, 'observer write stalled')
            view = view[count:]
        os.fsync(fd)
    except BaseException as exc:
        primary = exc
    try:
        os.close(fd)
    except BaseException as exc:
        raise RuntimeError('observer write cleanup uncertain') from (primary or exc)
    if primary:
        raise RuntimeError('observer write uncertain') from primary
    os.fsync(parent_fd)
    return hashlib.sha256(raw).hexdigest()


def _output(parent_fd, leaf, limit=1024*1024):
    st = os.stat(leaf, dir_fd=parent_fd, follow_symlinks=False)
    if st.st_size > limit:
        return {'size': st.st_size, 'bounded': False, 'sha256': None, 'bytes': None}
    raw = held_small(OBSERVATION, leaf, limit)
    return {'size': len(raw), 'bounded': True,
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': raw}


def observe_effect(timeout=1800):
    """One external effect launch; observation dir remains consumed on uncertainty."""
    pin_dispatch()
    tmp_fd = os.open('/tmp', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                     os.O_CLOEXEC)
    parent_fd = None
    try:
        os.mkdir(OBSERVATION.name, 0o700, dir_fd=tmp_fd)
        os.fsync(tmp_fd)
        parent_fd = os.open(OBSERVATION.name, os.O_RDONLY | os.O_DIRECTORY |
                            os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=tmp_fd)
        st = os.fstat(parent_fd)
        refuse(stat.S_ISDIR(st.st_mode) and st.st_uid == os.geteuid() and
               st.st_gid == os.getegid() and st.st_mode & 0o777 == 0o700,
               'OS observation custody differs')
        _write_once(parent_fd, 'intent.json',
                    {'schema_version': 'lab-context-stage-os-intent/v2',
                     'argv': EFFECT_ARGV, 'release_sha256': RELEASE_SHA,
                     'selection_sha256': SELECTION_SHA,
                     'status': 'CONSUMED_NO_RETRY'})
        stdout_fd = os.open('stdout.bin', os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                            os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent_fd)
        stderr_fd = os.open('stderr.bin', os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                            os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent_fd)
        started = time.time_ns(); child = None; os_exit = None; process_error = None
        try:
            child = subprocess.Popen(EFFECT_ARGV, stdout=stdout_fd,
                                     stderr=stderr_fd, close_fds=True)
            try:
                os_exit = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.kill(); child.wait()
                process_error = 'TIMEOUT_KILLED_UNKNOWN'
        except BaseException as exc:
            process_error = type(exc).__name__
        finally:
            close_errors = []
            for fd in (stdout_fd, stderr_fd):
                try:
                    os.fsync(fd)
                except BaseException as exc:
                    close_errors.append(repr(exc))
                try:
                    os.close(fd)
                except BaseException as exc:
                    close_errors.append(repr(exc))
            if close_errors:
                process_error = 'OUTPUT_FD_CLEANUP_UNKNOWN'
        ended = time.time_ns()
        stdout = _output(parent_fd, 'stdout.bin')
        stderr = _output(parent_fd, 'stderr.bin')
        stage_receipt_sha = None
        stage_receipt_match = False
        if process_error is None and os_exit == 0 and stdout['bounded'] and stderr['bounded']:
            try:
                stated = json.loads(stdout['bytes'])
                stage_raw = held_small(ATTEMPT, 'stage-receipt.json', 32*1024)
                stage = json.loads(stage_raw)
                stage_receipt_sha = hashlib.sha256(stage_raw).hexdigest()
                stage_receipt_match = (stated['status'] == 'STAGE_ONLY_PASS' and
                    stated['receipt_sha256'] == stage_receipt_sha and
                    stage['status'] == 'STAGE_ONLY_PASS' and
                    stage['schema_version'] == 'lab-context-stage-release-receipt/v1-candidate' and
                    stage['selection_sha256'] == STAGE_SELECTION_SHA and
                    stage['archive_sha256'] == ARCHIVE_SHA and
                    stage['archive_size'] == 23550300 and
                    stage['stage_files'] == 1570 and
                    stage['security_profile'] == 'trusted_local_fixture' and
                    stage['original_protected_G01_G02'] == 'UNSATISFIED' and
                    stage['context_launch'] == 'REFUSED')
            except (OSError, ValueError, KeyError, TypeError):
                stage_receipt_match = False
        status = ('OS_EXIT0_STAGE_RECEIPT_MATCHED' if stage_receipt_match else
                  'OS_OBSERVED_STAGE_UNKNOWN')
        value = {'schema_version': 'lab-context-stage-os-observation/v2',
                 'status': status, 'argv': EFFECT_ARGV, 'os_exit_code': os_exit,
                 'process_error': process_error, 'started_ns': started,
                 'ended_ns': ended, 'stdout_sha256': stdout['sha256'],
                 'stdout_size': stdout['size'], 'stdout_bounded': stdout['bounded'],
                 'stderr_sha256': stderr['sha256'], 'stderr_size': stderr['size'],
                 'stderr_bounded': stderr['bounded'], 'stage_receipt_sha256':
                 stage_receipt_sha, 'stage_receipt_match': stage_receipt_match,
                 'retry_allowed': False, 'security_profile': 'trusted_local_fixture',
                 'original_protected_G01_G02': 'UNSATISFIED',
                 'context_launch': 'REFUSED'}
        _write_once(parent_fd, 'result.json', value)
        return value
    finally:
        if parent_fd is not None:
            os.close(parent_fd)
        os.close(tmp_fd)


if __name__ == '__main__':
    if sys.argv[1:] != ['--effect']:
        raise SystemExit('exact --effect command required')
    result = observe_effect()
    print(json.dumps({'status': result['status'], 'os_exit_code': result['os_exit_code'],
                      'observation': str(OBSERVATION)}, sort_keys=True))
    if result['status'] != 'OS_EXIT0_STAGE_RECEIPT_MATCHED':
        raise SystemExit(1)
