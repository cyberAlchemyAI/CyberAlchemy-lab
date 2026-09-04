#!/usr/bin/env python3
"""Validate the CTX07 two-type candidate closure and normalization invariants."""

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE = ROOT / "artifact-type-pack.json"
OUTPUT = ROOT / "ARTIFACT-TYPE-PACK.md"
RECEIPT = ROOT / "receipts/validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(value)
    return value


def main() -> int:
    pack = load(SOURCE)
    checks = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("pack-identity", pack.get("pack_id") == "CAL-ARTIFACT-TYPE-PACK-CTX07-0002", pack.get("pack_id"))
    check("construction-authorization", pack["construction_authorization"]["token"] == "AUTHOR-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPES-V2" and pack["authority_effect"] == "none" and pack["status"].startswith("candidate-"), pack["construction_authorization"])
    items = pack["artifact_types"]
    check("two-type-closure", [item["slug"] for item in items] == ["bounded-context", "context-map"], [item["artifact_type_ref"] for item in items])
    for field in ("slug", "artifact_type_ref", "definition_ref", "identity_field", "artifact_path", "schema_path", "receipt_path"):
        values = [item[field] for item in items]
        check(f"unique-{field.replace('_', '-')}", len(values) == len(set(values)), values)

    material_results = []
    artifacts = {}
    receipts = {}
    for item in items:
        artifact_path = LAB / item["artifact_path"]
        schema_path = LAB / item["schema_path"]
        human_path = LAB / item["human_path"]
        receipt_path = LAB / item["receipt_path"]
        predecessor_path = LAB / item["predecessor_path"]
        artifacts[item["slug"]] = load(artifact_path)
        receipts[item["slug"]] = load(receipt_path)
        result = {
            "slug": item["slug"],
            "direct_path": item["artifact_path"] == f"authority/artifact-types/{item['slug']}/v2/artifact.json",
            "artifact_current": sha(artifact_path) == item["artifact_sha256"],
            "schema_current": sha(schema_path) == item["schema_sha256"],
            "human_current": sha(human_path) == item["human_sha256"],
            "receipt_current": sha(receipt_path) == item["receipt_sha256"],
            "receipt_pass": receipts[item["slug"]].get("result") == "PASS" and receipts[item["slug"]].get("summary", {}).get("failed") == 0 and receipts[item["slug"]].get("summary", {}).get("total") == item["validation_checks"],
            "predecessor_current": sha(predecessor_path) == item["predecessor_sha256"],
        }
        if "membership_projection_path" in item:
            result["membership_projection_current"] = sha(LAB / item["membership_projection_path"]) == item["membership_projection_sha256"]
        material_results.append(result)
    check("all-materials-current", all(all(value for key, value in item.items() if key != "slug") for item in material_results), material_results)
    check("all-candidates-no-authority", all(value["status"] == "candidate-unadmitted" and value["authority_effect"] == "none" for value in artifacts.values()), {key: {"status": value["status"], "authority_effect": value["authority_effect"]} for key, value in artifacts.items()})

    shared_results = []
    for field in ("schema", "generator", "validator"):
        path = LAB / pack["shared_mechanics"][f"{field}_path"]
        shared_results.append({"field": field, "expected": pack["shared_mechanics"][f"{field}_sha256"], "actual": sha(path), "current": sha(path) == pack["shared_mechanics"][f"{field}_sha256"]})
    check("shared-mechanics-current", all(item["current"] for item in shared_results), shared_results)

    prerequisite_results = []
    for name, item in pack["admitted_prerequisites"].items():
        actual = sha(LAB / item["path"])
        prerequisite_results.append({"name": name, "expected": item["sha256"], "actual": actual, "current": actual == item["sha256"]})
    check("admitted-prerequisites-current", all(item["current"] for item in prerequisite_results), prerequisite_results)
    registry = load(LAB / pack["admitted_prerequisites"]["definition_registry"]["path"])
    check("current-definition-lookup", registry["current_lookup"]["cal.definition.bounded-context"] == "cal.definition.bounded-context@2.0.0-candidate.1" and registry["current_lookup"]["cal.definition.context-map"] == "cal.definition.context-map@2.0.0-candidate.1", registry["current_lookup"])

    bc_fields = set(artifacts["bounded-context"]["instance_contract"]["required_semantic_fields"])
    bc_forbidden = set(artifacts["bounded-context"]["instance_contract"]["forbidden_canonical_fields"])
    cm_fields = set(artifacts["context-map"]["instance_contract"]["required_semantic_fields"])
    check("bounded-context-backreferences-forbidden", "context_map_refs" not in bc_fields and {"context_map_refs", "map_membership", "canonical_reverse_membership_index"}.issubset(bc_forbidden), {"required": sorted(bc_fields), "forbidden": sorted(bc_forbidden)})
    check("context-map-sole-relation-owner", {"context_refs", "relationships"}.issubset(cm_fields) and "relationships" not in bc_fields and artifacts["context-map"]["instance_contract"]["canonical_relation_owner"] is True, {"bounded": sorted(bc_fields), "map": sorted(cm_fields)})

    projection_item = next(item for item in items if item["slug"] == "context-map")
    projection = load(LAB / projection_item["membership_projection_path"])
    check("reverse-membership-generated-only", projection["canonical"] is False and projection["authority_effect"] == "none" and all(source["path"].endswith("/map.json") and sha(LAB / source["path"]) == source["sha256"] for source in projection["generated_from"]), projection)
    generator = module("ctx07_generator_pack", LAB / pack["shared_mechanics"]["generator_path"])
    regenerated = generator.build_membership_index([(source["path"], load(LAB / source["path"]), source["sha256"]) for source in projection["generated_from"]])
    check("reverse-membership-rebuild-parity", regenerated == projection, regenerated)
    check("cross-type-invariants-complete", [item["invariant_id"] for item in pack["cross_type_invariants"]] == ["CTX07-X01", "CTX07-X02", "CTX07-X03", "CTX07-X04", "CTX07-X05"], pack["cross_type_invariants"])
    check("promotion-remains-gated", pack["promotion_gate"]["required_role"] == "artifact-type-owner" and pack["promotion_gate"]["current_state"].startswith("not_evaluable"), pack["promotion_gate"])
    check("no-context-instance-materials", all(not item["artifact_path"].startswith("contexts/") for item in items), [item["artifact_path"] for item in items])
    renderer = module("ctx07_pack_renderer", ROOT / "render.py")
    check("pack-projection-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == renderer.render(pack), str(OUTPUT.relative_to(LAB)))

    failed = [item for item in checks if item["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-artifact-type-pack-validation/v1",
        "subject": pack["pack_id"],
        "result": result,
        "authority_effect": "evidence-only-does-not-admit-artifact-types",
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "promotion_eligibility": "eligible-for-exact-artifact-type-owner-review" if result == "PASS" else "blocked",
        "materials": {"pack_sha256": sha(SOURCE), "projection_sha256": sha(OUTPUT)},
        "claim_ceiling": pack["claim_ceiling"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX07_ARTIFACT_TYPE_PACK_VALIDATION={result}")
    print(f"PROMOTION_ELIGIBILITY={receipt['promotion_eligibility']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    for item in failed:
        print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
