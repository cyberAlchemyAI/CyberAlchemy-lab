import tempfile
import unittest
from pathlib import Path

from src.body_war_canary_evidence import build_evidence_pack, derive_snapshot_boundary, scan_protected_values
from src.body_war_canary_projector import invoke_projector, projector_invocation


def receipts():
    return {"decision": {"decision": "rollback"}, "observer": {"outcome": "passed"}, "teardown": {"runtime_project_residue": []}}


class EvidenceTests(unittest.TestCase):
    def test_pack_is_canonical_bound_complete_and_denied(self):
        first = build_evidence_pack("run-1", receipts(), ["prepared-image-id"])
        second = build_evidence_pack("run-1", {"teardown": receipts()["teardown"], "observer": receipts()["observer"], "decision": receipts()["decision"]}, ["prepared-image-id"])
        self.assertEqual(first["raw_pack_sha256"], second["raw_pack_sha256"])
        boundary = derive_snapshot_boundary(first)
        self.assertEqual((boundary["runtime_admission"], boundary["eligible_control_ids"], boundary["authority_effect"]), ("denied", [], "none"))

    def test_partial_secret_and_residue_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "MISSING"):
            build_evidence_pack("run-1", {"decision": {}, "observer": {}})
        hostile = receipts(); hostile["decision"]["note"] = "token=super-secret"
        self.assertTrue(scan_protected_values(hostile))
        with self.assertRaisesRegex(ValueError, "PROTECTED"):
            build_evidence_pack("run-1", hostile)
        dirty = receipts(); dirty["teardown"]["runtime_project_residue"] = ["network"]
        with self.assertRaisesRegex(ValueError, "RESIDUE"):
            build_evidence_pack("run-1", dirty)

    def test_projector_is_argv_only_and_runner_injected(self):
        repo = Path.cwd().parents[3]
        snapshot = Path.cwd() / "fixtures/valid/body-war-runtime-rollback-pass.snapshot.json"
        raw = Path.cwd() / "fixtures/hostile/body-war-canary-tabletop-cases.json"
        invocation = projector_invocation(repo, snapshot, raw, "2026-09-02T00:00:00Z")
        self.assertIsInstance(invocation.argv, tuple)
        calls = []
        class Result: returncode = 0; stdout = "{}"; stderr = ""
        result = invoke_projector(invocation, lambda *args, **kwargs: calls.append((args, kwargs)) or Result())
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("shell", calls[0][1])


if __name__ == "__main__": unittest.main()
