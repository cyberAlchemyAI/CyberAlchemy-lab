#!/usr/bin/env python3
"""Compile or check the standalone relational-checker planning candidate."""
import argparse
import copy
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
SOURCE = BASE / "PLAN-SOURCE.json"
OUTPUT = BASE / "dag-plan"
BT = chr(96)
FENCE = BT * 3

def digest(data):
    return hashlib.sha256(data).hexdigest()

def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def analyze(source):
    require(source["schema"] == "relational-theorem-checker.plan-source/v1", "wrong source schema")
    tasks = source["tasks"]
    ids = [t["id"] for t in tasks]
    require(len(ids) == len(set(ids)), "duplicate task ID")
    require(all(re.fullmatch(r"[A-Z][0-9]{2}|G[0-4]", i) for i in ids), "unsafe task ID")
    index = {t["id"]: t for t in tasks}
    ranks, ancestors = {}, {}
    pending = set(ids)
    while pending:
        ready = sorted(i for i in pending if set(index[i]["depends_on"]) <= ranks.keys())
        require(ready, "missing prerequisite or dependency cycle")
        for i in ready:
            deps = index[i]["depends_on"]
            require(len(deps) == len(set(deps)), f"duplicate dependency: {i}")
            require(i not in deps, f"self dependency: {i}")
            ranks[i] = 0 if not deps else 1 + max(ranks[d] for d in deps)
            ancestors[i] = set(deps).union(*(ancestors[d] for d in deps))
            pending.remove(i)
    require(set(ids) - {"G4"} <= ancestors["G4"], "tasks orphaned from final gate")
    phase = source["entry_phase"]
    phase_ids = phase["task_ids"]
    require(phase_ids == ["P01", "P03", "P04", "P05"] and phase["exit_task"] == "P05",
            "formalization entry phase changed")
    require({i for i in ids if not index[i]["depends_on"]} == {phase_ids[0]},
            "formalization must be the unique first task")
    for before, after in zip(phase_ids, phase_ids[1:]):
        require(before in ancestors[after], "formalization steps are out of order")
    for i in set(ids) - set(phase_ids):
        require(phase["exit_task"] in ancestors[i], "task bypasses formalization review: " + i)
    layer_ids = {l["id"] for l in source["layers"]}
    swus, scopes = [], []
    for t in tasks:
        i = t["id"]
        require(t["layer"] in layer_ids, f"unknown layer: {i}")
        require(t["status"] in {"not-started", "accepted"}, f"unsupported task status: {i}")
        require(t["objective"] and t["outputs"] and t["ordered_rules"], f"incomplete task contract: {i}")
        require(t["acceptance_criteria"] and t["failure_controls"] and t["source_refs"], f"incomplete evidence contract: {i}")
        require(t["validation"]["id"] == "V-" + i, f"validation identity mismatch: {i}")
        require(t["validation"]["execution_status"] == t["status"], f"validation status mismatch: {i}")
        if t["status"] == "accepted":
            require(all(index[d]["status"] == "accepted" for d in t["depends_on"]), f"unaccepted predecessor: {i}")
            binding = t["validation"].get("acceptance_ref", {})
            path = binding.get("path", "")
            require(path.startswith(t["write_scope"]) and ".." not in Path(path).parts, f"acceptance scope escape: {i}")
            data = (ROOT / path).read_bytes()
            require(digest(data) == binding.get("sha256"), f"stale acceptance receipt: {i}")
            acceptance = json.loads(data)
            require(acceptance["schema"] == "relational.task-acceptance/v1" and acceptance["task_id"] == i and acceptance["result"] == "accepted", f"wrong acceptance receipt: {i}")
            require([c["criterion"] for c in acceptance["criteria"]] == t["acceptance_criteria"] and all(c["result"] == "pass" for c in acceptance["criteria"]), f"criterion acceptance mismatch: {i}")
            artifacts = {a["name"]:a for a in acceptance["artifacts"]}
            require(set(t["outputs"]) <= artifacts.keys(), f"missing accepted output: {i}")
            if i not in phase_ids:
                require(acceptance.get("review_mode") and acceptance.get("authority_effect") == "none", f"missing review boundary: {i}")
                require([c["control"] for c in acceptance.get("failure_controls", [])] == t["failure_controls"]
                        and all(c["result"] == "pass" for c in acceptance["failure_controls"]), f"failure controls not reviewed: {i}")
                dependencies = {(b["path"], b["sha256"]) for b in acceptance["dependency_bindings"]}
                require(all((index[d]["validation"]["acceptance_ref"]["path"], index[d]["validation"]["acceptance_ref"]["sha256"]) in dependencies
                            for d in t["depends_on"]), f"predecessor receipt not bound: {i}")
                require(all(a["path"].startswith(t["write_scope"]) for a in acceptance["artifacts"]), f"output scope escape: {i}")
                require(all(c.get("evidence") and c.get("finding") for c in acceptance["criteria"] + acceptance["failure_controls"]), f"empty acceptance findings: {i}")
            for a in acceptance["artifacts"] + acceptance["dependency_bindings"]:
                require(not Path(a["path"]).is_absolute() and ".." not in Path(a["path"]).parts, "accepted evidence path escape")
                require(digest((ROOT/a["path"]).read_bytes()) == a["sha256"], f"accepted evidence drift: {a['path']}")
        require(set(t["outputs"]) <= set(t["validation"]["required_evidence"]), f"output evidence omitted: {i}")
        require(t["working_units"], f"no working units: {i}")
        scope = t["write_scope"]
        require(scope.startswith("craft/formalization/candidates/relational-theorem-checker/v1/"), f"scope escape: {i}")
        require(scope.endswith("/") and ".." not in Path(scope).parts, f"unsafe scope: {i}")
        scopes.append(scope)
        for unit in t["working_units"]:
            require(unit["status"] == t["status"] and unit["exit_criteria"] and unit["acceptance_evidence"], f"incomplete or inconsistent SWU: {i}")
            swus.append(unit["id"])
    require(len(swus) == len(set(swus)), "duplicate working unit ID")
    require(len(scopes) == len(set(scopes)), "duplicate candidate scope")
    for a in scopes:
        for b in scopes:
            require(a == b or not a.startswith(b), f"overlapping candidate scopes: {a}, {b}")
    for l in source["layers"]:
        g = l["gate"]
        require(g in index and index[g]["kind"] == "evidence-gate", "missing layer gate")
        own = {t["id"] for t in tasks if t["layer"] == l["id"]} - {g}
        require(own <= ancestors[g], f"gate misses layer work: {g}")
    paths = {}
    for i in sorted(ids, key=lambda i: (ranks[i], i)):
        deps = index[i]["depends_on"]
        paths[i] = [i] if not deps else max((paths[d] + [i] for d in deps), key=lambda p: (len(p), tuple(p)))
    waves = [{"id": f"W{r:02d}", "depth": r, "tasks": sorted(i for i in ids if ranks[i] == r),
              "validation": f"WV-W{r:02d}"} for r in range(max(ranks.values()) + 1)]
    return index, ranks, paths["G4"], waves

