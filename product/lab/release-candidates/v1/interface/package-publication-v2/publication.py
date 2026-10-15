"""Bounded package files in independently owned, immutable candidate generations.

This filesystem kernel grants no permission. Its callbacks must be supplied by
the actual authenticated host; fixture callbacks qualify filesystem behavior only.
It never accepts a caller path, admits artifacts, or replaces an uncertain output.
"""
import copy
import fcntl
import hashlib
import json
import importlib.util
import os
from pathlib import Path
import stat
import sys
from contextlib import contextmanager

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
TRANSFER = HERE.parent / 'package-transfer-v3'
TRANSFER_SOURCE = '72375558b7cf9205e559e0320aca2a5bfc6c971c9a89cf1d64b71205b5d2fcb1'


def load_transfer():
    manifest = json.loads((TRANSFER / 'source-manifest.json').read_bytes())
    if manifest['source_sha256'] != TRANSFER_SOURCE:
        raise ValueError('independent transfer source selection differs')
    original = json.dumps(manifest['files'] + manifest['input_bindings'], sort_keys=True,
        separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()
    if hashlib.sha256(original).hexdigest() != TRANSFER_SOURCE:
        raise ValueError('transfer source digest differs')
    for row in manifest['files'] + manifest['input_bindings']:
        path = ROOT / row['path']
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('transfer source bytes changed')
    spec = importlib.util.spec_from_file_location('_cal_managed_package_transfer_v3', TRANSFER / 'transfer.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


T = load_transfer()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(ref, raw):
    return {'ref': ref, 'sha256': sha(raw)}


def identity(info):
    return {'device': info.st_dev, 'inode': info.st_ino}


@contextmanager
def directory(path):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'independent absolute root required')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        info = os.fstat(fd)
        require(stat.S_IMODE(info.st_mode) == 0o700 and info.st_uid == os.getuid(), 'private owned root required')
        yield fd
    finally:
        os.close(fd)


def child_dir(fd, name):
    result = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
    try:
        info = os.fstat(result)
        require(stat.S_IMODE(info.st_mode) == 0o700 and info.st_uid == os.getuid(), 'private owned generation required')
        return result
    except BaseException:
        os.close(result)
        raise


def write(fd, name, raw):
    out = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        with os.fdopen(out, 'wb', closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(out)
    finally:
        os.close(out)


def read(fd, name, maximum):
    item = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    try:
        info = os.fstat(item)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.getuid()
                and stat.S_IMODE(info.st_mode) == 0o600 and info.st_size <= maximum, 'unsafe managed file')
        with os.fdopen(item, 'rb', closefd=False) as stream:
            raw = stream.read(maximum + 1)
        require(len(raw) <= maximum and len(raw) == info.st_size, 'managed file changed or exceeded bound')
        return raw
    finally:
        os.close(item)


class RecoveryRequired(RuntimeError):
    """An existing/reserved generation must be inspected; never redispatch writes."""


class Publisher:
    def __init__(self, root, scope_ref, root_identity, scope_binding, principal_ref,
                 transfer, source_guard, permission_guard, max_output_bytes, max_generations):
        self.root = Path(root)
        self.scope_ref, self.root_identity, self.scope_binding = scope_ref, copy.deepcopy(root_identity), copy.deepcopy(scope_binding)
        self.principal_ref, self.transfer = principal_ref, transfer
        require(type(transfer) is T.Transfer and transfer.source_pin == TRANSFER_SOURCE, 'actual independently selected transfer implementation required')
        self.source_guard, self.permission_guard = source_guard, permission_guard
        require(type(max_output_bytes) is int and 0 < max_output_bytes <= 64 * 1024 * 1024, 'independent output bound required')
        require(type(max_generations) is int and 0 < max_generations <= 64, 'independent generation count bound required')
        require(callable(source_guard) and callable(permission_guard), 'actual host callbacks required')
        require(type(scope_ref) is str and scope_ref and type(principal_ref) is str and principal_ref, 'independent scope and principal required')
        self.max_output_bytes, self.max_generations = max_output_bytes, max_generations

    def guard(self, root_fd):
        self.transfer.guard()
        self.source_guard()
        require(self.permission_guard() is True, 'current host permission refused')
        require(identity(os.fstat(root_fd)) == self.root_identity, 'opened root identity changed')
        # Also bind the current path; a held descriptor must not hide a root swap.
        with directory(self.root) as current:
            require(identity(os.fstat(current)) == self.root_identity, 'current root identity changed')
        raw = read(root_fd, '.scope.json', 1024 * 1024)
        self.transfer.bound(self.scope_binding, raw)
        expected = {'schema_version': 'lab-owned-package-root/v1-candidate', 'output_root': str(self.root),
            'output_root_scope_ref': self.scope_ref, 'principal_ref': self.principal_ref,
            'output_root_identity': self.root_identity, 'authority_effect': 'none', 'actual_owner_outcome': None}
        require(T.parse(raw) == expected, 'independent output root manifest differs')

    def describe(self, package_raw, package_binding, request_binding, source_cut):
        """Verify originals and derive the single expected publication record."""
        require(type(package_raw) is bytes and len(package_raw) <= self.max_output_bytes, 'bounded package output required')
        self.transfer.valid('urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding', request_binding)
        package = self.transfer.verify_archive(package_raw, package_binding)
        require(package['source_cut'] == source_cut, 'package source cut differs')
        selection = {'output_root_scope_ref': self.scope_ref, 'package_binding': package_binding,
                     'request_binding': request_binding, 'source_cut': source_cut}
        generation = 'pkg-' + sha(encoded(selection))
        generation_ref = self.scope_ref + '/generations/' + generation
        content = {'content_ref': generation_ref + '/package.json', 'byte_sha256': sha(package_raw),
                   'size_bytes': len(package_raw), 'media_type': 'application/json'}
        manifest = {'schema_version': 'lab-managed-package-manifest/v1-candidate', **selection,
                    'generation_ref': generation_ref, 'output_binding': content, 'authority_effect': 'none',
                    'actual_owner_outcome': None, 'canonical_replay_source': False}
        manifest_raw = encoded(manifest)
        receipt = {'schema_version': 'lab-file-materialization-receipt/v1-candidate', 'request_binding': request_binding,
            'manifest_binding': pin(generation_ref + '/manifest.json', manifest_raw), 'source_cut': source_cut,
            'generation_ref': generation_ref, 'posture': 'published', 'output_bindings': [content],
            'canonical_replay_source': False, 'unmanaged_files_overwritten': False, 'gaps': [],
            'claim_ceiling': 'Exact bytes published in this independently owned candidate generation; no source authority, import admission or host authentication is granted by this kernel.',
            'authority_effect': 'none', 'recovery_required': False}
        self.transfer.valid('urn:cyberalchemy-lab:protocol:file-materialization-receipt:v1-candidate', receipt)
        receipt_raw = encoded(receipt)
        marker = encoded({'schema_version': 'lab-package-publication-marker/v1-candidate',
            'package_sha256': sha(package_raw), 'manifest_sha256': sha(manifest_raw), 'receipt_sha256': sha(receipt_raw)})
        return generation, manifest_raw, receipt, receipt_raw, marker

    def publish(self, package_raw, package_binding, request_binding, source_cut, *, existing_only=False):
        package_binding, request_binding, source_cut = copy.deepcopy((package_binding, request_binding, source_cut))
        require(type(existing_only) is bool, 'explicit retry posture required')
        generation, manifest_raw, receipt, receipt_raw, marker = self.describe(
            package_raw, package_binding, request_binding, source_cut)
        started = existing_only
        try:
            with directory(self.root) as root:
                self.guard(root)
                fcntl.flock(root, fcntl.LOCK_EX | fcntl.LOCK_NB)
                names = set(os.listdir(root))
                require(all(name == '.scope.json' or name.startswith('pkg-') and len(name) == 68
                    and all(c in '0123456789abcdef' for c in name[4:]) for name in names), 'unmanaged root entry')
                fresh = False
                if generation in names:
                    started = True
                elif existing_only:
                    raise RecoveryRequired('recorded generation absent; no write retry')
                else:
                    require(len(names - {'.scope.json'}) < self.max_generations, 'generation count budget exhausted')
                    # Permission/source checked immediately before exclusive claim.
                    self.guard(root)
                    os.mkdir(generation, 0o700, dir_fd=root)
                    started = True
                    os.fsync(root)
                    fresh = True
                fd = child_dir(root, generation)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    if not fresh:
                        require(set(os.listdir(fd)) == {'package.json', 'manifest.json', 'receipt.json', 'PUBLISHED.json'}, 'pending or unexpected generation contents')
                        require(read(fd, 'PUBLISHED.json', 1048576) == marker, 'publication marker changed')
                        require(read(fd, 'manifest.json', 1048576) == manifest_raw, 'manifest changed')
                        require(read(fd, 'receipt.json', 1048576) == receipt_raw, 'receipt changed')
                        require(read(fd, 'package.json', self.max_output_bytes) == package_raw, 'package changed')
                    else:
                        write(fd, 'package.json', package_raw)
                        write(fd, 'manifest.json', manifest_raw)
                        write(fd, 'receipt.json', receipt_raw)
                        os.fsync(fd)
                        self.guard(root)
                        # Durable marker is the last mutation. Uncertain generations
                        # without it are preserved for reconciliation, never repaired.
                        write(fd, 'PUBLISHED.json', marker)
                        os.fsync(fd)
                        os.fsync(root)
                    self.guard(root)
                    return copy.deepcopy(receipt)
                finally:
                    os.close(fd)
        except RecoveryRequired:
            raise
        except Exception as error:
            if started:
                raise RecoveryRequired('reserved generation requires reconciliation; no overwrite or redispatch') from error
            raise

    def read_package(self, package_binding, request_binding, source_cut, generation_ref):
        """Read one independently selected generation; never create or repair files.

        The host supplies bindings and source cut from its own selected control.
        The caller cannot choose a filesystem path or turn this into upload access.
        The returned source bytes still require target mapping and model validation.
        """
        package_binding, request_binding, source_cut = copy.deepcopy((package_binding, request_binding, source_cut))
        self.transfer.valid('urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding', package_binding)
        self.transfer.valid('urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding', request_binding)
        selection = {'output_root_scope_ref': self.scope_ref, 'package_binding': package_binding,
                     'request_binding': request_binding, 'source_cut': source_cut}
        generation = 'pkg-' + sha(encoded(selection))
        expected_ref = self.scope_ref + '/generations/' + generation
        require(type(generation_ref) is str and generation_ref == expected_ref,
                'independently selected generation differs')
        try:
            with directory(self.root) as root:
                self.guard(root)
                fcntl.flock(root, fcntl.LOCK_SH | fcntl.LOCK_NB)
                names = set(os.listdir(root))
                require(all(name == '.scope.json' or name.startswith('pkg-') and len(name) == 68
                    and all(c in '0123456789abcdef' for c in name[4:]) for name in names), 'unmanaged root entry')
                require(generation in names, 'selected generation absent')
                fd = child_dir(root, generation)
                try:
                    generation_identity = identity(os.fstat(fd))
                    fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
                    require(set(os.listdir(fd)) == {'package.json', 'manifest.json', 'receipt.json', 'PUBLISHED.json'},
                            'pending or unexpected generation contents')
                    original = read(fd, 'package.json', self.max_output_bytes)
                    # Rebuild every expected metadata byte from the authenticated
                    # host's selection and the verified original archive.
                    _, manifest_raw, receipt, receipt_raw, marker = self.describe(
                        original, package_binding, request_binding, source_cut)
                    require(read(fd, 'manifest.json', 1048576) == manifest_raw, 'manifest changed')
                    require(read(fd, 'receipt.json', 1048576) == receipt_raw, 'receipt changed')
                    require(read(fd, 'PUBLISHED.json', 1048576) == marker, 'publication marker changed')
                    # A held descriptor cannot hide a replaced generation name.
                    current = child_dir(root, generation)
                    try:
                        require(identity(os.fstat(current)) == generation_identity, 'current generation identity changed')
                    finally:
                        os.close(current)
                    self.guard(root)
                    return original, copy.deepcopy(receipt)
                finally:
                    os.close(fd)
        except RecoveryRequired:
            raise
        except Exception as error:
            raise RecoveryRequired('selected generation could not be verified; read-only reconciliation required') from error
