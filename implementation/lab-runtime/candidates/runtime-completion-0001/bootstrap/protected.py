"""Fixed held-locator mechanics for selected startup inputs.

These integrity primitives do not authenticate G02. A separately admitted fixed
host capability must select the roots, members and current permission before use.
No request flag, matching digest, fixture grant or callback grants actual custody.
"""
from contextlib import contextmanager
from dataclasses import dataclass
import array
import hashlib
import fcntl
import json
import os
import secrets
import select
import socket
import stat
import struct
import sys
import time


class Refusal(ValueError):
    """Only fixed bounded codes cross the public adapter boundary."""
    def __init__(self, code, *, cleanup_codes=()):
        super().__init__(code)
        self.cleanup_codes = tuple(c for c in cleanup_codes if type(c) is str and c == 'OWNED_DESCRIPTOR_CLOSE_UNCERTAIN') if type(cleanup_codes) is tuple else ()


def _has_cleanup_note(error):
    fields = BaseException.__dict__['__dict__'].__get__(error, BaseException)
    notes = dict.get(fields, '__notes__') if type(fields) is dict else None
    return type(notes) is list and any(type(n) is str and n == 'STARTUP_CLEANUP_UNCERTAIN' for n in notes)


def _cleanup_note(error):
    # Bypass subclass attribute/equality hooks; never stringify foreign errors.
    fields = BaseException.__dict__['__dict__'].__get__(error, BaseException)
    if type(fields) is dict:
        notes = dict.get(fields, '__notes__')
        safe = [n for n in notes if type(n) is str] if type(notes) is list else []
        dict.__setitem__(fields, '__notes__', safe + ['STARTUP_CLEANUP_UNCERTAIN'])


def cleanup_uncertain(error):
    fields=BaseException.__dict__['__dict__'].__get__(error,BaseException)
    codes=dict.get(fields,'cleanup_codes') if type(error) is Refusal else None
    return _has_cleanup_note(error) or (type(codes) is tuple and any(
        type(c) is str and c=='OWNED_DESCRIPTOR_CLOSE_UNCERTAIN' for c in codes))


def public_boundary(method):
    """Do not render downstream exception text, path, body or exception chain."""
    def invoke(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as error:
            uncertain = cleanup_uncertain(error)
            raise Refusal('STARTUP_REFUSED', cleanup_codes=(
                ('OWNED_DESCRIPTOR_CLOSE_UNCERTAIN',) if uncertain else ())) from None
    invoke.__name__ = method.__name__
    return invoke


def need(condition, code):
    if not condition:
        raise Refusal(code)


def _attempt_closes(resources):
    """Consume each owned handle once; never retry an ambiguous Linux close."""
    failures = []
    for kind, resource in resources:
        try:
            if kind == 'fd': os.close(resource)
            else: resource.close()
        except BaseException as error:
            failures.append(error)
    return failures


def _finish_closes(failures, primary, code):
    if not failures: return
    if primary is not None:
        # Keep the original failure and add only a fixed nonprivate note.
        _cleanup_note(primary)
        return
    interrupted = next((e for e in failures if not isinstance(e, Exception)), None)
    if interrupted is not None:
        _cleanup_note(interrupted)
        raise interrupted
    raise Refusal(code, cleanup_codes=('OWNED_DESCRIPTOR_CLOSE_UNCERTAIN',)) from None


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def closed(value, fields, code='INPUT_FIELDS'):
    need(type(value) is dict and set(value) == set(fields), code)


def parse(raw, maximum=1024 * 1024):
    need(type(raw) is bytes and 0 < len(raw) <= maximum, 'INPUT_BOUND')
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'DUPLICATE_KEY')
            result[key] = value
        return result
    def invalid(_value):
        raise Refusal('NONFINITE_INPUT')
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                       parse_constant=invalid, parse_float=invalid)
    def bounded(v, depth=0):
        need(depth <= 64, 'INPUT_DEPTH')
        if type(v) is str:
            need(not any(0xD800 <= ord(c) <= 0xDFFF for c in v), 'INPUT_UNICODE')
        elif type(v) is int:
            need(-(2**63) <= v <= 2**63 - 1, 'INPUT_INTEGER')
        elif type(v) is dict:
            for k, x in v.items(): bounded(k, depth + 1); bounded(x, depth + 1)
        elif type(v) is list:
            for x in v: bounded(x, depth + 1)
        else: need(v is None or type(v) is bool, 'INPUT_TYPE')
    bounded(value)
    return value


def relative(path):
    need(type(path) is str and 0 < len(path) <= 4096 and not path.startswith('/')
         and '\\' not in path and '\0' not in path, 'LOCATOR_PATH')
    parts = path.split('/')
    need(len(parts) <= 128 and all(p not in ('', '.', '..') for p in parts),
         'LOCATOR_PATH')
    return parts


def binding(value):
    closed(value, ('kind', 'root_id', 'relative_path', 'sha256', 'size_bytes'))
    need(value['kind'] in ('execution', 'evidence', 'protected-input', 'public-package')
         and type(value['root_id']) is str and 0 < len(value['root_id']) <= 4096,
         'INPUT_BINDING')
    relative(value['relative_path'])
    need(type(value['sha256']) is str and len(value['sha256']) == 64
         and all(c in '0123456789abcdef' for c in value['sha256'])
         and type(value['size_bytes']) is int
         and 0 <= value['size_bytes'] <= 2**63 - 1, 'INPUT_BINDING')


def identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid,
            'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)}


def stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def mount_id(fd):
    """Linux held-mount observation, not a writable-alias exclusion proof."""
    with open('/proc/self/fdinfo/' + str(fd), 'rb') as stream:
        raw = stream.read(16385)
    need(len(raw) <= 16384, 'MOUNT_INFO_BOUND')
    rows = [line.split(b':', 1)[1].strip() for line in raw.splitlines() if line.startswith(b'mnt_id:')]
    need(len(rows) == 1 and rows[0].isdigit(), 'MOUNT_INFO')
    return int(rows[0])


def check_identity(value):
    closed(value, ('device', 'inode', 'uid', 'gid', 'mode'))
    need(all(type(n) is int and n >= 0 for n in value.values())
         and value['uid'] < 2**32 - 1 and value['gid'] < 2**32 - 1
         and value['mode'] <= 0o7777, 'LOCATOR_IDENTITY')


