import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import ROOT, LAB, PACKAGE, load, dump, binding
from check import inspect, read_input


class DecisionInspection(unittest.TestCase):
    def setUp(self):
        self.record = load(PACKAGE / "fixtures/valid/decision.json")
        self.temp = tempfile.TemporaryDirectory(prefix="decision-test-", dir=LAB / ".tmp")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def rebind(self, proposal=None, statement=None):
        proposal = load(ROOT / "examples/proposal.json") if proposal is None else proposal
        statement = load(ROOT / "examples/statement.json") if statement is None else statement
        path = self.directory / "proposal.json"; dump(path, proposal)
        self.record["proposal"] = binding(path)
        statement["proposal_sha256"] = self.record["proposal"]["sha256"]
        path = self.directory / "statement.json"; dump(path, statement)
        self.record["statement"] = binding(path)

    def local_subject(self):
        path = self.directory / "candidate.json"; dump(path, {"candidate": "test-only"})
        member = self.directory / "implementation.json"; dump(member, {"version": 1})
        manifest = self.directory / "manifest.json"; dump(manifest, {"materials": [binding(path), binding(member)]})
        subject = {"subject_ref": "simulation:local-subject", **binding(path), "material_manifest": binding(manifest)}
        self.record["subject"] = subject
        proposal = load(ROOT / "examples/proposal.json"); proposal["subject"] = subject
        statement = load(ROOT / "examples/statement.json"); statement["subject"] = subject
        self.rebind(proposal, statement)
        return path, member, manifest

    def test_valid_simulation_does_not_grant_authority(self):
        result = inspect(self.record)
        self.assertTrue(result["record_valid"])
        self.assertEqual(result["provenance_kind"], "simulation")
        self.assertGreater(result["subject_materials_verified"], 1)
        for key in ["principal_authenticated", "role_authority_verified", "effect_authorized_by_checker", "effect_executed"]:
            self.assertFalse(result[key])

    def test_unknown_option_is_rejected(self):
        self.record["selected_option_id"] = "publish-everything"
        with self.assertRaisesRegex(ValueError, "Unknown selected option"):
            inspect(self.record)

    def test_effect_cannot_expand_selected_choice(self):
        self.record["declared_effect"] = "adopt-and-enforce"
        with self.assertRaisesRegex(ValueError, "effect differs"):
            inspect(self.record)

    def test_scope_cannot_expand(self):
        self.record["scope_ref"] = "scope:all-repositories"
        with self.assertRaisesRegex(ValueError, "scope differs"):
            inspect(self.record)

    def test_actor_must_match_bound_statement(self):
        self.record["actor"]["principal_ref"] = "person:someone-else"
        with self.assertRaisesRegex(ValueError, "Statement mismatch: actor"):
            inspect(self.record)

    def test_role_must_match_proposal_owner(self):
        self.record["actor"]["role_ref"] = "role:other"
        with self.assertRaisesRegex(ValueError, "role differs"):
            inspect(self.record)

    def test_stale_proposal_and_statement_digests(self):
        for key in ["proposal", "statement"]:
            record = copy.deepcopy(self.record); record[key]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "missing or changed"):
                inspect(record)

    def test_changed_subject_member_invalidates_decision(self):
        _, member, _ = self.local_subject()
        self.assertTrue(inspect(self.record)["record_valid"])
        dump(member, {"version": 2})
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            inspect(self.record)

    def test_changed_subject_file_invalidates_decision(self):
        path, _, _ = self.local_subject()
        dump(path, {"candidate": "changed"})
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            inspect(self.record)

    def test_duplicate_option_ids_fail_closed(self):
        proposal = load(ROOT / "examples/proposal.json")
        proposal["options"].append(copy.deepcopy(proposal["options"][0]))
        self.rebind(proposal=proposal)
        with self.assertRaisesRegex(ValueError, "Duplicate proposal option"):
            inspect(self.record)

    def test_manifest_must_include_subject(self):
        _, member, manifest = self.local_subject()
        dump(manifest, {"materials": [binding(member)]})
        self.record["subject"]["material_manifest"] = binding(manifest)
        proposal = load(LAB / self.record["proposal"]["path"]); proposal["subject"] = self.record["subject"]
        statement = load(LAB / self.record["statement"]["path"]); statement["subject"] = self.record["subject"]
        self.rebind(proposal, statement)
        with self.assertRaisesRegex(ValueError, "absent from its material manifest"):
            inspect(self.record)

    def test_recorded_timestamp_and_provenance_must_match_statement(self):
        for key, value in [("recorded_at", "2026-09-08T00:00:00Z"), ("provenance_kind", "recorded-owner-statement")]:
            record = copy.deepcopy(self.record); record[key] = value
            with self.assertRaisesRegex(ValueError, "Statement mismatch"):
                inspect(record)

    def test_forged_consistent_actor_still_has_no_authority(self):
        statement = load(ROOT / "examples/statement.json")
        statement["actor"]["principal_ref"] = "asserted:owner"
        statement["provenance_kind"] = "recorded-owner-statement"
        self.record["actor"] = statement["actor"]
        self.record["provenance_kind"] = statement["provenance_kind"]
        self.rebind(statement=statement)
        result = inspect(self.record)
        self.assertFalse(result["principal_authenticated"])
        self.assertFalse(result["effect_authorized_by_checker"])

    def test_path_escape_and_duplicate_json_keys_rejected(self):
        self.record["proposal"]["path"] = "../elsewhere.json"
        with self.assertRaisesRegex(ValueError, "Lab-relative"):
            inspect(self.record)
        path = self.directory / "bad.json"; path.write_text('{"choice":"a","choice":"b"}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            read_input(path)

    def test_read_only_cli_and_nonmutation(self):
        before = copy.deepcopy(self.record)
        inspect(self.record)
        self.assertEqual(self.record, before)
        path = PACKAGE / "fixtures/valid/decision.json"; bytes_before = path.read_bytes()
        result = subprocess.run([sys.executable, str(ROOT / "check.py"), str(path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(json.loads(result.stdout)["effect_executed"])
        self.assertEqual(path.read_bytes(), bytes_before)


if __name__ == "__main__":
    unittest.main()
