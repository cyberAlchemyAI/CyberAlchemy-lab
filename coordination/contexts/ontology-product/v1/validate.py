#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    context = load(ROOT / "coordination-context.json")
    schema = load(LAB / "tooling/schemas/ctx01/v1/schema.json")
    schema["$ref"] = "#/$defs/coordinationContext"
    errors = sorted(error.message for error in Draft202012Validator(schema).iter_errors(context))
    check("CC-01-CLOSED-SCHEMA", not errors, errors)
    check("CC-02-PRODUCT-ANCHOR", context["product_ref"] == "CA2-PRODUCT-ONTOLOGY/v1" and context["project_ref"] is None and context["goal_ref"] is None, {key: context[key] for key in ("product_ref", "project_ref", "goal_ref")})

    governance = load(LAB / "contexts/governance/v3/context.json")
    lifecycle = load(LAB / "contexts/ontology-lifecycle/v3/context.json")
    context_map = load(LAB / "contexts/maps/governance-ontology-lifecycle/v2/map.json")
    expected_refs = ["cal.context.governance/v2", "cal.context.ontology-lifecycle/v2"]
    check("CC-03-EXACT-CONTEXT-ENDPOINTS", context["bounded_context_refs"] == expected_refs and context_map["context_refs"] == expected_refs, {"coordination": context["bounded_context_refs"], "map": context_map["context_refs"]})
    check("CC-04-CONTEXT-IDENTITY-CURRENT", governance["context_id"] == "cal.context.governance" and governance["version"].startswith("2.0.0-") and lifecycle["context_id"] == "cal.context.ontology-lifecycle" and lifecycle["version"].startswith("2.0.0-"), {"governance": governance["version"], "ontology_lifecycle": lifecycle["version"]})
    check("CC-05-CONTEXT-MAP-OWNS-RELATIONSHIP", "context_map_refs" not in context and len(context_map["relationships"]) == 1 and context_map["relationships"][0]["source_context_ref"] == expected_refs[0] and context_map["relationships"][0]["target_context_ref"] == expected_refs[1], context_map["relationships"])
    forbidden = {"domain_model_ref", "ubiquitous_language_ref", "context_map_refs"}
    check("CC-06-NO-BOUNDED-CONTEXT-COLLAPSE", not forbidden.intersection(context), sorted(forbidden.intersection(context)))
    check("CC-07-NO-AUTHORITY-EFFECT", context["status"] == "candidate-unadmitted" and context["authority_effect"] == "none", {"status": context["status"], "authority_effect": context["authority_effect"]})

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("coordination_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    projection = ROOT / "COORDINATION-CONTEXT.md"
    rendered = module.render(context)
    check("CC-08-GENERATOR-BINDING", context["source_direction"]["generator_sha256"] == sha(generator_path), {"expected": context["source_direction"]["generator_sha256"], "actual": sha(generator_path)})
    check("CC-09-PROJECTION-PARITY", projection.is_file() and projection.read_text(encoding="utf-8") == rendered, sha(projection) if projection.is_file() else "missing")

    failures = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-coordination-validation/v1",
        "coordination_context_id": context["coordination_context_id"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "summary": {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks)},
        "checks": checks,
        "materials": {
            "coordination_context_sha256": sha(ROOT / "coordination-context.json"),
            "projection_sha256": sha(projection) if projection.is_file() else None,
            "governance_context_sha256": sha(LAB / "contexts/governance/v3/context.json"),
            "ontology_lifecycle_context_sha256": sha(LAB / "contexts/ontology-lifecycle/v3/context.json"),
            "context_map_sha256": sha(LAB / "contexts/maps/governance-ontology-lifecycle/v2/map.json")
        },
        "claim_ceiling": "PASS proves exact candidate context coordination and generated projection parity only; it does not admit a context, map, Product, or runtime."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
