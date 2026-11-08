"""Bounded external observer mechanics; real release entrypoint stays disabled."""
import os
from pathlib import Path
import subprocess
import time

import prior_io as IO
import wire_bridge as B

CAPTURE_COMBINED = 8192
EFFECT_ENABLED = False


def join(raw, selected_digest, os_exit, streams, expected):
    B.need(type(os_exit) is int and os_exit == 0 and
           streams['stderr'] == b'' and
           sum(len(streams[k]) for k in ('stdout', 'stderr')) <= CAPTURE_COMBINED, 'OS_UNKNOWN')
    B.need(B.hex64(selected_digest) and B.sha(raw) == selected_digest, 'RECEIPT_DIGEST')
    value = B.parse(raw)
    B.need(type(value) is dict and set(value) == {
        'schema', 'status', 'attempt', 'selection_sha256', 'cid', 'container_name',
        'container_os_exit', 'cid_absent', 'name_absent', 'writer_closed',
        'mediator_joined', 'postclose_readback', 'manifest_sha256'}, 'RECEIPT_FIELDS')
    B.need(value['schema'] == 'context-release-terminal/v1' and
           value['status'] == 'POSTCLOSE_COMPLETE' and
           type(value['container_os_exit']) is int and value['container_os_exit'] == 0 and
           all(value[k] is True for k in ('cid_absent', 'name_absent', 'writer_closed',
                                          'mediator_joined', 'postclose_readback')), 'TERMINAL_UNKNOWN')
    B.need(B.hex64(value['cid']) and B.hex64(value['manifest_sha256']), 'TERMINAL_BINDINGS')
    for key in ('attempt', 'selection_sha256', 'container_name'):
        B.need(value[key] == expected[key], 'TERMINAL_SCOPE')
    B.need(streams['stdout'] == B.encode({'status': 'POSTCLOSE_COMPLETE',
                                         'receipt_sha256': B.sha(raw)}) + b'\n',
           'STDOUT_RECEIPT_JOIN')
    return value


def observe_fixture(directory, command, expected_command, receipt_path, expected, timeout=2):
    """Ordinary owned public subprocess oracle only; cannot select real stage.

    Inputs are controlled test fixtures, not a public authority loader. The
    production observer must be selected by a separate frozen release.
    """
    directory = Path(directory)
    base = directory.parent
    B.need(base.name.startswith('context-release-observer-fixture-') and base.parent == Path('/tmp')
           and directory.name == 'observation' and
           Path(receipt_path) == base / 'terminal.json', 'FIXTURE_SCOPE')
    B.need(type(command) is list and command == expected_command and
           command[:4] == ['/usr/bin/python3.14', '-I', '-B', '-S'] and
           type(timeout) in (int, float) and 0 < timeout <= 3, 'FIXTURE_COMMAND')
    ancestors = B.chain(base)
    fd = process = None
    error = False
    streams = {'stdout': b'', 'stderr': b''}
    candidate = None
    try:
        os.mkdir(directory.name, 0o700, dir_fd=ancestors[-1])
        fd = os.open(directory.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                     dir_fd=ancestors[-1])
        identity = B.identity(os.fstat(fd))
        os.fsync(fd)
        os.fsync(ancestors[-1])
        IO.durable(fd, 'intent.json', B.encode({'status': 'RESERVED_NO_RETRY', 'argv': command,
                                              'expected': expected}))
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env={'PATH': '/usr/bin:/bin'}, close_fds=True,
                                   start_new_session=True)
        try:
            streams = IO.capture(process, time.monotonic() + timeout, CAPTURE_COMBINED)
        except IO.CaptureUnknown as exc:
            streams = exc.outputs
            raise
        # The receipt digest originates in exact child stdout, then joins bytes
        # and externally selected scope; it is not independent child honesty.
        # The selected terminal stdout framing is canonical JSON plus LF.
        # Parse only to locate the digest; join() below checks exact framing.
        summary = B.parse(streams['stdout'], canonical=False)
        digest = summary['receipt_sha256']
        raw = IO.selected(receipt_path, digest)
        candidate = join(raw, digest, process.returncode, streams, expected)
    except BaseException:
        error = True
    finally:
        if process is not None:
            try:
                IO.end_group(process)
                late = IO.capture(process, time.monotonic() + 0.5, CAPTURE_COMBINED)
                for key in streams:
                    streams[key] += late[key]
                B.need(sum(map(len, streams.values())) <= CAPTURE_COMBINED, 'LATE_STREAM_BOUND')
            except BaseException:
                error = True
            for pipe in (process.stdout, process.stderr):
                try:
                    pipe.close()
                except BaseException:
                    error = True
        try:
            if fd is not None:
                observation = B.encode({'status': 'PROVISIONAL_UNKNOWN' if error else 'PROVISIONAL_MATCH',
                                       'os_exit': None if process is None else process.returncode,
                                       'stdout_sha256': B.sha(streams['stdout']),
                                       'stderr_sha256': B.sha(streams['stderr']),
                                       'candidate': candidate, 'retry_allowed': False})
                IO.durable(fd, 'stdout', streams['stdout'])
                IO.durable(fd, 'stderr', streams['stderr'])
                IO.durable(fd, 'observation.json', observation)
        except BaseException:
            error = True
        try:
            B.close_all(([fd] if fd is not None else []) + ancestors)
        except BaseException:
            error = True
    B.need(not error and candidate is not None, 'OBSERVER_UNKNOWN')
    B.need(B.identity(directory.lstat()) == identity, 'POSTCLOSE_ATTACHMENT')
    IO.selected(directory / 'observation.json', B.sha(observation))
    # Recheck exact originals only after every observer handle has closed.
    IO.selected(receipt_path, digest)
    IO.selected(directory / 'stdout', B.sha(streams['stdout']))
    IO.selected(directory / 'stderr', B.sha(streams['stderr']))
    return {'status': 'EXTERNAL_FIXTURE_OS_RECEIPT_MATCH', 'os_exit': process.returncode,
            'receipt_sha256': digest, 'retry_allowed': False}


def execute(*args, **kwargs):
    raise RuntimeError('CONTEXT_DOCKER_RELEASE_EFFECT_DISABLED')
