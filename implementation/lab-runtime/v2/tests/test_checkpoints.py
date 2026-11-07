"""Regression checks for explicit post-D75 source selection and refusal boundaries."""
import copy
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_runtime.common import RuntimeFault, encoded, load
from lab_runtime.sources import Capture, capture, freshness, under

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parents[2]


class CheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = load(PACKAGE / "profile.json")
        cls.snapshot = capture(REPO, cls.profile)

    def test_current_head_and_exact_history_extension(self):
        lookup = load(REPO / self.profile["current_selection"]["lookup"]["path"])
        self.assertEqual(self.snapshot["state"]["node_id"], lookup["identity_ref"])
        for history in self.snapshot["histories"].values():
            self.assertEqual(len(history["payload"]["events"]), 7)
        old = self.snapshot["subjects"]["project-state:cyberalchemy-v2-to-lab-migration:decision-0075@decision-0075"]
        self.assertEqual(old["effective_state"], "admitted-historical")
        self.assertEqual(freshness(REPO, self.snapshot)["status"], "current")

    def test_checkpoint_members_do_not_grant_native_role_authority(self):
        projected = {v["source"]["path"] for v in self.snapshot["subjects"].values()}
        for binding in self.profile["state_checkpoint_roots"]:
            parent = Path(binding["path"]).parent
            for name in ("role.json", "role-assignment.json", "definition-owner-role.json",
                         "definition-owner-role-assignment.json"):
                path = (parent / "instances" / name).as_posix()
                if (REPO / path).exists():
                    self.assertIn(path, self.snapshot["materials"])
                    self.assertNotIn(path, projected)

    def test_omitted_or_reversed_checkpoint_refuses(self):
        for roots in (self.profile["state_checkpoint_roots"][1:],
                      list(reversed(self.profile["state_checkpoint_roots"]))):
            profile = copy.deepcopy(self.profile)
            profile["state_checkpoint_roots"] = roots
            with self.subTest(roots=roots), self.assertRaisesRegex(RuntimeFault, "predecessor mismatch"):
                capture(REPO, profile)

    def test_rewritten_predecessor_history_refuses(self):
        path = (Path(self.profile["state_checkpoint_roots"][0]["path"]).parent /
                "instances/project-semantic-event-history.json").as_posix()
        original = Capture.read
        def changed(cap, name, expected=None):
            value = original(cap, name, expected)
            if name == path:
                value["payload"]["events"][0]["event_id"] += "-rewritten"
            return value
        with patch.object(Capture, "read", changed), self.assertRaisesRegex(RuntimeFault, "extend exact history"):
            capture(REPO, self.profile)

    def test_changed_bundle_member_refuses_and_marks_existing_snapshot_stale(self):
        parent = Path(self.profile["state_checkpoint_roots"][0]["path"]).parent
        name = (parent / "owner-response.json").as_posix()
        with TemporaryDirectory(prefix="cal-checkpoint-drift-") as directory:
            changed = Path(directory) / "response.json"
            changed.write_bytes(encoded({"changed": True}))
            def redirected(root, path):
                return changed if path == name else under(root, path)
            with patch("lab_runtime.sources.under", redirected):
                with self.assertRaisesRegex(RuntimeFault, "source digest mismatch"):
                    capture(REPO, self.profile)
                self.assertIn(name, freshness(REPO, self.snapshot)["changed"])

    def test_receipt_state_and_predecessor_bindings_refuse(self):
        parent = Path(self.profile["state_checkpoint_roots"][0]["path"]).parent
        mutations = (
            ("bundle.json", lambda d: d["predecessor_state"].update(sha256="0" * 64), "predecessor mismatch"),
            ("bundle.json", lambda d: d.update(current_project_state_sha256="0" * 64), "State binding mismatch"),
            ("receipts/application.json", lambda d: d.update(authorization_sha256="0" * 64), "receipt binding mismatch"),
            ("decision.json", lambda d: d.update(selected_outcome="reject"), "not approved"),
        )
        original = Capture.read
        for member, mutate, message in mutations:
            target = (parent / member).as_posix()
            def changed(cap, name, expected=None):
                value = original(cap, name, expected)
                if name == target:
                    mutate(value)
                return value
            with self.subTest(member=member, message=message), patch.object(Capture, "read", changed):
                with self.assertRaisesRegex(RuntimeFault, message):
                    capture(REPO, self.profile)
