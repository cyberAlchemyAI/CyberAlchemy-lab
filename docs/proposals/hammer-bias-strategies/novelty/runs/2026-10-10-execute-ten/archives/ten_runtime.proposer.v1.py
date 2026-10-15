#!/usr/bin/env python3
"""Case-bound native preparation, guard, join, and report. No model calls."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import secrets
import sys
from datetime import datetime, timezone

CASES = ("PD", "WD", "PC", "WC")
CONDITIONS = ("A", "B", "C", "D", "O", "G", "S01", "S02", "S03", "S04", "S07", "S08", "S09", "S10")
FINAL_WITNESS_KEYS = {"handle", "observation", "native_tool", "final_text", "observer"}
PROFILE = {
    "QUALITY_BAR_STATUS": "bounded_native_contract",
    "ANTI_PATTERN_HITS_JSON": [],
    "WORKFLOW_GAPS_JSON": ["native observation truth rests on independent parent receipts",
                          "model judgments are synthetic and case-bound"],
    "PROFILE_ID": "ten-native-deep-preparation.v1",
    "LIFECYCLE_OWNER": "parent-native-orchestrator",
    "ARTIFACT_TYPE": "native-runner-contract",
    "CONTRACT_PATH": "CONTRACT.md",
    "PROMPT_SET": "ten-literal-prompts.v1",
    "REGIME_SET": ["development", "confirmation"],
    "PROFILE_VALIDATION": "schema-and-guard-tests; independent prelaunch required",
}
POLICIES = {
    "A": "Immediate convergence: commit early to the best main account and operating construction.",
    "B": "Delayed convergence: retain two incompatible accounts and their separating observations before committing. This is the S05 process contrast against A.",
    "C": "Immediate convergence as A. Builder receives only the stage2 residue branch. This is the S06 supplement contrast against A.",
    "D": "Delay as B; builder receives only stage2 residue. This combines S05 and S06, preserving interaction uncertainty.",
    "O": "Ordinary control: analyze the case by routine feasibility, fit and useful next action. Preserve honest uncertainties.",
    "G": "Generic creativity control: generate alternative approaches and refine their feasibility without a prescribed inversion technique.",
    "S01": "Tool deprivation: remove the actual preferred operating dependency; preserve the valued outcome and seek an operating construction without that dependency.",
    "S02": "Causal return-path inversion: intervene on the causal return link while holding initial demand fixed. Describe predictions that separate rival causal accounts. Do not turn this into an intervention-dose boundary test.",
    "S03": "Attack to fresh builder: attack the preferred dependency and preserve the surviving valued outcome. Transfer the attacked dependency, failed account and surviving outcome explicitly in main core items for the fresh builder.",
    "S04": "Carrier migration: move the function to a new carrier, then attack that new carrier. Preserve distinct migration and second-attack predictions.",
    "S07": "Protected anomaly: protect the case anomaly and retain incompatible accounts with predictions separating them instead of smoothing the anomaly away.",
    "S08": "Rival backcasting: specify successful futures for rival accounts and backcast each to the first causal divergence; preserve the separating first-divergence probe.",
    "S09": "Interface ablation: preserve both parent operations and ablate only their interface. Specify whether the interface carries the result without inventing a parent deletion.",
    "S10": "Objective boundary inversion: increase the present intervention dose to an adverse boundary and specify a detector. Keep this distinct from S02 return-link inversion with fixed demand.",
}
SCHEMAS = {
    "INV": {"job_id":"text","case_id":"text","role":"INV","dependency":"text","surviving_outcome":"text","predictions":[{"account":"text","when":"text","result":"text"}],"source_refs":["exact local case IDs"],"unknowns":["text"]},
    "ATT": {"job_id":"text","case_id":"text","role":"ATT","dependency":"text","surviving_outcome":"text","predictions":[{"account":"text","when":"text","result":"text"}],"source_refs":["exact local case IDs"],"unknowns":["text"]},
    "stage1": {"job_id":"text","case_id":"text","policy":"exact condition ID","core":[{"id":"unique text","text":"text","source_refs":["exact local case IDs"]}],"residue":[{"id":"unique text","text":"text","source_refs":["exact local case IDs"]}],"tension":{"account_a":"text","account_b":"text","prediction_a":"text","prediction_b":"text"}},
    "stage2": {"job_id":"text","case_id":"text","summary":[{"id":"unique text","text":"text","source_refs":["exact local case IDs"]}],"residue":[{"id":"unique text","text":"text","source_refs":["exact local case IDs"]}]},
    "builder": {"job_id":"text","case_id":"text","cards":[{"id":"unique text","anchor":"text","mutation":"text","construction":"text","rival":"text","probe":"text","prediction_candidate":"text","prediction_rival":"text","defeat":"text","resources":["R IDs"],"source_refs":["exact local case IDs"],"residue_refs":["exact received supplement item IDs"],"burden":"text","unknowns":["text"]}],"no_opening_reason":"nonempty text for zero cards, otherwise null"},
    "review": {"job_id":"text","case_id":"text","units":[{"unit_id":"opaque unit ID","status":"valid|invalid|gated","reason":"text"}],"cards":[{"card_id":"opaque card ID","unit_id":"opaque unit ID","anchor_fit":"boolean|null","resource_fit":"boolean|null","separating":"boolean|null","defeat_clear":"boolean|null","source_support":"boolean|null","reason":"text"}],"archive_pairs":[{"card_id":"opaque card ID","archive_id":"exact archive ID","relation":"equivalent|distinct|unknown","reason":"text"}],"candidate_pairs":[{"left":"opaque card ID","right":"opaque card ID","relation":"equivalent|distinct|unknown","reason":"text"}]},
}
RUBRIC = {
    "axes": ["anchor_fit", "resource_fit", "separating", "defeat_clear", "source_support"],
    "qualified": "both locked reviewers return true on all five axes and distinct against every archive",
    "uncertainty_eligible": "neither reviewer returns false on any axis or equivalent against any archive; structural validity and available indispensable resources remain required",
    "pair_distinct": "both reviewers distinct",
    "pair_equivalent": "either reviewer equivalent",
    "pair_unknown": "all other cases; no transitivity",
    "lower": "maximum clique of proven-distinct edges among qualified cards",
    "upper": "maximum clique of distinct-or-unknown edges among uncertainty-eligible cards",
    "max_rows": 532,
    "review_soft_word_cap": 25000,
}
class GuardError(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise GuardError(message)

def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()

def sha(path):
    return digest_bytes(Path(path).read_bytes())

def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()

def exclusive(path, value, binary=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if binary else encode(value)
    with path.open("xb") as target:
        target.write(data)
        target.flush()
        os.fsync(target.fileno())
    return {"path": str(path.resolve()), "sha256": digest_bytes(data)}

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def obj(value, keys, label):
    require(isinstance(value, dict) and set(value) == set(keys), label + ": exact object keys required")

def string(value, label, allow_empty=False):
    require(isinstance(value, str) and (allow_empty or bool(value.strip())), label + ": nonempty text required")

def array(value, label, low=0, high=None):
    require(isinstance(value, list) and len(value) >= low and (high is None or len(value) <= high), label + ": invalid array/count")

def strings(value, label, low=0):
    array(value, label, low)
    for item in value:
        string(item, label)

def unique(value, label):
    require(len(value) == len(set(value)), label + ": duplicate values")

def words(value):
    # Count every saved JSON token, including keys and IDs, conservatively.
    return len(json.dumps(value, ensure_ascii=False).split())

def validate_cases(data):
    obj(data, ("classification","cases","independence_note"), "input")
    require(data["classification"] == "synthetic_fresh_case_and_archive_preparation", "input classification")
    require(data["independence_note"] == "No prior candidates, strategy prompts or results were read", "input independence note")
    array(data["cases"], "cases", 4, 4)
    require({c.get("case_id") for c in data["cases"] if isinstance(c, dict)} == set(CASES), "exact four case IDs required")
    fields = ("case_id","phase","domain","valued_outcome","hard_constraints","observations","resources","preferred_dependency","causal_return_path_hypothesis","anomaly_id","parent_operations","available_observables","unknowns","ordinary_archive")
    tables = {"hard_constraints":("C",3,6),"observations":("O",5,8),"resources":("R",5,8),"parent_operations":("P",2,2),"available_observables":("M",3,5),"unknowns":("U",2,4),"ordinary_archive":("A",3,4)}
    for case in data["cases"]:
        obj(case, fields, "case")
        cid = case["case_id"]
        require(case["phase"] == ("development" if cid in ("PD","WD") else "confirmation"), "case phase")
        require(case["domain"] == ("physical" if cid in ("PD","PC") else "workflow"), "case domain")
        for field in ("valued_outcome","preferred_dependency","causal_return_path_hypothesis","anomaly_id"):
            string(case[field], field)
        seen = []
        for field, (prefix, low, high) in tables.items():
            array(case[field], field, low, high)
            table_ids = []
            for row in case[field]:
                keys = ("id","text","available") if field == "resources" else (("id","operation","relation","probe","limits") if field == "ordinary_archive" else ("id","text"))
                obj(row, keys, field)
                for key in keys:
                    if key == "available":
                        require(type(row[key]) is bool, "resource availability must be boolean")
                    else:
                        string(row[key], field + "." + key)
                ident = row["id"]
                require(ident.startswith(prefix) and ident[len(prefix):].isdigit() and int(ident[len(prefix):]) > 0, field + ": ID prefix/number")
                table_ids.append(ident)
                seen.append(ident)
            unique(table_ids, field + " IDs")
            require(set(table_ids) == {prefix + str(i) for i in range(1,len(table_ids)+1)}, field + ": contiguous IDs required")
        unique(seen, "case IDs")
        require(case["anomaly_id"] in {r["id"] for r in case["observations"]}, "anomaly must be an observed ID")
    return True

def packet(case):
    return {k:v for k,v in case.items() if k != "ordinary_archive"}

def case_refs(case):
    return {r["id"] for field in ("hard_constraints","observations","resources","parent_operations","available_observables","unknowns") for r in case[field]}

def make_plan():
    jobs = []
    for cid in CASES:
        for role in ("INV","ATT"):
            jobs.append({"job_id":cid+"-"+role,"case_id":cid,"role":role,"condition":None,"dependencies":[]})
        for condition in CONDITIONS:
            previous = None
            for role in ("stage1","stage2","builder"):
                jid = cid+"-"+condition+"-"+role
                deps = [cid+"-INV",cid+"-ATT"] + ([previous] if previous else [])
                jobs.append({"job_id":jid,"case_id":cid,"role":role,"condition":condition,"dependencies":deps,
                             "supplement_branch":"residue" if condition in ("C","D") else "summary"})
                previous = jid
        builders = [cid+"-"+c+"-builder" for c in CONDITIONS]
        for number in (1,2):
            jobs.append({"job_id":cid+"-review"+str(number),"case_id":cid,"role":"review","condition":None,"dependencies":builders})
    require(len(jobs) == 184 and len({j["job_id"] for j in jobs}) == 184, "factor accounting")
    return {"schema":"ten-plan.v1","planned_native_calls":184,"per_case":46,"conditions":list(CONDITIONS),"cases":list(CASES),"phase_barrier":"all PD/WD jobs and reviewer locks before PC/WC","jobs":jobs}

def base_prompt(job):
    role = job["role"]
    instructions = [
        "Fresh native call; fork_turns='none'. Read only this assigned literal prompt. No folder search, agents, web, prior results, siblings, state, permutation map, or future-phase data.",
        "Produce only one JSON object at OUTPUT_PATH. Use create-exclusive save (Python open(path, 'x')); build and validate your own object in memory first. Do not repair or overwrite after the first save. No retry.",
        "Treat supplied observations as synthetic stipulated facts. Every proposed mechanism, intervention, prediction or successful future is a hypothesis unless already explicitly observed. Preserve uncertainty.",
        "All source_refs must be exact local case IDs visible in this packet. Never invent source IDs. Literal typed schema (all listed keys required; no extra keys):",
        json.dumps(SCHEMAS[role], ensure_ascii=False, sort_keys=True),
    ]
    if role in ("INV","ATT"):
        instructions.append("Extract the preferred dependency and surviving valued outcome; specify at least two rival-account predictions. INV explicitly examines causal_return_path_hypothesis, tests the reversed causal arrow, and proposes intervention on the return link holding initial demand and valued outcome fixed. Distinguish necessity reasoning from observed causal evidence. ATT explicitly breaks the named operating dependency and records the surviving outcome; do not quietly reinstall that dependency. Shared concerns remain case-bound and proposed interventions are hypotheses.")
    elif role == "stage1":
        instructions.append("Condition policy: " + POLICIES[job["condition"]])
        instructions.append("Maximum 600 saved JSON words. Core and residue must both be nonempty and each item must cite at least one exact case source ID. Item IDs must be unique. Tension must name incompatible accounts and their separating predictions.")
    elif role == "stage2":
        instructions.append("Maximum 600 saved JSON words. Receive own stage1 plus shared concerns and own case. Preserve both nonempty summary and residue with unique item IDs and exact source IDs. " + ("Retain rival branches until final selection." if job["condition"] in ("B","D") else "Consolidate useful construction information and unresolved residue."))
        instructions.append("Both branches must draw from the supplied own stage1, concerns and case. Preserve source-bound omitted material in residue. Explicitly label any new inference or hypothesis; never portray fabricated residue as discarded source content.")
    elif role == "builder":
        instructions.append("Maximum 1200 saved JSON words; maximum two cards. Only your assigned supplement branch is supplied; never request or infer omitted branch bodies. Every card needs a valued-outcome anchor, operating construction, rival, separating probe, both predictions, clear defeat, burden, uncertainties, exact resources and source_refs. residue_refs means IDs actually received in your assigned supplement, including summary item IDs if that is the assigned branch. Indispensable unavailable resources fail feasibility. Zero cards is valid only with a nonempty no_opening_reason; with cards, no_opening_reason must be null.")
    else:
        instructions.append("You are a whole-case reviewer with administrative method labels withheld. Unit/card labels are opaque; never read permutation secrets. Substantive operational content may suggest a policy; full semantic blinding is not claimed. Cover exactly every unit, every declared raw candidate including malformed candidates in failure wrappers, every candidate/archive pair and every unordered candidate/candidate pair once. Missing/invalid output contains no invented candidate. Judge true/false/null on all five axes; null means uncertain, not false. Explicitly reject unavailable indispensable resources. Use equivalent/distinct/unknown independently per pair; do not force transitivity. Explain disagreement-relevant evidence. A no-opening valid unit is valid and has no card rows. Soft cap 25000 words; complete coverage takes priority.")
        instructions.append("Unit status must equal the supplied structural disposition (valid, invalid or gated). Card weaknesses belong on the five axes; a valid no-opening or weak card is never converted into missing protocol by an assessor.")
    return "\n".join(instructions) + "\n"

def witness(value, handle=None):
    require(isinstance(value, dict) and FINAL_WITNESS_KEYS <= set(value), "native witness fields missing")
    for key in FINAL_WITNESS_KEYS:
        string(value[key], "witness." + key)
    require(value["observation"] == "FINAL", "actual FINAL observation required")
    require(value["native_tool"] == "collaboration", "native collaboration witness required")
    if handle is not None:
        require(value["handle"] == handle, "native handle mismatch")
    # The parent's supplied receipt is evidence; a filesystem output alone never qualifies.
    return True

def refs(value, allowed, label):
    strings(value, label, 1)
    unique(value, label)
    require(set(value) <= allowed, label + ": malformed/unavailable source reference")

def raw_cards(value):
    if not isinstance(value, dict) or not isinstance(value.get("cards"), list):
        return []
    return value["cards"]

def blind_card(card, label):
    # Preserve semantic bodies and malformed declarations; remove routing identities.
    if not isinstance(card, dict):
        return card
    projected = dict(card)
    for key in ("id", "job_id", "case_id"):
        projected.pop(key, None)
    if isinstance(projected.get("residue_refs"), list):
        projected["residue_refs"] = [label+"-SUP"+str(i+1) for i in range(len(projected["residue_refs"]))]
    for key in ("job_id", "policy", "condition"):
        if key in projected:
            projected[key] = "<opaque routing identity>"
    return projected

def validate_output(job, value, case, supplement_ids=(), review_packet=None):
    role = job["role"]
    obj(value, SCHEMAS[role], "role output")
    require(value["job_id"] == job["job_id"] and value["case_id"] == job["case_id"], "job/case identity mismatch")
    allowed = case_refs(case)
    if role in ("INV","ATT"):
        require(value["role"] == role, "concern role mismatch")
        for key in ("dependency","surviving_outcome"):
            string(value[key], key)
        array(value["predictions"], "predictions", 2)
        for prediction in value["predictions"]:
            obj(prediction, ("account","when","result"), "prediction")
            for key in prediction:
                string(prediction[key], key)
        refs(value["source_refs"], allowed, "concern refs")
        strings(value["unknowns"], "concern unknowns")
    elif role in ("stage1","stage2"):
        branches = ("core","residue") if role == "stage1" else ("summary","residue")
        all_ids = []
        for branch in branches:
            array(value[branch], branch, 1)
            for item in value[branch]:
                obj(item, ("id","text","source_refs"), branch)
                string(item["id"], "item ID")
                string(item["text"], "item text")
                refs(item["source_refs"], allowed, "item source refs")
                all_ids.append(item["id"])
        unique(all_ids, "branch IDs")
        if role == "stage1":
            require(value["policy"] == job["condition"], "condition policy mismatch")
            obj(value["tension"], ("account_a","account_b","prediction_a","prediction_b"), "tension")
            for key in value["tension"]:
                string(value["tension"][key], key)
        require(words(value) <= 600, "stage saved-word cap exceeded")
    elif role == "builder":
        array(value["cards"], "cards", 0, 2)
        if not value["cards"]:
            string(value["no_opening_reason"], "zero-card no-opening reason")
        else:
            require(value["no_opening_reason"] is None, "nonempty builder requires null no-opening reason")
        ids = []
        for card in value["cards"]:
            obj(card, SCHEMAS["builder"]["cards"][0], "card")
            for key in ("id","anchor","mutation","construction","rival","probe","prediction_candidate","prediction_rival","defeat","burden"):
                string(card[key], key)
            ids.append(card["id"])
            strings(card["resources"], "resources", 1)
            unique(card["resources"], "resources")
            require(set(card["resources"]) <= {r["id"] for r in case["resources"]}, "malformed resource refs")
            refs(card["source_refs"], allowed, "card source refs")
            refs(card["residue_refs"], set(supplement_ids), "received supplement refs")
            strings(card["unknowns"], "card unknowns")
        unique(ids, "card IDs")
        require(words(value) <= 1200, "builder saved-word cap exceeded")
    else:
        require(review_packet is not None, "review packet required")
        validate_review(value, review_packet)
    return True

def validate_review(value, review):
    obj(value, SCHEMAS["review"], "review")
    require(value["job_id"] == review["job_id"] and value["case_id"] == review["case_id"], "review identity")
    expected_units = {u["unit_id"] for u in review["units"]}
    expected_cards = {c["card_id"]:c["unit_id"] for c in review["cards"]}
    array(value["units"], "unit rows")
    unit_ids = []
    for row in value["units"]:
        obj(row, ("unit_id","status","reason"), "unit row")
        require(row["status"] in ("valid","invalid","gated"), "unit status")
        require(row["status"] == next(u["status"] for u in review["units"] if u["unit_id"] == row["unit_id"]) if row["unit_id"] in expected_units else False, "unit structural disposition mismatch")
        string(row["reason"], "unit reason")
        unit_ids.append(row["unit_id"])
    unique(unit_ids, "unit rows")
    require(set(unit_ids) == expected_units, "incomplete unit rows")
    array(value["cards"], "card rows")
    card_ids = []
    for row in value["cards"]:
        obj(row, ("card_id","unit_id","anchor_fit","resource_fit","separating","defeat_clear","source_support","reason"), "card row")
        require(row["card_id"] in expected_cards and row["unit_id"] == expected_cards[row["card_id"]], "card/unit binding")
        for key in RUBRIC["axes"]:
            require(row[key] is None or type(row[key]) is bool, "typed card judgment")
        string(row["reason"], "card reason")
        card_ids.append(row["card_id"])
    unique(card_ids, "card rows")
    require(set(card_ids) == set(expected_cards), "incomplete card rows")
    archives = {a["id"] for a in review["archive"]}
    expected_archive = set(itertools.product(expected_cards, archives))
    actual_archive = []
    array(value["archive_pairs"], "archive pairs")
    for row in value["archive_pairs"]:
        obj(row, ("card_id","archive_id","relation","reason"), "archive pair")
        require(row["relation"] in ("equivalent","distinct","unknown"), "archive relation")
        string(row["reason"], "archive reason")
        actual_archive.append((row["card_id"],row["archive_id"]))
    unique(actual_archive, "archive pairs")
    require(set(actual_archive) == expected_archive, "incomplete archive pairs")
    expected_pairs = {tuple(sorted(pair)) for pair in itertools.combinations(expected_cards,2)}
    actual_pairs = []
    array(value["candidate_pairs"], "candidate pairs")
    for row in value["candidate_pairs"]:
        obj(row, ("left","right","relation","reason"), "candidate pair")
        require(row["relation"] in ("equivalent","distinct","unknown"), "candidate relation")
        string(row["reason"], "candidate reason")
        actual_pairs.append(tuple(sorted((row["left"],row["right"]))))
    unique(actual_pairs, "candidate pairs")
    require(set(actual_pairs) == expected_pairs, "incomplete candidate pairs")
    return True

class Runtime:
    def __init__(self, root):
        self.root = Path(root).resolve()
    def p(self, relative):
        return self.root / relative
    def load(self, relative):
        return read_json(self.p(relative))
    def save(self, relative, value, binary=False):
        return exclusive(self.p(relative), value, binary)
    def plan(self):
        return self.load("prepared/plan.json")
    def job(self, jid):
        jobs = {j["job_id"]:j for j in self.plan()["jobs"]}
        require(jid in jobs, "unknown job ID")
        return jobs[jid]
    def case(self, cid):
        return self.load("prepared/cases/" + cid + ".json")
    def source_snapshot(self):
        paths = [self.p("SCOPE.json"), self.p("PREPARATION-BUDGET.json"), self.p("prompts/PREP-proposer.v1.txt"),
                 self.p("tools/ten_runtime.py"), self.p("tools/test_ten_runtime.py"), self.p("CONTRACT.md"), self.p("PROPOSER-TRACE.json"),
                 self.p("inputs/fresh-cases-and-archives.v1.json")]
        paths += [self.p("SCORING-EXAMPLES.md"), self.p("PREPARATION-BUDGET-AMENDMENT.v1.json"),
                  self.p("runtime.dispatch.json"), self.p("dispatch-validation.v2.json"),
                  self.p("receipts/preparation-arithmetic-correction.v1.json"),
                  self.p("receipts/dispatch-source-bindings.v1.json")]
        for path in paths:
            require(path.is_file(), "required protocol source missing: " + str(path))
        if self.p("receipts/preparation-ledger.freeze.json").exists():
            paths.append(self.p("receipts/preparation-ledger.freeze.json"))
        paths += sorted(self.p("prompts").glob("*.txt"))
        paths += sorted(self.p("prepared").rglob("*"))
        paths += sorted(self.p("capacity").rglob("*"))
        paths = [p for p in paths if p.is_file() and p.suffix != ".pyc" and "__pycache__" not in str(p)]
        scope = self.load("SCOPE.json")
        paths += [Path(item["path"]) for item in scope.get("source_bindings",[])]
        for item in scope.get("source_bindings",[]):
            require(sha(item["path"]) == item["sha256"], "declared source binding drift: " + item["path"])
        for item in self.load("receipts/dispatch-source-bindings.v1.json")["bindings"]:
            require(sha(item["path"]) == item["sha256"], "dispatch source binding drift: " + item["path"])
            paths.append(Path(item["path"]))
        return {str(p.resolve()):sha(p) for p in sorted(set(paths))}
    def integrity(self, frozen=True):
        bindings = self.load("prepared/bindings.json")["sources"]
        if frozen:
            bindings = self.load("events/freeze.json")["sources"]
        for path, expected in bindings.items():
            require(Path(path).is_file() and sha(path) == expected, "source drift: " + path)
        return True
    def prepare(self):
        require(not self.p("prepared/plan.json").exists(), "prepare already first-saved")
        data = self.load("inputs/fresh-cases-and-archives.v1.json")
        validate_cases(data)
        scope = self.load("SCOPE.json")
        require(scope["scope_extension_before_any_scored_call"]["total_scored_native_calls"] == 184, "scope call count")
        require(self.load("PREPARATION-BUDGET.json")["scored_calls"] == 184, "budget call count")
        plan = make_plan()
        self.save("prepared/plan.json",plan)
        self.save("prepared/rubric.json", RUBRIC)
        self.save("prepared/profile.json", PROFILE)
        for case in data["cases"]:
            cid = case["case_id"]
            self.save("prepared/cases/"+cid+".json",packet(case))
            self.save("prepared/archives/"+cid+".json",case["ordinary_archive"])
        permutations = {}
        for cid in CASES:
            shuffled = list(CONDITIONS)
            secrets.SystemRandom().shuffle(shuffled)
            permutations[cid] = {condition:cid+"-U"+str(index+1).zfill(2) for index,condition in enumerate(shuffled)}
        self.save("prepared/private-unit-map.json",permutations)
        for job in plan["jobs"]:
            text = base_prompt(job)
            if job["role"] == "review":
                text += "PROSPECTIVE SEMANTIC SCORING EXAMPLES:\n" + self.p("SCORING-EXAMPLES.md").read_text(encoding="utf-8") + "\n"
            self.save("prepared/base-prompts/"+job["job_id"]+".txt",text.encode(),True)
        bindings = self.source_snapshot()
        self.save("prepared/bindings.json",{"sources":bindings})
        self.save("events/prepared.json",{"event":"prepared","native_calls":184,"profile":PROFILE})
        return {"planned_native_calls":184,"jobs":184,"bindings":sha(self.p("prepared/bindings.json")),"profile":PROFILE}
    def status(self, jid):
        for disposition in ("joined","gated"):
            path = self.p("events/"+disposition+"--"+jid+".json")
            if path.exists():
                value = read_json(path)
                return {"terminal":True,"valid":value.get("valid",False),"disposition":disposition,"receipt":value}
        started = self.p("events/started--"+jid+".json")
        return {"terminal":False,"valid":False,"disposition":"started" if started.exists() else "pending"}
    def output(self, jid):
        return self.p("outputs/"+jid+".json")
    def join_body(self, jid):
        status = self.status(jid)
        require(status["terminal"] and status["valid"], "dependency not valid: "+jid)
        require(sha(self.output(jid)) == status["receipt"]["output_sha256"], "dependency output drift: "+jid)
        return read_json(self.output(jid))
    def allowed_phase(self, job):
        if job["case_id"] in ("PD","WD"):
            return True
        development = [j for j in self.plan()["jobs"] if j["case_id"] in ("PD","WD")]
        return all(self.status(j["job_id"])["terminal"] for j in development)
    def ready(self):
        self.integrity()
        # Closure propagation is bounded by the 184 acyclic jobs, without extra model calls.
        for _ in range(184):
            changed = False
            for job in self.plan()["jobs"]:
                if job["role"] == "review" or self.status(job["job_id"])["disposition"] != "pending" or not self.allowed_phase(job):
                    continue
                dependencies = [self.status(d) for d in job["dependencies"]]
                if any(s["terminal"] and not s["valid"] for s in dependencies):
                    failures = [d for d,s in zip(job["dependencies"],dependencies) if s["terminal"] and not s["valid"]]
                    self.save("events/gated--"+job["job_id"]+".json",{"event":"gated","job_id":job["job_id"],"valid":False,"failed_sources":failures,"reason":"invalid or missing indispensable predecessor","observed_at":datetime.now(timezone.utc).isoformat()})
                    changed = True
            if not changed:
                break
        ready = []
        for job in self.plan()["jobs"]:
            if self.status(job["job_id"])["disposition"] != "pending" or not self.allowed_phase(job):
                continue
            states = [self.status(dep) for dep in job["dependencies"]]
            eligible = all(s["terminal"] for s in states) if job["role"] == "review" else all(s["terminal"] and s["valid"] for s in states)
            if eligible:
                ready.append({"job_id":job["job_id"],"role":job["role"],"case_id":job["case_id"],"fork_turns":"none"})
            if len(ready) == 3:
                break
        return {"ready":ready}
    def review_packet(self, job):
        cid = job["case_id"]
        mapping = self.load("prepared/private-unit-map.json")[cid]
        units, cards, bindings = [], [], {}
        for condition in CONDITIONS:
            jid = cid+"-"+condition+"-builder"
            status = self.status(jid)
            require(status["terminal"], "case review requires every builder terminal")
            unit = {"unit_id":mapping[condition],"status":"gated" if status["disposition"] == "gated" else ("valid" if status["valid"] else "invalid"),
                    "reason":status["receipt"].get("reason","validated native first save")}
            units.append(unit)
            value = None
            if self.output(jid).exists():
                receipt = status["receipt"]
                require(receipt.get("output_sha256") == sha(self.output(jid)), "review source output drift")
                try:
                    value = read_json(self.output(jid))
                except (json.JSONDecodeError,UnicodeDecodeError):
                    pass
            for index, card in enumerate(raw_cards(value)):
                # Even non-object raw declarations receive a failure wrapper and a distinct row.
                label = mapping[condition]+"-C"+str(index+1).zfill(2)
                cards.append({"card_id":label,"unit_id":mapping[condition],"declared_card":blind_card(card,label),
                              "structurally_valid_unit":status["valid"],
                              "failure_reason":None if status["valid"] else status["receipt"].get("reason","invalid builder")})
                bindings[label] = {"job_id":jid,"condition":condition,"index":index,"raw_sha256":digest_bytes(encode(card))}
        units.sort(key=lambda u:u["unit_id"])
        cards.sort(key=lambda c:c["card_id"])
        review = {"job_id":job["job_id"],"case_id":cid,"case":self.case(cid),"units":units,"cards":cards,
                  "archive":self.load("prepared/archives/"+cid+".json"),"rubric":RUBRIC}
        return review, bindings
    def projection(self, job):
        case = self.case(job["case_id"])
        bodies = {"case":case}
        bindings = [{"path":str(self.p("prepared/cases/"+job["case_id"]+".json")),"sha256":sha(self.p("prepared/cases/"+job["case_id"]+".json")),"projection":"whole case packet excluding archive"}]
        if job["role"] == "review":
            review, private = self.review_packet(job)
            bodies = review
            for dep in job["dependencies"]:
                status = self.status(dep)
                bindings.append({"job_id":dep,"sha256":status["receipt"].get("output_sha256"),"projection":"opaque declared candidates or terminal failure packet"})
            bindings.append({"path":str(self.p("prepared/archives/"+job["case_id"]+".json")),"sha256":sha(self.p("prepared/archives/"+job["case_id"]+".json")),"projection":"whole ordinary archive"})
            return bodies,bindings
        for dep in job["dependencies"]:
            body = self.join_body(dep)
            if dep.endswith("-INV") or dep.endswith("-ATT"):
                bodies[dep.rsplit("-",1)[1]] = body
                projection = "whole concern"
            elif job["role"] == "builder":
                branch = job["supplement_branch"]
                bodies["supplement"] = body[branch]
                projection = branch + " items only"
            else:
                bodies["stage1"] = body
                projection = "whole own stage1"
            bindings.append({"job_id":dep,"sha256":sha(self.output(dep)),"projection":projection})
        return bodies,bindings
    def prompt(self, jid):
        self.integrity()
        job = self.job(jid)
        require(self.status(jid)["disposition"] == "pending", "job is already started or terminal")
        require(not self.output(jid).exists(), "stale output exists before prompt admission")
        require(self.allowed_phase(job), "confirmation phase barrier")
        states = [self.status(dep) for dep in job["dependencies"]]
        require(all(s["terminal"] for s in states) if job["role"] == "review" else all(s["terminal"] and s["valid"] for s in states), "predecessor gates")
        bodies, bindings = self.projection(job)
        base = self.p("prepared/base-prompts/"+jid+".txt").read_bytes()
        literal = base + ("JOB_ID="+jid+"\nCASE_ID="+job["case_id"]+"\nOUTPUT_PATH="+str(self.output(jid))+"\nDECLARED_INPUTS_JSON:\n").encode() + encode(bodies)
        result = self.save("prompts/actual/"+jid+".txt",literal,True)
        descriptor = {"job_id":jid,"path":result["path"],"sha256":result["sha256"],"base_sha256":digest_bytes(base),
                      "output":str(self.output(jid)),"dependencies":bindings,"input_saved_words":words(bodies),
                      "supplement_saved_words":words(bodies.get("supplement",[])) if job["role"] == "builder" else None,
                      "fork_turns":"none","admitted_at":datetime.now(timezone.utc).isoformat(),"output_absent_at_admission":True}
        self.save("prompts/actual/"+jid+".binding.json",descriptor)
        return descriptor
    def started(self, jid, handle):
        self.integrity()
        job = self.job(jid)
        string(handle,"native handle")
        require(self.status(jid)["disposition"] == "pending", "duplicate start or terminal job")
        require(self.allowed_phase(job),"confirmation phase barrier")
        descriptor = self.load("prompts/actual/"+jid+".binding.json")
        require(sha(descriptor["path"]) == descriptor["sha256"], "actual prompt drift")
        require(descriptor["output_absent_at_admission"] is True, "output absence admission guard missing")
        early_output = sha(self.output(jid)) if self.output(jid).exists() else None
        bodies, bindings = self.projection(job)
        require(bindings == descriptor["dependencies"], "pre-spawn dependency drift")
        actual = self.p("prepared/base-prompts/"+jid+".txt").read_bytes() + ("JOB_ID="+jid+"\nCASE_ID="+job["case_id"]+"\nOUTPUT_PATH="+str(self.output(jid))+"\nDECLARED_INPUTS_JSON:\n").encode() + encode(bodies)
        require(digest_bytes(actual) == descriptor["sha256"], "actual input projection drift")
        for existing in self.p("events").glob("started--*.json"):
            require(read_json(existing)["handle"] != handle, "fresh native handle reused")
        event = {"event":"started","job_id":jid,"handle":handle,"fork_turns":"none","actual_prompt_sha256":descriptor["sha256"],
                 "input_bindings":bindings,"input_saved_words":descriptor["input_saved_words"],"supplement_saved_words":descriptor["supplement_saved_words"],"native_turn":1,"observed_at":datetime.now(timezone.utc).isoformat(),"early_output_sha256":early_output,"admitted_at":descriptor["admitted_at"]}
        self.save("events/started--"+jid+".json",event)
        return event
    def validation(self, job, value):
        case = self.case(job["case_id"])
        received = []
        review = None
        if job["role"] == "builder":
            previous = job["case_id"]+"-"+job["condition"]+"-stage2"
            received = [item["id"] for item in self.join_body(previous)[job["supplement_branch"]]]
        if job["role"] == "review":
            review = self.review_packet(job)[0]
        return validate_output(job,value,case,received,review)
    def joined(self, jid, handle, receipt):
        self.integrity()
        job = self.job(jid)
        require(self.status(jid)["disposition"] == "started", "join requires exactly one prior native start")
        start = self.load("events/started--"+jid+".json")
        require(start["handle"] == handle, "started native handle mismatch")
        require(sha(self.p("prompts/actual/"+jid+".txt")) == start["actual_prompt_sha256"], "joined actual prompt drift")
        witness(receipt,handle)
        value, valid, reason, output_hash, saved_words = None, False, "missing first-saved output", None, None
        if self.output(jid).exists():
            output_hash = sha(self.output(jid))
            require(start.get("early_output_sha256") in (None,output_hash), "early first-save output drift")
            saved_words = len(self.output(jid).read_text(encoding="utf-8",errors="replace").split())
            try:
                value = read_json(self.output(jid))
                self.validation(job,value)
                valid, reason = True,"valid"
            except (GuardError,json.JSONDecodeError,UnicodeDecodeError,TypeError,KeyError) as error:
                reason = str(error)
        witnessed = self.save("receipts/"+jid+".witness.json",receipt)
        event = {"event":"joined","job_id":jid,"handle":handle,"observation":"FINAL","valid":valid,"reason":reason,
                 "output_sha256":output_hash,"saved_words":saved_words,"witness_sha256":witnessed["sha256"],
                 "final_text_sha256":digest_bytes(receipt["final_text"].encode()),
                 "review_lock":job["role"] == "review","observed_at":datetime.now(timezone.utc).isoformat()}
        self.save("events/joined--"+jid+".json",event)
        return event
    def capacity(self):
        self.integrity(frozen=False)
        require(not self.p("capacity/fixture.json").exists(),"capacity already first-saved")
        units, cards = [],[]
        for i in range(1,15):
            unit = "CAP-U"+str(i).zfill(2)
            units.append({"unit_id":unit,"status":"valid","reason":"unscored synthetic capacity fixture"})
            for number in (1,2):
                cards.append({"card_id":unit+"-C"+str(number),"unit_id":unit,
                              "declared_card":{"anchor":"Synthetic valued outcome",
                                               "mutation":"Bounded alternate construction "+str(i),
                                               "construction":"Use available R1 with alternate interface "+str(number),
                                               "rival":"The result is driven by unchanged parent operation",
                                               "probe":"Ablate only synthetic interface and compare",
                                               "prediction_candidate":"Interface effect remains distinguishable",
                                               "prediction_rival":"Parent explains result without interface effect",
                                               "defeat":"No separating difference at observable M1",
                                               "resources":["R1"],"source_refs":["O1","M1"],"residue_refs":[unit+"-C"+str(number)+"-SUP1"],
                                               "burden":"Small stipulated model-only probe","unknowns":["All effects hypothetical"]},
                              "structurally_valid_unit":True,"failure_reason":None})
        fixture = {"job_id":"CAPACITY","case_id":"CAP","case":{"valued_outcome":"Unscored coverage capacity","resources":[{"id":"R1","text":"synthetic model operation","available":True}],
                   "observations":[{"id":"O1","text":"Synthetic stipulated baseline"}],"available_observables":[{"id":"M1","text":"Synthetic difference"}]},
                   "units":units,"cards":cards,"archive":[{"id":"A"+str(i),"operation":"Synthetic archive operation "+str(i),"relation":"Unknown relation","probe":"Synthetic probe","limits":"Unscored hypothetical"} for i in range(1,5)],"rubric":RUBRIC}
        require(len(units)+len(cards)+len(cards)*4+math.comb(len(cards),2) == 532,"capacity fixture accounting")
        self.save("capacity/fixture.json",fixture)
        instruction = base_prompt({"role":"review","job_id":"CAPACITY","case_id":"CAP","condition":None})
        instruction += "PROSPECTIVE SEMANTIC SCORING EXAMPLES:\n" + self.p("SCORING-EXAMPLES.md").read_text(encoding="utf-8") + "\n"
        prompt = instruction + "This is unscored maximal review-row geometry only: exactly 14 unit, 28 card, 112 archive-pair, 378 candidate-pair rows (532 total). Its smaller synthetic descriptions do not test the maximal scored input context. Do not infer scored quality or largest-context readiness from this fixture.\nOUTPUT_PATH="+str(self.p("capacity/output.json"))+"\nDECLARED_INPUTS_JSON:\n"+encode(fixture).decode()
        result = self.save("capacity/prompt.txt",prompt.encode(),True)
        return {**result,"output":str(self.p("capacity/output.json")),"rows":532,"input_fixture_words":words(fixture),"capacity_scope":"maximum output-row geometry; maximal input context untested","scored":False,"fork_turns":"none"}
    def freeze(self, capacity_output, capacity_witness, prelaunch, prelaunch_witness):
        self.integrity(frozen=False)
        require(not self.p("events/freeze.json").exists(),"already frozen")
        require(not list(self.p("events").glob("started--*.json")),"cannot freeze after scored start")
        require(self.p("receipts/preparation-ledger.freeze.json").is_file(), "immutable actual preparation ledger required")
        cw, pw = read_json(capacity_witness),read_json(prelaunch_witness)
        witness(cw)
        witness(pw)
        require(cw["handle"] != pw["handle"],"capacity and prelaunch require independent native handles")
        require(cw["observer"] and pw["observer"],"independent observation")
        fixture = self.load("capacity/fixture.json")
        result = read_json(capacity_output)
        validate_review(result,fixture)
        verdict = read_json(prelaunch)
        obj(verdict,("verdict","checks","blocking_issues"),"prelaunch")
        require(verdict["verdict"] == "pass" and verdict["blocking_issues"] == [],"independent prelaunch must pass")
        array(verdict["checks"],"prelaunch checks",1)
        check_ids = []
        for check in verdict["checks"]:
            obj(check,("id","status","reason"),"prelaunch check")
            require(check["status"] == "pass","prelaunch failed check")
            string(check["id"],"prelaunch check ID")
            string(check["reason"],"prelaunch check reason")
            check_ids.append(check["id"])
        unique(check_ids,"prelaunch check IDs")
        evidence = {"capacity_output":self.save("receipts/capacity.output.json",result),
                    "capacity_witness":self.save("receipts/capacity.witness.json",cw),
                    "prelaunch_output":self.save("receipts/prelaunch.output.json",verdict),
                    "prelaunch_witness":self.save("receipts/prelaunch.witness.json",pw)}
        sources = self.source_snapshot()
        for item in evidence.values():
            sources[item["path"]] = item["sha256"]
        event = {"event":"freeze","sources":sources,"evidence":evidence,"capacity_rows":532,"profile":PROFILE,
                 "frozen_at":datetime.now(timezone.utc).isoformat(),"native_scored_calls":184,"capacity_scope":"maximum output-row geometry; maximal input context untested","capacity_input_fixture_words":words(fixture)}
        self.save("events/freeze.json",event)
        return {"frozen":True,"sha256":sha(self.p("events/freeze.json")),"capacity_rows":532,"native_scored_calls":184}
    def report(self):
        self.integrity()
        jobs = self.plan()["jobs"]
        statuses = {j["job_id"]:self.status(j["job_id"]) for j in jobs}
        require(all(s["terminal"] for s in statuses.values()),"all184 dispositions required")
        reviews = [j for j in jobs if j["role"] == "review"]
        require(len(reviews) == 8 and all(statuses[j["job_id"]]["receipt"].get("review_lock") for j in reviews),"all8 reviewer locks required")
        for jid, status in statuses.items():
            receipt = status["receipt"]
            if receipt.get("output_sha256") is not None:
                require(self.output(jid).exists() and sha(self.output(jid)) == receipt["output_sha256"],"joined output drift: "+jid)
            if status["disposition"] == "joined":
                require(sha(self.p("receipts/"+jid+".witness.json")) == receipt["witness_sha256"],"terminal witness drift: "+jid)
                start = self.load("events/started--"+jid+".json")
                require(sha(self.p("prompts/actual/"+jid+".txt")) == start["actual_prompt_sha256"],"spawned prompt drift: "+jid)
        hard_failure = any(not s["valid"] for s in statuses.values())
        case_reports = {cid:self.score_case(cid) for cid in CASES}
        contrasts = {}
        for cid, report in case_reports.items():
            intervals = report["intervals"]
            contrasts[cid] = factorial(intervals) if not hard_failure else None
            if hard_failure:
                report["compared_controls"] = None
        report = {
            "classification":"exploratory_case_bound_model_judgment","scope_ceiling":"Synthetic process/probe specifications only; no global originality, physical benefit, canonical skill efficacy or equal-compute claim",
            "profile":PROFILE,"protocol_complete":True,"hard_protocol_failure":hard_failure,
            "numeric_superiority_claims_allowed":not hard_failure,
            "planned_native_calls":184,"started_native_calls":sum(s["disposition"] == "joined" for s in statuses.values()),
            "completed_native_final_calls":sum(s["disposition"] == "joined" for s in statuses.values()),
            "skipped_gated_calls":sum(s["disposition"] == "gated" for s in statuses.values()),
            "valid_native_outputs":sum(s["valid"] for s in statuses.values()),
            "saved_output_words":sum(s["receipt"].get("saved_words") or 0 for s in statuses.values()),
            "input_words_by_job":{j["job_id"]:self.load("events/started--"+j["job_id"]+".json").get("input_saved_words") for j in jobs if statuses[j["job_id"]]["disposition"] == "joined"},
            "supplement_words_by_builder":{j["job_id"]:self.load("events/started--"+j["job_id"]+".json").get("supplement_saved_words") for j in jobs if j["role"] == "builder" and statuses[j["job_id"]]["disposition"] == "joined"},
            "unmatched_context":True,"context_accounting_note":"Only caps matched; exact supplied words are recorded. No padding and no equal-compute/context claim.",
            "tokens":None,"cost":None,"unavailable_accounting":"Native token/cost usage not supplied; unavailable does not mean zero",
            "case_reports":case_reports,"factorial_contrast_intervals":contrasts,
            "all_dispositions":{jid:s["receipt"] for jid,s in statuses.items()},
        }
        result = self.save("reports/report.json",report)
        lines = ["# Exploratory ten-strategy native report","",
                 "All 184 planned dispositions closed. Native started/completed: "+str(report["started_native_calls"])+". Gated/skipped: "+str(report["skipped_gated_calls"])+".",
                 "Hard protocol failure: "+str(hard_failure)+". Numeric superiority claims allowed: "+str(not hard_failure)+".",
                 "Interpretation: synthetic, case-bound model judgment. No global originality, physical benefit, whole canonical skill efficacy or equal-compute claim.",
                 "Token usage and monetary cost unavailable.","",
                 "| Case | Condition | Raw | Qualified | Uncertainty eligible | Distinct families lower/upper |",
                 "|---|---|---:|---:|---:|---|"]
        for cid, case in case_reports.items():
            for condition in CONDITIONS:
                row = case["conditions"][condition]
                lines.append("| "+cid+" | "+condition+" | "+str(row["raw"])+" | "+str(row["qualified"])+" | "+str(row["uncertainty_eligible"])+" | "+str(row["families"])+" |")
        lines += ["","Factorial contrasts use interval arithmetic; protocol-missing cases have null contrasts. Unknown pairs do not force merges. Genuine valid zero-opening outcomes count zero.","",
                  "JSON report contains every disposition, independent-review disagreement, per-condition intervals and comparisons against O/G."]
        md = self.save("reports/report.md",("\n".join(lines)+"\n").encode(),True)
        self.save("events/report.json",{"event":"report","report":result,"markdown":md,"profile":PROFILE})
        return {"report":result,"markdown":md,"hard_protocol_failure":hard_failure}
    def score_case(self,cid):
        reviewer_ids = [cid+"-review1",cid+"-review2"]
        states = [self.status(jid) for jid in reviewer_ids]
        protocol_missing = any(not s["valid"] for s in states)
        missing_sources = [j["job_id"] for j in self.plan()["jobs"] if j["case_id"] == cid and j["role"] != "review" and not self.status(j["job_id"])["valid"]]
        protocol_missing = protocol_missing or bool(missing_sources)
        packet, bindings = self.review_packet(self.job(reviewer_ids[0]))
        raw_by_condition = {condition:sum(b["condition"] == condition for b in bindings.values()) for condition in CONDITIONS}
        counts = {condition:{"raw":raw_by_condition[condition],"qualified":None,"uncertainty_eligible":None,"families":None} for condition in CONDITIONS}
        if any(not s["valid"] for s in states):
            return {"protocol_missing":True,"missing_sources":missing_sources,"conditions":counts,"intervals":None,"disagreements":[],"families":None,"compared_controls":None}
        reviews = [self.join_body(jid) for jid in reviewer_ids]
        card_rows = [{r["card_id"]:r for r in review["cards"]} for review in reviews]
        unit_rows = [{r["unit_id"]:r for r in review["units"]} for review in reviews]
        archive_rows = [{(r["card_id"],r["archive_id"]):r["relation"] for r in review["archive_pairs"]} for review in reviews]
        pair_rows = [{tuple(sorted((r["left"],r["right"]))):r["relation"] for r in review["candidate_pairs"]} for review in reviews]
        qualified, uncertain, disagreements = [],[],[]
        archives = [a["id"] for a in packet["archive"]]
        cards_by_id = {card["card_id"]:card for card in packet["cards"]}
        for card_id, binding in bindings.items():
            raw = cards_by_id[card_id]
            declared = raw["declared_card"]
            structural = raw["structurally_valid_unit"] and isinstance(declared,dict)
            available = structural and all(next((r["available"] for r in self.case(cid)["resources"] if r["id"] == rid),False) for rid in declared["resources"])
            unit = raw["unit_id"]
            unit_valid = all(rows[unit]["status"] == "valid" for rows in unit_rows)
            axes = [rows[card_id][axis] for rows in card_rows for axis in RUBRIC["axes"]]
            ars = [rows[(card_id,archive)] for rows in archive_rows for archive in archives]
            if structural and available and unit_valid and all(v is True for v in axes) and all(r == "distinct" for r in ars):
                qualified.append(card_id)
            if structural and available and unit_valid and not any(v is False for v in axes) and "equivalent" not in ars:
                uncertain.append(card_id)
            if any(card_rows[0][card_id][axis] != card_rows[1][card_id][axis] for axis in RUBRIC["axes"]) or any(archive_rows[0][(card_id,a)] != archive_rows[1][(card_id,a)] for a in archives):
                disagreements.append({"card_id":card_id,"type":"qualification"})
        distinct, possible = set(),set()
        for pair in pair_rows[0]:
            relations = [rows[pair] for rows in pair_rows]
            if relations == ["distinct","distinct"]:
                distinct.add(pair)
            if "equivalent" not in relations:
                possible.add(pair)
            if relations[0] != relations[1]:
                disagreements.append({"pair":list(pair),"type":"candidate_relation","reviewer_relations":relations})
        intervals = {}
        for condition in CONDITIONS:
            q = [c for c in qualified if bindings[c]["condition"] == condition]
            u = [c for c in uncertain if bindings[c]["condition"] == condition]
            interval = [max_clique(q,distinct),max_clique(u,possible)]
            counts[condition].update({"qualified":len(q),"uncertainty_eligible":len(u),"families":interval})
            intervals[condition] = interval
        families = [max_clique(qualified,distinct),max_clique(uncertain,possible)]
        comparisons = {condition:{control:interval_sub(intervals[condition],intervals[control]) for control in ("O","G")} for condition in CONDITIONS if condition not in ("O","G")}
        return {"protocol_missing":protocol_missing,"missing_sources":missing_sources,"conditions":counts,"intervals":intervals,
                "qualified_cards":qualified,"uncertainty_eligible_cards":uncertain,"disagreements":disagreements,"families":families,
                "compared_controls":None if protocol_missing else comparisons,"pair_policy":"equivalence excludes coexistence; unknown permissive only in upper; no transitivity"}

def max_clique(vertices, edges):
    """Exact maximum cardinality; <=28 vertices, branch/bound with greedy coloring."""
    vertices = sorted(vertices)
    if not vertices:
        return 0
    adjacency = {v:{u for u in vertices if u != v and tuple(sorted((u,v))) in edges} for v in vertices}
    best = 0
    def expand(chosen, candidates):
        nonlocal best
        if not candidates:
            best = max(best,chosen)
            return
        remaining = set(candidates)
        order, bounds, color = [],[],0
        while remaining:
            color += 1
            independent = set(remaining)
            while independent:
                v = min(independent,key=lambda x:len(adjacency[x] & remaining))
                order.append(v)
                bounds.append(color)
                remaining.remove(v)
                independent.remove(v)
                independent -= adjacency[v]
        for index in range(len(order)-1,-1,-1):
            if chosen + bounds[index] <= best:
                return
            v = order[index]
            expand(chosen+1,candidates & adjacency[v])
            candidates.remove(v)
    expand(0,set(vertices))
    return best

def interval_sub(a,b):
    return [a[0]-b[1],a[1]-b[0]]

def interval_add(a,b):
    return [a[0]+b[0],a[1]+b[1]]

def factorial(intervals):
    a,b,c,d = (intervals[k] for k in ("A","B","C","D"))
    return {"B_minus_A_delayed":interval_sub(b,a),"C_minus_A_residue":interval_sub(c,a),
            "D_minus_A_combined":interval_sub(d,a),"interaction_D_minus_B_minus_C_plus_A":interval_add(interval_sub(interval_sub(d,b),c),a)}

def get_witness(argument):
    if argument.lstrip().startswith("{"):
        return json.loads(argument)
    return read_json(argument)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",default=str(Path(__file__).resolve().parents[1]))
    sub = parser.add_subparsers(dest="command",required=True)
    for command in ("prepare","ready","capacity","report"):
        sub.add_parser(command)
    for command in ("prompt","started","joined","validate"):
        item = sub.add_parser(command)
        item.add_argument("job")
        if command in ("started","joined"):
            item.add_argument("handle")
        if command == "joined":
            item.add_argument("witness")
        if command == "validate":
            item.add_argument("output")
    item = sub.add_parser("freeze")
    for name in ("capacity-output","capacity-witness","prelaunch","prelaunch-witness"):
        item.add_argument("--"+name,required=True)
    args = parser.parse_args(argv)
    rt = Runtime(args.root)
    try:
        if args.command == "prepare":
            result = rt.prepare()
        elif args.command == "ready":
            result = rt.ready()
        elif args.command == "capacity":
            result = rt.capacity()
        elif args.command == "freeze":
            result = rt.freeze(args.capacity_output,args.capacity_witness,args.prelaunch,args.prelaunch_witness)
        elif args.command == "prompt":
            result = rt.prompt(args.job)
        elif args.command == "started":
            result = rt.started(args.job,args.handle)
        elif args.command == "joined":
            result = rt.joined(args.job,args.handle,get_witness(args.witness))
        elif args.command == "validate":
            rt.integrity()
            result = {"valid":rt.validation(rt.job(args.job),read_json(args.output)),"job_id":args.job}
        else:
            result = rt.report()
        print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        return 0
    except (GuardError,FileExistsError,FileNotFoundError,json.JSONDecodeError,UnicodeDecodeError) as error:
        print(json.dumps({"error":str(error),"command":args.command},sort_keys=True),file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())

