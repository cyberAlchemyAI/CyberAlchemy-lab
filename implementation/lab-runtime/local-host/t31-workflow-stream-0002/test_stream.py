"""Focused cold replay and changed-byte/lineage refusal checks."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from stream import HERE, check_trial_ids, digest, receipt, verify


RUN = HERE / "run-0001"


class StreamTests(unittest.TestCase):
    def test_cold_replay(self):
        self.assertEqual(verify(RUN)["remaining"], 24)

    def changed(self, kind, relative, mutate):
        with tempfile.TemporaryDirectory(prefix="lab-t31-middle-negative-") as temp:
            target = Path(temp) / "run"
            shutil.copytree(RUN, target)
            path = target / kind / relative
            mutate(path)
            with self.assertRaises((ValueError, KeyError, json.JSONDecodeError)):
                verify(target)

    def test_output_original_bytes_refused(self):
        self.changed("engineering", "workflow/evidence-set.json",
                     lambda p: p.write_bytes(p.read_bytes() + b" "))

    def test_later_consumer_refused(self):
        def remove(path):
            body = json.loads(path.read_bytes())
            body["payload"]["evidence_refs"] = []
            path.write_text(json.dumps(body))
        self.changed("engineering", "workflow/work-outcome-assessment.json", remove)

    def test_middle_event_refused(self):
        def change(path):
            body = json.loads(path.read_bytes())
            body[1]["to"] = "wrong"
            path.write_text(json.dumps(body))
        self.changed("research", "transitions.json", change)

    def test_actual_replay_child_bytes_refused(self):
        self.changed("research", "sample-1-direct.stdout",
                     lambda p: p.write_bytes(p.read_bytes() + b"x"))

    def test_research_later_finding_refused(self):
        def remove(path):
            body = json.loads(path.read_bytes())
            body["evidence_refs"] = []
            path.write_text(json.dumps(body))
        self.changed("research", "finding.json", remove)

    def test_duplicate_sample_id_refused(self):
        with self.assertRaisesRegex(ValueError, "distinct ordered paired sample"):
            check_trial_ids([{"sample": 1}, {"sample": 1}, {"sample": 3}])

    def test_predecessor_byte_drift_refused(self):
        with tempfile.TemporaryDirectory(prefix="lab-t31-predecessor-negative-") as temp:
            prior = Path(temp) / "RESULT.json"
            from stream import PREVIOUS_RESULT
            prior.write_bytes(PREVIOUS_RESULT.read_bytes() + b" ")
            with mock.patch("stream.PREVIOUS_RESULT", prior):
                with self.assertRaisesRegex(ValueError, "predecessor result bytes differ"):
                    receipt(RUN)

    def test_duplicate_cumulative_ref_refused(self):
        with tempfile.TemporaryDirectory(prefix="lab-t31-duplicate-ref-") as temp:
            prior = Path(temp) / "RESULT.json"
            from stream import PREVIOUS_RESULT
            body = json.loads(PREVIOUS_RESULT.read_bytes())
            body["observed_terminal_output_transitions"][1]["transition_ref"] = body["observed_terminal_output_transitions"][0]["transition_ref"]
            prior.write_text(json.dumps(body))
            with mock.patch("stream.PREVIOUS_RESULT", prior), mock.patch("stream.PREVIOUS_RESULT_SHA256", digest(prior.read_bytes())):
                with self.assertRaisesRegex(ValueError, "distinct selected transition identities"):
                    receipt(RUN)


if __name__ == "__main__":
    unittest.main()
