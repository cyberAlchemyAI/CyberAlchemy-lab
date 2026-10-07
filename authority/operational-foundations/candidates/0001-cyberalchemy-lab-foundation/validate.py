#!/usr/bin/env python3
"""Validate the operational foundation candidate against admitted Lab contracts."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
MANIFEST = ROOT / "foundation.json"
RECEIPT = ROOT / "receipts" / "validation.json"
REGISTRY = LAB / "authority/admissions/definition-complete-lab-model/v1/artifact-type-registry.json"
RELATION_REGISTRY = LAB / "authority/admissions/definition-complete-lab-model/v1/relation-kind-registry.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_value(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def schema_errors(record: dict[str, Any], schema_path: Path) -> list[str]:
    schema = load(schema_path)
    validator_class = jsonschema.validators.validator_for(schema)
    validator_class.check_schema(schema)
    errors = []
    for error in sorted(validator_class(schema).iter_errors(record), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(item) for item in error.absolute_path) or "$"
        errors.append(f"{location}: {error.message}")
    return errors


def generated_snapshot() -> dict[str, str]:
    paths = [ROOT / "foundation.json", ROOT / "FOUNDATION.md", ROOT / "history-declarations.json"]
    for folder in (ROOT / "instances" / "artifacts", ROOT / "instances" / "typed-relations"):
        paths.extend(sorted(path for path in folder.glob("*.json") if path.is_file()))
    return {str(path.relative_to(ROOT)): sha(path) for path in paths}


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, result: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if result else "FAIL", "detail": detail})

    before = generated_snapshot()
    built = subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=LAB, text=True, capture_output=True, check=False)
    after = generated_snapshot()
    check("deterministic-build", built.returncode == 0 and before == after, {"returncode": built.returncode, "stdout": built.stdout.strip(), "stderr": built.stderr.strip(), "changed": sorted(set(before) | set(after)) if before != after else []})

    manifest = load(MANIFEST)
    registry = load(REGISTRY)
    relation_registry = load(RELATION_REGISTRY)
    contracts = {item["artifact_type_ref"]: item for item in registry["admitted_contracts"] if item["lifecycle_state"] == "admitted-current"}
    kinds = {item["relation_kind_id"]: item for item in relation_registry["entries"] if item["lifecycle_state"] == "admitted-current"}

    input_results = []
    for name, binding in manifest["inputs"].items():
        current = sha(LAB / binding["path"])
        input_results.append({"name": name, "declared": binding["sha256"], "current": current, "match": current == binding["sha256"]})
    check("admitted-inputs-current", all(item["match"] for item in input_results), input_results)

    artifact_records: dict[str, dict[str, Any]] = {}
    artifact_entries = {item["identity_ref"]: item for item in manifest["artifacts"]}
    artifact_validation = []
    for identity, entry in artifact_entries.items():
        record = load(LAB / entry["path"])
        contract = contracts.get(entry["carrier_type_ref"])
        errors = [] if contract else ["carrier is not admitted-current"]
        if contract:
            errors.extend(schema_errors(record, LAB / contract["schema_path"]))
        if sha(LAB / entry["path"]) != entry["sha256"]:
            errors.append("manifest digest mismatch")
        actual_identity = record.get("node_id") or record.get("product_id") or record.get("project_id")
        if actual_identity != identity:
            errors.append("identity mismatch")
        if record.get("authority_effect") != "none":
            errors.append("candidate authority_effect is not none")
        artifact_records[identity] = record
        artifact_validation.append({"identity_ref": identity, "carrier_type_ref": entry["carrier_type_ref"], "errors": errors})
    check("artifact-contracts", len(artifact_entries) == 9 and all(not item["errors"] for item in artifact_validation), artifact_validation)

    typed_contract = contracts["cal.artifact-type.typed-relation/v2"]
    relation_validation = []
    relation_records: dict[str, dict[str, Any]] = {}
    for entry in manifest["typed_relations"]:
        record = load(LAB / entry["path"])
        payload = record["payload"]
        kind_entry = kinds.get(payload["relation_kind_ref"])
        errors = schema_errors(record, LAB / typed_contract["schema_path"])
        if sha(LAB / entry["path"]) != entry["sha256"]:
            errors.append("manifest digest mismatch")
        if kind_entry is None:
            errors.append("Relation Kind is not admitted-current")
        else:
            kind_record = load(LAB / kind_entry["instance_path"])
            pair = {"source_kind": payload["source"]["kind"], "target_kind": payload["target"]["kind"]}
            if pair not in kind_record["payload"]["allowed_endpoint_pairs"]:
                errors.append(f"undeclared endpoint pair {pair}")
            required = set(kind_record["payload"]["qualifier_contract"]["required_axes"])
            actual = set(payload["qualifiers"])
            if actual != required:
                errors.append(f"qualifier axes {sorted(actual)} != {sorted(required)}")
        for side in ("source", "target"):
            endpoint = payload[side]
            local = artifact_entries.get(endpoint["ref"])
            if local is None:
                errors.append(f"{side} endpoint missing")
            elif local["semantic_kind"] != endpoint["kind"] or local["version_ref"] != endpoint["version_ref"]:
                errors.append(f"{side} endpoint binding mismatch")
        if record.get("authority_effect") != "none" or payload.get("relation_lifecycle_state") != "candidate":
            errors.append("candidate relation authority/lifecycle mismatch")
        relation_records[record["node_id"]] = record
        relation_validation.append({"relation_id": record["node_id"], "relation_kind_ref": payload["relation_kind_ref"], "errors": errors})
    check("typed-relation-closure", len(relation_records) == 13 and all(not item["errors"] for item in relation_validation), relation_validation)

    embedded_errors = []
    for identity, record in artifact_records.items():
        entry = artifact_entries[identity]
        if "relation_refs" not in record:
            continue
        descriptor = load(LAB / contracts[entry["carrier_type_ref"]]["artifact_path"])
        roles = descriptor.get("relation_roles", [])
        for binding in record["relation_refs"]:
            matching = []
            for relation in relation_records.values():
                payload = relation["payload"]
                endpoint = payload["source"] if binding["direction"] == "source" else payload["target"]
                counterpart = payload["target"] if binding["direction"] == "source" else payload["source"]
                if endpoint["ref"] == identity and payload["relation_kind_ref"] == binding["relation_kind_ref"] and counterpart["ref"] == binding["counterpart_ref"] and counterpart["kind"] == binding["counterpart_kind"]:
                    matching.append(relation["node_id"])
            role_ok = any(role["relation_kind_ref"] == binding["relation_kind_ref"] and role["direction"] == binding["direction"] and binding["counterpart_kind"] in role["counterpart_kinds"] for role in roles)
            if len(matching) != 1 or not role_ok:
                embedded_errors.append({"identity": identity, "binding": binding, "matches": matching, "role_ok": role_ok})
    check("embedded-relation-bindings", not embedded_errors, embedded_errors or "All embedded bindings resolve one exact allowed Typed Relation")

    state = artifact_records["project-state:cyberalchemy-v2-to-lab-migration:decision-0070"]
    materials = [{"path": path, "sha256": sha(LAB / path)} for path in state["payload"]["artifact_refs"]]
    expected_state_digest = f"sha256:{digest_value(materials)}"
    state_ok = state["payload"]["state_digest"] == expected_state_digest and state["payload"]["cursor"] == "decision:0070"
    check("project-state-snapshot", state_ok, {"declared": state["payload"]["state_digest"], "calculated": expected_state_digest, "materials": materials})

    history_binding = manifest["history_declarations"]
    histories = load(LAB / history_binding["path"])
    refs = {item["history_ref"] for item in histories["streams"]}
    state_refs = {state["payload"]["semantic_history_ref"], state["payload"]["governance_history_ref"]}
    history_ok = sha(LAB / history_binding["path"]) == history_binding["sha256"] and refs == state_refs and all(item["cursor"] == 0 and item["state"] == "initialized-empty" and item["runtime_active"] is False for item in histories["streams"])
    check("history-bootstrap", history_ok, histories)

    expected_kinds = {"intent", "product", "product-thesis", "product-capability", "project", "policy", "challenge-contract", "project-state", "context"}
    actual_kinds = {item["semantic_kind"] for item in manifest["artifacts"]}
    excluded_present = sorted(actual_kinds & set(manifest["excluded_instances"]))
    minimal_ok = actual_kinds == expected_kinds and not excluded_present and manifest["counts"] == {"artifact_instances": 9, "typed_relation_instances": 13, "history_stream_declarations": 2, "runtime_activations": 0}
    check("minimal-real-foundation", minimal_ok, {"actual_kinds": sorted(actual_kinds), "excluded_present": excluded_present, "counts": manifest["counts"]})

    generation = manifest["generation_contracts"]
    generation_ok = set(generation) == {"project_state", "agent_context", "evidence", "ontology"} and all(generation.values())
    check("future-generation-contracts", generation_ok, generation)

    no_effect = manifest["authority_effect"] == "none" and manifest["status"] == "candidate-awaiting-admission" and manifest["counts"]["runtime_activations"] == 0
    check("candidate-authority-boundary", no_effect, {"status": manifest["status"], "authority_effect": manifest["authority_effect"], "runtime_activations": manifest["counts"]["runtime_activations"]})

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-operational-foundation-validation/v1",
        "result": result,
        "authority_effect": "none",
        "foundation_path": str(MANIFEST.relative_to(LAB)),
        "foundation_sha256": sha(MANIFEST),
        "checks": checks,
        "claim_ceiling": "PASS proves deterministic contract, relation, snapshot, and bootstrap closure only. Admission requires the exact Decision 0071 transaction.",
    }
    dump(RECEIPT, receipt)
    print(json.dumps({"result": result, "checks": len(checks), "foundation_sha256": receipt["foundation_sha256"]}, sort_keys=True))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
