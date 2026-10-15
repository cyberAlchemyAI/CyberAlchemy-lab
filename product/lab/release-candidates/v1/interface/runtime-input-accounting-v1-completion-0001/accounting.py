"""Exact current input accounting; historical physical closure remains refused.

Independent host pins select metadata and consumption dispositions. This module
never reads input bodies, creates old paths, supplies authority, or replaces any
signed-history/schema/source/custody verifier. Current byte verification remains
the actual guard's separate obligation at every original required boundary.
"""
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

SOURCE_SHA = '8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7'
PROFILE_SHA = '8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c'
SOURCE_ROWS = 24497
PROFILE_ROWS = 24496
UNAVAILABLE_SHA = '4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'
CLASSIFICATION_BASIS_SHA = '0598e6b5fbb64cd7038aa4aada8d99e4cbf11c50f41b9320ac2f8ad2331bba91'
VERSION = 'lab-runtime-input-accounting/v1-candidate'
ADDITION_KINDS = {'successor-code', 'successor-family', 'host-dependency'}
STATUSES = {'required-current-byte', 'historical-metadata-only', 'required-unavailable-byte'}


class Refusal(ValueError):
    pass


def require(value, reason):
    if not value:
        raise Refusal(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    require(type(raw) is bytes and len(raw) <= 64 * 1024 * 1024, 'bounded metadata bytes required')
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, 'duplicate metadata key')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _: require(False, 'nonfinite metadata'))
    except (ValueError, UnicodeError) as error:
        raise Refusal('invalid metadata JSON') from error


def closed(value, fields):
    require(type(value) is dict and set(value) == set(fields), 'closed metadata fields required')


def pin(raw, expected):
    require(type(expected) is str and re.fullmatch('[a-f0-9]{64}', expected), 'independent SHA required')
    require(type(raw) is bytes and sha(raw) == expected, 'independent metadata pin differs')
    return parse(raw)


def row(value):
    closed(value, ('path', 'sha256'))
    name = value['path']
    require(type(name) is str and bool(name) and '\\' not in name and '\x00' not in name, 'unsafe input path')
    path = PurePosixPath(name)
    require(path.as_posix() == name and '..' not in path.parts and name not in ('.', '/'), 'unsafe input path')
    require(type(value['sha256']) is str and re.fullmatch('[a-f0-9]{64}', value['sha256']), 'input SHA required')
    return value


def rows(values):
    require(type(values) is list, 'input rows required')
    for value in values:
        row(value)
    require(len({value['path'] for value in values}) == len(values), 'duplicate input paths')
    return values


