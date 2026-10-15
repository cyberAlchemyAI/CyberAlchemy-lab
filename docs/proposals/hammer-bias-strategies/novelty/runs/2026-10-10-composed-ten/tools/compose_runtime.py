#!/usr/bin/env python3
"""Pure filesystem adapter for a local, source-bound composed-method study.

No model, agent, browser or network calls occur here. Actual native observations
are supplied by the coordinator; a file is never evidence of a native call.
The older adapter is compiled into an isolated module without bytecode writes.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import sys
import tempfile
import types

REFERENCE_PATH = (Path(__file__).resolve().parents[2] /
                  "2026-10-10-reference-explicit/tools/ten_runtime.py")
_legacy = types.ModuleType("composed_immutable_reference")
_legacy.__file__ = str(REFERENCE_PATH)
exec(compile(REFERENCE_PATH.read_bytes(), str(REFERENCE_PATH), "exec"), _legacy.__dict__)
# These imported pure functions retain their original globals and schema.
encode = _legacy.encode
sha = _legacy.sha
case_refs = _legacy.case_refs
SCHEMAS = _legacy.SCHEMAS
validate_output = _legacy.validate_output
validate_review = _legacy.validate_review
GuardError = _legacy.GuardError
require = _legacy.require
obj = _legacy.obj
string = _legacy.string
array = _legacy.array
strings = _legacy.strings
unique = _legacy.unique
refs = _legacy.refs
words = _legacy.words
read_json = _legacy.read_json
digest_bytes = _legacy.digest_bytes


def blind_card(card, label):
    """Keep raw evidence private while masking administrative identity aliases."""
    projected = _legacy.blind_card(card, label)
    if isinstance(projected, dict) and "condition_id" in projected:
        projected["condition_id"] = "<opaque routing identity>"
    return projected

CASES = ("DEV", "CONF")
CONDITIONS = ("O",) + tuple("S%02d" % i for i in range(1, 11)) + tuple("R%02d" % i for i in range(1, 11))
PARENTS = {"R01": ("S01", "S06"), "R02": ("S02", "S05"),
           "R03": ("S03", "S07"), "R04": ("S04", "S03"),
           "R05": ("S07", "S06"), "R06": ("S08", "S05"),
           "R07": ("S09", "S04"), "R08": ("S10", "S01"),
           "R09": ("S02", "S08"), "R10": ("S09", "S07")}
RESIDUE = {"S06", "R01", "R05"}
AXES = ("anchor_fit", "resource_fit", "separating", "defeat_clear", "source_support")
GUARD_SCHEMA = {"job_id": "text", "case_id": "text", "outcome": "exact fixed valued_outcome",
                "limits": [{"constraint_id": "C ID", "text": "text"}],
                "burden_observables": ["M IDs"], "source_refs": ["numbered allowed fact IDs"],
                "unknowns": ["text"]}
PROFILE = {"PROFILE_ID": "composed-ten-local-native-study.v1", "ARTIFACT_TYPE": "pure-filesystem-native-study-adapter",
           "QUALITY_BAR_STATUS": "bounded_synthetic_local_contract", "LIFECYCLE_OWNER": "human-authorized-native-coordinator",
           "REGIME_SET": ["development", "confirmation"], "CONTRACT_PATH": "CONTRACT.md",
           "PROMPT_SET": "composed-ten-literal-prompts.v1", "PROFILE_VALIDATION": "mechanical tests plus independent native prelaunch",
           "WORKFLOW_GAPS_JSON": ["actual spawn and FINAL truth rests on coordinator observation",
                                  "unobserved pre-FINAL overwrites cannot be certified absent",
                                  "synthetic reviewer judgments do not establish real-world benefit"],
           "ANTI_PATTERN_HITS_JSON": []}
RUBRIC = {"axes": list(AXES), "qualified": "valid full chain; available resources; both reviewers true on all five axes and distinct against every ordinary archive",
          "composition_addition": "all four relevant chains and both review locks valid; qualified recipe card distinct by both reviewers against every raw card in O and both parents",
          "pair_policy": "either equivalent excludes addition; both distinct proves separation; all remaining pairs unknown and conservative null",
          "nominal_rows": 315, "review_soft_word_cap": 16000,
          "coverage_priority": "every declared raw card and all pairs, including anomalous extra declarations"}


def now():
    return datetime.now(timezone.utc).isoformat()


def exclusive(path, value, binary=False):
    """Atomic exclusive first publication: link a synced temporary file, never replace."""
    path = Path(path)
    require(path.parent.is_dir(), "output parent must already exist: " + str(path.parent))
    data = value if binary else encode(value)
    fd, temp = tempfile.mkstemp(prefix=".first-save-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp, path)
        directory = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(temp)
    return {"path": str(path.resolve()), "sha256": digest_bytes(data), "bytes": len(data)}


def stable_bytes(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "regular output file required")
    first_stat = path.stat()
    first = path.read_bytes()
    second = path.read_bytes()
    second_stat = path.stat()
    signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    require(first == second and signature(first_stat) == signature(second_stat), "output changed during terminal observation")
    return first, {"sha256": digest_bytes(first), "bytes": len(first), "stable_double_read": True,
                   "stat": list(signature(second_stat)), "observed_at": now()}


def validate_cases(cases):
    obj(cases, CASES, "case registry")
    fields = ("case_id", "phase", "domain", "valued_outcome", "hard_constraints", "observations", "resources",
              "preferred_dependency", "causal_return_path_hypothesis", "anomaly_id", "parent_operations",
              "available_observables", "unknowns", "ordinary_archive")
    tables = {"hard_constraints": ("C", 3, 6), "observations": ("O", 5, 8), "resources": ("R", 5, 8),
              "parent_operations": ("P", 2, 2), "available_observables": ("M", 3, 5),
              "unknowns": ("U", 2, 4), "ordinary_archive": ("A", 3, 4)}
    for cid in CASES:
        case = cases[cid]
        obj(case, fields, "case")
        require(case["case_id"] == cid, "case registry identity")
        require(case["phase"] == ("development" if cid == "DEV" else "confirmation"), "case phase")
        for key in ("domain", "valued_outcome", "preferred_dependency", "causal_return_path_hypothesis", "anomaly_id"):
            string(case[key], key)
        seen = []
        for field, (prefix, low, high) in tables.items():
            array(case[field], field, low, high)
            ids = []
            for row in case[field]:
                keys = ("id", "text", "available") if field == "resources" else (("id", "operation", "relation", "probe", "limits") if field == "ordinary_archive" else ("id", "text"))
                obj(row, keys, field)
                for key in keys:
                    if key == "available":
                        require(type(row[key]) is bool, "resource availability must be boolean")
                    else:
                        string(row[key], field + "." + key)
                ident = row["id"]
                require(ident.startswith(prefix) and ident[len(prefix):].isdigit() and int(ident[len(prefix):]) > 0, "numbered source ID required")
                ids.append(ident)
                seen.append(ident)
            unique(ids, field)
            require(set(ids) == {prefix + str(i) for i in range(1, len(ids) + 1)}, "contiguous source IDs required")
        unique(seen, "case row IDs")
        require(case["anomaly_id"] in {r["id"] for r in case["observations"]}, "anomaly is an observed row ID")
    return True


def validate_methods(methods):
    obj(methods, CONDITIONS, "method registry")
    for condition, method in methods.items():
        obj(method, ("name", "instructions", "supplement_branch"), "method")
        string(method["name"], "human method name")
        string(method["instructions"], "method instructions")
        require(method["supplement_branch"] == ("residue" if condition in RESIDUE else "summary"), "assigned branch mismatch")
    return True


def make_plan():
    jobs = []
    for cid in CASES:
        guard = cid + "-guard"
        jobs.append({"job_id": guard, "case_id": cid, "role": "guard", "condition": None, "dependencies": []})
        for condition in CONDITIONS:
            previous = None
            for role in ("stage1", "stage2", "builder"):
                jid = cid + "-" + condition + "-" + role
                deps = [previous] if role == "builder" else [guard] + ([previous] if previous else [])
                jobs.append({"job_id": jid, "case_id": cid, "role": role, "condition": condition,
                             "dependencies": deps, "supplement_branch": "residue" if condition in RESIDUE else "summary"})
                previous = jid
        for reviewer in (1, 2):
            jobs.append({"job_id": cid + "-review" + str(reviewer), "case_id": cid, "role": "review", "condition": None,
                         "dependencies": [cid + "-" + c + "-builder" for c in CONDITIONS]})
    require(len(jobs) == 132, "132 scored slots required")
    return {"schema": "composed-ten-plan.v1", "planned_native_calls": 132, "per_case": 66,
            "conditions": list(CONDITIONS), "cases": list(CASES), "parents": PARENTS, "jobs": jobs,
            "attempt_policy": "one first attempt; invalid upstream gates dependents; reviews still run"}


def base_prompt(job, common):
    role = job["role"]
    schema = GUARD_SCHEMA if role == "guard" else SCHEMAS[role]
    text = [common.rstrip(),
            "Fresh native worker, fork_turns='none'. Read only the assigned literal prompt. No search, siblings, prior results, web, agents, private receipts, condition map or other case.",
            "Produce one JSON object at OUTPUT_PATH, first and only save using Python open(OUTPUT_PATH, 'x'). Validate in memory first. Never repair, retry or overwrite the first saved bytes.",
            "Synthetic facts are stipulated. New mechanisms, predictions and successful futures are hypotheses. Preserve uncertainty.",
            "ALLOWED_SOURCE_REFS_JSON is the complete whitelist: numbered C/O/R/P/M/U row IDs only. Case, job, CONDITION_ID, archive, human method name and generated item IDs never count as source_refs. Validate every source_refs nonempty unique list is a subset of that whitelist before first save.",
            "Exact required keys and typed schema:\n" + json.dumps(schema, ensure_ascii=False, sort_keys=True)]
    if role == "guard":
        text += ["Outcome-only audit. Keep outcome exactly equal to the supplied valued_outcome. Audit fixed hard constraints, available work/resources and burden observables only. Never propose or select methods, inversions, attacks, alternatives, interventions or constructions. One limit for every supplied C ID, nonempty texts, burden_observables only supplied M IDs, nonempty source_refs and unknowns. Maximum 600 normalized saved JSON words."]
    elif role == "stage1":
        text += ["Apply only your assigned method. policy MUST be exact CONDITION_ID, separately from its human-readable name. Use own case, ordinary archive and outcome-only guard. Both core and residue nonempty; unique generated IDs; exact numbered source_refs. Tension names incompatible accounts and separating predictions. Maximum 600 normalized saved JSON words."]
        if job["condition"] == "R04":
            text += ["R04 role: propose the carrier migration only, retaining uncertain attack predictions. Do not select a final attack. The separate stage2 worker will freshly attack this proposed new carrier."]
    elif role == "stage2":
        text += ["Distill only own stage1 using own case, fixed guard and assigned method. Preserve nonempty summary and residue with unique item IDs and exact numbered source_refs. Both branches must derive from admitted inputs; label new hypotheses honestly. Maximum 600 normalized saved JSON words."]
        if job["condition"] == "R04":
            text += ["R04 role: act as the fresh attacker of the stage1 proposed carrier. Trace displacement, actor burden and failure of the new dependency before source-bound distillation. Preserve the attack and surviving outcome in summary for the separate fresh builder; do not merely compress the migration proposal."]
    elif role == "builder":
        text += ["Fresh builder: only own case, ordinary archive, assigned method and the supplied supplement branch are admitted. Full stage1, outcome guard and omitted branch are unavailable. Do not infer or request omitted content. residue_refs names only exact IDs received in supplement, including summary IDs where assigned. Maximum ONE card and 600 normalized saved JSON words. Zero cards requires nonempty no_opening_reason; otherwise null. Each card needs anchor, mutation, construction, rival, separating probe, both predictions, defeat, resources, source_refs, residue_refs, burden and unknowns. Required unavailable resources make a card unqualified."]
    else:
        text += ["Whole-case independent review. Method labels and the private permutation map are withheld; substantive content can suggest a method, so full semantic blinding is not claimed. Preserve supplied structural unit status. Judge all five axes true/false/null and explicitly reject indispensable unavailable resources. Pair relations are equivalent/distinct/unknown without transitivity.",
                 "Cover exactly all units, every declared raw card including malformed declarations in failure wrappers, every card/archive pair and every unordered card/card pair once. Valid zero-opening units have no card rows. Complete coverage takes priority over the 16000 normalized JSON word soft cap. Nominal geometry is 315 rows with 21 cards and three archives; anomalous extra cards are never discarded."]
    return ("\n".join(text) + "\n").encode()


def literal_prompt(job, base, output, payload):
    source = sorted(case_refs(payload["case"]))
    header = ("JOB_ID=" + job["job_id"] + "\nCASE_ID=" + job["case_id"] +
              "\nCONDITION_ID=" + (job["condition"] or "NONE") + "\nOUTPUT_PATH=" + str(output) +
              "\nALLOWED_SOURCE_REFS_JSON:\n" + json.dumps(source) + "\nDECLARED_INPUTS_JSON:\n")
    return base + header.encode() + encode(payload)


def validate_guard(job, value, case):
    obj(value, GUARD_SCHEMA, "outcome guard")
    require(value["job_id"] == job["job_id"] and value["case_id"] == job["case_id"], "guard identity")
    require(value["outcome"] == case["valued_outcome"], "guard changed fixed outcome")
    array(value["limits"], "limits", 1)
    ids = []
    for row in value["limits"]:
        obj(row, ("constraint_id", "text"), "limit")
        string(row["text"], "limit text")
        ids.append(row["constraint_id"])
    unique(ids, "guard constraints")
    require(set(ids) == {r["id"] for r in case["hard_constraints"]}, "guard must audit every fixed constraint")
    refs(value["burden_observables"], {r["id"] for r in case["available_observables"]}, "burden observable refs")
    refs(value["source_refs"], case_refs(case), "guard source refs")
    strings(value["unknowns"], "guard unknowns", 1)
    require(words(value) <= 600, "guard saved-word cap exceeded")
    return True


def validate_native_witness(value, handle=None):
    _legacy.witness(value, handle)
    if "worker_create_exclusive_reported" in value:
        require(type(value["worker_create_exclusive_reported"]) is bool, "exclusive-save report is boolean")
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

    @contextmanager
    def controller(self):
        require(self.root.is_dir(), "run root missing")
        with self.p(".controller.lock").open("ab") as stream:
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise GuardError("another controller is mutating this run") from error
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)

    def record(self, action, artifacts=(), **fields):
        logs = sorted(self.p("events/log").glob("*.json"))
        index = len(logs) + 1
        event = {"sequence": index, "action": action, "observed_at": now(),
                 "previous_sha256": sha(logs[-1]) if logs else None, "artifacts": list(artifacts), **fields}
        self.save("events/log/%06d.json" % index, event)
        return event

    def log_integrity(self):
        previous = None
        for index, path in enumerate(sorted(self.p("events/log").glob("*.json")), 1):
            event = read_json(path)
            require(path.name == "%06d.json" % index and event["sequence"] == index and event["previous_sha256"] == previous, "event log chain drift")
            for artifact in event["artifacts"]:
                require(Path(artifact["path"]).is_file() and sha(artifact["path"]) == artifact["sha256"], "immutable event artifact drift: " + artifact["path"])
            previous = sha(path)
        return True

    def plan(self):
        return self.load("prepared/plan.json")

    def job(self, jid):
        jobs = {j["job_id"]: j for j in self.plan()["jobs"]}
        require(jid in jobs, "unknown job ID")
        return jobs[jid]

    def case(self, cid):
        return self.load("prepared/cases/" + cid + ".json")

    def output(self, jid):
        return self.p("raw/" + jid + ".json")

    def init(self):
        with self.controller():
            require(shutil.which("python3") is not None, "python3 must be available before admission")
            require(not self.p("prepared/plan.json").exists(), "already initialized")
            cases, methods = self.load("inputs/cases.json"), self.load("inputs/methods.json")
            validate_cases(cases)
            validate_methods(methods)
            budget = self.load("preparation/BUDGET.v1.json")
            require(budget["scored"]["total"] == 132 and budget["maximum_native_calls"] == 143, "budget accounting mismatch")
            require(budget["output_caps"] == {"proposal_normalized_json_words": 600, "distillation_normalized_json_words": 600, "builder_normalized_json_words": 600, "cards_per_builder": 1, "review_normalized_json_words": 16000}, "budget caps mismatch")
            string(self.p("CONTRACT.md").read_text(), "contract")
            common = self.p("prompts/COMMON.md").read_text(encoding="utf-8")
            string(common, "common prompt")
            for directory in ("prepared", "prepared/cases", "prepared/base-prompts", "prepared/private", "prompts/actual", "raw", "receipts", "receipts/raw", "receipts/jobs", "events", "events/log", "reports", "development/example-prompts", "development/example-outputs"):
                self.p(directory).mkdir(parents=True, exist_ok=True)
            require(not any(self.output(j["job_id"]).exists() for j in make_plan()["jobs"]), "stale scored outputs before init")
            artifacts = [self.save("prepared/plan.json", make_plan()), self.save("prepared/profile.json", PROFILE),
                         self.save("prepared/rubric.json", RUBRIC), self.save("prepared/methods.json", methods)]
            permutations = {}
            seed = digest_bytes(encode({"cases": cases, "methods": methods, "study": "composed-ten.v1"}))
            for cid in CASES:
                artifacts.append(self.save("prepared/cases/" + cid + ".json", cases[cid]))
                conditions = list(CONDITIONS)
                random.Random(seed + cid).shuffle(conditions)
                permutations[cid] = {c: cid + "-U%02d" % (i + 1) for i, c in enumerate(conditions)}
            artifacts.append(self.save("prepared/private/unit-map.json", {"seed_sha256": seed, "mapping": permutations}))
            for job in self.plan()["jobs"]:
                artifacts.append(self.save("prepared/base-prompts/" + job["job_id"] + ".txt", base_prompt(job, common), True))
            self.record("init", artifacts, planned_native_calls=132, maximum_total_native_calls=143, profile=PROFILE)
            return {"initialized": True, "planned_native_calls": 132, "output_parent": str(self.p("raw")), "python3": shutil.which("python3")}

    def source_snapshot(self):
        required = [self.p(p) for p in ("inputs/cases.json", "inputs/methods.json", "CONTRACT.md", "prompts/COMMON.md", "preparation/BUDGET.v1.json", "preparation/ENGINEER-RECEIPT.v1.json", "tools/compose_runtime.py", "tools/test_compose_runtime.py")]
        required.append(REFERENCE_PATH)
        for path in required:
            require(path.is_file(), "required frozen source missing: " + str(path))
        paths = required + [p for p in self.p("prepared").rglob("*") if p.is_file()]
        for path in self.root.iterdir():
            if path.is_file() and path.suffix in (".md", ".json"):
                paths.append(path)
        for directory in ("inputs", "prompts", "development"):
            for path in self.p(directory).rglob("*"):
                if path.is_file() and not any(part in ("actual", "example-prompts", "example-outputs", "__pycache__") for part in path.parts):
                    paths.append(path)
        source_bindings = self.p("preparation/SOURCE-BINDINGS.v1.json")
        if source_bindings.is_file():
            for binding in read_json(source_bindings):
                require(Path(binding["path"]).is_file() and sha(binding["path"]) == binding["sha256"], "declared source binding drift: " + binding["path"])
                paths.append(Path(binding["path"]))
        return {str(p.resolve()): sha(p) for p in sorted(set(paths))}

    def freeze(self, prelaunch=None, prelaunch_witness=None, capacity_receipt=None, capacity_witness=None):
        with self.controller():
            self.log_integrity()
            require(not self.p("events/freeze.json").exists(), "already frozen")
            require(not any(self.p("receipts/jobs").iterdir()) and not any(self.output(j["job_id"]).exists() for j in self.plan()["jobs"]), "freeze must precede scored admissions")
            # No silent source edit between init and freeze may leave stale prepared inputs.
            validate_cases(self.load("inputs/cases.json"))
            validate_methods(self.load("inputs/methods.json"))
            require(self.load("prepared/methods.json") == self.load("inputs/methods.json"), "methods changed after init")
            common = self.p("prompts/COMMON.md").read_text(encoding="utf-8")
            for cid in CASES:
                require(self.case(cid) == self.load("inputs/cases.json")[cid], "case changed after init")
            for job in self.plan()["jobs"]:
                require(self.p("prepared/base-prompts/" + job["job_id"] + ".txt").read_bytes() == base_prompt(job, common), "common prompt changed after init")
            prelaunch = Path(prelaunch or self.p("preparation/BALANCER-3.v1.json"))
            prelaunch_witness = Path(prelaunch_witness or self.p("receipts/PREP-BALANCER-3.native.json"))
            capacity_receipt = Path(capacity_receipt or self.p("preparation/CAPACITY.v1.json"))
            capacity_witness = Path(capacity_witness or self.p("receipts/CAPACITY.native.json"))
            verdict, capacity = read_json(prelaunch), read_json(capacity_receipt)
            require(verdict.get("verdict") == "pass" and verdict.get("blocking_issues") == [], "independent prelaunch must pass")
            array(verdict.get("checks"), "prelaunch checks", 1)
            require(capacity.get("verdict") == "pass", "capacity must pass")
            witnesses = [read_json(prelaunch_witness), read_json(capacity_witness)]
            for witness in witnesses:
                validate_native_witness(witness)
            require(witnesses[0]["handle"] != witnesses[1]["handle"], "prelaunch and capacity must be independent native calls")
            capacity_packet = self.load("capacity/review-packet.json")
            require(len(capacity_packet["units"]) == 21 and len(capacity_packet["cards"]) == 21 and len(capacity_packet["archive"]) == 3,
                    "capacity requires the 21-unit/21-card/three-archive nominal geometry")
            capacity_bytes, capacity_observation = stable_bytes(self.p("raw/CAPACITY.review.json"))
            capacity_assessment = json.loads(capacity_bytes.decode("utf-8"))
            validate_review(capacity_assessment, capacity_packet)
            require(sum(len(capacity_assessment[k]) for k in ("units", "cards", "archive_pairs", "candidate_pairs")) == 315,
                    "capacity must cover all 315 nominal rows")
            if witnesses[1].get("first_observed_output_sha256") is not None:
                require(witnesses[1]["first_observed_output_sha256"] == capacity_observation["sha256"], "capacity coordinator output digest mismatch")
            sources = self.source_snapshot()
            for path in (prelaunch, prelaunch_witness, capacity_receipt, capacity_witness):
                sources[str(path.resolve())] = sha(path)
            # Bind root-authored preparation, capacity and literal fixtures that exist now.
            for directory in ("preparation", "capacity", "raw"):
                for path in self.p(directory).rglob("*"):
                    if path.is_file() and "__pycache__" not in path.parts:
                        sources[str(path.resolve())] = sha(path)
            artifact = self.save("events/freeze.json", {"schema": "composed-freeze.v1", "sources": sources, "profile": PROFILE,
                                  "prelaunch": str(prelaunch.resolve()), "capacity": str(capacity_receipt.resolve()),
                                  "prelaunch_handle": witnesses[0]["handle"], "capacity_handle": witnesses[1]["handle"],
                                  "capacity_output_observation": capacity_observation, "capacity_rows": 315,
                                  "capacity_scope": "nominal maximal one-card review geometry and declared input fixture; no scored quality inference", "frozen_at": now()})
            self.record("freeze", [artifact], sources=len(sources), planned_native_calls=132)
            return {"frozen": True, "sha256": artifact["sha256"], "sources": len(sources), "planned_native_calls": 132}

    def integrity(self):
        require(self.p("events/freeze.json").is_file(), "freeze required before scored admission")
        self.log_integrity()
        for path, digest in self.load("events/freeze.json")["sources"].items():
            require(Path(path).is_file() and sha(path) == digest, "frozen source drift: " + path)
        return True

    def status(self, jid=None):
        if jid is None:
            return {"planned_native_calls": 132, "jobs": {j["job_id"]: self.status(j["job_id"]) for j in self.plan()["jobs"]}}
        self.job(jid)
        for disposition in ("finished", "gated", "spawned", "admitted"):
            path = self.p("receipts/jobs/" + jid + "." + disposition + ".json")
            if path.is_file():
                receipt = read_json(path)
                return {"disposition": disposition, "terminal": disposition in ("finished", "gated"), "valid": receipt.get("valid", False), "receipt": receipt}
        return {"disposition": "pending", "terminal": False, "valid": False}

    def checked_terminal(self, jid):
        state = self.status(jid)
        require(state["terminal"], "dependency not terminal: " + jid)
        output_digest = state["receipt"].get("output_sha256")
        if output_digest is None:
            require(not self.output(jid).exists(), "output appeared after absent/gated lock: " + jid)
        else:
            require(self.output(jid).is_file() and not self.output(jid).is_symlink() and sha(self.output(jid)) == output_digest, "first saved output drift: " + jid)
            observed = state["receipt"].get("output_observation")
            if observed is not None:
                stat = self.output(jid).stat()
                require(list((stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)) == observed["stat"], "first saved output metadata drift: " + jid)
        return state

    def join_body(self, jid):
        state = self.checked_terminal(jid)
        require(state["valid"], "dependency not valid: " + jid)
        return read_json(self.output(jid))

    def allowed_phase(self, job):
        if job["case_id"] == "DEV":
            return True
        states = [self.checked_terminal("DEV-review" + str(i)) if self.status("DEV-review" + str(i))["terminal"] else self.status("DEV-review" + str(i)) for i in (1, 2)]
        return all(s["disposition"] == "finished" and s["receipt"].get("review_lock") is True and s["receipt"].get("observation") == "FINAL" for s in states)

    def eligibility(self, job):
        if not self.allowed_phase(job):
            return False
        states = [self.checked_terminal(d) if self.status(d)["terminal"] else self.status(d) for d in job["dependencies"]]
        return all(s["terminal"] for s in states) if job["role"] == "review" else all(s["terminal"] and s["valid"] for s in states)

    def ready(self):
        self.integrity()
        ready, gateable = [], []
        for job in self.plan()["jobs"]:
            if self.status(job["job_id"])["disposition"] != "pending" or not self.allowed_phase(job):
                continue
            if self.eligibility(job):
                ready.append({"job_id": job["job_id"], "role": job["role"], "case_id": job["case_id"], "condition_id": job["condition"], "fork_turns": "none"})
            elif job["role"] != "review" and any(self.status(d)["terminal"] and not self.status(d)["valid"] for d in job["dependencies"]):
                gateable.append(job["job_id"])
        return {"ready": ready, "gateable": gateable, "read_only": True}

    def gate(self, jid):
        with self.controller():
            self.integrity()
            job = self.job(jid)
            require(self.status(jid)["disposition"] == "pending", "gate only a never-admitted job")
            require(self.allowed_phase(job), "not-before-ready confirmation barrier")
            require(job["role"] != "review", "reviews cannot be gated; review every terminal declaration")
            require(not self.output(jid).exists(), "unexpected output before gating")
            failures = [d for d in job["dependencies"] if self.status(d)["terminal"] and not self.checked_terminal(d)["valid"]]
            require(failures, "not-before-ready gate needs a terminal invalid/missing predecessor")
            body = {"job_id": jid, "event": "gated", "valid": False, "failed_sources": failures,
                    "reason": "invalid or missing indispensable predecessor", "output_sha256": None, "observed_at": now()}
            artifact = self.save("receipts/jobs/" + jid + ".gated.json", body)
            self.record("gate", [artifact], job_id=jid)
            return body

    def review_packet(self, job):
        cid = job["case_id"]
        mapping = self.load("prepared/private/unit-map.json")["mapping"][cid]
        units, cards, private = [], [], {}
        for condition in CONDITIONS:
            jid = cid + "-" + condition + "-builder"
            state = self.checked_terminal(jid)
            unit = mapping[condition]
            units.append({"unit_id": unit, "status": "gated" if state["disposition"] == "gated" else ("valid" if state["valid"] else "invalid"), "reason": state["receipt"].get("reason", "valid")})
            value = None
            if self.output(jid).is_file():
                try:
                    value = read_json(self.output(jid))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
            for index, card in enumerate(_legacy.raw_cards(value)):
                label = unit + "-C%02d" % (index + 1)
                cards.append({"card_id": label, "unit_id": unit, "declared_card": blind_card(card, label),
                              "structurally_valid_unit": state["valid"], "failure_reason": None if state["valid"] else state["receipt"]["reason"]})
                private[label] = {"job_id": jid, "condition": condition, "index": index, "raw_sha256": digest_bytes(encode(card))}
        case = self.case(cid)
        rows = len(units) + len(cards) + len(cards) * len(case["ordinary_archive"]) + len(cards) * (len(cards) - 1) // 2
        packet = {"job_id": job["job_id"], "case_id": cid, "case": case, "units": sorted(units, key=lambda x: x["unit_id"]),
                  "cards": sorted(cards, key=lambda x: x["card_id"]), "archive": case["ordinary_archive"], "rubric": RUBRIC,
                  "required_row_count": rows}
        return packet, private

    def projection(self, job):
        cid, role = job["case_id"], job["role"]
        full = self.case(cid)
        case = {k: v for k, v in full.items() if k != "ordinary_archive"}
        bindings = [{"path": str(self.p("prepared/cases/" + cid + ".json")), "sha256": sha(self.p("prepared/cases/" + cid + ".json")), "projection": "own case"}]
        if role == "review":
            body, _ = self.review_packet(job)
            for dep in job["dependencies"]:
                state = self.checked_terminal(dep)
                bindings.append({"job_id": dep, "output_sha256": state["receipt"].get("output_sha256"), "terminal_receipt_sha256": sha(self.p("receipts/jobs/" + dep + "." + state["disposition"] + ".json")), "projection": "opaque every raw declared card or failure"})
            return body, bindings
        body = {"case": case}
        if role in ("stage1", "builder"):
            body["archive"] = full["ordinary_archive"]
        if job["condition"] is not None:
            body["method"] = {"condition_id": job["condition"], **self.load("prepared/methods.json")[job["condition"]]}
        for dep in job["dependencies"]:
            value = self.join_body(dep)
            if role == "builder":
                body["supplement"] = value[job["supplement_branch"]]
                projection = "only " + job["supplement_branch"]
            elif dep.endswith("-guard"):
                body["outcome_guard"] = value
                projection = "outcome-only guard"
            else:
                body["stage1"] = value
                projection = "whole own stage1"
            bindings.append({"job_id": dep, "output_sha256": sha(self.output(dep)), "projection": projection})
        return body, bindings

    def start(self, jid):
        with self.controller():
            self.integrity()
            job = self.job(jid)
            require(self.status(jid)["disposition"] == "pending", "one admission only; no retry")
            require(not self.output(jid).exists(), "output exists before native admission")
            require(self.allowed_phase(job), "confirmation barrier: both DEV raw review FINAL locks required")
            require(self.eligibility(job), "dependencies not ready/valid")
            body, bindings = self.projection(job)
            base = self.p("prepared/base-prompts/" + jid + ".txt").read_bytes()
            literal = literal_prompt(job, base, self.output(jid), body)
            artifacts = [self.save("prompts/actual/" + jid + ".payload.json", body), self.save("prompts/actual/" + jid + ".txt", literal, True),
                         self.save("development/example-prompts/" + jid + ".md", literal, True)]
            private = None
            if job["role"] == "review":
                private = self.save("prepared/private/" + jid + ".card-map.json", self.review_packet(job)[1])
                artifacts.append(private)
            prompt_path = str(self.p("prompts/actual/" + jid + ".txt"))
            task = "Read only " + prompt_path + ". Follow its exact schema and create-exclusive first-save instruction. Exact CONDITION_ID=" + (job["condition"] or "NONE") + ". Save only the assigned OUTPUT_PATH; report terminal FINAL."
            descriptor = {"job_id": jid, "role": job["role"], "case_id": job["case_id"], "condition_id": job["condition"],
                          "prompt_path": prompt_path, "prompt_sha256": digest_bytes(literal), "payload_sha256": digest_bytes(encode(body)),
                          "output_path": str(self.output(jid)), "output_absent_at_admission": True, "dependencies": bindings,
                          "input_normalized_json_words": words(body), "literal_words": len(literal.decode().split()),
                          "supplement_words": words(body["supplement"]) if "supplement" in body else None,
                          "fork_turns": "none", "native_worker_task": task, "admitted_at": now()}
            artifacts.append(self.save("receipts/jobs/" + jid + ".admitted.json", descriptor))
            self.record("start", artifacts, job_id=jid)
            return descriptor

    def reconstruct(self, jid):
        job = self.job(jid)
        descriptor = self.load("receipts/jobs/" + jid + ".admitted.json")
        body, bindings = self.projection(job)
        require(bindings == descriptor["dependencies"], "admitted dependency binding drift")
        require(encode(body) == self.p("prompts/actual/" + jid + ".payload.json").read_bytes(), "payload reconstruction drift")
        actual = literal_prompt(job, self.p("prepared/base-prompts/" + jid + ".txt").read_bytes(), self.output(jid), body)
        require(actual == self.p("prompts/actual/" + jid + ".txt").read_bytes() and digest_bytes(actual) == descriptor["prompt_sha256"], "literal prompt reconstruction drift")
        return descriptor

    def spawned(self, jid, handle):
        with self.controller():
            self.integrity()
            require(self.status(jid)["disposition"] == "admitted", "one spawn requires prior admission")
            string(handle, "actual native spawn handle")
            reserved = {self.load("events/freeze.json")["prelaunch_handle"], self.load("events/freeze.json")["capacity_handle"]}
            for path in self.p("receipts/jobs").glob("*.spawned.json"):
                reserved.add(read_json(path)["handle"])
            require(handle not in reserved, "native spawn handle reused")
            descriptor = self.reconstruct(jid)
            observation = None
            if self.output(jid).exists():
                _, observation = stable_bytes(self.output(jid))
            body = {"job_id": jid, "handle": handle, "event": "spawned", "fork_turns": "none", "native_turn": 1,
                    "prompt_sha256": descriptor["prompt_sha256"], "first_parent_output_observation": observation,
                    "observed_at": now(), "timing_limit": "registration follows actual spawn; early file alone does not prove native provenance"}
            artifact = self.save("receipts/jobs/" + jid + ".spawned.json", body)
            self.record("spawned", [artifact], job_id=jid, handle=handle)
            return body

    def validation(self, job, value):
        case = self.case(job["case_id"])
        if job["role"] == "guard":
            return validate_guard(job, value, case)
        supplement, review = (), None
        if job["role"] == "builder":
            supplement = [row["id"] for row in self.join_body(job["case_id"] + "-" + job["condition"] + "-stage2")[job["supplement_branch"]]]
        if job["role"] == "review":
            review = self.review_packet(job)[0]
        validate_output(job, value, case, supplement, review)
        if job["role"] in ("stage1", "stage2", "builder"):
            require(words(value) <= 600, "600 normalized JSON word cap exceeded")
        if job["role"] == "builder":
            require(len(value["cards"]) <= 1, "one builder card cap exceeded")
        return True

    def finish(self, jid, witness):
        with self.controller():
            self.integrity()
            require(self.status(jid)["disposition"] == "spawned", "finish needs one registered actual native spawn")
            job = self.job(jid)
            start = self.load("receipts/jobs/" + jid + ".spawned.json")
            validate_native_witness(witness, start["handle"])
            self.reconstruct(jid)
            value, valid, reason, observation, output_data = None, False, "missing first-saved output", None, None
            artifacts = []
            if self.output(jid).exists():
                output_data, observation = stable_bytes(self.output(jid))
                first = start["first_parent_output_observation"]
                if first is not None:
                    require(first["sha256"] == observation["sha256"] and first["stat"] == observation["stat"], "first observed output mutated before FINAL lock")
                if witness.get("first_observed_output_sha256") is not None:
                    require(witness["first_observed_output_sha256"] == observation["sha256"], "coordinator first output digest mismatch")
                artifacts.append(self.save("receipts/raw/" + jid + ".first.bin", output_data, True))
                artifacts.append(self.save("development/example-outputs/" + jid + ".json", output_data, True))
                try:
                    value = json.loads(output_data.decode("utf-8"))
                    self.validation(job, value)
                    valid, reason = True, "valid"
                except (GuardError, json.JSONDecodeError, UnicodeDecodeError, TypeError, KeyError) as error:
                    reason = str(error)
            elif start["first_parent_output_observation"] is not None:
                raise GuardError("first observed output disappeared before FINAL")
            artifacts.append(self.save("receipts/jobs/" + jid + ".witness.json", witness))
            body = {"job_id": jid, "handle": start["handle"], "event": "finished", "observation": "FINAL", "valid": valid,
                    "reason": reason, "review_lock": job["role"] == "review", "output_sha256": observation["sha256"] if observation else None,
                    "output_observation": observation, "normalized_json_words": words(value) if value is not None else None,
                    "literal_output_words": len(output_data.decode("utf-8", errors="replace").split()) if output_data is not None else None,
                    "output_bytes": len(output_data) if output_data is not None else None, "witness_sha256": artifacts[-1]["sha256"],
                    "final_text_sha256": digest_bytes(witness["final_text"].encode()), "worker_create_exclusive_reported": witness.get("worker_create_exclusive_reported"),
                    "first_save_limit": "first parent-observed bytes locked; unobserved pre-FINAL overwrite cannot be certified absent", "observed_at": now()}
            artifacts.append(self.save("receipts/jobs/" + jid + ".finished.json", body))
            self.record("finish", artifacts, job_id=jid, handle=start["handle"], valid=valid)
            return body

    def chain(self, cid, condition):
        ids = [cid + "-guard"] + [cid + "-" + condition + "-" + r for r in ("stage1", "stage2", "builder")]
        states = [self.status(jid) for jid in ids]
        valid = all(s["terminal"] and s["valid"] for s in states)
        return {"valid": valid, "generation_chain_valid": valid, "semantic_recipe_fidelity": "not_checked",
                "jobs": {jid: {"disposition": state["disposition"], "valid": state["valid"]} for jid, state in zip(ids, states)}}

    def score_case(self, cid):
        packet, private = self.review_packet(self.job(cid + "-review1"))
        review_states = [self.checked_terminal(cid + "-review" + str(i)) for i in (1, 2)]
        reviews_valid = all(s["valid"] and s["receipt"].get("review_lock") is True for s in review_states)
        chains = {c: self.chain(cid, c) for c in CONDITIONS}
        by_condition = {c: [card for card, binding in private.items() if binding["condition"] == c] for c in CONDITIONS}
        counts = {c: {"chain_valid": chains[c]["valid"], "raw": len(by_condition[c]), "qualified": None, "uncertainty_eligible": None} for c in CONDITIONS}
        report = {"both_review_locks_valid": reviews_valid, "chains": chains, "conditions": counts, "recipes": {}, "disagreements": []}
        if not reviews_valid:
            for recipe, parents in PARENTS.items():
                relevant = ("O", *parents, recipe)
                report["recipes"][recipe] = {"comparators": list(relevant), "all_four_chains_valid": all(chains[c]["valid"] for c in relevant),
                                             "composition_adds": None, "qualified_additions": None, "reason": "both complete independent review locks required"}
            return report
        reviews = [self.join_body(cid + "-review" + str(i)) for i in (1, 2)]
        card_rows = [{r["card_id"]: r for r in v["cards"]} for v in reviews]
        archive_rows = [{(r["card_id"], r["archive_id"]): r["relation"] for r in v["archive_pairs"]} for v in reviews]
        pairs = [{tuple(sorted((r["left"], r["right"]))): r["relation"] for r in v["candidate_pairs"]} for v in reviews]
        qualified, uncertainty_eligible, qualification = set(), set(), {}
        resources = {r["id"]: r["available"] for r in self.case(cid)["resources"]}
        for card in packet["cards"]:
            cardid = card["card_id"]
            raw = card["declared_card"]
            structural = card["structurally_valid_unit"] and isinstance(raw, dict) and chains[private[cardid]["condition"]]["valid"]
            available = structural and all(resources.get(r, False) for r in raw["resources"])
            axes = [rows[cardid][axis] for rows in card_rows for axis in AXES]
            archive_relations = [rows[(cardid, archive["id"])] for rows in archive_rows for archive in packet["archive"]]
            if available and all(v is True for v in axes) and all(v == "distinct" for v in archive_relations):
                qualified.add(cardid)
            if available and not any(v is False for v in axes) and "equivalent" not in archive_relations:
                uncertainty_eligible.add(cardid)
            qualification[cardid] = {"structural_chain_valid": structural, "resources_available": available,
                                     "axes": axes, "archive_relations": archive_relations,
                                     "qualified": cardid in qualified, "uncertainty_eligible": cardid in uncertainty_eligible}
            for axis in AXES:
                if card_rows[0][cardid][axis] != card_rows[1][cardid][axis]:
                    report["disagreements"].append({"type": "axis", "card_id": cardid, "axis": axis, "values": [rows[cardid][axis] for rows in card_rows]})
            for archive in packet["archive"]:
                key = (cardid, archive["id"])
                if archive_rows[0][key] != archive_rows[1][key]:
                    report["disagreements"].append({"type": "archive", "card_id": cardid, "archive_id": archive["id"], "values": [rows[key] for rows in archive_rows]})
        for pair in pairs[0]:
            if pairs[0][pair] != pairs[1][pair]:
                report["disagreements"].append({"type": "candidate_pair", "pair": list(pair), "values": [p[pair] for p in pairs]})
        for condition in CONDITIONS:
            if chains[condition]["valid"]:
                counts[condition]["qualified"] = sum(c in qualified for c in by_condition[condition])
                counts[condition]["uncertainty_eligible"] = sum(c in uncertainty_eligible for c in by_condition[condition])
        for recipe, parents in PARENTS.items():
            relevant = ("O", *parents, recipe)
            all_valid = all(chains[c]["valid"] for c in relevant)
            row = {"comparators": list(relevant), "all_four_chains_valid": all_valid,
                   "comparator_raw_cards": {c: by_condition[c] for c in relevant}, "composition_adds": None, "qualified_additions": None, "card_addition_assessments": []}
            if not all_valid:
                row["reason"] = "invalid/missing comparator or recipe chain; null does not mean zero"
            else:
                comparator_cards = [card for c in relevant[:-1] for card in by_condition[c]]
                assessments = []
                for candidate in by_condition[recipe]:
                    relations = []
                    for comparator in comparator_cards:
                        pair = tuple(sorted((candidate, comparator)))
                        values = [p[pair] for p in pairs]
                        relation = "equivalent" if "equivalent" in values else ("distinct" if values == ["distinct", "distinct"] else "unknown")
                        relations.append({"comparator_card": comparator, "reviewer_relations": values, "relation": relation})
                    if candidate not in uncertainty_eligible:
                        addition, reason = False, "explicit qualification failure: invalid chain/resources, false axis or equivalent archive"
                    elif any(r["relation"] == "equivalent" for r in relations):
                        addition, reason = False, "a reviewer marks a relevant raw comparator card equivalent"
                    elif candidate not in qualified:
                        addition, reason = None, "unresolved axes or archive qualification"
                    elif any(r["relation"] == "unknown" for r in relations):
                        addition, reason = None, "unresolved comparator distinction"
                    else:
                        addition, reason = True, "both reviewers qualify and distinguish every relevant raw comparator"
                    assessments.append(addition)
                    row["card_addition_assessments"].append({"card_id": candidate, "qualified": candidate in qualified,
                                                           "uncertainty_eligible": candidate in uncertainty_eligible,
                                                           "qualification": qualification[candidate], "adds": addition, "reason": reason, "pairs": relations})
                row["composition_adds"] = True if True in assessments else (None if None in assessments else False)
                row["qualified_additions"] = None if None in assessments else sum(a is True for a in assessments)
                row["reason"] = "valid zero repertoire is zero; comparison covers every raw card in all three comparator arms"
            report["recipes"][recipe] = row
        return report

    def verify(self, complete=True):
        self.integrity()
        statuses = {}
        handles = set()
        for job in self.plan()["jobs"]:
            jid = job["job_id"]
            state = self.status(jid)
            statuses[jid] = state["disposition"]
            if complete:
                require(state["terminal"], "all 132 slots must close: " + jid)
            if state["disposition"] in ("admitted", "spawned", "finished"):
                self.reconstruct(jid)
            if state["terminal"]:
                self.checked_terminal(jid)
            if state["disposition"] == "finished":
                spawn = self.load("receipts/jobs/" + jid + ".spawned.json")
                require(spawn["handle"] not in handles, "native handle reused")
                handles.add(spawn["handle"])
                witness = self.load("receipts/jobs/" + jid + ".witness.json")
                validate_native_witness(witness, spawn["handle"])
                require(sha(self.p("receipts/jobs/" + jid + ".witness.json")) == state["receipt"]["witness_sha256"], "witness drift")
                if state["receipt"]["output_sha256"] is not None:
                    require(self.p("receipts/raw/" + jid + ".first.bin").read_bytes() == self.output(jid).read_bytes(), "first observed raw snapshot drift")
                if job["role"] == "review":
                    require(state["receipt"]["review_lock"] is True, "terminal review lock missing")
                # Revalidate locks without changing an invalid assessment or repairing it.
                valid = False
                if self.output(jid).is_file():
                    try:
                        self.validation(job, read_json(self.output(jid)))
                        valid = True
                    except (GuardError, json.JSONDecodeError, UnicodeDecodeError, TypeError, KeyError):
                        pass
                require(valid == state["valid"], "locked structural disposition changed")
        if complete:
            require(all(self.status(cid + "-review" + str(i))["disposition"] == "finished" for cid in CASES for i in (1, 2)), "four actual terminal review locks required")
        return {"verified": True, "complete": complete, "planned_slots": 132, "terminal_final_calls": len(handles), "statuses": statuses,
                "claim_ceiling": "filesystem closure and coordinator-observed native witnesses; no global originality, benefit, equal compute or canonical efficacy"}

    def report(self):
        with self.controller():
            verification = self.verify()
            case_reports = {cid: self.score_case(cid) for cid in CASES}
            jobs = self.plan()["jobs"]
            statuses = {j["job_id"]: self.status(j["job_id"]) for j in jobs}
            recipes = {}
            for recipe in PARENTS:
                per_case = {cid: case_reports[cid]["recipes"][recipe] for cid in CASES}
                valid = all(case_reports[cid]["both_review_locks_valid"] and per_case[cid]["all_four_chains_valid"] for cid in CASES)
                adds = [per_case[cid]["composition_adds"] for cid in CASES]
                recipes[recipe] = {"both_cases_assessable": valid, "case_additions": dict(zip(CASES, adds)),
                                   "adds_in_both_cases": (all(v is True for v in adds) if valid and all(v is not None for v in adds) else None)}
            report = {"classification": "exploratory_synthetic_source_bound_native_study", "profile": PROFILE,
                      "protocol_complete": True, "planned_scored_slots": 132, "maximum_total_native_calls": 143,
                      "actual_scored_spawned": sum(s["disposition"] == "finished" for s in statuses.values()),
                      "actual_scored_terminal_final": verification["terminal_final_calls"], "gated": sum(s["disposition"] == "gated" for s in statuses.values()),
                      "valid_outputs": sum(s["valid"] for s in statuses.values()), "case_reports": case_reports, "recipes": recipes,
                      "generation_coverage": {cid: {c: case_reports[cid]["chains"][c] for c in CONDITIONS} for cid in CASES},
                      "job_accounting": {}, "all_dispositions": {jid: s.get("receipt") for jid, s in statuses.items()},
                      "tokens": None, "cost": None, "context_compute_claim": "caps are matched, exact words differ; no equal-compute claim",
                      "interpretation_ceiling": "synthetic source-bound operations and independent local archive/comparator judgments only; no global originality, observed benefit or canonical whole-skill efficacy",
                      "composition_repertoire_limit": "addition is judged against final builder repertoires only, with one card opportunity per arm; stage1/stage2 latent content is outside this numerical comparison and needs a separate completion audit",
                      "evidence_limit": "actual spawn and FINAL rest on coordinator observations; first parent-observed bytes locked, unobserved pre-FINAL overwrite cannot be certified absent"}
            for jid, state in statuses.items():
                if state["disposition"] == "finished":
                    admitted = self.load("receipts/jobs/" + jid + ".admitted.json")
                    report["job_accounting"][jid] = {k: admitted[k] for k in ("input_normalized_json_words", "literal_words", "supplement_words")}
                    report["job_accounting"][jid].update({k: state["receipt"][k] for k in ("normalized_json_words", "literal_output_words", "output_bytes", "worker_create_exclusive_reported")})
            artifact = self.save("reports/report.json", report)
            self.record("report", [artifact], actual_scored_terminal_final=verification["terminal_final_calls"])
            return {"report": artifact, "actual_scored_terminal_final": verification["terminal_final_calls"], "gated": report["gated"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "ready", "report"):
        commands.add_parser(command)
    item = commands.add_parser("status")
    item.add_argument("job", nargs="?")
    item = commands.add_parser("verify")
    item.add_argument("--partial", action="store_true")
    item = commands.add_parser("freeze")
    for name in ("prelaunch", "prelaunch-witness", "capacity-receipt", "capacity-witness"):
        item.add_argument("--" + name)
    for command in ("start", "spawned", "finish", "gate"):
        item = commands.add_parser(command)
        item.add_argument("job")
        if command == "spawned":
            item.add_argument("handle")
        if command == "finish":
            item.add_argument("witness", help="JSON path with actual coordinator-observed FINAL")
    args = parser.parse_args(argv)
    runtime = Runtime(args.root)
    try:
        if args.command == "freeze":
            result = runtime.freeze(args.prelaunch, args.prelaunch_witness, args.capacity_receipt, args.capacity_witness)
        elif args.command == "verify":
            result = runtime.verify(not args.partial)
        elif args.command == "spawned":
            result = runtime.spawned(args.job, args.handle)
        elif args.command == "finish":
            result = runtime.finish(args.job, read_json(args.witness))
        elif args.command in ("start", "gate", "status"):
            result = getattr(runtime, args.command)(args.job)
        else:
            result = getattr(runtime, args.command)()
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (GuardError, FileExistsError, FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error), "command": args.command}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