def snapshot(source):
    result = []
    bindings = {b["path"]: b["sha256"] for b in source["source_bindings"]}
    paths = set(bindings) | set(source["additional_context"])
    paths |= {r["path"] for t in source["tasks"] for r in t["source_refs"]}
    for p in sorted(paths):
        require(not Path(p).is_absolute() and ".." not in Path(p).parts, "source path escape")
        data = (ROOT / p).read_bytes()
        sha = digest(data)
        require(p not in bindings or sha == bindings[p], f"source changed: {p}")
        result.append({"path": p, "sha256": sha, "bytes": len(data)})
    return result

def negative_controls(source):
    controls = []
    def rejected(name, mutate):
        specimen = copy.deepcopy(source)
        mutate(specimen)
        try:
            analyze(specimen)
        except (ValueError, KeyError):
            controls.append({"control": name, "result": "rejected"})
        else:
            raise ValueError("negative control accepted: " + name)
    rejected("duplicate task", lambda s: s["tasks"].append(copy.deepcopy(s["tasks"][0])))
    rejected("missing prerequisite", lambda s: s["tasks"][1]["depends_on"].append("MISSING"))
    rejected("dependency cycle", lambda s: s["tasks"][0]["depends_on"].append("G4"))
    rejected("missing layer closure", lambda s: next(t for t in s["tasks"] if t["id"] == "G1").update(depends_on=["C05"]))
    rejected("duplicate SWU", lambda s: s["tasks"][1]["working_units"][0].update(id=s["tasks"][0]["working_units"][0]["id"]))
    rejected("omitted output evidence", lambda s: s["tasks"][0]["validation"].update(required_evidence=[]))
    rejected("overlapping write scope", lambda s: s["tasks"][1].update(write_scope=s["tasks"][0]["write_scope"]))
    rejected("premature execution status", lambda s: next(t for t in s["tasks"] if t["id"] == "P02")["validation"].update(execution_status="unchecked"))
    rejected("unbound acceptance", lambda s: (s["tasks"][0].update(status="accepted"), s["tasks"][0]["validation"].update(execution_status="accepted", acceptance_ref={})))
    rejected("L2-to-L3 gate cycle", lambda s: next(t for t in s["tasks"] if t["id"] == "G2")["depends_on"].append("I06"))
    rejected("decoder before soundness", lambda s: next(t for t in s["tasks"] if t["id"] == "P02").update(depends_on=["P01"]))
    rejected("baseline before formalization", lambda s: next(t for t in s["tasks"] if t["id"] == "B00").update(depends_on=[]))
    rejected("formalization ordering bypass", lambda s: next(t for t in s["tasks"] if t["id"] == "P03").update(depends_on=[]))
    return controls

