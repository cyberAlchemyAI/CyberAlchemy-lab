"""Synthetic evaluation mechanics tests; no experiment artifacts are opened."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import evaluation as ev


def save(root, path, value):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2), encoding="utf-8")
    return target


def output(identifier, text="complete arbitrary semantic evidence P01", sources=None):
    return {"role": "test", "condition": "concealed-method", "job_id": "concealed-job",
            "openings": [{"id": identifier, "claim": text, "mechanism": text,
                          "source_ids": sources or [], "fit": "preserves",
                          "uncertainty": {"reason": "Explicitly uncertain", "prediction": "rival differs"}}]}


def fixture(root):
    save(root, "cases/S.json", {"case_id": "S", "hard_constraints": ["constraint unchanged"]})
    save(root, "archives/S.json", {"families": [{"id": "F01", "signature": "known mechanism"}]})
    save(root, "fixtures/parents.json", {"parents": [{"function": "prior supplied function"}]})
    jobs, units = [], []
    for name in ("Z", "A", "A2", "D", "D2"):
        jobs.append({"job_id": name, "case_id": "S", "stage": "main", "sources": ["cases/S.json", "fixtures/parents.json"]})
        save(root, f"outputs/{name}.json", output("Z1" if name == "Z" else "A1" if name in {"A", "A2"} else "D1", sources=["Z1", "A1"] if name.startswith("D") else []))
    for n, a, d in ((1, "A", "D"), (2, "A2", "D2")):
        units.append({"unit_id": f"unit-{n}", "case_id": "S", "stage": "main",
                      "condition": "concealed-method", "repetition": n,
                      "raw_jobs": ["Z", a], "post_job": d,
                      "semantic_requirement": "causal relation and bounded rejection test"})
    for name in ("T-left", "T-right", "P-left", "P-right"):
        jobs.append({"job_id": name, "case_id": "S", "stage": "p08" if name.startswith("T") else "p09",
                     "sources": ["cases/S.json", "fixtures/tensions.json"]})
        save(root, f"outputs/{name}.json", output("T1" if name.startswith("T") else "D1", sources=["Z1", "A1"]))
    save(root, "fixtures/tensions.json", {"evidence": "fixed cross concern tension"})
    save(root, "inputs/oldD.json", {"openings": [{"id": "Dold", "mechanism": "EVALUATOR_ONLY_SECRET_LOSS"}]})
    schedule = {"jobs": jobs, "units": units,
                "p08_pairs": [{"pair_id": "p8-original", "case_id": "S", "repetition": 1,
                               "arms": {"consensus": "T-left", "P08": "T-right"}}],
                "p09_pairs": [{"pair_id": "p9-original", "case_id": "S",
                               "stratum": "SECRET_STRATUM", "reason": "SECRET_LOSS_REASON",
                               "case": "cases/S.json", "raw_sources": ["outputs/Z.json", "outputs/A.json"],
                               "evaluator_only": "inputs/oldD.json",
                               "arms": {"ordinary": "P-left", "P09": "P-right"}}]}
    save(root, "schedule.json", schedule)
    events = []
    for job in jobs:
        raw = (root / f'outputs/{job["job_id"]}.json').read_bytes()
        events.append({"event": "join", "job_id": job["job_id"], "native": True,
                       "terminal_observed": True, "validation": {"valid": True, "errors": []},
                       "sha256": hashlib.sha256(raw).hexdigest(), "known_words": len(raw.split())})
    (root / "events.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
    return schedule


def main_review(packet, reviewer="J1"):
    review = {"reviewer_id": reviewer, "case_id": packet["case_id"],
              "packet_sha256": packet["packet_sha256"], "families": [], "units": [], "limits": "synthetic"}
    members = []
    for unit in packet["units"]:
        raws = []
        for rid in ev._main_raw_ids(unit):
            members.append(f'{unit["unit_id"]}:{rid}')
            raws.append({"raw_id": rid, "intelligible": True, "family_id": "family-any-label",
                         "kind": "mechanism", "novelty": "new", "usefulness": 1,
                         "fit": "preserves", "observability": 2, "support": "inference",
                         "retention": "retained" if ev._post_valid(unit) else "unobservable",
                         "contract": "met", "reason": "arbitrary full reason",
                         "retention_reason": "whole causal and uncertainty trace"})
        review["units"].append({"unit_id": unit["unit_id"], "raw": raws,
                                "post_only": [], "lineage_comment": "Every relation retained or unobservable"})
    if members:
        review["families"] = [{"family_id": "family-any-label", "members": members,
                               "signature": "synthetic causal identity", "archive_matches": [],
                               "uncertain_with": [], "reason": "synthetic partition"}]
    return review


def pair_review(packet, reviewer="J1"):
    review = {"reviewer_id": reviewer, "packet_sha256": packet["packet_sha256"], "pairs": [], "limits": "synthetic"}
    for pair in packet["pairs"]:
        arms = []
        for arm in pair["arms"]:
            row = {"arm_id": arm["arm_id"], "fit": "preserves", "reason": "whole evidence"}
            if packet["kind"] == "p08":
                row.update({"decision_relevant": True, "competing_predictions": True,
                            "probe_feasible": "uncertain", "support": "inference",
                            "distinct_question": False, "unresolved_contradictions": 1})
            else:
                row.update({"raw": [{"source_id": rid, "causal_relation": "retained",
                                     "discriminator": "uncertain", "uncertainty": "retained", "reason": "complete trace"}
                                    for rid in pair["raw_ids"]], "unsupported_additions": []})
            arms.append(row)
        review["pairs"].append({"pair_id": pair["pair_id"], "arms": arms, "contrast": "full comparison"})
    return review


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        fixture(self.root)

    def packets(self, kind="main"):
        paths = ev.prepare(kind, "S" if kind == "main" else None, self.root)
        return tuple(ev.read_json(p) for p in paths)

    def main_inputs(self):
        p1, p2 = self.packets()
        return p1, main_review(p1), p2, main_review(p2, "J2"), ev.read_json(self.root / "blinded/main-S-mapping.json")

    def test_prepare_counterbalanced_and_once_only(self):
        p1, p2 = self.packets()
        self.assertEqual([u["unit_id"] for u in p1["units"]], list(reversed([u["unit_id"] for u in p2["units"]])))
        self.assertEqual(ev._normalized_packet(p1), ev._normalized_packet(p2))
        with self.assertRaises(FileExistsError):
            ev.prepare("main", "S", self.root)

    def test_opaque_ids_stable_and_shared_source_hashes_bound(self):
        p1, p2 = self.packets()
        self.assertEqual(p1["units"][0]["unit_id"], ev.opaque("S", "unit-1"))
        zhashes = [u["raw"][0]["source_sha256"] for u in p1["units"]]
        self.assertEqual(len(set(zhashes)), 1)
        self.assertEqual(p1["case"]["source_sha256"], hashlib.sha256((self.root / "cases/S.json").read_bytes()).hexdigest())
        self.assertEqual(p1["shared_sources"][0]["evidence"]["parents"][0]["function"], "prior supplied function")

    def test_blinding_preserves_semantic_strings_and_lineage(self):
        p1, _ = self.packets()
        text = json.dumps(p1)
        for concealed in ("concealed-method", "concealed-job", "unit-1", "outputs/Z.json", "fixtures/parents.json"):
            self.assertNotIn(concealed, text)
        self.assertIn("complete arbitrary semantic evidence P01", text)
        self.assertEqual(p1["units"][0]["post"]["evidence"]["openings"][0]["source_ids"], ["Z1", "A1"])
        requirements = p1["units"][0]["raw_semantic_requirements"]
        self.assertNotEqual(requirements["Z1"], requirements["A1"])

    def test_saved_file_does_not_establish_native_completion(self):
        (self.root / "events.jsonl").unlink()
        p1, _ = self.packets()
        unit = p1["units"][0]
        self.assertFalse(unit["raw"][0]["disposition"]["terminal_observed"])
        self.assertEqual(unit["raw"][0]["disposition"]["execution"], "missing")
        self.assertEqual(ev._main_raw_ids(unit), ["Z1", "A1"])

    def test_changed_output_invalidates_native_hash_binding(self):
        save(self.root, "outputs/Z.json", output("Z1", "changed after native join"))
        p1, _ = self.packets()
        self.assertEqual(p1["units"][0]["raw"][0]["disposition"]["execution"], "invalid")
        self.assertIn("hash mismatch", p1["units"][0]["raw"][0]["disposition"]["output_error"])

    def test_actual_receipts_event_location_and_missing_terminal_file(self):
        receipts = self.root / "receipts"
        receipts.mkdir()
        (self.root / "events.jsonl").rename(receipts / "events.jsonl")
        (self.root / "outputs/D.json").unlink()
        p1, _ = self.packets()
        self.assertEqual(p1["units"][0]["raw"][0]["disposition"]["execution"], "valid")
        self.assertEqual(p1["units"][0]["post"]["disposition"]["execution"], "invalid")
        self.assertFalse(ev._post_valid(p1["units"][0]))

    def test_nonterminal_native_join_does_not_complete_output(self):
        (self.root / "events.jsonl").write_text(json.dumps({"event": "join", "job_id": "Z", "status": "completed",
                                                          "terminal_observed": False, "native": True,
                                                          "validation": {"valid": True}}) + "\n")
        p1, _ = self.packets()
        self.assertEqual(p1["units"][0]["raw"][0]["disposition"]["execution"], "missing")

    def test_runtime_status_valid_record_is_accepted_without_file_inference(self):
        (self.root / "events.jsonl").unlink()
        runtime = self.root / "tools/runtime.py"
        runtime.parent.mkdir()
        runtime.write_text("def status():\n    return {'jobs': {'Z': {'status': 'valid', 'errors': []}}, 'next_ready_ids': [], 'terminal': False}\n")
        p1, _ = self.packets()
        self.assertEqual(p1["units"][0]["raw"][0]["disposition"]["execution"], "valid")
        self.assertEqual(p1["units"][0]["raw"][1]["disposition"]["execution"], "missing")

    def test_private_source_inventory_keeps_all_paths_with_identical_bytes(self):
        self.packets()
        mapping = ev.read_json(self.root / "blinded/main-S-mapping.json")
        sha = hashlib.sha256((self.root / "outputs/A.json").read_bytes()).hexdigest()
        self.assertEqual(set(mapping["sources"][sha]["paths"]), {"outputs/A.json", "outputs/A2.json"})

    def test_valid_main_review_and_zero_post_additions(self):
        p1, r1, _, _, _ = self.main_inputs()
        self.assertEqual(ev.check("main", p1, r1), [])
        self.assertEqual([u["post_only"] for u in r1["units"]], [[], []])

    def test_normalization_keeps_exact_source_claim_hash_and_constraints(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        result = ev.normalize_main(p1, r1, p2, r2, mapping)
        raw = result["units"][0]["raw"][0]
        self.assertEqual(raw["claim"], "complete arbitrary semantic evidence P01")
        self.assertEqual(raw["source_sha256"], p1["units"][0]["raw"][0]["source_sha256"])
        self.assertEqual(raw["source_evidence"]["fit"], "preserves")
        self.assertNotEqual(raw["claim"], r1["units"][0]["raw"][0]["reason"])

    def test_missing_duplicate_and_unknown_raw_rows_rejected(self):
        p1, r1, _, _, _ = self.main_inputs()
        for mutation in ("missing", "duplicate", "unknown"):
            with self.subTest(mutation=mutation):
                bad = copy.deepcopy(r1)
                raws = bad["units"][0]["raw"]
                if mutation == "missing":
                    raws.pop()
                elif mutation == "duplicate":
                    raws.append(copy.deepcopy(raws[0]))
                else:
                    raws[0]["raw_id"] = "unknown"
                self.assertTrue(ev.check("main", p1, bad))

    def test_missing_and_duplicate_unit_rejected(self):
        p1, r1, _, _, _ = self.main_inputs()
        bad = copy.deepcopy(r1)
        bad["units"].pop()
        self.assertTrue(any("missing" in e for e in ev.check("main", p1, bad)))
        bad = copy.deepcopy(r1)
        bad["units"].append(copy.deepcopy(bad["units"][0]))
        self.assertTrue(any("duplicate" in e for e in ev.check("main", p1, bad)))

    def test_family_partition_unknown_archive_and_duplicate_members_rejected(self):
        p1, r1, _, _, _ = self.main_inputs()
        for field, value in (("members", ["unknown:A1"]), ("archive_matches", ["F999"]),
                             ("uncertain_with", ["undeclared-family"])):
            bad = copy.deepcopy(r1)
            bad["families"][0][field] = value
            self.assertTrue(ev.check("main", p1, bad))
        bad = copy.deepcopy(r1)
        bad["families"][0]["members"].append(bad["families"][0]["members"][0])
        self.assertTrue(ev.check("main", p1, bad))

    def test_boolean_as_integer_and_illegal_enum_rejected(self):
        p1, r1, _, _, _ = self.main_inputs()
        for field, value in (("usefulness", True), ("observability", 3), ("intelligible", 1),
                             ("fit", "safe"), ("contract", "unknown"), ("retention", "absent")):
            bad = copy.deepcopy(r1)
            bad["units"][0]["raw"][0][field] = value
            self.assertTrue(ev.check("main", p1, bad))

    def test_post_only_requires_known_distinct_post_ids(self):
        p1, r1, _, _, _ = self.main_inputs()
        entry = {"post_id": "D1", "support": "unsupported", "fit": "uncertain", "reason": "extra unsupported certainty", "family_id": "optional"}
        r1["units"][0]["post_only"] = [entry]
        self.assertEqual(ev.check("main", p1, r1), [])
        r1["units"][0]["post_only"].append(copy.deepcopy(entry))
        self.assertTrue(ev.check("main", p1, r1))
        r1["units"][0]["post_only"] = [{**entry, "post_id": "orphan"}]
        self.assertTrue(ev.check("main", p1, r1))

    def test_review_hash_binding_and_packet_tampering_rejected(self):
        p1, r1, _, _, _ = self.main_inputs()
        bad = copy.deepcopy(r1)
        bad["packet_sha256"] = "wrong"
        self.assertTrue(ev.check("main", p1, bad))
        p1["case"]["evidence"]["new"] = "unbound"
        self.assertTrue(any("packet hash invalid" in e for e in ev.check("main", p1, r1)))

    def test_family_label_rename_is_not_disagreement(self):
        p1, r1, p2, r2, _ = self.main_inputs()
        r2["families"][0]["family_id"] = "completely-different-label"
        for u in r2["units"]:
            for raw in u["raw"]:
                raw["family_id"] = "completely-different-label"
        comparison = ev.compare("main", p1, r1, p2, r2)
        self.assertEqual(comparison["disputes"], [])
        self.assertEqual(comparison["families"]["clusters"], [])

    def test_membership_disagreement_gates_entire_connected_cluster(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        family = r2["families"].pop()
        for n, member in enumerate(family["members"]):
            fid = f"split-{n}"
            r2["families"].append({**family, "family_id": fid, "members": [member]})
            for unit in r2["units"]:
                for raw in unit["raw"]:
                    if f'{unit["unit_id"]}:{raw["raw_id"]}' == member:
                        raw["family_id"] = fid
        comparison = ev.compare("main", p1, r1, p2, r2)
        self.assertEqual(len(comparison["families"]["clusters"]), 1)
        result = ev.normalize_main(p1, r1, p2, r2, mapping)
        self.assertTrue(result["judgments_locked"])
        self.assertTrue(all(f["equivalence_status"] == "uncertain" for f in result["families"]))
        self.assertTrue(all(f["uncertain_equivalence_with"] for f in result["families"]))
        self.assertTrue(all(raw["judgment_resolved"] for u in result["units"] for raw in u["raw"]))

    def test_uncertain_link_disagreement_compares_members_not_labels(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        for review in (r1, r2):
            original = review["families"].pop()
            members = original["members"]
            for fid, chosen in (("f-left", members[:2]), ("f-right", members[2:])):
                review["families"].append({**original, "family_id": fid, "members": chosen})
                for unit in review["units"]:
                    for raw in unit["raw"]:
                        if f'{unit["unit_id"]}:{raw["raw_id"]}' in chosen:
                            raw["family_id"] = fid
        r2["families"][0]["uncertain_with"] = ["f-right"]
        comparison = ev.compare("main", p1, r1, p2, r2)
        self.assertEqual(comparison["families"]["co_membership"], [])
        self.assertTrue(comparison["families"]["uncertain_links"])
        self.assertTrue(comparison["families"]["clusters"])
        result = ev.normalize_main(p1, r1, p2, r2, mapping)
        self.assertTrue(all(f["equivalence_status"] == "uncertain" for f in result["families"]))

    def test_scalar_dispute_null_preserves_agreed_values_and_all_candidates(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        uid = r1["units"][0]["unit_id"]
        target = next(u for u in r2["units"] if u["unit_id"] == uid)
        rid = r1["units"][0]["raw"][0]["raw_id"]
        next(r for r in target["raw"] if r["raw_id"] == rid)["usefulness"] = 2
        result = ev.normalize_main(p1, r1, p2, r2, mapping)
        raw = result["units"][0]["raw"][0]
        self.assertIsNone(raw["usefulness"])
        self.assertEqual(raw["observability"], 2)
        self.assertEqual(raw["fit"], "preserves")
        self.assertFalse(raw["judgment_resolved"])
        self.assertEqual(raw["unresolved_fields"], ["usefulness"])
        self.assertEqual(sum(len(u["raw"]) for u in result["units"]), 4)
        self.assertEqual(result["units"][0]["unit_id"], "unit-1")

    def test_failed_d_keeps_valid_raw_reviews_but_retention_unobservable(self):
        with (self.root / "events.jsonl").open("a") as stream:
            stream.write(json.dumps({"event": "join", "job_id": "D", "native": True,
                                     "terminal_observed": True, "validation": {"valid": False}}) + "\n")
        p1, r1, p2, r2, mapping = self.main_inputs()
        self.assertEqual(ev.check("main", p1, r1), [])
        unit = next(u for u in r1["units"] if u["unit_id"] == ev.opaque("S", "unit-1"))
        unit["raw"][0]["retention"] = "lost"
        self.assertTrue(any("unobservable" in e for e in ev.check("main", p1, r1)))
        unit["raw"][0]["retention"] = "unobservable"
        result = ev.normalize_main(p1, r1, p2, r2, mapping)
        unit = result["units"][0]
        self.assertTrue(unit["raw_execution_valid"])
        self.assertTrue(unit["raw_assessment_complete"])
        self.assertFalse(unit["post_assessment_complete"])
        self.assertFalse(unit["execution_valid"])
        self.assertIsNone(unit["output_words"])
        self.assertGreater(unit["observed_output_words"], 0)

    def test_retention_only_dispute_preserves_raw_judgment_resolution(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        uid, rid = r1["units"][0]["unit_id"], r1["units"][0]["raw"][0]["raw_id"]
        target_unit = next(unit for unit in r2["units"] if unit["unit_id"] == uid)
        target_raw = next(raw for raw in target_unit["raw"] if raw["raw_id"] == rid)
        target_raw["retention"] = "lost"
        result = ev.normalize_main(p1, r1, p2, r2, mapping)
        raw = result["units"][0]["raw"][0]
        self.assertTrue(raw["raw_judgment_resolved"])
        self.assertEqual(raw["raw_unresolved_fields"], [])
        self.assertFalse(raw["judgment_resolved"])
        self.assertEqual(raw["unresolved_fields"], ["retention"])
        self.assertIsNone(raw["retention"])
        self.assertEqual(raw["novelty"], "new")
        self.assertEqual(raw["fit"], "preserves")
        self.assertEqual(raw["usefulness"], 1)

    def test_incomplete_invalid_review_produces_no_fabricated_rows(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        r2["units"].pop()
        result = ev.normalize_main(p1, r1, p2, r2, mapping)
        self.assertEqual(result["status"], "incomplete")
        self.assertFalse(result["judgments_locked"])
        self.assertEqual(result["units"], [])

    def test_paired_reviewers_must_be_distinct(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        r2["reviewer_id"] = r1["reviewer_id"]
        self.assertEqual(ev.compare("main", p1, r1, p2, r2)["status"], "incomplete")

    def test_changed_between_reviewer_packets_rejected_even_if_resealed(self):
        p1, r1, p2, r2, _ = self.main_inputs()
        p2["case"]["evidence"]["extra"] = "different evidence"
        p2.pop("packet_sha256")
        ev._seal(p2)
        r2["packet_sha256"] = p2["packet_sha256"]
        self.assertEqual(ev.compare("main", p1, r1, p2, r2)["status"], "incomplete")

    def test_scalar_adjudication_only_changes_declared_field(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        uid, rid = r1["units"][0]["unit_id"], r1["units"][0]["raw"][0]["raw_id"]
        target = next(u for u in r2["units"] if u["unit_id"] == uid)
        next(r for r in target["raw"] if r["raw_id"] == rid)["usefulness"] = 2
        adjudication = {"resolutions": [{"candidate_key": f"{uid}:{rid}", "field": "usefulness", "value": 2, "reason": "Declared dispute bounded decision"}], "unresolved": []}
        result = ev.normalize_main(p1, r1, p2, r2, mapping, adjudication)
        raw = result["units"][0]["raw"][0]
        self.assertEqual(raw["usefulness"], 2)
        self.assertEqual(raw["observability"], 2)
        self.assertTrue(raw["judgment_resolved"])
        self.assertEqual(result["unresolved"], [])
        self.assertEqual(r1["units"][0]["raw"][0]["usefulness"], 1)

    def test_adjudication_rejects_agreed_field_bad_enum_duplicate_and_family_edit(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        uid, rid = r1["units"][0]["unit_id"], r1["units"][0]["raw"][0]["raw_id"]
        target = next(u for u in r2["units"] if u["unit_id"] == uid)
        next(r for r in target["raw"] if r["raw_id"] == rid)["fit"] = "uncertain"
        base = {"candidate_key": f"{uid}:{rid}", "field": "fit", "value": "preserves", "reason": "bounded"}
        for resolutions in ([{**base, "field": "usefulness", "value": 0}], [{**base, "value": "invented"}],
                            [base, base], [{**base, "field": "family_id", "value": "guessed-family"}]):
            result = ev.normalize_main(p1, r1, p2, r2, mapping, {"resolutions": resolutions})
            self.assertEqual(result["status"], "incomplete")
            self.assertFalse(result["judgments_locked"])
            self.assertEqual(result["units"], [])

    def test_adjudication_rejects_boolean_integer_and_preserves_unresolved_field(self):
        p1, r1, p2, r2, mapping = self.main_inputs()
        uid, rid = r1["units"][0]["unit_id"], r1["units"][0]["raw"][0]["raw_id"]
        target = next(u for u in r2["units"] if u["unit_id"] == uid)
        target = next(r for r in target["raw"] if r["raw_id"] == rid)
        target["usefulness"], target["fit"] = 2, "uncertain"
        row = {"candidate_key": f"{uid}:{rid}", "field": "usefulness", "value": True, "reason": "bounded"}
        rejected = ev.normalize_main(p1, r1, p2, r2, mapping, {"resolutions": [row]})
        self.assertEqual(rejected["status"], "incomplete")
        row["value"] = 2
        result = ev.normalize_main(p1, r1, p2, r2, mapping, {"resolutions": [row]})
        raw = result["units"][0]["raw"][0]
        self.assertEqual(raw["usefulness"], 2)
        self.assertIsNone(raw["fit"])
        self.assertEqual(raw["unresolved_fields"], ["fit"])

    def test_p08_exact_arm_and_pair_coverage_and_scalar_disagreement(self):
        p1, p2 = self.packets("p08")
        r1, r2 = pair_review(p1), pair_review(p2, "J2")
        self.assertEqual(ev.check("p08", p1, r1), [])
        missing = copy.deepcopy(r1)
        missing["pairs"][0]["arms"].pop()
        self.assertTrue(ev.check("p08", p1, missing))
        duplicate = copy.deepcopy(r1)
        duplicate["pairs"].append(copy.deepcopy(duplicate["pairs"][0]))
        self.assertTrue(ev.check("p08", p1, duplicate))
        aid = r1["pairs"][0]["arms"][0]["arm_id"]
        next(a for a in r2["pairs"][0]["arms"] if a["arm_id"] == aid)["decision_relevant"] = False
        comparison = ev.compare("p08", p1, r1, p2, r2)
        self.assertEqual(comparison["disputes"][0]["field"], "decision_relevant")

    def test_p09_blinds_stratum_reason_old_d_and_methods(self):
        p1, p2 = self.packets("p09")
        text = json.dumps(p1)
        for hidden in ("SECRET_STRATUM", "SECRET_LOSS_REASON", "EVALUATOR_ONLY_SECRET_LOSS", "ordinary", "P09", "inputs/oldD.json", "outputs/Z.json"):
            self.assertNotIn(hidden, text)
        self.assertEqual(p1["pairs"][0]["raw_ids"], ["Z1", "A1"])
        self.assertEqual([a["arm_id"] for a in p1["pairs"][0]["arms"]], list(reversed([a["arm_id"] for a in p2["pairs"][0]["arms"]])))

    def test_p09_each_raw_exactly_once_in_every_arm(self):
        p1, _ = self.packets("p09")
        r1 = pair_review(p1)
        self.assertEqual(ev.check("p09", p1, r1), [])
        for modification in ("missing", "duplicate", "orphan"):
            bad = copy.deepcopy(r1)
            raws = bad["pairs"][0]["arms"][1]["raw"]
            if modification == "missing":
                raws.pop()
            elif modification == "duplicate":
                raws.append(copy.deepcopy(raws[0]))
            else:
                raws[0]["source_id"] = "orphan"
            self.assertTrue(ev.check("p09", p1, bad))

    def test_p09_normalization_preserves_candidates_and_nulls_disputed_scalar(self):
        p1, p2 = self.packets("p09")
        r1, r2 = pair_review(p1), pair_review(p2, "J2")
        aid = r1["pairs"][0]["arms"][0]["arm_id"]
        next(a for a in r2["pairs"][0]["arms"] if a["arm_id"] == aid)["raw"][0]["discriminator"] = "lost"
        mapping = ev.read_json(self.root / "blinded/p09-mapping.json")
        result = ev.normalize_pairs("p09", p1, r1, p2, r2, mapping)
        arm = result["pairs"][0]["arms"][0]
        self.assertIsNone(arm["raw"][0]["discriminator"])
        self.assertEqual(arm["raw"][0]["causal_relation"], "retained")
        self.assertFalse(arm["judgment_resolved"])
        self.assertEqual(len(arm["raw"]), 2)

    def test_resolve_missing_reviews_explicit_gate_and_separate_log(self):
        self.packets()
        result = ev.resolve("main", "S", self.root)
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(result["units"], [])
        self.assertTrue((self.root / "reports/main-S-resolved.json").exists())
        self.assertTrue((self.root / "reports/evaluation-events.jsonl").exists())
        self.assertNotIn('"operation": "resolve"', (self.root / "events.jsonl").read_text())


if __name__ == "__main__":
    unittest.main()
