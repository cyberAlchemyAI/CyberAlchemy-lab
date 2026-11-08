import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import rehearse


class CandidateRehearsalTests(unittest.TestCase):
    def test_disposable_import_fresh_process_and_exact_receipt(self):
        result = rehearse.run()
        self.assertEqual(result["archive_sha256"], rehearse.ARCHIVE_SHA)
        self.assertEqual(result["fresh_process_replay"]["cold_archive_sha256"],
                         rehearse.ARCHIVE_SHA)
        self.assertTrue(result["unapproved_refused"])
        self.assertTrue(result["changed_bytes_refused"])
        self.assertTrue(result["exact_retry_idempotent"])
        self.assertTrue(result["foreign_sentinel_preserved"])
        self.assertTrue(result["clean_fixture_extract_verified"])
        self.assertFalse(result["full_t30_release"])
        raw = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
        self.assertEqual(raw, (Path(rehearse.__file__).parent / "RESULT.json").read_bytes())

    def test_changed_selected_code_refuses_before_import(self):
        path, _ = rehearse.SOURCES["t27_import"]
        with patch.dict(rehearse.SOURCES, {"t27_import": (path, "0" * 64)}):
            with self.assertRaisesRegex(ValueError, "selected source changed"):
                rehearse.load_selected("t27_import")

    def test_cold_child_rejects_changed_code_before_side_effect(self):
        with tempfile.TemporaryDirectory(prefix="cal-t30-cold-tamper-") as name:
            sentinel = Path(name) / "executed"
            changed = (f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('bad')\n").encode()
            expected = rehearse.sha(b"pass\n")
            child = subprocess.run([sys.executable, "-I", "-B", "-c",
                                    rehearse.COLD_BOOTSTRAP, expected,
                                    str(Path(rehearse.__file__))],
                                   input=changed, capture_output=True, timeout=30)
            self.assertNotEqual(child.returncode, 0)
            self.assertFalse(sentinel.exists())


if __name__ == "__main__":
    unittest.main()
