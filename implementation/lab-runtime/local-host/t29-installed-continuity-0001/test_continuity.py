"""Fast causal checks; the full installed fixture is exercised by continuity.py."""
import copy
import importlib.util
import pathlib
import tempfile
import unittest
from unittest.mock import patch

SOURCE = pathlib.Path(__file__).with_name("continuity.py")
spec = importlib.util.spec_from_file_location("t29_continuity", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify_spec = importlib.util.spec_from_file_location("t29_verify", SOURCE.with_name("verify.py"))
receipt_check = importlib.util.module_from_spec(verify_spec)
verify_spec.loader.exec_module(receipt_check)


def sample():
    proposal = {"targets": [{"version_ref": "work:one@candidate.1"}]}
    applied = {"transaction_digest": "admitted-head"}
    status = {"head": "admitted-head", "current_project_state": {"node_id": "state:one"}}
    packet = {"session_disposition": "closed-after-export", "context_packet": {
        "head": "admitted-head", "agent_session": {"payload": {"input_refs": ["work:one@candidate.1"]}},
        "context_view": {"source_epoch": "admitted-head", "node_id": "view:one",
                         "generated_at": "2026-10-23T12:00:00Z", "expires_at": "2026-10-23T12:02:00Z"},
        "project_state": {"node_id": "state:one"}, "authority_effect": "none", "short_memory_persisted": False}}
    return proposal, applied, packet, status


class ContinuityTests(unittest.TestCase):
    def test_cold_receipt_and_changed_pin(self):
        self.assertTrue(receipt_check.verify()["local_t29_check_passed"])
        with patch.object(receipt_check, "RECEIPT_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "selected byte changed"):
                receipt_check.verify()

    def test_selected_controls(self):
        manifest = module.selected()
        self.assertEqual((len(manifest["materials"]), len(manifest["runtime_code"])), (698, 3))

    def test_bounded_consumption(self):
        data = sample()
        self.assertTrue(module.validate_consumer(*data)["bounded_input_consumed"])
        for path, value in [
            (("context_packet", "head"), "other-head"),
            (("context_packet", "agent_session", "payload", "input_refs"), ["work:other"]),
            (("context_packet", "context_view", "source_epoch"), "old-head"),
            (("context_packet", "context_view", "expires_at"), "2026-10-23T12:03:00Z"),
            (("context_packet", "project_state", "node_id"), "state:other"),
            (("context_packet", "short_memory_persisted"), True),
            (("session_disposition",), "active")]:
            packet = copy.deepcopy(data[2])
            at = packet
            for name in path[:-1]:
                at = at[name]
            at[path[-1]] = value
            with self.subTest(path=path), self.assertRaises(ValueError):
                module.validate_consumer(data[0], data[1], packet, data[3])

    def test_held_read_rejects_changed_bytes_and_linked_ancestor(self):
        with tempfile.TemporaryDirectory(prefix="cal-t29-test-") as directory:
            root = pathlib.Path(directory)
            real = root / "real"
            real.mkdir()
            source = real / "source"
            source.write_bytes(b"selected")
            expected = module.sha(b"selected")
            self.assertEqual(module.checked(source, expected), b"selected")
            source.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "digest changed"):
                module.checked(source, expected)
            source.write_bytes(b"selected")
            (root / "linked").symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "linked selected path"):
                module.checked(root / "linked/source", expected)


if __name__ == "__main__":
    unittest.main()
