#!/usr/bin/env python3
"""Synthetic temporary-root guard tests. Never starts a native model call."""
import copy
import itertools
import json
from pathlib import Path
import random
import tempfile
import unittest
import ten_runtime as tr

def synthetic_cases():
    cases = []
    for cid in tr.CASES:
        cases.append({
            "case_id":cid, "phase":"development" if cid in ("PD","WD") else "confirmation",
            "domain":"physical" if cid in ("PD","PC") else "workflow",
            "valued_outcome":"Synthetic retained outcome", "preferred_dependency":"R1 operating dependency",
            "causal_return_path_hypothesis":"Unobserved proposed return link", "anomaly_id":"O1",
            "hard_constraints":[{"id":"C"+str(i),"text":"Constraint "+str(i)} for i in range(1,4)],
            "observations":[{"id":"O"+str(i),"text":"Synthetic observation "+str(i)} for i in range(1,6)],
            "resources":[{"id":"R"+str(i),"text":"Resource "+str(i),"available":i != 5} for i in range(1,6)],
            "parent_operations":[{"id":"P"+str(i),"text":"Parent "+str(i)} for i in range(1,3)],
            "available_observables":[{"id":"M"+str(i),"text":"Observable "+str(i)} for i in range(1,4)],
            "unknowns":[{"id":"U"+str(i),"text":"Unknown "+str(i)} for i in range(1,3)],
            "ordinary_archive":[{"id":"A"+str(i),"operation":"Operation "+str(i),"relation":"Hypothetical relation",
                                 "probe":"Hypothetical probe","limits":"Unmeasured"} for i in range(1,5)],
        })
    return {"classification":"synthetic_fresh_case_and_archive_preparation","cases":cases,
            "independence_note":"No prior candidates, strategy prompts or results were read"}

def review_answer(packet, relation="unknown"):
    return {
        "job_id":packet["job_id"],"case_id":packet["case_id"],
        "units":[{"unit_id":u["unit_id"],"status":u["status"],"reason":"Synthetic validator fixture"} for u in packet["units"]],
        "cards":[dict({"card_id":c["card_id"],"unit_id":c["unit_id"],"reason":"Synthetic assessment fixture"},
                      **{axis:True for axis in tr.RUBRIC["axes"]}) for c in packet["cards"]],
        "archive_pairs":[{"card_id":c["card_id"],"archive_id":a["id"],"relation":"distinct","reason":"Fixture distinct"}
                         for c in packet["cards"] for a in packet["archive"]],
        "candidate_pairs":[{"left":a["card_id"],"right":b["card_id"],"relation":relation,"reason":"Fixture relation"}
                           for a,b in itertools.combinations(packet["cards"],2)],
    }

def fake_witness(handle):
    return {"handle":handle,"observation":"FINAL","native_tool":"collaboration","final_text":"SYNTHETIC TEST ONLY; no actual call",
            "observer":"unit-test fixture, never production evidence"}

