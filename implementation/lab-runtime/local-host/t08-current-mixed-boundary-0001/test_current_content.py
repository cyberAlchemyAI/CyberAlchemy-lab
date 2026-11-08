"""Focused current Source/accounting join controls on selected public bytes."""

import copy
import hashlib
import json
from pathlib import Path
import types
import unittest

import current_content as C


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Reader:
    def __init__(self):
        base = 'product/lab/release-candidates/v1/interface/api-integration-v33-current-0001/'
        self.anchor = types.SimpleNamespace(
            source_binding={'ref': base + 'source-manifest.json', 'sha256': C.SOURCE_SHA},
            profile_binding={'ref': base + 'contract-profile.json', 'sha256': C.PROFILE_SHA})
        self.files = {}
        self.payloads = {}
        self.roots = {'repo': {'path': str(C.ROOT)}}
        self.calls = []
        self.selector = {'proof_tables': []}
        source = self.add('source', self.anchor.source_binding['ref'], 'source-manifest')
        profile = self.add('profile', self.anchor.profile_binding['ref'], 'contract-profile')
        account = self.add('account', C.ACCOUNT_PATH, 'execution-selection')
        self.selector['proof_tables'].append({'file_id': 'source', 'row_selector': '/files',
                                              'coverage_file_ids': ['account']})
        proof_ids = []
        for i, binding in enumerate(C._base.ACCOUNTING_SOURCE_LINKS.values()):
            ident = f'proof-{i}'
            self.add(ident, binding['path'], 'history-proof')
            proof_ids.append(ident)
        self.selector['proof_tables'].append({'file_id': 'profile', 'row_selector': '/files',
                                              'coverage_file_ids': proof_ids})
        native = C._base.ACCOUNTING_FIXED['native_reprovision']
        self.add('installed', native['installed_binding']['path'], 'host-dependency')
        self.add('deployment', native['deployment_terminal_binding']['path'], 'history-proof')
        assert sha(source) == C.SOURCE_SHA and sha(profile) == C.PROFILE_SHA
        assert sha(account) == C.ACCOUNT_SHA

    def add(self, ident, logical, kind):
        path = Path(logical)
        physical = path if path.is_absolute() else C.ROOT / path
        raw = physical.read_bytes()
        self.files[ident] = {'id': ident, 'logical_path': logical, 'sha256': sha(raw),
                             'kind': kind, 'root_id': 'repo', 'path': logical,
                             'size': len(raw), 'mode': 0o755 if ident == 'installed' else 0o600,
                             'uid': __import__('os').geteuid()}
        self.payloads[ident] = raw
        return raw

    def read(self, ident, kind):
        self.calls.append(ident)
        row = self.files[ident]
        if row['kind'] != kind or sha(self.payloads[ident]) != row['sha256']:
            raise ValueError('selected fixture bytes differ')
        return self.payloads[ident]


def port(reader):
    value = object.__new__(C.PrivateHistoricalContent)
    value.reader = reader
    value.P = types.SimpleNamespace(parse=json.loads)
    value.root = C.ROOT
    value.value = {'current_accounting_file_id': 'account',
                   'installed_native_file_id': 'installed', 'coverage': []}
    return value


class CurrentStandingTests(unittest.TestCase):
    def setUp(self):
        self.reader = Reader()
        self.port = port(self.reader)

    def test_selected_current_source_and_profile_join(self):
        result = self.port.current_standing()
        self.assertEqual((result['restored_originals'], result['original_alternates'],
                          result['recovered_contents'], result['installed_native_witnesses']),
                         (23, 2, 3, 1))
        self.assertEqual(result['authority_effect'], 'none')
        self.assertTrue(all(f'proof-{i}' in self.reader.calls for i in range(5)))

    def test_missing_accounting_source_proof_refuses(self):
        self.reader.selector['proof_tables'][0]['coverage_file_ids'] = []
        with self.assertRaisesRegex(ValueError, 'typed proof differs'):
            self.port.current_standing()

    def test_substituted_profile_provenance_refuses(self):
        self.reader.selector['proof_tables'][1]['coverage_file_ids'].pop()
        with self.assertRaisesRegex(ValueError, 'not selected as profile proof'):
            self.port.current_standing()

    def test_changed_native_host_witness_refuses(self):
        self.reader.files['installed']['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'native witness'):
            self.port.current_standing()

    def test_accounting_byte_substitution_refuses(self):
        self.reader.payloads['account'] = b'{}'
        with self.assertRaisesRegex(ValueError, 'selected fixture bytes differ'):
            self.port.current_standing()


if __name__ == '__main__':
    unittest.main()
