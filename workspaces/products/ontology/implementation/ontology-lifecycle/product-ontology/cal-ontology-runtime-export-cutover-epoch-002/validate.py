#!/usr/bin/env python3
"""Validate and render the D65 epoch-002 Product Capability contribution."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
SOURCE = HERE / "product-capability-prototype.json"
SCHEMA = HERE / "schema.json"
OUTPUT = HERE / "PRODUCT-CAPABILITY.md"
RECEIPT = HERE / "receipts/validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(prototype: dict) -> str:
    contribution = prototype["epoch_contribution"]
    lines = [
        "<!-- GENERATED FILE: edit product-capability-prototype.json and rerun validate.py. -->",
        "",
        "# Epoch-002 Product Capability contribution",
        "",
        f"- Prototype: `{prototype['prototype_id']}`",
        f"- Capability: `{prototype['capability_id']}`",
        f"- Stage: `{prototype['stage_id']}`",
        f"- Status: `{prototype['status']}`",
        f"- Next product frontier: `{prototype['next_product_frontier']}`",
        f"- Product approval: `{prototype['product_approval']}`",
        f"- Authority effect: `{prototype['authority_effect']}`",
        "",
        "## Stable outcome",
        "",
        prototype["stable_outcome"],
        "",
        "## Epoch contribution",
        "",
        contribution["objective"],
    ]
    for heading, field in (("Input contracts", "input_contracts"), ("Output contracts", "output_contracts"), ("Promised behaviors", "promised_behaviors"), ("Product-test obligations", "product_test_obligations")):
        lines.extend(["", f"## {heading}", ""])
        lines.extend(f"- {item}" for item in contribution[field])
    lines.extend(["", "## Exclusions", ""])
    lines.extend(f"- {item}" for item in prototype["preserved_scope"]["exclusions"])
    lines.extend(["", "## Challenge route", "", prototype["challenge_route"], "", "## Claim ceiling", "", prototype["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def evaluate(prototype: dict, *, check_sources: bool = True) -> list[dict]:
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    errors = sorted(error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(prototype))
    check("product-capability-prototype-schema-valid", not errors, errors)

    bound = [prototype["predecessor"], prototype["definition_predecessor"]]
    source_failures = []
    if check_sources:
        for record in bound:
            for path_key, sha_key in (("path", "sha256"), ("admission_decision_path", "admission_decision_sha256"), ("validation_path", "validation_sha256")):
                if path_key not in record:
                    continue
                path = LAB / record[path_key]
                actual = digest(path) if path.is_file() else None
                if actual != record[sha_key]:
                    source_failures.append({"path": record[path_key], "expected": record[sha_key], "actual": actual})
        for record in prototype["selected_evidence"]:
            path = LAB / record["path"]
            actual = digest(path) if path.is_file() else None
            if actual != record["sha256"]:
                source_failures.append({"path": record["path"], "expected": record["sha256"], "actual": actual})
    check("selected-predecessor-currentness", not source_failures, source_failures)

    predecessor = load(LAB / prototype["predecessor"]["path"])
    check("stable-capability-identity", prototype.get("capability_id") == predecessor.get("capability_id") and prototype.get("product_ref") == predecessor.get("product_ref"), {"prototype": prototype.get("capability_id"), "predecessor": predecessor.get("capability_id")})
    check("stable-capability-outcome", prototype.get("stable_outcome") == predecessor.get("outcome"), {"same": prototype.get("stable_outcome") == predecessor.get("outcome")})

    contribution = prototype.get("epoch_contribution", {})
    joined = json.dumps(contribution, sort_keys=True).lower()
    check("event-calculated-context-contract", "canonical per-subject" in joined and "exact consistent event cut" in joined and "v2 context map" in joined and "public versioned adapter" in joined, contribution)
    check("product-test-obligation-closure", len(contribution.get("product_test_obligations", [])) == 6 and "byte-identical" in joined and "rollback rehearsal" in joined and "admitted runtime" in joined, contribution.get("product_test_obligations"))

    exclusions = " ".join(prototype.get("preserved_scope", {}).get("exclusions", [])).lower()
    check("scope-and-authority-boundary", "changing the stable product capability identity" in exclusions and "transferring governance authority" in exclusions and "migration, cutover, publication" in exclusions, prototype.get("preserved_scope"))
    check("two-lane-product-continuation", prototype.get("work_plan") == {"lane": "product-construction", "current_frontier": "D65-S2", "operational_tasks": [], "continuation_status": "runnable"} and prototype.get("next_product_frontier") == "D65-S3", prototype.get("work_plan"))
    check("no-premature-product-approval", prototype.get("product_approval") == "not-requested" and prototype.get("authority_effect") == "none", {"product_approval": prototype.get("product_approval"), "authority_effect": prototype.get("authority_effect")})
    rendered = render(prototype)
    check("product-capability-projection-deterministic", rendered == render(copy.deepcopy(prototype)), hashlib.sha256(rendered.encode()).hexdigest())
    return checks


def hostile_probes(prototype: dict) -> list[dict]:
    probes = []

    drift = copy.deepcopy(prototype)
    drift["predecessor"]["sha256"] = "0" * 64
    failed = {item["check_id"] for item in evaluate(drift) if item["result"] == "FAIL"}
    probes.append({"probe_id": "predecessor-drift", "result": "PASS" if "selected-predecessor-currentness" in failed else "FAIL"})

    identity = copy.deepcopy(prototype)
    identity["capability_id"] = "CA2-CAP-SILENTLY-REPLACED"
    failed = {item["check_id"] for item in evaluate(identity, check_sources=False) if item["result"] == "FAIL"}
    probes.append({"probe_id": "silent-capability-replacement", "result": "PASS" if "product-capability-prototype-schema-valid" in failed and "stable-capability-identity" in failed else "FAIL"})

    outcome = copy.deepcopy(prototype)
    outcome["stable_outcome"] = "A materially different outcome."
    failed = {item["check_id"] for item in evaluate(outcome, check_sources=False) if item["result"] == "FAIL"}
    probes.append({"probe_id": "silent-outcome-change", "result": "PASS" if "stable-capability-outcome" in failed else "FAIL"})

    approval = copy.deepcopy(prototype)
    approval["product_approval"] = "approved"
    failed = {item["check_id"] for item in evaluate(approval, check_sources=False) if item["result"] == "FAIL"}
    probes.append({"probe_id": "premature-product-approval", "result": "PASS" if "no-premature-product-approval" in failed else "FAIL"})
    return probes


def main() -> int:
    prototype = load(SOURCE)
    OUTPUT.write_text(render(prototype), encoding="utf-8")
    checks = evaluate(prototype)
    probes = hostile_probes(prototype)
    passed = all(item["result"] == "PASS" for item in checks + probes)
    receipt = {
        "schema_version": "cal.d65-epoch-002-product-capability-prototype-validation/v1",
        "prototype_id": prototype["prototype_id"],
        "stage_id": prototype["stage_id"],
        "result": "PASS" if passed else "FAIL",
        "checks_passed": sum(item["result"] == "PASS" for item in checks),
        "checks_total": len(checks),
        "hostile_probes_passed": sum(item["result"] == "PASS" for item in probes),
        "hostile_probes_total": len(probes),
        "checks": checks,
        "hostile_probes": probes,
        "artifacts": {
            "prototype_path": str(SOURCE.relative_to(LAB)),
            "prototype_sha256": digest(SOURCE),
            "projection_path": str(OUTPUT.relative_to(LAB)),
            "projection_sha256": digest(OUTPUT)
        },
        "stage_state": "TESTED_PROTOTYPE" if passed else "PROTOTYPE_TEST_FAILED",
        "next_product_frontier": "D65-S3" if passed else "D65-S2",
        "product_approval": "not-requested",
        "authority_effect": "none",
        "claim_ceiling": prototype["claim_ceiling"]
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"D65_S2_PRODUCT_CAPABILITY_PROTOTYPE={receipt['result']}")
    print(f"CHECKS={receipt['checks_passed']}/{receipt['checks_total']}")
    print(f"HOSTILE_PROBES={receipt['hostile_probes_passed']}/{receipt['hostile_probes_total']}")
    print(f"NEXT_PRODUCT_FRONTIER={receipt['next_product_frontier']}")
    print("PRODUCT_APPROVAL=not-requested")
    print("AUTHORITY_EFFECT=none")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
