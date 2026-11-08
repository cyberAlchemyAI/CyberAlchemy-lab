"""Separately provisioned current host permission and one-use transport authentication."""

def _t35_effect_refused():
    raise RuntimeError('Generated T35 role effects require the uninstalled T02 custody gate')

def _t35_binding_path(path):
    from pathlib import Path, PurePosixPath
    value = Path(path)
    name = value.as_posix()
    if not value.is_absolute() or '//' in name or any((x in ('.', '..') for x in name.split('/'))):
        raise ValueError('noncanonical generated binding path')
    family = PurePosixPath(Path(__file__).resolve().parent)
    snapshot = PurePosixPath(Path(__file__).resolve().parent.parents[5])
    item = PurePosixPath(name)
    if family in item.parents:
        return name
    if snapshot in item.parents:
        return str(item.relative_to(snapshot))
    raise ValueError('generated path outside external output and input snapshot')
from pathlib import Path
import sys
from .base import HERE, ROOT, sha, encoded, load, require, binding, original, reader, records, API, MAPPED, API_PROFILE_PIN, preflight, FACT_SCOPE
import json, os, copy, secrets, uuid, base64
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
EL = reader.adapter.eligibility
AUTH = ROOT / 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001' / 'authorization/context-development.json'
AUTH_SHA = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

"""Bounded, attached read of one selected development authorization leaf."""
import hashlib as _auth_hashlib
import os as _auth_os
import stat as _auth_stat
from pathlib import PurePosixPath as _AuthPurePath

AUTH_LIMIT = 16 * 1024


class AuthRefused(ValueError):
    pass


class AuthCleanupRefused(AuthRefused):
    """A read or validation may also have failed; close outcomes are uncertain."""

    def __init__(self, primary_error, cleanup_errors):
        self.primary_error = primary_error
        self.cleanup_errors = tuple(cleanup_errors)
        super().__init__('authorization descriptor cleanup uncertain; no success result')


def _auth_require(ok, reason):
    if not ok:
        raise AuthRefused(reason)


def _auth_identity(item):
    return (item.st_dev, item.st_ino, item.st_mode, item.st_uid,
            item.st_nlink, item.st_size)


def _auth_close(fds):
    failures = []
    for fd in reversed(fds):
        try:
            _auth_os.close(fd)
        except BaseException as error:
            # A failed close has an uncertain outcome. Never retry the number:
            # it may already have been released and reassigned by the OS.
            failures.append((fd, error))
    return failures


def _auth_finish(primary, cleanup):
    if isinstance(primary, AuthCleanupRefused):
        cleanup = list(primary.cleanup_errors) + list(cleanup)
        primary = primary.primary_error
    if cleanup:
        raise AuthCleanupRefused(primary, cleanup) from primary
    if primary is not None:
        raise primary.with_traceback(primary.__traceback__)


def _auth_open_selected(path, root, uid):
    _auth_require(type(uid) is int and uid == _auth_os.geteuid() and
                  uid == _auth_os.getuid(),
                  'selected effective UID or real/effective identity split differs')
    value = _AuthPurePath(str(path))
    base = _AuthPurePath(str(root))
    _auth_require(value.is_absolute() and base.is_absolute() and
                  str(value) == str(path) and str(base) == str(root) and
                  '..' not in value.parts and '..' not in base.parts and
                  value == base / 'authorization/context-development.json',
                  'exact owned development authorization path required')
    root_index = len(base.parts) - 1
    fds = []
    try:
        fd = _auth_os.open('/', _auth_os.O_RDONLY | _auth_os.O_DIRECTORY | _auth_os.O_CLOEXEC)
        fds.append(fd)
        for part in value.parts[1:-1]:
            fd = _auth_os.open(part, _auth_os.O_RDONLY | _auth_os.O_DIRECTORY |
                               _auth_os.O_NOFOLLOW | _auth_os.O_CLOEXEC, dir_fd=fds[-1])
            fds.append(fd)
        _auth_require(len(fds) == len(value.parts) - 1 and root_index < len(fds) - 1,
                      'authorization ancestor topology differs')
        for index in (root_index, root_index + 1):
            info = _auth_os.fstat(fds[index])
            _auth_require(_auth_stat.S_ISDIR(info.st_mode) and info.st_uid == uid and
                          _auth_stat.S_IMODE(info.st_mode) == 0o700,
                          'owned authorization directory mode differs')
        leaf = value.name
        before = _auth_os.stat(leaf, dir_fd=fds[-1], follow_symlinks=False)
        _auth_require(_auth_stat.S_ISREG(before.st_mode) and before.st_uid == uid and
                      _auth_stat.S_IMODE(before.st_mode) == 0o600 and
                      before.st_nlink == 1 and 1 <= before.st_size <= AUTH_LIMIT,
                      'authorization must be owned bounded single-link regular file')
        fd = _auth_os.open(leaf, _auth_os.O_RDONLY | _auth_os.O_NOFOLLOW |
                           _auth_os.O_NONBLOCK | _auth_os.O_CLOEXEC, dir_fd=fds[-1])
        fds.append(fd)
        after = _auth_os.fstat(fd)
        _auth_require(_auth_identity(after) == _auth_identity(before),
                      'authorization leaf changed during open')
        identities = tuple(_auth_identity(_auth_os.fstat(held)) for held in fds)
        return fds, identities
    except BaseException as primary:
        cleanup = _auth_close(fds)
        if cleanup:
            _auth_finish(primary, cleanup)
        raise


