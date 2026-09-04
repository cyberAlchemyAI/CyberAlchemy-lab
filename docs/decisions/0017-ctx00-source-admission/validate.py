#!/usr/bin/env python3
"""Validate the exact CTX-00 source-admission decision and selected bytes."""

import hashlib
import importlib.util
import json
from pathlib import Path

from render import OUTPUT, SOURCE, render

ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parents[2]
SOURCE_ROOT = Path("/home/vrondelli/projects/domainspec-core")
RECEIPT = ROOT / "receipts" / "validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def selected_heading_digest(path: Path, selector: str) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.startswith(f"## {selector}:")]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return hashlib.sha256("".join(lines[start:end]).encode()).hexdigest()


def main() -> int:
    decision = load(SOURCE)
    admissions_path = LAB_ROOT / decision["accepted_candidate"]["path"]
    admissions = load(admissions_path)
    request_path = ROOT / decision["admissibility"]["request_ref"]
    gate_receipt_path = ROOT / decision["admissibility"]["receipt_ref"]
    request = load(request_path)
    gate_receipt = load(gate_receipt_path)
    owners_path = LAB_ROOT / decision["authority_basis"]["owner_registry_path"]
    owners = load(owners_path)
    foundation_path = LAB_ROOT / decision["authority_basis"]["owner_registry_admission_path"]
    foundation = load(foundation_path)
    pack_path = LAB_ROOT / decision["evidence_basis"]["definition_pack_path"]
    pack_receipt_path = LAB_ROOT / decision["evidence_basis"]["validation_receipt_path"]
    pack_receipt = load(pack_receipt_path)
    registry_path = LAB_ROOT / "authority/definitions/registry.json"
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("decision-identity", decision["decision_id"] == "CAL-DECISION-0017-CTX00-SOURCE-ADMISSION" and decision["status"] == "owner-admitted", {"decision_id": decision["decision_id"], "status": decision["status"]})
    check("authority-effect-narrow", decision["authority_effect"] == "ctx00-source-evidence-admission-only", decision["authority_effect"])
    check("selection-exact", decision["selection"]["option_id"] == "CTX00-SOURCES-ADMIT" and decision["selection"]["selected_by_principal"] == "person:<vrondelli>" and decision["selection"]["selected_role"] == "source-admission-owner", decision["selection"])
    check("request-current", sha256(request_path) == decision["admissibility"]["request_sha256"], sha256(request_path))
    check("gate-receipt-current", sha256(gate_receipt_path) == decision["admissibility"]["receipt_sha256"], sha256(gate_receipt_path))
    check("request-digest-current", canonical_digest(request) == decision["admissibility"]["request_digest"] == gate_receipt["requestDigest"], canonical_digest(request))
    check("selected-option-admissible", gate_receipt["routeOutcome"] == "gate" and decision["selection"]["option_id"] in gate_receipt["admissibleOptionIds"] and decision["selection"]["option_id"] in gate_receipt["presentedOptionIds"], gate_receipt)
    check("owner-registry-current", sha256(owners_path) == decision["authority_basis"]["owner_registry_sha256"], sha256(owners_path))
    assignments = {(x["role_id"], x["principal_id"]) for x in owners["role_assignments"]}
    check("source-owner-bound", ("source-admission-owner", "person:<vrondelli>") in assignments, sorted([list(x) for x in assignments]))
    check("foundation-decision-current", sha256(foundation_path) == decision["authority_basis"]["owner_registry_admission_sha256"] and foundation["status"] == "owner-admitted", {"sha256": sha256(foundation_path), "status": foundation["status"]})
    check("source-admission-type-admitted", "cal.artifact-type.source-admission/v1" in foundation["admitted_artifact_types"], foundation["admitted_artifact_types"])
    check("accepted-candidate-current", sha256(admissions_path) == decision["accepted_candidate"]["sha256"], sha256(admissions_path))
    check("accepted-candidate-input-posture", admissions["status"] == "candidate-unadmitted" and admissions["authority_effect"] == "none-until-bound-decision", {"status": admissions["status"], "authority_effect": admissions["authority_effect"]})
    check("pack-current", sha256(pack_path) == decision["evidence_basis"]["definition_pack_sha256"], sha256(pack_path))
    check("pack-receipt-current", sha256(pack_receipt_path) == decision["evidence_basis"]["validation_receipt_sha256"], sha256(pack_receipt_path))
    check("pack-validation-pass", pack_receipt.get("result") == "PASS" and len(pack_receipt.get("checks", [])) == 20 and all(x["result"] == "PASS" for x in pack_receipt["checks"]), {"result": pack_receipt.get("result"), "checks": len(pack_receipt.get("checks", []))})

    source_paths = {
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D29": SOURCE_ROOT / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md",
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D64": SOURCE_ROOT / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md",
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D66": SOURCE_ROOT / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md",
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D67": SOURCE_ROOT / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md",
        "CAL-SOURCE-ADMISSION-CTX00-LANGUAGE-CONCEPTS": SOURCE_ROOT / "cyberAlchemy-v2/language/concepts.json",
        "CAL-SOURCE-ADMISSION-CTX00-GOVERNANCE-LANGUAGE": SOURCE_ROOT / "cyberAlchemy-v2/language/languages/governance-ubiquitous-language.json",
        "CAL-SOURCE-ADMISSION-CTX00-CONTEXT-PACKAGE": SOURCE_ROOT / "cyberAlchemy-v2/context/README.md",
    }
    source_results = []
    for item in admissions["admissions"]:
        path = source_paths[item["admission_id"]]
        actual = selected_heading_digest(path, item["selector"]) if item["selector_kind"] == "markdown-h2-block-v1" else sha256(path)
        source_results.append({"admission_id": item["admission_id"], "expected": item["selected_sha256"], "actual": actual, "current": actual == item["selected_sha256"]})
    check("seven-source-selections", len(source_results) == 7 and len({x["admission_id"] for x in source_results}) == 7, source_results)
    check("selected-bytes-current", all(x["current"] for x in source_results), source_results)
    decision_sources = {(x["admission_id"], x["selected_sha256"]) for x in decision["admitted_source_selections"]}
    candidate_sources = {(x["admission_id"], x["selected_sha256"]) for x in admissions["admissions"]}
    check("decision-candidate-source-parity", decision_sources == candidate_sources, sorted([list(x) for x in decision_sources]))
    check("target-uses-bounded", all(x["target_concept_ids"] and x["target_use"] and x["non_effects"] for x in admissions["admissions"]), {x["admission_id"]: x["target_concept_ids"] for x in admissions["admissions"]})
    check("definition-registry-unchanged-empty", sha256(registry_path) == "ed7575bd0754136c3075ba1a8d132d4673f2b6f6c1fc258c3734debc8c51b33f" and load(registry_path).get("entries") == [], {"sha256": sha256(registry_path), "entries": len(load(registry_path).get("entries", []))})
    check("exclusions-explicit", len(decision["excluded_effects"]) >= 7 and any("No candidate" in x for x in decision["excluded_effects"]) and any("No directory migration" in x for x in decision["excluded_effects"]), decision["excluded_effects"])
    check("successor-gates-explicit", len(decision["successor_obligations"]) == 4, decision["successor_obligations"])
    expected_projection = render(decision)
    check("decision-projection-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == expected_projection, str(OUTPUT.relative_to(LAB_ROOT)))
    source_projection = admissions_path.with_name("SOURCE-ADMISSIONS.md")
    source_renderer_path = admissions_path.with_name("render.py")
    spec = importlib.util.spec_from_file_location("ctx00_source_admission_renderer", source_renderer_path)
    source_renderer = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(source_renderer)
    check(
        "source-projection-parity",
        admissions["source_direction"]["projection_policy"] == "generated-only"
        and source_projection.is_file()
        and source_projection.read_text(encoding="utf-8") == source_renderer.render(admissions),
        str(source_projection.relative_to(LAB_ROOT)),
    )

    result = "PASS" if all(x["result"] == "PASS" for x in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-validation-receipt/v0",
        "subject": decision["decision_id"],
        "result": result,
        "authority_effect": "evidence-only-does-not-perform-admission",
        "checks": checks,
        "summary": {"passed": sum(x["result"] == "PASS" for x in checks), "total": len(checks)},
        "claim_ceiling": "This receipt checks the decision record, owner route, selected bytes, bounded target uses, and generated projection. Authority comes only from the human source-admission decision."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX00_SOURCE_ADMISSION_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
