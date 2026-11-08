"""A passing fixture smoke cannot become a full release by relabeling the status."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import verify_release_status as release


class ReleaseStatusTests(unittest.TestCase):
    def changed_status_must_fail(self, change):
        with tempfile.TemporaryDirectory(prefix="cal-t30-release-status-") as name:
            changed = json.loads(release.STATUS.read_bytes())
            change(changed)
            path = Path(name) / "changed.json"
            path.write_text(json.dumps(changed))
            with patch.object(release, "STATUS", path), self.assertRaisesRegex(
                    ValueError, "release-status claim differs"):
                release.verify()

    def test_selected_candidate_and_false_release_refusal(self):
        self.assertEqual(release.verify()["status"], "candidate-not-released")
        self.changed_status_must_fail(lambda record: record.update(status="released"))

    def test_contradictory_flags_refused(self):
        self.changed_status_must_fail(lambda record: record.update(
            local_fixture_smoke_passed=False, selected_docker_cleanup_passed=False))

    def test_substituted_evidence_refused_even_when_hash_matches(self):
        def substitute(record):
            ref = record["references"]["docker_review"]
            for name in ("candidate_inventory", "candidate_result", "local_import"):
                record["references"][name] = dict(ref)
        self.changed_status_must_fail(substitute)

    def test_linked_status_refused_even_with_identical_bytes(self):
        with tempfile.TemporaryDirectory(prefix="cal-t30-release-status-") as name:
            copy = Path(name) / "copy.json"
            copy.write_bytes(release.STATUS.read_bytes())
            link = Path(name) / "status.json"
            link.symlink_to(copy)
            with patch.object(release, "STATUS", link), self.assertRaisesRegex(
                    ValueError, "not a regular file"):
                release.verify()


if __name__ == "__main__":
    unittest.main()
