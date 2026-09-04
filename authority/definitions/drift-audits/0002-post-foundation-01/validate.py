#!/usr/bin/env python3
"""Validate the post-Foundation-01 Definition drift-audit candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from render import OUTPUT, SOURCE, render


ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parents[3]
FOUNDATION_SCHEMA = LAB_ROOT / "authority/foundation/v1/schema.json"
FOUNDATION_RENDERER = LAB_ROOT / "authority/foundation/v1/render.py"
REGISTRY = LAB_ROOT / "authority/definitions/registry.json"
INDEX = LAB_ROOT / "authority/definitions/DEFINITIONS-INDEX.md"
FOUNDATION_DECISION = LAB_ROOT / "docs/decisions/0013-foundation-01-admission/decision.json"
FOUNDATION_DECISION_RECEIPT = LAB_ROOT / "docs/decisions/0013-foundation-01-admission/receipts/validation.json"
RECEIPT = ROOT / "receipts/validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def foundation_registry_projection(registry: dict) -> str:
    spec = importlib.util.spec_from_file_location("foundation_projection_renderer", FOUNDATION_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Foundation-01 renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.registry(registry).rstrip() + "\n"


def main() -> int:
    data = load(SOURCE)
    schema = load(FOUNDATION_SCHEMA)
    registry = load(REGISTRY)
    decision = load(FOUNDATION_DECISION)
    decision_receipt = load(FOUNDATION_DECISION_RECEIPT)
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    audit_validator = Draft202012Validator({"$ref": "#/$defs/driftAudit", "$defs": schema["$defs"]})
    schema_errors = sorted(audit_validator.iter_errors(data), key=lambda error: list(error.path))
    check("schema-valid", not schema_errors, "; ".join(error.message for error in schema_errors) or "accepted")
    check(
        "candidate-non-effectful",
        data.get("status") == "candidate-unadmitted" and data.get("authority_effect") == "none",
        f"status={data.get('status')!r} authority_effect={data.get('authority_effect')!r}",
    )
    check(
        "foundation-decision-current",
        sha256(FOUNDATION_DECISION) == "2aec4fc4cee04804047dbdfecdf521837b0bd1b006fc6b7ea55f46c9a15b4f52"
        and decision.get("status") == "owner-admitted"
        and decision.get("admission_result", {}).get("result") == "complete-semantic-foundation-admission",
        f"decision_sha256={sha256(FOUNDATION_DECISION)} status={decision.get('status')!r}",
    )
    receipt_checks = decision_receipt.get("checks", [])
    check(
        "foundation-decision-evidence-pass",
        sha256(FOUNDATION_DECISION_RECEIPT) == "0d0fbf5ef314298786ed7dcebc69ce96b4e615b570066eb330c89f4035cf6265"
        and decision_receipt.get("result") == "PASS"
        and len(receipt_checks) == 31
        and all(item.get("result") == "PASS" for item in receipt_checks),
        f"receipt_sha256={sha256(FOUNDATION_DECISION_RECEIPT)} result={decision_receipt.get('result')!r}",
    )
    admitted_selectors = {item["selector"] for item in decision.get("source_admissions", [])}
    check(
        "three-source-admissions-resolved",
        admitted_selectors == {"CAV2-D21", "CAV2-D33", "CAV2-D51"},
        f"selectors={sorted(admitted_selectors)}",
    )

    check(
        "registry-current-and-empty",
        sha256(REGISTRY) == data.get("registry_sha256") == "ed7575bd0754136c3075ba1a8d132d4673f2b6f6c1fc258c3734debc8c51b33f"
        and registry.get("entries") == [],
        f"registry_sha256={sha256(REGISTRY)} entries={len(registry.get('entries', []))}",
    )
    expected_index = foundation_registry_projection(registry)
    check(
        "generated-index-still-synchronized",
        INDEX.is_file() and INDEX.read_text(encoding="utf-8") == expected_index,
        f"expected_sha256={hashlib.sha256(expected_index.encode()).hexdigest()} actual_sha256={sha256(INDEX) if INDEX.is_file() else None}",
    )

    findings = {item["finding_id"]: item for item in data.get("findings", [])}
    check(
        "undefined-definition-blocker-preserved",
        findings.get("CAL-DRIFT-001-UNDEFINED-DEFINITION", {}).get("severity") == "blocker"
        and data.get("summary", {}).get("undefined_critical_terms") == 1,
        json.dumps(findings.get("CAL-DRIFT-001-UNDEFINED-DEFINITION"), sort_keys=True),
    )
    check(
        "sources-pending-replaced-by-admitted-finding",
        "CAL-DRIFT-002-SOURCES-PENDING" not in findings
        and findings.get("CAL-DRIFT-002-SOURCES-ADMITTED", {}).get("severity") == "info",
        f"finding_ids={sorted(findings)}",
    )
    summary = data.get("summary", {})
    check(
        "summary-orthogonal-counts",
        summary
        == {
            "undefined_critical_terms": 1,
            "conflicting_consumers": 0,
            "stale_entries": 0,
            "wrong_workspace_voices": 0,
        },
        json.dumps(summary, sort_keys=True),
    )

    direction = data.get("source_direction", {})
    check(
        "machine-canonical-human-generated",
        direction.get("canonical") == SOURCE.name
        and direction.get("human_projection") == OUTPUT.name
        and direction.get("projection_policy") == "generated-only"
        and direction.get("generator_ref") == "cal.generator.foundation-projections/v1"
        and direction.get("generator_sha256") == sha256(FOUNDATION_RENDERER),
        json.dumps(direction, sort_keys=True),
    )
    projected_a = render(data)
    projected_b = render(data)
    check(
        "projection-two-run-determinism",
        projected_a == projected_b,
        f"sha256={hashlib.sha256(projected_a.encode()).hexdigest()}",
    )
    check(
        "projection-parity",
        OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == projected_a,
        "DEFINITION-DRIFT-AUDIT.md must equal render(drift-audit.json)",
    )

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-drift-audit-validation/v1",
        "record_id": data.get("record_id"),
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {
            "drift_audit_json_sha256": sha256(SOURCE),
            "drift_audit_md_sha256": sha256(OUTPUT) if OUTPUT.is_file() else None,
            "registry_sha256": sha256(REGISTRY),
            "definition_index_sha256": sha256(INDEX),
            "foundation_decision_sha256": sha256(FOUNDATION_DECISION),
            "foundation_decision_validation_sha256": sha256(FOUNDATION_DECISION_RECEIPT),
            "projection_generator_sha256": sha256(FOUNDATION_RENDERER),
            "local_invocation_adapter_sha256": sha256(ROOT / "render.py"),
            "validator_sha256": sha256(ROOT / "validate.py"),
        },
        "claim_ceiling": data.get("claim_ceiling"),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{result}: {sum(item['result'] == 'PASS' for item in checks)}/{len(checks)} checks passed")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