class HeldInputs:
    """Exact selected roots and members, with no permission inference.

    Every ancestor is held and compared with its independently selected identity.
    Reads are nonblocking until a regular single-link file is established. No
    selected root or member is created, repaired, chmodded, adopted or removed.
    Caller must check current permission before and after each read.
    """
    @public_boundary
    def __init__(self, roots, members):
        need(type(roots) is list and 0 < len(roots) <= 64
             and type(members) is list and 0 < len(members) <= 65536,
             'LOCATOR_INVENTORY_BOUND')
        self._roots = {}; self._members = {}; self._handles = {}; self._closed = False
        self._close_attempted = False; self._cleanup_uncertain = False
        # Capture original selected values; caller mutation does not repin them.
        roots = parse(canonical(roots)); members = parse(canonical(members), 64 * 1024 * 1024)
        try:
            for row in roots:
                closed(row, ('root_id', 'path', 'ancestors', 'mount_ids'))
                need(type(row['root_id']) is str and row['root_id']
                     and row['root_id'] not in self._roots
                     and type(row['path']) is str and row['path'].startswith('/')
                     and not row['path'].endswith('/'), 'ROOT_SELECTION')
                parts = relative(row['path'][1:])
                need(type(row['ancestors']) is list and len(row['ancestors']) == len(parts) + 1,
                     'ROOT_ANCESTORS')
                need(type(row['mount_ids']) is list and len(row['mount_ids']) == len(row['ancestors'])
                     and all(type(x) is int and x > 0 for x in row['mount_ids']), 'ROOT_MOUNTS')
                for expected in row['ancestors']:
                    check_identity(expected)
                handles = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)]
                self._handles[row['root_id']] = handles
                for name in parts:
                    handles.append(os.open(name, os.O_RDONLY | os.O_DIRECTORY |
                        os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=handles[-1]))
                self._roots[row['root_id']] = row
            for row in members:
                closed(row, ('file_id', 'binding', 'identity', 'mount_id'))
                binding(row['binding']); check_identity(row['identity'])
                need(type(row['mount_id']) is int and row['mount_id'] > 0, 'MEMBER_MOUNT')
                need(type(row['file_id']) is str and row['file_id']
                     and row['file_id'] not in self._members
                     and row['binding']['root_id'] in self._roots, 'MEMBER_SELECTION')
                key = (row['binding']['root_id'], row['binding']['relative_path'])
                need(not any((r['binding']['root_id'], r['binding']['relative_path']) == key
                             for r in self._members.values()), 'MEMBER_ALIAS')
                self._members[row['file_id']] = row
            self.guard()
        except BaseException:
            self.close()
            raise

    @public_boundary
    def guard(self):
        need(not self._closed, 'INPUTS_CLOSED')
        for root_id, row in self._roots.items():
            handles = self._handles[root_id]; parts = relative(row['path'][1:])
            for index, handle in enumerate(handles):
                need(identity(os.fstat(handle)) == row['ancestors'][index]
                     and mount_id(handle) == row['mount_ids'][index], 'ROOT_CHANGED')
                if index:
                    attached = os.stat(parts[index - 1], dir_fd=handles[index - 1], follow_symlinks=False)
                    need(stat.S_ISDIR(attached.st_mode) and identity(attached) == row['ancestors'][index],
                         'ROOT_DETACHED')
                    named = os.open(parts[index - 1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                    dir_fd=handles[index - 1])
                    try: need(mount_id(named) == row['mount_ids'][index], 'ROOT_MOUNT_DETACHED')
                    finally: self._close_temporary(named)

    def selected(self, file_id):
        need(file_id in self._members, 'MEMBER_UNSELECTED')
        return parse(canonical(self._members[file_id]))

    def path(self, file_id):
        row = self.selected(file_id)['binding']
        return self._roots[row['root_id']]['path'] + '/' + row['relative_path']

    def inventory_digest(self, excluded=()):
        return digest(canonical({'roots': list(self._roots.values()),
                                 'members': [v for k, v in self._members.items() if k not in excluded]}))

    @public_boundary
    def read(self, file_id, *, maximum=64 * 1024 * 1024):
        need(type(maximum) is int and 0 < maximum <= 64 * 1024 * 1024, 'READ_BOUND')
        row = self.selected(file_id); selected = row['binding']
        need(selected['size_bytes'] <= maximum, 'READ_BOUND')
        self.guard()
        handles = []; links = []; fd = None
        parent = self._handles[selected['root_id']][-1]
        try:
            parts = relative(selected['relative_path'])
            for name in parts[:-1]:
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=parent)
                handles.append(child); links.append((parent, name, child)); parent = child
                need(os.fstat(child).st_uid == row['identity']['uid']
                     and stat.S_IMODE(os.fstat(child).st_mode) & 0o022 == 0,
                     'MEMBER_ANCESTOR_CUSTODY')
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                         dir_fd=parent)
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
                 and identity(before) == row['identity']
                 and before.st_size == selected['size_bytes'] and mount_id(fd) == row['mount_id'], 'MEMBER_PREIMAGE')
            if selected['kind'] == 'protected-input':
                need(row['identity']['mode'] == 0o600, 'PROTECTED_MODE')
            chunks = []; total = 0
            while True:
                chunk = os.read(fd, min(1024 * 1024, maximum - total + 1))
                if not chunk: break
                total += len(chunk); need(total <= maximum, 'READ_BOUND'); chunks.append(chunk)
            raw = b''.join(chunks)
            attached = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            need(stamp(before) == stamp(os.fstat(fd)) == stamp(attached)
                 and len(raw) == selected['size_bytes'] and digest(raw) == selected['sha256'],
                 'MEMBER_CHANGED')
            named = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=parent)
            try: need(stamp(os.fstat(named)) == stamp(before) and mount_id(named) == row['mount_id'], 'MEMBER_MOUNT_DETACHED')
            finally: self._close_temporary(named)
            for ancestor, name, child in links:
                current = os.stat(name, dir_fd=ancestor, follow_symlinks=False)
                need(stat.S_ISDIR(current.st_mode) and identity(current) == identity(os.fstat(child)),
                     'MEMBER_ANCESTOR_DETACHED')
                named = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=ancestor)
                try: need(mount_id(named) == mount_id(child), 'MEMBER_ANCESTOR_MOUNT')
                finally: self._close_temporary(named)
            self.guard()
            return raw
        finally:
            primary = sys.exception()
            failures = _attempt_closes(([('fd', fd)] if fd is not None else []) +
                                       [('fd', handle) for handle in reversed(handles)])
            if failures:
                self._cleanup_uncertain = True; self._closed = True
            _finish_closes(failures, primary, 'INPUT_READ_CLOSE_FAILED')

    def _close_temporary(self, fd):
        primary = sys.exception()
        failures = _attempt_closes([('fd', fd)])
        if failures:
            self._cleanup_uncertain = True; self._closed = True
        _finish_closes(failures, primary, 'INPUT_TEMPORARY_CLOSE_FAILED')

    def close(self):
        if self._close_attempted:
            if self._cleanup_uncertain:
                _finish_closes([None], sys.exception(), 'INPUT_CLOSE_UNCERTAIN')
            return
        self._close_attempted = True
        self._closed = True
        handles = self._handles; self._handles = {}
        failures = _attempt_closes([('fd', handle) for group in handles.values()
                                    for handle in reversed(group)])
        self._cleanup_uncertain |= bool(failures)
        _finish_closes(failures or ([None] if self._cleanup_uncertain else []),
                       sys.exception(), 'INPUT_CLOSE_FAILED')

    def teardown_status(self):
        return {'closed': self._closed, 'cleanup': 'unknown' if self._cleanup_uncertain else
                ('clean' if self._close_attempted else 'not-attempted')}


@dataclass(frozen=True)
class StartupOutcome:
    posture: str
    completed_stages: tuple
    primary_code: str | None
    cleanup_codes: tuple
    effect_state: str
    actual_startup_qualified: bool = False
    secondary_codes: tuple = ()
    role: str | None = None

    def public(self):
        return {'schema_version': 'lab-protected-startup-outcome/v2', 'role': self.role,
                'construction_coverage_only': True, 'simultaneously_live_contexts': False,
                'posture': self.posture, 'completed_stages': list(self.completed_stages),
                'primary_code': self.primary_code, 'cleanup_codes': list(self.cleanup_codes),
                'effect_state': self.effect_state,
                'secondary_codes': list(self.secondary_codes),
                'actual_startup_qualified': self.actual_startup_qualified}


def _adopt_seqpacket(inherited_fd, peer, timeout):
    """Transport ownership only; this function creates no custody capability."""
    fd = None; channel = None
    try:
        fd = os.dup(inherited_fd); os.set_inheritable(fd, False)
        channel = socket.socket(fileno=fd); fd = None
        need(channel.family == socket.AF_UNIX
             and channel.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE) == socket.SOCK_SEQPACKET,
             'HOST_TRANSPORT')
        need(struct.unpack('3i', channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)) == peer,
             'HOST_PEER')
        channel.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        channel.settimeout(timeout)
        return channel
    except BaseException as primary:
        failures = _attempt_closes(([('socket', channel)] if channel is not None else []) +
                                   ([('fd', fd)] if fd is not None else []))
        _finish_closes(failures, primary, 'HOST_TRANSPORT_CLOSE_FAILED')
        raise


def process_start_ticks(pid):
    need(type(pid) is int and pid > 0, 'HOST_PID')
    with open('/proc/' + str(pid) + '/stat', 'rb') as stream: raw = stream.read(65537)
    need(len(raw) <= 65536 and b') ' in raw, 'HOST_PROCESS_STAT')
    fields = raw.rsplit(b') ', 1)[1].split()
    need(len(fields) >= 20 and fields[19].isdigit(), 'HOST_PROCESS_STAT')
    return int(fields[19])