def _auth_read_bounded(fd, identity):
    opening_size = identity[-1]
    parts, total = [], 0
    while True:
        chunk = _auth_os.read(fd, min(4096, opening_size + 1 - total))
        if not chunk:
            break
        total += len(chunk)
        _auth_require(total <= opening_size, 'authorization grew during bounded read')
        parts.append(chunk)
    _auth_require(total == opening_size and _auth_identity(_auth_os.fstat(fd)) == identity,
                  'authorization identity or size changed during read')
    return b''.join(parts)


def read_auth_bytes(path, root, pin, uid):
    """Hold ancestor and leaf FDs through bounded read and same-path reopen."""
    _auth_require(type(pin) is str and len(pin) == 64 and
                  all(c in '0123456789abcdef' for c in pin),
                  'exact authorization SHA-256 required')
    held = None
    reopened = None
    primary = None
    result = None
    try:
        held, identities = _auth_open_selected(path, root, uid)
        raw = _auth_read_bounded(held[-1], identities[-1])
        _auth_require(_auth_hashlib.sha256(raw).hexdigest() == pin,
                      'authorization digest differs')
        reopened, current = _auth_open_selected(path, root, uid)
        _auth_require(current == identities, 'authorization path attachment changed')
        again = _auth_read_bounded(reopened[-1], current[-1])
        _auth_require(again == raw and _auth_hashlib.sha256(again).hexdigest() == pin,
                      'authorization attached bytes changed')
        _auth_require(tuple(_auth_identity(_auth_os.fstat(fd)) for fd in held) == identities,
                      'held authorization chain changed')
        _auth_require(type(uid) is int and uid == _auth_os.geteuid() and
                      uid == _auth_os.getuid(),
                      'selected effective UID changed during read')
        result = raw
    except BaseException as error:
        primary = error
    finally:
        cleanup = []
        if reopened is not None:
            cleanup.extend(_auth_close(reopened))
        if held is not None:
            cleanup.extend(_auth_close(held))
    _auth_finish(primary, cleanup)
    # Cleanup may run after the in-try identity observation. This is the last
    # observation before bytes leave the guard; cleanup errors keep precedence.
    _auth_require(type(uid) is int and uid == _auth_os.geteuid() and
                  uid == _auth_os.getuid(),
                  'selected effective UID changed during cleanup')
    return result


def _context_development_auth(scope_ref):
    raw = read_auth_bytes(AUTH, ROOT / 'product/lab/release-candidates/v1/interface/docker-source-20261020-0001', AUTH_SHA, os.geteuid())
    require(sha(raw) == AUTH_SHA, 'development authorization bytes changed')
    value = EL.parse(raw)
    require(type(value) is dict and set(value) == {
        'schema_version', 'family_ref', 'episode_ref', 'scope_ref',
        'period_binding', 'not_before', 'expires_at', 'authority_effect',
        'actual_owner_outcome', 'claim_ceiling'}, 'closed development authorization required')
    period_path = reader.HERE / 'packages/0001/period.json'
    period = load(period_path)
    start, end = EL.instant(value['not_before']), EL.instant(value['expires_at'])
    require(value['schema_version'] == 'lab-context-development-authorization/v1-candidate' and
            value['family_ref'] == str(HERE) and
            value['episode_ref'] == period['period_ref'] and
            value['scope_ref'] == scope_ref and
            value['period_binding'] == binding(period_path) and
            value['authority_effect'] == 'none' and
            value['actual_owner_outcome'] is None and
            value['claim_ceiling'] == 'Local disposable development episode only; no protected Source8 issuer grant or owner outcome.' and
            EL.instant(period['not_before']) <= start <= now() < end <= EL.instant(period['expires_at']) and
            (end - start).total_seconds() <= 1200,
            'development authorization period, scope or posture differs')
    return raw


