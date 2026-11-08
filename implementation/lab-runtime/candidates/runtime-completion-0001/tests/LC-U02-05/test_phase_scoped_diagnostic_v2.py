"""Pure allowlist tests for versioned Source/Reader diagnostic receipts."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1.path_contract import ContractError
from t35_external_v1.phase_scoped_v2 import prefix_diagnostic_0001 as diagnostic


class PrefixDiagnosticTests(unittest.TestCase):
    def test_closed_stage_and_child_result(self):
        state = diagnostic.DiagnosticState()
        with self.assertRaises(ContractError):
            state.step('arbitrary-private-path')
        state.step('source_child_postreturn')
        state.child('source', 124, b'fixture secret stdout', b'fixture secret stderr')
        with self.assertRaises(ContractError):
            state.child('source', 0, b'', b'')
        with self.assertRaises(ContractError):
            state.child('mapped', 0, b'', b'')
        row = diagnostic.sanitized_failure(state, ContractError('secret exception path'))
        self.assertEqual(row['failure_stage'], 'source_child_postreturn')
        self.assertEqual(row['failure_code'], 'CHILD_TIMEOUT')
        self.assertEqual(row['child_results']['source']['return_code'], 124)
        self.assertEqual(row['child_results']['source']['stdout_bytes'], 21)
        self.assertEqual(row['child_results']['source']['stderr_bytes'], 21)
        serialized = json.dumps(row)
        self.assertNotIn('fixture secret', serialized)
        self.assertNotIn('secret exception', serialized)
        self.assertTrue(row['raw_stdout_stderr_or_exception_published'] is False)

    def test_refusal_codes_and_observed_cleanup(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch) / 'owned'
            root.mkdir()
            state = diagnostic.DiagnosticState()
            state.scratch_root = root
            state.step('reader_child_postreturn')
            state.child('reader', 125, b'', b'x')
            first = diagnostic.sanitized_failure(state, ValueError('private raw'))
            self.assertEqual(first['failure_code'], 'CHILD_OUTPUT_LIMIT')
            self.assertFalse(first['scratch_cleanup_observed'])
            root.rmdir()
            second = diagnostic.sanitized_failure(state, ValueError('private raw'))
            self.assertTrue(second['scratch_cleanup_observed'])
        other = diagnostic.DiagnosticState()
        other.step('source_poststate')
        self.assertEqual(diagnostic.sanitized_failure(
            other, ContractError('selected secret'))['failure_code'], 'CONTRACT_REFUSAL')
        self.assertEqual(diagnostic.sanitized_failure(
            other, RuntimeError('selected secret'))['failure_code'], 'UNEXPECTED_EXCEPTION')

    def test_diagnose_catches_failure_without_raw_text(self):
        def broken(state):
            state.step('reader_child_postreturn')
            state.child('reader', 7, b'private stdout', b'private stderr')
            raise ContractError('/home/private/key and fixture signing material')
        with patch.object(diagnostic, 'probe', side_effect=broken):
            result = diagnostic.diagnose()
        self.assertEqual(result['status'], 'FAIL-disposable-prefix-diagnostic')
        self.assertEqual(result['failure_code'], 'CHILD_NONZERO')
        self.assertEqual(result['failure_stage'], 'reader_child_postreturn')
        self.assertEqual(result['child_results']['reader']['return_code'], 7)
        self.assertNotIn('/home/private', json.dumps(result))
        self.assertNotIn('private stdout', json.dumps(result))
        self.assertIsNone(result['scratch_cleanup_observed'])


if __name__ == '__main__':
    unittest.main()
