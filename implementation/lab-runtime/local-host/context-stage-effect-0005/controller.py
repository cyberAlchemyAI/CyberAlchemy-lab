"""One-shot Context stage candidate. Real effect is deliberately disabled.

This module contains no Context import, key, grant, or launch path. The fixture
entrypoint exercises the same held-FD copy engine with disposable public bytes.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
REPO = Path('/home/vlad_/projects/CyberAlchemy-lab')
SELECTION = LOCAL / 'context-stage-0001/selection.json'
SELECTION_SHA = '6721210d076da6462f904b2836a9e3ff5853be92f395a05ee2b141b517e078bf'
REVIEW = LOCAL / 'CONTEXT-STAGE-INDEPENDENT-STATIC-REVIEW-0002.md'
REVIEW_SHA = 'f448feb0f6eceaa75a144c77aa0c415265b01d946aebe3c7911db227ff1c3e90'
STAGE2_FREEZE = LOCAL / 'context-stage-0002/freeze.json'
STAGE2_FREEZE_SHA = '57f69000d85bb4da1294c7eca159fc06a80e1de79c136e8c1c06a5703da056a5'
STAGE1_CODE = LOCAL / 'context-stage-0001/stage.py'
STAGE1_CODE_SHA = 'fabc4a60e0e2eee751e783f843a73c883b7967db56a54983bc3e0d7d2b33d884'
ARCHIVE = ('product/lab/release-candidates/v1/interface/'
           'docker-source-20261020-0001/packages/0001/branch.snapshot')
REAL_ATTEMPT = Path('/tmp/cal-context-family-20261020-0001')
REAL_SOURCE = Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/root')
MAX_PUBLIC = 4 * 1024 * 1024
MAX_PRIVATE = 24 * 1024 * 1024
MAX_NATIVE = 32 * 1024 * 1024
REAL_EFFECT_ENABLED = False
FIXTURE_CLAIM_MARKER = '.context-stage-one-shot-claim.json'


class Refused(RuntimeError):
    pass


class Poisoned(Refused):
    def __init__(self, primary, cleanup, attempt, owned_inode, observed_name_inode=None,
                 claim_marker_path=None):
        self.primary = primary
        self.cleanup = tuple(cleanup)
        self.attempt = str(attempt)
        self.owned_inode = owned_inode
        self.observed_name_inode = observed_name_inode
        self.claim_marker_path = str(claim_marker_path) if claim_marker_path else None
        self.outcome = 'UNKNOWN' if owned_inode is not None or cleanup else 'REFUSED'
        self.disposition = 'RETAIN_OWNED_INODE_NO_NAME_UNLINK'
        self.retry_allowed = False
        super().__init__('attempt retained; primary or cleanup uncertainty; never retry')


def need(ok, why):
    if not ok:
        raise Refused(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def valid_name(name):
    need(type(name) is str and name and not name.startswith('/') and '\\' not in name
         and '//' not in name and PurePosixPath(name).as_posix() == name
         and all(x not in ('', '.', '..') for x in name.split('/')), 'unsafe relative path')
    return name


def valid_pin(pin):
    need(type(pin) is str and len(pin) == 64 and
         all(c in '0123456789abcdef' for c in pin), 'invalid SHA-256 pin')
    return pin


class FixtureCustody:
    """Owns validated ancestry until every fixture leaf and attachment check ends."""
    def __init__(self, root, owned):
        self.root = root
        self.owned = owned
        self.baseline = tuple((st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid)
                              for st in (os.fstat(fd) for fd in owned))

    def check_attachment(self):
        need(len(self.owned) == 4, 'fixture custody was closed')
        for index, component in enumerate(('tmp', self.root.parent.name, 'source'), 1):
            by_fd = os.fstat(self.owned[index])
            by_name = os.stat(component, dir_fd=self.owned[index-1],
                              follow_symlinks=False)
            for item in (by_fd, by_name):
                current = (item.st_dev, item.st_ino, item.st_mode, item.st_uid, item.st_gid)
                need(current == self.baseline[index],
                     'fixture source ancestry detached or changed')

    def close(self):
        return close_all_once(self.owned)


class FixtureTargetCustody:
    """Owns exclusive attempt and root FDs throughout fixture writes."""
    def __init__(self, attempt, owned):
        self.attempt = Path(attempt)
        self.owned = owned
        self.baseline = tuple((st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid)
                              for st in (os.fstat(fd) for fd in owned))

    @property
    def root_fd(self):
        return self.owned[-1]

    @property
    def attempt_inode(self):
        return self.baseline[-2][:2]

    def check_attachment(self):
        need(len(self.owned) == 4, 'fixture target custody closed')
        for index, component in enumerate(('tmp', self.attempt.name, 'root'), 1):
            by_fd = os.fstat(self.owned[index])
            by_name = os.stat(component, dir_fd=self.owned[index-1],
                              follow_symlinks=False)
            for item in (by_fd, by_name):
                current = (item.st_dev, item.st_ino, item.st_mode, item.st_uid, item.st_gid)
                need(current == self.baseline[index],
                     'fixture attempt/root detached or changed')
                if index >= 2:
                    need(stat.S_ISDIR(item.st_mode) and item.st_uid == os.geteuid() and
                         item.st_gid == os.getegid() and item.st_mode & 0o777 == 0o700,
                         'fixture attempt/root owner or mode differs')

    def close(self):
        return close_all_once(self.owned)


def acquire_fixture_source(root, attempt=None):
    """Return held no-follow disposable source custody; caller must close it."""
    root = Path(root)
    need(root.is_absolute() and root.name == 'source' and
         root.parent.parent == Path('/tmp') and
         root.parent.name.startswith('cal-context-stage-fixture-test-') and
         root.parent.name != 'cal-context-stage-fixture-test-' and
         root != REAL_SOURCE, 'exclusive disposable public source root required')
    if attempt is not None:
        need(Path(attempt) == Path('/tmp') /
             ('cal-context-stage-fixture-' + root.parent.name),
             'attempt/source fixture identity differs')
    owned = root_fds(root); real_owned = []; primary = None
    try:
        parent = os.fstat(owned[-2]); selected = os.fstat(owned[-1])
        need(all(stat.S_ISDIR(x.st_mode) and x.st_uid == os.geteuid() and
                 x.st_gid == os.getegid() and x.st_mode & 0o777 == 0o700
                 for x in (parent, selected)),
             'public fixture ancestry owner/mode differs')
        real_owned = root_fds(REAL_SOURCE)
        need(inode(selected) != inode(os.fstat(real_owned[-1])),
             'fixture source aliases retained family root')
    except BaseException as exc:
        primary = exc
    cleanup = close_all_once(real_owned)
    if primary or cleanup:
        cleanup += close_all_once(owned)
        raise Poisoned(primary, cleanup, root, None) from primary
    try:
        custody = FixtureCustody(root, owned)
    except BaseException as exc:
        cleanup = close_all_once(owned)
        raise Poisoned(exc, cleanup, root, None) from exc
    try:
        custody.check_attachment()
    except BaseException as exc:
        cleanup = custody.close()
        raise Poisoned(exc, cleanup, root, None) from exc
    return custody


def ident(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid, st.st_nlink, st.st_size)


def inode(st):
    return (st.st_dev, st.st_ino)


def _close_once(fd):
    os.close(fd)


def close_all_once(fds):
    errors = []
    for fd in reversed(fds):
        try:
            _close_once(fd)
        except BaseException as exc:
            # The close may already have released this numeric FD. Never retry it.
            errors.append((fd, repr(exc)))
    fds.clear()
    return errors


def root_fds(path):
    path = Path(path)
    need(path.is_absolute() and path.as_posix() == str(path), 'absolute root required')
    owned = []
    try:
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        owned.append(fd)
        for part in path.parts[1:]:
            fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                         dir_fd=fd)
            owned.append(fd)
        return owned
    except BaseException as exc:
        failures = close_all_once(owned)
        if failures:
            raise Poisoned(exc, failures, path, None) from exc
        raise


def descend(fd, parts, owned):
    for part in parts:
        fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=fd)
        owned.append(fd)
    return fd


def held_measure(root, name, pin, size=None, mode=None, limit=MAX_PUBLIC, capture=False):
    """Digest through a held regular-file FD; no private read during preflight."""
    valid_name(name); valid_pin(pin)
    need(size is None or (type(size) is int and 0 <= size <= limit),
         'invalid expected size')
    owned = [] if type(root) is int else root_fds(root)
    primary = None; result = None
    try:
        parts = name.split('/')
        parent = descend(root if type(root) is int else owned[-1], parts[:-1], owned)
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=parent)
        owned.append(fd)
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             (size is None or before.st_size == size) and before.st_size <= limit,
             'input type, link count, or size differs')
        if mode is not None:
            need(before.st_mode & 0o777 == int(mode, 8), 'input mode differs')
        size = before.st_size
        digest = hashlib.sha256(); total = 0; parts = []
        while True:
            block = os.read(fd, min(65536, size + 1 - total))
            if not block:
                break
            total += len(block)
            need(total <= size, 'input grew during read')
            digest.update(block)
            if capture:
                parts.append(block)
        need(ident(os.fstat(fd)) == ident(before) and total == size and
             digest.hexdigest() == pin, 'input changed or digest differs')
        result = {'sha256': pin, 'size': size, 'mode': format(before.st_mode & 0o777, '04o'),
                  'uid': before.st_uid, 'gid': before.st_gid, 'inode': inode(before)}
        if capture:
            result['bytes'] = b''.join(parts)
    except BaseException as exc:
        primary = exc
    cleanup = close_all_once(owned)
    if primary or cleanup:
        raise Poisoned(primary, cleanup, root, None) from primary
    return result


def closed_selection():
    selection_raw = None
    for path, pin in ((SELECTION, SELECTION_SHA), (REVIEW, REVIEW_SHA),
                      (STAGE2_FREEZE, STAGE2_FREEZE_SHA)):
        st = path.stat(follow_symlinks=False)
        need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_size <= 1024*1024,
             'reviewed selection/review/freeze metadata differs')
        measured = held_measure(REPO, path.relative_to(REPO).as_posix(), pin, st.st_size,
                                limit=1024*1024, capture=path == SELECTION)
        if path == SELECTION:
            selection_raw = measured['bytes']
    selected = json.loads(selection_raw)
    need(selected['schema_version'] == 'lab-context-stage-role-selection/v1-candidate'
         and selected['effect'] == 'NOT_RUN' and selected['context_launch'] == 'REFUSED'
         and selected['future_root_file_count_if_protected_copied_under_separate_effect'] == 1570
         and selected['protected_body_read'] is False
         and selected['source_family_root'] == str(REAL_SOURCE)
         and selected['future_exclusive_stage_root'] == str(REAL_ATTEMPT / 'root')
         and selected['protected_family_binding']['path'] == ARCHIVE,
         'reviewed stage selection differs')
    rows = []
    for key, root in (('existing_family_public', REAL_SOURCE),
                      ('exact_public_checkout_additions', REPO),
                      ('projected_api_additions', LOCAL / 'context-family-0001/generated'),
                      ('projected_context_additions', LOCAL / 'context-stage-0001/generated')):
        for row in selected[key]:
            name = valid_name(row['path'])
            valid_pin(row['sha256'])
            source_name = name
            if key == 'projected_api_additions':
                source_name = 'api-v25/' + Path(name).name
            elif key == 'projected_context_additions':
                source_name = 'context/' + Path(name).name
            rows.append({'path': name, 'sha256': row['sha256'], 'size': row.get('size'),
                         'mode': row.get('mode'), 'source_root': root,
                         'source_name': source_name})
    protected = selected['protected_archive_metadata']
    need(protected['path'] == ARCHIVE and protected['body'] == 'UNOPENED_UNCOPIED'
         and protected['sha256'] == selected['protected_family_binding']['sha256']
         and protected['size'] == 23550300 and protected['mode'] == '0600',
         'reviewed protected binding differs')
    rows.append({'path': ARCHIVE, 'sha256': protected['sha256'],
                 'size': protected['size'], 'mode': '0600',
                 'source_root': REAL_SOURCE, 'source_name': ARCHIVE,
                 'protected': True})
    names = [x['path'] for x in rows]
    need(len(rows) == len(set(names)) == 1570 and
         sum(x.get('protected', False) for x in rows) == 1,
         'stage manifest duplicate or count differs')
    return selected, rows


def preflight_public(rows):
    """Resolve missing selected metadata and rehash every public source leaf."""
    need(len(rows) == 1570 and sum(x.get('protected', False) for x in rows) == 1,
         'exact reviewed stage rows required')
    raw = held_measure(REPO, STAGE1_CODE.relative_to(REPO).as_posix(), STAGE1_CODE_SHA,
                       limit=128*1024, capture=True)['bytes']
    namespace = {'__file__': str(STAGE1_CODE), '__name__': '_pinned_stage_inventory'}
    exec(compile(raw, str(STAGE1_CODE), 'exec'), namespace)
    inventory = namespace['verify_inventory']()
    reviewed = {x['path']: x for x in inventory['reader_stage_public'] +
                inventory['mapper_source_files'] + inventory['mapper_package_members']}
    manifest = inventory['mapper_package_manifest']
    need(len(reviewed) == 1044 and inventory['selected_family_total_files'] == 1046,
         'reviewed Source/Reader/Mapper inventory differs')
    reviewed[manifest['path']] = {'path': manifest['path'],
                                 'sha256': manifest['sha256'], 'mode': '0600'}
    result = []
    for row in rows:
        if row.get('protected'):
            # Only metadata, no private FD and no archive body read.
            owned = root_fds(row['source_root']); primary = None
            try:
                parent = descend(owned[-1], row['source_name'].split('/')[:-1], owned)
                st = os.stat(row['source_name'].split('/')[-1], dir_fd=parent,
                             follow_symlinks=False)
                need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
                     st.st_size == row['size'] and st.st_mode & 0o777 == 0o600 and
                     st.st_uid == os.geteuid() and st.st_gid == os.getegid(),
                     'protected archive metadata differs')
            except BaseException as exc:
                primary = exc
            cleanup = close_all_once(owned)
            if primary or cleanup:
                raise Poisoned(primary, cleanup, row['source_root'], None) from primary
            result.append(row.copy())
            continue
        info = held_measure(row['source_root'], row['source_name'], row['sha256'],
                            row['size'], row['mode'])
        need(info['uid'] == os.geteuid() and info['gid'] == os.getegid(),
             'public input owner differs')
        if row['source_root'] == REAL_SOURCE:
            selected = reviewed.get(row['path'])
            need(selected is not None and selected['sha256'] == row['sha256'] and
                 selected['mode'] == info['mode'] and
                 (selected.get('size') is None or selected['size'] == info['size']),
                 'same-family reviewed metadata differs')
        bound = row.copy(); bound['size'] = info['size']; bound['mode'] = info['mode']
        result.append(bound)
    return result


def native_binding(selected):
    source = Path(selected['native_source_path'])
    need(source == Path('/tmp/cal-mapper-only-dev-20261020-0001-release3/input/'
                        'lab-context-native-reader') and
         selected['container_native_path'] == '/attempt/input/lab-context-native-reader'
         and selected['native_mount_mode'] == 'ro', 'native mount selection differs')
    info = held_measure(source.parent, source.name, selected['native_sha256'],
                        20243600, '0755', MAX_NATIVE)
    need(info['uid'] == os.geteuid() and info['gid'] == os.getegid(),
         'native executable owner differs')
    return {'path': 'input/lab-context-native-reader',
            'sha256': selected['native_sha256'], 'size': 20243600, 'mode': '0755',
            'source_root': source.parent, 'source_name': source.name}


def _copy_one_core(row, target_root, *, allow_protected=False, fault=None,
                   custody=None, target_custody=None):
    name = valid_name(row['path'])
    source_name = valid_name(row['source_name'])
    # A caller's protected flag or allow_protected keyword is not authority.
    need(not allow_protected or REAL_EFFECT_ENABLED, 'real copy effect disabled')
    need(REAL_EFFECT_ENABLED or (name != ARCHIVE and source_name != ARCHIVE and
         not row.get('protected')), 'protected archive copy refused before source open')
    if not allow_protected:
        need(isinstance(custody, FixtureCustody) and
             custody.root == Path(row['source_root']) and custody.owned,
             'held validated fixture source required')
        need(isinstance(target_custody, FixtureTargetCustody) and
             Path(target_root) == target_custody.attempt / 'root' and
             target_custody.attempt == Path('/tmp') /
                 ('cal-context-stage-fixture-' + custody.root.parent.name) and
             target_custody.owned,
             'claimed held disposable fixture target required')
        custody.check_attachment()
        target_custody.check_attachment()
    pin = valid_pin(row['sha256'])
    size = row['size']; mode = row['mode']
    need(type(size) is int and 0 <= size <= (MAX_PRIVATE if row.get('protected') else MAX_NATIVE)
         and type(mode) is str and mode in ('0400','0444','0600','0644','0755'),
         'copy row size/mode unclosed')
    parts = name.split('/'); source_owned = []; target_owned = []
    primary = None; result = None; created = None; observed = None; target_parent = None
    try:
        source_owned = [] if custody is not None else root_fds(row['source_root'])
        target_owned = [] if target_custody is not None else root_fds(target_root)
        source_parent = descend(custody.owned[-1] if custody is not None else source_owned[-1],
                                row['source_name'].split('/')[:-1], source_owned)
        target_parent = descend(target_custody.root_fd if target_custody is not None
                                else target_owned[-1], parts[:-1], target_owned)
        leaf = parts[-1]
        if custody is not None:
            custody.check_attachment()  # Before opening any source leaf.
        sfd = os.open(row['source_name'].split('/')[-1],
                      os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                      dir_fd=source_parent)
        source_owned.append(sfd)
        a = os.fstat(sfd)
        need(stat.S_ISREG(a.st_mode) and a.st_nlink == 1 and a.st_size == size and
             a.st_mode & 0o777 == int(mode, 8), 'source type/size/mode differs')
        need(a.st_uid == os.geteuid() and a.st_gid == os.getegid(), 'source owner differs')
        if target_custody is not None:
            target_custody.check_attachment()  # Before any target creation.
        tfd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
                      os.O_CLOEXEC, int(mode, 8), dir_fd=target_parent)
        target_owned.append(tfd)
        os.fchmod(tfd, int(mode, 8))
        created = inode(os.fstat(tfd)); digest = hashlib.sha256(); count = 0
        if fault:
            fault('created', target_parent, leaf, created)
        while True:
            block = os.read(sfd, min(65536, size + 1 - count))
            if not block:
                break
            count += len(block)
            need(count <= size, 'source grew during copy')
            digest.update(block)
            view = memoryview(block)
            while view:
                wrote = os.write(tfd, view)
                need(type(wrote) is int and wrote > 0, 'target write stalled')
                view = view[wrote:]
        need(ident(os.fstat(sfd)) == ident(a) and count == size and
             digest.hexdigest() == pin, 'source changed during copy')
        os.fsync(tfd)
        b = os.fstat(tfd)
        need(inode(b) == created and b.st_size == size and b.st_nlink == 1 and
             b.st_mode & 0o777 == int(mode, 8) and
             b.st_uid == os.geteuid() and b.st_gid == os.getegid(),
             'target inode/mode/owner differs')
        need(inode(os.stat(leaf, dir_fd=target_parent, follow_symlinks=False)) == created,
             'target name replaced or detached')
        if fault:
            fault('precheck', target_parent, leaf, created)
        cfd = os.open(leaf, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                      dir_fd=target_parent)
        target_owned.append(cfd)
        c = os.fstat(cfd)
        need(ident(c) == ident(b), 'target reopened as different inode')
        check = hashlib.sha256(); checked = 0
        while True:
            block = os.read(cfd, min(65536, size + 1 - checked))
            if not block:
                break
            checked += len(block)
            need(checked <= size, 'target grew during verification')
            check.update(block)
        need(ident(os.fstat(cfd)) == ident(c) and checked == size and
             check.hexdigest() == pin, 'target changed or digest differs')
        os.fsync(target_parent)
        need(inode(os.stat(leaf, dir_fd=target_parent, follow_symlinks=False)) == created,
             'target name changed after directory fsync')
        if custody is not None:
            custody.check_attachment()  # Reject detachment during copy.
        if target_custody is not None:
            target_custody.check_attachment()
        result = size
    except BaseException as exc:
        primary = exc
    if primary is not None and target_parent is not None:
        try:
            observed = inode(os.stat(parts[-1], dir_fd=target_parent,
                                     follow_symlinks=False))
        except BaseException:
            pass
    cleanup = close_all_once(target_owned) + close_all_once(source_owned)
    if primary or cleanup:
        # Retain both owned partial names and foreign replacements. No unlink race.
        raise Poisoned(primary, cleanup, target_root, created, observed) from primary
    return {'path': name, 'sha256': pin, 'size': result,
            'created_inode': created, 'observed_on_failure': observed}


def copy_one(row, target_root, *, allow_protected=False, fault=None):
    """Direct public copy is disabled; only run_fixture owns target custody."""
    raise Refused('direct copy disabled; exclusive fixture attempt required')


def expected_dirs(names):
    dirs = set()
    for name in names:
        parts = name.split('/')
        for count in range(1, len(parts)):
            dirs.add('/'.join(parts[:count]))
    return dirs


def create_dirs(stage_root, names, *, target_custody=None):
    """All mkdir operations are exclusive, anchored below the claimed root."""
    need(target_custody is not None or REAL_EFFECT_ENABLED,
         'unclaimed stage directory creation disabled')
    if target_custody is not None:
        need(isinstance(target_custody, FixtureTargetCustody) and
             Path(stage_root) == target_custody.attempt / 'root' and
             target_custody.attempt.parent == Path('/tmp') and
             target_custody.attempt.name.startswith(
                 'cal-context-stage-fixture-cal-context-stage-fixture-test-'),
             'stage directory target outside claimed fixture envelope')
    dirs = expected_dirs(names)
    for name in sorted(dirs, key=lambda x: (x.count('/'), x)):
        parts = name.split('/')
        owned = [] if target_custody is not None else root_fds(stage_root)
        primary = None
        try:
            parent = descend(target_custody.root_fd if target_custody is not None
                             else owned[-1], parts[:-1], owned)
            if target_custody is not None:
                target_custody.check_attachment()
            os.mkdir(parts[-1], 0o700, dir_fd=parent)
            child = os.open(parts[-1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                            os.O_CLOEXEC, dir_fd=parent)
            owned.append(child)
            need(stat.S_ISDIR(os.fstat(child).st_mode), 'created stage directory differs')
            os.fsync(parent)
            if target_custody is not None:
                target_custody.check_attachment()
        except BaseException as exc:
            primary = exc
        cleanup = close_all_once(owned)
        if primary or cleanup:
            raise Poisoned(primary, cleanup, stage_root, None) from primary
    return dirs


def verify_namespace(stage_root, rows, *, target_custody=None):
    names = {x['path'] for x in rows}; dirs = expected_dirs(names)
    observed_files = set(); observed_dirs = set()
    owned = [] if target_custody is not None else root_fds(stage_root)
    primary = None
    try:
        if target_custody is not None:
            target_custody.check_attachment()
        for base, children, files, dirfd in os.fwalk('.', topdown=True, follow_symlinks=False,
                dir_fd=target_custody.root_fd if target_custody is not None else owned[-1]):
            prefix = '' if base == '.' else base[2:] + '/'
            for child in children:
                rel = prefix + child
                st = os.stat(child, dir_fd=dirfd, follow_symlinks=False)
                need(stat.S_ISDIR(st.st_mode) and st.st_nlink >= 2 and rel in dirs,
                     'stage directory namespace differs')
                observed_dirs.add(rel)
            for leaf in files:
                rel = prefix + leaf
                st = os.stat(leaf, dir_fd=dirfd, follow_symlinks=False)
                need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and rel in names,
                     'stage file namespace differs')
                observed_files.add(rel)
        need(observed_files == names and observed_dirs == dirs,
             'stage missing or surplus names')
        for row in rows:
            info = held_measure(target_custody.root_fd if target_custody is not None
                                else stage_root, row['path'], row['sha256'], row['size'],
                                row['mode'], MAX_PRIVATE if row.get('protected') else MAX_NATIVE)
            need(info['uid'] == os.geteuid() and info['gid'] == os.getegid(),
                 'postcopy owner differs')
        if target_custody is not None:
            target_custody.check_attachment()
    except BaseException as exc:
        primary = exc
    cleanup = close_all_once(owned)
    if primary or cleanup:
        raise Poisoned(primary, cleanup, stage_root, None) from primary
    return {'files': len(observed_files), 'directories': len(observed_dirs),
            'private_digest_checked': sum(x.get('protected', False) for x in rows)}


def claim_attempt(attempt, *, real=False):
    """Never rerun: even an empty or failed attempt name is terminal."""
    attempt = Path(attempt)
    if real:
        need(REAL_EFFECT_ENABLED and attempt == REAL_ATTEMPT,
             'exact real attempt disabled')
    else:
        need(attempt.is_absolute() and attempt.name.startswith('cal-context-stage-fixture-')
             and attempt.parent == Path('/tmp'), 'disposable fixture attempt required')
    owned = root_fds(attempt.parent)
    primary = None; created = None
    try:
        os.mkdir(attempt.name, 0o700, dir_fd=owned[-1])
        child = os.open(attempt.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                        os.O_CLOEXEC, dir_fd=owned[-1])
        owned.append(child)
        created = inode(os.fstat(child))
        os.fsync(owned[-2])
        need(inode(os.stat(attempt.name, dir_fd=owned[-2], follow_symlinks=False)) == created,
             'attempt name replaced')
    except BaseException as exc:
        primary = exc
    cleanup = close_all_once(owned)
    if primary or cleanup:
        raise Poisoned(primary, cleanup, attempt, created) from primary
    return created


def reserve_fixture_once(source_custody, attempt):
    """Durable no-retry marker outside a movable attempt, in owned fixture parent."""
    source_custody.check_attachment()
    parent = source_custody.owned[-2]
    record = {'schema_version': 'lab-context-stage-fixture-one-shot/v1',
              'attempt': str(attempt),
              'source_root_inode': source_custody.baseline[-1][:2],
              'status': 'RESERVED_NO_RETRY'}
    raw = (json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode()
    fd = os.open(FIXTURE_CLAIM_MARKER,
                 os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=parent)
    primary = None; created = inode(os.fstat(fd))
    try:
        view = memoryview(raw)
        while view:
            count = os.write(fd, view)
            need(type(count) is int and count > 0, 'fixture claim marker write stalled')
            view = view[count:]
        os.fsync(fd)
        os.fsync(parent)
        need(inode(os.stat(FIXTURE_CLAIM_MARKER, dir_fd=parent,
                           follow_symlinks=False)) == created,
             'fixture claim marker detached')
        source_custody.check_attachment()
    except BaseException as exc:
        primary = exc
    cleanup = []
    try:
        _close_once(fd)
    except BaseException as exc:
        cleanup.append((fd, repr(exc)))
    if primary or cleanup:
        raise Poisoned(primary, cleanup, attempt, None, claim_marker_path=
                       source_custody.root.parent / FIXTURE_CLAIM_MARKER) from primary
    return sha(raw)


def claim_fixture_target(attempt, source_custody):
    """No-replace disposable attempt; hold its root through every target write."""
    attempt = Path(attempt)
    need(isinstance(source_custody, FixtureCustody), 'held fixture source required')
    source_root = source_custody.root
    need(attempt == Path('/tmp') /
         ('cal-context-stage-fixture-' + Path(source_root).parent.name),
         'attempt/source fixture identity differs')
    reserve_fixture_once(source_custody, attempt)
    owned = root_fds(Path('/tmp')); primary = None; created = None
    try:
        os.mkdir(attempt.name, 0o700, dir_fd=owned[-1])
        attempt_fd = os.open(attempt.name, os.O_RDONLY | os.O_DIRECTORY |
                             os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=owned[-1])
        owned.append(attempt_fd)
        created = inode(os.fstat(attempt_fd))
        os.fsync(owned[-2])
        need(inode(os.stat(attempt.name, dir_fd=owned[-2],
                           follow_symlinks=False)) == created,
             'exclusive attempt name detached')
        os.mkdir('root', 0o700, dir_fd=attempt_fd)
        root_fd = os.open('root', os.O_RDONLY | os.O_DIRECTORY |
                          os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=attempt_fd)
        owned.append(root_fd)
        os.fsync(attempt_fd)
        need(stat.S_ISDIR(os.fstat(root_fd).st_mode) and
             inode(os.stat('root', dir_fd=attempt_fd,
                           follow_symlinks=False)) == inode(os.fstat(root_fd)),
             'exclusive stage root detached')
        custody = FixtureTargetCustody(attempt, owned)
        custody.check_attachment()
        return custody
    except BaseException as exc:
        primary = exc
    cleanup = close_all_once(owned)
    raise Poisoned(primary, cleanup, attempt, created) from primary


def mkdir_held(parent_path, leaf):
    need(REAL_EFFECT_ENABLED, 'real stage directory creation disabled')
    need(type(leaf) is str and leaf and '/' not in leaf and leaf not in ('.', '..'),
         'unsafe directory leaf')
    owned = root_fds(parent_path); primary = None; created = None
    try:
        os.mkdir(leaf, 0o700, dir_fd=owned[-1])
        fd = os.open(leaf, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
                     os.O_CLOEXEC, dir_fd=owned[-1])
        owned.append(fd)
        created = inode(os.fstat(fd))
        os.fsync(owned[-2])
        need(inode(os.stat(leaf, dir_fd=owned[-2], follow_symlinks=False)) == created,
             'new directory name detached')
    except BaseException as exc:
        primary = exc
    cleanup = close_all_once(owned)
    if primary or cleanup:
        raise Poisoned(primary, cleanup, parent_path, created) from primary
    return created


def terminal_receipt(attempt, value):
    need(REAL_EFFECT_ENABLED, 'real stage receipt creation disabled')
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    need(len(raw) <= 64*1024, 'terminal receipt exceeds bound')
    owned = root_fds(attempt); primary = None; leaf = 'stage-receipt.json'; created = None
    try:
        fd = os.open(leaf, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
                     os.O_CLOEXEC, 0o600, dir_fd=owned[-1])
        owned.append(fd)
        created = inode(os.fstat(fd))
        view = memoryview(raw)
        while view:
            count = os.write(fd, view)
            need(type(count) is int and count > 0, 'terminal receipt write stalled')
            view = view[count:]
        os.fsync(fd)
        os.fsync(owned[-2])
        need(inode(os.stat(leaf, dir_fd=owned[-2], follow_symlinks=False)) == created,
             'terminal receipt name detached')
    except BaseException as exc:
        primary = exc
    cleanup = close_all_once(owned)
    if primary or cleanup:
        raise Poisoned(primary, cleanup, attempt, created) from primary
    return sha(raw)


def _materialize_exact_after_future_authority(selected, rows, native):
    """Frozen implementation sketch, unreachable until a reviewed effect adapter.

    The future adapter must prove current Source scope, time, same UID/GID and
    exact policy/grant before enabling this call. The stage alone cannot supply
    those authorities or make a Context launch claim.
    """
    need(REAL_EFFECT_ENABLED, 'real stage effect disabled')
    need(len(rows) == 1570 and sum(x.get('protected', False) for x in rows) == 1
         and selected['future_exclusive_stage_root'] == str(REAL_ATTEMPT / 'root'),
         'exact reviewed stage selection required')
    attempt_inode = claim_attempt(REAL_ATTEMPT, real=True)
    stage = REAL_ATTEMPT / 'root'
    try:
        mkdir_held(REAL_ATTEMPT, 'root')
        mkdir_held(REAL_ATTEMPT, 'input')
        create_dirs(stage, [x['path'] for x in rows])
        # No protected archive FD is opened before the exclusive attempt claim.
        for row in rows:
            _copy_one_core(row, stage, allow_protected=True)
        verified = verify_namespace(stage, rows)
        _copy_one_core(native, REAL_ATTEMPT, allow_protected=True)
        native_post = held_measure(REAL_ATTEMPT, native['path'], native['sha256'],
                                   native['size'], native['mode'], MAX_NATIVE)
        need(verified['files'] == 1570 and
             verified['directories'] == len(expected_dirs(x['path'] for x in rows)) and
             verified['private_digest_checked'] == 1 and
             native_post['uid'] == os.geteuid() and native_post['gid'] == os.getegid(),
             'complete staged namespace/native proof differs')
        receipt = {'schema_version': 'lab-context-stage-effect-receipt/v1-candidate',
                   'status': 'STAGE_MATERIALIZED_ONLY', 'attempt': str(REAL_ATTEMPT),
                   'attempt_inode': attempt_inode, 'selected_stage_sha256': SELECTION_SHA,
                   'stage_files': 1570, 'stage_directories': verified['directories'],
                   'protected_archive_sha256':
                       selected['protected_archive_metadata']['sha256'],
                   'protected_body_read': True, 'protected_body_copied': True,
                   'native_sha256': native['sha256'], 'context_launch': 'REFUSED'}
        digest = terminal_receipt(REAL_ATTEMPT, receipt)
        return {'status': receipt['status'], 'receipt_sha256': digest,
                'attempt_inode': attempt_inode}
    except BaseException as exc:
        # No name-based cleanup: a failed attempt is permanently retained.
        raise Poisoned(exc, [], REAL_ATTEMPT, attempt_inode) from exc


def run_fixture(attempt, rows, *, fault=None):
    """Public fixture only; retained attempt is the final evidence on failure."""
    need(os.getuid() == os.geteuid() and os.getgid() == os.getegid(),
         'split real/effective identity')
    need(type(rows) is list and rows and all(type(x) is dict and
         not x.get('protected') for x in rows),
         'fixture rows only')
    names = [valid_name(x['path']) for x in rows]
    need(len(names) == len(set(names)), 'fixture duplicate path')
    source = Path(rows[0]['source_root'])
    for row in rows:
        need(row['path'] != ARCHIVE and valid_name(row['source_name']) != ARCHIVE,
             'protected archive path refused before attempt claim')
        need(Path(row['source_root']) == source, 'mixed fixture source roots refused')
    custody = acquire_fixture_source(source, attempt)
    target = None; owned = None; primary = None; result = None
    stage = Path(attempt) / 'root'
    try:
        custody.check_attachment()
        target = claim_fixture_target(attempt, custody)
        owned = target.attempt_inode
        dirs = create_dirs(stage, names, target_custody=target)
        copies = [_copy_one_core(row, stage, fault=fault, custody=custody,
                                 target_custody=target)
                  for row in rows]
        verified = verify_namespace(stage, rows, target_custody=target)
        custody.check_attachment()
        target.check_attachment()
        result = {'status': 'PASS_FIXTURE', 'attempt_inode': owned,
                  'files': verified['files'], 'directories': len(dirs),
                  'copied_sha256': sha(json.dumps(copies, sort_keys=True).encode()),
                  'profile': 'TRUSTED_SINGLE_WRITER_DISPOSABLE_FIXTURE',
                  'adversarial_same_uid_write_envelope': 'NOT_CLAIMED',
                  'protected_body': 'ABSENT', 'context_launch': 'REFUSED'}
    except BaseException as exc:
        primary = exc
        if owned is None and isinstance(exc, Poisoned):
            owned = exc.owned_inode
    observed_name = None
    if primary is not None and owned is not None:
        try:
            observed_name = inode(os.stat(attempt, follow_symlinks=False))
        except FileNotFoundError:
            pass
        except BaseException as exc:
            primary = Poisoned(primary, [('attempt-name-observation', repr(exc))],
                               attempt, owned)
    cleanup = (target.close() if target is not None else []) + custody.close()
    if primary or cleanup:
        raise Poisoned(primary, cleanup, attempt, owned, observed_name,
                       source.parent / FIXTURE_CLAIM_MARKER) from primary
    return result


def real_stage(*_args, **_kwargs):
    # This constant is frozen false. A later independently reviewed disjoint
    # effect adapter must perform authorization, fresh period and full preflight,
    # claim exact attempt, then invoke the engine under that authority.
    need(REAL_EFFECT_ENABLED, 'real Context stage effect disabled')
    raise Refused('fresh Source/JIT authority and topology amendment absent')


def launch_context(*_args, **_kwargs):
    raise Refused('Context launch disabled')


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight-public']:
        selection, manifest = closed_selection()
        bound = preflight_public(manifest)
        native = native_binding(selection)
        print(json.dumps({'status': 'EFFECT_DISABLED', 'rows': len(bound),
                          'public_rehashed': len(bound)-1,
                          'native_sha256': native['sha256'],
                          'protected_body': 'UNOPENED', 'context_launch': 'REFUSED'},
                         sort_keys=True))
    else:
        real_stage()
