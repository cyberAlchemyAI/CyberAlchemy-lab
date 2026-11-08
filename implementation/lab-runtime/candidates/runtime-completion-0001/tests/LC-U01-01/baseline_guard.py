"""Read-only authoring-baseline guard; supplies no runtime/custody authority."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess


def fail(message):
    raise ValueError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail('duplicate JSON key')
        result[key] = value
    return result


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_pairs)


def safe_relative(value):
    if not isinstance(value, str) or not value or '\x00' in value or '\\' in value:
        fail('unsafe path')
    if value.startswith('/') or any(x in ('', '.', '..') for x in value.split('/')):
        fail('unsafe path')
    return PurePosixPath(value)


def open_directory(path):
    path = Path(path)
    if not path.is_absolute():
        fail('absolute directory required')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except BaseException:
        os.close(fd)
        raise


def read_binding(root, row):
    if set(row) != {'path', 'sha256', 'size_bytes'}:
        fail('binding shape')
    rel = safe_relative(row['path'])
    if not isinstance(row['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', row['sha256']):
        fail('digest shape')
    if type(row['size_bytes']) is not int or row['size_bytes'] < 0:
        fail('size shape')
    parent = open_directory(Path(root) / rel.parent)
    try:
        fd = os.open(rel.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                fail('nonregular binding')
            digest = hashlib.sha256()
            size = 0
            while chunk := os.read(fd, 1024 * 1024):
                size += len(chunk)
                digest.update(chunk)
            after = os.fstat(fd)
            identity = lambda x: (x.st_dev, x.st_ino, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
            attached = os.stat(rel.name, dir_fd=parent, follow_symlinks=False)
            if identity(before) != identity(after) or (attached.st_dev, attached.st_ino) != (after.st_dev, after.st_ino):
                fail('input changed or detached during read')
            if digest.hexdigest() != row['sha256'] or size != row['size_bytes']:
                fail('selected source drift')
        finally:
            os.close(fd)
    finally:
        os.close(parent)


def verify_bindings(root, rows):
    seen = set()
    for row in rows:
        if row.get('path') in seen:
            fail('duplicate binding path')
        seen.add(row.get('path'))
        read_binding(root, row)
    return len(seen)


def witness(fd):
    s = os.fstat(fd)
    return {'device': s.st_dev, 'inode': s.st_ino, 'uid': s.st_uid,
            'gid': s.st_gid, 'mode': oct(stat.S_IMODE(s.st_mode))}


def verify_root(path, expected):
    fd = open_directory(path)
    try:
        if witness(fd) != expected:
            fail('owned root identity or permission changed')
    finally:
        os.close(fd)


def absent(path):
    path = Path(path)
    parent = open_directory(path.parent)
    try:
        try:
            os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            return
        raise FileExistsError('reserved target is no longer absent')
    finally:
        os.close(parent)


def exclusive_file(parent, name, content):
    """No replacement, plus data/name durability; caller owns parent."""
    if safe_relative(name).name != name:
        fail('single member name required')
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent)
    try:
        offset = 0
        while offset < len(content):
            offset += os.write(fd, content[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)
    os.fsync(parent)


def claim_pair(root, names, install_name, interpose=None):
    """Regression primitive: rejects ordinary collisions before either mkdir.

    A racing second-root collision preserves the first owned root. There is no
    cross-root atomicity or hostile peer exclusion claim. No automatic cleanup.
    """
    root = Path(root)
    for name in [*names, install_name]:
        if safe_relative(name).name != name:
            fail('single root name required')
        absent(root / name)
    parent = open_directory(root)
    created = []
    try:
        for name in names:
            if interpose:
                interpose(name)
            os.mkdir(name, 0o700, dir_fd=parent)
            created.append(name)
            os.fsync(parent)
    except BaseException as exc:
        exc.created_roots = created
        raise
    finally:
        os.close(parent)
    return created


def verify_current(root, baseline_path):
    root = Path(root)
    baseline = load(baseline_path)
    if baseline.get('schema_version') != 'lab-completion-authoring-baseline/v1' or baseline.get('selection_kind') != 'code':
        fail('inert authoring baseline required')
    if baseline.get('runtime_eligible') is not False or baseline.get('authority_effect') != 'none':
        fail('baseline cannot grant runtime authority')
    count = verify_bindings(root, baseline['selected_inputs'])
    head = subprocess.run(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=root,
                          capture_output=True, check=True, timeout=10).stdout.decode().strip()
    if head != baseline['git_head']:
        fail('HEAD drift')
    paths = load(root / baseline['paths_binding']['path'])
    read_binding(root, baseline['paths_binding'])
    for name in ('S', 'E'):
        verify_root(root / paths['roots'][name]['path'], paths['roots'][name]['identity'])
    absent(root / paths['roots']['I']['path'])
    return {'result': 'PASS', 'selected_inputs_verified': count, 'I_absent': True,
            'authority_effect': 'none', 'runtime_eligible': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--baseline', required=True)
    args = parser.parse_args()
    print(json.dumps(verify_current(args.root, args.baseline), sort_keys=True))