class AnchoredPresence:
    """Per-call no-follow metadata only, including fresh absent-link checks."""
    def __init__(self, root):
        root = Path(root)
        require(root.is_absolute() and root.as_posix() == str(root) and '..' not in root.parts,
                'absolute canonical input root required')
        self.root = PurePosixPath(root.as_posix())
        self.handles = {}
        self.links = []
        self.files = []
        self.absences = []

    @staticmethod
    def identity(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_uid,
                value.st_size, value.st_mtime_ns, value.st_ctime_ns)

    def directory(self, parts):
        if parts in self.handles:
            return self.handles[parts]
        if not parts:
            handle = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        else:
            parent = self.directory(parts[:-1])
            handle = os.open(parts[-1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                             dir_fd=parent)
            value = os.fstat(handle)
            require(stat.S_ISDIR(value.st_mode) and value.st_mode & 0o111, 'unsafe input directory')
            self.links.append((parent, parts[-1], handle, value.st_dev, value.st_ino))
        self.handles[parts] = handle
        return handle

    def inspect(self, value, *, unavailable):
        row(value)
        path = PurePosixPath(value['path'])
        if not path.is_absolute():
            path = self.root / path
        parts = path.parts[1:]
        parent = self.directory(())
        prefix = ()
        for index, name in enumerate(parts):
            final = index == len(parts) - 1
            try:
                if not final:
                    parent = self.directory(prefix + (name,))
                    prefix += (name,)
                    continue
                handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                                 dir_fd=parent)
                try:
                    before = os.fstat(handle)
                    require(stat.S_ISREG(before.st_mode) and before.st_mode & 0o444, 'unsafe/unreadable input identity')
                    require(not unavailable, 'selected unavailable original locator exists or was restored')
                    current = os.stat(name, dir_fd=parent, follow_symlinks=False)
                    require(self.identity(before) == self.identity(current), 'input attachment changed')
                    self.files.append((parent, name, self.identity(before)))
                finally:
                    os.close(handle)
                return {'status': 'PRESENT-REGULAR-METADATA-ONLY', 'body_read': False}
            except OSError as error:
                if error.errno != errno.ENOENT:
                    raise Refusal('unsafe/unreadable input locator') from error
                require(unavailable, 'required current input absent')
                self.absences.append((parent, name))
                return {'status': 'MISSING-ORIGINAL-LOCATOR',
                        'absent_component': '/' + '/'.join(parts[:index + 1]), 'body_read': False}
        raise Refusal('invalid input locator')

    def finish(self):
        for parent, name in self.absences:
            try:
                os.stat(name, dir_fd=parent, follow_symlinks=False)
            except OSError as error:
                if error.errno == errno.ENOENT:
                    continue
                raise Refusal('unreadable unavailable input recheck') from error
            raise Refusal('unavailable original locator restored during accounting')
        for parent, name, expected in self.files:
            value = os.stat(name, dir_fd=parent, follow_symlinks=False)
            require(self.identity(value) == expected and stat.S_ISREG(value.st_mode), 'current input identity changed')
        for parent, name, handle, device, inode in reversed(self.links):
            value = os.stat(name, dir_fd=parent, follow_symlinks=False)
            held = os.fstat(handle)
            require(stat.S_ISDIR(value.st_mode) and (value.st_dev, value.st_ino) ==
                    (held.st_dev, held.st_ino) == (device, inode), 'input directory attachment changed')

    def close(self):
        for parts in sorted(self.handles, key=len, reverse=True):
            os.close(self.handles[parts])


