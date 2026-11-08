"""Effect-disabled durable public Source stage candidate.

The selected persistent attempt is never touched by this version. Fixture
tests exercise the same held-FD copy core under a disposable /tmp directory.
No historical branch.snapshot body may enter the selected 941-file cut.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
import datetime as dt
from pathlib import Path, PurePosixPath

REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
LOCAL = REPO / 'implementation/lab-runtime/local-host'
PROFILE = LOCAL / 'context-successor-recovery-0001'
PROFILE_FREEZE_SHA = 'bb9f9be62c606dc87ccfdab9b5497c833cf781e89170d789379167582950bf66'
PUBLIC_CUT_SHA = '0333193eecf462528082f79123aba15d53fc630cf21e9ae2ca39b993b30bf11b'
SOURCE_MANIFEST_SHA = '2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1'
SOURCE_ROLE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
LIVE_BASE = Path('/home/vlad_/.local/state/cyberalchemy-lab')
STATE_PARENT = LIVE_BASE.parent
LIVE_FAMILY = 'context-successor-20261020-0001'
LIVE_ATTEMPT = 'source-attempt'
MARKER = '.context-successor-20261020-0001-source-stage-consumed.json'
REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-STAGE-INDEPENDENT-STATIC-REVIEW-0001.md'
MAX_PUBLIC_BYTES = 4 * 1024 * 1024


class Refused(RuntimeError):
    pass


class Unknown(Refused):
    def __init__(self, reason, marker, family, identities=None):
        self.status = 'UNKNOWN_PRESERVE_NO_RETRY'
        self.retry_allowed = False
        self.marker = str(marker)
        self.family = str(family)
        self.identities = identities or {}
        super().__init__(reason)


def need(ok, why):
    if not ok:
        raise Refused(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def wire(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + '\n').encode()


def write_all(fd, raw):
    view = memoryview(raw)
    while view:
        count = os.write(fd, view)
        need(count > 0, 'short durable write')
        view = view[count:]


def safe_rel(name):
    need(type(name) is str and name and not name.startswith('/') and
         '\\' not in name and '//' not in name and
         PurePosixPath(name).as_posix() == name and
         all(part not in ('', '.', '..') for part in name.split('/')) and
         not name.endswith('/branch.snapshot') and
         not any(s in name.lower() for s in ('.pem', '.key', 'private', 'secret', 'credential')),
         'unsafe or protected public-stage member')
    return name


def profile():
    freeze_raw = (PROFILE / 'freeze.json').read_bytes()
    need(sha(freeze_raw) == PROFILE_FREEZE_SHA, 'public successor freeze differs')
    freeze = json.loads(freeze_raw)
    need(freeze['status'] == 'PUBLIC_ONLY_EFFECT_DISABLED' and
         freeze['private_archive_body_included'] is False and
         freeze['source_effect'] == 'NOT_RUN', 'public successor effect differs')
    for row in freeze['file_bindings']:
        path = PROFILE / safe_rel(row['path'])
        need(path.is_file() and not path.is_symlink(), 'frozen public member missing')
        raw = path.read_bytes()
        need(len(raw) == row['size'] and sha(raw) == row['sha256'],
             'frozen public member changed')
    cut_raw = (PROFILE / 'public-cut.json').read_bytes()
    need(sha(cut_raw) == PUBLIC_CUT_SHA, 'public cut changed')
    cut = json.loads(cut_raw)
    rows = cut['public_inputs'] + cut['generated_bindings']
    paths = [safe_rel(row['path']) for row in rows]
    need(len(cut['public_inputs']) == 933 and len(cut['generated_bindings']) == 8 and
         len(rows) == len(set(paths)) == 941 and cut['effect'] == 'NOT_RUN' and
         cut['private_archive_bodies_read'] is False and
         cut['new_family'] == SOURCE_ROLE and
         cut['source_manifest'] == {'path': SOURCE_ROLE + '/source-manifest.json',
                                    'sha256': SOURCE_MANIFEST_SHA},
         'exact 941-file public stage selection differs')
    generated = {row['path'] for row in cut['generated_bindings']}
    need(len(generated) == 8 and generated.isdisjoint(
         {row['path'] for row in cut['public_inputs']}), 'generated/public collision')
    return cut, rows, generated


def selected_bytes(row, generated):
    name = safe_rel(row['path'])
    path = (PROFILE / 'generated' / name) if name in generated else (REPO / name)
    need(path.is_file() and not path.is_symlink() and
         all(not p.is_symlink() for p in path.parents if p != REPO and p != PROFILE),
         'public preimage missing or symlinked')
    raw = path.read_bytes()
    need(len(raw) <= MAX_PUBLIC_BYTES and sha(raw) == row['sha256'],
         'public preimage digest or size differs')
    return raw


class HeldAbsolute:
    """Keep every no-follow ancestor FD and reject detached components."""
    def __init__(self, path, *, private_leaf=True):
        path = Path(path)
        need(path.is_absolute() and str(path) == path.as_posix() and
             all(part not in ('', '.', '..') for part in path.parts[1:]),
             'absolute normalized directory required')
        self.path = path
        self.parts = path.parts[1:]
        self.fds = []
        self.baseline = []
        try:
            fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                         os.O_CLOEXEC)
            self.fds.append(fd)
            for name in self.parts:
                fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                             os.O_CLOEXEC, dir_fd=fd)
                self.fds.append(fd)
            for index, fd in enumerate(self.fds):
                st = os.fstat(fd)
                observed_path = Path('/', *self.parts[:index])
                sticky_tmp = (observed_path == Path('/tmp') and
                              path.parent == Path('/tmp') and
                              st.st_uid == 0 and stat.S_IMODE(st.st_mode) == 0o1777)
                need(stat.S_ISDIR(st.st_mode) and st.st_uid in (0, os.geteuid()) and
                     (not (st.st_mode & 0o022) or sticky_tmp),
                     'unsafe writable or foreign ancestor')
            self.baseline = [self.identity(os.fstat(fd)) for fd in self.fds]
            self.check()
            own = os.fstat(self.fds[-1])
            need((not private_leaf or stat.S_IMODE(own.st_mode) == 0o700) and
                 own.st_uid == os.getuid() == os.geteuid() and
                 own.st_gid == os.getgid() == os.getegid(),
                 'owner-0700 selected base required')
        except BaseException:
            self.close()
            raise

    @staticmethod
    def identity(st):
        return (st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid)

    @property
    def fd(self):
        return self.fds[-1]

    def check(self):
        need(len(self.fds) == len(self.parts) + 1, 'held ancestry closed')
        for index, baseline in enumerate(self.baseline):
            need(self.identity(os.fstat(self.fds[index])) == baseline,
                 'held ancestor changed')
            if index:
                by_name = os.stat(self.parts[index - 1],
                                  dir_fd=self.fds[index - 1], follow_symlinks=False)
                need(self.identity(by_name) == baseline,
                     'held ancestor detached or replaced')

    def close(self):
        failures = []
        for fd in reversed(self.fds):
            try:
                os.close(fd)
            except OSError as exc:
                failures.append(exc)
        self.fds = []
        need(not failures, 'held ancestry close uncertain')


def mkdir_at(parent, name):
    need(type(name) is str and name not in ('', '.', '..') and '/' not in name,
         'unsafe directory name')
    os.mkdir(name, 0o700, dir_fd=parent)
    fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                 dir_fd=parent)
    os.fchmod(fd, 0o700)
    os.fsync(fd)
    os.fsync(parent)
    return fd


def open_or_create_dirs(root_fd, parts):
    opened = []
    parent = root_fd
    try:
        for name in parts:
            try:
                fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                             os.O_CLOEXEC, dir_fd=parent)
            except FileNotFoundError:
                fd = mkdir_at(parent, name)
            st = os.fstat(fd)
            need(stat.S_ISDIR(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o700 and
                 st.st_uid == os.geteuid() and st.st_gid == os.getegid(),
                 'stage directory changed')
            opened.append(fd)
            parent = fd
        return opened
    except BaseException:
        for fd in reversed(opened):
            os.close(fd)
        raise


def write_file(root_fd, name, raw, expected_sha):
    parts = safe_rel(name).split('/')
    opened = open_or_create_dirs(root_fd, parts[:-1])
    parent = opened[-1] if opened else root_fd
    fd = None
    try:
        fd = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                     os.O_NOFOLLOW | os.O_CLOEXEC, 0o444, dir_fd=parent)
        write_all(fd, raw)
        os.fchmod(fd, 0o444)
        os.fsync(fd)
        os.close(fd)
        fd = None
        reader = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                         dir_fd=parent)
        try:
            st = os.fstat(reader)
            observed = os.read(reader, len(raw) + 1)
            need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
                 stat.S_IMODE(st.st_mode) == 0o444 and
                 st.st_uid == os.geteuid() and st.st_gid == os.getegid() and
                 len(observed) == len(raw) and sha(observed) == expected_sha,
                 'public stage held readback differs')
        finally:
            os.close(reader)
        os.fsync(parent)
    finally:
        if fd is not None:
            os.close(fd)
        for item in reversed(opened):
            os.close(item)


def verify_tree(root_fd, rows):
    expected = {row['path']: row['sha256'] for row in rows}
    expected_dirs = {str(parent) for name in expected for parent in PurePosixPath(name).parents
                     if str(parent) != '.'}
    expected_dirs |= {SOURCE_ROLE + '/packages', SOURCE_ROLE + '/receipts'}
    files, dirs = set(), set()
    for base, children, leaves, fd in os.fwalk('.', topdown=True,
                                               follow_symlinks=False, dir_fd=root_fd):
        prefix = PurePosixPath(base)
        for name in children:
            rel = str(prefix / name).removeprefix('./')
            st = os.stat(name, dir_fd=fd, follow_symlinks=False)
            need(stat.S_ISDIR(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o700 and
                 st.st_uid == os.geteuid() and st.st_gid == os.getegid(),
                 'stage directory mode or owner differs')
            dirs.add(rel)
        for name in leaves:
            rel = str(prefix / name).removeprefix('./')
            safe_rel(rel)
            fd_leaf = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                              dir_fd=fd)
            try:
                st = os.fstat(fd_leaf)
                need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
                     stat.S_IMODE(st.st_mode) == 0o444 and
                     st.st_uid == os.geteuid() and st.st_gid == os.getegid() and
                     rel in expected and st.st_size <= MAX_PUBLIC_BYTES,
                     'stage leaf owner/mode/selection differs')
                raw = os.read(fd_leaf, st.st_size + 1)
                need(len(raw) == st.st_size and sha(raw) == expected[rel],
                     'stage leaf digest differs')
            finally:
                os.close(fd_leaf)
            files.add(rel)
    need(files == set(expected) and dirs == expected_dirs and len(files) == 941,
         'exact public-stage namespace differs')
    return len(files), len(dirs)


def write_private_at(parent_fd, name, raw):
    """Exclusive owner-0600 durable leaf with exact held readback."""
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent_fd)
    try:
        write_all(fd, raw)
        os.fchmod(fd, 0o600)
        os.fsync(fd)
    finally:
        os.close(fd)
    reader = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=parent_fd)
    try:
        st = os.fstat(reader)
        observed = os.read(reader, len(raw) + 1)
        need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
             stat.S_IMODE(st.st_mode) == 0o600 and
             st.st_uid == os.geteuid() and st.st_gid == os.getegid() and
             len(observed) == len(raw) and sha(observed) == sha(raw),
             'private durable leaf mode/owner/readback differs')
        identity = [st.st_dev, st.st_ino]
    finally:
        os.close(reader)
    os.fsync(parent_fd)
    return identity


def claim_marker(base_fd, name, value, marker, family):
    raw = wire(value)
    try:
        identity = write_private_at(base_fd, name, raw)
    except FileExistsError as exc:
        raise Refused('durable stage marker already consumed; no retry') from exc
    except BaseException as exc:
        try:
            st = os.stat(name, dir_fd=base_fd, follow_symlinks=False)
            identity = [st.st_dev, st.st_ino]
        except OSError:
            identity = 'PATH_UNCERTAIN'
        raise Unknown(type(exc).__name__, marker, family,
                      {'marker': identity}) from exc
    return sha(raw), identity


def available_identities(base_fd, marker_name, family_fd, attempt_fd,
                         evidence_fd, root_fd):
    observed = {}
    for name, fd in (('base', base_fd), ('family', family_fd),
                     ('attempt', attempt_fd), ('evidence', evidence_fd),
                     ('root', root_fd)):
        if fd is not None:
            try:
                st = os.fstat(fd)
                observed[name] = [st.st_dev, st.st_ino]
            except OSError:
                observed[name] = 'FD_UNCERTAIN'
    try:
        st = os.stat(marker_name, dir_fd=base_fd, follow_symlinks=False)
        observed['marker'] = [st.st_dev, st.st_ino]
    except OSError:
        observed['marker'] = 'PATH_UNCERTAIN'
    return observed


def stage_core(base, family_name, attempt_name, marker_name, *, rows, generated,
               inject_after=None, live=False):
    """Exact held-FD public copy core; live path needs external review gate."""
    base = Path(base)
    fixture = (base.parent == Path('/tmp') and
               base.name.startswith('cal-source-successor-stage-fixture-') and
               family_name == 'family' and attempt_name == 'source-attempt' and
               marker_name == 'consumed.json' and not live)
    selected_live = (base == LIVE_BASE and family_name == LIVE_FAMILY and
                     attempt_name == LIVE_ATTEMPT and marker_name == MARKER and live)
    need(fixture or selected_live, 'exact fixture or reviewed live stage root required')
    held = HeldAbsolute(base)
    base_fd = held.fd
    family = base / family_name
    marker = base / marker_name
    family_fd = attempt_fd = evidence_fd = root_fd = None
    consumed = False
    pending = None
    result = None
    try:
        need(not family.exists() and not family.is_symlink(), 'fixture family occupied')
        marker_digest, marker_identity = claim_marker(base_fd, marker_name, {
            'schema': 'context-successor-stage-intent/v1',
            'family': str(family), 'attempt': str(family / attempt_name),
            'public_cut_sha256': PUBLIC_CUT_SHA, 'retry_allowed': False,
            'status': 'CONSUMED_NO_RETRY'}, marker, family)
        consumed = True
        held.check()
        family_fd = mkdir_at(base_fd, family_name)
        attempt_fd = mkdir_at(family_fd, attempt_name)
        evidence_fd = mkdir_at(attempt_fd, 'evidence')
        root_fd = mkdir_at(attempt_fd, 'root')
        for index, row in enumerate(rows, 1):
            held.check()
            for parent_fd, name, owned_fd in ((base_fd, family_name, family_fd),
                                              (family_fd, attempt_name, attempt_fd),
                                              (attempt_fd, 'root', root_fd)):
                observed = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                owned = os.fstat(owned_fd)
                need((observed.st_dev, observed.st_ino, observed.st_mode,
                      observed.st_uid, observed.st_gid) ==
                     (owned.st_dev, owned.st_ino, owned.st_mode,
                      owned.st_uid, owned.st_gid), 'stage path detached')
            write_file(root_fd, row['path'], selected_bytes(row, generated), row['sha256'])
            held.check()
            if inject_after == index:
                raise OSError('injected post-copy uncertainty')
        for leaf in ('packages', 'receipts'):
            opened = open_or_create_dirs(root_fd, SOURCE_ROLE.split('/') + [leaf])
            for fd in reversed(opened):
                os.close(fd)
        files, dirs = verify_tree(root_fd, rows)
        held.check()
        for parent_fd, name, held_fd in ((base_fd, family_name, family_fd),
                                         (family_fd, attempt_name, attempt_fd),
                                         (attempt_fd, 'root', root_fd)):
            observed = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            held_stat = os.fstat(held_fd)
            need((observed.st_dev, observed.st_ino) ==
                 (held_stat.st_dev, held_stat.st_ino),
                 'stage attempt detached')
        receipt = {'schema': 'context-successor-public-stage-receipt/v1',
                   'status': 'STAGE_ONLY_PASS', 'root': str(family / attempt_name / 'root'),
                   'files': files, 'directories': dirs,
                   'public_cut_sha256': PUBLIC_CUT_SHA,
                   'source_manifest_sha256': SOURCE_MANIFEST_SHA,
                   'marker_sha256': marker_digest,
                   'marker_identity': marker_identity,
                   'protected_archive_body': 'ABSENT',
                   'source_effect': 'NOT_RUN', 'retry_allowed': False,
                   'root_identity': [os.fstat(root_fd).st_dev, os.fstat(root_fd).st_ino]}
        raw = wire(receipt)
        write_private_at(evidence_fd, 'stage-receipt.json', raw)
        held.check()
        result = receipt
    except BaseException as exc:
        identities = available_identities(base_fd, marker_name, family_fd,
                                          attempt_fd, evidence_fd, root_fd)
        pending = (Unknown(type(exc).__name__, marker, family, identities)
                   if consumed and not isinstance(exc, Unknown) else exc)
    finally:
        failures = []
        closing_identities = available_identities(base_fd, marker_name, family_fd,
                                                  attempt_fd, evidence_fd, root_fd)
        for fd in (root_fd, evidence_fd, attempt_fd, family_fd):
            if fd is not None:
                try:
                    os.close(fd)
                except BaseException as exc:
                    failures.append(type(exc).__name__)
        try:
            held.close()
        except BaseException as exc:
            failures.append(type(exc).__name__)
        if failures:
            pending = (Unknown('close uncertainty: ' + ','.join(failures), marker, family,
                               closing_identities)
                       if consumed else Refused('preclaim close uncertainty'))
    if pending is not None:
        raise pending
    return result


def stage_live():
    """One-shot live public stage, gated by the exact independent review."""
    freeze = Path(__file__).resolve().parent / 'freeze.json'
    need(freeze.is_file() and REVIEW.is_file(),
         'INDEPENDENT_STAGE_REVIEW_REQUIRED_BEFORE_LIVE_EFFECT')
    freeze_raw = freeze.read_bytes()
    review_raw = REVIEW.read_bytes()
    need(b'Verdict: PASS' in review_raw and sha(freeze_raw).encode() in review_raw,
         'INDEPENDENT_STAGE_REVIEW_DOES_NOT_BIND_FREEZE')
    rows_value = json.loads(freeze_raw)
    need(rows_value['status'] == 'EFFECT_DISABLED_UNRUN_PENDING_INDEPENDENT_REVIEW' and
         rows_value['profile_freeze_sha256'] == PROFILE_FREEZE_SHA and
         rows_value['public_cut_sha256'] == PUBLIC_CUT_SHA and
         rows_value['live_stage'] == 'UNRUN',
         'stage release status or selected profile differs')
    for row in rows_value['file_bindings']:
        path = freeze.parent / safe_rel(row['path'])
        raw = path.read_bytes()
        need(len(raw) == row['size'] and sha(raw) == row['sha256'],
             'stage release file changed after independent review')
    cut, rows, generated = profile()
    now = dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(cut['not_before'])
    end = dt.datetime.fromisoformat(cut['expires_at'])
    need(start <= now < end and end - start == dt.timedelta(hours=24),
         'selected Source period absent or expired')
    # All public input bodies are prechecked before the first host mutation.
    for row in rows:
        selected_bytes(row, generated)
    parent = HeldAbsolute(STATE_PARENT, private_leaf=False)
    try:
        parent.check()
        try:
            base_fd = mkdir_at(parent.fd, LIVE_BASE.name)
        except FileExistsError:
            base_fd = os.open(LIVE_BASE.name, os.O_RDONLY | os.O_DIRECTORY |
                              os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent.fd)
            st = os.fstat(base_fd)
            need(stat.S_IMODE(st.st_mode) == 0o700 and
                 st.st_uid == os.geteuid() and st.st_gid == os.getegid(),
                 'selected persistent base occupied by another owner or mode')
        try:
            parent.check()
            by_name = os.stat(LIVE_BASE.name, dir_fd=parent.fd,
                              follow_symlinks=False)
            held = os.fstat(base_fd)
            need((by_name.st_dev, by_name.st_ino) == (held.st_dev, held.st_ino),
                 'persistent base detached before stage')
        finally:
            os.close(base_fd)
    finally:
        parent.close()
    return stage_core(LIVE_BASE, LIVE_FAMILY, LIVE_ATTEMPT, MARKER,
                      rows=rows, generated=generated, live=True)


if __name__ == '__main__':
    import sys
    need(sys.argv[1:] == ['--execute-reviewed-one-shot'],
         'reviewed one-shot flag required')
    print(json.dumps(stage_live(), sort_keys=True))
