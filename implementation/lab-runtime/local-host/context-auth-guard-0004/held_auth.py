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