def verify(source_raw, profile_raw, unavailable_raw, unavailable_sha,
           selection_raw, selection_sha, current_files, root):
    """Run before/after the actual full current byte guard; never returns its PASS.

    The host independently selects the unavailable ledger and full successor
    addition/consumption inventory. It cannot derive expected pins from request
    content. Every declared dependency must have a consumption disposition and
    be in the exact current guard list, or explicitly unavailable and blocked.
    """
    source = pin(source_raw, SOURCE_SHA)
    profile = pin(profile_raw, PROFILE_SHA)
    original = rows(source['files'])
    profile_rows = rows(profile['files'])
    require(len(original) == SOURCE_ROWS and len(profile_rows) == PROFILE_ROWS, 'original full row count differs')
    by_path = {value['path']: value for value in original}
    require(all(by_path.get(value['path']) == value for value in profile_rows), 'original profile row outside source')
    require(unavailable_sha == UNAVAILABLE_SHA, 'exact independently reviewed unavailable selection required')
    missing = pin(unavailable_raw, unavailable_sha)
    closed(missing, ('schema_version', 'rows', 'parent_source_sha256', 'parent_profile_sha256',
                     'classification_basis_sha256', 'historical_physical_closure', 'authority_effect'))
    require(missing['schema_version'] == 'lab-exact-unavailable-original-inputs/v1' and
            missing['parent_source_sha256'] == SOURCE_SHA and missing['parent_profile_sha256'] == PROFILE_SHA and
            missing['classification_basis_sha256'] == CLASSIFICATION_BASIS_SHA and
            missing['historical_physical_closure'] == 'REFUSED' and missing['authority_effect'] == 'none',
            'unavailable classification cannot grant historical closure')
    require(type(missing['rows']) is list and len(missing['rows']) == 25, 'exact 25 unavailable rows required')
    unavailable = {}
    for entry in missing['rows']:
        closed(entry, ('binding', 'classification', 'body_export_allowed'))
        binding = row(entry['binding'])
        require(entry['classification'] in ('protected-historical-source', 'historical-repository-provenance',
                'historical-source-without-body-export-authority', 'historical-native-executable') and
                entry['body_export_allowed'] is False, 'unknown/unsafe unavailable classification')
        require(by_path.get(binding['path']) == binding and binding['path'] not in unavailable,
                'unavailable input outside exact parent or duplicate')
        unavailable[binding['path']] = entry
    selected = pin(selection_raw, selection_sha)
    closed(selected, ('schema_version', 'source_sha256', 'profile_sha256', 'unavailable_sha256',
                      'additions', 'consumption', 'authority_effect', 'claim_ceiling'))
    require(selected['schema_version'] == VERSION and selected['source_sha256'] == SOURCE_SHA and
            selected['profile_sha256'] == PROFILE_SHA and selected['unavailable_sha256'] == unavailable_sha and
            selected['authority_effect'] == 'none', 'input selection parent differs')
    require(type(selected['additions']) is list, 'explicit additions required')
    additions = []
    for entry in selected['additions']:
        closed(entry, ('binding', 'classification', 'selection_reason'))
        value = row(entry['binding'])
        require(entry['classification'] in ADDITION_KINDS and type(entry['selection_reason']) is str and
                bool(entry['selection_reason'].strip()), 'unknown/unexplained addition')
        require(value['path'] not in by_path, 'new input aliases an original locator')
        additions.append(value)
    rows(additions)
    require([v['path'] for v in additions] == sorted(v['path'] for v in additions), 'addition ordering differs')
    expected_current = [value for value in original if value['path'] not in unavailable] + additions
    require(rows(current_files) == expected_current, 'current guard omitted/reordered/substituted/undeclared input')
    expected_all = original + additions
    require(type(selected['consumption']) is list and len(selected['consumption']) == len(expected_all),
            'complete consumed-input status required')
    for expected, entry in zip(expected_all, selected['consumption']):
        closed(entry, ('binding', 'status', 'basis'))
        require(entry['binding'] == expected and entry['status'] in STATUSES and
                type(entry['basis']) is str and bool(entry['basis'].strip()), 'consumption row/order/type differs')
        if expected['path'] in unavailable:
            require(entry['status'] == 'historical-metadata-only', 'unavailable original byte required by selected callback')
        else:
            require(entry['status'] == 'required-current-byte', 'present original/addition excluded from current guard')
    probe = AnchoredPresence(root)
    dispositions = []
    try:
        for value in expected_all:
            absence = value['path'] in unavailable
            observed = probe.inspect(value, unavailable=absence)
            dispositions.append({'binding': value, 'selection': 'historical-unavailable' if absence else 'current-guard-required',
                                 **observed})
        probe.finish()
    except OSError as error:
        raise Refusal('input custody changed/unreadable during accounting') from error
    finally:
        probe.close()
    return {'schema_version': VERSION, 'result': 'METADATA-ACCOUNTING-OBSERVED',
            'original_source_sha256': SOURCE_SHA, 'original_profile_sha256': PROFILE_SHA,
            'original_source_files': original, 'original_profile_files': profile_rows,
            'dispositions': dispositions, 'current_guard_files': current_files,
            'historical_original_physical_closure': 'REFUSED', 'unavailable_original_count': len(unavailable),
            'original_tables_byte_identical': True, 'input_bodies_read_or_exported': False,
            'current_execution_byte_guard': 'REQUIRED-SEPARATE-NOT-RUN-BY-ACCOUNTING',
            'signed_history_schema_source_custody_callbacks': 'REQUIRED-UNCHANGED-SEPARATE',
            'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False}
