#!/usr/bin/env python3
"""Validate Snapshot 0002 as an exact additive refresh of Snapshot 0001."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema


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
    registry = load(ROOT / "registry.json")
    inputs = candidate["inputs"]
    predecessor = load(LAB / inputs["predecessor_snapshot"]["path"])
    schema = load(LAB / inputs["schema"]["path"])
    decision = load(LAB / inputs["decision"]["path"])
    admission = load(LAB / inputs["admission_record"]["path"])
    checks = []

    def check(check_id, ok, detail):
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    input_results = {
        name: sha(LAB / binding["path"]) == binding["sha256"]
        for name, binding in inputs.items()
    }
    check("exact-input-digests", all(input_results.values()), input_results)
    check(
        "predecessor-immutable",
        sha(LAB / inputs["predecessor_snapshot"]["path"]) == "4f77443384a734acc9a1bd668f87941c45ae78291ecba1d420d3ac4eda2c578c"
        and predecessor["registry_id"] == inputs["predecessor_snapshot"]["registry_id"],
        inputs["predecessor_snapshot"],
    )
    errors = [error.message for error in jsonschema.Draft202012Validator(schema).iter_errors(registry)]
    check("registry-v2-schema", not errors, errors)
    check(
        "decision-and-admission-agree",
        decision["decision_id"] == admission["admission_decision_ref"]
        and decision["admitted_artifact_type"] == admission["artifact_type"]
        and decision["admitted_initial_instance"]["registry"]["sha256"] == inputs["predecessor_snapshot"]["sha256"],
        {"decision": decision["decision_id"], "admission": admission["admission_decision_ref"]},
    )

    prior_descriptor_count = len(predecessor["descriptors"])
    prior_contract_count = len(predecessor["admitted_contracts"])
    prior_overlay_count = len(predecessor["overlay_sources"])
    check(
        "exact-additive-delta",
        registry["descriptors"][:prior_descriptor_count] == predecessor["descriptors"]
        and registry["admitted_contracts"][:prior_contract_count] == predecessor["admitted_contracts"]
        and registry["overlay_sources"][:prior_overlay_count] == predecessor["overlay_sources"]
        and registry["duplicate_resolutions"] == predecessor["duplicate_resolutions"]
        and registry["candidate_lineage"] == predecessor["candidate_lineage"]
        and len(registry["descriptors"]) == prior_descriptor_count + 1
        and len(registry["admitted_contracts"]) == prior_contract_count + 1
        and len(registry["overlay_sources"]) == prior_overlay_count + 1,
        candidate["delta_contract"],
    )
    prior_map = dict(registry["current_by_identity"])
    prior_map.pop("cal.artifact-type.artifact-type-registry")
    predecessor_without_replaced = dict(predecessor["current_by_identity"])
    predecessor_without_replaced.pop("cal.artifact-type.artifact-type-registry", None)
    check(
        "single-current-map-update",
        prior_map == predecessor_without_replaced
        and registry["current_by_identity"]["cal.artifact-type.artifact-type-registry"] == "cal.artifact-type.artifact-type-registry/v2",
        {"before": predecessor["current_by_identity"].get("cal.artifact-type.artifact-type-registry"), "after": registry["current_by_identity"]["cal.artifact-type.artifact-type-registry"]},
    )
    added_descriptor = registry["descriptors"][-1]
    added_contract = registry["admitted_contracts"][-1]
    check(
        "registry-v2-self-inclusion",
        added_descriptor["artifact_type_ref"] == added_contract["artifact_type_ref"] == "cal.artifact-type.artifact-type-registry/v2"
        and added_descriptor["effective_state"] == added_contract["lifecycle_state"] == "admitted-current"
        and added_descriptor["effective_decision_refs"] == [decision["decision_id"]]
        and added_descriptor["descriptor_sha256"] == added_contract["artifact_sha256"] == inputs["artifact_type_contract"]["sha256"]
        and added_descriptor["schema_sha256"] == added_contract["schema_sha256"] == inputs["schema"]["sha256"],
        {"descriptor": added_descriptor, "contract": added_contract},
    )
    expected_inventory = {
        "admitted_contract_count": 34,
        "admitted_current_count": 29,
        "admitted_historical_count": 5,
        "descriptor_count": 57,
        "descriptor_declared_ref_count": 50,
        "descriptor_identity_count": 46,
        "descriptor_resolved_ref_count": 52,
        "duplicate_resolution_count": 2,
        "semantic_binding_counts": {"admitted-successor-required": 1, "candidate-rebind-required": 4, "current-as-declared": 52},
        "state_counts": {"admitted-current": 22, "admitted-historical": 5, "candidate-unadmitted": 28, "resolved-duplicate": 2},
    }
    check("inventory-cardinality", registry["inventory"] == expected_inventory, registry["inventory"])
    check(
        "candidate-has-no-authority-effect",
        candidate["authority_effect"] == registry["authority_effect"] == "none"
        and candidate["status"] == "candidate-owner-review-open"
        and registry["status"] == "candidate-postimage",
        {"candidate": candidate["status"], "registry": registry["status"], "authority_effect": registry["authority_effect"]},
    )
    before = (ROOT / "REGISTRY.md").read_bytes()
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    check("deterministic-projection", before == (ROOT / "REGISTRY.md").read_bytes(), {"projection_sha256": sha(ROOT / "REGISTRY.md")})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-registry-snapshot-validation/v1",
        "candidate_id": candidate["candidate_id"],
        "result": result,
        "checks": checks,
        "output": {"path": candidate["output"]["path"], "sha256": sha(ROOT / "registry.json")},
        "claim_ceiling": "PASS proves this candidate is an exact schema-valid additive refresh of Snapshot 0001 with Decision 0068. It does not admit Snapshot 0002 or grant any additional authority effect.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    print(json.dumps({"result": result, "checks": len(checks), "registry_sha256": receipt["output"]["sha256"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
