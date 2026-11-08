"""Bounded, network-isolated Lean execution; compiled bytes remain untrusted."""
from pathlib import Path
import hashlib
import io
import os
import resource
import selectors
import signal
import subprocess
import tarfile
import time

HERE = Path(__file__).resolve().parent
BWRAP = Path('/usr/bin/bwrap')
MAX_ARCHIVE = 40 * 1024 * 1024
MAX_LOG = 1024 * 1024
PARTS = {'Submitted.olean', 'Submitted.olean.server', 'Submitted.olean.private'}


class IsolationError(RuntimeError):
    def __init__(self, execution, message):
        super().__init__(message)
        self.execution = execution


def limits():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (90, 90))
    resource.setrlimit(resource.RLIMIT_FSIZE, (40*1024*1024, 40*1024*1024))
    resource.setrlimit(resource.RLIMIT_AS, (8*1024**3, 8*1024**3))
    resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
    resource.setrlimit(resource.RLIMIT_NPROC, (1024, 1024))


def command(toolchain, source, trusted, driver, extra=()):
    if not BWRAP.is_file():
        raise IsolationError('unavailable', 'required Bubblewrap isolation is unavailable')
    return [str(BWRAP), '--unshare-all', '--new-session', '--die-with-parent',
        '--cap-drop', 'ALL', '--clearenv', '--ro-bind', '/lib', '/lib',
        '--ro-bind', '/lib64', '/lib64', '--ro-bind', str(toolchain), '/toolchain',
        '--ro-bind', str(source), '/source', '--ro-bind', str(trusted), '/trusted',
        '--ro-bind', str(driver), '/driver', '--dir', '/runtime',
        '--ro-bind', '/usr/bin/bash', '/runtime/bash',
        '--ro-bind', '/usr/bin/tar', '/runtime/tar',
        '--ro-bind', '/usr/bin/cat', '/runtime/cat',
        '--proc', '/proc', '--dev', '/dev', '--size', str(128*1024*1024), '--tmpfs', '/tmp',
        '--setenv', 'PATH', '/toolchain/bin:/runtime',
        '--setenv', 'LEAN_PATH', '/trusted:/source', '--chdir', '/source', *extra]


def run(argv, timeout=90, stdout_limit=MAX_ARCHIVE):
    """Drain bounded streams concurrently; kill the complete sandbox on excess/time."""
    started = time.monotonic()
    try:
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, env={'PATH':'/usr/bin:/bin'}, start_new_session=True,
            preexec_fn=limits)
    except OSError as error:
        raise IsolationError('unavailable', str(error)) from error
    streams = {'stdout':bytearray(), 'stderr':bytearray()}
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, 'stdout')
    selector.register(process.stderr, selectors.EVENT_READ, 'stderr')
    try:
        while selector.get_map():
            if time.monotonic()-started > timeout:
                raise IsolationError('timeout', 'isolated replay exceeded its wall-clock bound; '+bytes(streams['stderr'][-4096:]).decode('utf-8', errors='replace'))
            for key, _ in selector.select(.1):
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                target = streams[key.data]
                target.extend(chunk)
                if len(target) > (stdout_limit if key.data=='stdout' else MAX_LOG):
                    raise IsolationError('provider-error', 'isolated output exceeded its byte bound')
        code = process.wait(timeout=max(.1, timeout-(time.monotonic()-started)))
        return {'returncode':code, 'stdout':bytes(streams['stdout']),
            'stderr':bytes(streams['stderr']), 'elapsed_seconds':time.monotonic()-started}
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        selector.close()
        process.stdout.close()
        process.stderr.close()


def compile_submission(toolchain, source, trusted, driver, timeout=60):
    # No writable host directory is mounted. The archive is an untrusted byte
    # transport: neither compiler logs nor archive metadata establish proof truth.
    argv = command(toolchain, source, trusted, driver,
        ['/runtime/bash', '/driver/compile.sh'])
    result = run(argv, timeout)
    if result['returncode']:
        log = result['stderr'].decode('utf-8', errors='replace')
        category = 'unavailable' if 'bwrap:' in log else 'completed'
        raise IsolationError(category, 'isolated elaboration failed: '+log[:16000])
    files = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(result['stdout']), mode='r:') as archive:
            total = 0
            for member in archive:
                if member.name not in PARTS or member.name in files or not member.isfile():
                    raise ValueError('unexpected compiled-artifact archive member')
                total += member.size
                if total > MAX_ARCHIVE or member.size <= 0:
                    raise ValueError('compiled artifact byte limit')
                files[member.name] = archive.extractfile(member).read()
        if 'Submitted.olean' not in files:
            raise ValueError('missing compiled main artifact')
    except (tarfile.TarError, ValueError, OSError) as error:
        raise IsolationError('completed', 'invalid untrusted compilation transport: '+str(error)) from error
    return files, {'execution':'completed', 'elapsed_seconds':result['elapsed_seconds'],
        'untrusted_log':result['stderr'].decode('utf-8', errors='replace')[:16000],
        'compiled_parts':{name:hashlib.sha256(value).hexdigest() for name,value in files.items()}}