def loader_attestation(value, peer, executable, scope, channel_identity, client):
    """Validate selected host evidence joins, never establish its OS assertions.

    G01's independently custodied loader must establish the running image,
    namespace/alias exclusion and no-exec lifetime. An endpoint's response or
    this parser cannot issue that evidence. The enclosing exact enrollment is
    selected before the worker runs; no candidate-derived replacement is valid.
    """
    closed(value, ('schema_version', 'peer', 'executable', 'scope_sha256',
                   'inventory_sha256', 'custody_basis', 'client', 'channel',
                   'exec_excluded', 'writable_aliases_excluded',
                   'not_before_unix', 'expires_unix'))
    need(value['schema_version'] == 'lab-startup-loader-attestation/v1'
         and value['peer'] == peer and value['executable'] == executable
         and value['scope_sha256'] == digest(canonical(scope))
         and value['inventory_sha256'] == scope['inventory_sha256']
         and value['client'] == client and value['channel'] == channel_identity
         and value['exec_excluded'] is True and value['writable_aliases_excluded'] is True,
         'HOST_LOADER_ATTESTATION')
    binding(value['custody_basis'])
    need(value['custody_basis']['sha256'] == scope['root_control_sha256'], 'HOST_CUSTODY_BASIS')
    now = time.time()
    need(type(value['not_before_unix']) is int and type(value['expires_unix']) is int
         and value['not_before_unix'] <= now < value['expires_unix'], 'HOST_ATTESTATION_PERIOD')


class HostCustody:
    """Client for a separately installed, enrolled host; never a worker grant.

    Admission parameters come from the fixed trusted installed loader's external
    selection, not a public request. The host has a distinct UID and custodies
    enrollment and current control. This is a process/OS custody boundary: Python
    class privacy is not isolation. The host endpoint is owned by G01 integration
    and consumes authentic G02 inputs. This client does not implement that host.

    A duplicated connected fd is owned here; the caller's fd is never closed.
    All messages carry fresh nonces and exact immutable scope; every response
    must contain one kernel SCM_CREDENTIALS and no rights/other ancillary data.
    Every delivered FD is closed even on malformed/truncated messages. The
    channel is single-threaded and cannot be shared across a fork.
    """
    posture = 'actual'

    @classmethod
    @public_boundary
    def from_fixed_host_loader(cls, inputs, enrollment_id, expected_enrollment,
                               control_id, expected_scope, inherited_fd):
        need(type(inputs) is HeldInputs, 'HOST_INPUTS')
        binding(expected_enrollment)
        need(inputs.selected(enrollment_id)['binding'] == expected_enrollment,
             'HOST_ENROLLMENT_SELECTION')
        value = parse(inputs.read(enrollment_id))
        closed(value, ('schema_version', 'peer', 'scope', 'control_binding',
                       'max_response_bytes', 'timeout_ms', 'loader_attestation'))
        need(value['schema_version'] == 'lab-startup-host-enrollment/v1'
             and value['scope'] == expected_scope, 'HOST_ENROLLMENT')
        closed(expected_scope, ('selection_sha256', 'inventory_sha256', 'principal_ref',
                               'family', 'role', 'operation', 'source_cut_sha256', 'root_control_sha256',
                               'attempt_id', 'not_before_unix', 'expires_unix'))
        for key in ('selection_sha256', 'inventory_sha256', 'source_cut_sha256', 'root_control_sha256'):
            need(type(expected_scope[key]) is str and len(expected_scope[key]) == 64
                 and set(expected_scope[key]) <= set('0123456789abcdef'), 'HOST_SCOPE_DIGEST')
        need(type(expected_scope['principal_ref']) is str and 0 < len(expected_scope['principal_ref']) <= 4096
             and type(expected_scope['attempt_id']) is str and 0 < len(expected_scope['attempt_id']) <= 128,
             'HOST_SCOPE_IDENTITY')
        need(expected_scope['family'] in ('optimized-0005', 'legacy-source8-20261018-b')
             and expected_scope['role'] in ('participation', 'installation-metadata')
             and (expected_scope['role'] != 'installation-metadata' or expected_scope['family'] == 'legacy-source8-20261018-b')
             and expected_scope['operation'] in ('installation.execute', 'release.prepare')
             and expected_scope['inventory_sha256'] == inputs.inventory_digest((enrollment_id, control_id)),
             'HOST_SCOPE')
        closed(value['peer'], ('pid', 'uid', 'gid', 'start_ticks', 'executable_file_id'))
        peer = value['peer']
        need(type(peer['pid']) is int and peer['pid'] > 0
             and all(type(peer[k]) is int and 0 <= peer[k] < 2**32 - 1 for k in ('uid', 'gid'))
             and peer['uid'] != os.geteuid(), 'HOST_DISTINCT_CUSTODY')
        need(type(peer['start_ticks']) is int and peer['start_ticks'] > 0
             and process_start_ticks(peer['pid']) == peer['start_ticks'], 'HOST_PROCESS_LIFETIME')
        executable = inputs.selected(peer['executable_file_id'])
        need(executable['identity']['uid'] != os.geteuid()
             and executable['identity']['mode'] & 0o222 == 0
             and executable['identity']['mode'] & 0o111 != 0, 'HOST_EXECUTABLE_CUSTODY')
        inputs.read(peer['executable_file_id'])
        # The selected record binds this specific inherited channel and worker,
        # not a pathname, same-UID peer or freely replayable executable hash.
        channel_stat = os.fstat(inherited_fd)
        channel_identity = {'device': channel_stat.st_dev, 'inode': channel_stat.st_ino}
        client = {'pid': os.getpid(), 'start_ticks': process_start_ticks(os.getpid())}
        loader_attestation(value['loader_attestation'], peer, executable, expected_scope,
                           channel_identity, client)
        basis = value['loader_attestation']['custody_basis']
        basis_ids = [name for name, row in inputs._members.items() if row['binding'] == basis]
        need(len(basis_ids) == 1, 'HOST_CUSTODY_BASIS_SELECTION')
        inputs.read(basis_ids[0])
        need(value['control_binding'] == inputs.selected(control_id)['binding'], 'HOST_CONTROL')
        # Enrollment/control are selected external host-owned inputs, never
        # writable worker fixtures. Their ancestors must exclude worker writes.
        for name in (enrollment_id, control_id, basis_ids[0]):
            row = inputs.selected(name)
            need(row['identity']['uid'] == peer['uid'] and row['identity']['mode'] & 0o222 == 0,
                 'HOST_CONTROL_CUSTODY')
            root = inputs._roots[row['binding']['root_id']]
            need(all(i['uid'] != os.geteuid() and i['mode'] & 0o022 == 0
                     for i in root['ancestors']), 'HOST_ROOT_CUSTODY')
        need(type(value['max_response_bytes']) is int and 1 <= value['max_response_bytes'] <= 65536
             and type(value['timeout_ms']) is int and 1 <= value['timeout_ms'] <= 5000,
             'HOST_BOUNDS')
        obj = object.__new__(cls)
        obj._socket = None; obj._pidfd = None; obj._closed = False
        obj._close_attempted = False; obj._cleanup_uncertain = False
        obj.inputs = inputs; obj._enrollment_id = enrollment_id; obj._control_id = control_id
        obj._enrollment_raw = canonical(value); obj._scope = parse(canonical(expected_scope))
        obj._creator_pid = os.getpid(); obj._peer = (peer['pid'], peer['uid'], peer['gid'])
        obj._start_ticks = peer['start_ticks']; obj._executable_id = peer['executable_file_id']
        obj._attestation = value['loader_attestation']; obj._peer_selection = peer
        obj._channel_identity = channel_identity; obj._client = client; obj._basis_id = basis_ids[0]
        obj._max = value['max_response_bytes']; obj._timeout = value['timeout_ms'] / 1000; obj._next_query = 0
        try:
            obj._pidfd = os.pidfd_open(peer['pid'], 0)
            obj._socket = _adopt_seqpacket(inherited_fd, obj._peer, obj._timeout)
            obj.check('admission')
            return obj
        except BaseException:
            obj.close(); raise

    def _current(self, cleanup=False):
        need(not self._closed and os.getpid() == self._creator_pid, 'HOST_LIFETIME')
        need(not select.select([self._pidfd], [], [], 0)[0]
             and process_start_ticks(self._peer[0]) == self._start_ticks, 'HOST_PROCESS_LIFETIME')
        self.inputs.read(self._executable_id)
        channel_stat = os.fstat(self._socket.fileno())
        need({'device': channel_stat.st_dev, 'inode': channel_stat.st_ino} == self._channel_identity,
             'HOST_CHANNEL_CHANGED')
        loader_attestation(self._attestation, self._peer_selection,
                           self.inputs.selected(self._executable_id), self._scope,
                           self._channel_identity, self._client)
        self.inputs.read(self._basis_id)
        need(canonical(parse(self.inputs.read(self._enrollment_id))) == self._enrollment_raw,
             'HOST_ENROLLMENT_CHANGED')
        control = parse(self.inputs.read(self._control_id))
        closed(control, ('schema_version', 'scope', 'revoked', 'cleanup'))
        need(control['schema_version'] == 'lab-startup-host-control/v1'
             and control['scope'] == self._scope and type(control['revoked']) is bool, 'HOST_CURRENT_CONTROL')
        now = time.time()
        if cleanup:
            selected = control['cleanup']
            closed(selected, ('scope_sha256', 'permitted', 'not_before_unix', 'expires_unix'))
            need(selected['scope_sha256'] == digest(canonical(self._scope))
                 and selected['permitted'] is True, 'HOST_CLEANUP_SCOPE')
        else:
            need(control['revoked'] is False, 'HOST_REVOKED')
            selected = self._scope
        need(type(selected['not_before_unix']) is int and type(selected['expires_unix']) is int
             and selected['not_before_unix'] <= now < selected['expires_unix'], 'HOST_PERIOD')

    def _exchange(self, action, stage, challenge=None):
        cleanup = action == 'cleanup'
        self._current(cleanup)
        ordinal = getattr(self, '_next_query', 0)
        need(type(ordinal) is int and 0 <= ordinal < 2**64, 'HOST_QUERY_BOUND')
        self._next_query = ordinal + 1 # No same-channel retry after an ambiguous send.
        request = {'schema_version': 'lab-startup-host-request/v1', 'nonce': ('%016x' % ordinal) + secrets.token_hex(24),
                   'scope': self._scope, 'action': action, 'stage': stage, 'challenge': challenge}
        raw = canonical(request); need(len(raw) <= 65536, 'HOST_REQUEST_BOUND')
        need(self._socket.send(raw) == len(raw), 'HOST_SEND')
        body, ancillary, flags, _ = self._socket.recvmsg(self._max, socket.CMSG_SPACE(12) + socket.CMSG_SPACE(4 * 253), socket.MSG_CMSG_CLOEXEC)
        peers = []; extra = False; close_failures = []
        # Close SCM_RIGHTS before inspecting body/flags or raising any refusal.
        for level, kind, data in ancillary:
            if level == socket.SOL_SOCKET and kind == socket.SCM_RIGHTS:
                fds = array.array('i'); fds.frombytes(data[:len(data) - len(data) % fds.itemsize])
                close_failures.extend(_attempt_closes([('fd',fd) for fd in fds]))
                extra = True
            elif level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS and len(data) == 12:
                peers.append(struct.unpack('3i', data))
            else: extra = True
        if close_failures:self._cleanup_uncertain=True
        _finish_closes(close_failures,None,'HOST_RIGHTS_CLOSE_FAILED')
        need(not flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC) and not extra
             and peers == [self._peer], 'HOST_RESPONSE_CREDENTIALS')
        response = parse(body, self._max)
        closed(response, ('schema_version', 'request_sha256', 'nonce', 'scope',
                          'permitted', 'reader_proof'))
        need(canonical(response) == body
             and response['schema_version'] == 'lab-startup-host-response/v1'
             and response['request_sha256'] == digest(raw) and response['nonce'] == request['nonce']
             and response['scope'] == self._scope and response['permitted'] is True,
             'HOST_RESPONSE_SCOPE')
        self._current(cleanup)
        if action in ('current', 'cleanup'):
            need(response['reader_proof'] is None, 'HOST_UNEXPECTED_PROOF')
        else:
            need(type(response['reader_proof']) is dict, 'HOST_READER_PROOF')
        return response['reader_proof']

    @public_boundary
    def check(self, stage):
        need(stage in STAGES, 'HOST_STAGE')
        self._exchange('cleanup' if stage == 'cleanup' else 'current', stage)

    @public_boundary
    def reader_proof(self, challenge):
        # Original ReaderChannel verifies signature/nonce; this transport is
        # allowed only to request the already selected principal's exact proof.
        return self._exchange('reader-proof', 'reader-authentication', challenge)

    @public_boundary
    def read(self, file_id, *, maximum=64 * 1024 * 1024):
        self.check('private-read')
        try: return self.inputs.read(file_id, maximum=maximum)
        finally: self.check('private-read')

    def close(self):
        if self._close_attempted:
            if self._cleanup_uncertain:
                _finish_closes([None], sys.exception(), 'HOST_CLOSE_UNCERTAIN')
            return
        self._close_attempted = True
        self._closed = True
        channel, pidfd = self._socket, self._pidfd
        self._socket = None; self._pidfd = None
        failures = _attempt_closes(([('socket', channel)] if channel is not None else []) +
                                   ([('fd', pidfd)] if pidfd is not None else []))
        self._cleanup_uncertain |= bool(failures)
        _finish_closes(failures, sys.exception(), 'HOST_CLOSE_FAILED')

    def teardown_status(self):
        return {'closed': self._closed, 'cleanup': 'unknown' if self._cleanup_uncertain else
                ('clean' if self._close_attempted else 'not-attempted')}


