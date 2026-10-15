"""All fixtures live in temporary directories; the real run root is never mutated."""

import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("runtime_under_test", Path(__file__).with_name("runtime.py"))
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def opening(identifier="Z1", refs=None):
    return {"id": identifier, "kind": "question", "claim": "test string", "delta": "test string",
            "refs": ["O1", "H1"] if refs is None else refs, "prediction": "test string",
            "rival_prediction": "test string", "defeat": "test string",
            "probe": "test string", "fit": "uncertain", "assumptions": []}


def raw(role="Z", identifier="Z1"):
    document = {"case_id": "temporary-case", "role": role, "openings": [opening(identifier)]}
    if role == "T":
        document.update(decision="temporary", unresolved=[])
    return document


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="runtime-test-")
        self.root = Path(self.temp.name)
        self.original_root = runtime.R
        runtime.R = self.root
        self.case = {"case_id": "temporary-case", "observations": [{"id": "O1", "text": "temporary stipulated string"}],
                     "hard_constraints": [{"id": "H1", "text": "temporary stipulated string"}]}
        self.write("case.json", self.case)
        self.write("fixture.json", raw("A", "A1"))
        (self.root / "template.txt").write_text("Produce only the requested structural JSON.", encoding="utf-8")
        self.jobs = [self.job("raw"), self.job("critic", "critique", "Q", "Q", ["raw"], ["case.json", "outputs/raw.json"]),
                     self.job("distill", "distill", "D", "D", ["raw", "critic"], ["outputs/raw.json", "outputs/critic.json"])]
        self.write("schedule.json", {"jobs": self.jobs})

    def tearDown(self):
        runtime.R = self.original_root
        self.temp.cleanup()

    def job(self, identifier, kind="raw", role="Z", prefix="Z", deps=None, sources=None):
        return {"job_id": identifier, "stage": "preflight", "case_id": "temporary-case", "role": role,
                "condition": "temporary", "prefix": prefix, "kind": kind, "template": "template.txt",
                "depends_on": [] if deps is None else deps, "sources": ["case.json", "fixture.json"] if sources is None else sources}

    def write(self, name, document):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def valid_raw_join(self):
        runtime.prepare("raw")
        runtime.spawn("raw", "native-agent-1")
        self.write("outputs/raw.json", raw())
        self.assertTrue(runtime.join("raw", "native-agent-1", True)["validation"]["valid"])

    def distill(self):
        return {"case_id": "temporary-case", "role": "D", "openings": [
            {"id": "D1", "source_ids": ["Z1", "Q1"], "claim": "test string", "discriminator": "test string",
             "fit": "conditional", "probe": "test string", "uncertainty": "test string"}],
            "lineage": [{"source_id": identifier, "disposition": "merged", "target_ids": ["D1"], "reason": "unknown"}
                        for identifier in ("Z1", "Q1")], "decision": "test string"}

    def check(self, document, job=None, sources=None):
        return runtime.validate_document(self.jobs[0] if job is None else job, document,
                                         [self.case, raw("A", "A1")] if sources is None else sources)

    def test_valid_raw_and_zero_openings(self):
        self.assertTrue(self.check(raw())["valid"])
        self.assertTrue(self.check({"case_id": "temporary-case", "role": "Z", "openings": []})["valid"])
        self.assertTrue(self.check(raw("Z", "Z2"))["valid"])

    def test_all_critic_fit_enums_and_new_opening_links(self):
        job = self.jobs[1]
        for fit in runtime.FIT:
            document = raw("Q", "Q1")
            document["openings"][0]["refs"] = ["A1", "O1"]
            document["critiques"] = [{"source_id": "A1", "issue": "temporary", "fit": fit, "opening_ids": ["Q1"]}]
            self.assertTrue(self.check(document, job)["valid"])
        document["critiques"][0]["fit"] = "invented"
        self.assertFalse(self.check(document, job)["valid"])
        document["critiques"][0]["fit"] = "uncertain"
        document["critiques"][0]["opening_ids"] = []
        self.assertTrue(self.check(document, job)["valid"])
        document["critiques"][0]["opening_ids"] = ["MISSING"]
        self.assertFalse(self.check(document, job)["valid"])
        del document["critiques"]
        self.assertFalse(self.check(document, job)["valid"])

    def test_unknown_refs_case_identity_and_duplicate_ids(self):
        document = raw()
        document["openings"][0]["refs"] = ["archive-unseen"]
        self.assertFalse(self.check(document)["valid"])
        document = raw()
        document["openings"].append(copy.deepcopy(document["openings"][0]))
        self.assertFalse(self.check(document)["valid"])
        document = raw()
        document["case_id"] = "another-case"
        self.assertFalse(self.check(document)["valid"])
        document = raw("A")
        self.assertFalse(self.check(document)["valid"])

    def test_field_types_and_limits(self):
        document = raw()
        document["openings"][0]["assumptions"] = [3]
        self.assertFalse(self.check(document)["valid"])
        document = raw()
        document["openings"][0]["probe"] = None
        self.assertFalse(self.check(document)["valid"])
        document = raw()
        document["openings"] = [opening("Z1"), opening("Z2"), opening("Z3")]
        self.assertFalse(self.check(document)["valid"])

    def test_rival_prediction_and_defeat_required_on_every_non_distill_role(self):
        for role in ("Z", "A", "Q", "T"):
            job = self.job("temporary", "critique" if role == "Q" else "raw", role, role)
            document = raw(role, role + "1")
            if role == "Q":
                document["critiques"] = []
            self.assertTrue(self.check(document, job)["valid"])
            for field in ("rival_prediction", "defeat"):
                broken = copy.deepcopy(document)
                del broken["openings"][0][field]
                self.assertFalse(self.check(broken, job)["valid"])

    def test_t_decision_and_unresolved_reference_contract(self):
        job = self.job("temporary", role="T", prefix="T")
        document = raw("T", "T1")
        self.assertTrue(self.check(document, job)["valid"])
        for field in ("decision", "unresolved"):
            broken = copy.deepcopy(document)
            del broken[field]
            self.assertFalse(self.check(broken, job)["valid"])
        document["unresolved"] = [{"issue": "temporary", "refs": ["O1", "H1", "A1", "temporary-case"]}]
        self.assertTrue(self.check(document, job)["valid"])
        document["unresolved"][0]["refs"] = ["unknown"]
        self.assertFalse(self.check(document, job)["valid"])
        document["unresolved"][0] = {"issue": [], "refs": []}
        self.assertFalse(self.check(document, job)["valid"])
        document["unresolved"] = []
        document["openings"] = []
        self.assertTrue(self.check(document, job)["valid"])

    def test_p04_component_comparison_and_case_only_named_refs(self):
        job = dict(self.job("temporary", role="A", prefix="A"), condition="P04")
        document = raw("A", "A1")
        self.assertFalse(self.check(document, job)["valid"])
        comparison = {key: "temporary" for key in ("baseline", "parent_a", "parent_b", "hybrid", "interaction_test")}
        document["openings"][0]["component_comparison"] = comparison
        self.assertTrue(self.check(document, job)["valid"])
        for key in comparison:
            broken = copy.deepcopy(document)
            broken["openings"][0]["component_comparison"][key] = " "
            self.assertFalse(self.check(broken, job)["valid"])
        document["openings"][0]["refs"] = ["parent_a"]
        parents = {"case_id": "temporary-case", "parent_a": {"function": "temporary"}, "parent_b": {"function": "temporary"}}
        self.assertFalse(self.check(document, job, [self.case, parents])["valid"])
        document["openings"] = []
        self.assertTrue(self.check(document, job)["valid"])
        self.assertTrue(self.check(raw(), dict(self.jobs[0], condition="P04"))["valid"])
        self.assertTrue(self.check(raw("A", "A1"), dict(job, condition="parent_a"))["valid"])

    def test_malformed_enum_and_reference_types_return_errors(self):
        for field in ("fit", "kind"):
            document = raw()
            document["openings"][0][field] = []
            self.assertFalse(self.check(document)["valid"])
        document = raw("Q", "Q1")
        document["critiques"] = [{"source_id": [], "issue": "temporary", "fit": [], "opening_ids": []}]
        self.assertFalse(self.check(document, self.jobs[1])["valid"])
        document = self.distill()
        document["lineage"][0]["disposition"] = []
        self.assertFalse(self.check(document, self.jobs[2], [raw(), raw("Q", "Q1")])["valid"])

    def test_invalid_json_is_terminal_failure_without_repair(self):
        runtime.prepare("raw")
        runtime.spawn("raw", "native-agent-1")
        path = runtime.paths("raw")[2]
        invalid = b'{"case_id":"temporary-case","role":"Z","role":"A"}'
        path.write_bytes(invalid)
        result = runtime.join("raw", "native-agent-1", True)
        self.assertFalse(result["validation"]["valid"])
        self.assertEqual(path.read_bytes(), invalid)
        self.assertTrue(runtime.audit()["ok"])

    def test_historical_case_reference_schema(self):
        historical = {"hard_constraints_with_source": [{"id": "H1", "text": "temporary source"}],
                      "supplied_observations": [{"id": "O1", "text": "temporary source"}]}
        self.assertTrue(self.check(raw(), sources=[historical])["valid"])
        document = raw()
        document["openings"][0]["refs"] = ["unknown"]
        self.assertFalse(self.check(document, sources=[historical])["valid"])

    def test_case_qualified_aliases_require_matching_supplied_case(self):
        case = {"case_id": "S1", "observations": [{"id": "O1", "text": "temporary"}],
                "hard_constraints": [{"id": "C1", "text": "temporary"}]}
        job = dict(self.jobs[0], case_id="S1")
        document = dict(raw(), case_id="S1")
        document["openings"][0]["refs"] = ["S1", "O1", "C1", "S1:O1", "S1:C1"]
        self.assertTrue(self.check(document, job, [case])["valid"])
        for unknown in ("K1:O1", "K1:C1", "S1:O2", "S1:C2", "K1"):
            document["openings"][0]["refs"] = [unknown]
            self.assertFalse(self.check(document, job, [case])["valid"])
        document["openings"][0]["refs"] = ["K1:O1"]
        other_case = dict(case, case_id="K1")
        self.assertFalse(self.check(document, job, [case, other_case])["valid"])

    def test_already_qualified_ids_do_not_gain_arbitrary_prefixes(self):
        case = {"case_id": "D1", "supplied_observations": [{"id": "D1-O1", "text": "temporary"}],
                "hard_constraints_with_source": [{"id": "D1-C1", "text": "temporary"}]}
        job = dict(self.jobs[0], case_id="D1")
        document = dict(raw(), case_id="D1")
        document["openings"][0]["refs"] = ["D1", "D1-O1", "D1-C1"]
        self.assertTrue(self.check(document, job, [case])["valid"])
        for unknown in ("D1:D1-O1", "D1:O1", "D1:D1-C1", "D1:C1", "S1:D1-O1"):
            document["openings"][0]["refs"] = [unknown]
            self.assertFalse(self.check(document, job, [case])["valid"])

    def test_p02_construction_disposition_and_no_viable_branch(self):
        job = dict(self.jobs[1], condition="P02")
        document = {"case_id": "temporary-case", "role": "Q", "openings": [], "critiques": [
            {"source_id": "A1", "issue": "No construction asserted in this temporary fixture.",
             "fit": "uncertain", "opening_ids": [], "construction_disposition": "no_viable_branch"}]}
        self.assertTrue(self.check(document, job)["valid"])
        document["critiques"][0]["issue"] = " "
        self.assertFalse(self.check(document, job)["valid"])
        document["critiques"][0]["issue"] = "temporary"
        for state in ("constructed", "tested"):
            document["critiques"][0]["construction_disposition"] = state
            self.assertFalse(self.check(document, job)["valid"])
            document["openings"] = [opening("Q1")]
            document["critiques"][0]["opening_ids"] = ["Q1"]
            self.assertTrue(self.check(document, job)["valid"])
            document["openings"] = []
            document["critiques"][0]["opening_ids"] = []
        del document["critiques"][0]["construction_disposition"]
        self.assertFalse(self.check(document, job)["valid"])
        self.assertTrue(self.check(document, dict(job, condition="critique"))["valid"])

    def test_critique_two_slot_cap(self):
        document = {"case_id": "temporary-case", "role": "Q", "openings": [], "critiques": [
            {"source_id": "A1", "issue": "temporary", "fit": "uncertain", "opening_ids": []}] * 3}
        self.assertFalse(self.check(document, dict(self.jobs[1], condition="critique"))["valid"])

    def test_full_native_chain_and_terminal_audit(self):
        self.valid_raw_join()
        runtime.prepare("critic")
        runtime.spawn("critic", "native-agent-2")
        document = raw("Q", "Q1")
        document["critiques"] = [{"source_id": "Z1", "issue": "temporary", "fit": "uncertain", "opening_ids": ["Q1"]}]
        self.write("outputs/critic.json", document)
        self.assertTrue(runtime.join("critic", "native-agent-2", True)["validation"]["valid"])
        runtime.prepare("distill")
        runtime.spawn("distill", "native-agent-3")
        self.write("outputs/distill.json", self.distill())
        self.assertTrue(runtime.join("distill", "native-agent-3", True)["validation"]["valid"])
        self.assertTrue(runtime.status()["terminal"])
        self.assertEqual(runtime.status()["next_ready_ids"], [])
        report = runtime.audit()
        self.assertTrue(report["ok"], report)
        self.assertTrue(report["terminal"])
        self.assertEqual(report["counts"]["valid"], 3)

    def test_valid_distill_and_source_exclusion(self):
        document = self.distill()
        sources = [raw(), raw("Q", "Q1"), {"role": "D", "openings": [{"id": "D99", "source_ids": ["Z1"]}]}]
        self.assertTrue(self.check(document, self.jobs[2], sources)["valid"])
        document["openings"][0]["source_ids"] = ["Z1", "Q1", "D99"]
        self.assertFalse(self.check(document, self.jobs[2], sources)["valid"])

    def test_lineage_missing_duplicate_orphan_misattribution(self):
        sources = [raw(), raw("Q", "Q1")]
        for change in ("missing", "duplicate", "orphan", "misattributed", "rejected", "unknown-source", "empty-source"):
            with self.subTest(change=change):
                document = self.distill()
                if change == "missing":
                    document["lineage"].pop()
                elif change == "duplicate":
                    document["lineage"].append(copy.deepcopy(document["lineage"][0]))
                elif change == "orphan":
                    document["lineage"][0]["target_ids"] = []
                elif change == "misattributed":
                    document["openings"][0]["source_ids"] = ["Z1"]
                elif change == "rejected":
                    document["lineage"][0].update(disposition="rejected", target_ids=[])
                elif change == "unknown-source":
                    document["openings"][0]["source_ids"] = ["Z1", "UNKNOWN"]
                else:
                    document["openings"][0]["source_ids"] = []
                self.assertFalse(self.check(document, self.jobs[2], sources)["valid"])

    def test_rejected_parked_and_distill_duplicate_ids(self):
        document = self.distill()
        document["openings"] = []
        document["lineage"][0].update(disposition="rejected", target_ids=[])
        document["lineage"][1].update(disposition="parked", target_ids=[])
        self.assertTrue(self.check(document, self.jobs[2], [raw(), raw("Q", "Q1")])["valid"])
        document = self.distill()
        document["openings"].append(copy.deepcopy(document["openings"][0]))
        self.assertFalse(self.check(document, self.jobs[2], [raw(), raw("Q", "Q1")])["valid"])

    def test_dependency_readiness_requires_native_join(self):
        self.assertEqual(runtime.status()["next_ready_ids"], [])
        runtime.prepare("raw")
        self.assertEqual(runtime.status()["next_ready_ids"], ["raw"])
        with self.assertRaises(runtime.RuntimeFault):
            runtime.prepare("critic")
        runtime.spawn("raw", "native-agent-1")
        self.write("outputs/raw.json", raw())
        self.assertEqual(runtime.status()["jobs"]["raw"]["status"], "running")
        with self.assertRaises(runtime.RuntimeFault):
            runtime.prepare("critic")
        runtime.join("raw", "native-agent-1", True)
        runtime.prepare("critic")
        self.assertEqual(runtime.status()["next_ready_ids"], ["critic"])
        self.assertTrue(runtime.audit()["ok"])
        self.assertFalse(runtime.audit()["terminal"])

    def test_static_fixtures_are_not_native_dependencies(self):
        runtime.prepare("raw")
        manifest = runtime.decode(runtime.paths("raw")[1].read_bytes())
        self.assertEqual(manifest["dependencies"], [])
        self.assertEqual(len(manifest["sources"]), 2)
        self.assertFalse(runtime.events()[0]["native"])

    def test_duplicate_spawn_join_wrong_agent_and_observation(self):
        runtime.prepare("raw")
        runtime.spawn("raw", "native-agent-1")
        with self.assertRaises(runtime.RuntimeFault):
            runtime.spawn("raw", "native-agent-1")
        self.write("outputs/raw.json", raw())
        with self.assertRaises(runtime.RuntimeFault):
            runtime.join("raw", "native-agent-1")
        with self.assertRaises(runtime.RuntimeFault):
            runtime.join("raw", "other-agent", True)
        runtime.join("raw", "native-agent-1", True)
        with self.assertRaises(runtime.RuntimeFault):
            runtime.join("raw", "native-agent-1", True)

    def test_failed_output_preserved_and_causal_skips(self):
        runtime.prepare("raw")
        runtime.spawn("raw", "native-agent-1")
        output = self.write("outputs/raw.json", {"case_id": "wrong", "role": "Z", "openings": []})
        original = output.read_bytes()
        receipt = runtime.join("raw", "native-agent-1", True)
        self.assertFalse(receipt["validation"]["valid"])
        self.assertEqual(output.read_bytes(), original)
        self.assertEqual(receipt["sha256"], runtime.sha(original))
        self.assertIsNone(receipt["actual_tokens"])
        self.assertFalse(receipt["os_isolation"])
        with self.assertRaises(runtime.RuntimeFault):
            runtime.prepare("critic")
        runtime.skip("critic")
        runtime.skip("distill")
        report = runtime.audit()
        self.assertTrue(report["ok"], report)
        self.assertTrue(report["terminal"])
        self.assertEqual(report["counts"]["failed"], 1)
        self.assertEqual(report["counts"]["skipped"], 2)
        output.write_text("{}", encoding="utf-8")
        self.assertFalse(runtime.audit()["ok"])

    def test_missing_failed_output_must_stay_missing(self):
        runtime.prepare("raw")
        runtime.spawn("raw", "native-agent-1")
        receipt = runtime.join("raw", "native-agent-1", True)
        self.assertIsNone(receipt["sha256"])
        self.assertIsNone(receipt["known_words"])
        self.assertFalse(receipt["validation"]["valid"])
        self.assertTrue(runtime.audit()["ok"])
        self.write("outputs/raw.json", raw())
        self.assertFalse(runtime.audit()["ok"])

    def test_no_overwrite_and_no_spawn_with_output(self):
        runtime.prepare("raw")
        before = runtime.paths("raw")[0].read_bytes()
        with self.assertRaises(runtime.RuntimeFault):
            runtime.prepare("raw")
        self.assertEqual(runtime.paths("raw")[0].read_bytes(), before)
        self.write("outputs/raw.json", raw())
        with self.assertRaises(runtime.RuntimeFault):
            runtime.spawn("raw", "native-agent-1")
        self.assertFalse(runtime.audit()["ok"])

    def test_source_template_prompt_manifest_and_output_hashes(self):
        for name in ("case.json", "template.txt", "prompts/jobs/raw.txt", "prompts/jobs/raw.manifest.json"):
            with self.subTest(path=name):
                # Recreate the temporary ledger/prompt inside this same temporary root.
                for path in [self.root / "receipts" / "events.jsonl", *runtime.paths("raw")[:2]]:
                    if path.exists():
                        path.unlink()
                runtime.prepare("raw")
                path = self.root / name
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                with self.assertRaises(runtime.RuntimeFault):
                    runtime.spawn("raw", "native-agent-1")
                self.assertFalse(runtime.audit()["ok"])
                path.write_bytes(original)
        for path in [self.root / "receipts" / "events.jsonl", *runtime.paths("raw")[:2]]:
            path.unlink()
        self.valid_raw_join()
        self.write("outputs/raw.json", {"case_id": "temporary-case", "role": "Z", "openings": []})
        self.assertFalse(runtime.audit()["ok"])
        with self.assertRaises(runtime.RuntimeFault):
            runtime.prepare("critic")

    def test_freeze_schedule_hash(self):
        digest = runtime.sha((self.root / "schedule.json").read_bytes())
        self.write("freeze-manifest.json", {"schedule_sha256": digest})
        runtime.prepare("raw")
        self.jobs[0]["condition"] = "changed"
        self.write("schedule.json", {"jobs": self.jobs})
        with self.assertRaises(runtime.RuntimeFault):
            runtime.status()

    def test_validate_alone_does_not_complete(self):
        runtime.prepare("raw")
        runtime.spawn("raw", "native-agent-1")
        self.write("outputs/raw.json", raw())
        self.assertTrue(runtime.validate("raw")["validation"]["valid"])
        self.assertEqual(runtime.status()["jobs"]["raw"]["status"], "running")
        self.assertFalse(runtime.status()["terminal"])

    def test_cli_and_preflight_accounting(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runtime.main(["prepare", "raw"]), 0)
            self.assertEqual(runtime.main(["spawn", "raw", "native-agent-1"]), 0)
        self.write("outputs/raw.json", raw())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runtime.main(["join", "raw", "native-agent-1", "--terminal-observed"]), 0)
        report = runtime.audit()
        self.assertEqual(report["counts"]["preparation_events"], 1)
        self.assertEqual(report["counts"]["preflight_native_spawns"], 1)
        self.assertEqual(report["counts"]["scored_native_spawns"], 0)

    def test_receipt_duplicate_and_order_audit(self):
        self.valid_raw_join()
        receipt = runtime.events()[-1]
        runtime.append(receipt)
        self.assertFalse(runtime.audit()["ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