class Guards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ten-synthetic-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.rt = tr.Runtime(self.root)
        self.rt.save("fixture-dispatch-source.txt",b"Synthetic external source binding\n",True)
        files = {
            "SCOPE.json":{"scope_extension_before_any_scored_call":{"total_scored_native_calls":184},"source_bindings":[]},
            "PREPARATION-BUDGET.json":{"scored_calls":184},
            "PREPARATION-BUDGET-AMENDMENT.v1.json":{"overhead_calls":7,"scored_calls":184},
            "runtime.dispatch.json":{"fixture":"synthetic"},
            "dispatch-validation.v2.json":{"fixture":"synthetic"},
            "receipts/preparation-arithmetic-correction.v1.json":{"correct_maximal_review_rows":532},
            "receipts/dispatch-source-bindings.v1.json":{"bindings":[{"path":str(self.root/"fixture-dispatch-source.txt"),"sha256":tr.sha(self.root/"fixture-dispatch-source.txt")}]},
            "PROPOSER-TRACE.json":{"fixture":"synthetic"},
            "inputs/fresh-cases-and-archives.v1.json":synthetic_cases(),
        }
        for path,value in files.items():
            self.rt.save(path,value)
        for path in ("tools/ten_runtime.py","tools/test_ten_runtime.py","CONTRACT.md","prompts/PREP-proposer.v1.txt","SCORING-EXAMPLES.md"):
            self.rt.save(path,b"Synthetic source binding only\n",True)
        self.rt.prepare()
    def freeze(self):
        self.rt.capacity()
        self.rt.save("capacity/output.json",review_answer(self.rt.load("capacity/fixture.json")))
        self.rt.save("fixture-capacity-witness.json",fake_witness("fake-capacity"))
        self.rt.save("fixture-prelaunch.json",{"verdict":"pass","checks":[{"id":"fixture","status":"pass","reason":"Synthetic test only"}],"blocking_issues":[]})
        self.rt.save("fixture-prelaunch-witness.json",fake_witness("fake-prelaunch"))
        self.rt.save("receipts/preparation-ledger.freeze.json",{"fixture":"synthetic-test-only"})
        return self.rt.freeze(self.root/"capacity/output.json",self.root/"fixture-capacity-witness.json",
                              self.root/"fixture-prelaunch.json",self.root/"fixture-prelaunch-witness.json")
    def start(self,jid):
        self.rt.prompt(jid)
        self.rt.started(jid,"fake-"+jid)
    def join(self,jid,value):
        self.rt.save("outputs/"+jid+".json",value)
        return self.rt.joined(jid,"fake-"+jid,fake_witness("fake-"+jid))
    def concern(self,jid):
        job = self.rt.job(jid)
        return {"job_id":jid,"case_id":job["case_id"],"role":job["role"],"dependency":"Preferred dependency",
                "surviving_outcome":"Synthetic retained outcome",
                "predictions":[{"account":"a","when":"remove dependency","result":"loss"},
                               {"account":"b","when":"remove dependency","result":"survival"}],
                "source_refs":["O1","R1"],"unknowns":["Hypothesis untested"]}
    def stage(self,jid):
        job = self.rt.job(jid)
        result = {"job_id":jid,"case_id":job["case_id"],
                  "residue":[{"id":jid+"-residue","text":"Source-bound unresolved hypothesis","source_refs":["O1"]}]}
        if job["role"] == "stage1":
            result.update({"policy":job["condition"],"core":[{"id":jid+"-core","text":"Core hypothesis","source_refs":["O1"]}],
                           "tension":{"account_a":"a","account_b":"b","prediction_a":"loss","prediction_b":"survival"}})
        else:
            result["summary"] = [{"id":jid+"-summary","text":"Summary hypothesis","source_refs":["O1"]}]
        return result
    def builder(self,jid,cards=False):
        job = self.rt.job(jid)
        output = {"job_id":jid,"case_id":job["case_id"],"cards":[],"no_opening_reason":"Synthetic source-bound no opening"}
        if cards:
            previous = job["case_id"]+"-"+job["condition"]+"-stage2"
            branch = self.rt.join_body(previous)[job["supplement_branch"]]
            output["cards"] = [{"id":jid+"-card","anchor":"Protected outcome","mutation":"Alternate dependency",
                              "construction":"Use R1","rival":"Original dependency drives result","probe":"Compare M1",
                              "prediction_candidate":"difference","prediction_rival":"no difference","defeat":"No difference",
                              "resources":["R1"],"source_refs":["O1"],"residue_refs":[branch[0]["id"]],
                              "burden":"One hypothetical comparison","unknowns":["Unmeasured mechanism"]}]
            output["no_opening_reason"] = None
        return output
    def advance(self,malformed_first=False,cards=False):
        self.freeze()
        malformed_done = False
        turns = 0
        while not all(self.rt.status(j["job_id"])["terminal"] for j in self.rt.plan()["jobs"]):
            jobs = self.rt.ready()["ready"]
            self.assertLessEqual(len(jobs),3)
            self.assertTrue(jobs,"synthetic scheduler deadlock")
            for selected in jobs:
                jid = selected["job_id"]
                job = self.rt.job(jid)
                self.start(jid)
                if job["role"] in ("INV","ATT"):
                    answer = self.concern(jid)
                    if malformed_first and not malformed_done:
                        answer["source_refs"] = ["INVENTED"]
                        malformed_done = True
                elif job["role"] in ("stage1","stage2"):
                    answer = self.stage(jid)
                elif job["role"] == "builder":
                    answer = self.builder(jid,cards)
                else:
                    answer = review_answer(self.rt.review_packet(job)[0])
                self.join(jid,answer)
            turns += 1
            self.assertLess(turns,200)
        return self.rt.report()
    def test_exact_schema_and_factor_accounting(self):
        data = synthetic_cases()
        self.assertTrue(tr.validate_cases(data))
        plan = self.rt.plan()
        self.assertEqual(len(plan["jobs"]),184)
        for cid in tr.CASES:
            self.assertEqual(sum(j["case_id"] == cid for j in plan["jobs"]),46)
        self.assertEqual(len(tr.CONDITIONS),14)
        data["cases"][0]["resources"][0]["available"] = 1
        with self.assertRaises(tr.GuardError):
            tr.validate_cases(data)
    def test_no_archive_in_case_packet(self):
        self.assertNotIn("ordinary_archive",self.rt.case("PD"))
        self.assertEqual(len(self.rt.load("prepared/archives/PD.json")),4)
    def test_freeze_required(self):
        with self.assertRaises(FileNotFoundError):
            self.rt.ready()
    def test_exclusive_firstsave(self):
        self.rt.save("exclusive.json",{"first":True})
        before = tr.sha(self.root/"exclusive.json")
        with self.assertRaises(FileExistsError):
            self.rt.save("exclusive.json",{"second":True})
        self.assertEqual(tr.sha(self.root/"exclusive.json"),before)
    def test_capacity_full_geometry_and_incomplete_pair_guard(self):
        self.rt.capacity()
        packet = self.rt.load("capacity/fixture.json")
        answer = review_answer(packet)
        self.assertEqual(sum(len(answer[k]) for k in ("units","cards","archive_pairs","candidate_pairs")),532)
        self.assertEqual(len(answer["candidate_pairs"]),378)
        self.assertTrue(tr.validate_review(answer,packet))
        answer["candidate_pairs"].pop()
        with self.assertRaisesRegex(tr.GuardError,"incomplete candidate pairs"):
            tr.validate_review(answer,packet)
    def test_duplicate_pairs_rejected(self):
        self.rt.capacity()
        packet = self.rt.load("capacity/fixture.json")
        answer = review_answer(packet)
        answer["archive_pairs"][-1] = answer["archive_pairs"][0]
        with self.assertRaisesRegex(tr.GuardError,"duplicate"):
            tr.validate_review(answer,packet)
    def test_source_drift_rejected(self):
        self.freeze()
        (self.root/"tools/ten_runtime.py").write_text("source drift",encoding="utf-8")
        with self.assertRaisesRegex(tr.GuardError,"source drift"):
            self.rt.ready()
        with self.assertRaisesRegex(tr.GuardError,"source drift"):
            self.rt.prompt("PD-INV")
    def test_external_dispatch_source_binding_drift_rejected(self):
        self.freeze()
        (self.root/"fixture-dispatch-source.txt").write_text("External source drift",encoding="utf-8")
        with self.assertRaisesRegex(tr.GuardError,"source drift"):
            self.rt.ready()
    def test_duplicate_start_and_reused_native_handle(self):
        self.freeze()
        self.start("PD-INV")
        with self.assertRaisesRegex(tr.GuardError,"duplicate start"):
            self.rt.started("PD-INV","other")
        self.rt.prompt("PD-ATT")
        with self.assertRaisesRegex(tr.GuardError,"handle reused"):
            self.rt.started("PD-ATT","fake-PD-INV")
    def test_fast_worker_save_allowed_after_admission(self):
        self.freeze()
        self.rt.prompt("PD-INV")
        self.rt.save("outputs/PD-INV.json",self.concern("PD-INV"))
        started = self.rt.started("PD-INV","fast-fixture-handle")
        self.assertEqual(started["early_output_sha256"],tr.sha(self.rt.output("PD-INV")))
        joined = self.rt.joined("PD-INV","fast-fixture-handle",fake_witness("fast-fixture-handle"))
        self.assertTrue(joined["valid"])
    def test_stale_output_before_admission_rejected(self):
        self.freeze()
        self.rt.save("outputs/PD-INV.json",self.concern("PD-INV"))
        with self.assertRaisesRegex(tr.GuardError,"stale output"):
            self.rt.prompt("PD-INV")
    def test_missing_final_and_prompt_drift_rejected(self):
        self.freeze()
        self.start("PD-INV")
        self.rt.save("outputs/PD-INV.json",self.concern("PD-INV"))
        receipt = fake_witness("fake-PD-INV")
        receipt["observation"] = "RUNNING"
        with self.assertRaisesRegex(tr.GuardError,"actual FINAL"):
            self.rt.joined("PD-INV","fake-PD-INV",receipt)
        self.assertFalse(self.rt.status("PD-INV")["terminal"])
        (self.root/"prompts/actual/PD-INV.txt").write_text("drift",encoding="utf-8")
        with self.assertRaisesRegex(tr.GuardError,"prompt drift"):
            self.rt.joined("PD-INV","fake-PD-INV",fake_witness("fake-PD-INV"))
    def test_malformed_refs_terminal_invalid_gates_dependents(self):
        self.freeze()
        self.start("PD-INV")
        answer = self.concern("PD-INV")
        answer["source_refs"] = ["O999"]
        receipt = self.join("PD-INV",answer)
        self.assertFalse(receipt["valid"])
        self.rt.ready()
        self.assertEqual(self.rt.status("PD-A-stage1")["disposition"],"gated")
        self.assertEqual(self.rt.status("PD-A-builder")["disposition"],"gated")
        self.assertFalse(self.rt.status("PC-INV")["terminal"])
    def test_confirmation_phase_barrier(self):
        self.freeze()
        with self.assertRaisesRegex(tr.GuardError,"confirmation phase barrier"):
            self.rt.prompt("PC-INV")
    def test_assigned_supplement_only(self):
        self.freeze()
        for jid in ("PD-INV","PD-ATT"):
            self.start(jid)
            self.join(jid,self.concern(jid))
        for condition in ("A","C"):
            for role in ("stage1","stage2"):
                jid = "PD-"+condition+"-"+role
                self.start(jid)
                self.join(jid,self.stage(jid))
            body,bindings = self.rt.projection(self.rt.job("PD-"+condition+"-builder"))
            expected = "summary" if condition == "A" else "residue"
            self.assertEqual(body["supplement"][0]["id"],"PD-"+condition+"-stage2-"+expected)
            self.assertNotIn("stage1",body)
            self.assertEqual(set(body),{"case","INV","ATT","supplement"})
    def test_blinding_keeps_substantive_body(self):
        original = {"id":"PD-S01-builder-card","job_id":"PD-S01-builder","case_id":"PD",
                    "anchor":"Keep actual dependency description","residue_refs":["PD-S01-stage2-item"]}
        view = tr.blind_card(original,"PD-U01-C01")
        self.assertNotIn("id",view)
        self.assertNotIn("job_id",view)
        self.assertNotIn("case_id",view)
        self.assertEqual(view["anchor"],original["anchor"])
        self.assertEqual(view["residue_refs"],["PD-U01-C01-SUP1"])
        self.assertEqual(original["id"],"PD-S01-builder-card")
    def test_clique_bounds_unknown_does_not_merge(self):
        vertices = ["a","b","c"]
        self.assertEqual(tr.max_clique(vertices,set()),1)
        possible = set(itertools.combinations(vertices,2))
        self.assertEqual(tr.max_clique(vertices,possible),3)
        possible.remove(("a","b"))
        self.assertEqual(tr.max_clique(vertices,possible),2)
        self.assertEqual(tr.max_clique([],set()),0)
    def test_clique_matches_bruteforce(self):
        rng = random.Random(17)
        for size in range(1,9):
            vertices = [str(i) for i in range(size)]
            for _ in range(12):
                edges = {p for p in itertools.combinations(vertices,2) if rng.random() < .5}
                exact = max(len(subset) for n in range(size+1) for subset in itertools.combinations(vertices,n)
                            if all(tuple(sorted(pair)) in edges for pair in itertools.combinations(subset,2)))
                self.assertEqual(tr.max_clique(vertices,edges),exact)
    def test_factorial_interval_arithmetic(self):
        intervals = {"A":[1,2],"B":[3,4],"C":[2,3],"D":[4,5]}
        result = tr.factorial(intervals)
        self.assertEqual(result["B_minus_A_delayed"],[1,3])
        self.assertEqual(result["C_minus_A_residue"],[0,2])
        self.assertEqual(result["interaction_D_minus_B_minus_C_plus_A"],[-2,2])
    def test_upstream_factor_policy_does_not_disclose_routing(self):
        for left,right in (("A","C"),("B","D")):
            self.assertEqual(tr.POLICIES[left],tr.POLICIES[right])
            for role in ("stage1","stage2"):
                self.assertEqual(tr.base_prompt({"role":role,"condition":left}),tr.base_prompt({"role":role,"condition":right}))
    def test_full184_valid_zeroopenings_and_firstsaved_report(self):
        self.advance()
        report = self.rt.load("reports/report.json")
        self.assertEqual(report["started_native_calls"],184)
        self.assertEqual(report["skipped_gated_calls"],0)
        self.assertFalse(report["hard_protocol_failure"])
        for case in report["case_reports"].values():
            self.assertFalse(case["protocol_missing"])
            for count in case["conditions"].values():
                self.assertEqual(count["raw"],0)
                self.assertEqual(count["families"],[0,0])
        with self.assertRaises(FileExistsError):
            self.rt.report()
    def test_failure_closes184_and_confirmation_runs(self):
        self.advance(malformed_first=True)
        report = self.rt.load("reports/report.json")
        self.assertEqual(report["started_native_calls"]+report["skipped_gated_calls"],184)
        self.assertEqual(report["started_native_calls"],142)
        self.assertEqual(report["skipped_gated_calls"],42)
        self.assertTrue(report["hard_protocol_failure"])
        self.assertFalse(report["numeric_superiority_claims_allowed"])
        self.assertTrue(self.rt.status("PC-INV")["valid"])
        self.assertTrue(self.rt.status("WC-review2")["valid"])
        self.assertTrue(all(v is None for v in report["factorial_contrast_intervals"].values()))
        missing=report["case_reports"]["PD"]
        self.assertTrue(missing["protocol_missing"])
        self.assertIsNone(missing["intervals"])
        self.assertIsNone(missing["families"])
        self.assertIsNone(missing["compared_controls"])
        for count in missing["conditions"].values():
            self.assertEqual(count["raw"],0)
            self.assertIsNone(count["qualified"])
            self.assertIsNone(count["uncertainty_eligible"])
            self.assertIsNone(count["families"])
        reviews = [j for j in self.rt.plan()["jobs"] if j["role"] == "review"]
        self.assertEqual(sum(self.rt.status(j["job_id"])["receipt"]["review_lock"] for j in reviews),8)
    def test_pair_scoring_all_unknown_preserves_upper(self):
        self.advance(cards=True)
        report = self.rt.load("reports/report.json")
        for case in report["case_reports"].values():
            self.assertEqual(case["families"],[1,14])
            for condition in tr.CONDITIONS:
                self.assertEqual(case["conditions"][condition]["families"],[1,1])
    def test_review_failure_wrapper_includes_declared_invalid_card(self):
        self.freeze()
        # Synthetic terminal fixtures, not production joins or native evidence.
        for condition in tr.CONDITIONS:
            jid = "PD-"+condition+"-builder"
            if condition == "A":
                self.rt.save("outputs/"+jid+".json",{"cards":[{"id":jid+"-one","anchor":"malformed"}]})
                self.rt.save("events/joined--"+jid+".json",{"valid":False,"output_sha256":tr.sha(self.rt.output(jid)),"reason":"synthetic malformed card"})
            else:
                self.rt.save("events/gated--"+jid+".json",{"valid":False,"reason":"synthetic gated source"})
        packet,bindings = self.rt.review_packet(self.rt.job("PD-review1"))
        self.assertEqual(len(packet["units"]),14)
        self.assertEqual(len(packet["cards"]),1)
        self.assertFalse(packet["cards"][0]["structurally_valid_unit"])
        self.assertIn("raw_sha256",next(iter(bindings.values())))
        answer = review_answer(packet)
        self.assertEqual(len(answer["archive_pairs"]),4)
        self.assertTrue(tr.validate_review(answer,packet))
    def test_missing_review_invalidates_inferential_contrasts(self):
        self.freeze()
        for job in self.rt.plan()["jobs"]:
            jid = job["job_id"]
            if job["role"] != "review":
                self.rt.save("events/gated--"+jid+".json",{"valid":False,"reason":"synthetic missing predecessor"})
        job = self.rt.job("PD-review1")
        self.start(job["job_id"])
        joined = self.rt.joined(job["job_id"],"fake-"+job["job_id"],fake_witness("fake-"+job["job_id"]))
        self.assertFalse(joined["valid"])
        self.assertTrue(joined["review_lock"])
        self.assertFalse(self.rt.output(job["job_id"]).exists())

if __name__ == "__main__":
    unittest.main(verbosity=2)