STAGES = ('admission', 'closure', 'private-read', 'module-import', 'protected-reader',
          'schemas', 'source', 'mapper', 'reader-channel', 'reader-authentication',
          'context-sessions', 'context-query', 'composite-environment', 'completion-bridge',
          'installation-release', 'final-currentness', 'cleanup')


# Fixed host-side mechanics. These execute only inside the separately enrolled
# host process. The worker cannot select keys, journal roots, policy or scope.
_CRYPTO_SEAL = None


def _crypto(inputs, selection, runtime):
    global _CRYPTO_SEAL
    closed(selection, ('root_id', 'relative_directory', 'file_ids'))
    root = inputs._roots[selection['root_id']]
    parts = relative(selection['relative_directory'])
    directory = root['path'] + '/' + '/'.join(parts)
    ids = selection['file_ids']
    need(type(ids) is list and 1 <= len(ids) <= 4096 and len(set(ids)) == len(ids), 'CRYPTO_INVENTORY')
    paths = {}
    for name in ids:
        row = inputs.selected(name)
        path = inputs.path(name)
        need(row['binding']['root_id'] == selection['root_id']
             and path.startswith(directory + '/cryptography/')
             and row['binding']['kind'] == 'execution', 'CRYPTO_ORIGIN')
        inputs.read(name); paths[path] = name
    # The complete selected package is finite and checked before native import.
    actual = set(); entries = 0; pending = [(directory + '/cryptography', 0)]
    while pending:
        parent, depth = pending.pop(); need(depth <= 32, 'CRYPTO_DEPTH')
        with os.scandir(parent) as scan:
            for entry in scan:
                entries += 1; need(entries <= 8192, 'CRYPTO_SCAN_BOUND')
                need(not entry.is_symlink(), 'CRYPTO_ALIAS')
                if entry.is_dir(follow_symlinks=False): pending.append((entry.path, depth+1))
                else: actual.add(entry.path)
    need(actual == set(paths), 'CRYPTO_COMPLETE_INVENTORY')
    selected_digest = digest(canonical([inputs.selected(name) for name in ids]))
    if _CRYPTO_SEAL is None:
        need(not any(n == 'cryptography' or n.startswith('cryptography.') or n == '_cffi_backend' for n in sys.modules),
             'CRYPTO_PRELOADED')
        previous = list(sys.path)
        try:
            sys.path.insert(0, directory)
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat
        finally: sys.path[:] = previous
        modules = {n: m for n, m in sys.modules.items() if n == 'cryptography' or n.startswith('cryptography.') or n == '_cffi_backend'}
        native_paths={inputs.path(n) for n in runtime['native_file_ids']}
        for module in modules.values():
            need(type(module) is type(sys) and module.__file__ in set(paths)|native_paths, 'CRYPTO_LOADED_ORIGIN')
        _CRYPTO_SEAL = (selected_digest, modules, Ed25519PrivateKey, Encoding, PublicFormat)
    selected, modules, key_type, encoding, public_format = _CRYPTO_SEAL
    need(selected == selected_digest and all(sys.modules.get(n) is m for n, m in modules.items()),
         'CRYPTO_SELECTION_CHANGED')
    need(modules['cryptography.hazmat.primitives.asymmetric.ed25519'].Ed25519PrivateKey is key_type,
         'CRYPTO_CLASS_CHANGED')
    for name in ids: inputs.read(name)
    return key_type, encoding, public_format


