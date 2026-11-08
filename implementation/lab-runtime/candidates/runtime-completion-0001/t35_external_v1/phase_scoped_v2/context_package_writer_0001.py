"""Owned scratch Context writer, never a generated-role or host capability.

Reuses reviewed Mapper nofollow mkdir/write/readback primitives. All Context
schedule, private lifetime and manifest checks are owned by this new slice.
"""
from __future__ import annotations

import copy
import os
from pathlib import Path
import re
import stat

from ..held_paths import HeldCanonicalDirectory
from . import mapper_package_writer_0001 as held
from . import context_ipc_model_0001 as model

Refusal = held.Refusal
need = held.require
sha = model.sha
MARKER = '.context-package-attempt-0001'
LEAVES = tuple(leaf for verb, leaf in model.schedule() if verb == 'EMIT')
CEILING = 'Owned scratch stand-in only; no actual Context delivery or host authority.'


class PackageWriter(held.PackageWriter):
    """Single-threaded one-shot scratch writer. Failures retain UNKNOWN."""

    def __init__(self, context: Path, source_binding: dict):
        need(type(context) is type(Path('/')) and context.is_absolute() and
             context.parts[-3:] == ('output', 'legacy-fixture-source', 'context') and
             context.parent.parent.parent.parent == Path('/tmp') and
             re.fullmatch(r'lc-u02-05-context-writer-[a-z0-9-]{1,48}', context.parent.parent.parent.name),
             'scratch_scope')
        need(type(source_binding) is dict and set(source_binding) == {'path','sha256'} and
             source_binding['path'] == str(context / 'source-manifest.json') and
             model.hexhash(source_binding['sha256']), 'source_binding')
        self.context = context
        self.scratch = context.parent.parent.parent
        self.private_path = Path('/tmp') / self.scratch.name.replace('context-writer-', 'context-private-', 1)
        self.source_binding = copy.deepcopy(source_binding)
        self.uid, self.gid = os.geteuid(), os.getegid()
        self.held = self.private_parent = None
        self.packages_fd = self.package_fd = self.private_fd = self.marker_fd = None
        self.event_fds, self.identities, self.hashes, self.file_signatures = {}, {}, {}, {}
        self.leaf_fds = {}
        self.index = self.total = self.artifact_total = self.close_errors = 0
        self.unknown = self.closed = self.finished = self.released = False
        self.private_signature = self.policy_raw = self.marker_signature = None
        try:
            self.held = HeldCanonicalDirectory(str(context))
            for path in (self.scratch, self.scratch / 'output', context.parent, context):
                row = os.fstat(self.held.at(str(path)))
                need(row.st_uid == self.uid and row.st_gid == self.gid and
                     stat.S_IMODE(row.st_mode) == 0o700, 'scratch_custody')
            need('packages' not in os.listdir(self.held.fd), 'preexisting_package')
            self.private_parent = HeldCanonicalDirectory('/tmp')
            try:
                os.stat(self.private_path.name, dir_fd=self.private_parent.fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise Refusal('preexisting_private_root')
            root = self.held.at(str(self.scratch))
            self.marker_fd = os.open(MARKER, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=root)
            os.fchmod(self.marker_fd, 0o600)
            marker = model.encoded({'schema_version':'lab-context-scratch-attempt/v1','source_binding':self.source_binding,'package':str(context/'packages/0001'),'private_root':str(self.private_path),'authority_effect':'none'})
            self._write_all(self.marker_fd, marker)
            os.fsync(self.marker_fd)
            self.marker_signature = self._readback(root, MARKER, marker, self.marker_fd)
            os.fsync(root)
            self.packages_fd = self._mkdir(self.held.fd, 'packages')
            self.package_fd = self._mkdir(self.packages_fd, '0001')
            self._scan()
        except BaseException:
            self.unknown = True
            self.close()
            raise

    def _available(self):
        need(not self.closed and not self.unknown and not self.finished, 'writer_unavailable')

    def _attached(self):
        super()._attached()
        need(self.private_parent is not None and self.private_parent.attached(), 'private_parent_detached')
        if self.private_fd is not None:
            self._attached_dir(self.private_fd, self.private_parent.fd, self.private_path.name, self.identities[self.private_path.name])
        if self.marker_fd is not None:
            need(held._file_signature(os.fstat(self.marker_fd)) == self.marker_signature == held._file_signature(os.stat(MARKER, dir_fd=self.held.at(str(self.scratch)), follow_symlinks=False)), 'marker_changed')

    def _scan(self):
        self._attached()
        need(set(os.listdir(self.packages_fd)) == {'0001'}, 'package_sibling')
        roots = {name for name in self.hashes if '/' not in name} | set(self.event_fds)
        need(set(os.listdir(self.package_fd)) == roots, 'package_extra_or_missing')
        for family, fd in self.event_fds.items():
            need(set(os.listdir(fd)) == {n.split('/')[1] for n in self.hashes if n.startswith(family+'/')}, 'artifact_extra_or_missing')
        for name, signature in self.file_signatures.items():
            parent, leaf = self._target(name)
            need(held._file_signature(os.stat(leaf, dir_fd=parent, follow_symlinks=False)) == signature == held._file_signature(os.fstat(self.leaf_fds[name])), 'emitted_leaf_changed')
        if self.private_fd is not None:
            need(set(os.listdir(self.private_fd)) == ({'permission.json'} if self.policy_raw is not None else set()), 'private_inventory')
            if self.policy_raw is not None:
                need(held._file_signature(os.stat('permission.json', dir_fd=self.private_fd, follow_symlinks=False)) == self.private_signature, 'policy_changed')
        if self.released:
            try:
                os.stat(self.private_path.name, dir_fd=self.private_parent.fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise Refusal('private_reappeared')

    def _target(self, name):
        family, sep, leaf = name.partition('/')
        return (self.event_fds[family], leaf) if sep else (self.package_fd, family)

    def prepare_receipt(self):
        self._available()
        try:
            self._scan()
            need(self.index == 0 and not self.event_fds, 'prepare_not_empty')
            return self._receipt(False)
        except BaseException:
            self.unknown = True
            raise

    def _receipt(self, private):
        identity = self.identities[self.private_path.name if private else '0001']
        return {'path':str(self.private_path if private else self.context/'packages/0001'),
                'absent_before':True,'empty_after':True,'readonly_visible':True,
                'nonsymlink':True,'uid':self.uid,'mode':0o700,
                'identity_sha256':sha(model.encoded(list(identity)))}

    def create_private(self):
        self._available()
        try:
            self._scan()
            need(self.private_fd is None and not self.released, 'private_already_selected')
            self.private_fd = self._mkdir(self.private_parent.fd, self.private_path.name)
            self._scan()
            return self._receipt(True)
        except BaseException:
            self.unknown = True
            raise

    def _put(self, parent, name, raw):
        fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent)
        try:
            os.fchmod(fd, 0o600)
            self._write_all(fd, raw)
            os.fsync(fd)
            signature = self._readback(parent, name, raw, fd)
            os.fsync(parent)
            return signature, fd
        except BaseException:
            os.close(fd)
            raise

    def provision(self, raw):
        self._available()
        try:
            need(type(raw) is bytes and 0 < len(raw) <= model.POLICY_MAX and self.private_fd is not None and self.policy_raw is None, 'policy_state')
            self._scan()
            signature, fd = self._put(self.private_fd, 'permission.json', raw)
            os.close(fd)
            self.private_signature, self.policy_raw = signature, raw
            self._scan()
            return {'sha256':sha(raw),'size_bytes':len(raw),'durable_observed':True}
        except BaseException:
            self.unknown = True
            raise

    def release_private(self):
        self._available()
        try:
            need(self.index == 38 and self.private_fd is not None and self.policy_raw is not None, 'private_release_order')
            self._scan()
            receipt = self._receipt(True)
            fd = os.open('permission.json', os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC, dir_fd=self.private_fd)
            try:
                self._readback(self.private_fd, 'permission.json', self.policy_raw, fd)
            finally:
                os.close(fd)
            os.unlink('permission.json', dir_fd=self.private_fd)
            os.fsync(self.private_fd)
            need(os.listdir(self.private_fd) == [], 'private_not_empty')
            self._attached()
            os.rmdir(self.private_path.name, dir_fd=self.private_parent.fd)
            os.fsync(self.private_parent.fd)
            os.close(self.private_fd)
            self.private_fd = None
            self.released = True
            self._scan()
            return {'path':str(self.private_path),'identity_sha256':receipt['identity_sha256'],'policy_absent':True,'root_absent':True,'owner_uid':self.uid}
        except BaseException:
            self.unknown = True
            raise

    def manifest_rows(self):
        return [{'path':str(self.context/'packages/0001'/name),'sha256':self.hashes[name]} for name in sorted(self.hashes) if name != 'manifest.json']

    def _validate_manifest(self, raw):
        try:
            value = held._closed_json(raw)
        except (ValueError, UnicodeError, RecursionError, Refusal):
            raise Refusal('manifest_parse') from None
        need(type(value) is dict and set(value) == {'schema_version','files','source_manifest_binding','authority_effect','actual_owner_outcome','delivery_binding','provenance_binding','claim_ceiling'}, 'manifest_fields')
        need(value['schema_version'] == 'lab-context-scratch-package/v1-inert' and value['authority_effect'] == 'none' and value['actual_owner_outcome'] is None and value['claim_ceiling'] == CEILING and value['source_manifest_binding'] == self.source_binding and value['files'] == self.manifest_rows() and len(value['files']) == 39, 'manifest_binding')
        for key, name in [('delivery_binding','delivery.json'),('provenance_binding','delivery-provenance.json')]:
            need(value[key] == {'path':str(self.context/'packages/0001'/name),'sha256':self.hashes[name]}, 'manifest_delivery_binding')
        need(model.encoded(value) == raw, 'manifest_encoding')

    def emit(self, name, raw):
        self._available()
        try:
            need(type(name) is str and type(raw) is bytes and self.index < 40 and name == LEAVES[self.index], 'leaf_order')
            need(0 < len(raw) <= model.LEAF_MAX and self.total+len(raw) <= model.PACKAGE_MAX, 'package_bound')
            need(self.private_fd is not None if self.index < 38 else self.released, 'private_lifetime')
            if name == 'request.json': need(len(raw) <= model.REQUEST_MAX, 'request_bound')
            if name.startswith('artifacts/'):
                need(self.artifact_total + len(raw) <= model.ARTIFACT_TOTAL_MAX, 'artifact_bound')
            self._scan()
            if name == 'manifest.json': self._validate_manifest(raw)
            if '/' in name and 'artifacts' not in self.event_fds:
                self.event_fds['artifacts'] = self._mkdir(self.package_fd, 'artifacts')
            parent, leaf = self._target(name)
            signature, fd = self._put(parent, leaf, raw)
            self.leaf_fds[name] = fd
            self.hashes[name], self.file_signatures[name] = sha(raw), signature
            self.index += 1
            self.total += len(raw)
            if name.startswith('artifacts/'): self.artifact_total += len(raw)
            self._scan()
            return {'path':name,'sha256':sha(raw),'size_bytes':len(raw),'durable_observed':True}
        except BaseException:
            self.unknown = True
            raise

    def finish(self):
        self._available()
        try:
            need(self.index == 40 and self.released and set(self.hashes) == set(LEAVES), 'package_incomplete')
            self._scan()
            for name in LEAVES:
                parent, leaf = self._target(name)
                fd = self.leaf_fds[name]
                os.lseek(fd, 0, os.SEEK_SET)
                raw = bytearray()
                while len(raw) <= model.LEAF_MAX:
                    chunk = os.read(fd, min(65536, model.LEAF_MAX+1-len(raw)))
                    if not chunk: break
                    raw.extend(chunk)
                need(sha(raw) == self.hashes[name], 'final_hash_changed')
                self._readback(parent, leaf, bytes(raw), fd)
            self._scan()
            self.finished = True
            return {'leaf_count':40,'manifest_row_count':39,'total_bytes':self.total,'scratch_retained':True,'effect_ready':False}
        except BaseException:
            self.unknown = True
            raise

    def close(self):
        if self.closed: return
        for fd in [*self.leaf_fds.values(),self.private_fd,self.marker_fd]:
            if fd is not None:
                try: os.close(fd)
                except OSError: self.close_errors += 1
        self.leaf_fds.clear()
        self.private_fd = self.marker_fd = None
        if self.private_parent is not None:
            # Drain every held descriptor even when one close observation is
            # uncertain; never retry an individual numeric descriptor.
            for fd in reversed(self.private_parent.fds):
                try: os.close(fd)
                except OSError: self.close_errors += 1
            self.private_parent.fds.clear()
            self.private_parent.records.clear()
            self.private_parent = None
        super().close()
