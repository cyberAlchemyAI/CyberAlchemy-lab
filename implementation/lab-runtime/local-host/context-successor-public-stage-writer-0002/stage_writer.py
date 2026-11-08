"""Effect-disabled, one-shot writer for the selected 1,570-row Context stage.

Import and preflight do not write. The only public production entrypoint stays
disabled until a separate exact freeze and independent effect review.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
HERE = Path(__file__).resolve().parent
SELECTOR_DIR = LOCAL / 'context-successor-final-stage-0004'
SELECTOR = SELECTOR_DIR / 'final_stage.py'
SELECTOR_SHA = '559d2b2255293deceb4bee862cfcb4f04c23a7159277ad8952994a20bbbd2668'
SELECTOR_FREEZE = SELECTOR_DIR / 'freeze.json'
SELECTOR_FREEZE_SHA = 'b96908371b064fa0fd90e398a8dfbe3023cf83cb99175dacb3393d08f02ed984'
SELECTOR_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-FINAL-STAGE-INDEPENDENT-STATIC-REVIEW-0004.md'
SELECTOR_REVIEW_SHA = '44d9681c9b1eefa4f28479e4a27133428c6d735c4f32325203dbd80e2a1d12f6'
PLAN_DIR = LOCAL / 'context-successor-stage-jit-release-plan-0002'
PLAN_FREEZE = PLAN_DIR / 'freeze.json'
PLAN_FREEZE_SHA = '8569cfc5593de49ebe19484cc25b64a78f04250175a3833c46d5471d8d37e17f'
PLAN_CODE = PLAN_DIR / 'release_plan.py'
PLAN_CODE_SHA = '1e403bdee4eb38da88ca8463e607ba923965117d48dc3419b60f6a000cc9c090'
PLAN_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-STAGE-JIT-RELEASE-PLAN-INDEPENDENT-STATIC-REVIEW-0002.md'
PLAN_REVIEW_SHA = '08cbff29bdebc93b63d2cf4930a0bfcca5fb24f80ec37cc474f9dd0d9aa8840d'
JIT_FREEZE = LOCAL / 'context-successor-jit-0002/freeze.json'
JIT_FREEZE_SHA = '06501e59f66afcec5ff360750bec142b7293abdcb82d418f4800d9fd965b6136'
JIT_REVIEW = LOCAL / 'CONTEXT-SUCCESSOR-JIT-INDEPENDENT-STATIC-REVIEW-0002.md'
JIT_REVIEW_SHA = '5a01e697c80beb877777c8c722d1c027922924ebab44ec5c8546add6a96cc081'
FAMILY = Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001')
ATTEMPT = FAMILY / 'context-attempt'
ROOT = ATTEMPT / 'root'
EFFECT_ENABLED = False
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
READ_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
MAX_FILE = 64 * 1024 * 1024
ALLOWED_MODES = {0o444, 0o600, 0o644}


class Refused(RuntimeError):
    pass


class Unknown(Refused):
    def __init__(self, cause, attempt, claimed):
        self.primary = cause
        self.attempt = str(attempt)
        self.claimed = claimed
        self.retry_allowed = False
        self.status = 'UNKNOWN_PRESERVE_NO_RETRY'
        super().__init__('stage outcome unknown; retain attempt and never retry')


def need(ok, code):
    if not ok:
        raise Refused(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def ident(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid,
            st.st_nlink, st.st_size)


def dir_id(st):
    return (st.st_dev, st.st_ino, st.st_mode, st.st_uid, st.st_gid)


def close_all(fds, primary=None):
    errors = []
    for fd in reversed(fds):
        try:
            os.close(fd)
        except BaseException as exc:
            errors.append((fd, exc))
    if errors and primary is not None:
        primary.secondary_close_errors = getattr(primary, 'secondary_close_errors', ()) + tuple(errors)
        primary.add_note('secondary owned descriptor close failures retained')
    elif errors:
        raise BaseExceptionGroup('owned descriptor close uncertain', [exc for _, exc in errors])


@contextmanager
def held_dir(path):
    path = Path(path)
    need(path.is_absolute() and all(part not in ('.', '..') for part in path.parts), 'ABSOLUTE_DIR')
    fds = []
    primary = None
    try:
        fds.append(os.open('/', DIR_FLAGS))
        for part in path.parts[1:]:
            fds.append(os.open(part, DIR_FLAGS, dir_fd=fds[-1]))
        ids = tuple(dir_id(os.fstat(fd)) for fd in fds)
        need(all(owner in (0, os.getuid()) and not(mode & 0o022)
                 for _, _, mode, owner, _ in ids), 'UNTRUSTED_DIR_CHAIN')
        yield fds[-1], ids
        need(tuple(dir_id(os.fstat(fd)) for fd in fds) == ids, 'HELD_DIR_CHANGED')
    except BaseException as exc:
        primary = exc
        raise
    finally:
        close_all(fds, primary)


def reattach(path, ids):
    with held_dir(path) as (_fd, actual):
        need(actual == ids, 'DIR_DETACHED')


def pinned(path, expected, maximum=2*1024*1024):
    path = Path(path)
    with held_dir(path.parent) as (parent, ids):
        fd = os.open(path.name, READ_FLAGS, dir_fd=parent)
        primary = None
        try:
            before = os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                 0 < before.st_size <= maximum, 'PIN_SHAPE')
            raw = bytearray()
            while len(raw) <= before.st_size:
                block = os.read(fd, min(65536, before.st_size + 1 - len(raw)))
                if not block:
                    break
                raw.extend(block)
            need(len(raw) == before.st_size and ident(os.fstat(fd)) == ident(before) and
                 sha(raw) == expected, 'PIN_DRIFT')
            result = bytes(raw)
        except BaseException as exc:
            primary = exc
            raise
        finally:
            close_all([fd], primary)
    reattach(path.parent, ids)
    return result


def selected():
    # Execute only one checked source buffer, not a second pathname import.
    raw = pinned(SELECTOR, SELECTOR_SHA)
    selector_freeze = json.loads(pinned(SELECTOR_FREEZE, SELECTOR_FREEZE_SHA))
    need(selector_freeze['members']['final_stage.py'] == SELECTOR_SHA and
         selector_freeze['effect_enabled'] is False and
         selector_freeze['mapper_effect_review_sha256'] ==
         '5676b6b6ea2d45981ea9db637cde240a86a94983afc3411ee2eb3287e9c6b13f',
         'SELECTOR_FREEZE_CONTRACT')
    for name, digest in selector_freeze['members'].items():
        pinned(SELECTOR_DIR/name, digest)
    pinned(SELECTOR_REVIEW, SELECTOR_REVIEW_SHA)
    plan_freeze = json.loads(pinned(PLAN_FREEZE, PLAN_FREEZE_SHA))
    need(plan_freeze['effect_enabled'] is False and
         plan_freeze['bindings']['release_plan.py'] == PLAN_CODE_SHA,
         'STAGE_JIT_PLAN_FREEZE_CONTRACT')
    for name, digest in plan_freeze['bindings'].items():
        pinned(PLAN_DIR/name, digest)
    pinned(PLAN_REVIEW, PLAN_REVIEW_SHA)
    pinned(JIT_FREEZE, JIT_FREEZE_SHA)
    pinned(JIT_REVIEW, JIT_REVIEW_SHA)
    plan_raw = pinned(PLAN_CODE, PLAN_CODE_SHA)
    plan = types.ModuleType('selected_stage_jit_plan_0002')
    plan.__file__ = str(PLAN_CODE)
    exec(compile(plan_raw, plan.__file__, 'exec'), plan.__dict__)
    plan.checked_sequence(plan.SEQUENCE)
    need(plan.SEQUENCE.index('EXCLUSIVELY_CREATE_STAGE_ROOT_AS_CONSUMED_ATTEMPT_CLAIM') <
         plan.SEQUENCE.index('WRITE_CLOSE_AND_FSYNC_DURABLE_NO_RETRY_MARKER_BEFORE_STAGE_CONTENT') <
         plan.SEQUENCE.index('COPY_EXACT_1570_FILES_WITH_HASH_MODE_AND_HELD_READBACK'),
         'REVIEWED_STAGE_SEQUENCE')
    selector = types.ModuleType('selected_context_final_stage_0004')
    selector.__file__ = str(SELECTOR)
    exec(compile(raw, selector.__file__, 'exec'), selector.__dict__)
    result = selector.select_after_mapper()
    need(result['effect_enabled'] is False and result['bound_file_count'] == 1570 and
         len(result['bound_rows']) == 1570 and result['final_count_with_auth'] == 1571 and
         result['auth_placeholder']['sha256'] == 'UNMINTED_UNSELECTED' and
         result['stage_copy'] == result['docker_effect'] == 'REFUSED' and
         result['topology']['stage_root'] == str(ROOT), 'SELECTED_STAGE_PLAN')
    return selector, result


def path_ok(relative):
    return (type(relative) is str and relative and not relative.startswith('/') and
            all(part not in ('', '.', '..') for part in relative.split('/')) and
            len(relative) <= 512)


def source_rows(selector, result):
    """Resolve fixed physical sources; projected bytes never read from a pathname."""
    pre = selector.source_reader_preflight()
    context, jit = pre['context_selector'], pre['jit']
    api = context.project_api(result['pins'])
    context_files = context.project_context(result['pins'], sha(api['contract-profile.json']),
                                            pre['reader_code_sha256'])
    context_files['build.py'] = jit.rebind_guarded_build(context_files['build.py'])
    generated = {selector.API_ROLE+'/'+name: raw for name, raw in api.items()}
    generated.update({selector.CONTEXT_ROLE+'/'+name: raw for name, raw in context_files.items()})
    mapper_root = selector.DOCKER_ATTEMPT.parent/'root'
    roots = {'reviewed_reader_stage_metadata': selector.READER_STAGE/'root',
             'original_public_checkout': selector.REPO,
             'actual_reviewed_mapper_role': mapper_root,
             'actual_reviewed_mapper_package': mapper_root}
    rows = []
    for row in result['bound_rows']:
        name = row['path']
        need(path_ok(name) and type(row['sha256']) is str and len(row['sha256']) == 64,
             'ROW_SHAPE')
        mode = int(row['mode'], 8)
        need(mode in ALLOWED_MODES, 'ROW_MODE')
        if row['source'] in roots:
            source = roots[row['source']]/name
            source_mode = 0o600 if row['source'] == 'actual_reviewed_mapper_package' else mode
            rows.append(dict(row, source_path=source, source_mode=source_mode))
        else:
            need(name in generated and row['source'] in
                 ('in_memory_api_projection', 'in_memory_guarded_context_projection'),
                 'GENERATED_SOURCE')
            raw = generated[name]
            need(type(raw) is bytes and sha(raw) == row['sha256'], 'GENERATED_PIN')
            rows.append(dict(row, raw=raw))
    need(len(rows) == 1570 and len(generated) == 12, 'ROW_CLOSURE')
    return rows


def directory_modes(rows):
    modes = {}
    for row in rows:
        parts = row['path'].split('/')
        for n in range(1, len(parts)):
            rel = '/'.join(parts[:n])
            selected = 0o755
            if 'source_path' in row:
                root = row['source_path']
                for _ in range(len(parts)-n):
                    root = root.parent
                st = os.stat(root, follow_symlinks=False)
                need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid(), 'SOURCE_DIR_SHAPE')
                selected = stat.S_IMODE(st.st_mode)
                need(selected in (0o700, 0o755), 'SOURCE_DIR_MODE')
            if rel in modes:
                need(modes[rel] == selected or 'source_path' not in row,
                     'DIRECTORY_MODE_CONFLICT')
            else:
                modes[rel] = selected
    return modes


def precheck_sources(rows):
    """Hash public selected sources; inspect 0600 source leaves by metadata only.

    The preceding selector opens 55 mapped-package buffers, separately.
    """
    public_hashed = 0
    owner_only_metadata = 0
    for row in rows:
        if 'raw' in row:
            need(sha(row['raw']) == row['sha256'], 'PRE_PROJECTED_PIN')
            continue
        source = row['source_path']
        with held_dir(source.parent) as (parent, _ids):
            st = os.stat(source.name, dir_fd=parent, follow_symlinks=False)
            need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
                 st.st_uid == os.getuid() and
                 stat.S_IMODE(st.st_mode) == row['source_mode'] and
                 st.st_size <= MAX_FILE, 'PRE_SOURCE_SHAPE')
        if row['source_mode'] == 0o600:
            owner_only_metadata += 1
        else:
            pinned(source, row['sha256'], MAX_FILE)
            public_hashed += 1
    return {'public_hashed':public_hashed,
            'owner_only_metadata_only':owner_only_metadata}


@contextmanager
def claimed_child(parent, name, mode, *, on_created=None, after_mkdir=None):
    """Keep the exact newly named directory inode until its caller finishes."""
    need(type(name) is str and name not in ('', '.', '..') and '/' not in name and
         mode in (0o700, 0o755), 'CLAIM_SHAPE')
    os.mkdir(name, mode, dir_fd=parent)
    if on_created is not None:
        on_created()
    original = os.stat(name, dir_fd=parent, follow_symlinks=False)
    need(stat.S_ISDIR(original.st_mode) and original.st_uid == os.getuid(),
         'CLAIM_ORIGINAL_SHAPE')
    if after_mkdir is not None:
        after_mkdir()
    child = None
    primary = None
    try:
        child = os.open(name, DIR_FLAGS, dir_fd=parent)
        need(dir_id(os.fstat(child)) == dir_id(original), 'CLAIM_INODE_REPLACED')
        os.fchmod(child, mode)
        os.fsync(child)
        os.fsync(parent)
        expected = dir_id(os.fstat(child))
        need(stat.S_IMODE(expected[2]) == mode, 'CLAIM_MODE')
        attached(parent, name, child, expected)
        yield child, expected
        attached(parent, name, child, expected)
    except BaseException as exc:
        primary = exc
        raise
    finally:
        if child is not None:
            close_all([child], primary)


def attached(parent, name, child, expected):
    need(dir_id(os.fstat(child)) == expected and
         dir_id(os.stat(name, dir_fd=parent, follow_symlinks=False)) == expected,
         'CLAIM_DETACHED')


@contextmanager
def relative_parent(rootfd, relative, directory_ids):
    """Traverse only retained, joined descendants of the original root FD."""
    need(path_ok(relative), 'RELATIVE_PATH')
    parts = relative.split('/')
    opened = []
    primary = None
    parent = rootfd
    try:
        for depth, name in enumerate(parts[:-1], 1):
            rel = '/'.join(parts[:depth])
            expected = directory_ids[rel]
            child = os.open(name, DIR_FLAGS, dir_fd=parent)
            opened.append(child)
            attached(parent, name, child, expected)
            parent = child
        yield parent, parts[-1]
        for depth in range(len(opened), 0, -1):
            ancestor = rootfd if depth == 1 else opened[depth-2]
            attached(ancestor, parts[depth-1], opened[depth-1],
                     directory_ids['/'.join(parts[:depth])])
    except BaseException as exc:
        primary = exc
        raise
    finally:
        close_all(opened, primary)


def write_new_at(parent, name, raw, mode):
    need(type(name) is str and name not in ('', '.', '..') and '/' not in name and
         type(raw) is bytes and len(raw) <= MAX_FILE and mode in ALLOWED_MODES,
         'HELD_WRITE_SHAPE')
    fd = os.open(name, WRITE_FLAGS, mode, dir_fd=parent)
    primary = None
    try:
        view = memoryview(raw)
        while view:
            n = os.write(fd, view)
            need(type(n) is int and n > 0, 'HELD_WRITE_STALLED')
            view = view[n:]
        os.fchmod(fd, mode)
        os.fsync(fd)
        written = os.fstat(fd)
        need(stat.S_ISREG(written.st_mode) and written.st_nlink == 1 and
             written.st_uid == os.getuid() and stat.S_IMODE(written.st_mode) == mode and
             written.st_size == len(raw), 'HELD_WRITE_SHAPE')
        check = os.open(name, READ_FLAGS, dir_fd=parent)
        check_error = None
        try:
            need(ident(os.fstat(check)) == ident(written), 'HELD_READBACK_ID')
            buf = bytearray()
            while len(buf) < len(raw):
                block = os.read(check, min(65536,len(raw)-len(buf)))
                need(bool(block), 'HELD_READBACK_SHORT')
                buf.extend(block)
            need(os.read(check,1) == b'' and sha(buf) == sha(raw) and
                 ident(os.fstat(check)) == ident(written), 'HELD_READBACK_BYTES')
        except BaseException as exc:
            check_error = exc
            raise
        finally:
            close_all([check], check_error)
        os.fsync(parent)
        need(ident(os.stat(name, dir_fd=parent, follow_symlinks=False)) ==
             ident(written), 'HELD_WRITE_DETACHED')
    except BaseException as exc:
        primary = exc
        raise
    finally:
        close_all([fd], primary)
    return sha(raw)


def copy_row_at(row, rootfd, directory_ids):
    with relative_parent(rootfd, row['path'], directory_ids) as (target_parent, name):
        if 'raw' in row:
            need(sha(row['raw']) == row['sha256'], 'PROJECTED_BYTES')
            return write_new_at(target_parent, name, row['raw'], int(row['mode'],8))
        source = Path(row['source_path'])
        with held_dir(source.parent) as (source_parent, source_chain):
            sfd = os.open(source.name, READ_FLAGS, dir_fd=source_parent)
            primary = None
            try:
                before = os.fstat(sfd)
                need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                     before.st_uid == os.getuid() and
                     stat.S_IMODE(before.st_mode) == row['source_mode'] and
                     before.st_size <= MAX_FILE, 'SOURCE_LEAF_SHAPE')
                out = os.open(name, WRITE_FLAGS, int(row['mode'],8), dir_fd=target_parent)
                out_error = None
                try:
                    digest = hashlib.sha256()
                    copied = 0
                    while True:
                        block = os.read(sfd, min(65536, before.st_size+1-copied))
                        if not block:
                            break
                        copied += len(block)
                        need(copied <= before.st_size, 'SOURCE_GROWTH')
                        digest.update(block)
                        view = memoryview(block)
                        while view:
                            n = os.write(out, view)
                            need(type(n) is int and n > 0, 'COPY_STALLED')
                            view = view[n:]
                    need(copied == before.st_size and digest.hexdigest() == row['sha256'] and
                         ident(os.fstat(sfd)) == ident(before), 'SOURCE_HASH_OR_ID')
                    os.fchmod(out, int(row['mode'],8))
                    os.fsync(out)
                    written = os.fstat(out)
                    need(stat.S_ISREG(written.st_mode) and written.st_nlink == 1 and
                         written.st_uid == os.getuid() and written.st_size == copied and
                         stat.S_IMODE(written.st_mode) == int(row['mode'],8), 'COPIED_SHAPE')
                    check = os.open(name, READ_FLAGS, dir_fd=target_parent)
                    check_error = None
                    try:
                        need(ident(os.fstat(check)) == ident(written), 'COPY_READBACK_ID')
                        verified = hashlib.sha256()
                        count = 0
                        while True:
                            block = os.read(check, min(65536, copied+1-count))
                            if not block:
                                break
                            count += len(block)
                            need(count <= copied, 'COPY_READBACK_GROWTH')
                            verified.update(block)
                        need(count == copied and verified.hexdigest() == row['sha256'] and
                             ident(os.fstat(check)) == ident(written), 'COPY_READBACK_HASH')
                    except BaseException as exc:
                        check_error = exc
                        raise
                    finally:
                        close_all([check], check_error)
                    os.fsync(target_parent)
                    need(ident(os.stat(name, dir_fd=target_parent,
                                       follow_symlinks=False)) == ident(written),
                         'COPY_DETACHED')
                except BaseException as exc:
                    out_error = exc
                    raise
                finally:
                    close_all([out], out_error)
            except BaseException as exc:
                primary = exc
                raise
            finally:
                close_all([sfd], primary)
        reattach(source.parent, source_chain)
    return row['sha256']


def verify_tree_at(rootfd, rows, dirs, directory_ids):
    expected = {row['path']: row for row in rows}
    seen_files, seen_dirs = set(), set()
    for base, children, files, dirfd in os.fwalk('.', topdown=True,
            follow_symlinks=False, dir_fd=rootfd):
        prefix = '' if base == '.' else base[2:]+'/'
        for name in children:
            relative = prefix+name
            st = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
            need(relative in dirs and stat.S_ISDIR(st.st_mode) and
                 st.st_uid == os.getuid() and stat.S_IMODE(st.st_mode) == dirs[relative] and
                 dir_id(st) == directory_ids[relative], 'TREE_DIR')
            seen_dirs.add(relative)
        for name in files:
            relative = prefix+name
            st = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
            need(relative in expected and stat.S_ISREG(st.st_mode) and
                 st.st_nlink == 1 and st.st_uid == os.getuid() and
                 stat.S_IMODE(st.st_mode) == int(expected[relative]['mode'],8),
                 'TREE_FILE')
            seen_files.add(relative)
    need(seen_files == set(expected) and seen_dirs == set(dirs), 'TREE_CLOSURE')
    os.fsync(rootfd)
    for row in rows:
        with relative_parent(rootfd, row['path'], directory_ids) as (parent, name):
            fd = os.open(name, READ_FLAGS, dir_fd=parent)
            primary = None
            try:
                before = os.fstat(fd)
                need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                     before.st_uid == os.getuid() and
                     stat.S_IMODE(before.st_mode) == int(row['mode'],8) and
                     before.st_size <= MAX_FILE, 'TREE_LEAF')
                digest = hashlib.sha256()
                count = 0
                while True:
                    block = os.read(fd, min(65536, before.st_size+1-count))
                    if not block:
                        break
                    count += len(block)
                    need(count <= before.st_size, 'TREE_GROWTH')
                    digest.update(block)
                need(count == before.st_size and digest.hexdigest() == row['sha256'] and
                     ident(os.fstat(fd)) == ident(before) and
                     ident(os.stat(name, dir_fd=parent, follow_symlinks=False)) ==
                     ident(before), 'TREE_HASH_OR_ID')
            except BaseException as exc:
                primary = exc
                raise
            finally:
                close_all([fd], primary)
    return {'files':len(seen_files), 'directories':len(seen_dirs)}


def postcheck_sources(rows):
    for row in rows:
        if 'raw' in row:
            need(sha(row['raw']) == row['sha256'], 'POST_PROJECTED_PIN')
        else:
            source = row['source_path']
            with held_dir(source.parent) as (parent, _ids):
                st = os.stat(source.name, dir_fd=parent, follow_symlinks=False)
                need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
                     st.st_uid == os.getuid() and
                     stat.S_IMODE(st.st_mode) == row['source_mode'],
                     'POST_SOURCE_MODE')
            pinned(source, row['sha256'], MAX_FILE)


def stage_once(attempt, rows, dirs, plan_sha, *, fixture=False, fault=None):
    attempt = Path(attempt)
    if fixture:
        need(attempt.parent == Path(__file__).resolve().parent and
             attempt.name.startswith('fixture-') and
             all(row.get('source_mode') != 0o600 and
                 not row['path'].endswith('/branch.snapshot') for row in rows),
             'FIXTURE_SCOPE')
    else:
        need(EFFECT_ENABLED is True and attempt == ATTEMPT and len(rows) == 1570,
             'STAGE_EFFECT_DISABLED')
    need(type(rows) is list and rows and len({r['path'] for r in rows}) == len(rows) and
         all(path_ok(r['path']) for r in rows) and
         type(plan_sha) is str and len(plan_sha) == 64, 'STAGE_ROWS')
    claimed = False
    try:
        with held_dir(attempt.parent) as (family_fd, family_chain):
            def mark_claimed():
                nonlocal claimed
                claimed = True
            def after_attempt_mkdir():
                if fault:
                    fault('after_attempt_mkdir')
            with claimed_child(family_fd, attempt.name, 0o700,
                    on_created=mark_claimed,
                    after_mkdir=after_attempt_mkdir) as (attempt_fd, attempt_id):
                def after_root_mkdir():
                    if fault:
                        fault('after_root_mkdir')
                with claimed_child(attempt_fd, 'root', 0o700,
                        after_mkdir=after_root_mkdir) as (rootfd, root_id):
                    def graph():
                        attached(family_fd, attempt.name, attempt_fd, attempt_id)
                        attached(attempt_fd, 'root', rootfd, root_id)
                        reattach(attempt.parent, family_chain)
                    graph()
                    write_new_at(attempt_fd, 'consumed.json', wire({
                        'schema':'context-successor-stage-consumed/v1',
                        'status':'CONSUMED_UNKNOWN_UNTIL_EXTERNAL_REVIEW',
                        'attempt':str(attempt),'plan_sha256':plan_sha,
                        'retry_allowed':False}), 0o600)
                    if fault:
                        fault('after_marker')
                    directory_ids = {}
                    for relative, mode in sorted(dirs.items(),
                            key=lambda item:(item[0].count('/'),item[0])):
                        graph()
                        with relative_parent(rootfd, relative, directory_ids) as (parent, name):
                            with claimed_child(parent, name, mode) as (_fd, expected):
                                directory_ids[relative] = expected
                        graph()
                    ordered = ([row for row in rows if not row['path'].endswith('/branch.snapshot')] +
                               [row for row in rows if row['path'].endswith('/branch.snapshot')])
                    for index, row in enumerate(ordered):
                        graph()
                        if fault:
                            fault('before_row', index)
                        graph()
                        copy_row_at(row, rootfd, directory_ids)
                        graph()
                        if fault:
                            fault('after_row', index)
                    verified = verify_tree_at(rootfd, rows, dirs, directory_ids)
                    postcheck_sources(rows)
                    graph()
                    write_new_at(attempt_fd, 'stage.provisional.json', wire({
                        'schema':'context-successor-stage-provisional/v1',
                        'status':'OBSERVED_STAGE_ONLY_PENDING_EXTERNAL_OS_REVIEW',
                        'attempt':str(attempt),'plan_sha256':plan_sha,
                        'files':verified['files'],'directories':verified['directories'],
                        'auth':'UNMINTED_UNSELECTED','retry_allowed':False}), 0o600)
                    graph()
                    return verified
    except BaseException as exc:
        if claimed:
            exc.add_note('original claimed attempt retained; no pathname UNKNOWN write')
        raise Unknown(exc, attempt, claimed) from exc


def preflight():
    selector, result = selected()
    rows = source_rows(selector, result)
    dirs = directory_modes(rows)
    source_checks = precheck_sources(rows)
    need(not os.path.lexists(ATTEMPT) and not os.path.lexists(ROOT), 'ATTEMPT_CONSUMED')
    with held_dir(FAMILY) as (family_fd, _ids):
        st = os.fstat(family_fd)
        need(st.st_uid == os.getuid() and stat.S_IMODE(st.st_mode) == 0o700,
             'FAMILY_OWNER_0700')
    return {'schema':'context-successor-public-stage-predispatch/v1',
            'status':'EFFECT_DISABLED_READY_FOR_INDEPENDENT_STATIC_REVIEW',
            'effect':'NOT_RUN','attempt':str(ATTEMPT),'stage_root':str(ROOT),
            'rows':len(rows),'directories':len(dirs),
            'source_checks':source_checks,
            'selection_reads':{'mapped_package_buffers':55,
                               'protected_source_archive_body':'UNOPENED'},
            'mapper_effect_review_sha256':result['mapper_effect_review_sha256'],
            'auth':result['auth_placeholder']['sha256'],
            'selector_freeze_sha256':SELECTOR_FREEZE_SHA,
            'selector_review_sha256':SELECTOR_REVIEW_SHA,
            'stage_jit_plan_freeze_sha256':PLAN_FREEZE_SHA,
            'stage_jit_plan_review_sha256':PLAN_REVIEW_SHA,
            'source_period_sha256':result['source_period_sha256']}


def run_effect():
    need(EFFECT_ENABLED is True, 'STAGE_EFFECT_DISABLED_PENDING_INDEPENDENT_REVIEW')
    selector, result = selected()
    rows = source_rows(selector, result)
    dirs = directory_modes(rows)
    precheck_sources(rows)
    need(not os.path.lexists(ATTEMPT), 'ATTEMPT_CONSUMED')
    plan_sha = sha(wire(result['bound_rows']))
    # Recheck Source currentness and all outside Mapper evidence before claim.
    need(selector.select_after_mapper()['bound_rows'] == result['bound_rows'],
         'SELECTED_ROWS_CHANGED')
    verified = stage_once(ATTEMPT, rows, dirs, plan_sha)
    # A later external observer must still establish OS0, no UNKNOWN, and full
    # independent stage effect review before downstream AUTH or Context.
    need(selector.select_after_mapper()['bound_rows'] == result['bound_rows'],
         'POST_STAGE_SELECTION_CHANGED')
    return {'status':'PROVISIONAL_STAGE_ONLY_EXTERNAL_OS_REVIEW_REQUIRED',
            'files':verified['files'],'directories':verified['directories'],
            'attempt':str(ATTEMPT),'retry_allowed':False}


def issue_authority(*_args, **_kwargs):
    raise Refused('AUTH_ISSUER_AND_SIGNED_SCOPE_DISABLED')


def create_private_key_or_policy(*_args, **_kwargs):
    raise Refused('PRIVATE_KEY_AND_POLICY_DISABLED')


def jit_or_docker(*_args, **_kwargs):
    raise Refused('JIT_AND_DOCKER_DISABLED')


if __name__ == '__main__':
    if sys.argv[1:] == ['--preflight']:
        print(json.dumps(preflight(), sort_keys=True, separators=(',', ':')))
    else:
        raise SystemExit('expected --preflight; effect disabled')