def render(source):
    index, ranks, longest, waves = analyze(source)
    bindings = snapshot(source)
    controls = negative_controls(source)
    source_sha = digest(SOURCE.read_bytes())
    compiler_sha = digest(Path(__file__).read_bytes())
    files = {}
    def put(path, content):
        files[path] = content.encode() if isinstance(content, str) else encoded(content)
    def md(path, lines):
        put(path, "\n".join(lines) + "\n")
    def bullets(items):
        return ["- " + v for v in items]
    tasks = source["tasks"]
    accepted = [t["id"] for t in tasks if t["status"] == "accepted"]
    execution_status = "all-tasks-accepted" if len(accepted) == len(tasks) else "partial-execution" if accepted else "not-started"
    header = ["> Generated from [PLAN-SOURCE.json](../PLAN-SOURCE.json).",
        "> Standalone candidate. " + (f"{len(accepted)}/{len(tasks)} tasks accepted with hash-bound evidence; see task receipts for review scope." if accepted else "All execution tasks are not started.") + " No formal Invoke admission is claimed.", ""]
    edges = [{"from": d, "to": t["id"], "type": "accepted-scoped-evidence"} for t in tasks for d in t["depends_on"]]
    units = []
    for t in tasks:
        prev = [index[d]["working_units"][-1]["id"] for d in t["depends_on"]]
        for u in t["working_units"]:
            units.append({**u, "task_id": t["id"], "layer": t["layer"], "depends_on": list(prev),
                "validation_id": t["validation"]["id"], "write_scope": t["write_scope"]})
            prev = [u["id"]]
    seen = set()
    for u in sorted(units, key=lambda u: (ranks[u["task_id"]], u["id"])):
        require(set(u["depends_on"]) <= seen, "working-unit cycle or missing dependency")
        seen.add(u["id"])
    put("dag.json", {"schema": "relational-theorem-checker.dag/v1", "source_sha256": source_sha,
        "dependency_policy": source["dependency_policy"], "entry_phase": source["entry_phase"], "nodes": [
            {"id":t["id"],"title":t["title"],"layer":t["layer"],"kind":t["kind"],"status":t["status"],
             "depends_on":t["depends_on"],"wave":f'W{ranks[t["id"]]:02d}',"validation_id":t["validation"]["id"],
             "task_card":f'work-pack/tasks/{t["id"]}.md',"working_units":[u["id"] for u in t["working_units"]]}
            for t in tasks], "edges":edges, "waves":waves,
        "longest_dependency_path":{"tasks":longest,"node_count":len(longest),
            "scheduling_claim":"No duration-based critical path is asserted."}})
    put("swu-manifest.json", {"schema":"relational-theorem-checker.swu-manifest/v1",
        "source_sha256":source_sha,"working_units":units})
    graph = ["# Full dependency DAG", ""] + header + [
        "An arrow means accepted, current and applicable evidence is required before the successor starts. Wave membership denotes dependency depth; it is not a deadline or staffing assignment.",
        "The first phase is F0: P01 semantics → P03 independent formal predicates → P04 Lean reference checker → P05 general soundness and formalization review. Baseline refresh B00 and decoder/interface alignment P02 follow accepted P05 evidence.",
        "", FENCE+"mermaid", "flowchart TD"]
    for layer in source["layers"]:
        graph.append(f'  subgraph {layer["id"]}["{layer["id"]}"]')
        for t in tasks:
            if t["layer"] == layer["id"]:
                label = f'{t["id"]}: {t["title"]}'
                graph.append(f'    {t["id"]}{{"{label}"}}' if t["kind"]=="evidence-gate" else f'    {t["id"]}["{label}"]')
        graph.append("  end")
    graph += [f'  {e["from"]} --> {e["to"]}' for e in edges]
    graph += [FENCE, "", "## Dependency depth", "",
        f'The longest dependency path contains {len(longest)} tasks: ' + " → ".join(longest) + ".",
        "This counts prerequisite steps; engineering effort and elapsed time remain unestimated.", "",
        "## Rule-change handoff", "",
        "E02 generates rule-change obligations. G2 closes supported non-rule extensions and releases I01. I06 combines L3 evidence with those obligations. G2 never waits on I06, so the handoff creates no cycle.",
        "", "## Concurrent branches", "",
        "- P01, P03, P04 and P05 form the opening formalization chain; P02 begins only after its accepted evidence and B00 alignment.",
        "- E03 preservation and E04 model witnesses join at E05.",
        "- I05 independence witnesses run alongside derivation and closure work after I01.",
        "- R01 workflow contracts and R02 proof replay join at R03.",
        "- R04 CLI integration and R05 application adapter join at R06.", "",
        "Concurrency is permissible after shared predecessor contracts are fixed and accepted. Task scopes are disjoint; changing an upstream export triggers impact review and a replan."]
    md("DAG.md", graph)
    plan = ["# Relational model and theorem checker plan", ""] + header + [
        f'The plan contains **{len(tasks)} tasks**, **{len(units)} working units**, **{len(edges)} dependency edges**, **{len(waves)} execution waves**, and **five layer evidence gates**.',
        "", "## Reading map", "",
        "- [Full Mermaid DAG](DAG.md) and [machine-readable graph](dag.json)",
        "- [Task board and working units](WORK-PACK.md)",
        "- [Execution protocol and waves](EXECUTION-PACK.md)",
        "- [Validation strategy](VALIDATION-STRATEGY.md) and [planning check](receipts/planning-check.json)",
        "- [Planning provenance](PLANNING-PROVENANCE.json)", "",
        "## Layer closure", "", "| Layer | Gate | Allowed conclusion |", "|---|---|---|"]
    plan += [f'| {l["id"]} | [{l["gate"]}](work-pack/tasks/{l["gate"]}.md) | {l["claim_ceiling"]} |' for l in source["layers"]]
    plan += ["", "## Start here", "",
        "Start with F0 formalization: P01 defines normative relational semantics and theorem targets; P03 formalizes typed finite inputs and independent validity; P04 defines the pure reference checker in Lean; P05 proves general soundness and closes the formalization review. B00 then refreshes execution source bindings and P02 aligns the candidate schemas/APIs and decoder with the proved model. All later tasks depend transitively on accepted P05 evidence.",
        "Use the captured research sources for formalization. If the later B00 refresh detects relevant drift, invalidate the affected formal evidence and replan/reprove before adapters proceed. Existing schemas/APIs remain draft projections until P02 alignment. Earlier research documents retain their captured bytes; this plan supersedes their prior implementation ordering.", "",
        "## First phase exit evidence", ""] + bullets(source["entry_phase"]["exit_evidence"]) + ["",
        "## Scheduling", "", source["dependency_policy"]["schedule"],
        "Estimate effort and dates after selecting the L0 semantic contract, reviewer capacity and proof toolchain. Dependency depth is the ordering metric currently supported by evidence.",
        "", "## Scope and preserved state", "",
        f'Future implementation is proposed under {BT}craft/formalization/candidates/relational-theorem-checker/v1/{BT}. Tasks do not authorize edits to immutable authority records, existing Lean modules, live governance stores, runtime state, credentials or keys. The final output is a bounded-use recommendation.',
        "", "## Decisions before dependent work", "", "| Decision | Due before | Owner role | Direction to record |", "|---|---|---|---|"]
    plan += [f'| {d["id"]} | {d["due_before"]} | {d["owner"]} | {d["question"]} {d["default_direction"]} |' for d in source["decisions"]]
    plan += ["", "## Non-regression contract", ""] + bullets(source["non_regression"])
    md("PLAN.md", plan)
    board = ["# Work pack", ""] + header + [
        "## Task board", "", "| Task | Layer / wave | Accepted prerequisites | Working units | Validation |",
        "|---|---|---|---|---|"]
    board += [f'| [{t["id"]} — {t["title"]}](work-pack/tasks/{t["id"]}.md) | {t["layer"]} / W{ranks[t["id"]]:02d} | {", ".join(t["depends_on"]) or "none"} | {", ".join(u["id"] for u in t["working_units"])} | {t["validation"]["id"]} |' for t in tasks]
    board += ["", ("Accepted tasks and working units: **" + ", ".join(accepted) + "**. Remaining tasks are **not-started**. F0 ownership and author self-review are recorded in task evidence." if accepted else "All tasks and working units are **not-started**. Owner roles are proposed; assignments are unassigned."),
        "", "## Working-unit policy", "",
        "Units run in their listed order. The first unit depends on the final accepted unit of every prerequisite task. Split tasks require both units before task validation. Acceptance is evaluated against task criteria, not output filenames.",
        "", "## Shared context", "",
        "- [Context and trust boundaries](work-pack/shared/context.md)",
        "- [Cross-task gaps](work-pack/shared/cross-task-gaps.md)",
        "- [Cross-task decisions](work-pack/shared/cross-task-decisions.md)",
        "- [Traceability](work-pack/shared/traceability.md)",
        "- [Working-unit manifest](swu-manifest.json)"]
    md("WORK-PACK.md", board)
    for t in tasks:
        card = [f'# {t["id"]} — {t["title"]}', "", f'**Status:** {t["status"]}', "",
            f'**Layer:** {t["layer"]} · **Wave:** W{ranks[t["id"]]:02d} · **Validation:** {t["validation"]["id"]}',
            "", "## Objective", "", t["objective"], "", "## Prerequisites and inputs", ""]
        card += bullets(t["inputs"])
        card += ["", "## Ownership and write boundary", "",
            f'Role: {t["execution_owner"]["role"]}. Assignment: {t["execution_owner"]["assignment"]}.',
            f'Future write scope: {BT}{t["write_scope"]}{BT}.',
            "Use versioned predecessor exports; an upstream interface change requires impact review and replan.",
            "", "## Planned outputs", ""] + bullets(t["outputs"])
        card += ["", "## Ordered working rules", ""] + [f"{i+1}. {rule}" for i,rule in enumerate(t["ordered_rules"])]
        card += ["", "## Working units", ""]
        for u in t["working_units"]:
            card += [f'- **{u["id"]}** — {u["title"]}. Exit criteria: ' + " ".join(u["exit_criteria"])]
        card += ["", "## Acceptance evidence", ""] + bullets(t["acceptance_criteria"])
        card += ["", "## Failure and challenge controls", ""] + bullets(t["failure_controls"])
        card += ["", "## Validation contract", "",
            t["validation"]["method"] + (". Checked evidence is bound below." if t["status"] == "accepted" else ". No task implementation validation has run yet."),
            "Produce the specified evidence with exact profile and dependency identities; a reviewer must accept the scoped criteria before successors start.",
            "", "## Source anchors", ""]
        if t["status"] == "accepted":
            ref = t["validation"]["acceptance_ref"]
            rel = os.path.relpath(ROOT / ref["path"], OUTPUT / "work-pack/tasks")
            card += [f'- [Accepted candidate evidence]({rel}) — SHA-256 {ref["sha256"]}; author self-review, no authority admission.']
        for r in t["source_refs"]:
            rel = os.path.relpath(ROOT / r["path"], OUTPUT / "work-pack/tasks")
            card.append(f'- [{Path(r["path"]).name}]({rel}) — {r["selector"]}.')
        card += ["", "[Task board](../../WORK-PACK.md) · [DAG](../../DAG.md)"]
        md(f'work-pack/tasks/{t["id"]}.md', card)
    execution = ["# Execution protocol", ""] + header + [
        "1. Complete F0 (P01 → P03 → P04 → P05), including the pinned Lean toolchain, independent semantics, inhabited example, general soundness and evidence review.",
        "2. Refresh B00 against the reviewed formal model and align candidate schema/API projections in P02; replan/reprove if bound inputs drift.",
        "3. Start every task only with accepted, current prerequisite evidence.",
        "4. Work in the candidate scope and publish versioned exported contracts.",
        "5. Complete working units, validation and evidence review; explicitly narrow unsupported profiles.",
        "6. Close the wave check after every member is accepted and re-evaluate dependencies after changes.",
        "7. Close each layer gate while retaining its named claim ceiling.", "",
        "## Wave checks", "",
        "Each dependency-depth cohort has one wave check. It verifies membership completion, evidence currentness, hard obligations and scope conflicts. These are review controls, not additional DAG nodes; they do not create dependencies between independent branches.",
        "", "| Wave | Tasks | Single closure check |", "|---|---|---|"]
    for w in waves:
        execution.append(f'| [{w["id"]}](work-pack/waves/{w["id"]}.md) | {", ".join(w["tasks"])} | {w["validation"]} |')
        md(f'work-pack/waves/{w["id"]}.md', [f'# {w["id"]} — dependency depth {w["depth"]}', "",
            f'**Single wave closure check:** {w["validation"]}', "**Status:** " + ("accepted" if all(index[i]["status"] == "accepted" for i in w["tasks"]) else "not-started"), "",
            "## Membership", ""] + [f'- [{i} — {index[i]["title"]}](../tasks/{i}.md)' for i in w["tasks"]] + [
            "", "## Ready conditions", "", "Every prerequisite has accepted, current evidence; task-specific decisions are recorded.",
            "", "## Closure", "",
            "Accept only when every member passes task validation. Confirm scoped evidence, current dependency identities, no hidden hard obligation and no conflicting writes. Record failures without advancing affected successors."])
    execution += ["", "## Replan triggers", "",
        "- Required source bytes or a reviewed semantic contract change.",
        "- A supported profile is inconsistent or a required proof cannot be discharged.",
        "- Scope expands into immutable authority, live runtime or actual admission.",
        "- An interface change affects accepted downstream evidence.", "",
        "Narrow scope explicitly when justified; do not drop obligations to obtain readiness. Dates, staffing and automatic delegation remain unassigned."]
    md("EXECUTION-PACK.md", execution)
    md("VALIDATION-STRATEGY.md", ["# Validation strategy", ""] + header + [
        "## Planning checks performed now", "",
        "The compiler checks source identity, unique tasks/SWUs, acyclicity, final gate reachability, complete layer gate ancestry, formalization-first ordering, disjoint scopes, evidence coverage and status consistency. Accepted F0 tasks require current hash-bound outputs, criteria and dependency evidence. Thirteen hostile mutations must be rejected, including unbound acceptance and attempts to start decoding or baseline capture before formalization review. All views, cards, working units and waves are derived from one source.",
        "", FENCE+"bash", "python3 docs/plans/relational-theorem-checker/compile_plan.py check", FENCE, "",
        "This verifies deterministic regeneration and bound source hashes. It does not run the future checker, prove Lean theorems, execute the pilot or admit a Plan.",
        "", "## Future execution validation", "",
        "| Layer | Required evidence | Principal failure class |", "|---|---|---|",
        "| L0 | Independent predicates, general soundness, statement/axiom audit, bound demo and hostile controls | Circular correctness or weakened theorem |",
        "| L1 | Exact registry projection, ordered pairs, reference resolution, coverage and replay | Omission, pair widening or stale evidence |",
        "| L2 | Required obligations, data compatibility, preservation and model evidence | Vacuity or unsupported conservativity |",
        "| L3 | Derivation soundness, least-fixed-point adequacy, protected lineage and checked witnesses | Indirect authority leakage or incomplete closure |",
        "| L4 | Isolated proof replay, complete aggregation, application freshness and pilot | Substituted proof, missing obligation or source drift |",
        "", "## Claim ceilings", "",
        "Planning checks establish consistency and fidelity to captured sources. Semantic acceptance requires task evidence. A DAG is not a proved relational model; theorem acceptance does not establish parser, hash or compiled-runtime correctness.",
        "", "## Rebuilding", "",
        "Build refuses to overwrite an existing package. Preserve the current source and package when preparing a successor version. The custom compiler is fixed to this package target and does not implement the formal Invoke compiler or admission contract."])
    md("work-pack/shared/context.md", ["# Shared context", "",
        "The analysis selects a 41-kind registry with 550 relation-specific ordered-pair entries and a frozen 40-branch carrier that excludes materializes-consequence. B00 must refresh these facts before execution.",
        "Candidate source posture and effective admitted-current registry state are separate. Existing Lean identity-binding results do not prove the new independently defined relational semantics.",
        "", "## Trust boundaries", "",
        "Source interpretation, JSON parsing, hashing and compiled host execution stay explicit assumptions until separately verified. The theorem concerns the supported formal input. Evidence preserves exact statement and dependency identities.",
        "", "## Non-regression", ""] + bullets(source["non_regression"]))
    md("work-pack/shared/cross-task-gaps.md", ["# Cross-task gaps", "",
        "- F0 implementation and author self-review are recorded in accepted task evidence; later assignments remain unassigned.",
        "- F0 formalization starts at P01; P03/P04/P05 establish formal semantics, reference checker and soundness before B00/P02 adapter work.",
        "- Carrier compatibility strategy is selected in C02.",
        "- Conservativity applies only to supported profiles with evidence.",
        "- G2 retains rule obligations; I06 discharges them.",
        "- Proof isolation and axiom policy are selected before R02.",
        "- No durations, deployment or actual governance admission are included."])
    md("work-pack/shared/cross-task-decisions.md", ["# Cross-task decisions", ""] + [
        f'- **{d["id"]}**, before **{d["due_before"]}**, owner role **{d["owner"]}**: {d["question"]} Direction: {d["default_direction"]}'
        for d in source["decisions"]])
    md("work-pack/shared/traceability.md", ["# Traceability", "",
        "| Task | Layer contract | Immediate prerequisites | Validation |", "|---|---|---|---|"] + [
        f'| [{t["id"]}](../tasks/{t["id"]}.md) | [{t["layer"]}](../../../layers/{Path(t["source_refs"][0]["path"]).name}) | {", ".join(t["depends_on"]) or "baseline documents"} | {t["validation"]["id"]} |'
        for t in tasks])
    put("PLANNING-PROVENANCE.json", {"schema":"relational-theorem-checker.planning-provenance/v1",
        "created_on":source["created_on"],"source_sha256":source_sha,"compiler_sha256":compiler_sha,
        "planning_method":source["planning_method"],"authority":source["authority"],
        "ordering_override":source["ordering_override"],"entry_phase":source["entry_phase"],
        "formal_invoke_admission":"not-requested-or-claimed","design_receipts":"not-present",
        "source_bindings":bindings,"execution_status":execution_status})
    for p, data in files.items():
        if p.endswith(".md"):
            for target in re.findall(r"\]\(([^)]+)\)", data.decode()):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (OUTPUT / p).parent.joinpath(target.split("#")[0]).resolve()
                try:
                    in_bundle = str(resolved.relative_to(OUTPUT.resolve()))
                except ValueError:
                    require(resolved.is_file(), f"missing source link: {p}: {target}")
                else:
                    require(in_bundle in files or in_bundle == "receipts/planning-check.json",
                            f"missing generated link: {p}: {target}")
    graph_data = json.loads(files["dag.json"])
    require({(e["from"],e["to"]) for e in graph_data["edges"]} ==
        {(d,n["id"]) for n in graph_data["nodes"] for d in n["depends_on"]}, "edge projection mismatch")
    receipt = {"schema":"relational-theorem-checker.planning-check/v1", "result":"pass",
        "claim_ceiling":"Planning structure, source bindings and deterministic artifacts only; no implementation or theorem validation.",
        "source_sha256":source_sha,"compiler_sha256":compiler_sha,
        "counts":{"tasks":len(tasks),"working_units":len(units),"edges":len(edges),"waves":len(waves),
            "layer_gates":len(source["layers"]),"source_bindings":len(bindings)},
        "checks":["source hashes","unique task and SWU identities","task and SWU DAGs",
            "final gate reachability","complete layer gate ancestry","formalization-first ordering","task evidence contracts",
            "disjoint scopes","single check per wave","local Markdown links","edge projection","status and accepted evidence consistency"],
        "negative_controls":controls,"longest_dependency_path":longest,
        "artifacts":[{"path":p,"sha256":digest(data),"bytes":len(data)} for p,data in sorted(files.items())]}
    put("receipts/planning-check.json", receipt)
    return files, receipt

