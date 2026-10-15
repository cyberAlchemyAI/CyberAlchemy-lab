"""Prospective I11 native mechanics. Import and pure helpers admit no scored work.

All mutation entry points require a new exact freeze and independent admission.
Host start/FINAL witnesses are explicit inputs, never inferred from saved files.
The frozen raw builder is reused with private function globals; old loaders and
files remain untouched. No compression, post review, or scalar turn is exposed.
"""
from pathlib import Path
from types import FunctionType, SimpleNamespace
import copy
import hashlib
import json

import generation_runtime_v2 as g
import blind_generation_v2 as b
import blind_generation_raw_first as raw
import generation_disputes_v2 as disputes
import generation_review_validation_v2 as v
import generation_review_validation_raw_first as rv

R = Path(__file__).resolve().parents[1]
VERSION = "composition-I11-native-v3"
SCHEDULE = "composition-i11-schedule.draft-v2.json"
REVIEWS = "composition-i11-reviews.draft-v2.json"
PACK = "receipts/I11-native-repair-author-inputs.v3.json"
AUTHOR_PROMPT = "prompts/I11-native-repair-author.v3.txt"
BUDGET = "receipts/I11-composition-preparation-budget.v2.json"
CODE = "tools/composition_i11_runtime_v3.py"
TESTS = "tools/test_composition_i11_runtime_v3.py"
CHECK = "reports/I11-native-runtime-preparation-code-check.v3.json"
FREEZE = "freeze-I11-native.v3.json"
INDEPENDENT = "reports/I11-native-independent-prelaunch.v3.json"
CAPACITY = "reviews/composition-capacity/I11-maximal-raw-v2.json"
CAPACITY_VALIDATION = "reports/I11-maximal-native-capacity-validation.v2.json"
ADMISSION = "receipts/gates/I11-composition-native-admission.v3.json"
REVIEW_PROMPT = "prompts/generation-review-raw-first.txt"
CASES = ("H-P", "A-P", "H-C1", "H-C2", "A-C1", "A-C2")
ARMS = ("000", "001", "010", "011", "100", "101", "110", "111", "G")
TERMINAL = {"valid", "invalid", "missing", "skipped"}
MAX_COUNTS = {"raw_rows": 54, "archive_pairs": 216, "candidate_pairs": 1431,
              "post_rows": 0, "retention_rows": 0, "lineage_rows": 54,
              "addition_rows": 0, "attack_rows": 8, "contradiction_rows": 0,
              "unit_rows": 27}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def json_text(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON object key: " + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError("non-JSON numeric constant: " + value)
    return json.loads(text, object_pairs_hook=unique, parse_constant=constant)


def read(path):
    return json_text(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(value):
    return (isinstance(value, str) and bool(value) and not Path(value).is_absolute()
            and ".." not in Path(value).parts and str(Path(value)) == value)


def save_new(path, value):
    """Exclusive first save; used only by admitted runtime or final code report."""
    path = Path(path)
    data = value if isinstance(value, bytes) else (json.dumps(value, indent=2,
        ensure_ascii=False, allow_nan=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def bindings_valid(bindings, root=R):
    require(isinstance(bindings, list) and bool(bindings), "nonempty source bindings")
    paths = []
    for item in bindings:
        require(isinstance(item, dict) and set(item) == {"path", "sha256"}, "exact binding fields")
        path, digest = item["path"], item["sha256"]
        require(relative(path) and isinstance(digest, str) and len(digest) == 64
                and all(c in "0123456789abcdef" for c in digest), "typed normalized binding")
        require(sha(Path(root) / path) == digest, "source hash drift: " + path)
        paths.append(path)
    require(len(paths) == len(set(paths)), "unique source bindings")


def bindings(paths, root=R):
    return [{"path": p, "sha256": sha(Path(root) / p)} for p in sorted(set(paths))]


def schedules(root=R):
    schedule, reviews = read(Path(root) / SCHEDULE), read(Path(root) / REVIEWS)
    validate_schedule(schedule, reviews)
    return schedule, reviews


def validate_schedule(schedule, reviews):
    jobs, judges = schedule.get("jobs"), reviews.get("jobs")
    require(isinstance(jobs, list) and len(jobs) == 162, "all 162 raw jobs")
    index = 401
    for case in CASES:
        for arm in ARMS:
            prior = []
            for stage in (1, 2, 3):
                j = jobs[index - 401]
                operation = ("generic" if arm == "G" else
                    ("necessity", "construction", "conversion")[stage - 1] if arm[stage - 1] == "1" else "ordinary")
                expected = {"job_id": f"G{index:04d}", "study_id": "I11", "case_id": case,
                    "phase": "pilot" if case.endswith("-P") else "confirmation", "role": "raw",
                    "arm": arm, "stage": stage, "operation": operation,
                    "prompt_ref": f"prompts/composition-i11-draft-v2/I11-{arm}-S{stage}.txt",
                    "output_ref": f"outputs/composition/G{index:04d}.json",
                    "input_refs": [f"cases/{case}.json", *[p["output_ref"] for p in prior]],
                    "depends_on": [p["job_id"] for p in prior],
                    "requires_gates": ["I11-composition-native-admission"] +
                        ([] if case.endswith("-P") else ["I11-pilot-lock"]),
                    "maximum_current_openings": 2, "soft_saved_word_limit": 420}
                require(isinstance(j, dict) and j == expected and
                        all(type(j[k]) is int for k in ("stage", "maximum_current_openings", "soft_saved_word_limit")),
                        "exact scheduled role/stage/prior/budget: " + expected["job_id"])
                prior.append(j)
                index += 1
    require(isinstance(judges, list) and len(judges) == 12, "all 12 raw reviews")
    for i, case in enumerate(CASES):
        for n in (1, 2):
            j = judges[2 * i + n - 1]
            expected = {"job_id": f"RF-R-I11-{case}-{n}", "study_id": "I11", "case_id": case,
                "phase": "pilot" if case.endswith("-P") else "confirmation", "review_phase": "raw",
                "depends_on": [x["job_id"] for x in jobs if x["case_id"] == case],
                "output_ref": f"reviews/composition/RF-R-I11-{case}-{n}.json", "soft_saved_word_limit": 30000}
            require(isinstance(j, dict) and j == expected and type(j["soft_saved_word_limit"]) is int,
                    "exact raw review schedule/coverage/budget")


def source_paths(root=R, include_independent=True, capacity_bindings=()):
    """Dynamic exact freeze union; admission is separate to avoid hash cycles."""
    pack = read(Path(root) / PACK)
    schedule, reviews = schedules(root)
    outputs = {j["output_ref"] for j in schedule["jobs"]}
    result = {x["path"] for x in pack["source_bindings"]}
    result.update({PACK, AUTHOR_PROMPT, CODE, TESTS, CHECK, CAPACITY, CAPACITY_VALIDATION,
                   SCHEDULE, REVIEWS, BUDGET, REVIEW_PROMPT})
    result.update(x["path"] for x in capacity_bindings)
    for j in schedule["jobs"]:
        result.add(j["prompt_ref"])
        result.update(p for p in j["input_refs"] if p not in outputs)
    for j in reviews["jobs"]:
        if "prompt_ref" in j:
            result.add(j["prompt_ref"])
    if include_independent:
        result.add(INDEPENDENT)
    require(all(relative(p) for p in result), "normalized required source paths")
    return result


def ready(root=R):
    """No authoring report or predecessor gate can grant admission.

    Capacity validation must bind the actual fresh capacity FINAL and full review.
    Independent prelaunch must bind every audited source except its own receipt.
    Parent writes these prospective receipts only after separate independent work.
    """
    root = Path(root)
    original = read(root / PACK)["source_bindings"]
    bindings_valid(original, root)
    budget = read(root / BUDGET)
    require(budget["scored_retries"] == 0 and budget["review_saved_word_soft_limit"] == 30000
            and budget["preparation_native_call_maximum"] == 6, "equal I11 budget and zero retries")
    manifest = read(root / FREEZE)
    files = manifest.get("files")
    bindings_valid(files, root)
    capacity = read(root / CAPACITY_VALIDATION)
    bindings_valid(capacity.get("source_bindings"), root)
    capacity_sources = {x["path"]: x["sha256"] for x in capacity["source_bindings"]}
    require(capacity.get("classification") == "pass"
            and capacity_sources.get(CAPACITY) == sha(root / CAPACITY)
            and type(capacity.get("expected_rows")) is int and capacity["expected_rows"] == 1790
            and capacity.get("native_fixture_structural_validation", {}).get("valid") is True
            and capacity["native_fixture_structural_validation"].get("output_sha256") == sha(root / CAPACITY)
            and type(capacity.get("actual_native_starts")) is int and capacity["actual_native_starts"] == 1
            and type(capacity.get("actual_native_terminal_joins")) is int and capacity["actual_native_terminal_joins"] == 1
            and capacity.get("saved_word_soft_limit") == 30000,
            "actual maximal native capacity and parent validation required")
    require({x["path"] for x in files} == source_paths(root, capacity_bindings=capacity["source_bindings"]),
            "exact new I11 source freeze including capacity evidence")
    # Future admission verifies actual observed preparation events. This is not
    # called in authoring and is never replaced by an output-presence inference.
    log = [json_text(line) for line in (root / "receipts/events.jsonl").read_text().splitlines() if line.strip()]
    starts = [e for e in log if e.get("job_id") == "CAP-I11-MAXIMAL-RAW" and e.get("event_kind") == "native_spawn"]
    joins = [e for e in log if e.get("job_id") == "CAP-I11-MAXIMAL-RAW" and e.get("event_kind") == "preparation_terminal_join"]
    require(len(starts) == len(joins) == 1 and starts[0].get("host_spawn_observed") is True
            and starts[0].get("fresh_context") is True and joins[0].get("terminal_observed") is True
            and joins[0].get("terminal_witness") == "parent_received_NATIVE_FINAL_ANSWER"
            and joins[0].get("agent_handle") == starts[0].get("agent_handle")
            and isinstance(joins[0].get("agent_handle"), str) and bool(joins[0]["agent_handle"])
            and joins[0].get("output_ref") == CAPACITY
            and joins[0].get("validation", {}).get("output_sha256") == sha(root / CAPACITY),
            "actual fresh maximal capacity native start/FINAL required")
    independent = read(root / INDEPENDENT)
    require(independent.get("classification") == "independent_prelaunch_pass"
            and independent.get("independent_native_final_observed") is True
            and isinstance(independent.get("independent_agent_handle"), str)
            and bool(independent["independent_agent_handle"]), "separate independent prelaunch pass required")
    bindings_valid(independent.get("source_bindings"), root)
    require({x["path"] for x in independent["source_bindings"]} ==
            source_paths(root, False, capacity["source_bindings"]),
            "independent exact audited source coverage")
    gate = read(root / ADMISSION)
    require(gate.get("status") == "pass" and gate.get("freeze_sha256") == sha(root / FREEZE)
            and gate.get("independent_prelaunch_sha256") == sha(root / INDEPENDENT)
            and gate.get("capacity_validation_sha256") == sha(root / CAPACITY_VALIDATION),
            "separate exact new native admission gate required")
    return {"freeze_sha256": sha(root / FREEZE), "sources": files}


def field_paths(value, prefix=""):
    result = set()
    if isinstance(value, dict):
        for k, child in value.items():
            path = prefix + "." + k if prefix else k
            result.add(path)
            result.update(field_paths(child, path))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            path = prefix + f"[{i}]"
            result.add(path)
            result.update(field_paths(child, path))
    return result


def strings(value, nonempty=False):
    return (isinstance(value, list) and all(isinstance(x, str) and (bool(x.strip()) or not nonempty)
            for x in value) and len(value) == len(set(value)))


def validate_generation(job, body, case, priors):
    """Pure typed generation/lineage/attack validation; no semantic judgment."""
    errors = []
    def need(ok, message):
        if not ok:
            errors.append(message)
    construction = job.get("operation") == "construction"
    keys = {"case_id", "role", "openings", "assessment", "lineage"} | ({"attacks"} if construction else set())
    if not isinstance(body, dict):
        return {"valid": False, "errors": ["artifact object required"], "semantic_validity": "not asserted"}
    need(set(body) == keys, "exact artifact fields")
    need(isinstance(body.get("case_id"), str) and body.get("case_id") == job["case_id"], "exact typed case ID")
    need(body.get("role") == "raw", "exact raw role; no D")
    need(isinstance(body.get("assessment"), str) and bool(body.get("assessment", "").strip()), "assessment/reason string")
    need(isinstance(priors, dict) and set(priors) == set(job["depends_on"]), "all assigned earlier stage artifacts")
    prior = set()
    if isinstance(priors, dict):
        for producer, artifact in priors.items():
            if not isinstance(producer, str) or producer not in job["depends_on"]:
                need(False, "exact typed assigned prior producer")
                continue
            values = artifact.get("openings") if isinstance(artifact, dict) else None
            need(isinstance(values, list), "prior openings list")
            seen = []
            for item in values if isinstance(values, list) else []:
                local = item.get("id") if isinstance(item, dict) else None
                need(isinstance(local, str) and local in {"R1", "R2"}, "known prior R1/R2 IDs")
                if isinstance(local, str):
                    seen.append(local)
                    prior.add(producer + ":" + local)
            need(len(seen) <= 2 and len(seen) == len(set(seen)), "prior unique cap2")
    openings, lineage = body.get("openings"), body.get("lineage")
    need(isinstance(openings, list) and len(openings) <= 2, "opening list cap2")
    need(isinstance(lineage, list), "lineage list")
    current = []
    known = prior | field_paths(case)
    opening_keys = {"id", "kind", "claim", "delta", "prediction", "probe", "fit", "assumptions", "source_refs"}
    for item in openings if isinstance(openings, list) else []:
        if not isinstance(item, dict):
            need(False, "typed opening object")
            continue
        need(set(item) == opening_keys, "exact opening fields")
        local = item.get("id")
        need(isinstance(local, str) and local in {"R1", "R2"}, "known local R1/R2")
        if isinstance(local, str):
            current.append(local)
        need(item.get("kind") in ("mechanism", "hypothesis", "question"), "kind enum")
        need(item.get("fit") in ("preserves", "uncertain", "conditional", "violates"), "fit enum")
        for f in ("claim", "delta", "prediction", "probe"):
            need(isinstance(item.get(f), str) and bool(item.get(f, "").strip()), "string field " + f)
        need(strings(item.get("assumptions")), "unique assumptions string list")
        refs = item.get("source_refs")
        need(strings(refs, True) and bool(refs), "nonempty unique source_refs")
        if strings(refs):
            need(set(refs) <= known, "only exact case fields or assigned G-qualified sources")
    need(len(current) == len(set(current)), "unique current R1/R2")
    seen = []
    for item in lineage if isinstance(lineage, list) else []:
        if not isinstance(item, dict):
            need(False, "typed lineage object")
            continue
        need(set(item) == {"source_id", "disposition", "target_ids", "reason"}, "exact lineage fields")
        source = item.get("source_id")
        need(isinstance(source, str) and source in prior, "assigned qualified lineage source")
        if isinstance(source, str):
            seen.append(source)
        disposition, targets = item.get("disposition"), item.get("target_ids")
        need(disposition in ("retained", "changed", "merged", "parked", "rejected"), "lineage disposition")
        need(isinstance(item.get("reason"), str) and bool(item.get("reason", "").strip()), "lineage reason")
        need(strings(targets, True), "unique typed lineage targets")
        if strings(targets):
            need(set(targets) <= set(current), "existing current targets")
            if disposition in ("retained", "changed"):
                need(len(targets) == 1, "retained/changed exactly one target")
            if disposition == "merged":
                need(bool(targets), "merged nonempty targets")
            if disposition in ("parked", "rejected"):
                need(not targets, "park/reject zero targets")
    need(len(seen) == len(set(seen)) and set(seen) == prior, "exact all-earlier-stage unique lineage coverage")
    if construction:
        attacks = body.get("attacks")
        need(isinstance(attacks, list) and len(attacks) <= 2, "construction attacks list cap2")
        seen_attacks = []
        for item in attacks if isinstance(attacks, list) else []:
            if not isinstance(item, dict):
                need(False, "typed attack object")
                continue
            need(set(item) == {"attack_id", "dependency", "source_refs", "linked_opening_ids", "disposition"}, "exact attack fields")
            ident = item.get("attack_id")
            need(isinstance(ident, str) and ident in {"A1", "A2"}, "known A1/A2 attack")
            if isinstance(ident, str):
                seen_attacks.append(ident)
            need(isinstance(item.get("dependency"), str) and bool(item.get("dependency", "").strip()), "attack dependency")
            refs, targets, disposition = item.get("source_refs"), item.get("linked_opening_ids"), item.get("disposition")
            need(strings(refs, True) and bool(refs), "nonempty unique attack source_refs")
            if strings(refs):
                need(set(refs) <= prior, "assigned qualified prior attack sources")
            need(strings(targets, True), "unique typed attack targets")
            need(disposition in ("replacement", "removal", "test", "no_branch"), "construction disposition; no critique")
            if strings(targets):
                need(set(targets) <= set(current), "existing construction targets")
                need(not targets if disposition == "no_branch" else bool(targets), "no_branch empty; other attacks linked")
        need(len(seen_attacks) == len(set(seen_attacks)), "unique attack IDs")
    return {"valid": not errors, "errors": errors, "semantic_validity": "not asserted by structural validation"}


def load_inputs(root=R):
    root = Path(root)
    schedule, reviews = schedules(root)
    return (schedule, reviews, read(root / "generation-review-contract.v2.json"),
            read(root / "criteria-generation.v2.json"), read(root / "archives/case-archives.json"))


def build_raw_case(case, artifacts, dispositions, root=R, inputs=None):
    """Frozen build_raw with custom tuple and isolated canonical-path adaptation.

    Frozen build_packet hardcodes two binding filenames. Only its private copy
    sees a path adapter; returned metadata is relabeled to the actual I11 paths.
    Neither b/f/g loaders nor any other original module global is mutated.
    """
    root = Path(root)
    inputs = inputs if inputs is not None else load_inputs(root)
    mapped = {"generation-schedule.v2.json": SCHEDULE, "generation-review-schedule.v2.json": REVIEWS}
    class BuilderRoot:
        def __truediv__(self, key):
            return root / mapped.get(str(key), str(key))
    adapter = BuilderRoot()
    def builder_path(value):
        return adapter if value is adapter or value == root else Path(value)
    local_globals = dict(b.build_packet.__globals__, Path=builder_path, read=read)
    private_builder = FunctionType(b.build_packet.__code__, local_globals, b.build_packet.__name__, b.build_packet.__defaults__)
    private_base = SimpleNamespace(**{**vars(b), "build_packet": private_builder})
    private_raw = FunctionType(raw.build_raw.__code__, dict(raw.build_raw.__globals__, base=private_base),
                               raw.build_raw.__name__, raw.build_raw.__defaults__)
    packet, admin = private_raw("I11", case, artifacts, dispositions, adapter, inputs)
    for item in admin["input_bindings"]:
        item["path"] = mapped.get(item["path"], item["path"])
    require(len(admin["input_bindings"]) == len({x["path"] for x in admin["input_bindings"]}), "unique actual builder bindings")
    admin["version"] = VERSION + "-mapping"
    return packet, admin


def state_from_events(jobs, events):
    result = {k: "pending" for k in jobs}
    transitions = {"job_prepared": ("pending", "ready"), "native_spawn": ("ready", "running"),
                   "dependency_disposition": ("pending", "skipped")}
    for event in events:
        if event.get("runtime_version") != VERSION or event.get("job_id") not in result:
            continue
        key, kind = event["job_id"], event["event_kind"]
        if kind == "native_terminal_join":
            require(result[key] == "running", "one native join after one start")
            require(event.get("terminal_observed") is True and event.get("terminal_witness") ==
                    "parent_received_NATIVE_FINAL_ANSWER", "actual native FINAL required")
            execution = event.get("execution")
            require(execution in {"valid", "invalid", "missing"}, "explicit terminal execution")
            result[key] = execution
        elif kind in transitions:
            before, after = transitions[kind]
            require(result[key] == before, "zero retries/unique native state transition")
            result[key] = after
    return result


def coverage(jobs, events, artifacts=None, locked=None):
    states = state_from_events(jobs, events)
    starts = [e for e in events if e.get("runtime_version") == VERSION and e.get("event_kind") == "native_spawn" and e.get("job_id") in jobs]
    return {"planned": len(jobs), "actual_native_starts": len(starts),
            **{state: sum(x == state for x in states.values()) for state in ("pending", "ready", "running", "valid", "invalid", "missing", "skipped")},
            "empty_valid": sum(states[k] == "valid" and isinstance(body, dict) and body.get("openings") == []
                               for k, body in (artifacts or {}).items() if k in states),
            "null_semantic_fields": sum(value is None for row in (locked or {}).get("rows", [])
                                         for field, value in row["values"].items() if field in row["field_status"])}


def events():
    ready()
    return [json_text(line) for line in (R / "receipts/events.jsonl").read_text().splitlines() if line.strip()]


def all_jobs():
    schedule, reviews = schedules()
    return {j["job_id"]: j for j in [*schedule["jobs"], *reviews["jobs"]]}


def status(log=None):
    return state_from_events(all_jobs(), events() if log is None else log)


def latest(log, key, kind):
    matches = [e for e in log if e.get("runtime_version") == VERSION and e.get("job_id") == key and e.get("event_kind") == kind]
    require(len(matches) == 1, "exact unique " + kind + " receipt")
    return matches[0]


def emit(body):
    freeze = ready()
    return g.event({**body, "runtime_version": VERSION, "study_id": "I11", "source_freeze_sha256": freeze["freeze_sha256"]})


def verify_prepared(prepared):
    current = ready()
    require(prepared["source_freeze_sha256"] == current["freeze_sha256"], "prepared freeze drift")
    bindings_valid(prepared["input_bindings"])
    require(sha(R / prepared["prompt_ref"]) == prepared["prompt_sha256"], "prepared prompt drift")


def packet_ref(case, kind):
    bases = {"packet": "fixtures/composition-i11", "map": "receipts/composition-i11-maps",
             "lock": "reports/composition-i11-locked"}
    return f"{bases[kind]}/I11-{case}-raw.json"


def phase_gate(job, log):
    if job["phase"] != "confirmation":
        return
    path = "receipts/gates/I11-pilot-lock.json"
    gate = read(R / path)
    policy = next(x for x in read(R / "inputs/plan/portfolio.json")["studies"] if x["id"] == "I11")
    require(gate.get("status") in {"pass", "stop"} and type(gate.get("confirmation_allowed")) is bool
            and gate.get("decision_status") in policy["decision_statuses"]
            and gate.get("policy_source_sha256") == sha(R / "inputs/plan/portfolio.json")
            and gate.get("failure_or_elimination") == policy["failure_or_elimination"], "original I11 pilot advancement policy")
    expected = {packet_ref(case, "lock") for case in CASES[:2]}
    bindings_valid(gate.get("pilot_lock_bindings"))
    require({x["path"] for x in gate["pilot_lock_bindings"]} == expected, "both exact pilot locks")
    for case in CASES[:2]:
        report, witness = bound_case(case, "lock", log)
        if gate["confirmation_allowed"]:
            require(report["independent_review_complete"] is True and witness["independent_review_complete"] is True,
                    "complete observed dual pilot raw review required")
    if gate["confirmation_allowed"]:
        require(gate["status"] == "pass" and gate["decision_status"] == "advance_screen", "original pilot advancement required")
        return None
    require(gate["decision_status"] != "advance_screen" and isinstance(gate.get("reason"), str)
            and bool(gate["reason"].strip()), "explicit original-policy nonadvancement reason")
    return "original_I11_pilot_policy_prevents_confirmation"


def generation_prepare(key):
    ready()
    job = all_jobs()[key]
    require(job.get("role") == "raw", "scheduled I11 generation only")
    log = events()
    states = status(log)
    require(states[key] == "pending", "first preparation only")
    phase_skip = phase_gate(job, log)
    if phase_skip:
        return emit({"event_kind": "dependency_disposition", "job_id": key, "case_id": job["case_id"],
            "phase": job["phase"], "status": "skipped", "cause": phase_skip,
            "pilot_gate_ref": "receipts/gates/I11-pilot-lock.json",
            "pilot_gate_sha256": sha(R / "receipts/gates/I11-pilot-lock.json"), "semantic_assessment": None})
    bad = [k for k in job["depends_on"] if states[k] in {"invalid", "missing", "skipped"}]
    if bad:
        return emit({"event_kind": "dependency_disposition", "job_id": key, "case_id": job["case_id"],
            "phase": job["phase"], "status": "skipped", "cause": "invalid_missing_or_skipped_prior_stage",
            "dependency_ids": bad, "semantic_assessment": None})
    require(all(states[k] == "valid" for k in job["depends_on"]), "all earlier same-arm stages terminal-valid")
    priors = {}
    for producer in job["depends_on"]:
        witness = latest(log, producer, "native_terminal_join")
        verify_prepared(latest(log, producer, "job_prepared"))
        source = all_jobs()[producer]["output_ref"]
        require(witness["validation"]["output_sha256"] == sha(R / source), "prior terminal output drift")
        priors[source] = producer
    output = R / job["output_ref"]
    require(not output.exists(), "first substantive generation save already exists")
    prompt = f"prompts/composition-i11-jobs/{key}.txt"
    text = (R / job["prompt_ref"]).read_text() + "\nExact job_id=" + key + "; role=raw; case_id=" + job["case_id"] + ".\n"
    text += "Exact prior artifact/job map: " + json.dumps(priors) + ".\n"
    text += "Read only this instruction and exact assigned inputs: " + ", ".join(str((R / p).resolve()) for p in job["input_refs"]) + ".\n"
    text += "Write first substantive JSON only " + str(output.resolve()) + ". Zero retries or overwrite. Final only artifact/hash.\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    save_new(R / prompt, text.encode())
    return emit({"event_kind": "job_prepared", "job_id": key, "phase": job["phase"], "case_id": job["case_id"],
        "input_bindings": bindings([*job["input_refs"], job["prompt_ref"], SCHEDULE, REVIEWS, BUDGET]),
        "prompt_ref": prompt, "prompt_sha256": sha(R / prompt), "output_ref": job["output_ref"]})


def start_valid(key, handle, witness, prepared, log):
    require(isinstance(handle, str) and bool(handle), "native handle required")
    require(isinstance(witness, dict) and witness.get("native_start_observed") is True
            and witness.get("fresh_context") is True and witness.get("turn") == 1
            and witness.get("job_id") == key and witness.get("agent_handle") == handle
            and witness.get("prompt_sha256") == prepared["prompt_sha256"]
            and witness.get("source_freeze_sha256") == prepared["source_freeze_sha256"]
            and isinstance(witness.get("native_call_id"), str) and bool(witness["native_call_id"]), "actual bound fresh native start witness")
    require(not any(e.get("runtime_version") == VERSION and e.get("event_kind") == "native_spawn" and
                    (e.get("agent_handle") == handle or e.get("native_call_id") == witness["native_call_id"]) for e in log),
            "distinct fresh native handles/calls; zero retries")


def spawn(key, handle, witness):
    ready()
    log, job = events(), all_jobs()[key]
    require(status(log)[key] == "ready", "prepared native start only")
    prepared = latest(log, key, "job_prepared")
    verify_prepared(prepared)
    require(not (R / prepared.get("opaque_output_ref", prepared["output_ref"])).exists(), "native start precedes first substantive save")
    start_valid(key, handle, witness, prepared, log)
    return emit({"event_kind": "native_spawn", "job_id": key, "case_id": job["case_id"],
                 "phase": job["phase"],
                 **({"review_phase": job["review_phase"]} if "review_phase" in job else {}),
                 "agent_handle": handle,
                 "native_call_id": witness["native_call_id"], "host_spawn_observed": True,
                 "fresh_context": True, "turn": 1, "prompt_sha256": prepared["prompt_sha256"],
                 "output_ref": prepared.get("opaque_output_ref", prepared["output_ref"])})


def final_valid(key, handle, witness, prepared, started, digest):
    require(isinstance(witness, dict) and witness.get("native_final_observed") is True
            and witness.get("terminal_witness") == "parent_received_NATIVE_FINAL_ANSWER"
            and witness.get("job_id") == key and witness.get("agent_handle") == handle == started["agent_handle"]
            and witness.get("native_call_id") == started["native_call_id"]
            and witness.get("prompt_sha256") == prepared["prompt_sha256"]
            and witness.get("source_freeze_sha256") == prepared["source_freeze_sha256"]
            and witness.get("output_ref") == prepared.get("opaque_output_ref", prepared["output_ref"])
            and "output_sha256" in witness and witness["output_sha256"] == digest,
            "actual source/prompt/output-bound native FINAL witness")


def join(key, handle, witness):
    ready()
    log, job = events(), all_jobs()[key]
    require(status(log)[key] == "running", "one observed join after native start")
    prepared, started = latest(log, key, "job_prepared"), latest(log, key, "native_spawn")
    verify_prepared(prepared)
    source = R / prepared.get("opaque_output_ref", prepared["output_ref"])
    digest = sha(source) if source.exists() else None
    final_valid(key, handle, witness, prepared, started, digest)
    try:
        body = read(source)
        if job.get("role") == "raw":
            prior = {k: read(R / all_jobs()[k]["output_ref"]) for k in job["depends_on"]}
            result = validate_generation(job, body, read(R / f"cases/{job['case_id']}.json"), prior)
        else:
            packet, _ = bound_case(job["case_id"], "packet", log)
            result = rv.validate_review(packet, body)
            if body.get("reviewer_id") != prepared["assigned_reviewer_id"]:
                result["valid"] = False
                result["errors"].append("assigned reviewer identity mismatch")
    except (OSError, ValueError, UnicodeError, TypeError, KeyError, AttributeError) as error:
        result = {"valid": False, "errors": ["missing/malformed/duplicate-key artifact: " + str(error)], "semantic_validity": "not asserted"}
    result.update(output_sha256=digest, saved_words=len(source.read_text(errors="replace").split()) if digest else None)
    execution = "missing" if digest is None else "valid" if result["valid"] else "invalid"
    if "opaque_output_ref" in prepared and digest is not None:
        save_new(R / prepared["output_ref"], source.read_bytes())
    return emit({"event_kind": "native_terminal_join", "job_id": key, "case_id": job["case_id"], "phase": job["phase"],
        "agent_handle": handle, "native_call_id": started["native_call_id"], "terminal_observed": True,
        "terminal_witness": "parent_received_NATIVE_FINAL_ANSWER", "prompt_sha256": prepared["prompt_sha256"],
        "execution": execution, "validation": result, "output_ref": prepared["output_ref"],
        "native_output_ref": prepared.get("opaque_output_ref", prepared["output_ref"]),
        "native_final_witness": copy.deepcopy(witness)})


def case_payload(case, log):
    jobs = {k: j for k, j in all_jobs().items() if j.get("role") == "raw" and j["case_id"] == case}
    states = status(log)
    require(len(jobs) == 27 and all(states[k] in TERMINAL for k in jobs), "all 27 raw units explicitly terminal")
    artifacts, dispositions, output_bindings = {}, {}, []
    for key, job in jobs.items():
        state, path = states[key], R / job["output_ref"]
        if state == "skipped":
            skipped = latest(log, key, "dependency_disposition")
            require(not path.exists(), "skipped unit cannot acquire an output")
            cause = skipped["cause"]
        else:
            terminal = latest(log, key, "native_terminal_join")
            prepared = latest(log, key, "job_prepared")
            verify_prepared(prepared)
            digest = terminal["validation"]["output_sha256"]
            require((digest is None and not path.exists()) or (path.exists() and sha(path) == digest), "terminal output drift/presence mismatch")
            started = latest(log, key, "native_spawn")
            final_valid(key, started["agent_handle"], terminal["native_final_witness"], prepared, started, digest)
            cause = "Observed native FINAL: " + state + "; no semantic validity asserted."
            if digest:
                output_bindings.append({"path": job["output_ref"], "sha256": digest})
                try:
                    artifacts[key] = read(path)
                except (ValueError, UnicodeError):
                    artifacts[key] = {"unparsed_text": path.read_text(errors="replace")}
        dispositions[key] = {"execution": state, "cause": cause}
    return artifacts, dispositions, output_bindings


def make_packet(case):
    ready()
    require(case in CASES, "scheduled case only")
    log = events()
    artifacts, dispositions, outputs = case_payload(case, log)
    packet, admin = build_raw_case(case, artifacts, dispositions)
    admin["input_bindings"] = list({x["path"]: x for x in [*admin["input_bindings"], *outputs,
                                         *bindings([BUDGET, CODE, TESTS, CHECK]) ]}.values())
    admin["disposition_coverage"] = coverage({k: all_jobs()[k] for k in dispositions}, log, artifacts)
    pr, mr = packet_ref(case, "packet"), packet_ref(case, "map")
    require(not (R / pr).exists() and not (R / mr).exists(), "first packet/map save only")
    save_new(R / mr, admin)
    save_new(R / pr, packet)
    return emit({"event_kind": "i11_raw_packet", "case_id": case, "packet_ref": pr, "packet_sha256": sha(R / pr),
                 "map_ref": mr, "map_sha256": sha(R / mr), "expected_rows": packet["expected_total_rows"]})


def bound_case(case, kind, log):
    ref = packet_ref(case, kind)
    event_kind = "i11_raw_lock" if kind == "lock" else "i11_raw_packet"
    witnesses = [e for e in log if e.get("runtime_version") == VERSION and e.get("event_kind") == event_kind and e.get("case_id") == case]
    require(len(witnesses) == 1, "one observed immutable case " + kind)
    witness = witnesses[0]
    field = "output" if kind == "lock" else kind
    require(witness[field + "_ref"] == ref and witness[field + "_sha256"] == sha(R / ref), "case artifact receipt hash drift")
    body = read(R / ref)
    if kind == "lock":
        bindings_valid(body["source_bindings"])
        require(body["independent_review_complete"] is witness["independent_review_complete"], "observed lock completeness binding")
    else:
        mr = packet_ref(case, "map")
        require(witness["map_ref"] == mr and witness["map_sha256"] == sha(R / mr), "administrative map receipt drift")
        bindings_valid(read(R / mr)["input_bindings"])
    return body, witness


def review_prepare(key):
    ready()
    job, log = all_jobs()[key], events()
    require(job.get("review_phase") == "raw" and status(log)[key] == "pending", "scheduled first raw review only")
    require(all(status(log)[k] in TERMINAL for k in job["depends_on"]), "all raw source dispositions required")
    packet, _ = bound_case(job["case_id"], "packet", log)
    reviewer = b.opaque("V", key)
    require(reviewer in packet["review_job_ids"], "exact opaque scheduled reviewer")
    blind = f"fixtures/composition-i11-opaque/{packet['packet_id']}.json"
    packet_path = R / packet_ref(job["case_id"], "packet")
    if (R / blind).exists():
        require(sha(R / blind) == sha(packet_path), "identical opaque packet only")
    else:
        save_new(R / blind, packet_path.read_bytes())
    opaque_out = f"reviews/composition-i11-opaque/{reviewer}.json"
    prompt = f"prompts/composition-i11-review-jobs/{reviewer}.txt"
    require(not (R / opaque_out).exists() and not (R / job["output_ref"]).exists(), "first review save only")
    text = (R / REVIEW_PROMPT).read_text().replace("Max6000 saved words soft", "Max30000 saved words soft")
    text += f"\nAssigned reviewer_id={reviewer}. Read only this instruction and exact packet {(R / blind).resolve()}.\n"
    text += f"Write first substantive JSON only {(R / opaque_out).resolve()}. Full coverage; zero retries or overwrite.\n"
    (R / opaque_out).parent.mkdir(parents=True, exist_ok=True)
    save_new(R / prompt, text.encode())
    admin = read(R / packet_ref(job["case_id"], "map"))
    inputs = list({x["path"]: x for x in [*admin["input_bindings"], *bindings([blind, REVIEW_PROMPT, BUDGET,
                    packet_ref(job["case_id"], "packet"), packet_ref(job["case_id"], "map")])]}.values())
    return emit({"event_kind": "job_prepared", "job_id": key, "case_id": job["case_id"], "phase": job["phase"],
        "input_bindings": inputs, "prompt_ref": prompt, "prompt_sha256": sha(R / prompt),
        "output_ref": job["output_ref"], "opaque_output_ref": opaque_out, "assigned_reviewer_id": reviewer,
        "expected_rows": packet["expected_total_rows"], "soft_saved_word_limit": 30000})


def reconcile_raw(packet, reviews, witnesses, starts):
    """Pure lock calculation after two distinct actual fresh native terminals."""
    require(len(reviews) == len(witnesses) == len(starts) == 2, "two raw reviewers required")
    require(len({e.get("agent_handle") for e in witnesses}) == 2, "distinct fresh review handles")
    require(len({e.get("native_call_id") for e in starts}) == 2, "distinct native review calls")
    for terminal, start in zip(witnesses, starts):
        require(terminal.get("terminal_observed") is True and terminal.get("terminal_witness") ==
                "parent_received_NATIVE_FINAL_ANSWER" and start.get("host_spawn_observed") is True
                and start.get("fresh_context") is True and start.get("turn") == 1
                and terminal.get("agent_handle") == start.get("agent_handle")
                and terminal.get("native_call_id") == start.get("native_call_id"), "actual fresh review FINAL witnesses")
    complete = all(w["validation"]["valid"] and rv.validate_review(packet, body)["valid"]
                   for w, body in zip(witnesses, reviews))
    if complete:
        require({body["reviewer_id"] for body in reviews} == set(packet["review_job_ids"]), "exact dual reviewer identity coverage")
        report = disputes.compare(packet, *reviews)
        for table, obligations in packet["expected_matrix"].items():
            unavailable = {ob["row_id"] for ob in obligations if ob["null_semantics"]}
            for row in report["rows"]:
                if row["table"] == table and row["row_id"] in unavailable:
                    row["field_status"] = {field: "unobservable" for field in row["field_status"]}
    else:
        rows = []
        for table, obligations in packet["expected_matrix"].items():
            for ob in obligations:
                values = {c: ob["identity"].get(c, ob["fixed_values"].get(c)) for c in packet["contract"]["columns"][table]}
                values["evidence"] = "Independent review invalid/unavailable; semantic judgments remain null."
                rows.append({"table": table, "row_id": ob["row_id"], "identity": ob["identity"], "values": values,
                    "field_status": {c: "unobservable" for c in values if c not in ob["identity"] and c not in ob["fixed_values"] and c != "evidence"}})
        report = {"case_packet_id": packet["packet_id"], "rows": rows, "disputes": [], "family_disagreements": []}
    report.update(independent_review_complete=complete, meaning_status="locked_source_bound_model_judgments" if complete else "gated_incomplete_review",
        raw_packet_sha256=raw.canonical_hash(packet), raw_packet_context_sha256=raw.raw_context_hash(packet),
        scalar_adjudication="unused_unless_separately_admitted", family_merge_credit=0,
        semantic_validity="source-bound model judgments only; parent supplies no semantic grade")
    return report


def lock(case):
    ready()
    log = events()
    selected = [j for j in all_jobs().values() if j.get("review_phase") == "raw" and j["case_id"] == case]
    require(len(selected) == 2 and all(status(log)[j["job_id"]] in {"valid", "invalid", "missing"} for j in selected), "two actual terminal raw reviews")
    packet, _ = bound_case(case, "packet", log)
    bodies, terminals, starts, sources = [], [], [], []
    for j in selected:
        key = j["job_id"]
        prepared = latest(log, key, "job_prepared")
        verify_prepared(prepared)
        terminal = latest(log, key, "native_terminal_join")
        start = latest(log, key, "native_spawn")
        path = R / j["output_ref"]
        digest = terminal["validation"]["output_sha256"]
        require((digest is None and not path.exists()) or (path.exists() and sha(path) == digest), "review terminal source drift")
        native_path = R / prepared["opaque_output_ref"]
        require((digest is None and not native_path.exists()) or
                (native_path.exists() and sha(native_path) == digest), "native opaque review output drift")
        final_valid(key, start["agent_handle"], terminal["native_final_witness"], prepared, start, digest)
        if digest:
            sources.append({"path": j["output_ref"], "sha256": digest})
            sources.append({"path": prepared["opaque_output_ref"], "sha256": digest})
        try:
            bodies.append(read(path))
        except (OSError, ValueError, UnicodeError):
            bodies.append(None)
        terminals.append(terminal)
        starts.append(start)
    report = reconcile_raw(packet, bodies, terminals, starts)
    admin = read(R / packet_ref(case, "map"))
    report.update(study_id="I11", case_id=case, review_phase="raw", source_bindings=list({x["path"]: x for x in
        [*admin["input_bindings"], *sources, *bindings([packet_ref(case, "packet"), packet_ref(case, "map"), BUDGET]) ]}.values()))
    artifacts, dispositions, _ = case_payload(case, log)
    report["disposition_coverage"] = coverage({k: all_jobs()[k] for k in dispositions}, log, artifacts, report)
    target = packet_ref(case, "lock")
    save_new(R / target, report)
    return emit({"event_kind": "i11_raw_lock", "case_id": case, "output_ref": target,
                 "output_sha256": sha(R / target), "independent_review_complete": report["independent_review_complete"]})
