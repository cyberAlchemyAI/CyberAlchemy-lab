#!/usr/bin/env python3
"""Validate completeness, exact bindings, and non-collapse of the Step 5 plan."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    candidate = load(ROOT / "candidate.json")
    plan = load(ROOT / "plan.json")
    audit = load(LAB / candidate["inputs"]["content_audit"]["path"])
    definitions = load(LAB / candidate["inputs"]["definition_registry"]["path"])
    endpoints = load(LAB / candidate["inputs"]["endpoint_inventory"]["path"])
    registry = load(LAB / candidate["inputs"]["registry_snapshot_0002"]["path"])
    relation_model = load(LAB / candidate["inputs"]["relation_model"]["path"])
    checks = []

    def check(check_id, ok, detail):
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    input_results = {name: sha(LAB / binding["path"]) == binding["sha256"] for name, binding in candidate["inputs"].items()}
    check("exact-source-bindings", all(input_results.values()), input_results)
    actionable = {entry["artifact_type_ref"] for entry in audit["entries"] if entry["content_posture"] in {"admitted-current-remediation-required", "candidate-revision-required"}}
    planned = {entry["source_artifact_type_ref"] for entry in plan["existing_contract_actions"]}
    check("all-14-existing-actions-covered", len(actionable) == len(planned) == 14 and actionable == planned, sorted(actionable ^ planned))
    successor_count = sum(entry["action"] == "author-immutable-successor" for entry in plan["existing_contract_actions"])
    revision_count = sum(entry["action"] == "revise-unadmitted-candidate-in-place" for entry in plan["existing_contract_actions"])
    check("action-mode-separation", successor_count == 9 and revision_count == 5, {"immutable_successors": successor_count, "candidate_revisions": revision_count})
    predecessor_refs = {entry["artifact_type_ref"] for entry in registry["descriptors"]}
    successor_targets = [entry["target_artifact_type_ref"] for entry in plan["existing_contract_actions"] if entry["action"] == "author-immutable-successor"]
    check("successor-identities-are-new", len(successor_targets) == len(set(successor_targets)) and not (set(successor_targets) & predecessor_refs), successor_targets)

    missing = {entry["endpoint_kind"] for entry in endpoints["entries"] if entry["lifecycle_state"] == "referenced-no-canonical-carrier"}
    carrier_kinds = {entry["endpoint_kind"] for entry in plan["new_endpoint_carriers"]}
    check("all-22-missing-carriers-covered", len(missing) == len(carrier_kinds) == 22 and missing == carrier_kinds, sorted(missing ^ carrier_kinds))
    definition_results = []
    for item in plan["new_endpoint_carriers"]:
        binding = item["semantic_definition_binding"]
        definition_id = binding["definition_ref"].split("@", 1)[0]
        definition_results.append({
            "endpoint_kind": item["endpoint_kind"],
            "current": definitions["current_lookup"].get(definition_id) == binding["definition_ref"],
            "digest": sha(LAB / binding["path"]) == binding["sha256"],
            "distinct_neighbors": len(item["must_remain_distinct_from"]) >= 1 and item["endpoint_kind"] not in item["must_remain_distinct_from"],
        })
    check("carrier-definitions-current-and-noncollapsed", all(all(value for key, value in row.items() if key != "endpoint_kind") for row in definition_results), definition_results)
    carrier_refs = [entry["artifact_type_ref"] for entry in plan["new_endpoint_carriers"]]
    check("new-carrier-identities-distinct", len(carrier_refs) == len(set(carrier_refs)) == 22 and not (set(carrier_refs) & predecessor_refs), carrier_refs)

    allowed = {
        entry["relation_kind_id"]: {(pair["source_kind"], pair["target_kind"]) for pair in entry["allowed_endpoint_pairs"]}
        for entry in relation_model["entries"]
    }
    example_results = []
    for example in plan["realistic_examples"]:
        relation = example["relation"]
        pair = (relation["source_kind"], relation["target_kind"])
        example_results.append({"example_id": example["example_id"], "declared": pair in allowed[relation["relation_kind_ref"]], "authority_none": example["authority_effect"] == "none"})
    check("realistic-examples-use-declared-pairs", len(example_results) == 6 and all(row["declared"] and row["authority_none"] for row in example_results), example_results)
    check(
        "closed-relation-universe-preserved",
        relation_model["counts"]["declared_endpoint_pairs"] == 147
        and endpoints["counts"]["wildcard_tokens"] == 0
        and endpoints["counts"]["named_endpoint_kinds"] == 50,
        {"relation_model": relation_model["counts"], "endpoint_inventory": endpoints["counts"]},
    )
    check(
        "candidate-no-authority-effect",
        candidate["authority_effect"] == plan["authority_effect"] == "none"
        and candidate["status"] == "candidate-plan-ready-for-owner-review"
        and plan["status"] == "candidate-complete-awaiting-owner-review",
        {"candidate": candidate["status"], "plan": plan["status"]},
    )
    before_json = (ROOT / "plan.json").read_bytes()
    before_md = (ROOT / "PLAN.md").read_bytes()
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    check("deterministic-plan-and-projection", before_json == (ROOT / "plan.json").read_bytes() and before_md == (ROOT / "PLAN.md").read_bytes(), {"plan_sha256": sha(ROOT / "plan.json"), "projection_sha256": sha(ROOT / "PLAN.md")})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-carrier-closure-validation/v1",
        "candidate_id": candidate["candidate_id"],
        "result": result,
        "checks": checks,
        "plan": {"path": candidate["output"]["path"], "sha256": sha(ROOT / "plan.json")},
        "claim_ceiling": "PASS proves the plan covers the exact 14 current contract actions and 22 missing endpoint carriers with current Definitions and declared relation examples. It does not prove the planned postimages exist or admit any contract.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(json.dumps({"result": result, "checks": len(checks), "plan_sha256": receipt["plan"]["sha256"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
