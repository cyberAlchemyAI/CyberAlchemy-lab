"""Versioned, inactive Mapper import/verify fixture with late native selection.

The effect-capable `probe` exists for a separately reviewed disposable run.
Importing this module, rendering its bridge, and running its pure validators do
not launch Source, Reader, Mapper, or a native executable.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import selectors
import shutil
import signal
import stat
import subprocess
import tempfile
import time

from .. import evidence_guard, role_stage, scratch_reader_probe as reader
from .. import scratch_source_probe as source
from ..held_paths import HeldCanonicalDirectory, _parse_closed
from ..path_contract import ContractError, require
from . import mapper_prepare_0002 as prepare, prefix_probe
from . import prefix_pair_milestone_0001 as milestone
from .plan import ACTIVE_ROLES, plan

FAMILY = reader.FAMILY
SNAPSHOT = reader.SNAPSHOT

# Hold an unclosed Popen object in-process on UNKNOWN so its destructor cannot
# reap an exited leader and free a numeric process-group identity prematurely.
# This does not survive controller exit and grants no closure claim.
_UNCLOSED_CHILDREN: dict[int, subprocess.Popen] = {}

MAPPER_BRIDGE_EXTENSION = '''
# Only the four delayed Mapper leaves are added to the reviewed Reader bridge.
MAPPER=FAMILY/'mapped/source-manifest.json'
MAPPER_SHA='__MAPPER_SHA__'
MAPPED=__MAPPED_ROWS__
NATIVE=SNAPSHOT/'__NATIVE_REL__'
NATIVE_SHA='__NATIVE_SHA__'
@functools.lru_cache(maxsize=1)
def _mapper():
    raw=read({'path':str(MAPPER),'sha256':MAPPER_SHA})
    if _sha(raw)!=MAPPER_SHA:raise ValueError('selected Mapper manifest pin differs')
    value=_parse(raw)
    if (type(value) is not dict or set(value)!={'schema_version','files','environment',
            'original_source_binding','original_package_binding','adapter_source_binding',
            'selected_native_executable','fixture_only','qualification','authority_effect',
            'actual_owner_outcome'} or
            value['schema_version']!='lab-T35-disposable-mapper-source/v2-inactive' or
            value['environment']!={'python':'3.14.4','jsonschema':'4.19.2','cryptography':'46.0.5'} or
            value['fixture_only'] is not True or value['qualification'] is not False or
            value['authority_effect']!='none' or value['actual_owner_outcome'] is not None):
        raise ValueError('closed fixture Mapper manifest claims differ')
    if (value['original_source_binding']!={'path':str(SOURCE),'sha256':SOURCE_SHA} or
            value['original_package_binding']!={'path':str(PACKAGE),'sha256':PACKAGE_SHA} or
            value['adapter_source_binding']!={'path':str(READER),'sha256':READER_SHA} or
            value['selected_native_executable']!={'path':str(NATIVE),'sha256':NATIVE_SHA} or
            '__NATIVE_REL__' in _source()):
        raise ValueError('Mapper predecessor or native selection differs')
    expected=dict(_reader())
    expected['__NATIVE_REL__']=NATIVE_SHA
    expected[str(READER)]=READER_SHA
    if (type(MAPPED) is not dict or len(MAPPED)!=4 or
            set(MAPPED)!={str(FAMILY/'mapped'/n) for n in
                ('__init__.py','base.py','build.py','policy.json')}):
        raise ValueError('exact four delayed Mapper paths required')
    for name,digest in MAPPED.items():
        if name in expected:raise ValueError('Mapper output aliases Reader input')
        expected[name]=digest
    rows=_rows(value['files'])
    if rows!=expected:raise ValueError('Mapper manifest has missing or unselected input')
    return rows
_reader_read=read
def read(row):
    if type(row) is not dict or set(row)!={'path','sha256'} or type(row['path']) is not str:
        raise ValueError('closed Mapper input required')
    name=row['path'];p=PurePosixPath(name)
    if p.as_posix()!=name or '..' in p.parts or '\\\\' in name:
        raise ValueError('noncanonical Mapper input')
    if name not in MAPPED and name!=str(MAPPER) and name!='__NATIVE_REL__':
        return _reader_read(row)
    allowed=(MAPPER_SHA if name==str(MAPPER) else NATIVE_SHA if
             name=='__NATIVE_REL__' else _mapper().get(name))
    if row['sha256']!=allowed:raise ValueError('unselected Mapper role input')
    path=NATIVE if name=='__NATIVE_REL__' else Path(name)
    if path.is_symlink() or any(a.is_symlink() for a in path.parents):
        raise ValueError('Mapper input alias')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        before=os.fstat(fd)
        limit=32*1024*1024 if name=='__NATIVE_REL__' else 2*1024*1024
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or
                before.st_size>limit or
                (name=='__NATIVE_REL__' and stat.S_IMODE(before.st_mode)!=0o400)):
            raise ValueError('Mapper input type or size differs')
        raw=bytearray()
        while len(raw)<before.st_size:
            chunk=os.read(fd,min(1024*1024,before.st_size-len(raw)))
            if not chunk:raise ValueError('Mapper input truncated')
            raw.extend(chunk)
        after=os.fstat(fd);attached=path.stat(follow_symlinks=False)
        key=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
        if key(before)!=key(after) or key(before)!=key(attached) or _sha(raw)!=allowed:
            raise ValueError('Mapper selected input changed')
        return bytes(raw)
    finally:os.close(fd)
def verify_inputs(rows,*,selected_external=()):
    selected=_mapper()
    if type(rows) is not list:raise ValueError('Mapper input rows required')
    external=[r for r in rows if type(r) is dict and type(r.get('path')) is str and r['path'].startswith('/')]
    if selected_external:
        if external!=list(selected_external):raise ValueError('Mapper external selection differs')
    elif any(selected.get(r['path'])!=r['sha256'] for r in external):
        raise ValueError('unselected Mapper external row')
    for row in rows:read(row)
    return len(rows)
'''

MAPPER_RUNNER = '''"""Read-only disposable Mapper base verification only."""
import hashlib,importlib.util,json,sys
from pathlib import Path
family=Path('/work/out/legacy-fixture-source')
snapshot=Path('/work/snapshot')
for forbidden in ('/home/vlad_','/var/lib/cyberalchemy-lab','/run/cyberalchemy-lab'):
    if Path(forbidden).exists():raise ValueError('forbidden host root visible in Mapper sandbox')
sys.path.insert(0,str(snapshot))
root=family/'mapped'
spec=importlib.util.spec_from_file_location('_t35_disposable_mapper',root/'__init__.py',submodule_search_locations=[str(root)])
package=importlib.util.module_from_spec(spec);sys.modules[spec.name]=package
spec.loader.exec_module(package)
base=__import__(spec.name+'.base',fromlist=['*'])
pin='__MAPPER_SHA__'
value=base.verify_source(pin)
if (value['schema_version']!='lab-T35-disposable-mapper-source/v2-inactive' or
        value['fixture_only'] is not True or value['qualification'] is not False or
        value['authority_effect']!='none' or value['actual_owner_outcome'] is not None or
        len(value['files'])!=__MAPPER_INPUT_COUNT__):
    raise ValueError('Mapper read-only selected manifest differs')
print(json.dumps({'result':'PASS-fixture-mapper-readonly',
    'mapper_manifest_sha256':pin,'selected_input_count':len(value['files']),
    'sandbox_host_checkout_absent':True,'sandbox_protected_roots_absent':True,
    'mapped_package_absent':not (root/'packages').exists(),
    'context_absent':not (family/'context').exists(),
    'authority_effect':'none','actual_owner_outcome':None},sort_keys=True),flush=True)
'''

RECEIPT_NAME = 'phase-mapper-readonly-result-0002.json'
STAGES = frozenset(('preflight', 'capture', 'source', 'source_poststate',
                    'reader', 'reader_poststate', 'mapper_materialize',
                    'mapper_readonly', 'mapper_poststate', 'cleanup'))


def render_bridge(source_raw: bytes, package_raw: bytes, reader_raw: bytes,
                  mapper_raw: bytes, stage_control: bytes,
                  mapped: dict[str, bytes]) -> bytes:
    require(type(mapped) is dict and set(mapped) == prepare.MAPPER_NAMES,
            'four selected Mapper role bytes required')
    selected = {str(FAMILY / 'mapped' / name): source._sha(raw)
                for name, raw in mapped.items()}
    text = prefix_probe._prefix_bridge(source._sha(source_raw), source._sha(package_raw),
                                        source._sha(reader_raw), source._sha(stage_control)).decode()
    extension = MAPPER_BRIDGE_EXTENSION
    replacements = {
        '__MAPPER_SHA__': source._sha(mapper_raw),
        '__MAPPED_ROWS__': json.dumps(selected, sort_keys=True, separators=(',', ':')),
        '__NATIVE_REL__': str(role_stage.NATIVE_REL),
        '__NATIVE_SHA__': role_stage.NATIVE_SHA,
    }
    for marker, replacement in replacements.items():
        require(extension.count(marker) == (8 if marker == '__NATIVE_REL__' else 1),
                'Mapper bridge template pin locus differs')
        extension = extension.replace(marker, replacement)
    text += extension
    compile(text, '<disposable-mapper-readonly-bridge>', 'exec', optimize=0)
    compile(text, '<disposable-mapper-readonly-bridge>', 'exec', optimize=2)
    return text.encode()


def render_runner(mapper_raw: bytes, selected_count: int) -> bytes:
    require(type(mapper_raw) is bytes and type(selected_count) is int and
            1700 < selected_count < 1800, 'closed Mapper read-only runner selection required')
    text = MAPPER_RUNNER
    for marker, value in (('__MAPPER_SHA__', source._sha(mapper_raw)),
                          ('__MAPPER_INPUT_COUNT__', str(selected_count))):
        require(text.count(marker) == 1, 'Mapper runner pin locus differs')
        text = text.replace(marker, value)
    compile(text, '<disposable-mapper-readonly-runner>', 'exec', optimize=0)
    compile(text, '<disposable-mapper-readonly-runner>', 'exec', optimize=2)
    return text.encode()


def _held_family_leaf(family_host: Path, suffix: str, expected_sha: str) -> bytes:
    """Capture a fresh predecessor by a held nofollow parent/leaf, never receipt data."""
    require(type(suffix) is str and suffix in
            (reader.SOURCE_REL, reader.PACKAGE_REL, reader.READER_REL) and
            type(expected_sha) is str and len(expected_sha) == 64,
            'exact Mapper predecessor leaf required')
    path = family_host / suffix
    with HeldCanonicalDirectory(str(path.parent)) as parent:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK |
                     os.O_CLOEXEC, dir_fd=parent.fd)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                    before.st_size <= 2 * 1024 * 1024,
                    'bounded single-link Mapper predecessor required')
            raw = bytearray()
            while len(raw) < before.st_size:
                chunk = os.read(fd, min(1024 * 1024, before.st_size - len(raw)))
                require(bool(chunk), 'Mapper predecessor truncated')
                raw.extend(chunk)
            after = os.fstat(fd)
            attached = os.stat(path.name, dir_fd=parent.fd, follow_symlinks=False)
            key = lambda value: (value.st_dev, value.st_ino, value.st_mode, value.st_uid,
                                 value.st_gid, value.st_nlink, value.st_size,
                                 value.st_mtime_ns, value.st_ctime_ns)
            require(key(before) == key(after) == key(attached) and parent.attached() and
                    source._sha(raw) == expected_sha,
                    'Mapper predecessor changed, aliased, or detached during held read')
            return bytes(raw)
        finally:
            os.close(fd)


def _held_native(path: Path, *, mode: int) -> bytes:
    """Read one exact native leaf with nofollow attachment and mode custody."""
    require(isinstance(path, Path) and type(mode) is int and mode in (0o755, 0o400),
            'exact native custody mode required')
    with HeldCanonicalDirectory(str(path.parent)) as parent:
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK |
                     os.O_CLOEXEC, dir_fd=parent.fd)
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                    stat.S_IMODE(before.st_mode) == mode and
                    before.st_size == 20243600,
                    'selected native type, mode, or size differs')
            raw = bytearray()
            while len(raw) < before.st_size:
                chunk = os.read(fd, min(1024 * 1024, before.st_size-len(raw)))
                require(bool(chunk), 'selected native truncated')
                raw.extend(chunk)
            after = os.fstat(fd)
            attached = os.stat(path.name, dir_fd=parent.fd, follow_symlinks=False)
            key = lambda item: (item.st_dev, item.st_ino, item.st_mode, item.st_uid,
                                item.st_gid, item.st_nlink, item.st_size,
                                item.st_mtime_ns, item.st_ctime_ns)
            require(key(before) == key(after) == key(attached) and parent.attached() and
                    source._sha(raw) == role_stage.NATIVE_SHA,
                    'selected native identity or digest changed')
            return bytes(raw)
        finally:
            os.close(fd)


def _select_native_for_mapper(snapshot: Path) -> bytes:
    """Add exactly one late native input to owned scratch, after Reader closes."""
    raw = _held_native(source.REPO / role_stage.NATIVE_REL, mode=0o755)
    relative = PurePosixPath(role_stage.NATIVE_REL)
    require(not relative.is_absolute() and '..' not in relative.parts and
            not os.path.lexists(snapshot / str(relative)),
            'native was already selected in early sparse snapshot')
    with HeldCanonicalDirectory(str(snapshot)) as held:
        opened: list[int] = []
        current = held.fd
        try:
            for part in relative.parts[:-1]:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=current)
                except FileExistsError:
                    pass
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY |
                                os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current)
                opened.append(child)
                current = child
            fd = os.open(relative.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         os.O_NOFOLLOW | os.O_CLOEXEC, 0o400, dir_fd=current)
            try:
                view = memoryview(raw)
                while view:
                    count = os.write(fd, view)
                    require(count > 0, 'native scratch copy stalled')
                    view = view[count:]
                os.fchmod(fd, 0o400)
                os.fsync(fd)
                before = os.fstat(fd)
                attached = os.stat(relative.name, dir_fd=current,
                                   follow_symlinks=False)
                require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                        stat.S_IMODE(before.st_mode) == 0o400 and
                        (before.st_dev, before.st_ino, before.st_size) ==
                        (attached.st_dev, attached.st_ino, attached.st_size) and
                        before.st_size == len(raw) and held.attached(),
                        'native scratch leaf detached or aliased')
            finally:
                os.close(fd)
            os.fsync(current)
            require(held.attached(), 'native scratch snapshot detached')
        finally:
            for directory_fd in reversed(opened):
                os.close(directory_fd)
    require(_held_native(snapshot / str(relative), mode=0o400) == raw,
            'native scratch copy bytes differ')
    return raw


def validate_result(stdout: bytes, *, mapper_sha: str, selected_count: int) -> dict:
    require(type(stdout) is bytes and len(stdout) <= 4096 and
            len(stdout.splitlines()) == 1, 'one bounded Mapper read-only result required')
    result = _parse_closed(stdout.splitlines()[0])
    require(type(result) is dict and set(result) ==
            {'result', 'mapper_manifest_sha256', 'selected_input_count',
             'sandbox_host_checkout_absent', 'sandbox_protected_roots_absent',
             'mapped_package_absent', 'context_absent', 'authority_effect',
             'actual_owner_outcome'} and
            result['result'] == 'PASS-fixture-mapper-readonly' and
            result['mapper_manifest_sha256'] == mapper_sha and
            result['selected_input_count'] == selected_count and
            result['sandbox_host_checkout_absent'] is True and
            result['sandbox_protected_roots_absent'] is True and
            result['mapped_package_absent'] is True and
            result['context_absent'] is True and
            result['authority_effect'] == 'none' and
            result['actual_owner_outcome'] is None,
            'Mapper result exceeded read-only fixture selection')
    return result


def _held_leader_exited(pid: int) -> bool:
    """Observe our child without reaping it, so its PGID cannot be reused."""
    status = os.waitid(os.P_PID, pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
    return status is not None and status.si_pid == pid


def _live_group_members(pgid: int) -> bool:
    """A held zombie leader remains in the group; count executable members."""
    with os.scandir('/proc') as entries:
        for entry in entries:
            if not entry.name.isdecimal():
                continue
            try:
                # comm may contain spaces and parentheses; fields after its
                # final ')' begin with state, ppid, and process group.
                raw = Path('/proc', entry.name, 'stat').read_text()
            except (FileNotFoundError, ProcessLookupError):
                continue
            fields = raw.rsplit(')', 1)[1].split()
            require(len(fields) >= 3, 'unreadable process-group observation')
            if int(fields[2]) == pgid and fields[0] not in ('Z', 'X', 'x'):
                return True
    return False


def _signal_held_group(pid: int) -> None:
    """Never address a numeric PGID after its child leader is reaped."""
    _held_leader_exited(pid)  # Raises if the child has already been reaped.
    require(os.getpgid(pid) == pid, 'disposable child session identity changed')
    os.killpg(pid, signal.SIGKILL)


def _wait_held_leader(pid: int, *, cap_seconds: float) -> bool:
    deadline = time.monotonic() + cap_seconds
    while not _held_leader_exited(pid):
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.05)
    return True


@contextmanager
def _scratch_custody(state: dict):
    root = Path(tempfile.mkdtemp(prefix='lc-u02-05-mapper-readonly-'))
    try:
        yield str(root)
    finally:
        children = state.get('children', {})
        unknown = any(row.get('launch_attempted') and not
                      (row.get('reaped_observed') and
                       row.get('process_group_absent_observed'))
                      for row in children.values())
        if unknown:
            state['scratch_retained_unknown'] = True
        else:
            shutil.rmtree(root)


def _close_held_group(process: subprocess.Popen, forced: int | None,
                      observed: dict, started: float,
                      child_deadline: float) -> tuple[int, int | None]:
    """Close the group before reaping; on observation failure, kill and refuse."""
    pid = process.pid
    group_started = None
    try:
        if forced is not None:
            observed['forced_group_cleanup'] = True
            _signal_held_group(pid)
        # EOF on both streams does not imply process exit. The original child
        # deadline still governs a leader that deliberately closes its FDs.
        while forced is None:
            remaining = child_deadline - time.monotonic()
            if remaining <= 0:
                forced = 124
                observed['forced_group_cleanup'] = True
                _signal_held_group(pid)
                break
            if _held_leader_exited(pid):
                break
            time.sleep(min(0.05, remaining))
        if not _wait_held_leader(pid, cap_seconds=2.0):
            observed['forced_group_cleanup'] = True
            _signal_held_group(pid)
            require(_wait_held_leader(pid, cap_seconds=2.0),
                    'disposable child leader did not exit under bounded cleanup')
        group_started = time.monotonic()
        if forced is None:
            grace_deadline = min(time.monotonic() + 0.5, child_deadline)
            while _live_group_members(pid) and time.monotonic() < grace_deadline:
                time.sleep(0.05)
        if _live_group_members(pid):
            observed['forced_group_cleanup'] = True
            if forced is None and time.monotonic() >= child_deadline:
                forced = 124
            _signal_held_group(pid)
        drain_deadline = time.monotonic() + 2.0
        while _live_group_members(pid) and time.monotonic() < drain_deadline:
            time.sleep(0.05)
        require(not _live_group_members(pid),
                'disposable child group retained a live member')
    except BaseException:
        # A /proc or signal-handler exception cannot bypass cleanup. Keep the
        # leader unreaped while signalling. A failed signal is retried only
        # while waitid still proves our child identity; never address a PGID
        # after wait() has released that identity.
        observed['forced_group_cleanup'] = True
        try:
            for attempt in range(2):
                try:
                    _signal_held_group(pid)
                except BaseException:
                    # A one-shot alarm, vanished zombie-only group, or failed
                    # signal still leaves this invocation a hard failure.
                    pass
                try:
                    exited = _wait_held_leader(pid, cap_seconds=2.0)
                    if not exited:
                        continue
                    try:
                        live = _live_group_members(pid)
                    except BaseException:
                        live = True
                    if live:
                        continue
                    process.wait(timeout=1)
                    observed['reaped_observed'] = True
                    try:
                        absent, waited = milestone._wait_group_absent(pid)
                        observed['process_group_absent_observed'] = absent
                    except BaseException:
                        pass
                    break
                except BaseException:
                    # Retry only while the child has not been reaped. The
                    # result remains unqualified if closure is uncertain.
                    if observed['reaped_observed']:
                        break
        finally:
            if not observed['reaped_observed']:
                _UNCLOSED_CHILDREN[pid] = process
            observed['elapsed_milliseconds'] = round((time.monotonic()-started)*1000)
            observed['group_wait_milliseconds'] = (None if group_started is None else
                round((time.monotonic()-group_started)*1000))
        raise
    rc = process.wait(timeout=1)
    observed['reaped_observed'] = True
    absent, _ = milestone._wait_group_absent(pid)
    observed.update({'elapsed_milliseconds': round((time.monotonic()-started)*1000),
                     'forced_timeout': forced == 124,
                     'forced_output_limit': forced == 125,
                     'process_group_absent_observed': absent,
                     'group_wait_milliseconds':
                         round((time.monotonic()-group_started)*1000)})
    require(absent, 'disposable child group remained after cleanup')
    _UNCLOSED_CHILDREN.pop(pid, None)
    return rc, forced


def _run_child(argv: list[str], *, timeout: int = 180,
               observation: dict | None = None) -> tuple[int, bytes, bytes, dict]:
    """Bound each disposable child and prove leader/group closure before reuse."""
    require(type(argv) is list and all(type(item) is str for item in argv) and
            type(timeout) is int and 0 < timeout <= 180,
            'bounded disposable child required')
    started = time.monotonic()
    launch_attempted = True
    process = None
    output: dict = {}
    selector = None
    forced = None
    child_deadline = started + timeout
    result = None
    observed = {} if observation is None else observation
    observed.update({'launch_attempted': launch_attempted,
                'leader_started': False,
                'elapsed_milliseconds': None,
                'forced_timeout': False, 'forced_output_limit': False,
                'forced_group_cleanup': False,
                'timeout_cap_seconds': timeout, 'reaped_observed': False,
                'process_group_absent_observed': False,
                'group_wait_milliseconds': None})
    try:
        # The wall watchdog uses SIGALRM. Do not deliver it between Popen
        # return and registration of a child whose identity we must retain.
        previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            process = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, start_new_session=True)
            _UNCLOSED_CHILDREN[process.pid] = process
            observed['leader_started'] = True
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        output = {process.stdout: bytearray(), process.stderr: bytearray()}
        selector = selectors.DefaultSelector()
        for stream in output:
            selector.register(stream, selectors.EVENT_READ)
        while selector.get_map():
            if time.monotonic() >= child_deadline:
                forced = 124
                break
            for event, _ in selector.select(timeout=min(
                    0.5, max(0, child_deadline-time.monotonic()))):
                chunk = os.read(event.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(event.fileobj)
                    continue
                target = output[event.fileobj]
                if len(target) + len(chunk) > 128 * 1024:
                    forced = 125
                    break
                target.extend(chunk)
            if forced is not None:
                break
    finally:
        try:
            if selector is not None:
                selector.close()
        finally:
            if process is not None:
                for attribute in ('stdout', 'stderr'):
                    try:
                        stream = getattr(process, attribute)
                    except Exception:
                        continue
                    if stream is not None:
                        try:
                            stream.close()
                        except Exception:
                            pass
                rc, forced = _close_held_group(
                    process, forced, observed, started, child_deadline)
                result = (forced if forced is not None else rc,
                          bytes(output.get(process.stdout, b'')),
                          bytes(output.get(process.stderr, b'')))
    require(result is not None and observed['reaped_observed'] and
            observed['process_group_absent_observed'],
            'completed child needs closed process observations')
    if observed['forced_group_cleanup'] and result[0] == 0:
        result = (126, result[1], result[2])
    return (*result, observed)


def _mapper_argv(snapshot: Path, family_host: Path, bridge_path: Path) -> list[str]:
    argv = prefix_probe._reader_argv(snapshot, family_host, bridge_path)
    require(argv[-1] == str(SNAPSHOT / '_t35_reader_runner.py'),
            'read-only Mapper child command preimage differs')
    argv[-1] = str(SNAPSHOT / '_t35_mapper_runner.py')
    require('--bind' not in argv and argv.count(str(family_host)) == 1,
            'Mapper sandbox family must be read-only and singular')
    return argv


def _probe_owned(controller: HeldCanonicalDirectory, observation: dict) -> dict:
    """Private owned fixture execution; only run_and_publish acquires its lock."""
    require(type(controller) is HeldCanonicalDirectory and
            controller.path == PurePosixPath(evidence_guard.EVIDENCE) and
            controller.attached() and type(observation) is dict,
            'held exact evidence controller required for Mapper fixture')
    state = observation
    def step(name: str) -> None:
        require(name in STAGES, 'closed Mapper fixture observation stage required')
        state['stage'] = name
    step('preflight')
    require(source.BWRAP.is_file() and source._sha(source.BWRAP.read_bytes()) ==
            source.BWRAP_SHA, 'exact selected bwrap executable differs')
    version = subprocess.check_output([str(source.BWRAP), '--version'],
                                      text=True, timeout=5).strip()
    require(version == 'bubblewrap 0.11.1', 'selected bwrap version differs')
    with milestone._wall_watchdog() as deadline:
        require(controller.attached(), 'controller lock detached before capture')
        with _scratch_custody(state) as scratch:
            root = Path(scratch)
            state['scratch_root'] = root
            step('capture')
            snapshot, output = root / 'snapshot', root / 'output'
            snapshot.mkdir(); output.mkdir()
            rows, captured = source._source_rows()
            source._copy_snapshot(snapshot, rows, captured)
            (snapshot / '_t35_source_runner.py').write_text(source.SANDBOX_RUNNER)
            (snapshot / '_t35_reader_runner.py').write_text(reader.READER_RUNNER)
            layout = role_stage.DisposableLayout(FAMILY, SNAPSHOT,
                                                  'legacy-fixture-source')
            staged = role_stage.stage_rows(layout, lambda name: captured[name])
            family_host = output / 'legacy-fixture-source'
            for row in staged:
                name = PurePosixPath(row['output']['path']).name
                raw = row['bytes']
                if row['role'] == 'source' and name.endswith('.py'):
                    raw = source._unsealed_source(captured[row['input']['path']],
                                                  layout, name)
                row['bytes'] = raw
                row['output'] = source._bind(Path(row['output']['path']), raw)
            episode_raw = prefix_probe._fixture_episode(captured)
            role_raw = (b'{"schema_version":"lab-T35-disposable-native-role/v1",'
                        b'"authority_effect":"none"}\n')
            planned = plan(layout, staged, episode_raw=episode_raw, role_raw=role_raw)
            for row in staged:
                if row['role'] not in ACTIVE_ROLES:
                    continue
                path = family_host / Path(row['output']['path']).relative_to(str(FAMILY))
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(row['bytes'])
            for suffix, raw in (('source/episode-contract.json', episode_raw),
                                ('source/context-native-role.json', role_raw),
                                ('construction-selection.json', planned.plan_leaf_bytes)):
                path = family_host / suffix
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(raw)
            prefix_files, prefix_dirs = prefix_probe._inventory(family_host)
            planned.check_initial_inventory({str(FAMILY / suffix): digest
                                             for suffix, digest in prefix_files.items()})
            require(prefix_dirs == {'source', 'reader'},
                    'future role present in initial Mapper fixture')
            stage_control, source_manifest = prefix_probe._source_selection(planned, rows)
            (snapshot / '_t35_stage_selection.json').write_bytes(stage_control)
            with (family_host / reader.SOURCE_REL).open('xb') as stream:
                stream.write(source_manifest)
            source_bridge = (source.SCRATCH_BRIDGE.replace('__SOURCE_MANIFEST_SHA__',
                             source._sha(source_manifest)).replace('__STAGE_SELECTION_SHA__',
                             source._sha(stage_control))).encode()
            require(b'__SOURCE_MANIFEST_SHA__' not in source_bridge and
                    b'__STAGE_SELECTION_SHA__' not in source_bridge,
                    'Source bridge pin substitution differs')
            with (snapshot / '_t35_external_runtime_capture.py').open('xb') as stream:
                stream.write(source_bridge)
            package_host = family_host / 'source/packages'
            package_host.mkdir()
            pre_files, pre_dirs = prefix_probe._inventory(family_host)
            require(set(pre_files) == set(prefix_files) | {reader.SOURCE_REL} and
                    pre_dirs == {'source', 'reader', 'source/packages'},
                    'Source prefix changed before Mapper fixture predecessor')
            expected_members = source._historical_package_names(
                captured[source.HISTORICAL_SOURCE_PACKAGE['path']])
            require(controller.attached(), 'controller lock detached before Source child')
            source_argv = reader._sandbox_argv(snapshot, family_host,
                '_t35_source_runner.py', package_host=package_host)
            step('source')
            source_observed: dict = {}
            state.setdefault('children', {})['source'] = source_observed
            source_rc, source_stdout, source_stderr, source_observed = _run_child(
                source_argv, timeout=milestone._remaining_child_seconds(deadline),
                observation=source_observed)
            require(source_rc == 0 and not source_stderr,
                    'fresh fixture Source child failed or emitted diagnostics')
            step('source_poststate')
            package_raw, source_post, source_dirs = reader._source_package_verified(
                family_host, pre_files, pre_dirs, expected_members, source_stdout)
            require(len(source_post) == 53 and 'mapped' not in source_dirs and
                    'context' not in source_dirs,
                    'Source child materialized future phase or unexpected leaf')
            package_sha = source._sha(package_raw)
            reader_manifest = reader._reader_manifest(source_manifest, package_raw)
            with (family_host / reader.READER_REL).open('xb') as stream:
                stream.write(reader_manifest)
            reader_pre, reader_dirs = prefix_probe._inventory(family_host)
            require(set(reader_pre) == set(source_post) | {reader.READER_REL} and
                    reader_dirs == source_dirs and len(reader_pre) == 54,
                    'Reader source manifest changed selected Source family')
            reader_bridge = prefix_probe._prefix_bridge(
                source._sha(source_manifest), package_sha,
                source._sha(reader_manifest), source._sha(stage_control))
            reader_bridge_path = snapshot / '_t35_reader_bridge.py'
            with reader_bridge_path.open('xb') as stream:
                stream.write(reader_bridge)
            require(source._sha((snapshot/'_t35_external_runtime_capture.py').read_bytes()) ==
                    source._sha(source_bridge) and controller.attached(),
                    'Source bridge or controller changed before Reader')
            reader_argv = prefix_probe._reader_argv(snapshot, family_host,
                                                    reader_bridge_path)
            step('reader')
            reader_observed: dict = {}
            state.setdefault('children', {})['reader'] = reader_observed
            reader_rc, reader_stdout, reader_stderr, reader_observed = _run_child(
                reader_argv, timeout=milestone._remaining_child_seconds(deadline),
                observation=reader_observed)
            step('reader_poststate')
            reader_post, reader_post_dirs = prefix_probe._inventory(family_host)
            require(reader_rc == 0 and not reader_stderr and
                    reader_post == reader_pre and reader_post_dirs == reader_dirs,
                    'fresh fixture Reader failed or changed family')
            reader_result = reader._reader_output(
                reader_stdout, reader_sha=source._sha(reader_manifest),
                source_sha=source._sha(source_manifest), package_sha=package_sha)
            # No receipt substitutes for these fresh, held predecessor bytes.
            held_source = _held_family_leaf(family_host, reader.SOURCE_REL,
                                            source._sha(source_manifest))
            held_package = _held_family_leaf(family_host, reader.PACKAGE_REL, package_sha)
            held_reader = _held_family_leaf(family_host, reader.READER_REL,
                                            source._sha(reader_manifest))
            require((held_source, held_package, held_reader) ==
                    (source_manifest, package_raw, reader_manifest),
                    'fresh Mapper predecessor held bytes differ from verified cut')
            require(controller.attached(), 'controller lock detached before Mapper materialization')
            step('mapper_materialize')
            require(str(role_stage.NATIVE_REL) not in rows,
                    'late Mapper native entered early Source/Reader selection')
            native_raw = _select_native_for_mapper(snapshot)
            mapped_post, mapped_dirs, mapper_raw, pins = prepare.materialize(
                family_host, planned, rows, held_source, held_package, held_reader,
                native_raw,
                expected_package_members=expected_members,
                pre_files=reader_post, pre_dirs=reader_post_dirs)
            rendered, expected_raw, _ = prepare.project(
                planned, rows, held_source, held_package, held_reader, native_raw,
                expected_package_members=expected_members)
            require(mapper_raw == expected_raw and
                    mapped_post == {**reader_post,
                                    **{'mapped/'+name: source._sha(raw)
                                       for name, raw in rendered.items()},
                                    prepare.MAPPER_MANIFEST: source._sha(mapper_raw)} and
                    mapped_dirs == reader_post_dirs | {'mapped'},
                    'Mapper five-leaf materialization differs from exact projection')
            selected_count = len(_parse_closed(mapper_raw)['files'])
            mapper_bridge = render_bridge(held_source, held_package, held_reader,
                                          mapper_raw, stage_control, rendered)
            mapper_bridge_path = snapshot / '_t35_mapper_bridge.py'
            with mapper_bridge_path.open('xb') as stream:
                stream.write(mapper_bridge)
            runner_raw = render_runner(mapper_raw, selected_count)
            with (snapshot/'_t35_mapper_runner.py').open('xb') as stream:
                stream.write(runner_raw)
            require(controller.attached(), 'controller lock detached before Mapper read')
            mapper_argv = _mapper_argv(snapshot, family_host, mapper_bridge_path)
            step('mapper_readonly')
            mapper_observed: dict = {}
            state.setdefault('children', {})['mapper_readonly'] = mapper_observed
            mapper_rc, mapper_stdout, mapper_stderr, mapper_observed = _run_child(
                mapper_argv, timeout=milestone._remaining_child_seconds(deadline),
                observation=mapper_observed)
            step('mapper_poststate')
            after_files, after_dirs = prefix_probe._inventory(family_host)
            require(mapper_rc == 0 and not mapper_stderr and
                    after_files == mapped_post and after_dirs == mapped_dirs and
                    'mapped/packages' not in after_dirs and 'context' not in after_dirs,
                    'read-only Mapper base verification failed or changed family')
            require(_held_native(snapshot / str(role_stage.NATIVE_REL), mode=0o400) ==
                    native_raw, 'Mapper native snapshot changed during read-only child')
            validate_result(mapper_stdout, mapper_sha=source._sha(mapper_raw),
                            selected_count=selected_count)
            result = {
                'status': 'PASS-disposable-mapper-base-readonly',
                'selected_repository_input_count': len(rows),
                'late_mapper_native_sha256': source._sha(native_raw),
                'late_mapper_native_nonexecutable': True,
                'selected_repository_input_sha256': source._sha((json.dumps(
                    [rows[name] for name in sorted(rows)], sort_keys=True,
                    separators=(',', ':')) + '\n').encode()),
                'source_manifest_sha256': source._sha(held_source),
                'source_package_manifest_sha256': source._sha(held_package),
                'reader_manifest_sha256': source._sha(held_reader),
                'mapper_manifest_sha256': source._sha(mapper_raw),
                'plan_leaf_sha256': source._sha(planned.plan_leaf_bytes),
                'stage_control_sha256': source._sha(stage_control),
                'mapped_role_sha256': {name: source._sha(raw)
                                       for name, raw in sorted(rendered.items())},
                'selected_mapper_input_count': selected_count,
                'source_package_leaf_count': len(source_post)-len(pre_files),
                'reader_selected_record_count': reader_result['selected_record_count'],
                'reader_accounted_subject_count': reader_result['accounted_subject_count'],
                'source_elapsed_milliseconds': source_observed['elapsed_milliseconds'],
                'reader_elapsed_milliseconds': reader_observed['elapsed_milliseconds'],
                'mapper_read_elapsed_milliseconds': mapper_observed['elapsed_milliseconds'],
                'child_process_observations': {
                    'source': source_observed, 'reader': reader_observed,
                    'mapper_readonly': mapper_observed},
                'effect_capture_watchdog_seconds': milestone.PAIR_WALL_SECONDS,
                'source_stdout_sha256': source._sha(source_stdout),
                'source_stdout_bytes': len(source_stdout),
                'reader_stdout_sha256': source._sha(reader_stdout),
                'reader_stdout_bytes': len(reader_stdout),
                'mapper_stdout_sha256': source._sha(mapper_stdout),
                'mapper_stdout_bytes': len(mapper_stdout),
                'child_stderr_bytes': 0,
                'source_reader_prestate_preserved': True,
                'mapped_package_absent': True, 'context_absent': True,
                'bwrap_sha256': source.BWRAP_SHA, 'bwrap_version': version,
                'source_bridge_sha256': source._sha(source_bridge),
                'reader_bridge_sha256': source._sha(reader_bridge),
                'mapper_bridge_sha256': source._sha(mapper_bridge),
                'mapper_runner_sha256': source._sha(runner_raw),
                'activation_allowed': False, 'actual_host_qualification': False,
                'authority_effect': 'none', 'actual_owner_outcome': None,
            }
            step('cleanup')
        require(not root.exists(), 'Mapper disposable scratch remained after cleanup')
        result['scratch_cleaned_after_return'] = True
        require(controller.attached(), 'controller lock detached before result')
        return result


def _safe_children(value: object, *, complete: bool) -> dict:
    require(type(value) is dict and
            set(value) <= {'source', 'reader', 'mapper_readonly'} and
            (not complete or set(value) == {'source', 'reader', 'mapper_readonly'}),
            'closed child observation names required')
    result = {}
    for name, row in value.items():
        if row == {} and not complete:
            result[name] = {'observation': 'UNAVAILABLE_AFTER_LAUNCH_ATTEMPT'}
            continue
        require(type(row) is dict and set(row) ==
                {'launch_attempted', 'leader_started', 'elapsed_milliseconds',
                 'forced_timeout', 'forced_output_limit', 'forced_group_cleanup',
                 'timeout_cap_seconds',
                 'reaped_observed', 'process_group_absent_observed',
                 'group_wait_milliseconds'} and
                all(type(row[key]) is bool for key in
                    ('launch_attempted', 'leader_started', 'forced_timeout',
                     'forced_output_limit', 'forced_group_cleanup', 'reaped_observed',
                     'process_group_absent_observed')) and
                type(row['timeout_cap_seconds']) is int and
                0 < row['timeout_cap_seconds'] <= 180 and
                (row['elapsed_milliseconds'] is None or
                 type(row['elapsed_milliseconds']) is int and
                 0 <= row['elapsed_milliseconds'] <= 900000) and
                (row['group_wait_milliseconds'] is None or
                 type(row['group_wait_milliseconds']) is int and
                 0 <= row['group_wait_milliseconds'] <= 30000),
                'closed child process observation required')
        if complete:
            require(row['leader_started'] and row['reaped_observed'] and
                    row['process_group_absent_observed'] and
                    not row['forced_timeout'] and not row['forced_output_limit'] and
                    not row['forced_group_cleanup'],
                    'PASS requires clean child process closure')
        result[name] = dict(row)
    return result


def _safe_success(value: object) -> dict:
    require(type(value) is dict and set(value) == {
        'status', 'source_manifest_sha256', 'source_package_manifest_sha256',
        'selected_repository_input_count', 'selected_repository_input_sha256',
        'late_mapper_native_sha256', 'late_mapper_native_nonexecutable',
        'reader_manifest_sha256', 'mapper_manifest_sha256', 'plan_leaf_sha256',
        'stage_control_sha256', 'mapped_role_sha256',
        'selected_mapper_input_count', 'source_package_leaf_count',
        'reader_selected_record_count', 'reader_accounted_subject_count',
        'source_elapsed_milliseconds', 'reader_elapsed_milliseconds',
        'mapper_read_elapsed_milliseconds', 'child_process_observations',
        'effect_capture_watchdog_seconds', 'source_stdout_sha256',
        'source_stdout_bytes', 'reader_stdout_sha256', 'reader_stdout_bytes',
        'mapper_stdout_sha256', 'mapper_stdout_bytes', 'child_stderr_bytes',
        'source_reader_prestate_preserved', 'mapped_package_absent',
        'context_absent', 'bwrap_sha256', 'bwrap_version',
        'source_bridge_sha256', 'reader_bridge_sha256',
        'mapper_bridge_sha256', 'mapper_runner_sha256',
        'activation_allowed', 'actual_host_qualification',
        'authority_effect', 'actual_owner_outcome',
        'scratch_cleaned_after_return'},
        'closed Mapper success receipt required')
    require(value['status'] == 'PASS-disposable-mapper-base-readonly' and
            value['source_reader_prestate_preserved'] is True and
            value['mapped_package_absent'] is True and
            value['context_absent'] is True and
            value['scratch_cleaned_after_return'] is True and
            value['activation_allowed'] is False and
            value['actual_host_qualification'] is False and
            value['authority_effect'] == 'none' and
            value['actual_owner_outcome'] is None and
            value['bwrap_version'] == 'bubblewrap 0.11.1' and
            value['bwrap_sha256'] == source.BWRAP_SHA and
            value['effect_capture_watchdog_seconds'] == milestone.PAIR_WALL_SECONDS and
            value['selected_repository_input_count'] == 1703 and
            value['late_mapper_native_sha256'] == role_stage.NATIVE_SHA and
            value['late_mapper_native_nonexecutable'] is True and
            value['source_package_leaf_count'] == 37 and
            value['selected_mapper_input_count'] == 1762 and
            value['child_stderr_bytes'] == 0,
            'Mapper success exceeds fixture ceiling')
    digests = ('selected_repository_input_sha256',
               'late_mapper_native_sha256',
               'source_manifest_sha256', 'source_package_manifest_sha256',
               'reader_manifest_sha256', 'mapper_manifest_sha256',
               'plan_leaf_sha256', 'stage_control_sha256',
               'source_stdout_sha256', 'reader_stdout_sha256',
               'mapper_stdout_sha256', 'bwrap_sha256', 'source_bridge_sha256',
               'reader_bridge_sha256', 'mapper_bridge_sha256',
               'mapper_runner_sha256')
    require(all(type(value[key]) is str and len(value[key]) == 64 and
                all(c in '0123456789abcdef' for c in value[key])
                for key in digests) and
            type(value['mapped_role_sha256']) is dict and
            set(value['mapped_role_sha256']) == prepare.MAPPER_NAMES and
            all(type(digest) is str and len(digest) == 64 and
                all(c in '0123456789abcdef' for c in digest)
                for digest in value['mapped_role_sha256'].values()),
            'Mapper success digest set differs')
    counts = ('reader_selected_record_count', 'reader_accounted_subject_count',
              'source_elapsed_milliseconds', 'reader_elapsed_milliseconds',
              'mapper_read_elapsed_milliseconds', 'source_stdout_bytes',
              'reader_stdout_bytes', 'mapper_stdout_bytes')
    require(all(type(value[key]) is int and 0 <= value[key] <= 900000
                for key in counts) and
            _safe_children(value['child_process_observations'], complete=True) ==
            value['child_process_observations'] and
            all(value[role+'_elapsed_milliseconds'] ==
                value['child_process_observations'][name]['elapsed_milliseconds']
                for role, name in (('source', 'source'), ('reader', 'reader'),
                                   ('mapper_read', 'mapper_readonly'))),
            'Mapper success counts or process closure differ')
    return dict(value)


def run_and_publish() -> dict:
    """One no-replace sanitized result under the same cooperative controller lock."""
    with milestone._exclusive_controller() as held:
        require(held.attached() and
                not os.path.lexists(evidence_guard.EVIDENCE / RECEIPT_NAME),
                'Mapper result name already occupied or evidence root detached')
        observation: dict = {}
        try:
            result = _safe_success(_probe_owned(held, observation))
        except Exception as error:
            root = observation.get('scratch_root')
            result = {
                'status': 'FAIL-disposable-mapper-readonly',
                'failure_code': ('WATCHDOG_EXHAUSTED' if type(error) is TimeoutError else
                                 'CONTRACT_REFUSAL' if isinstance(error, ContractError) else
                                 'UNEXPECTED_EXCEPTION'),
                'failure_stage': observation.get('stage')
                    if observation.get('stage') in STAGES else 'preflight',
                'scratch_cleanup_observed': root is None or not root.exists(),
                'scratch_retained_unknown':
                    observation.get('scratch_retained_unknown') is True,
                'completed_child_process_observations':
                    _safe_children(observation.get('children', {}), complete=False),
                'raw_diagnostics_published': False,
                'activation_allowed': False, 'actual_host_qualification': False,
            }
        # These fixed receipt claims describe the envelope actually observed.
        # A descendant that leaves the session is outside this fixture oracle.
        result['containment_scope'] = 'observed_process_groups_only'
        result['escaped_session_absence_proven'] = False
        require(held.attached(), 'controller lock detached before Mapper result publication')
        raw = (json.dumps(result, sort_keys=True, separators=(',', ':'),
                          allow_nan=False) + '\n').encode()
        binding = evidence_guard.publish_numbered(RECEIPT_NAME, raw)
        return {'receipt_binding': binding, 'status': result['status']}


def main() -> int:
    outcome = run_and_publish()
    print(json.dumps(outcome, sort_keys=True, separators=(',', ':')))
    return 0 if outcome['status'] == 'PASS-disposable-mapper-base-readonly' else 1


if __name__ == '__main__':
    raise SystemExit(main())