def publish_no_replace(temp):
    libc = ctypes.CDLL(None, use_errno=True)
    require(hasattr(libc, "renameat2"), "atomic no-replace publication unavailable")
    rename = libc.renameat2
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(temp), -100, os.fsencode(OUTPUT), 1) != 0:
        number = ctypes.get_errno()
        raise OSError(number, os.strerror(number), str(OUTPUT))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["build","check"])
    args = parser.parse_args()
    files, receipt = render(json.loads(SOURCE.read_bytes()))
    if args.mode == "build":
        require(not OUTPUT.exists(), "refusing to overwrite existing DAG package")
        temp = Path(tempfile.mkdtemp(prefix=".dag-plan-", dir=BASE))
        try:
            for p,data in files.items():
                target = temp / p
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            publish_no_replace(temp)
        finally:
            if temp.exists():
                shutil.rmtree(temp)
    else:
        require(OUTPUT.is_dir(), "DAG package does not exist")
        actual = {str(p.relative_to(OUTPUT)) for p in OUTPUT.rglob("*") if p.is_file()}
        require(actual == set(files), "package membership differs from deterministic generation")
        for p,data in files.items():
            require((OUTPUT / p).read_bytes() == data, "generated artifact drift: " + p)
    print(json.dumps({"mode":args.mode,"result":"pass","counts":receipt["counts"],
        "negative_controls_rejected":len(receipt["negative_controls"]),
        "longest_dependency_path":receipt["longest_dependency_path"],"execution_status":json.loads(files["PLANNING-PROVENANCE.json"])["execution_status"]}, indent=2))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        raise SystemExit("Planning validation failed: " + str(error))
