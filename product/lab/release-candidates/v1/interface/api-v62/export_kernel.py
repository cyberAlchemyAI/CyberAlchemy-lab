"""Pinned source exports, immutable generations and a durable publication marker.

The host supplies selected material, privacy review and output scope. Caller
strings cannot name a host path or grant export permission. No Session memory,
source mutation, canonical admission or process activation occurs here.
"""
import copy
import fcntl
import hashlib
import json
import os
import re
import stat
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from . import protocol as P
from .protocol import HERE
from . import workspace as W

def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def encoded(value):
    return P.compact(value)
def require(condition, reason):
    if not condition:
        raise ValueError(reason)
def pin(ref, raw):
    return {'ref': ref, 'sha256': sha(raw)}
def renderer_binding():
    return pin('renderer:lab-json-pretty-v1-candidate', (HERE / 'export_kernel.py').read_bytes())

@dataclass(frozen=True)
class Material:
    artifact_json: bytes
    original_bytes: bytes
    source_locator: str
    encoding: str
    @property
    def artifact(self):
        return json.loads(self.artifact_json)

@dataclass(frozen=True)
class Selection:
    ref: str
    cut_json: bytes
    materials: tuple
    privacy_review_json: bytes
    @property
    def cut(self):
        return json.loads(self.cut_json)
    @property
    def privacy_binding(self):
        return pin('privacy-review:' + self.ref, self.privacy_review_json)

def path_valid(path):
    return isinstance(path, str) and len(path) <= 240 and re.fullmatch(r'(?!/)(?!.*(?:^|/)\.{1,2}(?:/|$))(?!.*//)(?!.*\\)[A-Za-z0-9._/-]*[A-Za-z0-9_-]', path) is not None

@contextmanager
def directory(path):
    """Walk each component through directory descriptors with no symlink following."""
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'absolute independent output path required')
    fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        require(stat.S_IMODE(os.fstat(fd).st_mode) == 0o700 and os.fstat(fd).st_uid == os.getuid(), 'private owned output directory required')
        yield fd
    finally:
        os.close(fd)

def child_dir(fd, name, create=False):
    if create:
        os.mkdir(name, 0o700, dir_fd=fd)
    result = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
    require(stat.S_IMODE(os.fstat(result).st_mode) == 0o700, 'unsafe generation directory')
    return result

def write(fd, name, raw):
    out = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        with os.fdopen(out, 'wb', closefd=False) as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(out)
    finally:
        os.close(out)

def read(fd, name, maximum=2*1024*1024):
    item = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
    try:
        info = os.fstat(item)
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size <= maximum, 'unsafe managed file')
        with os.fdopen(item, 'rb', closefd=False) as stream:
            return stream.read(maximum + 1)
    finally:
        os.close(item)

def nested_write(fd, path, raw):
    pieces = path.split('/')
    current = os.dup(fd)
    try:
        for part in pieces[:-1]:
            try:
                os.mkdir(part, 0o700, dir_fd=current)
            except FileExistsError:
                pass
            nxt = child_dir(current, part)
            os.close(current)
            current = nxt
        write(current, pieces[-1], raw)
        os.fsync(current)
    finally:
        os.close(current)

def nested_read(fd, path):
    current = os.dup(fd)
    try:
        pieces = path.split('/')
        for part in pieces[:-1]:
            nxt = child_dir(current, part)
            os.close(current)
            current = nxt
        return read(current, pieces[-1])
    finally:
        os.close(current)

