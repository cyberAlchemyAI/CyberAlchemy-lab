"""Cheap prerequisites for the pending API42 native Session run."""
import json
import time
import unittest

import live_session as L


class LivePrerequisites(unittest.TestCase):
    def test_exact_note_partition(self):
        raw = b'x' * 7887
        chunks = L.chunks(raw)
        self.assertEqual([len(item) for item in chunks], [4096, 3791])
        self.assertEqual(b''.join(chunks), raw)

    def test_note_budget_refused(self):
        with self.assertRaisesRegex(ValueError, 'note budget'):
            L.chunks(b'x' * 65537)

    def test_fresh_current_project_state_report(self):
        episode = L.selected_episode()
        selected = episode.selection(L.ROOT)
        view = episode.bounded_view(selected, time.time())
        raw = episode.compact(view)
        delivery = {'context_view': {'version_ref': 'context-view:test@derived.1'}}
        opened = {'context_delivery_binding': {'ref': 'context-delivery:context-view:test@derived.1', 'sha256': 'a' * 64},
                  'session_ref': 'agent-session:test'}
        inspect = {'session_ref': opened['session_ref']}
        close = {'session_ref': opened['session_ref'], 'discarded_memory': True}
        report = L.observed_report(episode, selected, view, raw, delivery, opened, inspect, close, True)
        self.assertEqual(len(raw), 7887)
        self.assertEqual(report['result_kind'], 'observed-discrepancies')
        self.assertEqual(len(report['discrepancies']), 2)
        self.assertTrue(report['native_lab_session'])

    def test_false_disposal_refused(self):
        episode = L.selected_episode()
        selected = episode.selection(L.ROOT)
        view = episode.bounded_view(selected, time.time())
        delivery = {'context_view': {'version_ref': 'context-view:test@derived.1'}}
        opened = {'context_delivery_binding': {'ref': 'context-delivery:context-view:test@derived.1', 'sha256': 'a' * 64},
                  'session_ref': 'agent-session:test'}
        with self.assertRaisesRegex(ValueError, 'RAM disposal not observed'):
            L.observed_report(episode, selected, view, episode.compact(view), delivery, opened,
                              {'session_ref': opened['session_ref']},
                              {'session_ref': opened['session_ref'], 'discarded_memory': False}, False)


if __name__ == '__main__': unittest.main()
