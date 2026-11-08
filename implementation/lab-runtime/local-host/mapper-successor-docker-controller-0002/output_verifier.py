"""Bounded exact 55-leaf verifier for the disposable original Mapper role."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import sys

from anchored_copy import FLAGS, LEAF_FLAGS, close_all, identity, dir_identity

MAPPER = 'product/lab/release-candidates/v1/interface/docker-mapped-20261020-0002'
SOURCE = 'product/lab/release-candidates/v1/interface/docker-source-20261020-0002'
MAPPER_SHA = 'bad889d50a0ba302ae83c9f4d5d9b664417af50cf4a6e4c408dfb50f8680d947'
SOURCE_PACKAGE_SHA = 'bdb5eac92cbb3f96857c4d2ccb00880441d55fb8f1dbbeb5cdaae8d81c720653'
TOTAL_LIMIT = 256 * 1024 * 1024


class Refused(ValueError):
    pass


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise Refused(reason)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse(raw: bytes) -> dict:
    def pairs(rows):
        out = {}
        for key, value in rows:
            need(key not in out, 'OUTPUT_DUPLICATE_JSON_KEY')
            out[key] = value
        return out
    try:
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(
                               Refused('OUTPUT_NONFINITE_JSON')))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise Refused('OUTPUT_INVALID_JSON') from error
    need(type(value) is dict, 'OUTPUT_JSON_OBJECT_REQUIRED')
    return value


def inventory(root_fd: int) -> tuple[set[str], set[str]]:
    files, dirs = set(), set()
    def descend(fd: int, prefix: str) -> None:
        with os.scandir(fd) as scan:
            names = [entry.name for entry in scan]
        for name in names:
            info = os.stat(name, dir_fd=fd, follow_symlinks=False)
            relative = prefix + name
            if stat.S_ISDIR(info.st_mode):
                dirs.add(relative)
                child = os.open(name, FLAGS, dir_fd=fd)
                try:
                    need(dir_identity(os.fstat(child)) == dir_identity(info),
                         'OUTPUT_DIRECTORY_OPEN_DRIFT')
                    descend(child, relative + '/')
                    need(dir_identity(os.stat(name, dir_fd=fd,
                                              follow_symlinks=False)) ==
                         dir_identity(info), 'OUTPUT_DIRECTORY_DETACHED')
                finally:
                    close_all([child], sys.exception())
            else:
                need(stat.S_ISREG(info.st_mode), 'OUTPUT_NONREGULAR_ENTRY')
                files.add(relative)
    descend(root_fd, '')
    return files, dirs


def owned_dir(parent_fd: int, name: str) -> int:
    info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
         info.st_gid == os.getgid() and stat.S_IMODE(info.st_mode) == 0o700,
         'OUTPUT_DIRECTORY_OWNER_MODE')
    fd = os.open(name, FLAGS, dir_fd=parent_fd)
    try:
        need(dir_identity(os.fstat(fd)) == dir_identity(info),
             'OUTPUT_DIRECTORY_OPEN_DRIFT')
        return fd
    except BaseException:
        close_all([fd], sys.exception())
        raise


def leaf(package_fd: int, relative: str, *, capture: bool,
         expected_dirs: dict[str, tuple[int, ...]]) -> tuple[str, int, bytes | None]:
    parts = relative.split('/')
    need(all(part not in ('', '.', '..') for part in parts), 'OUTPUT_RELATIVE_PATH')
    opened = [os.dup(package_fd)]
    try:
        for part in parts[:-1]:
            opened.append(owned_dir(opened[-1], part))
            need(dir_identity(os.fstat(opened[-1])) == expected_dirs[part],
                 'OUTPUT_SUBDIRECTORY_DETACHED')
        parent, name = opened[-1], parts[-1]
        before = os.stat(name, dir_fd=parent, follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
             before.st_uid == os.getuid() and before.st_gid == os.getgid() and
             stat.S_IMODE(before.st_mode) == 0o600 and
             0 <= before.st_size <= TOTAL_LIMIT,
             'OUTPUT_LEAF_OWNER_MODE_SIZE')
        fd = os.open(name, LEAF_FLAGS, dir_fd=parent)
        try:
            need(identity(os.fstat(fd)) == identity(before), 'OUTPUT_LEAF_OPEN_DRIFT')
            h = hashlib.sha256()
            chunks = [] if capture else None
            size = 0
            while True:
                block = os.read(fd, 1024 * 1024)
                if not block:
                    break
                h.update(block)
                size += len(block)
                need(size <= TOTAL_LIMIT, 'OUTPUT_LEAF_OVERSIZE')
                if chunks is not None:
                    chunks.append(block)
            need(size == before.st_size and identity(os.fstat(fd)) == identity(before),
                 'OUTPUT_LEAF_BYTES_OR_IDENTITY_DRIFT')
            need(identity(os.stat(name, dir_fd=parent, follow_symlinks=False)) ==
                 identity(before), 'OUTPUT_LEAF_DETACHED')
            return h.hexdigest(), size, b''.join(chunks) if chunks is not None else None
        finally:
            close_all([fd], sys.exception())
    finally:
        close_all(opened, sys.exception())


def verify(package_parent_fd: int, expected_members: list[str]) -> dict:
    """Read-only post-Docker effect verifier; no authority promotion."""
    package_fd = owned_dir(package_parent_fd, '0001')
    package_identity = dir_identity(os.fstat(package_fd))
    try:
        return _verify_held(package_parent_fd, package_fd, package_identity,
                            expected_members)
    finally:
        close_all([package_fd], sys.exception())


def _verify_held(package_parent_fd: int, package_fd: int,
                 package_identity: tuple[int, ...], expected_members: list[str]) -> dict:
    members = set(expected_members)
    need(len(expected_members) == len(members) == 55 and
         all(type(name) is str and name and not name.startswith('/') and
             all(part not in ('', '.', '..') for part in name.split('/'))
             for name in expected_members), 'OUTPUT_EXPECTED_MEMBERS_DRIFT')
    files, dirs = inventory(package_fd)
    need(files == members and dirs == {'semantic', 'governance'} and
         len(files) == 55, 'OUTPUT_INVENTORY_DRIFT')
    expected_dirs = {}
    for name in dirs:
        child = owned_dir(package_fd, name)
        try:
            expected_dirs[name] = dir_identity(os.fstat(child))
        finally:
            close_all([child], sys.exception())
    observed = {}
    docs = {}
    total = 0
    captured = {'manifest.json': 1024 * 1024, 'build-result.json': 1024 * 1024,
                'mapping.json': 4 * 1024 * 1024,
                'native-output.json': 4 * 1024 * 1024}
    for name in sorted(files):
        digest, size, raw = leaf(package_fd, name, capture=name in captured,
                                 expected_dirs=expected_dirs)
        total += size
        need(total <= TOTAL_LIMIT, 'OUTPUT_TOTAL_OVERSIZE')
        observed[name] = digest
        if raw is not None:
            need(len(raw) <= captured[name], 'OUTPUT_JSON_OVERSIZE')
            docs[name] = parse(raw)
    manifest = docs['manifest.json']
    result = docs['build-result.json']
    mapping = docs['mapping.json']
    native = docs['native-output.json']
    expected_bindings = [{'path': MAPPER + '/packages/0001/' + name,
                          'sha256': observed[name]}
                         for name in sorted(files - {'manifest.json'})]
    need(manifest.get('schema_version') == 'lab-mapped-context-package/v1-candidate' and
         manifest.get('files') == expected_bindings and
         manifest.get('source_manifest_binding') ==
         {'path': MAPPER + '/source-manifest.json', 'sha256': MAPPER_SHA} and
         manifest.get('authority_effect') == 'none' and
         manifest.get('actual_owner_outcome') is None,
         'OUTPUT_MANIFEST_BINDINGS')
    need(result.get('result') == 'PASS' and
         type(result.get('node_count')) is int and result['node_count'] == 15 and
         type(result.get('edge_count')) is int and result['edge_count'] == 10 and
         type(result.get('exact_governance_joins')) is int and
         result['exact_governance_joins'] == 25 and
         result.get('cold_native_replay_byte_parity') is True and
         result.get('same_signed_source_cut') is True and
         result.get('source_sha256') == MAPPER_SHA and
         result.get('authority_effect') == 'none' and
         result.get('actual_owner_outcome') is None and
         result.get('task_complete') is False,
         'OUTPUT_BUILD_RESULT')
    need(mapping.get('source_package_binding') ==
         {'path': SOURCE + '/packages/0001/manifest.json',
          'sha256': SOURCE_PACKAGE_SHA} and
         type(mapping.get('native_seal_processes')) is int and
         mapping['native_seal_processes'] == 2 and
         type(mapping.get('actual_cold_native_read_processes')) is int and
         mapping['actual_cold_native_read_processes'] == 2 and
         mapping.get('native_domain_mapping_supplied') is True and
         mapping.get('context_or_ontology_view_carriers_generated') is False and
         mapping.get('authority_effect') == 'none' and
         mapping.get('actual_owner_outcome') is None and
         type(mapping.get('semantic_cursor')) is int and
         mapping['semantic_cursor'] == 25 and
         type(mapping.get('governance_cursor')) is int and
         mapping['governance_cursor'] == 25 and
         type(mapping.get('rows')) is list and len(mapping['rows']) == 25,
         'OUTPUT_DOMAIN_MAPPING')
    cut = native.get('cut')
    need(native.get('authority_effect') == 'none' and type(cut) is dict and
         type(cut.get('semantic_cursor')) is int and
         cut['semantic_cursor'] == 25 and
         type(native.get('governance_cursor')) is int and
         native['governance_cursor'] == 25 and
         type(native.get('governed_nodes')) is list and
         len(native['governed_nodes']) == 15,
         'OUTPUT_NATIVE_CUT')
    # The numbered leaves are the original two 25-event families. Their
    # actual bytes are hashed above; parse selected fields for join integrity.
    semantic = {}
    for index in range(1, 26):
        name = f'semantic/{index:08d}.json'
        digest, size, raw = leaf(package_fd, name, capture=True,
                                 expected_dirs=expected_dirs)
        need(size <= 4 * 1024 * 1024 and digest == observed[name],
             'OUTPUT_SEMANTIC_LEAF_DRIFT')
        event = parse(raw)
        need(event.get('event_family') == 'semantic' and
             type(event.get('semantic_cursor')) is int and
             event['semantic_cursor'] == index and
             type(event.get('event_id')) is str and
             type(event.get('event_digest')) is str,
             'OUTPUT_SEMANTIC_EVENT')
        semantic[index] = (event['event_id'], event['event_digest'])
    for index in range(1, 26):
        name = f'governance/{index:08d}.json'
        digest, size, raw = leaf(package_fd, name, capture=True,
                                 expected_dirs=expected_dirs)
        need(size <= 4 * 1024 * 1024 and digest == observed[name],
             'OUTPUT_GOVERNANCE_LEAF_DRIFT')
        event = parse(raw)
        ref = event.get('semantic_ref')
        need(event.get('event_family') == 'governance' and
             type(event.get('governance_cursor')) is int and
             event['governance_cursor'] == index and type(ref) is dict and
             type(ref.get('semantic_cursor')) is int and
             ref['semantic_cursor'] == index and
             (ref.get('semantic_event_id'), ref.get('semantic_event_digest')) ==
             semantic[index], 'OUTPUT_GOVERNANCE_JOIN')
    need(dir_identity(os.fstat(package_fd)) == package_identity ==
         dir_identity(os.stat('0001', dir_fd=package_parent_fd,
                              follow_symlinks=False)), 'OUTPUT_PACKAGE_DETACHED')
    for name, expected in expected_dirs.items():
        need(dir_identity(os.stat(name, dir_fd=package_fd,
                                  follow_symlinks=False)) == expected,
             'OUTPUT_SUBDIRECTORY_DETACHED')
    return {'schema': 'lab-mapper-successor-output-verification/v1',
            'result': 'PASS_CANDIDATE_OUTPUT_ONLY', 'manifest_sha256': observed['manifest.json'],
            'files': 55, 'semantic_leaves': 25, 'governance_leaves': 25,
            'node_count': 15, 'edge_count': 10, 'exact_governance_joins': 25,
            'native_seal_processes': 2, 'actual_cold_native_read_processes': 2,
            'total_bytes': total, 'authority_effect': 'none',
            'actual_owner_outcome': None, 'task_complete': False}