def now():
    return datetime.now(timezone.utc)

def stamp(v):
    return v.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def wire(value):
    return API.compact(value)

def bind(ref, raw):
    return {'ref': ref, 'sha256': sha(raw)}

def verify_source(pin):
    return preflight(pin)

"""Bounded, attached read of one selected development policy leaf."""
import hashlib as _policy_hashlib
import os as _policy_os
import stat as _policy_stat
from pathlib import PurePosixPath as _PolicyPurePath

POLICY_LIMIT = 16 * 1024


class PolicyRefused(ValueError):
    pass


class PolicyCleanupRefused(PolicyRefused):
    """A read or validation may also have failed; close outcomes are uncertain."""

    def __init__(self, primary_error, cleanup_errors):
        self.primary_error = primary_error
        self.cleanup_errors = tuple(cleanup_errors)
        super().__init__('policy descriptor cleanup uncertain; no success result')


def _policy_require(ok, reason):
    if not ok:
        raise PolicyRefused(reason)


def _policy_identity(item):
    return (item.st_dev, item.st_ino, item.st_mode, item.st_uid, item.st_gid,
            item.st_nlink, item.st_size)


def _policy_directory_identity(item):
    return (item.st_dev, item.st_ino, item.st_mode, item.st_uid, item.st_gid)


def _policy_close(fds):
    failures = []
    for fd in reversed(fds):
        try:
            _policy_os.close(fd)
        except BaseException as error:
            # A failed close has an uncertain outcome. Never retry the number:
            # it may already have been released and reassigned by the OS.
            failures.append((fd, error))
    return failures


def _policy_finish(primary, cleanup):
    if isinstance(primary, PolicyCleanupRefused):
        cleanup = list(primary.cleanup_errors) + list(cleanup)
        primary = primary.primary_error
    if cleanup:
        raise PolicyCleanupRefused(primary, cleanup) from primary
    if primary is not None:
        raise primary.with_traceback(primary.__traceback__)


def _policy_open_source(source_root):
    """Bind the selected Source root as a no-follow held directory chain."""
    source = _PolicyPurePath(str(source_root))
    _policy_require(source.is_absolute() and str(source) == str(source_root) and
                    '..' not in source.parts, 'canonical Source root required')
    fds = []
    try:
        fd = _policy_os.open('/', _policy_os.O_RDONLY | _policy_os.O_DIRECTORY |
                             _policy_os.O_CLOEXEC)
        fds.append(fd)
        for part in source.parts[1:]:
            fd = _policy_os.open(part, _policy_os.O_RDONLY | _policy_os.O_DIRECTORY |
                                 _policy_os.O_NOFOLLOW | _policy_os.O_CLOEXEC,
                                 dir_fd=fds[-1])
            fds.append(fd)
        _policy_require(len(fds) == len(source.parts), 'Source ancestor topology differs')
        identities = tuple(_policy_directory_identity(_policy_os.fstat(fd)) for fd in fds)
        _policy_require(all(_policy_stat.S_ISDIR(item[2]) for item in identities),
                        'selected Source chain is not directories')
        return fds, identities
    except BaseException as primary:
        _policy_finish(primary, _policy_close(fds))


