from pathlib import Path
import tempfile
import unittest

import source_diagnosis as diagnosis


class SourceDiagnosis(unittest.TestCase):
    def test_exact_missing_originals_and_recovery_candidates(self):
        result = diagnosis.diagnose()
        self.assertEqual(result['observation_count'], 76)
        self.assertEqual(result['source_binding_count'], 66)
        self.assertEqual(result['mismatch_occurrences'], 5)
        self.assertEqual(len(result['distinct_missing_sources']), 3)
        self.assertEqual(len(result['exact_byte_recovery_candidates']), 2)
        self.assertFalse(result['historical_o05_translation_currently_replayable'])

    def test_changed_selected_digest_refuses(self):
        old = diagnosis.SELECTION_SHA
        try:
            diagnosis.SELECTION_SHA = '0' * 64
            with self.assertRaisesRegex(ValueError, 'original O05 source selection changed'):
                diagnosis.diagnose()
        finally:
            diagnosis.SELECTION_SHA = old

    def test_changed_bytes_and_linked_parent_are_not_exact_recovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = root / 'original'
            original.mkdir()
            (original / 'source').write_bytes(b'exact')
            link = root / 'link'
            link.symlink_to(original, target_is_directory=True)
            self.assertEqual(diagnosis.checked(original / 'source', diagnosis.sha(b'other')), 'changed')
            self.assertEqual(diagnosis.checked(link / 'source', diagnosis.sha(b'exact')), 'unsafe-symlink')


if __name__ == '__main__':
    unittest.main()
