"""Closed original role selection over the accepted C01 reader.

This module has two explicitly inert postures. Public metadata can be read from
selected original documents; protected bodies can only be read in an explicitly
owned fixture. Neither entry point supplies actual host custody. The selected
policy, source/profile/cut and complete table descriptors are caller trust inputs
chosen before construction, never derived from the document being verified.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
import time
from lab_contracts.codec import canonical, parse, need, closed, Refusal, sha
from lab_contracts.validation import validate
from lab_selectors.anchors import AnchoredReader, legacy_json, relative
from lab_selectors.source_inventory import retain

MAX_READ = 64 * 1024 * 1024
ROLE_KINDS = {
    'governed-record': ('semantic', 'protected-input'),
    'governed-schema': ('execution', 'protected-input'),
    'governed-descriptor': ('execution', 'protected-input'),
    'semantic-policy': ('execution', 'protected-input'),
    'source-manifest': ('evidence', 'protected-input'),
    'contract-profile': ('evidence', 'protected-input'),
    'execution-selection': ('execution', 'protected-input'),
    'environment-contract': ('execution', 'protected-input'),
    'history-proof': ('evidence', 'protected-input'),
    'recovery-proof': ('evidence', 'protected-input'),
    'public-package': ('public-package',),
    'host-dependency': ('execution', 'protected-input'),
    'custody-state': ('evidence', 'protected-input'),
}

# Only independently fixed diagnostics cross this adapter boundary. In particular,
# a provider's Refusal is not trusted merely because it uses our exception type.
PUBLIC_CODES = frozenset(('READ_LIMIT', 'ACTUAL_PROTECTED_READ_GATED',
    'ACTUAL_HOST_PROVIDER_REQUIRED', 'ORIGINAL_ROLE_MISMATCH', 'ROLE_BINDING_KIND',
    'FIXTURE_PERMISSION_EXPIRED', 'FIXTURE_PERMISSION_SCOPE',
    'FIXTURE_PERMISSION_SELECTION', 'INDEPENDENT_ROLE_SELECTION',
    'SOURCE_PROFILE_CUT', 'INDEPENDENT_TABLE_SELECTION',
    'PROTECTED_TABLE_DOCUMENT_GATED', 'PERMISSION_READER_DOMAIN', 'ROLE_READER_REFUSED'))


def public_failure(error):
    # Do not call an arbitrary exception's __str__, which can itself disclose or
    # execute provider code. Recreate even known refusals to discard private frames.
    code = (error.args[0] if type(error) is Refusal and len(error.args) == 1
            and type(error.args[0]) is str else '')
    return Refusal(code if code in PUBLIC_CODES else 'ROLE_READER_REFUSED')


def public_boundary(function):
    @wraps(function)
    def call(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as error:
            raise public_failure(error) from None
    return call


def clone(value):
    return parse(canonical(value), max_bytes=MAX_READ)


def binding(value):
    validate('ByteBinding', value)
    relative(value['relative_path'])
    return value


def source_cut(value):
    # Original protected-selector source-cut fields, with exact values retained.
    closed(value, ('branch_ref', 'store_ref', 'commit_sequence', 'commit_sha256',
                  'source_profile_sha256', 'streams'))
    for key in ('branch_ref', 'store_ref'):
        need(type(value[key]) is str and 0 < len(value[key]) <= 4096, 'SOURCE_CUT_ID')
    need(type(value['commit_sequence']) is int and 0 <= value['commit_sequence'] < 2**63,
         'SOURCE_CUT_SEQUENCE')
    for key in ('commit_sha256', 'source_profile_sha256'):
        need(type(value[key]) is str and len(value[key]) == 64
             and all(c in '0123456789abcdef' for c in value[key]), 'SOURCE_CUT_DIGEST')
    need(type(value['streams']) is list, 'SOURCE_CUT_STREAMS')
    seen = set()
    for row in value['streams']:
        closed(row, ('stream_ref', 'cursor', 'head_sha256'))
        need(type(row['stream_ref']) is str and row['stream_ref'] and row['stream_ref'] not in seen,
             'SOURCE_CUT_STREAM')
        need(type(row['cursor']) is int and 0 <= row['cursor'] < 2**63, 'SOURCE_CUT_CURSOR')
        need(type(row['head_sha256']) is str and len(row['head_sha256']) == 64
             and all(c in '0123456789abcdef' for c in row['head_sha256']), 'SOURCE_CUT_HEAD')
        seen.add(row['stream_ref'])


@dataclass(frozen=True)
class ReaderSelection:
    policy_binding: dict
    source_binding: dict
    profile_binding: dict
    source_cut: dict
    table_descriptors: list


class FixturePermission:
    """Separately pinned current fixture permission, never an actual credential.

    The test owner selects this binding out of band. A replaced/revoked grant,
    source cut substitution or elapsed deadline refuses before/after the body
    read. The provider's own held-root checks still run through AnchoredReader.
    This is intentionally not a substitute for actual signed host enrollment.
    """
    @public_boundary
    def __init__(self, reader, expected_binding, expected_subject):
        need(type(reader) is AnchoredReader, 'PERMISSION_READER')
        need(type(expected_subject) is str and expected_subject, 'FIXTURE_SUBJECT')
        self._reader = reader
        self._binding = clone(binding(expected_binding))
        need(self._binding['kind'] != 'protected-input', 'PERMISSION_RECURSION')
        self._subject = expected_subject

    @public_boundary
    def check(self, selection, requested):
        grant = parse(self._reader.read(self._binding), max_bytes=MAX_READ)
        closed(grant, ('schema_version', 'posture', 'subject', 'source_binding',
                      'profile_binding', 'source_cut', 'allowed_bindings',
                      'not_before_ns', 'expires_ns', 'authority_effect'))
        need(grant['schema_version'] == 'lab-fixture-reader-permission/v1'
             and grant['posture'] == 'owned-fixture' and grant['authority_effect'] == 'none'
             and grant['subject'] == self._subject, 'FIXTURE_PERMISSION_DOMAIN')
        for name in ('source_binding', 'profile_binding', 'source_cut'):
            need(grant[name] == selection[name], 'FIXTURE_PERMISSION_SELECTION')
        need(type(grant['not_before_ns']) is int and type(grant['expires_ns']) is int
             and 0 <= grant['not_before_ns'] < grant['expires_ns'] < 2**63,
             'FIXTURE_PERMISSION_PERIOD')
        now = time.time_ns()
        need(grant['not_before_ns'] <= now < grant['expires_ns'], 'FIXTURE_PERMISSION_EXPIRED')
        need(type(grant['allowed_bindings']) is list, 'FIXTURE_PERMISSION_BINDINGS')
        keys = [AnchoredReader.key(b) for b in grant['allowed_bindings']]
        need(len(keys) == len(set(keys)), 'FIXTURE_PERMISSION_DUPLICATE')
        if requested is not None:
            need(AnchoredReader.key(requested) in keys, 'FIXTURE_PERMISSION_SCOPE')


class RoleReader:
    """Selected original file roles; no role is inferred from a path or hash."""
    @public_boundary
    def __init__(self, reader, selection, *, posture='public-metadata', permission=None):
        need(type(reader) is AnchoredReader and type(selection) is ReaderSelection,
             'READER_SELECTION_TYPE')
        need(posture in ('public-metadata', 'owned-fixture'), 'ACTUAL_HOST_PROVIDER_REQUIRED')
        need((posture == 'owned-fixture' and type(permission) is FixturePermission)
             or (posture == 'public-metadata' and permission is None), 'READER_POSTURE')
        need(permission is None or permission._reader is reader, 'PERMISSION_READER_DOMAIN')
        self._reader = reader
        self._selection = clone(selection.__dict__)
        self._posture, self._permission = posture, permission
        for key in ('policy_binding', 'source_binding', 'profile_binding'):
            binding(self._selection[key])
            need(self._selection[key]['kind'] != 'protected-input', 'ANCHOR_METADATA_REQUIRED')
        source_cut(self._selection['source_cut'])
        need(self._selection['source_cut']['source_profile_sha256'] ==
             self._selection['profile_binding']['sha256'], 'SOURCE_PROFILE_CUT')
        raw = reader.read(self._selection['policy_binding'])
        self._policy = parse(raw, max_bytes=MAX_READ)
        self._policy_raw = raw
        closed(self._policy, ('schema_version', 'source_binding', 'profile_binding',
                            'source_cut', 'files', 'table_descriptors', 'authority_effect'))
        need(self._policy['schema_version'] == 'lab-original-role-selection/v1'
             and self._policy['authority_effect'] == 'none', 'ROLE_POLICY_DOMAIN')
        for name in ('source_binding', 'profile_binding', 'source_cut', 'table_descriptors'):
            need(self._policy[name] == self._selection[name], 'INDEPENDENT_ROLE_SELECTION')
        need(type(self._selection['table_descriptors']) is list, 'TABLE_DESCRIPTORS')
        for descriptor in self._selection['table_descriptors']:
            need(type(descriptor) is dict and 'document_binding' in descriptor,
                 'TABLE_DESCRIPTOR')
            need(binding(descriptor['document_binding'])['kind'] != 'protected-input',
                 'PROTECTED_TABLE_DOCUMENT_GATED')
        need(type(self._policy['files']) is list, 'ROLE_FILES')
        self._files = {}
        selected_bindings = set()
        for row in self._policy['files']:
            closed(row, ('file_id', 'binding', 'logical_path', 'kind'))
            key = row['file_id']
            need(type(key) is str and 0 < len(key) <= 4096 and key not in self._files,
                 'ROLE_FILE_ID')
            relative(row['logical_path'])
            need(type(row['kind']) is str and row['kind'] in ROLE_KINDS and binding(row['binding'])['kind'] in
                 ROLE_KINDS[row['kind']], 'ROLE_BINDING_KIND')
            token = AnchoredReader.key(row['binding'])
            need(token in reader.allowed and token not in selected_bindings, 'ROLE_MEMBER_SELECTION')
            selected_bindings.add(token)
            self._files[key] = row
        self._depth = 0
        self._guard()

    @property
    @public_boundary
    def files(self):
        return clone(self._files)

    @property
    @public_boundary
    def selection(self):
        return clone(self._selection)

    @property
    def posture(self):
        return self._posture

    def _guard(self):
        need(self._permission is None or self._permission._reader is self._reader,
             'PERMISSION_READER_DOMAIN')
        need(self._reader.read(self._selection['policy_binding']) == self._policy_raw,
             'ROLE_POLICY_CHANGED')
        for name in ('source_binding', 'profile_binding'):
            self._reader.read(self._selection[name])
        if self._permission is not None:
            self._permission.check(self._selection, None)

    @contextmanager
    def boundary(self):
        try:
            outer = self._depth == 0
            if outer:
                self._guard()
            self._depth += 1
            try:
                yield self
            finally:
                self._depth -= 1
                if outer:
                    self._guard()
        except Exception as error:
            # A decorator around a generator would miss enter/exit exceptions.
            raise public_failure(error) from None

    @public_boundary
    def read(self, file_id, expected_role=None, *, max_bytes=MAX_READ):
        # Invalid limits must fail before any provider or boundary read.
        need(type(max_bytes) is int and 0 < max_bytes <= MAX_READ, 'READ_LIMIT')
        need(type(file_id) is str and file_id in self._files, 'UNSELECTED_FILE_ID')
        row = self._files[file_id]
        need(row['binding']['size_bytes'] <= max_bytes, 'READ_LIMIT')
        need(expected_role is None or expected_role == row['kind'], 'ORIGINAL_ROLE_MISMATCH')
        protected = row['binding']['kind'] == 'protected-input'
        need(not protected or self._posture == 'owned-fixture', 'ACTUAL_PROTECTED_READ_GATED')
        with self.boundary():
            if protected:
                self._permission.check(self._selection, row['binding'])
            raw = self._reader.read(row['binding'], max_bytes=max_bytes)
            if protected:
                self._permission.check(self._selection, row['binding'])
            return raw

    @public_boundary
    def inventory(self, descriptors):
        # Keep whole ordered rows, repeated identities and all metadata fields.
        # retain() reads only selected documents, never any row's member locator.
        with self.boundary():
            return retain(self._reader, descriptors, self._selection['table_descriptors'])

    @public_boundary
    def public_summary(self):
        # No body, private path, source locator or grant content may enter evidence.
        return {'schema_version': 'lab-role-reader-summary/v1',
                'posture': self._posture, 'selected_files': len(self._files),
                'policy_sha256': sha(self._policy_raw), 'authority_effect': 'none',
                'actual_protected_custody': False, 'semantic_admission': False}