def _policy_open_selected(path, root, source_root, source_identities, uid, gid):
    _policy_require(type(uid) is int and uid == _policy_os.geteuid() and
                  uid == _policy_os.getuid() and
                  type(gid) is int and gid == _policy_os.getegid() and
                  gid == _policy_os.getgid(),
                  'selected effective UID/GID or real/effective identity split differs')
    value = _PolicyPurePath(str(path))
    base = _PolicyPurePath(str(root))
    source = _PolicyPurePath(str(source_root))
    _policy_require(value.is_absolute() and base.is_absolute() and
                  source.is_absolute() and str(source) == str(source_root) and
                  str(value) == str(path) and str(base) == str(root) and
                  '..' not in value.parts and '..' not in base.parts and
                  '..' not in source.parts and
                  value == base / 'permission.json' and
                  _PolicyPurePath('/tmp') in base.parents and
                  source != base and source not in base.parents and
                  base not in source.parents,
                  'exact external private policy path required')
    root_index = len(base.parts) - 1
    fds = []
    try:
        fd = _policy_os.open('/', _policy_os.O_RDONLY | _policy_os.O_DIRECTORY | _policy_os.O_CLOEXEC)
        fds.append(fd)
        for part in value.parts[1:-1]:
            fd = _policy_os.open(part, _policy_os.O_RDONLY | _policy_os.O_DIRECTORY |
                               _policy_os.O_NOFOLLOW | _policy_os.O_CLOEXEC, dir_fd=fds[-1])
            fds.append(fd)
        _policy_require(len(fds) == len(value.parts) - 1 and root_index == len(fds) - 1,
                      'policy ancestor topology differs')
        info = _policy_os.fstat(fds[root_index])
        _policy_require(_policy_stat.S_ISDIR(info.st_mode) and info.st_uid == uid and
                        info.st_gid == gid and _policy_stat.S_IMODE(info.st_mode) == 0o700,
                        'owned policy directory mode differs')
        policy_dir_ids = tuple(_policy_directory_identity(_policy_os.fstat(fd)) for fd in fds)
        source_root_inode = source_identities[-1][:2]
        policy_root_inode = policy_dir_ids[-1][:2]
        _policy_require(source_root_inode not in {item[:2] for item in policy_dir_ids} and
                        policy_root_inode not in {item[:2] for item in source_identities},
                        'Source and private policy roots alias or contain each other')
        leaf = value.name
        before = _policy_os.stat(leaf, dir_fd=fds[-1], follow_symlinks=False)
        _policy_require(_policy_stat.S_ISREG(before.st_mode) and before.st_uid == uid and before.st_gid == gid and
                      _policy_stat.S_IMODE(before.st_mode) == 0o600 and
                      before.st_nlink == 1 and 1 <= before.st_size <= POLICY_LIMIT,
                      'policy must be UID/GID-owned bounded single-link regular file')
        fd = _policy_os.open(leaf, _policy_os.O_RDONLY | _policy_os.O_NOFOLLOW |
                           _policy_os.O_NONBLOCK | _policy_os.O_CLOEXEC, dir_fd=fds[-1])
        fds.append(fd)
        after = _policy_os.fstat(fd)
        _policy_require(_policy_identity(after) == _policy_identity(before),
                      'policy leaf changed during open')
        identities = tuple(_policy_directory_identity(_policy_os.fstat(held))
                           for held in fds[:-1]) + (_policy_identity(_policy_os.fstat(fds[-1])),)
        return fds, identities
    except BaseException as primary:
        cleanup = _policy_close(fds)
        if cleanup:
            _policy_finish(primary, cleanup)
        raise


def _policy_read_bounded(fd, identity):
    opening_size = identity[-1]
    parts, total = [], 0
    while True:
        chunk = _policy_os.read(fd, min(4096, opening_size + 1 - total))
        if not chunk:
            break
        total += len(chunk)
        _policy_require(total <= opening_size, 'policy grew during bounded read')
        parts.append(chunk)
    _policy_require(total == opening_size and _policy_identity(_policy_os.fstat(fd)) == identity,
                  'policy identity or size changed during read')
    return b''.join(parts)