class ExportHost:
    def __init__(self, root, scope_ref, actor, selection, schemas, source_guard, authorization_guard, max_bytes=1024*1024, root_identity=None):
        self.root = Path(root)
        self.scope_ref = scope_ref
        self.actor = copy.deepcopy(actor)
        self.selection = selection
        self.schemas = schemas
        self.source_guard = source_guard
        self.authorization_guard = authorization_guard
        self.max_bytes = max_bytes
        self.root_identity = root_identity
        self.code_sha = sha((HERE / 'export_kernel.py').read_bytes())
    def guard(self):
        require(sha((HERE / 'export_kernel.py').read_bytes()) == self.code_sha, 'renderer/kernel changed')
        self.schemas.guard()
        self.source_guard()
        require(self.authorization_guard() is True, 'export host permission not current')
    def plan(self, request):
        self.guard()
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:file-materialization-request:v1-candidate', request), 'invalid exact request schema')
        require(request['actor'] == self.actor, 'actor differs from independently selected host')
        require(request['output_root_scope_ref'] == self.scope_ref, 'output scope unavailable')
        selection = self.selection
        require(request['selection_ref'] == selection.ref and request['source_cut'] == selection.cut, 'selection/cut differs')
        require(request['artifact_refs'] == [m.artifact for m in selection.materials] and selection.materials, 'complete nonempty selected artifact closure required')
        require(request['privacy_review_binding'] == selection.privacy_binding, 'exact privacy review required')
        review = json.loads(selection.privacy_review_json)
        require(review == {'selection_ref': selection.ref, 'source_cut': selection.cut, 'artifact_refs': request['artifact_refs'], 'include_session_memory': False, 'authority_effect': 'none'}, 'privacy review does not cover complete selection')
        paths = request['managed_relative_paths']
        require(len(paths) == len(selection.materials) and all(path_valid(p) for p in paths) and len(paths) == len(set(paths)), 'exact artifact/path pairing required')
        require(not any(a != b and b.startswith(a + '/') for a in paths for b in paths), 'file/directory output collision')
        require(request['renderer_binding'] == (renderer_binding() if request['mode'] == 'rendered' else None), 'unselected renderer')
        rows = []
        total = 0
        for path, material in zip(paths, selection.materials, strict=True):
            raw = material.original_bytes
            require(sha(raw) == material.artifact['byte_sha256'], 'selected original bytes differ')
            W.privacy(P.frame_parse(raw))
            output = raw if request['mode'] == 'byte-exact' else (json.dumps(P.frame_parse(raw), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
            total += len(output)
            require(total <= self.max_bytes, 'complete output byte budget exhausted')
            rows.append((path, output, material))
        self.guard()
        return rows
    def materialize(self, request, *, existing_only=False):
        rows = self.plan(request)
        request_raw = encoded(request)
        generation = sha(request_raw)
        generation_ref = 'generated:' + self.scope_ref + ':' + generation
        base = 'managed-generation:' + generation
        manifest = {'schema_version': 'lab-file-generation-manifest/v1-candidate', 'request_binding': pin(request['request_ref'], request_raw), 'source_cut': request['source_cut'], 'selection_ref': request['selection_ref'], 'privacy_review_binding': request['privacy_review_binding'], 'mode': request['mode'], 'renderer_binding': request['renderer_binding'], 'files': [{'relative_path': p, 'output_sha256': sha(raw), 'size_bytes': len(raw), 'artifact': m.artifact, 'source_locator': m.source_locator, 'source_encoding': m.encoding} for p, raw, m in rows], 'authority_effect': 'none', 'canonical_replay_source': False}
        manifest_raw = encoded(manifest)
        receipt = {'schema_version': 'lab-file-materialization-receipt/v1-candidate', 'request_binding': manifest['request_binding'], 'manifest_binding': pin(base + '/manifest.json', manifest_raw), 'source_cut': request['source_cut'], 'generation_ref': generation_ref, 'posture': 'published', 'output_bindings': [{'content_ref': base + '/files/' + p, 'byte_sha256': sha(raw), 'size_bytes': len(raw), 'media_type': 'application/json'} for p, raw, _ in rows], 'canonical_replay_source': False, 'unmanaged_files_overwritten': False, 'gaps': [], 'claim_ceiling': 'Derived candidate export of exactly selected source bytes or pinned JSON rendering. No admission, release or current Agent participation.', 'authority_effect': 'none', 'recovery_required': False}
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:file-materialization-receipt:v1-candidate', receipt), 'invalid exact result schema')
        receipt_raw = encoded(receipt)
        started = False
        try:
            with directory(self.root) as root:
                if self.root_identity is not None:
                    info = os.fstat(root)
                    require({'device': info.st_dev, 'inode': info.st_ino} == self.root_identity, 'opened output root differs from independently granted inode')
                # A generation directory is claimed exclusively and never removed
                # by this kernel. Only a fully fsynced marker makes it published.
                if existing_only:
                    fresh = False
                else:
                    try:
                        self.guard()
                        os.mkdir(generation, 0o700, dir_fd=root)
                        started = True
                        os.fsync(root)
                        fresh = True
                    except FileExistsError:
                        fresh = False
                fd = child_dir(root, generation)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    if not fresh:
                        require(read(fd, 'PUBLISHED.json') == encoded({'manifest_sha256': sha(manifest_raw), 'receipt_sha256': sha(receipt_raw)}), 'pending or different generation; recovery required')
                        require(read(fd, 'manifest.json') == manifest_raw and read(fd, 'receipt.json') == receipt_raw, 'recorded output metadata differs')
                        files = child_dir(fd, 'files')
                        try:
                            require(all(nested_read(files, p) == raw for p, raw, _ in rows), 'published output bytes changed')
                        finally:
                            os.close(files)
                        self.guard()
                        return copy.deepcopy(receipt)
                    self.guard()
                    write(fd, 'CLAIM.json', encoded({'request_sha256': generation, 'state': 'pending', 'authority_effect': 'none'}))
                    os.fsync(fd)
                    files = child_dir(fd, 'files', create=True)
                    try:
                        for path, raw, _ in rows:
                            self.guard()
                            nested_write(files, path, raw)
                        os.fsync(files)
                    finally:
                        os.close(files)
                    write(fd, 'manifest.json', manifest_raw)
                    write(fd, 'receipt.json', receipt_raw)
                    self.guard()
                    write(fd, 'PUBLISHED.json', encoded({'manifest_sha256': sha(manifest_raw), 'receipt_sha256': sha(receipt_raw)}))
                    os.fsync(fd)
                    os.fsync(root)
                    self.guard()
                    return copy.deepcopy(receipt)
                finally:
                    os.close(fd)
        except Exception as error:
            if not started:
                raise ValueError('Existing generation or output root unavailable; inspect/recover without redispatch.') from error
            return {**receipt, 'posture': 'indeterminate', 'manifest_binding': None, 'output_bindings': [], 'recovery_required': True, 'gaps': [{'gap_ref': 'gap:export-uncertain:' + generation, 'subject_ref': generation_ref, 'reason': 'A managed generation may have been staged or published. Preserve it and inspect exact files before reconciliation.', 'owner_route': 'R03/S02/R08', 'blocking_use': 'export-retry'}]}
