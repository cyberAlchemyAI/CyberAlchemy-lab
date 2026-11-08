"""Pure pair boundary, redaction, and no-replace tests; no child is launched."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from t35_external_v1.path_contract import ContractError
from t35_external_v1 import evidence_guard
from t35_external_v1.phase_scoped_v2 import prefix_pair_diagnostic_0001 as pairmod


def selected():
    captured = {f'fixture/input-{index:04d}.json': str(index).encode()
                for index in range(1703)}
    rows = {name: {'path': name, 'sha256': hashlib.sha256(raw).hexdigest()}
            for name, raw in captured.items()}
    return rows, captured


def episode(hours=24):
    now = datetime.now(timezone.utc)
    return pairmod._json({'not_before': (now-timedelta(minutes=1)).isoformat(),
                          'expires_at': (now+timedelta(hours=hours)).isoformat()})


def success(vector, selection=None):
    if selection is None:
        selection = {'plan_leaf': 'a'*64, 'stage_control': 'b'*64,
                     'source_manifest': 'c'*64}
    result = {key: 1 for key in pairmod.SAFE_RESULT_COUNTS}
    result.update({key: 'd'*64 for key in pairmod.SAFE_RESULT_HASHES})
    result.update({key: True for key in pairmod.SAFE_RESULT_TRUE})
    result.update(pairmod.SAFE_RESULT_EXACT)
    result.update({'plan_leaf_sha256': selection.get('plan_leaf', 'd'*64),
                   'stage_selection_sha256': selection.get('stage_control', 'd'*64),
                   'source_manifest_sha256': selection.get('source_manifest', 'd'*64),
                   'source_argv_shape': ['/secret/never-publish'],
                   'reader_argv_shape': ['/secret/never-publish']})
    child = {'return_code': 0, 'stdout_bytes': 0, 'stdout_sha256': 'e'*64,
             'stderr_bytes': 0, 'stderr_sha256': 'e'*64}
    return {'status': 'PASS-disposable-prefix-diagnostic',
            'input_vector_sha256': vector.sha256, 'result': result,
            'child_results': {'source': dict(child), 'reader': dict(child)},
            'selection_sha256': selection, 'scratch_cleanup_observed': True,
            'raw_stdout_stderr_or_exception_published': False,
            'actual_host_qualification': False, 'activation_allowed': False}


def failed(vector, clean=True):
    return {'status': 'FAIL-disposable-prefix-diagnostic',
            'input_vector_sha256': vector.sha256,
            'failure_stage': 'reader_child_postreturn', 'failure_code': 'CHILD_NONZERO',
            'child_results': {}, 'selection_sha256': {'source_manifest': 'c'*64},
            'scratch_cleanup_observed': clean,
            'raw_stdout_stderr_or_exception_published': False,
            'actual_host_qualification': False, 'activation_allowed': False}


class PairDiagnosticTests(unittest.TestCase):
    def vector(self):
        rows, captured = selected()
        return pairmod.FrozenVector.from_selected(rows, captured, episode(), b'fixed role\n')

    def test_frozen_vector_copies_rows_and_refuses_drift(self):
        rows, captured = selected()
        vector = pairmod.FrozenVector.from_selected(rows, captured, episode(), b'role\n')
        rows['fixture/input-0000.json']['sha256'] = '0'*64
        captured['fixture/input-0000.json'] = b'changed'
        self.assertEqual(vector.captured()['fixture/input-0000.json'], b'0')
        with self.assertRaises(ContractError):
            pairmod.FrozenVector.from_selected(rows, captured, episode(), b'role\n')
        good_rows, good_captured = selected()
        with self.assertRaises(ContractError):
            pairmod.FrozenVector.from_selected(dict(list(good_rows.items())[:-1]),
                                               good_captured, episode(), b'role\n')

    def test_two_attempts_equal_selection_and_private_argv_redacted(self):
        vector = self.vector()
        published = []
        def publisher(number, safe):
            published.append((number, safe))
            return {'path': f'attempt-{number}', 'sha256': 'f'*64, 'size_bytes': 1}
        with patch.object(pairmod, 'diagnose', side_effect=[success(vector), success(vector)]) as run:
            result = pairmod.pair(vector, publish_attempt=publisher)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(result['status'], 'PASS-two-disposable-attempts')
        self.assertTrue(result['same_captured_input_vector'])
        self.assertTrue(result['derived_selection_equal_when_both_observed'])
        self.assertFalse(result['full_execution_inputs_identical'])
        self.assertEqual([number for number, _ in published], [1, 2])
        self.assertNotIn('/secret/never-publish', json.dumps(result))

    def test_missing_or_divergent_derived_selection_not_equal(self):
        vector = self.vector()
        for selection in ({}, {'plan_leaf': 'a'*64},
                          {'plan_leaf': 'a'*64, 'stage_control': 'b'*64,
                           'source_manifest': 'f'*64}):
            with patch.object(pairmod, 'diagnose', side_effect=[success(vector),
                                                               success(vector, selection)]):
                result = pairmod.pair(vector)
                self.assertEqual(result['status'], 'INCOMPLETE-or-mixed-disposable-attempts')
                self.assertTrue(result['same_captured_input_vector'])
                if len(selection) != 3:
                    self.assertEqual(result['attempts'][1]['status'], 'FAIL-attempt-result-schema')
                    self.assertIsNone(result['derived_selection_equal_when_both_observed'])
                else:
                    self.assertFalse(result['derived_selection_equal_when_both_observed'])

    def test_refusal_retained_and_unclean_scratch_stops_second(self):
        vector = self.vector()
        with patch.object(pairmod, 'diagnose', side_effect=[failed(vector), success(vector)]) as run:
            result = pairmod.pair(vector)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(result['attempts'][0]['failure_code'], 'CHILD_NONZERO')
        with patch.object(pairmod, 'diagnose', side_effect=[failed(vector, False)]) as run:
            stopped = pairmod.pair(vector)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(stopped['attempts'][1]['status'], 'SKIPPED-unclean-prior-attempt')

    def test_episode_must_cover_registered_pair_window(self):
        self.assertEqual(pairmod._episode_window(self.vector())['effect_capture_watchdog_seconds'], 900)
        rows, captured = selected()
        short = pairmod.FrozenVector.from_selected(rows, captured, episode(0), b'role')
        with self.assertRaises(ContractError):
            pairmod._episode_window(short)
        old = pairmod._json({'not_before': (datetime.now(timezone.utc)-timedelta(days=2)).isoformat(),
                             'expires_at': (datetime.now(timezone.utc)-timedelta(days=1)).isoformat()})
        expired = pairmod.FrozenVector.from_selected(rows, captured, old, b'role')
        with self.assertRaises(ContractError):
            pairmod._episode_window(expired)

    def test_no_replace_receipts_publish_between_attempts(self):
        rows, captured = selected()
        with tempfile.TemporaryDirectory() as scratch, \
             patch.object(pairmod.source, '_source_rows', return_value=(rows, captured)) as source_read, \
             patch.object(pairmod, '_fixture_episode', return_value=episode()) as episode_read, \
             patch.object(pairmod, 'diagnose') as diagnostic, \
             patch.object(evidence_guard, 'EVIDENCE', Path(scratch)), \
             patch.object(evidence_guard, 'publish_numbered',
                          side_effect=lambda name, raw: evidence_guard._publish_in(Path(scratch), name, raw)):
            seen = []
            def run(vector, _deadline):
                seen.append((Path(scratch)/pairmod.ATTEMPT_NAMES[0]).exists())
                return success(vector)
            diagnostic.side_effect = run
            result = pairmod.run_pair(publish=True)
            self.assertEqual(result['status'], 'PASS-two-disposable-attempts')
            self.assertEqual(seen, [False, True])
            source_read.assert_called_once_with()
            episode_read.assert_called_once_with(captured)
            self.assertEqual(sorted(path.name for path in Path(scratch).iterdir()),
                             sorted((*pairmod.ATTEMPT_NAMES, pairmod.SUMMARY_NAME)))
            for name in pairmod.ATTEMPT_NAMES:
                self.assertNotIn(b'/secret/never-publish', (Path(scratch)/name).read_bytes())
            with self.assertRaises(ContractError):
                pairmod.run_pair(publish=True)
            self.assertEqual(diagnostic.call_count, 2)

    def test_partial_leaf_blocks_restart_and_alarm_is_suspended_during_publish(self):
        with tempfile.TemporaryDirectory() as scratch, \
             patch.object(evidence_guard, 'EVIDENCE', Path(scratch)), \
             patch.object(evidence_guard, 'publish_numbered',
                          side_effect=lambda name, raw: evidence_guard._publish_in(Path(scratch), name, raw)):
            with pairmod._wall_watchdog():
                with pairmod._receipt_write_window():
                    self.assertEqual(signal.getitimer(signal.ITIMER_REAL)[0], 0)
                    self.assertIn(signal.SIGALRM,
                                  signal.pthread_sigmask(signal.SIG_BLOCK, set()))
                    evidence_guard.publish_numbered(pairmod.ATTEMPT_NAMES[0], b'partial\n')
            with self.assertRaises(ContractError):
                pairmod._preflight_evidence_names()

    def test_second_attempt_interruption_preserves_first_receipt_binding(self):
        rows, captured = selected()
        with tempfile.TemporaryDirectory() as scratch, \
             patch.object(pairmod.source, '_source_rows', return_value=(rows, captured)), \
             patch.object(pairmod, '_fixture_episode', return_value=episode()), \
             patch.object(pairmod, 'diagnose') as diagnostic, \
             patch.object(evidence_guard, 'EVIDENCE', Path(scratch)), \
             patch.object(evidence_guard, 'publish_numbered',
                          side_effect=lambda name, raw: evidence_guard._publish_in(Path(scratch), name, raw)):
            vector_holder = []
            def run(vector, _deadline):
                vector_holder.append(vector)
                if len(vector_holder) == 2:
                    raise RuntimeError('private second-attempt error text')
                return success(vector)
            diagnostic.side_effect = run
            result = pairmod.run_pair(publish=True)
            self.assertEqual(result['status'], 'FAIL-pair-controller')
            self.assertEqual(len(result['attempt_receipt_bindings']), 1)
            self.assertTrue((Path(scratch)/pairmod.ATTEMPT_NAMES[0]).exists())
            self.assertFalse((Path(scratch)/pairmod.ATTEMPT_NAMES[1]).exists())
            raw = (Path(scratch)/pairmod.SUMMARY_NAME).read_bytes()
            self.assertNotIn(b'private second-attempt error text', raw)
            self.assertEqual(json.loads(raw)['attempt_receipt_bindings'],
                             result['attempt_receipt_bindings'])

    def test_unknown_nested_success_payload_becomes_sanitized_failure(self):
        vector = self.vector()
        malicious = success(vector)
        malicious['result']['raw_private'] = '/secret/never-publish'
        with patch.object(pairmod, 'diagnose', side_effect=[malicious]):
            result = pairmod.pair(vector)
        self.assertEqual(result['attempts'][0]['status'], 'FAIL-attempt-result-schema')
        self.assertEqual(result['attempts'][1]['status'], 'SKIPPED-unclean-prior-attempt')
        self.assertNotIn('/secret/never-publish', json.dumps(result))

    def test_child_timeout_is_capped_by_remaining_pair_window(self):
        with patch.object(pairmod.time, 'monotonic', return_value=100.0):
            self.assertEqual(pairmod._remaining_child_seconds(250.0), 150)
            self.assertEqual(pairmod._remaining_child_seconds(500.0), 180)
            with self.assertRaises(ContractError):
                pairmod._remaining_child_seconds(100.5)

    def test_inherited_mask_refuses_before_watchdog_or_effect(self):
        prior_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            with self.assertRaises(ContractError):
                with pairmod._wall_watchdog():
                    self.fail('masked watchdog entered effect scope')
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, prior_mask)


if __name__ == '__main__':
    unittest.main()
