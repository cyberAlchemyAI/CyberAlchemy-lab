"""Focused cold controls for the disjoint T12/O03 successor."""
import hashlib
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import probe
import query_run

import sys
sys.path.insert(0, str(query_run.HERE / 'engine'))
from lab_runtime.sources import verify_successor_join
from lab_runtime.common import RuntimeFault


class SelectionTests(unittest.TestCase):
    def test_exact_engine_and_query_controls(self):
        self.assertEqual(len(query_run.verify_controls()['files']), 9)

    def test_changed_current_source_refused(self):
        with self.assertRaisesRegex(ValueError, 'current authority source differs'):
            probe.verify_successor('0' * 64)

    def test_changed_query_control_refused(self):
        row = query_run.verify_controls()['files'][0]
        with self.assertRaisesRegex(ValueError, 'selected bytes changed'):
            query_run.selected(row['path'], '0' * 64)

    def test_missing_control_row_refused(self):
        real = query_run.selected
        manifest_path = query_run.CONTROLS.relative_to(query_run.ROOT).as_posix()
        data = json.loads(real(manifest_path, query_run.CONTROLS_SHA))
        data['files'].pop()
        def altered(path, expected):
            if path == manifest_path:
                return json.dumps(data).encode()
            return real(path, expected)
        with patch.object(query_run, 'selected', side_effect=altered):
            with self.assertRaisesRegex(ValueError, 'query control closure changed'):
                query_run.verify_controls()

    def test_equal_byte_linked_parent_refused(self):
        with tempfile.TemporaryDirectory(dir=query_run.HERE) as name:
            base = Path(name)
            (base / 'real').mkdir()
            raw = b'control witness\n'
            (base / 'real' / 'witness').write_bytes(raw)
            (base / 'link').symlink_to(base / 'real', target_is_directory=True)
            rel = (base / 'link' / 'witness').relative_to(query_run.ROOT).as_posix()
            with self.assertRaisesRegex(ValueError, 'unsafe selected path'):
                query_run.selected(rel, hashlib.sha256(raw).hexdigest())

    def test_undeclared_scope_refused(self):
        with self.assertRaisesRegex(ValueError, 'undeclared query scope'):
            query_run.execute('d75-selected-source')

    def test_current_response_cold_replay(self):
        selected = query_run.HERE / 'run-current-0002'
        if selected.exists():
            result = query_run.verify_result(selected)
            self.assertEqual(result['queries']['lifecycle-current-specialist']['status'], 'partial')

    def test_false_local_model_selection_refused(self):
        selected = query_run.HERE / 'run-current-0002'
        if not selected.exists():
            self.skipTest('current query has not completed')
        with tempfile.TemporaryDirectory(dir=query_run.HERE) as name:
            dest = Path(name)
            source = selected / 'lifecycle-current-specialist.json'
            shutil.copyfile(source, dest / source.name)
            result = json.loads((selected / 'RESULT.json').read_bytes())
            result['queries']['lifecycle-current-specialist']['path'] = (dest / source.name).relative_to(query_run.ROOT).as_posix()
            result['selected_governed_models'] = 1
            (dest / 'RESULT.json').write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError, 'query result control/claim set differs'):
                query_run.verify_result(dest)

    def test_changed_response_digest_refused(self):
        selected = query_run.HERE / 'run-current-0002'
        if not selected.exists():
            self.skipTest('current query has not completed')
        with tempfile.TemporaryDirectory(dir=query_run.HERE) as name:
            dest = Path(name)
            source = selected / 'lifecycle-current-specialist.json'
            shutil.copyfile(source, dest / source.name)
            result = json.loads((selected / 'RESULT.json').read_bytes())
            result['queries']['lifecycle-current-specialist']['path'] = (dest / source.name).relative_to(query_run.ROOT).as_posix()
            result['queries']['lifecycle-current-specialist']['response_digest'] = '0' * 64
            (dest / 'RESULT.json').write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError, 'query response content/claim differs'):
                query_run.verify_result(dest)


class SuccessorJoinTests(unittest.TestCase):
    def setUp(self):
        root = query_run.ROOT
        parent = Path('authority/admissions/lab-specialist-owner-bootstrap-v1-0003')
        read = lambda path: json.loads((root / path).read_bytes())
        bundle = read(parent / 'bundle.json')
        predecessor_path = Path(bundle['predecessor_state']['path'])
        current_path = parent / 'instances/project-state.json'
        kinds = ('project-semantic-event-history', 'project-governance-event-history')
        self.args = [parent, bundle, read(parent / 'receipts/application.json'),
                     read(parent / 'decision.json'), read(predecessor_path),
                     hashlib.sha256((root / predecessor_path).read_bytes()).hexdigest(),
                     {k: read(predecessor_path.parent / (k + '.json')) for k in kinds},
                     read(current_path), {k: read(parent / 'instances' / (k + '.json')) for k in kinds},
                     {(parent / row['path']).as_posix(): row['sha256'] for row in bundle['files']},
                     hashlib.sha256((root / current_path).read_bytes()).hexdigest(), 7,
                     'CAL-DECISION-LAB-SPECIALIST-OWNER-BOOTSTRAP-0003',
                     'decision:lab-specialist-owner-bootstrap-0003']

    def test_exact_join(self):
        verify_successor_join(*self.args)

    def test_wrong_predecessor_refused(self):
        values = copy.deepcopy(self.args)
        values[1]['predecessor_state']['sha256'] = '0' * 64
        with self.assertRaisesRegex(RuntimeFault, 'predecessor State join'):
            verify_successor_join(*values)

    def test_swapped_decision_refused(self):
        values = copy.deepcopy(self.args)
        values[3]['decision_ref'] = 'decision:some-other-admission'
        with self.assertRaisesRegex(RuntimeFault, 'Decision/response/authorization join'):
            verify_successor_join(*values)

    def test_stale_semantic_history_refused(self):
        values = copy.deepcopy(self.args)
        values[8]['project-semantic-event-history']['payload']['events'][-1]['predecessor_state_ref'] = 'other-state'
        with self.assertRaisesRegex(RuntimeFault, 'State/Decision/history join'):
            verify_successor_join(*values)

    def test_swapped_governance_decision_refused(self):
        values = copy.deepcopy(self.args)
        values[8]['project-governance-event-history']['payload']['events'][-1]['decision_ref'] = 'other-decision'
        with self.assertRaisesRegex(RuntimeFault, 'State/Decision/history join'):
            verify_successor_join(*values)


if __name__ == '__main__':
    unittest.main()
