"""Disposable exact current API33 proof-table Reader fixture; no host or owner claim.

Only the original ProtectedReader performs physical byte verification. This
builder selects live files by their published table rows and current metadata;
it never copies selected file bodies or emits private controls in its receipt.
"""

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from preflight import API, ROOT, binding, inspect, parse, sha


SOURCE_SHA256 = 'b0120152001da6384a4da87cf5eb6d685410ce6893b252b37b8397b9df474b0c'
PROFILE_SHA256 = 'ff886cf8a7a295095834849c5d47fc0f3820c222cd3a157eda99dd8038521c31'
ORIGINAL = ROOT / 'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001'
ORIGINAL_MANIFEST_SHA256 = '7b098a10253628caa644e8ff0478ac39a601339bd277ec7203a5730e93e9cfe2'
ORIGINAL_READER_SHA256 = '7a51fed6ecf0842bc3b6711e02a0b480ca9eed666405643c4e6577f938da703f'


def original_reader():
    if (sha((ORIGINAL / 'source-manifest.json').read_bytes()) != ORIGINAL_MANIFEST_SHA256
            or sha((ORIGINAL / 'protected_inputs.py').read_bytes()) != ORIGINAL_READER_SHA256):
        raise ValueError('original protected Reader module selection differs')
    name = '_cal_t08_selected_original_reader_fixture_0001'
    if name in sys.modules:
        return sys.modules[name + '.protected_inputs']
    spec = importlib.util.spec_from_file_location(
        name, ORIGINAL / '__init__.py', submodule_search_locations=[str(ORIGINAL)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    return sys.modules[name + '.protected_inputs']


def metadata(info):
    return {'device': info.st_dev, 'inode': info.st_ino,
            'uid': info.st_uid, 'mode': stat.S_IMODE(info.st_mode)}


def private_write(path, raw):
    with path.open('xb') as stream:
        stream.write(raw)
    path.chmod(0o600)


def tables():
    source_raw = (ROOT / API / 'source-manifest.json').read_bytes()
    profile_raw = (ROOT / API / 'contract-profile.json').read_bytes()
    summary = inspect(source_raw, profile_raw, SOURCE_SHA256, PROFILE_SHA256)
    source, profile = parse(source_raw), parse(profile_raw)
    external = profile['external_execution_dependency_bindings']
    return source, profile, external, summary


def make_controls(private, source, profile, external, summary):
    """Return a signed technical selector without reading any selected body."""
    P = original_reader()
    private = Path(private)
    info = private.lstat()
    if not stat.S_ISDIR(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o700 or info.st_uid != os.geteuid():
        raise ValueError('owned private fixture root required')
    signer = Ed25519PrivateKey.generate()
    public = base64.b64encode(signer.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
    principal = 'technical-principal:T08-current-proof-fixture'
    source_ref = API + '/source-manifest.json'
    profile_ref = API + '/contract-profile.json'
    selected = {}
    roots = {'repo': {'id': 'repo', 'path': str(ROOT), **metadata(ROOT.lstat())},
             'private': {'id': 'private', 'path': str(private), **metadata(info)}}

    def select(path, digest, kind):
        binding({'path': path, 'sha256': digest})
        if path in selected:
            if selected[path]['sha256'] != digest:
                raise ValueError('same selected path has conflicting digest')
            if kind in ('source-manifest', 'contract-profile'):
                selected[path]['kind'] = kind
            return selected[path]['id']
        physical = Path(path)
        if physical.is_absolute():
            parent = physical.parent
            root_id = 'absolute:' + sha(str(parent).encode())[:20]
            roots[root_id] = {'id': root_id, 'path': str(parent), **metadata(parent.lstat())}
            relative = physical.name
        else:
            root_id = 'repo'
            physical = ROOT / physical
            relative = path
        value = physical.lstat()
        if not stat.S_ISREG(value.st_mode):
            raise ValueError('selected physical file absent/unsafe: ' + path)
        row = {'id': 'proof:' + sha(path.encode()), 'root_id': root_id,
               'path': relative, 'logical_path': path, 'kind': kind,
               'sha256': digest, 'size': value.st_size, **metadata(value)}
        selected[path] = row
        return row['id']

    # Source/profile files are mandatory proof-table sources even if a table
    # does not list itself. Their exact content hashes were checked in tables().
    source_id = select(source_ref, SOURCE_SHA256, 'source-manifest')
    profile_id = select(profile_ref, PROFILE_SHA256, 'contract-profile')
    source_ids = [select(*binding(row), 'host-dependency') for row in source['files']]
    profile_ids = [select(*binding(row), 'host-dependency') for row in profile['files']]
    external_ids = [select(*binding(row), 'host-dependency') for row in external]
    if len(source_ids) + len(profile_ids) + len(external_ids) != summary['ordered_proof_occurrences_required']:
        raise ValueError('ordered selected proof count changed')

    state_raw = P.canonical({'schema_version': 'lab-protected-input-custody-state/v1-candidate',
                             'principal_ref': principal, 'revoked': False,
                             'authority_effect': 'none'})
    state_path = private / 'state.json'
    private_write(state_path, state_raw)
    state_stat = state_path.lstat()
    files = list(selected.values()) + [{
        'id': 'custody-state', 'root_id': 'private', 'path': state_path.name,
        'logical_path': 'technical:T08-current-proof-fixture/state',
        'kind': 'custody-state', 'sha256': sha(state_raw),
        'size': len(state_raw), **metadata(state_stat)}]
    cut = {'branch_ref': 'technical:T08-current-proof-fixture/branch',
           'store_ref': 'technical:T08-current-proof-fixture/store',
           'commit_sequence': 0, 'commit_sha256': sha(b'T08-current-proof-fixture-branch'),
           'source_profile_sha256': PROFILE_SHA256, 'streams': []}
    source_binding = {'ref': source_ref, 'sha256': SOURCE_SHA256}
    profile_binding = {'ref': profile_ref, 'sha256': PROFILE_SHA256}
    selector = {'schema_version': 'lab-protected-input-selector/v1-candidate',
                'source_binding': source_binding, 'profile_binding': profile_binding,
                'source_cut': cut, 'principal_ref': principal,
                'operation': 'release.prepare', 'roots': list(roots.values()),
                'files': files,
                'proof_tables': [
                    {'file_id': source_id, 'row_selector': '/files', 'coverage_file_ids': source_ids},
                    {'file_id': profile_id, 'row_selector': '/files', 'coverage_file_ids': profile_ids},
                    {'file_id': profile_id, 'row_selector': '/external_execution_dependency_bindings',
                     'coverage_file_ids': external_ids}],
                'custody_state_file_id': 'custody-state', 'authority_effect': 'none'}
    selector_raw = P.canonical(selector)
    selector_path = private / 'selector.json'
    private_write(selector_path, selector_raw)
    selector_binding = {'ref': 'technical:T08-current-proof-fixture/selector',
                        'sha256': sha(selector_raw)}
    instant = datetime.now(timezone.utc)
    grant_payload = {
        'schema_version': 'lab-protected-input-custody-grant/v1-candidate',
        'selector_binding': selector_binding, 'source_binding': source_binding,
        'profile_binding': profile_binding, 'source_cut': cut,
        'principal_ref': principal, 'operation': 'release.prepare',
        'not_before': (instant - timedelta(seconds=5)).isoformat(),
        'expires_at': (instant + timedelta(minutes=30)).isoformat(),
        'authority_effect': 'none'}
    grant_raw = P.canonical({'payload': grant_payload,
                             'signature_b64': base64.b64encode(
                                 signer.sign(P.canonical(grant_payload))).decode()})
    grant_path = private / 'grant.json'
    private_write(grant_path, grant_raw)
    grant_binding = {'ref': 'technical:T08-current-proof-fixture/grant',
                     'sha256': sha(grant_raw)}

    def locator(path):
        value = path.lstat()
        return {'root_id': 'private', 'path': path.name, 'size': value.st_size,
                **metadata(value)}

    anchor = P.CustodyAnchor(principal, public, source_binding, profile_binding,
                             cut, 'release.prepare', selector_binding,
                             grant_binding, locator(selector_path), locator(grant_path))
    return P, selector_raw, grant_raw, anchor, len(files), len(roots)


def run():
    started = time.monotonic()
    source, profile, external, summary = tables()
    with tempfile.TemporaryDirectory(prefix='cal-t08-current-proof-') as location:
        private = Path(location)
        private.chmod(0o700)
        P, selector, grant, anchor, file_count, root_count = make_controls(
            private, source, profile, external, summary)
        reader = P.ProtectedReader(selector, grant, anchor)
        prepared = time.monotonic()
        print(json.dumps({'phase': 'reader-entry-start', 'preparation_seconds': round(prepared - started, 3),
                          'selected_files': file_count, 'ordered_proof_rows': summary['ordered_proof_occurrences_required']}),
              file=sys.stderr, flush=True)
        with reader.boundary():
            entered = time.monotonic()
            print(json.dumps({'phase': 'reader-entry-pass', 'elapsed_seconds': round(entered - prepared, 3)}),
                  file=sys.stderr, flush=True)
        exited = time.monotonic()
        if len(reader.files) != file_count:
            raise ValueError('actual original Reader proof closure differs')
        return {'schema_version': 'lab-T08-current-reader-fixture/v1-candidate',
                'result': 'PASS', 'source_sha256': SOURCE_SHA256,
                'profile_sha256': PROFILE_SHA256,
                'ordered_proof_rows_verified_each_boundary': summary['ordered_proof_occurrences_required'],
                'selected_files_verified_each_boundary': file_count,
                'selected_bytes_verified_each_boundary': sum(row['size'] for row in reader.files.values()),
                'root_count': root_count,
                'entry_seconds': round(entered - prepared, 3),
                'exit_seconds': round(exited - entered, 3),
                'total_seconds': round(exited - started, 3),
                'reader_entry_and_exit_verified': True,
                'technical_source_cut_only': True, 'host_guard_executed': False,
                'semantic_graph_executed': False, 'authority_effect': 'none',
                'T08_complete': False}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
