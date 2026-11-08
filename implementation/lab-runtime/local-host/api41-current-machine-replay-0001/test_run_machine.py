"""Bounded cold evidence-selection tests; no native replay."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import run_machine as R


def complete_99():
    ids = R.expected_v4_ids()
    return {
        'successor_manifest_sha256': R.V4_SOURCE_SHA,
        'tests_run': 99,
        'exact_whole_class_coverage': True,
        'expired_original_negative_passed': True,
        'current_legacy_machine_context_get_passed': True,
        'wrong_origin_old_source_refused': True,
        'harness_unchanged_during_run': True,
        'source_unchanged_during_run': True,
        't06_operator_unchanged_during_run': True,
        'stable_native_executable_unchanged_during_run': True,
        'selected_case_ids': ids,
        'case_rows': [{'test_id': case, 'result': 'PASS'} for case in ids],
        'class_case_counts': {name: count for name, (_, count) in R.V4_CLASSES.items()},
        'errors': [], 'failures': [],
        'harness_bindings': [{'path': path, 'sha256': digest} for path, digest in R.V4_HARNESS.items()],
        'result': 'FAIL',  # Frozen appended current-Machine refusal must not erase the 99 PASS rows.
        'current_source8_machine_context_get_passed': False,
        'current_source8_machine_case_rows': [],
        'current_source8_machine_errors': [[
            'setUpClass (' + R.V4_MODULE + '.test_machine_transport.MachineTransport)',
            'AttributeError: SelectedReader module has no CurrentFixtureReader',
        ]],
        'current_source8_machine_failures': [],
    }


class ColdEvidenceSelection(unittest.TestCase):
    def selected(self, value):
        working = R.HERE / 'working'
        working.mkdir(mode=0o700, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=working) as directory:
            path = Path(directory) / 'v4-result.json'
            path.write_text(json.dumps(value))
            with patch.object(R, 'V4', path):
                return R.prior_99(R.sha(path))

    def test_99_exact_cases_survive_appended_machine_refusal(self):
        selected = self.selected(complete_99())
        self.assertEqual(selected['case_count'], 99)
        self.assertEqual(selected['combined_v4_result'], 'FAIL')

    def test_duplicate_or_missing_case_refused(self):
        value = complete_99()
        value['case_rows'][-1] = dict(value['case_rows'][0])
        with self.assertRaises(ValueError):
            self.selected(value)

    def test_changed_frozen_source_refused(self):
        value = complete_99()
        value['successor_manifest_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            self.selected(value)

    def test_swapped_selected_id_refused(self):
        value = complete_99()
        value['selected_case_ids'][0] = 'unselected.case'
        with self.assertRaises(ValueError):
            self.selected(value)

    def test_one_failed_case_refused(self):
        value = complete_99()
        value['case_rows'][27]['result'] = 'FAIL'
        with self.assertRaises(ValueError):
            self.selected(value)

    def test_changed_native_executable_refused(self):
        value = complete_99()
        value['stable_native_executable_unchanged_during_run'] = False
        with self.assertRaises(ValueError):
            self.selected(value)

    def test_unattributed_combined_failure_refused(self):
        value = complete_99()
        value['current_source8_machine_errors'][0][1] = 'some other failure'
        with self.assertRaises(ValueError):
            self.selected(value)

    def test_wrong_expected_result_digest_refused(self):
        with tempfile.TemporaryDirectory(dir=R.HERE / 'working') as directory:
            path = Path(directory) / 'v4-result.json'
            path.write_text(json.dumps(complete_99()))
            with patch.object(R, 'V4', path), self.assertRaises(ValueError):
                R.prior_99('0' * 64)

    def test_exact_selected_machine_method(self):
        self.assertEqual(R.method_ast_sha(), R.MACHINE_METHOD_AST_SHA)

    def test_captured_verified_module_ignores_import_window_swap(self):
        with tempfile.TemporaryDirectory(dir=R.HERE / 'working') as directory:
            path = Path(directory) / '__init__.py'
            path.write_text("VALUE = 'verified'\n")
            captured = R.exact(path, R.sha(path))
            path.write_text("VALUE = 'swapped'\n")
            name = '_cal_machine_pinned_import_test_' + path.parent.name.replace('-', '_')
            finder = R.PinnedAPIFinder(name, {'__init__.py': (path, captured)})
            sys.meta_path.insert(0, finder)
            try:
                module = importlib.import_module(name)
                self.assertEqual(module.VALUE, 'verified')
            finally:
                sys.meta_path.remove(finder)
                sys.modules.pop(name, None)

    def test_result_symlink_and_existing_file_refused_without_overwrite(self):
        with tempfile.TemporaryDirectory(dir=R.HERE / 'working') as directory:
            parent = Path(directory)
            target = parent / 'outside.txt'
            target.write_text('unchanged')
            path = parent / 'result.json'
            path.symlink_to(target)
            with self.assertRaises(FileExistsError):
                R.write_result_once({'result': 'PASS'}, path)
            self.assertEqual(target.read_text(), 'unchanged')
            path.unlink()
            R.write_result_once({'result': 'PASS'}, path)
            with self.assertRaises(FileExistsError):
                R.write_result_once({'result': 'changed'}, path)
            self.assertEqual(json.loads(path.read_text()), {'result': 'PASS'})

    def test_result_directory_symlink_refused(self):
        with tempfile.TemporaryDirectory(dir=R.HERE / 'working') as directory:
            base = Path(directory)
            outside = base / 'outside'
            outside.mkdir(mode=0o700)
            alias = base / 'alias'
            alias.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(OSError):
                R.write_result_once({'result': 'PASS'}, alias / 'result.json')
            self.assertFalse((outside / 'result.json').exists())

    def test_reader_origin_refusal_accepts_only_exact_predicate(self):
        def exact():
            raise ValueError(R.READER_ORIGIN_REFUSAL)
        def unrelated():
            raise ValueError('some unrelated source integrity failure')
        self.assertTrue(R.exact_reader_origin_refusal(exact))
        with self.assertRaisesRegex(ValueError, 'unrelated source integrity'):
            R.exact_reader_origin_refusal(unrelated)
        with self.assertRaisesRegex(ValueError, 'wrong Reader origin was accepted'):
            R.exact_reader_origin_refusal(lambda: None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
