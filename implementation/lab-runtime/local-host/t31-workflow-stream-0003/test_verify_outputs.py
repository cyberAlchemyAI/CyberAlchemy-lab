"""Cold W06 carrier and later-consumer mutation controls."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from verify_outputs import HERE, digest, verify


RUN = HERE / "run-0007"


class W06OutputTests(unittest.TestCase):
    def test_retained_cold_carrier_and_consumer_check(self):
        result = verify(RUN)
        self.assertEqual(result["carrier_set_count"], 3)
        self.assertEqual(result["native_workflow_transition_events"], 0)

    def changed(self, update):
        with tempfile.TemporaryDirectory(prefix="lab-T31-W06-negative-") as temp:
            root = Path(temp) / "run"
            shutil.copytree(RUN, root)
            index_path = root / "episode-index.json"
            index = json.loads(index_path.read_bytes())
            update(root, index)
            index_path.write_text(json.dumps(index))
            with self.assertRaises(ValueError):
                verify(root, index_sha256=digest(index_path.read_bytes()))

    def test_missing_required_original_refused(self):
        def change(root, index):
            row = next(r for r in index["records"] if r["version_ref"] == index["improvement_signal_ref"])
            (root / row["path"]).unlink()
        self.changed(change)

    def test_false_canonical_effect_refused(self):
        self.changed(lambda root, index: index.__setitem__("canonical_effects_applied", 1))

    def test_coherently_rehashed_wrong_later_application_refused(self):
        def change(root, index):
            row = next(r for r in index["records"] if r["version_ref"] == index["outcome_ref"])
            path = root / row["path"]
            body = json.loads(path.read_bytes())
            body["payload"]["lesson_application_ref"] = "lesson-application:foreign@candidate.1"
            path.write_text(json.dumps(body))
            row["sha256"] = digest(path.read_bytes())
        self.changed(change)

    def test_wrong_predecessor_pin_refused(self):
        with mock.patch("verify_outputs.T31_V2_RESULT_SHA256", "0" * 64):
            with self.assertRaisesRegex(ValueError, "predecessor result changed"):
                verify(RUN)


if __name__ == "__main__":
    unittest.main()
