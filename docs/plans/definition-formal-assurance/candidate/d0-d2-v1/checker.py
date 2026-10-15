#!/usr/bin/env python3
"""Finite candidate interpretation; no solver or kernel-proof claim.

The search constructs records. The semantic predicates inspect records and
root grants independently of the query evaluator. No distinction is an axiom.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import platform
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[4]
AXES = ("kind", "status", "evidence", "commitment", "provenance", "owner", "residue")
OBLIGATIONS = ("combined-satisfiability", "required-inhabitation", "provenance-without-authority", "permitted-overlap")
DEPENDENCIES = ("cal.definition.authority", "cal.definition.provenance", "cal.definition.governance-axis-independence-invariant")


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def provenance_holds(record):
    """Typed nonempty trail, or explicit missing segments with an owner route.

    Nonemptiness is a pilot inhabitation choice, not a prohibition of the
    source expression's empty sequence. Missing/unrecorded is not asserted
    to mean historically no provenance.
    """
    path = record["provenance_path"]
    if not path:
        return False
    for step in path:
        if step.get("missing") is True:
            if not all(nonempty(step.get(k)) for k in ("residue_ref", "owner_route")):
                return False
        elif not all(nonempty(step.get(k)) for k in ("source", "relation", "operation", "owner", "posture")):
            return False
    return True


def authority_holds(record, roots):
    """A complete claim AND a matching independently supplied scoped root.

    Field presence is necessary, not sufficient. Root legitimacy is an
    explicit external assumption; neither an origin label nor a path grants it.
    """
    claim = record["authority_claim"]
    if claim is None:
        return False
    fields = ("scope", "owner", "surface", "object", "operation", "basis", "effect", "challenge_route")
    if not all(nonempty(claim.get(k)) for k in fields):
        return False
    if claim["object"] != record["id"] or claim["scope"] != "scope:pilot-local-use":
        return False
    return any(all(claim[k] == grant[k] for k in fields) for grant in roots)


def valid_move(move):
    before, after = move["before"], move["after"]
    if set(before) != set(AXES) or set(after) != set(AXES):
        return False
    intended, recorded = set(move["intended_axes"]), set(move["recorded_changes"])
    if not intended or not (intended | recorded) <= set(AXES):
        return False
    changed = {axis for axis in AXES if before[axis] != after[axis]}
    # No silent frame changes. Explicit couplings remain permissible.
    return changed <= intended | recorded and recorded <= changed


def subject(identity, path_mode, grant_present):
    step = {"source": "source:owner-authored-rule-v1", "relation": "derived-from",
            "operation": "import-for-review", "owner": "role:rule-owner", "posture": "candidate"}
    paths = {"unrecorded": [], "complete": [step],
             "routed-gap": [step, {"missing": True, "residue_ref": "residue:lost-import-step", "owner_route": "role:lineage-reviewer"}],
             "unrouted-gap": [step, {"missing": True, "residue_ref": "residue:lost-import-step"}]}
    claim = {"scope": "scope:pilot-local-use", "owner": "role:rule-owner", "surface": "surface:pilot-rules",
             "object": identity, "operation": "count-as-local-rule", "basis": "decision:hypothetical-owner-review-v1",
             "effect": "permitted-local-use", "challenge_route": "role:rule-challenge"}
    return {"id": identity, "provenance_path": copy.deepcopy(paths[path_mode]),
            "authority_claim": claim if grant_present else None}


def models(spec):
    """Exhaust all 64 record assignments and 3 moves (192 configurations)."""
    choices = list(itertools.product(spec["bounds"]["path_modes"], (False, True)))
    for pair in itertools.product(choices, repeat=len(spec["bounds"]["subjects"])):
        records = [subject(identity, *choice) for identity, choice in zip(spec["bounds"]["subjects"], pair)]
        # The Boolean chooses whether the hypothetical owner grant occurred.
        # Templates list permitted grants, not actual rights for every object.
        active = [grant for grant in spec["root_grants"] if any(r["authority_claim"] is not None and r["id"] == grant["object"] for r in records)]
        for move in spec["moves"]:
            yield {"records": copy.deepcopy(records), "root_grants": copy.deepcopy(active), "move": copy.deepcopy(move)}


def theory_holds(model, spec):
    for record in model["records"]:
        p = provenance_holds(record)
        a = authority_holds(record, model["root_grants"])
        if record["provenance_path"] and not p:
            return False
        if record["authority_claim"] is not None and not a:
            return False
        if spec["coupling"] == "routed-authority-requires-recorded-provenance" and a and not p:
            return False
        for restriction in spec["restrictions"]:
            if restriction == "provenance-implies-authority" and p and not a:
                return False
            if restriction == "no-authority" and a:
                return False
            if restriction == "no-provenance" and p:
                return False
    if "some-authority" in spec["restrictions"] and not any(authority_holds(r, model["root_grants"]) for r in model["records"]):
        return False
    return valid_move(model["move"])


def query_holds(model, query):
    pairs = [(provenance_holds(r), authority_holds(r, model["root_grants"])) for r in model["records"]]
    if query == "combined-satisfiability":
        return True
    if query == "required-inhabitation":
        return any(p for p, a in pairs) and any(a for p, a in pairs) and valid_move(model["move"])
    if query == "provenance-without-authority":
        return query_holds(model, "required-inhabitation") and any(p and not a for p, a in pairs)
    if query == "permitted-overlap":
        return any(p and a for p, a in pairs)
    raise ValueError("unsupported query: " + query)


def structural_issues(spec):
    supported = {"provenance-implies-authority", "no-authority", "some-authority", "no-provenance"}
    if spec.get("profile") != "python-finite-governance-v1-candidate":
        return "unsupported", "unsupported-profile"
    if spec.get("coupling") not in ("none", "routed-authority-requires-recorded-provenance") or not set(spec.get("restrictions", [])) <= supported:
        return "unsupported", "unsupported-logic"
    expected_bounds = {"subjects": ["artifact:import-review", "artifact:local-rule"],
                       "path_modes": ["unrecorded", "complete", "routed-gap", "unrouted-gap"]}
    if spec.get("bounds") != expected_bounds:
        return "unsupported", "unsupported-domain"
    if spec.get("required_obligations") != list(OBLIGATIONS):
        return "unknown", "missing-or-substituted-obligation"
    if set(spec["required_dependencies"]) != set(DEPENDENCIES) or set(spec["dependencies"]) != set(DEPENDENCIES):
        return "unknown", "missing-dependency"
    try:
        registry = load(LAB / "authority/definitions/registry.json")
    except (OSError, ValueError):
        return "unknown", "missing-or-malformed-registry"
    for identity in spec["required_dependencies"]:
        dep = spec["dependencies"][identity]
        if registry["current_lookup"].get(identity) != dep["version_ref"]:
            return "stale", "definition-version-changed"
        entry = next(e for e in registry["entries"] if e["definition_id"] + "@" + e["version"] == dep["version_ref"])
        if entry["path"] != dep["source_path"] or entry["sha256"] != dep["source_sha256"]:
            return "stale", "definition-registry-binding-changed"
        if not (LAB / dep["source_path"]).is_file():
            return "unknown", "missing-source"
        if sha(LAB / dep["source_path"]) != dep["source_sha256"]:
            return "stale", "definition-source-changed"
        if dep.get("translation_status") != "candidate-partial":
            return "unknown", "missing-translation"
    for binding in spec["bindings"]:
        if not (LAB / binding["path"]).is_file():
            return "unknown", "missing-bound-input"
        if sha(LAB / binding["path"]) != binding["sha256"]:
            return "stale", "bound-input-changed"
    return None


def run(spec, budget_seconds=5.0):
    issue = structural_issues(spec)
    if issue:
        return {"execution": "not-run", "readiness": "unresolved", "reason": issue[1],
                "outcome": issue[0], "obligations": [], "searched": 0}
    if budget_seconds <= 0:
        return {"execution": "timeout", "readiness": "unresolved", "reason": "search-budget-exhausted",
                "outcome": "unknown", "obligations": [], "searched": 0}
    start = time.monotonic()
    hits = {q: [] for q in OBLIGATIONS}
    searched = 0
    for model in models(spec):
        if time.monotonic() - start > budget_seconds:
            return {"execution": "timeout", "readiness": "unresolved", "outcome": "unknown",
                    "reason": "search-budget-exhausted", "searched": searched, "obligations": []}
        searched += 1
        if theory_holds(model, spec):
            for q in OBLIGATIONS:
                if query_holds(model, q):
                    hits[q].append(model)
    results = []
    viable = bool(hits["combined-satisfiability"])
    inhabited = bool(hits["required-inhabitation"])
    for q in OBLIGATIONS:
        gated = (q == "required-inhabitation" and not viable) or (q not in ("combined-satisfiability", "required-inhabitation") and not (viable and inhabited))
        results.append({"obligation_id": q, "outcome": "not-run" if gated else ("satisfied" if hits[q] else "violated"),
                        "evidence_strength": "finite-model-witness" if hits[q] and not gated else "bounded-search",
                        "models_found": len(hits[q]) if not gated else None,
                        "witness": hits[q][0] if hits[q] and not gated else None,
                        "ceiling": "Exact finite candidate theory only; no mechanized universal theorem."})
    return {"execution": "completed", "currentness": "current", "searched": searched,
            "outcome": "satisfied" if all(q["outcome"] == "satisfied" for q in results) else "violated",
            "readiness": "candidate-checks-satisfied-review-pending" if all(q["outcome"] == "satisfied" for q in results) else "failed-requirement",
            "obligations": results}


def bundle():
    spec = load(HERE / "interpretation.json")
    variants = [("positive", None), ("collapse", "provenance-implies-authority"),
                ("contradiction", ("some-authority", "no-authority")), ("vacuity", "no-provenance"),
                ("missing-dependency", None), ("missing-translation", None), ("stale", None),
                ("unsupported", None), ("timeout", None)]
    cases = []
    for name, restriction in variants:
        candidate = copy.deepcopy(spec)
        if restriction:
            candidate["restrictions"] = list(restriction) if isinstance(restriction, tuple) else [restriction]
        first = candidate["required_dependencies"][0]
        if name == "missing-dependency":
            del candidate["dependencies"][first]
        if name == "missing-translation":
            candidate["dependencies"][first]["translation_status"] = "not-translated"
        if name == "stale":
            candidate["dependencies"][first]["source_sha256"] = "0" * 64
        if name == "unsupported":
            candidate["restrictions"] = ["unbounded-temporal-fairness"]
        cases.append({"case": name, "input_sha256": canonical_digest(candidate), "input": candidate,
                      "result": run(candidate, 0 if name == "timeout" else 5.0)})
    return {"schema_version": "definition-assurance-evidence/v1-candidate", "authority_effect": "none",
            "provider": {"id": "python-finite-governance-v1-candidate", "python_version": platform.python_version(),
                         "executable": sys.executable, "executable_sha256": sha(sys.executable),
                         "checker_sha256": sha(__file__), "interpretation_sha256": sha(HERE / "interpretation.json"),
                         "contract_sha256": sha(HERE / "contracts.json"), "proof_kernel": None},
            "local_input_bindings": [{"path": name, "sha256": sha(HERE / name)} for name in
                                     ("checker.py", "replay.py", "test_pilot.py", "audit.py", "interpretation.json", "contracts.json", "context.json", "coverage.json", "tooling.json", "evidence.schema.json")],
            "assumptions": spec["assumptions"], "cases": cases, "fidelity": "owner-review-pending",
            "full_theory_consistency": "not-run-missing-180-translations",
            "claim_ceiling": "Candidate finite interpretation checks and witnesses only; no semantic admission or all-definition assurance."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = bundle()
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps({c["case"]: {"outcome": c["result"]["outcome"], "reason": c["result"].get("reason"),
                                  "searched": c["result"]["searched"]} for c in evidence["cases"]}, indent=2))
