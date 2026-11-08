"""Inert preflight and synthetic-only stage controller probes."""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import stage_only
from prepare_reader import PRODUCER, sha


class StageOnlyTests(unittest.TestCase):
    def test_live_readonly_selection_and_986_file_plan(self):
        real_read = Path.read_bytes
        def refuse_archive_body(path):
            if str(path).endswith('/packages/0001/branch.snapshot'):
                raise AssertionError('private archive body opened during preflight')
            return real_read(path)
        with patch.object(Path, 'read_bytes', refuse_archive_body):
            result = stage_only.preflight()
        self.assertEqual(result['effect'], 'NOT_RUN')
        self.assertEqual(result['selected_files'], 986)
        self.assertFalse(result['archive_current_bytes_checked'])
        self.assertEqual(result['source_audit'], 'PASS_INERT')
        plan, archive = stage_only.selected_plan()
        self.assertEqual(len(plan), 986)
        self.assertEqual(plan[archive][1], stage_only.ARCHIVE_SHA)
        self.assertEqual(plan[PRODUCER + '/source-manifest.json'][2:], (0o444, 0o444))
        self.assertEqual(plan[PRODUCER + '/packages/0001/manifest.json'][2:], (0o600, 0o600))

    def test_release_apis_refuse_wrong_attempt_before_any_effect(self):
        self.assertTrue(stage_only.STAGE_RELEASE_ENABLED)
        with self.assertRaisesRegex(ValueError, 'selected attempt differs'):
            stage_only.execute(attempt=Path('/tmp/unselected-reader-stage'))
        self.assertFalse(os.path.lexists(stage_only.ATTEMPT))

    def test_expired_period_or_occupied_attempt_refused(self):
        with self.assertRaisesRegex(ValueError, 'expired'):
            stage_only.preflight(now=dt.datetime(2026, 10, 21, 8, 20,
                                                 tzinfo=dt.timezone.utc))
        with tempfile.TemporaryDirectory(dir='/tmp') as temp:
            with self.assertRaisesRegex(ValueError, 'already exists'):
                stage_only.preflight(attempt=Path(temp))

    def test_wrong_predecessor_freeze_refused(self):
        with patch.object(stage_only, 'PREDECESSOR_FREEZE_SHA', '0' * 64):
            with self.assertRaisesRegex(ValueError, '0005 freeze changed'):
                stage_only.preflight()

    def test_wrong_release_base_or_review_refused(self):
        with patch.object(stage_only, 'RELEASE_BASE_FREEZE_SHA', '0' * 64):
            with self.assertRaisesRegex(ValueError, '0007 release base freeze changed'):
                stage_only.preflight()
        with patch.object(stage_only, 'RELEASE_REVIEW_SHA', '0' * 64):
            with self.assertRaisesRegex(ValueError, '0007 independent review changed'):
                stage_only.preflight()

    def test_wrong_stage_plan_receipt_refused(self):
        with patch.object(stage_only, 'STAGE_PLAN_SHA', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'stage-plan bytes changed'):
                stage_only.preflight()

    def test_selected_source_wrong_mode_refused_before_private_read(self):
        plan, archive = stage_only.selected_plan()
        source, digest, _, target_mode = plan[archive]
        altered = dict(plan)
        altered[archive] = (source, digest, 0o444, target_mode)
        with patch.object(stage_only, 'selected_plan', return_value=(altered, archive)):
            with self.assertRaisesRegex(ValueError, 'stage plan does not join executed selection'):
                stage_only.preflight()
            with patch.object(stage_only, 'plan_receipt'):
                with self.assertRaisesRegex(ValueError, 'selected source type/owner/mode differs'):
                    stage_only.preflight()

    @staticmethod
    def fixture(base: Path):
        source_root = base / 'source'
        archive = PRODUCER + '/packages/0001/branch.snapshot'
        period = PRODUCER + '/packages/0001/period.json'
        role = 'product/lab/release-candidates/v1/interface/docker-reader-20261020-0001/base.py'
        raw = {archive: b'synthetic private archive, no historical bytes',
               period: json.dumps({'not_before': '2026-10-20T08:20:00+00:00',
                                   'expires_at': '2026-10-21T08:20:00+00:00'}).encode(),
               role: b'synthetic Reader role'}
        plan = {}
        for name, data in raw.items():
            source = source_root / name
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(data)
            source_mode = 0o600 if name == archive or name == period else 0o644
            source.chmod(source_mode)
            plan[name] = (source, sha(data), source_mode, 0o600 if name == archive or name == period else 0o444)
        return source_root, plan, archive

    def test_synthetic_stage_marker_before_copy_and_exact_outputs(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as temp:
            base = Path(temp)
            source_root, plan, archive = self.fixture(base)
            attempt = base / 'attempt'
            observed = []
            real_copy = stage_only.copy_exact
            def copy_after_marker(*args):
                marker = attempt / 'consumed.json'
                self.assertTrue(marker.is_file())
                self.assertTrue(json.loads(marker.read_bytes())['no_retry'])
                observed.append(args[0])
                return real_copy(*args)
            with patch.object(stage_only, 'STAGE_RELEASE_ENABLED', True), \
                 patch.object(stage_only, 'ATTEMPT', attempt), \
                 patch.object(stage_only, 'SOURCE_ROOT', source_root), \
                 patch.object(stage_only, 'preflight', return_value={'result': 'READY_FOR_INDEPENDENT_REVIEW'}), \
                 patch.object(stage_only, 'selected_plan', return_value=(plan, archive)), \
                 patch.object(stage_only, 'audit', return_value={'result': 'PASS_INERT'}), \
                 patch.object(stage_only, 'copy_exact', side_effect=copy_after_marker):
                result = stage_only.execute(attempt=attempt)
            self.assertEqual(result['overall'], 'OBSERVED_STAGE_ONLY')
            self.assertFalse(result['reader_input_released'])
            self.assertEqual(len(observed), len(plan))
            self.assertEqual((source_root / archive).read_bytes(),
                             b'synthetic private archive, no historical bytes')
            self.assertEqual((attempt / 'root' / archive).read_bytes(),
                             (source_root / archive).read_bytes())
            self.assertTrue((attempt / 'evidence/stage-terminal.json').is_file())
            self.assertEqual(list((attempt / 'reader-output').iterdir()), [])
            self.assertEqual(stat.S_IMODE((attempt / 'root' / archive).stat().st_mode), 0o600)
            extra = attempt / 'root' / 'unexpected.txt'
            extra.write_bytes(b'unselected')
            with self.assertRaisesRegex(ValueError, 'inventory differs'):
                stage_only.verify_stage(attempt / 'root', plan)

    def test_partial_copy_consumed_unknown_retained_and_no_retry(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as temp:
            base = Path(temp)
            source_root, plan, archive = self.fixture(base)
            attempt = base / 'attempt'
            calls = []
            real_copy = stage_only.copy_exact
            def partial(*args):
                calls.append(args[0])
                if len(calls) == 2:
                    raise OSError('synthetic partial-copy failure')
                return real_copy(*args)
            with patch.object(stage_only, 'STAGE_RELEASE_ENABLED', True), \
                 patch.object(stage_only, 'ATTEMPT', attempt), \
                 patch.object(stage_only, 'SOURCE_ROOT', source_root), \
                 patch.object(stage_only, 'preflight', return_value={'result': 'READY_FOR_INDEPENDENT_REVIEW'}), \
                 patch.object(stage_only, 'selected_plan', return_value=(plan, archive)), \
                 patch.object(stage_only, 'copy_exact', side_effect=partial):
                with self.assertRaisesRegex(OSError, 'synthetic partial-copy'):
                    stage_only.execute(attempt=attempt)
                with self.assertRaises(FileExistsError):
                    stage_only.execute(attempt=attempt)
            self.assertTrue((attempt / 'consumed.json').is_file())
            unknown = json.loads((attempt / 'stage-unknown.json').read_bytes())
            self.assertEqual(unknown['overall'], 'UNKNOWN')
            self.assertTrue(unknown['partial_stage_retained_for_review'])
            self.assertFalse((attempt / 'evidence/stage-terminal.json').exists())
            self.assertEqual((source_root / archive).read_bytes(),
                             b'synthetic private archive, no historical bytes')

    def test_marker_write_failure_consumes_attempt_without_private_copy(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as temp:
            base = Path(temp)
            source_root, plan, archive = self.fixture(base)
            attempt = base / 'attempt'
            real_write = stage_only.write_exact
            def marker_fails(path, raw):
                if Path(path).name == 'consumed.json':
                    raise OSError('synthetic marker durability failure')
                return real_write(path, raw)
            with patch.object(stage_only, 'STAGE_RELEASE_ENABLED', True), \
                 patch.object(stage_only, 'ATTEMPT', attempt), \
                 patch.object(stage_only, 'SOURCE_ROOT', source_root), \
                 patch.object(stage_only, 'preflight', return_value={'result': 'READY_FOR_INDEPENDENT_REVIEW'}), \
                 patch.object(stage_only, 'selected_plan', return_value=(plan, archive)), \
                 patch.object(stage_only, 'write_exact', side_effect=marker_fails), \
                 patch.object(stage_only, 'copy_exact') as copy:
                with self.assertRaisesRegex(OSError, 'marker durability failure'):
                    stage_only.execute(attempt=attempt)
                copy.assert_not_called()
            self.assertTrue(attempt.is_dir())
            self.assertEqual(json.loads((attempt / 'stage-unknown.json').read_bytes())['overall'],
                             'UNKNOWN')
            self.assertFalse((attempt / 'root').exists())

    def test_postverify_mutation_refuses_observed_terminal(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as temp:
            base = Path(temp)
            source_root, plan, archive = self.fixture(base)
            attempt = base / 'attempt'
            role = next(name for name in plan if name.endswith('/base.py'))
            def mutate_then_audit():
                staged = attempt / 'root' / role
                staged.chmod(0o644)
                staged.write_bytes(b'mutated after initial verification')
                staged.chmod(0o444)
                return {'result': 'PASS_INERT'}
            with patch.object(stage_only, 'STAGE_RELEASE_ENABLED', True), \
                 patch.object(stage_only, 'ATTEMPT', attempt), \
                 patch.object(stage_only, 'SOURCE_ROOT', source_root), \
                 patch.object(stage_only, 'preflight', return_value={'result': 'READY_FOR_INDEPENDENT_REVIEW'}), \
                 patch.object(stage_only, 'selected_plan', return_value=(plan, archive)), \
                 patch.object(stage_only, 'audit', side_effect=mutate_then_audit):
                with self.assertRaisesRegex(ValueError, 'staged bytes/mode/owner differ'):
                    stage_only.execute(attempt=attempt)
            self.assertEqual(json.loads((attempt / 'evidence/stage-terminal.json').read_bytes())['overall'],
                             'OBSERVED_STAGE_ONLY')
            self.assertEqual(json.loads((attempt / 'stage-unknown.json').read_bytes())['overall'], 'UNKNOWN')

    def test_expiry_during_terminal_persistence_is_unknown(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as temp:
            base = Path(temp)
            source_root, plan, archive = self.fixture(base)
            attempt = base / 'attempt'
            expired = [False]
            real_write = stage_only.write_exact
            def expire_on_terminal(path, raw):
                result = real_write(path, raw)
                if Path(path).name == 'stage-terminal.json':
                    expired[0] = True
                return result
            def observed_period(_period):
                if expired[0]:
                    raise ValueError('Source participation period is not current')
            with patch.object(stage_only, 'STAGE_RELEASE_ENABLED', True), \
                 patch.object(stage_only, 'ATTEMPT', attempt), \
                 patch.object(stage_only, 'SOURCE_ROOT', source_root), \
                 patch.object(stage_only, 'preflight', return_value={'result': 'READY_FOR_INDEPENDENT_REVIEW'}), \
                 patch.object(stage_only, 'selected_plan', return_value=(plan, archive)), \
                 patch.object(stage_only, 'audit', return_value={'result': 'PASS_INERT'}), \
                 patch.object(stage_only, 'period_current', side_effect=observed_period), \
                 patch.object(stage_only, 'write_exact', side_effect=expire_on_terminal):
                with self.assertRaisesRegex(ValueError, 'period is not current'):
                    stage_only.execute(attempt=attempt)
            neutral = json.loads((attempt / 'evidence/stage-terminal.json').read_bytes())
            self.assertEqual(neutral['overall'], 'OBSERVED_STAGE_ONLY')
            self.assertTrue(neutral['unknown_receipt_takes_precedence'])
            self.assertEqual(json.loads((attempt / 'stage-unknown.json').read_bytes())['overall'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
