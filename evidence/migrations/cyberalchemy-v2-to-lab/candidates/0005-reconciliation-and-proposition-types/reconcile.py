#!/usr/bin/env python3
"""Reconcile every normalized target without rewriting the historical ledger."""
from collections import Counter
from common import LAB, ROOT, PREVIOUS, L0, L1, binding, dump, load, sha, need


def digest_chain(path, wanted, visited=None):
    """Follow only hash-verified local JSON bindings, including bundle manifests."""
    visited = set() if visited is None else visited
    if path in visited:
        return None
    visited.add(path)
    data = load(path)
    if wanted in path.read_text():
        return [path]
    refs = []
    def collect(value):
        if isinstance(value, dict):
            if "path" in value and "sha256" in value:
                refs.append((value["path"], value["sha256"]))
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    collect(data)
    if "authority_basis" in data and "manifest_path" in data["authority_basis"]:
        refs.append((data["authority_basis"]["manifest_path"], data["selection"]["manifest_sha256"]))
    for name, expected in refs:
        for child in [LAB / name, path.parent / name]:
            if child.suffix == ".json" and child.is_file() and sha(child) == expected:
                chain = digest_chain(child, wanted, visited)
                if chain:
                    return [path, *chain]
    return None


def build():
    ledger = load(PREVIOUS / "realization-ledger.json")
    definitions = load(LAB / "authority/definitions/registry.json")
    types_path = LAB / "authority/artifact-types/candidates/0002-artifact-surface-foundation-revision/registry.json"
    types = load(types_path)
    admitted = {}
    for entry in definitions["entries"]:
        ref = entry["definition_id"] + "@" + entry["version"]
        if entry["lifecycle_state"] == "admitted" and definitions["current_lookup"].get(entry["definition_id"]) == ref:
            admitted.setdefault(("semantic", entry["term"].casefold()), []).append({
                "path": entry["path"], "sha256": entry["sha256"],
                "admission_decision_ref": entry["admission_decision_ref"]})
    for entry in types["entries"]:
        if entry["lifecycle_state"] == "admitted-current":
            admitted.setdefault(("artifact-type", entry["semantic_kind"]), []).append({
                "path": entry["artifact_path"], "sha256": entry["artifact_sha256"],
                "admission_decision_ref": entry["admission_decision_ref"]})
    candidates = {}
    inputs = [PREVIOUS / "realization-ledger.json", PREVIOUS / "target-candidate-index.json",
              LAB / "authority/definitions/registry.json", types_path]
    for registry_path in [L0 / "registry.json", L1 / "registry.json", ROOT / "registry.json"]:
        if not registry_path.exists():
            continue
        inputs.append(registry_path)
        for entry in load(registry_path)["entries"]:
            if entry.get("normalized_target", True):
                candidates.setdefault(entry["target_id"], []).append({
                    "path": entry.get("candidate_path", entry.get("path")),
                    "sha256": entry.get("candidate_sha256", entry.get("sha256")),
                    "registry": str(registry_path.relative_to(LAB))})
    scaffolds = {x["target_id"]: x for x in load(PREVIOUS / "target-candidate-index.json")["entries"]}
    successor_path = PREVIOUS / "d65-successor.json"
    selection_path = PREVIOUS / "decisions/0001-planning-selection/decision.json"
    selection = load(selection_path)
    need(selection["decision_effect"]["d65_successor"] == "selected-as-normalization-planning-baseline"
         and any(x["path"] == "d65-successor.json" and x["sha256"] == sha(successor_path)
                 for x in selection["exact_subjects"]), "D65 successor selection drift")
    replacements = {x["predecessor_target"]: x["target_id"] for x in load(successor_path)["recommended_targets"] if x["change"] == "replace"}
    inputs += [successor_path, selection_path]
    decisions = {}
    for path in sorted((LAB / "docs/decisions").glob("*/decision.json")):
        data = load(path)
        if data.get("decision_id"):
            decisions.setdefault(data["decision_id"], []).append(path)
    rows = []
    for target in ledger["targets"]:
        ident, family = target["target_id"], target["family"]
        key = target["term"].casefold() if family == "semantic" else ident.removeprefix("type.")
        refs = admitted.get((family, key), [])
        state = "admitted-current" if refs else "constructed-candidate"
        if not refs:
            refs = candidates.get(replacements.get(ident, ident), [])
        if not refs:
            state = "scaffold-only"
            if ident in scaffolds:
                item = scaffolds[ident]
                refs = [{"path": str((PREVIOUS / item["machine_path"]).relative_to(LAB)), "sha256": item["machine_sha256"]}]
            else:
                state = "missing"
        problems = []
        for ref in refs:
            path = LAB / ref["path"]
            if not path.is_file() or sha(path) != ref["sha256"]:
                problems.append("missing-or-changed-material:" + ref["path"])
            if "admission_decision_ref" in ref:
                matches = decisions.get(ref["admission_decision_ref"], [])
                chain = digest_chain(matches[0], ref["sha256"]) if len(matches) == 1 else None
                if not chain:
                    problems.append("unresolved-exact-admission:" + ref["admission_decision_ref"])
                else:
                    inputs.extend(chain)
        if len(refs) != 1:
            problems.append("missing-or-ambiguous-realization")
        rows.append({"target_id": ident, "family": family, "term": target["term"],
                     "selected_successor_target": replacements.get(ident),
                     "historical_state": target["realization_state"],
                     "construction_state": "blocked-integrity" if problems else state,
                     "evidence": refs, "problems": problems,
                     "next_action": {"admitted-current": "reuse exact admitted version",
                         "constructed-candidate": "retain candidate; use current tests before promotion",
                         "scaffold-only": "implement family-specific contract and behavior",
                         "missing": "locate or construct explicit target"}[state]})
    need(len(rows) == len({x["target_id"] for x in rows}) == 195, "Target denominator changed")
    return {"schema_version": "cal-reconstruction-reconciliation/v1", "authority_effect": "none",
            "target_count": len(rows), "state_counts": dict(sorted(Counter(x["construction_state"] for x in rows).items())),
            "family_counts": dict(sorted(Counter(x["family"] for x in rows).items())),
            "inputs": [binding(p) for p in sorted(set(inputs))], "targets": rows,
            "claim_ceiling": "Current local material and exact admission-link reconciliation. Constructed candidates are not admissions; integrity checks do not rerun their historical tests or establish every external source as current. Exact identity matching does not equate similarly named packages."}


def render(data):
    lines = ["# Reconstruction state", "", "`195 normalized targets -> current Lab evidence -> next missing batch`", "",
             "A constructed candidate has concrete machine records. A scaffold only describes what still needs implementation. Admission is a separate recorded state.", "",
             "| State | Targets |", "| --- | ---: |"]
    lines += [f"| {key} | {value} |" for key, value in data["state_counts"].items()]
    lines += ["", "| Target | State | Next action |", "| --- | --- | --- |"]
    lines += [f"| `{x['target_id']}` | {x['construction_state']} | {x['next_action']} |" for x in data["targets"]]
    lines += ["", data["claim_ceiling"], ""]
    return "\n".join(lines)


if __name__ == "__main__":
    result = build()
    dump(ROOT / "reconciliation.json", result)
    (ROOT / "RECONCILIATION.md").write_text(render(result))
    print(result["state_counts"])