def read_policy_bytes(path, root, source_root, pin, uid, gid):
    """Hold both Source and policy chains through bounded read and reopens."""
    _policy_require(type(pin) is str and len(pin) == 64 and
                  all(c in '0123456789abcdef' for c in pin),
                  'exact policy SHA-256 required')
    _policy_require(type(uid) is int and uid == _policy_os.geteuid() and
                    uid == _policy_os.getuid() and type(gid) is int and
                    gid == _policy_os.getegid() and gid == _policy_os.getgid(),
                    'selected effective UID/GID or real/effective identity split differs')
    source_held = held = source_reopened = reopened = None
    primary = None
    result = None
    try:
        source_held, source_ids = _policy_open_source(source_root)
        held, identities = _policy_open_selected(path, root, source_root, source_ids, uid, gid)
        raw = _policy_read_bounded(held[-1], identities[-1])
        _policy_require(_policy_hashlib.sha256(raw).hexdigest() == pin,
                      'policy digest differs')
        source_reopened, source_current = _policy_open_source(source_root)
        _policy_require(source_current == source_ids, 'Source root attachment changed')
        reopened, current = _policy_open_selected(path, root, source_root, source_current, uid, gid)
        _policy_require(current == identities, 'policy path attachment changed')
        again = _policy_read_bounded(reopened[-1], current[-1])
        _policy_require(again == raw and _policy_hashlib.sha256(again).hexdigest() == pin,
                      'policy attached bytes changed')
        held_now = tuple(_policy_directory_identity(_policy_os.fstat(fd))
                         for fd in held[:-1]) + (_policy_identity(_policy_os.fstat(held[-1])),)
        _policy_require(held_now == identities,
                      'held policy chain changed')
        _policy_require(tuple(_policy_directory_identity(_policy_os.fstat(fd))
                              for fd in source_held) == source_ids,
                        'held Source chain changed')
        _policy_require(type(uid) is int and uid == _policy_os.geteuid() and
                        uid == _policy_os.getuid() and type(gid) is int and
                        gid == _policy_os.getegid() and gid == _policy_os.getgid(),
                        'selected effective UID/GID changed during read')
        result = raw
    except BaseException as error:
        primary = error
    finally:
        cleanup = []
        if reopened is not None:
            cleanup.extend(_policy_close(reopened))
        if source_reopened is not None:
            cleanup.extend(_policy_close(source_reopened))
        if held is not None:
            cleanup.extend(_policy_close(held))
        if source_held is not None:
            cleanup.extend(_policy_close(source_held))
    _policy_finish(primary, cleanup)
    # Cleanup may run after the in-try identity observation. This is the last
    # observation before bytes leave the guard; cleanup errors keep precedence.
    _policy_require(type(uid) is int and uid == _policy_os.geteuid() and
                    uid == _policy_os.getuid() and type(gid) is int and
                    gid == _policy_os.getegid() and gid == _policy_os.getgid(),
                    'selected effective UID/GID changed during cleanup')
    return result