def _policy_instant(text):
    from datetime import datetime, timezone
    need(type(text) is str and len(text) <= 64, 'POLICY_PERIOD')
    value = datetime.fromisoformat(text.replace('Z', '+00:00'))
    need(value.tzinfo is not None, 'POLICY_PERIOD')
    return value.astimezone(timezone.utc).timestamp()


def reader_role_policy(policy, role, family, operation):
    """Mechanical role separation. Original ReaderChannel still validates its full schema."""
    need(role in ('participation', 'installation-metadata'), 'READER_ROLE')
    if role == 'participation':
        need(policy['schema_version'] == 'lab-local-candidate-policy/v4-candidate'
             and policy.get('session_control') is not None
             and 'installation_release_control' not in policy
             and operation not in policy['allowed_operations'], 'PARTICIPATION_POLICY')
    else:
        need(family == 'legacy-source8-20261018-b'
             and policy['schema_version'] == 'lab-local-current-legacy-installation-release-policy/v1-candidate'
             and policy.get('session_control') is None
             and policy.get('installation_release_control') is not None
             and policy.get('current_legacy_installation_control') is not None
             and operation in policy['allowed_operations'], 'METADATA_POLICY')


def startup_query_budget(selected):
    """Finite per-role allowance, including four Composition guards and own run.

    Role has K=9 participation or K=12 metadata stages, fourteen module()
    retrieval guards and one final guard: G=2*K+15. Each full guard costs
    2+2*C; modules.enter adds 2+2*C; imports add at most 2*M. Five complete
    preflights (four Composition barriers plus run) each use at most
    2+2*(15+D+R+P+N) checks, including all actual private/control reads.
    Stages cost 2*K; final/proof/cleanup/admission <=6; constructor reads <=5
    cost10. Four Composition barriers add policy read+fresh check =12.
    Each preflight additionally validates all module bytes: five*(2+2*C).
    Total 200+2*G+2*K+(12+2*G)*C+2*M+10*(D+R+P+N).
    The allowance is consumed once at endpoint admission, never pooled across
    roles or renewed. Failure paths execute no more guards than this schedule.
    """
    closure=selected['modules']['closure_file_ids'];modules=selected['modules']['modules']
    cold=selected['cold'];runtime=selected['runtime']
    need(selected['role'] in ('participation','installation-metadata'),'SERVER_ROLE')
    stages=9 if selected['role']=='participation' else 12
    guards=2*stages+15
    sizes={'closure':len(closure),'modules':len(modules),'documents':len(cold['documents']),
           'runtime_rows':len(cold['runtime_origins']),
           'preloaded':0 if runtime is None else len(runtime['preloaded_modules']),
           'mapped':0 if runtime is None else len(runtime['mapped_file_ids'])}
    need(1<=sizes['closure']<=65536 and sizes['modules']<=4096
         and all(0<=n<=65536 for n in sizes.values()),'SERVER_SCHEDULE_BOUND')
    total=200+2*guards+2*stages+(12+2*guards)*sizes['closure']+2*sizes['modules']+10*sum(
        sizes[k]for k in ('documents','runtime_rows','preloaded','mapped'))
    need(total<=8*1024*1024,'SERVER_SCHEDULE_BOUND')
    return {'schema_version':'lab-startup-query-budget/v2','role':selected['role'],
            'maximum_stages':stages,'maximum_full_guards':guards,'maximum_preflights':5,
            'counts':sizes,'total':total}


def journal_inventory(rootfd):
    """Finite exact retained preimage, no-follow, under a separately held root lock."""
    rows=[]; total=0
    def walk(fd,prefix,depth):
        nonlocal total
        need(depth<=4,'JOURNAL_DEPTH')
        with os.scandir(fd) as scan:
            for entry in scan:
                need(len(rows)<2048,'JOURNAL_COUNT')
                info=entry.stat(follow_symlinks=False)
                need(stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode),'JOURNAL_ENTRY_TYPE')
                name=prefix+entry.name;relative(name)
                handle=None
                try:
                    handle=os.open(entry.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=fd)
                    held=os.fstat(handle);need(stamp(held)==stamp(info),'JOURNAL_ENTRY_RACE')
                    value={'path':name,'identity':identity(held),'mount_id':mount_id(handle),
                           'type':'directory'if stat.S_ISDIR(held.st_mode)else'file'}
                    if stat.S_ISREG(held.st_mode):
                        need(held.st_nlink==1 and held.st_size<=2*1024*1024,'JOURNAL_FILE_BOUND')
                        total+=held.st_size;need(total<=128*1024*1024,'JOURNAL_BYTES')
                        chunks=[];remaining=held.st_size+1
                        while remaining:
                            block=os.read(handle,min(65536,remaining))
                            if not block:break
                            chunks.append(block);remaining-=len(block)
                        raw=b''.join(chunks)
                        need(len(raw)==held.st_size and stamp(os.fstat(handle))==stamp(held),'JOURNAL_FILE_DRIFT')
                        value.update(size_bytes=len(raw),sha256=digest(raw))
                    rows.append(value)
                    if value['type']=='directory':walk(handle,name+'/',depth+1)
                finally:
                    _finish_closes(_attempt_closes([('fd',handle)]if handle is not None else []),sys.exception(),'JOURNAL_SCAN_CLOSE')
    walk(rootfd,'',0)
    return sorted(rows,key=lambda r:r['path'])


