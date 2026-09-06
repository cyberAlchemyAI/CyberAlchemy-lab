#!/usr/bin/env python3
"""Validate and render the D65 epoch-002 definition prototype."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
CORE = LAB.parent / "domainspec-core"
SOURCE = HERE / "definition-prototype.json"
SCHEMA = HERE / "schema.json"
OUTPUT = HERE / "DEFINITIONS.md"
RECEIPT = HERE / "receipts/validation.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_digest(path: Path, definition_id: str) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    heading = f"## {definition_id}:"
    start = next((i for i, line in enumerate(lines) if line.startswith(heading)), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return hashlib.sha256("".join(lines[start:end]).encode("utf-8")).hexdigest()


def render(prototype: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit definition-prototype.json and rerun validate.py. -->",
        "",
        "# D65 epoch-002 definition prototype",
        "",
        f"- Prototype: `{prototype['prototype_id']}`",
        f"- Stage: `{prototype['stage_id']}`",
        f"- Status: `{prototype['status']}`",
        f"- Next product frontier: `{prototype['next_product_frontier']}`",
        f"- Product approval: `{prototype['product_approval']}`",
        f"- Authority effect: `{prototype['authority_effect']}`",
    ]
    for item in prototype["terms"]:
        lines.extend([
            "",
            f"## {item['term']}",
            "",
            f"- ID: `{item['term_id']}`",
            f"- Disposition: `{item['disposition']}`",
            f"- Definition ref: `{item['definition_ref']}`" if item["definition_ref"] else "- Definition ref: local prototype",
            "",
            item["normative"],
            "",
            f"Plain language: {item['plain_language']}",
            "",
            f"Boundary: {item['boundary']}",
        ])
    lines.extend(["", "## Challenge route", "", prototype["challenge_route"], "", "## Claim ceiling", "", prototype["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def evaluate(prototype: dict, *, check_sources: bool = True) -> list[dict]:
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    errors = sorted(error.message for error in Draft202012Validator(load(SCHEMA)).iter_errors(prototype))
    check("definition-prototype-schema-valid", not errors, errors)

    source_failures = []
    if check_sources:
        for source in prototype.get("source_bindings", []):
            root = CORE if source["repository"] == str(CORE) else LAB
            path = root / source["path"]
            if source["selector_kind"] == "level-two-section":
                actual = section_digest(path, source["selector"])
            else:
                actual = digest(path) if path.is_file() else None
            if actual != source["sha256"]:
                source_failures.append({"source_id": source["source_id"], "expected": source["sha256"], "actual": actual})
    check("selected-definition-source-currentness", not source_failures, source_failures)

    terms = prototype.get("terms", [])
    term_ids = [item.get("term_id") for item in terms]
    term_names = [item.get("term") for item in terms]
    check("term-identity-closure", len(terms) == 7 and len(term_ids) == len(set(term_ids)) and len(term_names) == len(set(term_names)), term_ids)
    reuse_refs = {item.get("definition_ref") for item in terms if item.get("disposition") == "reuse"}
    prototype_refs = [item.get("definition_ref") for item in terms if item.get("disposition") == "prototype"]
    check("reuse-and-prototype-separation", reuse_refs == {"CAV2-D65", "CAV2-D67", "cal.definition.context-map@2.0.0-candidate.1"} and prototype_refs == [None, None, None, None], {"reuse": sorted(reuse_refs), "prototype_refs": prototype_refs})
    check("three-voice-boundary-coverage", all(item.get("normative") and item.get("plain_language") and item.get("boundary") for item in terms), len(terms))

    evidence_failures = []
    if check_sources:
        for item in prototype.get("evidence_bindings", []):
            path = LAB / item["path"]
            actual = digest(path) if path.is_file() else None
            if actual != item["sha256"]:
                evidence_failures.append({"path": item["path"], "expected": item["sha256"], "actual": actual})
    check("predecessor-evidence-currentness", not evidence_failures, evidence_failures)
    check("two-lane-product-continuation", prototype.get("work_plan") == {"lane": "product-construction", "current_frontier": "D65-S1", "operational_tasks": [], "continuation_status": "runnable"} and prototype.get("next_product_frontier") == "D65-S2", prototype.get("work_plan"))
    check("no-premature-product-approval", prototype.get("product_approval") == "not-requested" and prototype.get("authority_effect") == "none", {"product_approval": prototype.get("product_approval"), "authority_effect": prototype.get("authority_effect")})
    rendered = render(prototype)
    check("definition-projection-deterministic", rendered == render(copy.deepcopy(prototype)), hashlib.sha256(rendered.encode()).hexdigest())
    return checks


def hostile_probes(prototype: dict) -> list[dict]:
    probes = []

    stale = copy.deepcopy(prototype)
    stale["source_bindings"][0]["sha256"] = "0" * 64
    stale_failed = {item["check_id"] for item in evaluate(stale) if item["result"] == "FAIL"}
    probes.append({"probe_id": "stale-d65-selector", "result": "PASS" if "selected-definition-source-currentness" in stale_failed else "FAIL"})

    missing_boundary = copy.deepcopy(prototype)
    missing_boundary["terms"][0]["boundary"] = ""
    boundary_failed = {item["check_id"] for item in evaluate(missing_boundary, check_sources=False) if item["result"] == "FAIL"}
    probes.append({"probe_id": "missing-term-boundary", "result": "PASS" if "definition-prototype-schema-valid" in boundary_failed and "three-voice-boundary-coverage" in boundary_failed else "FAIL"})

    premature = copy.deepcopy(prototype)
    premature["product_approval"] = "approved"
    approval_failed = {item["check_id"] for item in evaluate(premature, check_sources=False) if item["result"] == "FAIL"}
    probes.append({"probe_id": "premature-product-approval", "result": "PASS" if "no-premature-product-approval" in approval_failed else "FAIL"})
    return probes


def main() -> int:
    prototype = load(SOURCE)
    OUTPUT.write_text(render(prototype), encoding="utf-8")
    checks = evaluate(prototype)
    probes = hostile_probes(prototype)
    passed = all(item["result"] == "PASS" for item in checks + probes)
    receipt = {
        "schema_version": "cal.d65-epoch-002-definition-prototype-validation/v1",
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
        "next_product_frontier": "D65-S2" if passed else "D65-S1",
        "product_approval": "not-requested",
        "authority_effect": "none",
        "claim_ceiling": prototype["claim_ceiling"]
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"D65_S1_DEFINITION_PROTOTYPE={receipt['result']}")
    print(f"CHECKS={receipt['checks_passed']}/{receipt['checks_total']}")
    print(f"HOSTILE_PROBES={receipt['hostile_probes_passed']}/{receipt['hostile_probes_total']}")
    print(f"NEXT_PRODUCT_FRONTIER={receipt['next_product_frontier']}")
    print("PRODUCT_APPROVAL=not-requested")
    print("AUTHORITY_EFFECT=none")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
