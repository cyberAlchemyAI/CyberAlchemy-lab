"""Closed signed protected inputs, fresh anchored reads; no admission authority.

The trust anchor must come from independent current transport/custody, never the
public request. The integrating host retains its original policy/source guards.
This reader neither substitutes those callbacks nor accepts a caller's PASS.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import hashlib
import json
import os
from pathlib import PurePosixPath
import stat

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

KINDS = frozenset(('governed-record', 'governed-schema', 'governed-descriptor',
    'semantic-policy', 'source-manifest', 'contract-profile', 'execution-selection',
    'environment-contract', 'history-proof', 'recovery-proof', 'public-package',
    'host-dependency', 'custody-state'))
PROOF_KINDS = frozenset(('source-manifest', 'contract-profile',
    'execution-selection', 'environment-contract', 'history-proof', 'recovery-proof'))
MAX_PARSE = 64 * 1024 * 1024  # Protected parser only; ordinary Vault is untouched.

class Refusal(ValueError):
    pass

def need(condition, message):
    if not condition:
        raise Refusal(message)

def closed(value, keys, label):
    need(type(value) is dict and set(value) == set(keys), label + ': fields differ')

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def parse(raw):
    need(type(raw) is bytes and len(raw) <= MAX_PARSE, 'bounded protected JSON required')
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    def invalid(value):
        raise Refusal('nonfinite JSON number')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                          parse_constant=invalid)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Refusal('invalid protected JSON') from exc

def instant(value):
    need(type(value) is str, 'UTC timestamp required')
    when = datetime.fromisoformat(value.replace('Z', '+00:00'))
    need(when.tzinfo is not None and when.utcoffset().total_seconds() == 0,
         'UTC timestamp required')
    return when

def now():
    return datetime.now(timezone.utc)

def binding(value):
    closed(value, ('ref', 'sha256'), 'binding')
    need(type(value['ref']) is str and value['ref'] and
         type(value['sha256']) is str and len(value['sha256']) == 64 and
         all(c in '0123456789abcdef' for c in value['sha256']), 'invalid binding')

def parts(value, absolute=False):
    need(type(value) is str and value and '\x00' not in value, 'path required')
    p = PurePosixPath(value)
    need(p.is_absolute() == absolute and p.as_posix() == value and
         all(x not in ('.', '..') for x in p.parts), 'canonical path required')
    return p.parts[1:] if absolute else p.parts

def metadata(info):
    return {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid,
            'mode': stat.S_IMODE(info.st_mode)}

def unchanged(info):
    return (info.st_dev, info.st_ino, info.st_uid, info.st_gid, info.st_mode,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_nlink)

@dataclass(frozen=True)
class CustodyAnchor:
    """Integration supplies this from its independent authenticated selection."""
    principal_ref: str
    public_key_b64: str
    source_binding: dict
    profile_binding: dict
    source_cut: dict
    operation: str
    selector_binding: dict
    grant_binding: dict
    selector_locator: dict
    grant_locator: dict

class ProtectedReader:
    def __init__(self, selector_raw, grant_raw, anchor):
        need(type(anchor) is CustodyAnchor, 'independent custody anchor required')
        self.anchor = anchor
        self.selector_raw = selector_raw
        self.grant_raw = grant_raw
        self.selector = parse(selector_raw)
        self.grant = parse(grant_raw)
        for b in (anchor.source_binding, anchor.profile_binding,
                  anchor.selector_binding, anchor.grant_binding):
            binding(b)
        need(digest(selector_raw) == anchor.selector_binding['sha256'] and
             digest(grant_raw) == anchor.grant_binding['sha256'], 'independent selector/grant pin differs')
        closed(self.selector, ('schema_version', 'source_binding', 'profile_binding',
            'source_cut', 'principal_ref', 'operation', 'roots', 'files', 'proof_tables',
            'custody_state_file_id', 'authority_effect'), 'selector')
        need(self.selector['schema_version'] == 'lab-protected-input-selector/v1-candidate'
             and self.selector['authority_effect'] == 'none', 'selector version/effect differs')
        for key, expected in (('source_binding', anchor.source_binding),
            ('profile_binding', anchor.profile_binding), ('source_cut', anchor.source_cut),
            ('principal_ref', anchor.principal_ref), ('operation', anchor.operation)):
            need(self.selector[key] == expected, 'independent ' + key + ' differs')
        closed(anchor.source_cut, ('branch_ref', 'store_ref', 'commit_sequence', 'commit_sha256',
            'source_profile_sha256', 'streams'), 'selected source cut')
        need(type(anchor.source_cut['commit_sequence']) is int and
             anchor.source_cut['commit_sequence'] >= 0 and type(anchor.source_cut['streams']) is list,
             'selected source cut shape differs')
        binding({'ref': anchor.source_cut['branch_ref'], 'sha256': anchor.source_cut['commit_sha256']})
        binding({'ref': anchor.source_cut['store_ref'], 'sha256': anchor.source_cut['source_profile_sha256']})
        seen_streams = set()
        for stream in anchor.source_cut['streams']:
            closed(stream, ('stream_ref', 'cursor', 'head_sha256'), 'selected stream cut')
            binding({'ref': stream['stream_ref'], 'sha256': stream['head_sha256']})
            need(type(stream['cursor']) is int and stream['cursor'] >= 0 and
                 stream['stream_ref'] not in seen_streams, 'duplicate/invalid stream cut')
            seen_streams.add(stream['stream_ref'])
        need(anchor.operation in ('release.prepare', 'installation.execute'), 'unsupported custody operation')
        closed(self.grant, ('payload', 'signature_b64'), 'grant')
        payload = self.grant['payload']
        closed(payload, ('schema_version', 'selector_binding', 'source_binding',
            'profile_binding', 'source_cut', 'principal_ref', 'operation', 'not_before',
            'expires_at', 'authority_effect'), 'grant payload')
        need(payload['schema_version'] == 'lab-protected-input-custody-grant/v1-candidate'
             and payload['authority_effect'] == 'none', 'custody grant version/effect differs')
        for key in ('source_binding', 'profile_binding', 'source_cut', 'principal_ref', 'operation'):
            need(payload[key] == self.selector[key], 'grant scope differs: ' + key)
        need(payload['selector_binding'] == anchor.selector_binding, 'grant selector differs')
        try:
            Ed25519PublicKey.from_public_bytes(base64.b64decode(anchor.public_key_b64,
                validate=True)).verify(base64.b64decode(self.grant['signature_b64'],
                validate=True), canonical(payload))
        except Exception as exc:
            raise Refusal('independent custody signature invalid') from exc
        self._validate_entries()
        self._anchor_seal = canonical(anchor.__dict__)
        self.authority()

    def _validate_entries(self):
        roots = self.selector['roots']; files = self.selector['files']
        need(type(roots) is list and roots and type(files) is list and files,
             'closed roots/files required')
        self.roots = {}; self.files = {}; locators = set(); logical = set()
        for root in roots:
            closed(root, ('id', 'path', 'device', 'inode', 'uid', 'mode'), 'root')
            parts(root['path'], absolute=True)
            need(type(root['id']) is str and root['id'] and root['id'] not in self.roots,
                 'duplicate/invalid root')
            for key in ('device', 'inode', 'uid', 'mode'):
                need(type(root[key]) is int and root[key] >= 0, 'root metadata invalid')
            need(root['mode'] & 0o022 == 0, 'selected root writable by foreign principals')
            self.roots[root['id']] = root
        for row in files:
            closed(row, ('id', 'root_id', 'path', 'logical_path', 'kind', 'sha256',
                         'size', 'device', 'inode', 'uid', 'mode'), 'file')
            parts(row['path']); need(row['root_id'] in self.roots, 'unselected root')
            binding({'ref': row['logical_path'], 'sha256': row['sha256']})
            need(row['kind'] in KINDS, 'unknown input kind')
            for key in ('size', 'device', 'inode', 'uid', 'mode'):
                need(type(row[key]) is int and row[key] >= 0, 'file metadata invalid')
            locator = (row['root_id'], row['path'])
            need(type(row['id']) is str and row['id'] and row['id'] not in self.files
                 and locator not in locators and row['logical_path'] not in logical,
                 'duplicate selected file/locator/logical path')
            locators.add(locator); logical.add(row['logical_path']); self.files[row['id']] = row
        state = self.files.get(self.selector['custody_state_file_id'])
        need(state is not None and state['kind'] == 'custody-state', 'exact custody state required')
        need(type(self.selector['proof_tables']) is list, 'proof table list required')
        seen = set()
        for table in self.selector['proof_tables']:
            closed(table, ('file_id', 'row_selector', 'coverage_file_ids'), 'proof table')
            need(table['file_id'] in self.files and self.files[table['file_id']]['kind'] in PROOF_KINDS
                 and (table['file_id'], table['row_selector']) not in seen,
                 'proof table kind/identity differs')
            need(table['row_selector'] in ('/files', '/bindings', '/complete_source_bindings',
                 '/complete_profile_bindings', '/schema_execution_bindings',
                 '/external_execution_dependency_bindings','/host_native_binding',
                 '/host_ABI_library_bindings','/offline_environment_wheel_bindings'), 'unsupported original row selector')
            ids = table['coverage_file_ids']
            need(type(ids) is list and len(set(ids)) == len(ids)
                 and all(i in self.files for i in ids), 'complete unique proof coverage required')
            seen.add((table['file_id'], table['row_selector']))
        for selected, kind in ((self.anchor.source_binding, 'source-manifest'),
                               (self.anchor.profile_binding, 'contract-profile')):
            found = [r for r in files if r['logical_path'] == selected['ref'] and
                     r['sha256'] == selected['sha256'] and r['kind'] == kind]
            need(len(found) == 1 and (found[0]['id'], '/files') in seen,
                 'mandatory complete source/profile proof rows unavailable')
        for row in files:
            if row['kind'] == 'environment-contract':
                need(all((row['id'], key) in seen for key in
                     ('/complete_source_bindings', '/complete_profile_bindings', '/schema_execution_bindings')),
                     'complete composite environment proof rows required')

    def authority(self):
        need(canonical(self.anchor.__dict__) == self._anchor_seal,
             'independent authority anchor mutated')
        need(digest(self.selector_raw) == self.anchor.selector_binding['sha256']
             and digest(self.grant_raw) == self.anchor.grant_binding['sha256']
             and parse(self.selector_raw) == self.selector
             and parse(self.grant_raw) == self.grant,
             'selected custody controls mutated')
        need({r['id']: r for r in self.selector['roots']} == self.roots and
             {r['id']: r for r in self.selector['files']} == self.files,
             'selected custody indices mutated')
        for raw, b, locator in ((self.selector_raw, self.anchor.selector_binding,
            self.anchor.selector_locator), (self.grant_raw, self.anchor.grant_binding,
            self.anchor.grant_locator)):
            closed(locator, ('root_id', 'path', 'size', 'device', 'inode', 'uid', 'mode'), 'control locator')
            need(locator['root_id'] in self.roots, 'control outside selected root')
            need(locator['mode'] == 0o600 and locator['uid'] == os.geteuid() and
                 self.roots[locator['root_id']]['mode'] == 0o700,
                 'independently selected custody controls must be privately owned')
            row = dict(locator, sha256=b['sha256'])
            need(self._read(row, collect=True) == raw, 'current custody control changed')
        state_raw = self._read(self.files[self.selector['custody_state_file_id']], collect=True)
        need(parse(state_raw) == {'schema_version': 'lab-protected-input-custody-state/v1-candidate',
            'principal_ref': self.anchor.principal_ref, 'revoked': False,
            'authority_effect': 'none'}, 'current custody revoked/changed')
        p = self.grant['payload']
        need(instant(p['not_before']) <= now() < instant(p['expires_at']), 'custody authority expired/not yet valid')

    @contextmanager
    def _root(self, root):
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
        try:
            for component in parts(root['path'], absolute=True):
                nxt = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd); fd = nxt
            info = os.fstat(fd)
            need(metadata(info) == {k: root[k] for k in ('device', 'inode', 'uid', 'mode')},
                 'root attachment/ownership differs')
            yield fd
        except OSError as exc:
            raise Refusal('root no-follow read refused') from exc
        finally:
            os.close(fd)

    def _read(self, row, collect=False):
        root = self.roots[row['root_id']]; chunks = []
        try:
            with self._root(root) as root_fd:
                parent_fd = os.dup(root_fd)
                fd = None
                try:
                    components = parts(row['path'])
                    for component in components[:-1]:
                        nxt = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                      dir_fd=parent_fd)
                        info = os.fstat(nxt)
                        if info.st_uid != root['uid'] or stat.S_IMODE(info.st_mode) & 0o022:
                            os.close(nxt); raise Refusal('intermediate directory ownership/mode differs')
                        os.close(parent_fd); parent_fd = nxt
                    fd = os.open(components[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                                 dir_fd=parent_fd)
                    before = os.fstat(fd)
                    need(stat.S_ISREG(before.st_mode) and metadata(before) ==
                         {k: row[k] for k in ('device', 'inode', 'uid', 'mode')}
                         and before.st_size == row['size'], 'file identity/ownership/mode/size differs')
                    need(not collect or before.st_size <= MAX_PARSE, 'protected parse bound exceeded')
                    h = hashlib.sha256(); length = 0
                    while True:
                        raw = os.read(fd, 1024 * 1024)
                        if not raw: break
                        h.update(raw); length += len(raw)
                        if collect: chunks.append(raw)
                        need(length <= row['size'], 'file grew while read')
                    after = os.fstat(fd)
                    attached = os.stat(components[-1], dir_fd=parent_fd, follow_symlinks=False)
                    need(unchanged(before) == unchanged(after) == unchanged(attached)
                         and length == row['size'] and h.hexdigest() == row['sha256'],
                         'fresh file bytes/attachment changed')
                    # Reopen the absolute root and relative chain to detect a renamed
                    # directory retaining the old open inode while path gets replaced.
                    with self._root(root) as current_root:
                        check_fd = os.dup(current_root)
                        try:
                            for component in components[:-1]:
                                nxt = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                              dir_fd=check_fd)
                                os.close(check_fd); check_fd = nxt
                            current = os.stat(components[-1], dir_fd=check_fd, follow_symlinks=False)
                            need(unchanged(current) == unchanged(after), 'directory/file attachment changed')
                        finally: os.close(check_fd)
                finally:
                    if fd is not None: os.close(fd)
                    os.close(parent_fd)
        except OSError as exc:
            raise Refusal('protected no-follow read refused') from exc
        return b''.join(chunks) if collect else None

    def read(self, file_id, expected_kind=None):
        self.authority()
        need(file_id in self.files, 'unselected file')
        row = self.files[file_id]
        need(expected_kind is None or row['kind'] == expected_kind, 'input kind spoof')
        raw = self._read(row, collect=True)
        self.authority()
        return raw

    def verify(self):
        """Fresh full boundary guard. Caller retains its original host guard too."""
        self.authority()
        for row in self.files.values(): self._read(row)
        state = parse(self.read(self.selector['custody_state_file_id'], 'custody-state'))
        closed(state, ('schema_version', 'principal_ref', 'revoked', 'authority_effect'), 'custody state')
        need(state == {'schema_version': 'lab-protected-input-custody-state/v1-candidate',
             'principal_ref': self.anchor.principal_ref, 'revoked': False,
             'authority_effect': 'none'}, 'custody revoked/changed')
        table_rows = 0
        selected_tables={(t['file_id'],t['row_selector'])for t in self.selector['proof_tables']}
        for row in self.files.values():
            if row['kind'] not in ('contract-profile','environment-contract'):continue
            document=parse(self.read(row['id']))
            required=('external_execution_dependency_bindings',) if row['kind']=='contract-profile' else (
                'host_native_binding','host_ABI_library_bindings','offline_environment_wheel_bindings')
            for key in required:
                if key in document:
                    need((row['id'],'/'+key) in selected_tables,
                         'mandatory original external/host proof coverage omitted')
        for table in self.selector['proof_tables']:
            value = parse(self.read(table['file_id']))
            key = table['row_selector'][1:]
            need(type(value) is dict and key in value, 'original proof rows missing')
            actual = [value[key]] if key=='host_native_binding' else value[key]
            need(type(actual) is list,'original proof row list required')
            expected = [self.files[i] for i in table['coverage_file_ids']]
            need(all(type(v) is dict and set(v) == {'path', 'sha256'} for v in actual),
                 'original closed path/hash rows required')
            pairs = [(v['path'], v['sha256']) for v in actual]
            wanted = [(v['logical_path'], v['sha256']) for v in expected]
            need(len(pairs) == len(set(pairs)) and pairs == wanted,
                 'original proof rows omitted/substituted/reordered')
            table_rows += len(pairs)
        self.authority()
        return {'selector_sha256': digest(self.selector_raw), 'verified_files': len(self.files),
                'verified_bytes': sum(r['size'] for r in self.files.values()),
                'proof_rows': table_rows, 'authority_effect': 'none', 'public_export_allowed': False}

    @contextmanager
    def boundary(self):
        self.verify()
        try: yield self
        finally: self.verify()