def _host_runtime(inputs, value, fixture):
    closed(value,('interpreter_file_id','implementation_file_id','cache_prefix_file_id','native_file_ids','python_file_ids','isolated'))
    need(type(value['isolated']) is bool and (fixture or value['isolated'] is True),'SERVER_RUNTIME_POSTURE')
    need(sys.flags.no_site and sys.dont_write_bytecode
         and (not value['isolated'] or sys.flags.isolated), 'SERVER_RUNTIME_FLAGS')
    prefix=inputs.path(value['cache_prefix_file_id'])
    need(sys.pycache_prefix==prefix and (not value['isolated'] or sys._xoptions.get('pycache_prefix')==prefix),
         'SERVER_BYTECODE_POLICY')
    inputs.read(value['cache_prefix_file_id']) # A held selected regular file cannot serve pyc children.
    need(os.path.realpath(sys.executable)==inputs.path(value['interpreter_file_id'])
         and __file__==inputs.path(value['implementation_file_id']),'SERVER_CODE_ORIGIN')
    for key in ('interpreter_file_id','implementation_file_id'):inputs.read(value[key])
    ids=value['native_file_ids'];need(type(ids) is list and 1<=len(ids)<=4096 and len(set(ids))==len(ids),'SERVER_NATIVE_SELECTION')
    allowed={inputs.path(name) for name in ids}
    with open('/proc/self/maps','rb') as stream:raw=stream.read(4*1024*1024+1)
    need(len(raw)<=4*1024*1024,'SERVER_MAP_BOUND')
    observed=set()
    for line in raw.splitlines():
        fields=line.split(None,5)
        if len(fields)==6 and fields[5].startswith(b'/'):
            path=fields[5].decode('utf-8');need(path in allowed,'SERVER_NATIVE_ORIGIN');observed.add(path)
    for name in ids:inputs.read(name)
    python_ids=value['python_file_ids']
    need(type(python_ids) is list and 1<=len(python_ids)<=8192 and len(set(python_ids))==len(python_ids),'SERVER_PYTHON_SELECTION')
    python_paths={inputs.path(n)for n in python_ids}
    for module in tuple(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path is not None:need(path in python_paths|allowed,'SERVER_PYTHON_ORIGIN')
    for name in python_ids:inputs.read(name)
    # This checks exact mapped bytes/origins, not symbol compatibility or loader custody.


class StartupHostEndpoint:
    """One selected attempt, one proof, no reset or recovery-as-new serving.

    from_fixed_host_loader consumes independently retained enrollment and actual
    host custody facts. for_fixture is a visibly separate same-UID inert oracle.
    Python visibility is not isolation. Authentic enrollment, nonrollback root,
    reservation and runtime/native-loader custody are G01/G02 qualifications.
    No fixture endpoint can be admitted by HostCustody's distinct-UID loader.
    """
    @classmethod
    @public_boundary
    def from_fixed_host_loader(cls, inputs, enrollment_id, expected_binding, inherited_fd):
        return cls._open(inputs, enrollment_id, expected_binding, inherited_fd, False)

    @classmethod
    @public_boundary
    def for_fixture(cls, inputs, enrollment_id, expected_binding, inherited_fd):
        return cls._open(inputs, enrollment_id, expected_binding, inherited_fd, True)

    @classmethod
    def _open(cls, inputs, enrollment_id, expected_binding, inherited_fd, fixture):
        need(type(inputs) is HeldInputs, 'SERVER_INPUTS')
        binding(expected_binding)
        need(inputs.selected(enrollment_id)['binding'] == expected_binding, 'SERVER_ENROLLMENT_SELECTION')
        raw = inputs.read(enrollment_id, maximum=1024*1024); value = parse(raw)
        closed(value, ('schema_version', 'fixture_only', 'host_inventory_sha256', 'worker', 'host',
                       'channel', 'scope', 'policy', 'control_file_id', 'key_file_id', 'crypto',
                       'journal', 'runtime', 'worker_selection_file_id', 'max_calls', 'max_record_bytes', 'max_response_bytes', 'total_response_bytes', 'timeout_ms'))
        need(value['schema_version'] == 'lab-startup-host-server-enrollment/v1'
             and value['fixture_only'] is fixture
             and value['host_inventory_sha256'] == inputs.inventory_digest((enrollment_id,)),
             'SERVER_ENROLLMENT')
        host = {'pid': os.getpid(), 'start_ticks': process_start_ticks(os.getpid()),
                'uid': os.geteuid(), 'gid': os.getegid()}
        need(value['host'] == host, 'SERVER_HOST_LIFETIME')
        worker = value['worker']; closed(worker, ('pid', 'start_ticks', 'uid', 'gid'))
        need(type(worker['pid']) is int and worker['pid'] > 0
             and all(type(worker[k]) is int and 0 <= worker[k] < 2**32-1 for k in ('uid','gid'))
             and process_start_ticks(worker['pid']) == worker['start_ticks'], 'SERVER_WORKER_LIFETIME')
        need(fixture or worker['uid'] != os.geteuid(), 'SERVER_DISTINCT_CUSTODY')
        info = os.fstat(inherited_fd)
        need(value['channel'] == {'device': info.st_dev, 'inode': info.st_ino}, 'SERVER_CHANNEL')
        scope = value['scope']
        closed(scope, ('selection_sha256', 'inventory_sha256', 'principal_ref', 'family', 'role', 'operation',
                       'source_cut_sha256', 'root_control_sha256', 'attempt_id', 'not_before_unix', 'expires_unix'))
        need(scope['family'] in ('optimized-0005','legacy-source8-20261018-b')
             and scope['role'] in ('participation','installation-metadata')
             and (scope['role'] != 'installation-metadata' or scope['family'] == 'legacy-source8-20261018-b')
             and scope['operation'] in ('installation.execute','release.prepare')
             and type(scope['attempt_id']) is str and 1 <= len(scope['attempt_id']) <= 128,
             'SERVER_SCOPE')
        policy = value['policy']
        closed(policy, ('file_id', 'binding', 'source_name', 'profile_file_id', 'profile_binding',
                        'source_file_id', 'source_binding', 'source_cut'))
        for field in ('binding','profile_binding','source_binding'): binding(policy[field])
        for file_field, bind_field in (('file_id','binding'),('profile_file_id','profile_binding'),('source_file_id','source_binding')):
            need(inputs.selected(policy[file_field])['binding'] == policy[bind_field], 'SERVER_POLICY_SELECTION')
            inputs.read(policy[file_field])
        need(digest(canonical(policy['source_cut'])) == scope['source_cut_sha256'], 'SERVER_SOURCE_CUT')
        worker_selection=parse(inputs.read(value['worker_selection_file_id'],maximum=64*1024*1024),64*1024*1024)
        need(inputs.selected(value['worker_selection_file_id'])['binding']['sha256']==scope['selection_sha256']
             and worker_selection['schema_version']=='lab-protected-startup-selection/v2'
             and worker_selection['posture']==('fixture'if fixture else'actual')
             and all(worker_selection[k]==scope[k] for k in ('family','role','operation','principal_ref'))
             and worker_selection['source_cut']==policy['source_cut']
             and worker_selection['profile_sha256']==policy['profile_binding']['sha256'],'SERVER_WORKER_SELECTION')
        families={'optimized-0005':('completion-current-participation:optimized-0005','completion-optimized-source8-0005-optimized-0005'),
                  'legacy-source8-20261018-b':('completion-legacy:legacy-source8-20261018-b','completion-legacy-source8-20261018-b')}
        source_name,store=families[scope['family']]
        need(policy['source_name']==source_name and policy['source_cut']['store_ref']==store
             and policy['source_cut']['branch_ref']=='branch:'+store,'SERVER_FAMILY_SOURCE')
        journal = value['journal']; closed(journal, ('root_id', 'capacity'))
        root = inputs._roots[journal['root_id']]; rootfd = inputs._handles[journal['root_id']][-1]
        capacity = journal['capacity']
        closed(capacity, ('root_identity','mount_id','control_binding','scope_sha256','preimage_sha256',
                          'reserved_bytes','reserved_inodes','not_before_unix','expires_unix','nonrollback_basis'))
        need(capacity['root_identity'] == identity(os.fstat(rootfd))
             and capacity['mount_id'] == mount_id(rootfd)
             and capacity['control_binding'] == inputs.selected(value['control_file_id'])['binding']
             and capacity['scope_sha256'] == digest(canonical(scope)), 'SERVER_CAPACITY_SCOPE')
        binding(capacity['nonrollback_basis'])
        basis = [n for n,r in inputs._members.items() if r['binding'] == capacity['nonrollback_basis']]
        need(len(basis) == 1 and capacity['nonrollback_basis']['sha256'] == scope['root_control_sha256'],
             'SERVER_NONROLLBACK_SELECTION')
        inputs.read(basis[0])
        need(type(value['max_calls']) is int and 1 <= value['max_calls'] <= 8*1024*1024
             and type(value['max_record_bytes']) is int and 1024 <= value['max_record_bytes'] <= 65536
             and type(value['timeout_ms']) is int and 1 <= value['timeout_ms'] <= 5000,
             'SERVER_BOUNDS')
        required_bytes = len(raw) + 65536 + value['max_record_bytes']
        need(type(capacity['reserved_bytes']) is int and required_bytes <= capacity['reserved_bytes'] <= 128*1024*1024
             and type(capacity['reserved_inodes']) is int and 3 <= capacity['reserved_inodes'] <= 2048,
             'SERVER_CAPACITY_RESERVE')
        if not fixture: need(value['max_calls'] >= startup_query_budget(worker_selection)['total'], 'SERVER_QUERY_ALLOWANCE')
        now = time.time()
        need(type(capacity['not_before_unix']) is int and type(capacity['expires_unix']) is int
             and capacity['not_before_unix'] <= now < capacity['expires_unix'], 'SERVER_CAPACITY_PERIOD')
        # Actual custody is selected, not inferred from free-space observations.
        if not fixture:
            for rid, r in inputs._roots.items():
                need(all(i['uid'] in (0,os.geteuid()) and i['mode'] & 0o022 == 0 for i in r['ancestors']),
                     'SERVER_ANCESTOR_CUSTODY')
            for name in (enrollment_id,value['key_file_id'],value['control_file_id'],basis[0]):
                selected = inputs.selected(name)
                need(selected['identity']['uid'] == os.geteuid() and selected['identity']['mode'] == 0o600,
                     'SERVER_SECRET_CUSTODY')
        _host_runtime(inputs, value['runtime'], fixture)
        key_type, encoding, public_format = _crypto(inputs, value['crypto'], value['runtime'])
        _host_runtime(inputs, value['runtime'], fixture)
        key_raw = inputs.read(value['key_file_id'], maximum=32)
        need(len(key_raw) == 32 and inputs.selected(value['key_file_id'])['binding']['kind'] == 'protected-input',
             'SERVER_KEY')
        key = key_type.from_private_bytes(key_raw)
        import base64
        policy_value = parse(inputs.read(policy['file_id'], maximum=16384))
        if scope['family']=='optimized-0005':
            source_path=inputs.path(policy['source_file_id']);repository=worker_selection['repository']
            need(type(repository) is str and repository.startswith('/') and source_path.startswith(repository+'/'), 'SERVER_SOURCE_ORIGIN')
            need(policy_value['source8_control']['source_binding']=={'ref':source_path[len(repository)+1:],
                 'sha256':policy['source_binding']['sha256']}, 'SERVER_POLICY_SOURCE_BINDING')
        need(base64.b64decode(policy_value['reader_public_key'], validate=True) ==
             key.public_key().public_bytes(encoding.Raw, public_format.Raw), 'SERVER_KEY_POLICY')
        control=parse(inputs.read(value['control_file_id']))
        closed(control,('schema_version','scope','revoked','cleanup'))
        cleanup=control['cleanup'];closed(cleanup,('scope_sha256','permitted','not_before_unix','expires_unix'))
        need(type(cleanup['expires_unix']) is int and type(cleanup['not_before_unix']) is int
             and capacity['not_before_unix']<=cleanup['not_before_unix']<cleanup['expires_unix']<=capacity['expires_unix']
             and scope['expires_unix']<=capacity['expires_unix'],'SERVER_CLEANUP_CAPACITY_PERIOD')
        challenge={'schema_version':'lab-local-reader-challenge/v1-candidate','host_instance_ref':'host:R03-api:'+'f'*32,
                   'connection_ref':'connection:R03-api:'+'f'*32,'nonce':'f'*64,'policy_sha256':policy['binding']['sha256'],
                   'expires_at':policy_value['expires_at'],'authority_effect':'none'}
        bound_request={'schema_version':'lab-startup-host-request/v1','nonce':'f'*64,'scope':scope,
                       'action':'reader-proof','stage':'reader-authentication','challenge':challenge}
        bound_record={'schema_version':'lab-startup-host-consumption/v1','ordinal':value['max_calls'],
                      'request_sha256':'f'*64,'request':bound_request,'proof_consumed':True}
        bound_response={'schema_version':'lab-startup-host-response/v1','request_sha256':'f'*64,'nonce':'f'*64,
                        'scope':scope,'permitted':True,'reader_proof':{'schema_version':'lab-local-reader-proof/v1-candidate',
                        'challenge':challenge,'signature':'f'*88}}
        need(len(canonical(bound_record))<=value['max_record_bytes'] and len(canonical(bound_request))<=65536
             and type(value['max_response_bytes']) is int and len(canonical(bound_response))<=value['max_response_bytes']<=65536
             and type(value['total_response_bytes']) is int
             and value['max_calls']*value['max_response_bytes']<=value['total_response_bytes']<=2**40,'SERVER_PROSPECTIVE_WIRE_BUDGET')
        obj = object.__new__(cls)
        obj._inputs=inputs; obj._selection=value; obj._enrollment_id=enrollment_id; obj._enrollment_raw=raw
        obj._key=key; obj._policy=policy_value; obj._socket=None; obj._pidfd=None; obj._journal_fd=None; obj._lock_fd=None
        obj._closed=False; obj._close_attempted=False; obj._cleanup_uncertain=False; obj._poisoned=False
        obj._calls=0; obj._bytes=0; obj._response_bytes=0; obj._proof_consumed=False; obj.posture='fixture' if fixture else 'actual'
        try:
            obj._pidfd=os.pidfd_open(worker['pid'],0)
            obj._socket=_adopt_seqpacket(inherited_fd,(worker['pid'],worker['uid'],worker['gid']),value['timeout_ms']/1000)
            obj._current(False)
            obj._lock_fd=os.open('.',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=rootfd)
            need(identity(os.fstat(obj._lock_fd))==identity(os.fstat(rootfd)) and mount_id(obj._lock_fd)==mount_id(rootfd), 'SERVER_LOCK_ROOT')
            fcntl.flock(obj._lock_fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            need(digest(canonical(journal_inventory(rootfd))) == capacity['preimage_sha256'], 'SERVER_JOURNAL_PREIMAGE')
            attempt='attempt-'+digest(scope['attempt_id'].encode('utf-8'))
            os.mkdir(attempt,0o700,dir_fd=rootfd) # Existing even-empty attempts refuse forever.
            obj._journal_fd=os.open(attempt,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=rootfd)
            obj._journal_identity=identity(os.fstat(obj._journal_fd)); obj._journal_mount=mount_id(obj._journal_fd); obj._journal_name=attempt
            need(obj._journal_identity['uid']==os.geteuid() and obj._journal_identity['mode']==0o700,'SERVER_JOURNAL_MODE')
            os.fsync(obj._journal_fd); os.fsync(rootfd)
            obj._persist('admission.json',canonical({'schema_version':'lab-startup-host-admission/v1',
                        'enrollment':value,'enrollment_sha256':digest(raw),'query_allowance_consumed':value['max_calls'],'authority_effect':'none'}), admission=True)
            return obj
        except BaseException:
            obj.close(); raise

    def _current(self, cleanup):
        value=self._selection; worker=value['worker']; scope=value['scope']; now=time.time()
        need(not self._closed and not self._poisoned and value['host']['pid']==os.getpid()
             and process_start_ticks(os.getpid())==value['host']['start_ticks'], 'SERVER_LIFETIME')
        need(not select.select([self._pidfd],[],[],0)[0]
             and process_start_ticks(worker['pid'])==worker['start_ticks'], 'SERVER_WORKER_LIFETIME')
        self._inputs.guard()
        _host_runtime(self._inputs,value['runtime'],self.posture=='fixture')
        need(self._inputs.read(self._enrollment_id, maximum=1024*1024)==self._enrollment_raw, 'SERVER_ENROLLMENT_CHANGED')
        cap=value['journal']['capacity']
        need(cap['not_before_unix']<=now<cap['expires_unix'],'SERVER_CAPACITY_PERIOD')
        control=parse(self._inputs.read(value['control_file_id']))
        closed(control,('schema_version','scope','revoked','cleanup'))
        need(control['schema_version']=='lab-startup-host-control/v1' and control['scope']==scope
             and type(control['revoked']) is bool,'SERVER_CONTROL')
        selected=scope
        if cleanup:
            selected=control['cleanup']; closed(selected,('scope_sha256','permitted','not_before_unix','expires_unix'))
            need(selected['scope_sha256']==digest(canonical(scope)) and selected['permitted'] is True,'SERVER_CLEANUP')
        else: need(control['revoked'] is False,'SERVER_REVOKED')
        need(type(selected['not_before_unix']) is int and type(selected['expires_unix']) is int
             and selected['not_before_unix']<=now<selected['expires_unix'],'SERVER_PERIOD')
        for name in (value['policy']['source_file_id'],value['policy']['profile_file_id'],value['key_file_id'],value['worker_selection_file_id']):
            self._inputs.read(name)
        basis=[n for n,r in self._inputs._members.items() if r['binding']==cap['nonrollback_basis']]
        need(len(basis)==1,'SERVER_BASIS');self._inputs.read(basis[0])
        policy=parse(self._inputs.read(value['policy']['file_id'],maximum=16384))
        need(policy==self._policy and policy['principal_ref']==scope['principal_ref']
             and policy['source_name']==value['policy']['source_name'] and policy['host_uid']==worker['uid']
             and policy['authority_effect']=='none'
             and policy['actual_owner_outcome'] is None,'SERVER_POLICY_SCOPE')
        reader_role_policy(policy, scope['role'], scope['family'], scope['operation'])
        if scope['role']=='installation-metadata':
            need(policy['current_legacy_installation_control']['source_cut']==value['policy']['source_cut'],
                 'SERVER_METADATA_CUT')
        if not cleanup:
            need(policy['revoked'] is False and now<_policy_instant(policy['expires_at']), 'SERVER_POLICY_CURRENT')
        if self._journal_fd is not None:
            rootfd=self._inputs._handles[value['journal']['root_id']][-1]
            handle=None
            try:
                handle=os.open(self._journal_name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=rootfd)
                need(identity(os.fstat(handle))==self._journal_identity and mount_id(handle)==self._journal_mount
                     and identity(os.fstat(self._journal_fd))==self._journal_identity
                     and mount_id(self._journal_fd)==self._journal_mount,'SERVER_JOURNAL_ATTACHMENT')
            finally:
                failures=_attempt_closes([('fd',handle)]if handle is not None else [])
                if failures:self._poisoned=True;self._cleanup_uncertain=True
                _finish_closes(failures,sys.exception(),'SERVER_ATTACHMENT_CLOSE')

    def _persist(self, name, raw, admission=False):
        limit=1024*1024+65536 if admission else self._selection['max_record_bytes']
        need(0<len(raw)<=limit and self._bytes+len(raw)<=self._selection['journal']['capacity']['reserved_bytes'],
             'SERVER_RECORD_BOUND')
        fd=None
        try:
            fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self._journal_fd)
            need(stat.S_ISREG(os.fstat(fd).st_mode) and stat.S_IMODE(os.fstat(fd).st_mode)==0o600,'SERVER_RECORD_MODE')
            view=memoryview(raw)
            while view:
                written=os.write(fd,view);need(written>0,'SERVER_WRITE');view=view[written:]
            os.fsync(fd);os.fsync(self._journal_fd);self._bytes+=len(raw)
        except BaseException:
            self._poisoned=True;raise
        finally:
            failures=_attempt_closes([('fd',fd)] if fd is not None else [])
            if failures:self._poisoned=True;self._cleanup_uncertain=True
            _finish_closes(failures,sys.exception(),'SERVER_RECORD_CLOSE_FAILED')

    @public_boundary
    def serve_once(self):
        try:
            need(not self._closed and not self._poisoned,'SERVER_CLOSED')
            raw,ancillary,flags,_=self._socket.recvmsg(65536,socket.CMSG_SPACE(12)+socket.CMSG_SPACE(4*253),socket.MSG_CMSG_CLOEXEC)
            peers=[];extra=False;failures=[]
            for level,kind,data in ancillary:
                if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
                    fds=array.array('i');fds.frombytes(data[:len(data)-len(data)%fds.itemsize])
                    failures.extend(_attempt_closes([('fd',fd) for fd in fds]));extra=True
                elif level==socket.SOL_SOCKET and kind==socket.SCM_CREDENTIALS and len(data)==12:
                    peers.append(struct.unpack('3i',data))
                else:extra=True
            if failures:self._cleanup_uncertain=True
            _finish_closes(failures,None,'SERVER_RIGHTS_CLOSE_FAILED')
            worker=self._selection['worker']
            need(not flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC) and not extra
                 and peers==[(worker['pid'],worker['uid'],worker['gid'])],'SERVER_CREDENTIALS')
            request=parse(raw,65536)
            closed(request,('schema_version','nonce','scope','action','stage','challenge'))
            action=request['action'];cleanup=action=='cleanup'
            need(canonical(request)==raw and request['schema_version']=='lab-startup-host-request/v1'
                 and request['scope']==self._selection['scope'] and action in ('current','cleanup','reader-proof')
                 and request['stage'] in STAGES and (request['stage']=='cleanup')==cleanup
                 and (action!='reader-proof' or request['stage']=='reader-authentication'), 'SERVER_REQUEST')
            nonce=request['nonce']
            need(type(nonce) is str and len(nonce)==64 and set(nonce)<=set('0123456789abcdef')
                 and int(nonce[:16],16)==self._calls and self._calls<self._selection['max_calls'],'SERVER_CALL_REPLAY')
            self._current(cleanup)
            if action=='reader-proof':
                challenge=request['challenge']
                closed(challenge,('schema_version','host_instance_ref','connection_ref','nonce','policy_sha256','expires_at','authority_effect'))
                need(not self._proof_consumed and challenge['schema_version']=='lab-local-reader-challenge/v1-candidate'
                     and challenge['authority_effect']=='none' and challenge['expires_at']==self._policy['expires_at']
                     and challenge['policy_sha256']==self._selection['policy']['binding']['sha256'], 'SERVER_PROOF_SCOPE')
                for field,prefix in (('host_instance_ref','host:R03-api:'),('connection_ref','connection:R03-api:')):
                    text=challenge[field];need(type(text) is str and text.startswith(prefix)
                         and len(text)==len(prefix)+32 and set(text[len(prefix):])<=set('0123456789abcdef'),'SERVER_CHALLENGE_ID')
                need(type(challenge['nonce']) is str and len(challenge['nonce'])==64
                     and set(challenge['nonce'])<=set('0123456789abcdef'),'SERVER_CHALLENGE_NONCE')
            else:need(request['challenge'] is None,'SERVER_UNEXPECTED_CHALLENGE')
            record=canonical({'schema_version':'lab-startup-host-consumption/v1','ordinal':self._calls,
                              'request_sha256':digest(raw),'request':request,'proof_consumed':action=='reader-proof'})
            # Entire finite query allowance was consumed durably at admission.
            # A restart cannot resume it. Only the one signature slot needs an
            # additional original record; partial record creation also fences it.
            if action=='reader-proof':
                self._persist('proof-consumed.json',record)
                self._proof_consumed=True
            self._calls+=1
            self._current(cleanup)
            proof=None
            if action=='reader-proof':
                import base64
                _crypto(self._inputs,self._selection['crypto'],self._selection['runtime'])
                self._current(False)
                signature=self._key.sign(canonical(request['challenge']))
                proof={'schema_version':'lab-local-reader-proof/v1-candidate','challenge':request['challenge'],
                       'signature':base64.b64encode(signature).decode('ascii')}
            self._current(cleanup)
            response=canonical({'schema_version':'lab-startup-host-response/v1','request_sha256':digest(raw),
                                'nonce':nonce,'scope':request['scope'],'permitted':True,'reader_proof':proof})
            need(len(response)<=self._selection['max_response_bytes'] and self._response_bytes+len(response)<=self._selection['total_response_bytes'],'SERVER_RESPONSE_BOUND')
            self._response_bytes+=len(response)
            need(self._socket.send(response)==len(response),'SERVER_SEND')
            self._current(cleanup)
            return {'result':'served','ordinal':self._calls-1,'proof_consumed':self._proof_consumed}
        except BaseException:
            self._poisoned=True;raise

    def close(self):
        if self._close_attempted:
            if self._cleanup_uncertain:_finish_closes([None],sys.exception(),'SERVER_CLOSE_UNCERTAIN')
            return
        self._closed=True;self._close_attempted=True
        resources=([('socket',self._socket)] if self._socket is not None else [])
        resources += [('fd',fd) for fd in (self._pidfd,self._journal_fd,self._lock_fd) if fd is not None]
        self._socket=None;self._pidfd=None;self._journal_fd=None;self._lock_fd=None;self._key=None
        failures=_attempt_closes(resources);self._cleanup_uncertain |= bool(failures)
        _finish_closes(failures,sys.exception(),'SERVER_CLOSE_FAILED')

    def teardown_status(self):
        return {'closed':self._closed,'cleanup':'unknown' if self._cleanup_uncertain else
                ('clean' if self._close_attempted else 'not-attempted'),
                'attempt_retained':True,'poisoned':self._poisoned,'proof_consumed':self._proof_consumed}
