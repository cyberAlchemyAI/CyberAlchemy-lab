#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    proposal = load(ROOT / "proposal.json")
    artifact_manifest = load(ROOT / "artifact-type-admission-manifest.json")
    relation_registry = load(ROOT / "relation-kind-registry-postimage.json")
    endpoints = load(ROOT / "endpoint-inventory-postimage.json")
    artifact_registry = load(ROOT / "artifact-type-registry-postimage.json")
    governed_postimage = load(ROOT / "governed-model-instance-postimage.json")
    checks = []

    def check(check_id, outcome, detail):
        checks.append({"check_id": check_id, "result": "PASS" if outcome else "BLOCK", "detail": detail})

    rows = []
    for entry in artifact_manifest["entries"]:
        receipt = load(LAB / entry["receipt_path"])
        rows.append(
            {
                "ref": entry["artifact_type_ref"],
                "artifact": sha(LAB / entry["artifact_path"]) == entry["artifact_sha256"],
                "schema": sha(LAB / entry["schema_path"]) == entry["schema_sha256"],
                "receipt": sha(LAB / entry["receipt_path"]) == entry["receipt_sha256"] and receipt.get("result") == "PASS",
                "candidate": load(LAB / entry["artifact_path"]).get("status") == "candidate-unadmitted",
            }
        )
    check(
        "exact-93-artifact-types-current",
        len(rows) == 93
        and len({entry["artifact_type_ref"] for entry in artifact_manifest["entries"]}) == 93
        and len({entry["artifact_type_id"] for entry in artifact_manifest["entries"]}) == 93
        and all(all(value for key, value in row.items() if key != "ref") for row in rows),
        rows,
    )

    relation_manifest = load(LAB / proposal["inputs"]["relation_kind_manifest"]["path"])
    relation_rows = []
    for entry in relation_manifest["entries"]:
        relation_rows.append(
            {
                "id": entry["relation_kind_id"],
                "current": sha(LAB / entry["instance_path"]) == entry["instance_sha256"],
                "typed_example_excluded": entry["typed_relation_example_admission"] == "excluded",
            }
        )
    check(
        "exact-40-relation-kinds-current",
        len(relation_rows) == 40
        and all(all(value for key, value in row.items() if key != "id") for row in relation_rows)
        and relation_manifest["typed_relation_instances_to_admit"] == 0,
        relation_rows,
    )
    check(
        "all-101-endpoints-resolved",
        endpoints["counts"]["named_endpoint_kinds"] == endpoints["counts"]["admitted-current"] == 101
        and endpoints["counts"]["referenced-no-canonical-carrier"] == endpoints["counts"]["wildcard_tokens"] == 0
        and len(endpoints["entries"]) == 101
        and all(entry["lifecycle_state"] == "admitted-current" and entry["carrier_ref"] and entry["path"] for entry in endpoints["entries"]),
        endpoints["counts"],
    )

    final_refs = {entry["artifact_type_ref"] for entry in artifact_manifest["entries"]}
    new_contracts = [entry for entry in artifact_registry["admitted_contracts"] if entry["admission_decision_ref"] == proposal["decision_id"]]
    check(
        "artifact-registry-postimage-complete",
        len(new_contracts) == 93
        and final_refs == {entry["artifact_type_ref"] for entry in new_contracts}
        and all(artifact_registry["current_by_identity"].get(entry["artifact_type_id"]) == entry["artifact_type_ref"] for entry in artifact_manifest["entries"]),
        {"new_contracts": len(new_contracts), "current_identities": len(artifact_registry["current_by_identity"]), "inventory": artifact_registry["inventory"]},
    )
    check(
        "relation-registry-postimage-complete",
        relation_registry["count"] == 40
        and len(relation_registry["entries"]) == 40
        and relation_registry["typed_relation_instances_admitted"] == 0
        and all(entry["lifecycle_state"] == "admitted-current" and entry["admission_decision_ref"] == proposal["decision_id"] for entry in relation_registry["entries"]),
        {"count": relation_registry["count"]},
    )

    stages = proposal["transaction"]["ordered_stages"]
    check(
        "atomic-dependency-order",
        proposal["transaction"]["atomic"] is True
        and [stage["order"] for stage in stages] == [1, 2, 3, 4, 5]
        and "93" in stages[0]["effect"]
        and "endpoints" in stages[1]["effect"]
        and "40" in stages[2]["effect"]
        and "one exact Governed Model" in stages[3]["effect"],
        stages,
    )
    expected_effects = {
        "artifact_types_admitted": 93,
        "artifact_type_predecessors_to_historical": 9,
        "relation_kinds_admitted": 40,
        "governed_model_instances_admitted": 1,
        "ordinary_artifact_instances_admitted": 1,
        "typed_relation_instances_admitted": 0,
        "consumer_activations": 0,
        "runtime_activations": 0,
        "migrations": 0,
        "cutovers": 0,
    }
    check("closed-effect-envelope", proposal["proposed_effects"] == expected_effects, proposal["proposed_effects"])
    check(
        "proposal-remains-no-effect",
        proposal["authorization_present"] is False
        and proposal["authority_effect"] == "none"
        and artifact_manifest["authority_effect"]
        == relation_registry["authority_effect"]
        == endpoints["authority_effect"]
        == artifact_registry["authority_effect"]
        == "none",
        {"proposal_authorization_present": proposal["authorization_present"], "external_authorization_file": (ROOT.parent / "authorization.json").exists()},
    )

    instance_ref = proposal["inputs"]["integrated_model_instance"]
    instance = load(LAB / instance_ref["path"])
    schema = load(LAB / "authority/artifact-types/governed-model/v1/schema.json")
    schema_errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda error: list(error.path))
    contract_path, contract_sha = instance["payload"]["contract_ref"].split("#sha256=", 1)
    check(
        "one-governed-model-instance-exact",
        sha(LAB / instance_ref["path"]) == instance_ref["sha256"]
        and not schema_errors
        and instance["node_id"] == governed_postimage["record_id"]
        and governed_postimage["artifact_type_ref"] == "cal.artifact-type.governed-model/v1"
        and governed_postimage["lifecycle_state"] == "admitted-current"
        and governed_postimage["source_record"]["sha256"] == instance_ref["sha256"]
        and governed_postimage["contract"]["path"] == contract_path
        and governed_postimage["contract"]["sha256"] == contract_sha == proposal["inputs"]["integrated_model"]["sha256"]
        and governed_postimage["contract"]["rule_count"] == 16
        and governed_postimage["runtime_activations"] == 0,
        {
            "record_id": governed_postimage["record_id"],
            "record_sha256": instance_ref["sha256"],
            "contract_sha256": contract_sha,
            "schema_errors": [error.message for error in schema_errors],
        },
    )

    postimages = [
        {"path": item["path"], "current": sha(LAB / item["path"]) == item["sha256"]}
        for item in proposal["postimages"].values()
    ]
    check("postimages-digest-bound", all(item["current"] for item in postimages), postimages)
    integrated_ref = proposal["inputs"]["integrated_model"]
    integrated = load(LAB / integrated_ref["path"])
    check(
        "integrated-model-bound",
        sha(LAB / integrated_ref["path"]) == integrated_ref["sha256"]
        and integrated["counts"]["projected_artifact_type_admissions"] == 93
        and integrated["admission_sequence"]["governed_model_instance_decision_target"] == 1
        and integrated["admission_sequence"]["runtime_change_authorized"] is False,
        integrated_ref,
    )

    generated_names = (
        "artifact-type-admission-manifest.json",
        "artifact-type-registry-postimage.json",
        "relation-kind-registry-postimage.json",
        "endpoint-inventory-postimage.json",
        "governed-model-instance-postimage.json",
        "proposal.json",
        "PROPOSAL.md",
    )
    before = [(ROOT / name).read_bytes() for name in generated_names]
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
    after = [(ROOT / name).read_bytes() for name in generated_names]
    check("deterministic-proposal", before == after, {"proposal_sha256": sha(ROOT / "proposal.json"), "review_sha256": sha(ROOT / "PROPOSAL.md")})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    materials = {
        "proposal_sha256": sha(ROOT / "proposal.json"),
        "artifact_type_manifest_sha256": sha(ROOT / "artifact-type-admission-manifest.json"),
        "artifact_type_registry_sha256": sha(ROOT / "artifact-type-registry-postimage.json"),
        "relation_kind_registry_sha256": sha(ROOT / "relation-kind-registry-postimage.json"),
        "endpoint_inventory_sha256": sha(ROOT / "endpoint-inventory-postimage.json"),
        "governed_model_instance_sha256": sha(ROOT / "governed-model-instance-postimage.json"),
        "review_sha256": sha(ROOT / "PROPOSAL.md"),
    }
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-complete-model-admission-proposal-validation/v2",
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": materials,
        "claim_ceiling": "PASS proves the exact no-effect atomic proposal is current, dependency ordered, complete, and deterministic. It admits nothing.",
    }
    dump(ROOT / "validation.json", receipt)
    print(json.dumps({"result": result, "checks": len(checks), **materials}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
