#!/usr/bin/env python3
"""Validate planning structure and exact current inputs; runs no implementation."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[4]
IMPL = "craft/formalization/candidates/definition-assurance-v1/"
DATA = "docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/"


def load(name):
    return json.loads((HERE / name).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    dag = load("dag.json")
    units = load("swu-manifest.json")["units"]
    sources = load("source-baseline.json")
    assertions = 0

    def require(condition, message):
        nonlocal assertions
        assertions += 1
        if not condition:
            raise ValueError(message)

    require(dag["authority_effect"] == "none", "Plan has an authority effect")
    tasks = {t["id"]: t for t in dag["tasks"]}
    require(len(tasks) == len(dag["tasks"]) == dag["task_count"], "Duplicate task/count mismatch")
    byunit = {u["id"]: u for u in units}
    require(len(byunit) == len(units) == dag["swu_count"], "Duplicate SWU/count mismatch")
    require(dag["execution_policy"]["current_request"] == "analysis-and-planning-only", "Unrequested implementation")
    require(dag["execution_policy"]["implementation_readiness"] == "not-run", "Fabricated implementation readiness")
    for decision in load("design-decisions.json")["decisions"]:
        require(set(decision["resolve_before_or_enforce_in"]) <= set(tasks), "Decision has an unbound gate")
    for task in tasks.values():
        require(task["status"] == "planned", "Future task claims execution")
        require(task["layer"] in {"L1", "L2", "L3"}, "Unknown layer")
        require(task["stage"] in {"D0", "D1", "D2", "D3", "D4", "D5", "D6"}, "Unknown stage")
        require(len(set(task["depends_on"])) == len(task["depends_on"]), "Duplicate edge")
        require(set(task["depends_on"]) <= set(tasks), "Unbound dependency: " + task["id"])
        require(bool(task["swu_ids"]) and set(task["swu_ids"]) <= set(byunit), "Missing task SWUs")
        require(all(byunit[u]["parent_task"] == task["id"] for u in task["swu_ids"]), "SWU membership mismatch")
        require(bool(task["implementation_rules"] and task["acceptance"]), "Missing implementation/acceptance detail")
    remaining, done, frontiers = set(tasks), set(), []
    while remaining:
        frontier = sorted(i for i in remaining if set(tasks[i]["depends_on"]) <= done)
        require(bool(frontier), "Execution graph cyclic")
        frontiers.append(frontier)
        done.update(frontier)
        remaining -= set(frontier)
    require(frontiers == load("topological-frontiers.json")["frontiers"], "Stale derived frontiers")
    ancestors = set()

    def visit(ident):
        if ident in ancestors:
            return
        ancestors.add(ident)
        for dep in tasks[ident]["depends_on"]:
            visit(dep)

    visit("H04")
    require(ancestors == set(tasks), "Task orphaned from project closeout")
    registry = json.loads((LAB / "authority/definitions/registry.json").read_text())
    entries = {e["definition_id"] + "@" + e["version"]: e for e in registry["entries"]}
    rows = {r["definition_id"]: r for r in dag["definition_queue"]}
    require(len(rows) == len(dag["definition_queue"]) == len(registry["current_lookup"]) == 183, "Current queue mismatch")
    require(len(registry["entries"]) == 189, "Admitted version denominator changed")
    require(dag["source_registry_sha256"] == sha(LAB / "authority/definitions/registry.json"), "Registry stale")
    families = {f["id"]: f for f in dag["families"]}
    assigned = [i for f in families.values() for i in f["members"]]
    require(len(assigned) == len(set(assigned)) == 183 and set(assigned) == set(rows), "Family partition incomplete or overlapping")
    for identity, row in rows.items():
        require(registry["current_lookup"][identity] == row["version_ref"], "Selected source version stale")
        entry = entries[row["version_ref"]]
        require(row["source_path"] == entry["path"] and row["source_sha256"] == entry["sha256"] == sha(LAB / row["source_path"]), "Source binding stale")
        require(identity in families[row["family_id"]]["members"], "Family member reference mismatch")
        for phase in ("T", "O", "E", "R"):
            expected = row["family_id"] + "-" + phase + "." + identity
            require(expected in byunit and byunit[expected]["definition_id"] == identity, "Missing per-definition phase")
            require(byunit[expected]["version_ref"] == row["version_ref"], "SWU source version mismatch")
    output_owners = {}
    for unit in units:
        require(unit["parent_task"] in tasks and unit["id"] in tasks[unit["parent_task"]]["swu_ids"], "Orphaned SWU")
        require(unit["depends_on_tasks"] == tasks[unit["parent_task"]]["depends_on"], "Stale unit prerequisites")
        require(unit["execution_condition"] == tasks[unit["parent_task"]]["condition"], "Conditional route mismatch")
        require(bool(unit["ordered_rules"] and unit["edge_cases"] and unit["failure_behavior"] and unit["closeout"]), "Incomplete unit contract")
        require(unit["validation"]["phase"] == "post-produce" and bool(unit["pre_execution_check"]), "Validation phases missing")
        require(bool(unit["validation"]["command"] or unit["validation"]["reviewable_check"]), "No verification surface")
        require(bool(unit["validation"]["runner_state"]), "Future validator availability concealed")
        require(set(d["path"] for d in unit["target_dispositions"]) == set(unit["outputs"]), "Output dispositions missing")
        for scope in unit["write_scope"]:
            require(scope.startswith((IMPL, DATA)) and ".." not in Path(scope).parts, "Protected/outside write scope")
        for output in unit["outputs"]:
            require(output.startswith((IMPL, DATA)) and ".." not in Path(output).parts, "Protected/outside output")
            require(output not in output_owners, "Multiple output writers: " + output)
            output_owners[output] = unit["id"]
            require(any(output == scope or (scope.endswith("/") and output.startswith(scope)) for scope in unit["write_scope"]), "Output outside SWU scope")
    for source in sources["sources"]:
        require(sha(LAB / source["path"]) == source["sha256"], "Planning input drift: " + source["path"])
    require(sources["definitions"] == dag["definition_queue"], "Snapshot queue drift")
    local_links = 0
    for path in HERE.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("https://", "http://")):
                continue
            resolved = (path.parent / target.split("#")[0]).resolve()
            # This receipt is created only after all checks pass on a fresh package.
            require(resolved.exists() or resolved in {HERE / "planning-validation.json", HERE / "manifest.json"}, "Broken link: " + str(path) + " -> " + target)
            local_links += 1
    receipt = {"schema_version": "definition-assurance-planning-validation/v1-candidate", "authority_effect": "none", "result": "PASS",
               "validated_assertions": assertions, "task_nodes": len(tasks), "task_edges": sum(len(t["depends_on"]) for t in tasks.values()),
               "swus": len(units), "definitions": len(rows), "families": len(families), "logical_frontiers": len(frontiers),
               "first_unit": "A01.1", "source_currentness": "183 exact current sources verified", "local_links": local_links,
               "dag_sha256": sha(HERE / "dag.json"), "swu_manifest_sha256": sha(HERE / "swu-manifest.json"), "validator_sha256": sha(__file__),
               "meaning": "Planning structure and exact current source bindings only; no implementation, owner fidelity, proof, Invoke admission or semantic admission PASS."}
    (HERE / "planning-validation.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
