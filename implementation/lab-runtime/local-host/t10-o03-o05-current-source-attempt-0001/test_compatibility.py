import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import compatibility


class CompatibilityTests(unittest.TestCase):
    def test_exact_archive_still_selects_d75(self):
        archive, files, baseline = compatibility.archive_inputs()
        self.assertEqual(baseline['materials'][compatibility.SOURCE], compatibility.OLD_LOOKUP)
        self.assertEqual(archive['project_pins']['baseline_snapshot_digest'], baseline['snapshot_digest'])
        self.assertEqual(len(files), 5)

    def test_changed_archive_bytes_refused(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / 'branch.snapshot'
            shutil.copyfile(compatibility.ARCHIVE, path)
            path.write_bytes(path.read_bytes() + b'\n')
            with patch.object(compatibility, 'ARCHIVE', path):
                with self.assertRaisesRegex(ValueError, 'archive changed'):
                    compatibility.archive_inputs()

    def test_wrong_archived_lookup_refused(self):
        with patch.object(compatibility, 'OLD_LOOKUP', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'does not select D75 baseline'):
                compatibility.archive_inputs()

    def test_current_and_historical_incompatibility_is_explicit(self):
        observed = compatibility.attempt()
        self.assertEqual(observed['result'], 'REFUSED-ORIGINAL-ARCHIVE-AS-CURRENT')
        self.assertEqual(observed['historical_replay'], 'PASS')
        self.assertFalse(observed['query_executed'])
        self.assertEqual(observed['selected_governed_models'], 0)


if __name__ == '__main__':
    unittest.main()
