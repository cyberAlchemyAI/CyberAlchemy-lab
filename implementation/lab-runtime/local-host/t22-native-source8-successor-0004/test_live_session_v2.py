"""Cheap byte-loader and clarified-report negatives; no native replay."""
import importlib
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

import live_session_v2 as L


class SelectedCodeAndReport(unittest.TestCase):
    def test_preselected_runner_bytes_required(self):
        selected = L.RUNNER_SELECTION.read_bytes()
        expected = hashlib.sha256(selected).hexdigest()
        try:
            L._HELD_RUNNER_SELECTION = selected
            self.assertEqual(L.runner_selection(expected)['sha256'], expected)
            with self.assertRaisesRegex(ValueError, 'selection differs'):
                L.runner_selection('0' * 64)
            L._HELD_RUNNER_SELECTION = selected + b' '
            with self.assertRaisesRegex(ValueError, 'selection differs'):
                L.runner_selection(expected)
        finally:
            del L._HELD_RUNNER_SELECTION

    def test_import_uses_held_selected_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / '__init__.py'
            member = root / 'member.py'
            package.write_bytes(b'from .member import answer\n')
            member.write_bytes(b'def answer(): return 7\n')
            name = '_cal_t22_held_byte_loader_test'
            finder = L.CapturedApi(name, {name: (package, package.read_bytes()),
                                          name + '.member': (member, member.read_bytes())})
            sys.meta_path.insert(0, finder)
            try:
                member.write_bytes(b'def answer(): return 99\n')
                imported = importlib.import_module(name)
                self.assertEqual(imported.answer(), 7)
                self.assertEqual(Path(imported.answer.__code__.co_filename), member)
                with self.assertRaisesRegex(ModuleNotFoundError, 'unselected API42'):
                    importlib.import_module(name + '.foreign')
            finally:
                sys.meta_path.remove(finder)
                for key in (name + '.member', name):
                    sys.modules.pop(key, None)

    def test_old_lookup_name_is_clarified(self):
        episode = L.selected_episode()
        selected = episode.selection(L.ROOT)
        view = episode.bounded_view(selected, 1_792_710_000.0)
        raw = episode.compact(view)
        delivery = {'context_view': {'version_ref': 'context-view:test@derived.1'}}
        opened = {'context_delivery_binding': {
            'ref': 'context-delivery:context-view:test@derived.1', 'sha256': 'a' * 64},
            'session_ref': 'agent-session:test'}
        report = L.observed_report(episode, selected, view, raw, delivery, opened,
                                   {'session_ref': opened['session_ref']},
                                   {'session_ref': opened['session_ref'], 'discarded_memory': True}, True)
        first = report['discrepancies'][0]
        self.assertNotIn('candidate_sha256', first)
        self.assertEqual(first['api30_pinned_lookup_sha256'], episode.OLD_LOOKUP_SHA)
        self.assertNotEqual(first['api30_pinned_lookup_sha256'], first['observed_sha256'])


if __name__ == '__main__':
    unittest.main()
