#!/usr/bin/env python3
"""Mechanical validity tests. All native receipts here are synthetic test fixtures.

Run: PYTHONDONTWRITEBYTECODE=1 python3 tools/test_compose_runtime.py
No agent/model calls, study outputs, or reference-run writes occur in these tests.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import tempfile
import types
import unittest
from unittest.mock import patch

ADAPTER = Path(__file__).with_name("compose_runtime.py")
r = types.ModuleType("compose_test_subject")
r.__file__ = str(ADAPTER)
exec(compile(ADAPTER.read_bytes(), str(ADAPTER), "exec"), r.__dict__)


def case(cid="DEV"):
    c = {"case_id": cid, "phase": "development" if cid == "DEV" else "confirmation", "domain": "neutral synthetic operation",
         "valued_outcome": "Maintain the fixed test outcome", "preferred_dependency": "Existing carrier",
         "causal_return_path_hypothesis": "A proposed return link, not an established cause", "anomaly_id": "O1"}
    for key, prefix, number in (("hard_constraints", "C", 3), ("observations", "O", 5), ("resources", "R", 5),
                                ("parent_operations", "P", 2), ("available_observables", "M", 3), ("unknowns", "U", 2)):
        c[key] = [{"id": prefix + str(i), "text": cid + " stipulated " + prefix + str(i)} for i in range(1, number + 1)]
    for row in c["resources"]:
        row["available"] = row["id"] != "R5"
    c["ordinary_archive"] = [{"id": "A" + str(i), "operation": "Routine operation " + str(i), "relation": "Local archive",
                              "probe": "Ordinary probe", "limits": "Synthetic only"} for i in range(1, 4)]
    return c


def methods():
    return {c: {"name": "Human name for " + c, "instructions": "Use assigned " + c,
                "supplement_branch": "residue" if c in r.RESIDUE else "summary"} for c in r.CONDITIONS}


def guard(job, c):
    return {"job_id": job["job_id"], "case_id": job["case_id"], "outcome": c["valued_outcome"],
            "limits": [{"constraint_id": row["id"], "text": row["text"]} for row in c["hard_constraints"]],
            "burden_observables": ["M1"], "source_refs": ["C1", "M1", "R1"], "unknowns": ["Available work is stipulated"]}


def stage(job):
    value = {"job_id": job["job_id"], "case_id": job["case_id"]}
    if job["role"] == "stage1":
        value.update({"policy": job["condition"], "core": [{"id": "CORE", "text": "OWN_CORE_SECRET", "source_refs": ["O1"]}],
                      "residue": [{"id": "RES1", "text": "OWN_STAGE1_RESIDUE", "source_refs": ["O1"]}],
                      "tension": {"account_a": "A", "account_b": "B", "prediction_a": "A separates", "prediction_b": "B separates"}})
    else:
        value.update({"summary": [{"id": "SUM", "text": "ONLY_SUMMARY", "source_refs": ["O1"]}],
                      "residue": [{"id": "RES", "text": "ONLY_RESIDUE", "source_refs": ["O1"]}]})
    return value


def card(ident="CARD", supplement="SUM", resource="R1"):
    return {"id": ident, "anchor": "Fixed outcome", "mutation": "Hypothetical change", "construction": "Bounded operation",
            "rival": "Unchanged carrier explains result", "probe": "Compare the admitted observable", "prediction_candidate": "Observable separates",
            "prediction_rival": "Observable is unchanged", "defeat": "No separating observation", "resources": [resource],
            "source_refs": ["O1", "M1"], "residue_refs": [supplement], "burden": "Stipulated work", "unknowns": ["No actual effect observed"]}


def builder(job, count=1):
    supplement = "RES" if job["condition"] in r.RESIDUE else "SUM"
    return {"job_id": job["job_id"], "case_id": job["case_id"], "cards": [card("CARD" + str(i), supplement) for i in range(count)],
            "no_opening_reason": None if count else "No supported opening in admitted inputs"}


def review(packet):
    return {"job_id": packet["job_id"], "case_id": packet["case_id"],
            "units": [{"unit_id": u["unit_id"], "status": u["status"], "reason": "Supplied structural disposition"} for u in packet["units"]],
            "cards": [{"card_id": c["card_id"], "unit_id": c["unit_id"], **{axis: True for axis in r.AXES}, "reason": "Synthetic judgment"} for c in packet["cards"]],
            "archive_pairs": [{"card_id": c["card_id"], "archive_id": a["id"], "relation": "distinct", "reason": "Synthetic relation"} for c in packet["cards"] for a in packet["archive"]],
            "candidate_pairs": [{"left": a["card_id"], "right": b["card_id"], "relation": "distinct", "reason": "Synthetic relation"} for a, b in r.itertools.combinations(packet["cards"], 2)]}


def witness(handle):
    return {"handle": handle, "observation": "FINAL", "native_tool": "collaboration", "final_text": "SYNTHETIC UNIT-TEST FINAL ONLY",
            "observer": "unit-test-fixture-not-actual-native-evidence", "worker_create_exclusive_reported": True}


class Fixture:
    def __init__(self, freeze=True):
        self.temp = tempfile.TemporaryDirectory(prefix="compose-runtime-test-")
        self.root = Path(self.temp.name)
        for d in ("inputs", "prompts", "preparation", "tools", "receipts"):
            (self.root / d).mkdir()
        self.write("inputs/cases.json", {cid: case(cid) for cid in r.CASES})
        self.write("inputs/methods.json", methods())
        self.write("preparation/BUDGET.v1.json", {"scored": {"total": 132}, "maximum_native_calls": 143,
                   "output_caps": {"proposal_normalized_json_words": 600, "distillation_normalized_json_words": 600,
                                   "builder_normalized_json_words": 600, "cards_per_builder": 1, "review_normalized_json_words": 16000}})
        self.write("preparation/ENGINEER-RECEIPT.v1.json", {"classification": "synthetic test fixture"})
        self.write("preparation/BALANCER-3.v1.json", {"verdict": "pass", "blocking_issues": [], "checks": [{"id": "test", "status": "pass", "reason": "fixture"}]})
        self.write("preparation/CAPACITY.v1.json", {"verdict": "pass", "classification": "synthetic test fixture"})
        self.write("receipts/PREP-BALANCER-3.native.json", witness("TEST-PRELAUNCH"))
        self.write("receipts/CAPACITY.native.json", witness("TEST-CAPACITY"))
        capacity_packet = {**ScoreFixture().packet, "job_id": "CAPACITY", "case_id": "CAPACITY"}
        self.write("capacity/review-packet.json", capacity_packet)
        self.write("raw/CAPACITY.review.json", review(capacity_packet))
        (self.root / "CONTRACT.md").write_text("Synthetic test contract\n")
        (self.root / "prompts/COMMON.md").write_text("Synthetic common prompt\n")
        shutil.copyfile(ADAPTER, self.root / "tools/compose_runtime.py")
        (self.root / "tools/test_compose_runtime.py").write_text("# Synthetic fixture source\n")
        self.rt = r.Runtime(self.root)
        self.rt.init()
        if freeze:
            self.rt.freeze()

    def write(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(r.encode(value))

    def close(self):
        self.temp.cleanup()

    def run(self, jid, value=None, raw=None):
        self.rt.start(jid)
        handle = "TEST-NATIVE-" + jid
        self.rt.spawned(jid, handle)
        if value is not None:
            with self.rt.output(jid).open("xb") as target:
                target.write(r.encode(value))
        if raw is not None:
            with self.rt.output(jid).open("xb") as target:
                target.write(raw)
        return self.rt.finish(jid, witness(handle))

    def upstream(self, condition="O"):
        if not self.rt.status("DEV-guard")["terminal"]:
            self.run("DEV-guard", guard(self.rt.job("DEV-guard"), case()))
        for role in ("stage1", "stage2"):
            jid = "DEV-" + condition + "-" + role
            self.run(jid, stage(self.rt.job(jid)))


class ScoreFixture(r.Runtime):
    """In-memory scoring fixture; independent review schema still validated."""
    def __init__(self, empty=()):
        self.cases = {cid: case(cid) for cid in r.CASES}
        self.jobs = r.make_plan()
        self.states = {j["job_id"]: {"terminal": True, "valid": True, "disposition": "finished",
                       "receipt": {"review_lock": j["role"] == "review", "observation": "FINAL"}} for j in self.jobs["jobs"]}
        self.private = {}
        units, cards = [], []
        for n, condition in enumerate(r.CONDITIONS):
            unitid = "DEV-U%02d" % (n + 1)
            units.append({"unit_id": unitid, "status": "valid", "reason": "test"})
            if condition not in empty:
                cardid = unitid + "-C01"
                cards.append({"card_id": cardid, "unit_id": unitid, "declared_card": card(), "structurally_valid_unit": True, "failure_reason": None})
                self.private[cardid] = {"condition": condition, "job_id": "DEV-" + condition + "-builder", "index": 0}
        self.packet = {"job_id": "DEV-review1", "case_id": "DEV", "case": self.cases["DEV"], "archive": self.cases["DEV"]["ordinary_archive"],
                       "units": units, "cards": cards, "rubric": r.RUBRIC}
        self.reviews = [review(self.packet), review({**self.packet, "job_id": "DEV-review2"})]

    def plan(self):
        return self.jobs

    def case(self, cid):
        return self.cases[cid]

    def status(self, jid):
        return self.states[jid]

    def checked_terminal(self, jid):
        return self.status(jid)

    def review_packet(self, job):
        return {**self.packet, "job_id": job["job_id"]}, self.private

    def join_body(self, jid):
        n = 0 if jid.endswith("review1") else 1
        r.validate_review(self.reviews[n], {**self.packet, "job_id": jid})
        return self.reviews[n]

    def cardid(self, condition):
        return next(c for c, b in self.private.items() if b["condition"] == condition)


class PureValidationTests(unittest.TestCase):
    def test_machine_condition_alias_masked_without_raw_mutation(self):
        raw = {"id": "raw-id", "condition_id": "R01", "construction": "keep semantic body"}
        before = copy.deepcopy(raw)
        projected = r.blind_card(raw, "opaque-card")
        self.assertEqual(projected["condition_id"], "<opaque routing identity>")
        self.assertEqual(projected["construction"], raw["construction"])
        self.assertEqual(raw, before)

    def test_reference_is_unchanged_and_independent(self):
        before = r.sha(r.REFERENCE_PATH)
        self.assertIs(r.validate_output, r._legacy.validate_output)
        self.assertNotEqual(r._legacy.CASES, r.CASES)
        self.assertNotEqual(r._legacy.RUBRIC["review_soft_word_cap"], r.RUBRIC["review_soft_word_cap"])
        r.validate_cases({cid: case(cid) for cid in r.CASES})
        self.assertEqual(before, r.sha(r.REFERENCE_PATH))

    def test_exact_registry_and_nonempty_domain(self):
        r.validate_cases({cid: case(cid) for cid in r.CASES})
        bad = {cid: case(cid) for cid in r.CASES}
        bad["DEV"]["observations"][0]["id"] = "CASE"
        with self.assertRaises(r.GuardError):
            r.validate_cases(bad)
        bad = {cid: case(cid) for cid in r.CASES}
        bad["CONF"]["case_id"] = "DEV"
        with self.assertRaises(r.GuardError):
            r.validate_cases(bad)

    def test_method_branch_policy_is_machine_exact(self):
        good = methods()
        r.validate_methods(good)
        good["R05"]["supplement_branch"] = "summary"
        with self.assertRaises(r.GuardError):
            r.validate_methods(good)
        jobs = r.make_plan()["jobs"]
        j = next(j for j in jobs if j["job_id"] == "DEV-R01-stage1")
        value = stage(j)
        r.validate_output(j, value, case())
        value["policy"] = "Human name for R01"
        with self.assertRaises(r.GuardError):
            r.validate_output(j, value, case())

    def test_r04_separate_fresh_attack_role_directives(self):
        jobs = r.make_plan()["jobs"]
        first = next(j for j in jobs if j["job_id"] == "DEV-R04-stage1")
        second = next(j for j in jobs if j["job_id"] == "DEV-R04-stage2")
        self.assertIn("carrier migration only", r.base_prompt(first, "test").decode())
        self.assertIn("fresh attacker of the stage1 proposed carrier", r.base_prompt(second, "test").decode())
        self.assertIn("actor burden", r.base_prompt(second, "test").decode())

    def test_guard_fixed_outcome_constraint_coverage_and_cap(self):
        j = r.make_plan()["jobs"][0]
        value = guard(j, case())
        r.validate_guard(j, value, case())
        for key, replacement in (("outcome", "Choose an improved outcome"), ("limits", value["limits"][:-1]),
                                 ("burden_observables", ["R1"]), ("source_refs", ["DEV"]),
                                 ("unknowns", ["word " * 601])):
            bad = {**value, key: replacement}
            with self.subTest(key=key), self.assertRaises(r.GuardError):
                r.validate_guard(j, bad, case())
        prompt = r.base_prompt(j, "test").decode()
        self.assertIn("Never propose or select methods, inversions, attacks", prompt)

    def test_source_closure_rejects_routing_archive_and_generated_ids(self):
        j = next(j for j in r.make_plan()["jobs"] if j["job_id"] == "DEV-O-builder")
        for forbidden in ("DEV", "DEV-O-builder", "O", "A1", "CARD0", "SUM", "R01", "valued_outcome"):
            value = builder(j)
            value["cards"][0]["source_refs"] = [forbidden]
            with self.subTest(forbidden=forbidden), self.assertRaises(r.GuardError):
                r.validate_output(j, value, case(), ["SUM"])

    def test_full_review_pair_and_archive_coverage(self):
        fixture = ScoreFixture()
        value = fixture.reviews[0]
        self.assertEqual(sum(len(value[k]) for k in ("units", "cards", "archive_pairs", "candidate_pairs")), 315)
        r.validate_review(value, fixture.packet)
        for section in ("units", "cards", "archive_pairs", "candidate_pairs"):
            incomplete = copy.deepcopy(value)
            incomplete[section].pop()
            with self.subTest(section=section), self.assertRaises(r.GuardError):
                r.validate_review(incomplete, fixture.packet)
        duplicate = copy.deepcopy(value)
        duplicate["candidate_pairs"].append(duplicate["candidate_pairs"][0])
        with self.assertRaises(r.GuardError):
            r.validate_review(duplicate, fixture.packet)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.rt = self.f.rt

    def tearDown(self):
        self.f.close()

    def test_ready_is_read_only_and_conf_not_admitted(self):
        logs = list(self.rt.p("events/log").iterdir())
        self.assertEqual([j["job_id"] for j in self.rt.ready()["ready"]], ["DEV-guard"])
        self.assertEqual(logs, list(self.rt.p("events/log").iterdir()))
        with self.assertRaises(r.GuardError):
            self.rt.start("CONF-guard")
        with self.assertRaises(r.GuardError):
            self.rt.gate("CONF-S01-stage1")

    def test_no_file_only_native_or_retry(self):
        with self.assertRaises(r.GuardError):
            self.rt.finish("DEV-guard", witness("TEST"))
        self.rt.output("DEV-guard").write_bytes(r.encode(guard(self.rt.job("DEV-guard"), case())))
        with self.assertRaises(r.GuardError):
            self.rt.start("DEV-guard")
        self.rt.output("DEV-guard").unlink()
        self.f.run("DEV-guard", guard(self.rt.job("DEV-guard"), case()))
        with self.assertRaises(r.GuardError):
            self.rt.start("DEV-guard")
        with self.assertRaises(r.GuardError):
            self.rt.spawned("DEV-guard", "TEST-NEW")
        with self.assertRaises(r.GuardError):
            self.rt.finish("DEV-guard", witness("TEST-NATIVE-DEV-guard"))

    def test_final_witness_is_required(self):
        self.rt.start("DEV-guard")
        self.rt.spawned("DEV-guard", "TEST-HANDLE")
        self.rt.output("DEV-guard").write_bytes(r.encode(guard(self.rt.job("DEV-guard"), case())))
        bad = witness("TEST-HANDLE")
        bad["observation"] = "RUNNING"
        with self.assertRaises(r.GuardError):
            self.rt.finish("DEV-guard", bad)
        bad = witness("WRONG-HANDLE")
        with self.assertRaises(r.GuardError):
            self.rt.finish("DEV-guard", bad)
        self.assertEqual(self.rt.status("DEV-guard")["disposition"], "spawned")

    def test_gate_waits_for_invalid_terminal_and_preserves_missing(self):
        with self.assertRaises(r.GuardError):
            self.rt.gate("DEV-O-stage1")
        self.rt.start("DEV-guard")
        self.rt.spawned("DEV-guard", "TEST-MISSING")
        with self.assertRaises(r.GuardError):
            self.rt.gate("DEV-O-stage1")
        terminal = self.rt.finish("DEV-guard", witness("TEST-MISSING"))
        self.assertFalse(terminal["valid"])
        self.assertIsNone(terminal["output_sha256"])
        self.rt.gate("DEV-O-stage1")
        self.rt.gate("DEV-O-stage2")
        self.rt.gate("DEV-O-builder")
        with self.assertRaises(r.GuardError):
            self.rt.gate("DEV-review1")
        self.rt.output("DEV-guard").write_bytes(b"{}")
        with self.assertRaises(r.GuardError):
            self.rt.checked_terminal("DEV-guard")

    def test_builder_isolation_both_branches(self):
        for condition in ("O", "S06", "R01", "R05"):
            self.f.upstream(condition)
            jid = "DEV-" + condition + "-builder"
            admitted = self.rt.start(jid)
            payload = self.rt.load("prompts/actual/" + jid + ".payload.json")
            self.assertEqual(set(payload), {"case", "archive", "method", "supplement"})
            self.assertNotIn("stage1", payload)
            self.assertNotIn("outcome_guard", payload)
            self.assertNotIn("ordinary_archive", payload["case"])
            self.assertEqual(payload["method"]["condition_id"], condition)
            text = Path(admitted["prompt_path"]).read_text()
            self.assertNotIn("OWN_CORE_SECRET", text)
            self.assertNotIn("CONF stipulated", text)
            if condition in r.RESIDUE:
                self.assertIn("ONLY_RESIDUE", text)
                self.assertNotIn("ONLY_SUMMARY", text)
            else:
                self.assertIn("ONLY_SUMMARY", text)
                self.assertNotIn("ONLY_RESIDUE", text)
            self.assertIn("CONDITION_ID=" + condition, admitted["native_worker_task"])
            self.assertEqual(Path(admitted["prompt_path"]).read_bytes(), self.rt.p("development/example-prompts/" + jid + ".md").read_bytes())

    def test_builder_caps_and_received_reference(self):
        self.f.upstream()
        j = self.rt.job("DEV-O-builder")
        self.rt.validation(j, builder(j))
        with self.assertRaises(r.GuardError):
            self.rt.validation(j, builder(j, 2))
        oversized = builder(j)
        oversized["cards"][0]["burden"] = "word " * 601
        with self.assertRaises(r.GuardError):
            self.rt.validation(j, oversized)
        unavailable = builder(j)
        unavailable["cards"][0]["resources"] = ["R5"]
        self.assertTrue(self.rt.validation(j, unavailable), "availability belongs to qualification, not schema")
        omitted = builder(j)
        omitted["cards"][0]["residue_refs"] = ["RES"]
        with self.assertRaises(r.GuardError):
            self.rt.validation(j, omitted)

    def test_source_and_admitted_literal_hash_drift(self):
        self.rt.p("inputs/methods.json").write_text("{}")
        with self.assertRaises(r.GuardError):
            self.rt.start("DEV-guard")

    def test_admitted_literal_and_payload_reconstruction(self):
        admitted = self.rt.start("DEV-guard")
        self.rt.reconstruct("DEV-guard")
        self.rt.p("prompts/actual/DEV-guard.payload.json").write_text("{}")
        with self.assertRaises(r.GuardError):
            self.rt.spawned("DEV-guard", "TEST-DRIFT")
        self.assertEqual(admitted["condition_id"], None)

    def test_first_observed_bytes_cannot_change(self):
        self.rt.start("DEV-guard")
        self.rt.output("DEV-guard").write_bytes(r.encode(guard(self.rt.job("DEV-guard"), case())))
        self.rt.spawned("DEV-guard", "TEST-EARLY")
        self.rt.output("DEV-guard").write_bytes(b"{}")
        with self.assertRaises(r.GuardError):
            self.rt.finish("DEV-guard", witness("TEST-EARLY"))

    def test_terminal_locks_invalid_outputs_without_repair(self):
        result = self.f.run("DEV-guard", raw=b"this is not JSON")
        self.assertFalse(result["valid"])
        self.assertEqual(self.rt.p("receipts/raw/DEV-guard.first.bin").read_bytes(), b"this is not JSON")
        self.assertEqual(self.rt.p("development/example-outputs/DEV-guard.json").read_bytes(), b"this is not JSON")
        self.rt.output("DEV-guard").write_bytes(r.encode(guard(self.rt.job("DEV-guard"), case())))
        with self.assertRaises(r.GuardError):
            self.rt.checked_terminal("DEV-guard")

    def test_same_byte_rewrite_after_lock_is_detected(self):
        self.f.run("DEV-guard", guard(self.rt.job("DEV-guard"), case()))
        original = self.rt.output("DEV-guard").read_bytes()
        self.rt.output("DEV-guard").write_bytes(original)
        with self.assertRaises(r.GuardError):
            self.rt.checked_terminal("DEV-guard")

    def test_handle_uniqueness_and_exclusive_receipts(self):
        self.f.run("DEV-guard", guard(self.rt.job("DEV-guard"), case()))
        self.rt.start("DEV-O-stage1")
        with self.assertRaises(r.GuardError):
            self.rt.spawned("DEV-O-stage1", "TEST-NATIVE-DEV-guard")
        with self.assertRaises(FileExistsError):
            self.rt.save("receipts/jobs/DEV-guard.finished.json", {"overwrite": True})

    def test_no_python3_blocks_initialization(self):
        other = self.rt.p("uninitialized-test-root")
        other.mkdir()
        with patch.object(r.shutil, "which", return_value=None), self.assertRaises(r.GuardError):
            r.Runtime(other).init()

    def test_freeze_rejects_stale_prepared_source_and_missing_capacity_pairs(self):
        other = Fixture(freeze=False)
        try:
            other.rt.p("prompts/COMMON.md").write_text("Changed after init")
            with self.assertRaises(r.GuardError):
                other.rt.freeze()
        finally:
            other.close()
        other = Fixture(freeze=False)
        try:
            assessment = other.rt.load("raw/CAPACITY.review.json")
            assessment["candidate_pairs"].pop()
            other.write("raw/CAPACITY.review.json", assessment)
            with self.assertRaises(r.GuardError):
                other.rt.freeze()
            self.assertFalse(other.rt.p("events/freeze.json").exists())
        finally:
            other.close()


class ReviewAndScoreTests(unittest.TestCase):
    def test_qualified_composition_distinct_against_every_raw_comparator(self):
        fixture = ScoreFixture()
        result = fixture.score_case("DEV")
        row = result["recipes"]["R01"]
        self.assertTrue(row["composition_adds"])
        self.assertEqual(len(row["card_addition_assessments"][0]["pairs"]), 3)
        self.assertEqual(row["comparators"], ["O", "S01", "S06", "R01"])
        self.assertEqual(result["chains"]["R01"]["semantic_recipe_fidelity"], "not_checked")

    def test_invalid_comparator_is_null_valid_zero_is_legitimate(self):
        fixture = ScoreFixture(empty=("S01", "S06"))
        self.assertTrue(fixture.score_case("DEV")["recipes"]["R01"]["composition_adds"])
        self.assertEqual(fixture.score_case("DEV")["conditions"]["S01"]["qualified"], 0)
        fixture.states["DEV-S01-stage1"]["valid"] = False
        row = fixture.score_case("DEV")["recipes"]["R01"]
        self.assertIsNone(row["composition_adds"])
        self.assertIsNone(row["qualified_additions"])
        self.assertFalse(row["all_four_chains_valid"])

    def test_unknown_pair_is_null_equivalence_is_no_addition(self):
        fixture = ScoreFixture()
        ids = {fixture.cardid("R01"), fixture.cardid("S06")}
        row = next(row for row in fixture.reviews[0]["candidate_pairs"] if {row["left"], row["right"]} == ids)
        row["relation"] = "unknown"
        self.assertIsNone(fixture.score_case("DEV")["recipes"]["R01"]["composition_adds"])
        row["relation"] = "equivalent"
        self.assertFalse(fixture.score_case("DEV")["recipes"]["R01"]["composition_adds"])

    def test_null_axis_and_unknown_archive_are_uncertain_not_false(self):
        for kind in ("axis", "archive"):
            with self.subTest(kind=kind):
                fixture = ScoreFixture()
                ident = fixture.cardid("R01")
                if kind == "axis":
                    row = next(row for row in fixture.reviews[0]["cards"] if row["card_id"] == ident)
                    row["anchor_fit"] = None
                else:
                    row = next(row for row in fixture.reviews[0]["archive_pairs"] if row["card_id"] == ident)
                    row["relation"] = "unknown"
                result = fixture.score_case("DEV")
                self.assertIsNone(result["recipes"]["R01"]["composition_adds"])
                self.assertEqual(result["conditions"]["R01"]["uncertainty_eligible"], 1)
                if kind == "axis":
                    row["anchor_fit"] = False
                else:
                    row["relation"] = "equivalent"
                self.assertFalse(fixture.score_case("DEV")["recipes"]["R01"]["composition_adds"])

    def test_unavailable_resources_override_positive_reviews(self):
        fixture = ScoreFixture()
        ident = fixture.cardid("R01")
        next(c for c in fixture.packet["cards"] if c["card_id"] == ident)["declared_card"]["resources"] = ["R5"]
        result = fixture.score_case("DEV")
        self.assertEqual(result["conditions"]["R01"]["qualified"], 0)
        self.assertEqual(result["conditions"]["R01"]["uncertainty_eligible"], 0)
        self.assertFalse(result["recipes"]["R01"]["composition_adds"])

    def test_invalid_review_lock_makes_every_addition_null(self):
        fixture = ScoreFixture()
        fixture.states["DEV-review2"]["valid"] = False
        result = fixture.score_case("DEV")
        self.assertFalse(result["both_review_locks_valid"])
        self.assertTrue(all(row["composition_adds"] is None for row in result["recipes"].values()))

    def test_failed_raw_extra_cards_are_preserved_and_blinded(self):
        f = Fixture()
        try:
            rt = f.rt
            # Inject only explicit test terminal fixtures to exercise packet preservation.
            for condition in r.CONDITIONS:
                jid = "DEV-" + condition + "-builder"
                if condition == "R01":
                    raw = {"cards": [card("ROUTING-CARD"), "malformed declared card", {"id": "another", "policy": "R01", "condition_id": "R01"}]}
                    f.write("raw/" + jid + ".json", raw)
                    f.write("receipts/jobs/" + jid + ".finished.json", {"valid": False, "reason": "one-card cap failure", "output_sha256": r.sha(rt.output(jid))})
                else:
                    f.write("receipts/jobs/" + jid + ".gated.json", {"valid": False, "reason": "fixture gated", "output_sha256": None})
            packet, private = rt.review_packet(rt.job("DEV-review1"))
            self.assertEqual(len(packet["units"]), 21)
            self.assertEqual(len(packet["cards"]), 3)
            self.assertEqual(len(private), 3)
            self.assertTrue(all(c["failure_reason"] for c in packet["cards"]))
            self.assertFalse(any(c["structurally_valid_unit"] for c in packet["cards"]))
            encoded = r.encode(packet).decode()
            self.assertNotIn("ROUTING-CARD", encoded)
            self.assertNotIn('"policy": "R01"', encoded)
            self.assertNotIn('"condition_id": "R01"', encoded)
            self.assertEqual(r.read_json(rt.output("DEV-R01-builder"))["cards"][2]["condition_id"], "R01")
            self.assertIn("malformed declared card", encoded)
            r.validate_review(review(packet), packet)
        finally:
            f.close()


class FullClosureTests(unittest.TestCase):
    def test_all_132_slots_close_with_real_gate_semantics_and_both_review_barrier(self):
        f = Fixture()
        try:
            rt = f.rt
            for cid in r.CASES:
                if cid == "CONF":
                    self.assertTrue(rt.allowed_phase(rt.job("CONF-guard")))
                f.run(cid + "-guard", value={})  # Deliberate invalid first attempt.
                for condition in r.CONDITIONS:
                    for role in ("stage1", "stage2", "builder"):
                        rt.gate(cid + "-" + condition + "-" + role)
                f.run(cid + "-review1", review(rt.review_packet(rt.job(cid + "-review1"))[0]))
                if cid == "DEV":
                    self.assertFalse(rt.allowed_phase(rt.job("CONF-guard")))
                # The raw second DEV assessment is invalid but still terminal and locked.
                f.run(cid + "-review2", {} if cid == "DEV" else review(rt.review_packet(rt.job(cid + "-review2"))[0]))
            verification = rt.verify()
            self.assertEqual(verification["terminal_final_calls"], 6)
            result = rt.report()
            data = r.read_json(result["report"]["path"])
            self.assertEqual(data["gated"], 126)
            self.assertEqual(data["actual_scored_spawned"], 6)
            self.assertEqual(len(data["generation_coverage"]["DEV"]), 21)
            self.assertTrue(all(row["adds_in_both_cases"] is None for row in data["recipes"].values()))
            self.assertFalse(rt.status("DEV-review2")["valid"])
            self.assertTrue(rt.status("DEV-review2")["receipt"]["review_lock"])
            rt.verify()
        finally:
            f.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