class HostChannel:
    """Private host policy and real cryptographic proof; no caller supplied grants."""

    def __init__(self, path, policy_sha, source_pin, source, schemas):
        self.path = Path(path)
        self.policy_sha = policy_sha
        self.source_pin = source_pin
        self.source = source
        self.schemas = schemas
        self.closed = False
        self.used = False
        self.context = None
        self.policy = self.policy_guard()
        self.connection = 'connection:R03-context:' + uuid.uuid4().hex
        self.host = 'host:R03-context:' + uuid.uuid4().hex
        self.challenge = {'schema_version': 'lab-context-host-challenge/v1-candidate', 'host_instance_ref': self.host, 'connection_ref': self.connection, 'nonce': secrets.token_hex(32), 'policy_sha256': policy_sha, 'expires_at': self.policy['expires_at'], 'authority_effect': 'none'}

    def policy_guard(self):
        require(not self.closed, 'closed host channel')
        require(os.getuid() == os.geteuid() and os.getgid() == os.getegid(), 'host runtime identity split')
        FACT_SCOPE.package_guard(self.source, verify_source, self.source_pin)
        FACT_SCOPE.parent_guard(self.source)
        raw = read_policy_bytes(self.path, self.path.parent, ROOT, self.policy_sha, os.geteuid(), os.getegid())
        v = EL.parse(raw)
        require(set(v) == set('schema_version host_uid principal_ref scope_ref reader_public_key not_before expires_at max_input_bytes max_output_bytes max_session_seconds period_binding allowed_operations authority_effect actual_owner_outcome'.split()), 'closed host policy required')
        require(v['schema_version'] == 'lab-context-host-policy/v1-candidate' and v['host_uid'] == os.geteuid() and (v['principal_ref'] == records.PRINCIPAL) and (v['scope_ref'] == self.source.sources.scope_ref) and (v['allowed_operations'] == ['context.get', 'session.open']) and (v['authority_effect'] == 'none') and (v['actual_owner_outcome'] is None), 'host permission scope/posture differs')
        require(EL.instant(v['not_before']) <= now() < EL.instant(v['expires_at']), 'host permission expired or not yet effective')
        require(v['period_binding'] == binding(reader.HERE / 'packages/0001/period.json'), 'independent absolute Assignment period differs')
        for key, maximum in [('max_input_bytes', 1048576), ('max_output_bytes', 4194304), ('max_session_seconds', 3600)]:
            require(type(v[key]) is int and 1 <= v[key] <= maximum, 'host budget invalid')
        Ed25519PublicKey.from_public_bytes(base64.b64decode(v['reader_public_key'], validate=True))
        return v

    def authenticate(self, proof_raw):
        require(not self.used and self.context is None, 'authentication challenge already consumed')
        self.used = True
        self.policy_guard()
        proof = EL.parse(proof_raw)
        require(set(proof) == {'challenge', 'signature'} and proof['challenge'] == self.challenge, 'proof names another challenge')
        Ed25519PublicKey.from_public_bytes(base64.b64decode(self.policy['reader_public_key'], validate=True)).verify(base64.b64decode(proof['signature'], validate=True), wire(self.challenge))
        profile = self.source.view.handle.manifest['profile_binding']
        self.context = {'schema_version': 'lab-trusted-call-context/v1-candidate', 'context_ref': 'context:R03-delivery:' + uuid.uuid4().hex, 'host_instance_ref': self.host, 'connection_ref': self.connection, 'principal_ref': records.PRINCIPAL, 'role_assignment_bindings': [], 'authority_scope': 'operator-local', 'scope_refs': [self.policy['scope_ref']], 'source_profile_binding': {'ref': profile['path'], 'sha256': profile['sha256']}, 'authentication_evidence_binding': bind('authentication:' + self.connection, proof_raw), 'policy_bindings': [bind('host-policy:' + self.connection, read_policy_bytes(self.path, self.path.parent, ROOT, self.policy_sha, os.geteuid(), os.getegid())), bind(_t35_binding_path(AUTH), _context_development_auth(self.source.sources.scope_ref))], 'agent_instance_ref': None, 'session_ref': None, 'assignment_ref': None, 'expires_at': self.policy['expires_at'], 'limits': {'max_request_bytes': self.policy['max_input_bytes'], 'max_response_bytes': self.policy['max_output_bytes'], 'max_actions': 1, 'deadline': self.policy['expires_at']}, 'origin': 'verified-local-adapter', 'accept_client_supplied_authority_context': False, 'private_credentials_in_context': False}
        require(self.schemas.valid('trusted-call-context', self.context), 'original trusted context schema rejected constructed host context')
        return copy.deepcopy(self.context)

    def guard(self):
        require(self.context is not None and (not self.closed), 'host channel unauthenticated or closed')
        self.policy_guard()
        require(EL.instant(self.context['expires_at']) > now(), 'host channel expired')
        return copy.deepcopy(self.context)

    def actor(self):
        c = self.guard()
        return {'principal_ref': c['principal_ref'], 'role_assignment_refs': c['role_assignment_bindings'], 'agent_instance_ref': None, 'session_ref': None, 'assignment_ref': None}

    def permission(self):
        self.guard()
        v = self.policy
        p = load(reader.HERE / 'packages/0001/period.json')
        protocols = {}
        for f in (HERE / 'protocols').glob('*.json'):
            body = load(f)
            protocols[body['reference']] = {'kind': body['kind'], 'binding': {'ref': _t35_binding_path(f), 'sha256': sha(f.read_bytes())}}
        implementation = load(HERE / 'implementation-binding.json')
        return EL.SessionPermission(records.PRINCIPAL, v['scope_ref'], frozenset(v['allowed_operations']), v['not_before'], v['expires_at'], {p['period_ref']: [p['not_before'], p['expires_at']]}, frozenset([records.POLICY]), frozenset(), frozenset(), (bind('host-policy:' + self.connection, read_policy_bytes(self.path, self.path.parent, ROOT, self.policy_sha, os.geteuid(), os.getegid())), bind(_t35_binding_path(AUTH), _context_development_auth(self.source.sources.scope_ref))), 1, v['max_input_bytes'], v['max_output_bytes'], v['max_session_seconds'], {records.IMPLEMENTATION + '@' + records.VERSION: {'entrypoint_ref': implementation['entrypoint_ref'], 'environment_contract_ref': implementation['environment_contract_ref'], 'evidence_binding': {'ref': _t35_binding_path(HERE / 'implementation-binding.json'), 'sha256': sha((HERE / 'implementation-binding.json').read_bytes())}}}, protocols)

    def permission_guard(self, value):
        return value == self.permission()

    def close(self):
        self.closed = True
        self.context = None
        self.challenge = None
        self.used = True
