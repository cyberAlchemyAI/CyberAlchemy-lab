#!/usr/bin/env python3
"""Validate the current eight-Definition admission and its exact dependencies."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE_ROOT = Path("/home/vrondelli/projects/domainspec-core")
DECISION = ROOT / "decision.json"
RECEIPT = ROOT / "receipts" / "admission-validation.json"


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


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    decision = load(DECISION)
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail: object) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check(
        "decision-identity",
        decision.get("decision_id") == "CAL-DECISION-0018-DEFINITION-AND-CTX00-PROMOTION"
        and decision.get("status") == "owner-admitted",
        {"decision_id": decision.get("decision_id"), "status": decision.get("status")},
    )
    check("authority-effect-exact", decision.get("authority_effect") == "eight-exact-definition-versions-canonical", decision.get("authority_effect"))
    selection = decision["selection"]
    check(
        "selection-exact",
        selection.get("option_id") == "ADMIT-DEFINITION-AND-CTX00-V1"
        and selection.get("selection_token") == "ADMIT-DEFINITION-AND-CTX00-V1"
        and selection.get("selected_by_principal") == "person:<vrondelli>"
        and selection.get("selected_role") == "definition-owner",
        selection,
    )

    request_path = ROOT / decision["admissibility"]["request_ref"]
    gate_receipt_path = ROOT / decision["admissibility"]["receipt_ref"]
    request = load(request_path)
    gate_receipt = load(gate_receipt_path)
    check("gate-request-current", sha256(request_path) == decision["admissibility"]["request_sha256"], sha256(request_path))
    check("gate-request-digest-current", canonical_digest(request) == decision["admissibility"]["request_digest"] == gate_receipt.get("requestDigest"), canonical_digest(request))
    check("gate-receipt-current", sha256(gate_receipt_path) == decision["admissibility"]["receipt_sha256"], sha256(gate_receipt_path))
    check(
        "selected-option-admissible",
        gate_receipt.get("routeOutcome") == "gate"
        and selection["option_id"] in gate_receipt.get("admissibleOptionIds", [])
        and selection["option_id"] in gate_receipt.get("presentedOptionIds", []),
        gate_receipt,
    )

    promotion = decision["promotion_request"]
    promotion_path = ROOT / promotion["path"]
    promotion_receipt_path = ROOT / promotion["validation_path"]
    promotion_receipt = load(promotion_receipt_path)
    check("promotion-request-current", sha256(promotion_path) == promotion["sha256"], sha256(promotion_path))
    check("promotion-request-validation-current", sha256(promotion_receipt_path) == promotion["validation_sha256"], sha256(promotion_receipt_path))
    check(
        "promotion-request-preselection-pass",
        promotion_receipt.get("result") == "PASS"
        and promotion_receipt.get("decision_gate_result") == "BLOCK"
        and promotion_receipt.get("summary") == {"passed": 16, "total": 16},
        {"result": promotion_receipt.get("result"), "decision_gate_result": promotion_receipt.get("decision_gate_result"), "summary": promotion_receipt.get("summary")},
    )

    owners_path = LAB / decision["authority_basis"]["owner_registry_path"]
    owners = load(owners_path)
    assignments = {(item["role_id"], item["principal_id"]) for item in owners["role_assignments"]}
    check("owner-registry-current", sha256(owners_path) == decision["authority_basis"]["owner_registry_sha256"], sha256(owners_path))
    check("definition-owner-bound", ("definition-owner", "person:<vrondelli>") in assignments, sorted([list(item) for item in assignments]))

    candidate_meta = decision["accepted_candidate"]
    candidate_path = LAB / candidate_meta["path"]
    candidate_receipt_path = LAB / candidate_meta["validation_path"]
    candidate = load(candidate_path)
    candidate_receipt = load(candidate_receipt_path)
    check("candidate-current", sha256(candidate_path) == candidate_meta["sha256"], sha256(candidate_path))
    check("candidate-validation-current", sha256(candidate_receipt_path) == candidate_meta["validation_sha256"], sha256(candidate_receipt_path))
    check(
        "candidate-preselection-validation-pass",
        candidate_receipt.get("result") == "PASS" and candidate_receipt.get("summary") == {"failed": 0, "passed": 29, "total": 29},
        {"result": candidate_receipt.get("result"), "summary": candidate_receipt.get("summary")},
    )

    evidence = decision["evidence_basis"]
    pack_path = LAB / evidence["definition_pack_path"]
    pack_receipt_path = LAB / evidence["validation_path"]
    pack_receipt = load(pack_receipt_path)
    check("successor-pack-current", sha256(pack_path) == evidence["definition_pack_sha256"], sha256(pack_path))
    check("successor-pack-validation-current", sha256(pack_receipt_path) == evidence["validation_sha256"], sha256(pack_receipt_path))
    check("successor-pack-validation-pass", pack_receipt.get("result") == "PASS" and pack_receipt.get("summary") == {"passed": 12, "total": 12}, {"result": pack_receipt.get("result"), "summary": pack_receipt.get("summary")})

    admitted = decision["admitted_definitions"]
    admitted_by_id = {item["definition_id"]: item for item in admitted}
    candidate_by_id = {item["definition_id"]: item for item in candidate["definitions"]}
    check("eight-definition-closure", len(admitted) == len(admitted_by_id) == 8 and set(admitted_by_id) == set(candidate_by_id), sorted(admitted_by_id))
    definition_renderer_path = LAB / "authority/artifact-types/definition/v1/generator.py"
    definition_renderer = load_module("definition_renderer_admission", definition_renderer_path)
    definition_results = []
    projection_results = []
    source_refs: dict[str, dict] = {}
    for definition_id, item in admitted_by_id.items():
        path = LAB / item["path"]
        data = load(path)
        candidate_item = candidate_by_id[definition_id]
        current = sha256(path)
        definition_results.append({
            "definition_id": definition_id,
            "path": item["path"],
            "expected": item["sha256"],
            "actual": current,
            "candidate_parity": item["path"] == candidate_item["path"] and item["sha256"] == candidate_item["sha256"],
            "identity_parity": data.get("definition_id") == definition_id and data.get("version") == item["version"],
        })
        projection = path.with_name("DEFINITION.md")
        projection_results.append({
            "definition_id": definition_id,
            "projection": str(projection.relative_to(LAB)),
            "current": projection.is_file() and projection.read_text(encoding="utf-8") == definition_renderer.render(data),
        })
        for source in data["source_refs"]:
            existing = source_refs.setdefault(source["source_ref"], source)
            if existing != source:
                source_refs[source["source_ref"]] = {"conflict": [existing, source]}
    check("definition-bytes-current", all(x["actual"] == x["expected"] for x in definition_results), definition_results)
    check("candidate-definition-parity", all(x["candidate_parity"] and x["identity_parity"] for x in definition_results), definition_results)
    check("definition-projection-parity", all(x["current"] for x in projection_results), projection_results)

    definitions_source = SOURCE_ROOT / "cyberAlchemy-v2/authority/definitions/DEFINITIONS.md"
    source_paths = {
        "CAL-SOURCE-ADMISSION-CAV2-D21": definitions_source,
        "CAL-SOURCE-ADMISSION-CAV2-D33": definitions_source,
        "CAL-SOURCE-ADMISSION-CAV2-D51": definitions_source,
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D29": definitions_source,
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D64": definitions_source,
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D66": definitions_source,
        "CAL-SOURCE-ADMISSION-CTX00-CAV2-D67": definitions_source,
        "CAL-SOURCE-ADMISSION-CTX00-LANGUAGE-CONCEPTS": SOURCE_ROOT / "cyberAlchemy-v2/language/concepts.json",
        "CAL-SOURCE-ADMISSION-CTX00-GOVERNANCE-LANGUAGE": SOURCE_ROOT / "cyberAlchemy-v2/language/languages/governance-ubiquitous-language.json",
        "CAL-SOURCE-ADMISSION-CTX00-CONTEXT-PACKAGE": SOURCE_ROOT / "cyberAlchemy-v2/context/README.md",
    }
    source_results = []
    for source_id, source in sorted(source_refs.items()):
        path = source_paths[source_id]
        selector = source["selector"]
        actual = selected_heading_digest(path, selector) if selector.startswith("CAV2-D") else sha256(path)
        source_results.append({"source_ref": source_id, "expected": source["content_sha256"], "actual": actual, "current": actual == source["content_sha256"]})
    check("selected-source-closure", len(source_results) == 10 and set(source_refs) == set(source_paths), sorted(source_refs))
    check("selected-source-bytes-current", all(x["current"] for x in source_results), source_results)

    for name, item in decision["bound_candidate_postimages"].items():
        check(f"candidate-postimage-{name}-current", sha256(LAB / item["path"]) == item["sha256"], sha256(LAB / item["path"]))

    registry_item = decision["canonical_postimages"]["registry"]
    registry_path = LAB / registry_item["path"]
    registry = load(registry_path)
    registry_rows = {item["definition_id"]: item for item in registry["entries"]}
    check("registry-current", sha256(registry_path) == registry_item["sha256"] and len(registry_rows) == registry_item["entry_count"] == 8, {"sha256": sha256(registry_path), "entries": len(registry_rows)})
    check("registry-admitted-state", registry.get("status") == "owner-admitted" and registry.get("authority_effect") == decision["authority_effect"] and registry.get("admission_decision_ref") == decision["decision_id"], {"status": registry.get("status"), "authority_effect": registry.get("authority_effect"), "decision": registry.get("admission_decision_ref")})
    registry_parity = []
    for definition_id, admitted_item in admitted_by_id.items():
        row = registry_rows.get(definition_id, {})
        registry_parity.append({"definition_id": definition_id, "current": all(row.get(key) == admitted_item[key] for key in ("version", "path", "sha256")) and row.get("lifecycle_state") == "admitted" and row.get("admission_decision_ref") == decision["decision_id"]})
    check("registry-definition-parity", all(x["current"] for x in registry_parity), registry_parity)

    foundation_renderer_path = LAB / "authority/foundation/v1/render.py"
    foundation_renderer = load_module("foundation_renderer_admission", foundation_renderer_path)
    index_item = decision["canonical_postimages"]["generated_index"]
    index_path = LAB / index_item["path"]
    check("registry-index-current", sha256(index_path) == index_item["sha256"], sha256(index_path))
    check("registry-index-projection-parity", index_path.read_text(encoding="utf-8") == foundation_renderer.registry(registry).rstrip() + "\n", str(index_path.relative_to(LAB)))

    drift_item = decision["canonical_postimages"]["drift_audit"]
    drift_path = LAB / drift_item["path"]
    drift = load(drift_path)
    check("drift-audit-current", sha256(drift_path) == drift_item["sha256"], sha256(drift_path))
    check("drift-registry-binding", drift.get("registry_sha256") == sha256(registry_path) and drift.get("admission_decision_ref") == decision["decision_id"], {"registry_sha256": drift.get("registry_sha256"), "decision": drift.get("admission_decision_ref")})
    check("drift-definition-closure", drift.get("summary", {}).get("admitted_definition_count") == 8 and drift["summary"].get("undefined_critical_terms") == 0 and drift["summary"].get("conflicting_consumers") == 0 and drift["summary"].get("stale_entries") == 0, drift.get("summary"))
    open_successors = [x for x in drift["findings"] if x.get("severity") == "successor-blocker" and x.get("status") == "open"]
    check("successor-blockers-preserved", len(open_successors) == drift["summary"].get("successor_context_blockers") == 2, [x["finding_id"] for x in open_successors])
    drift_view_item = decision["canonical_postimages"]["generated_drift_view"]
    drift_view_path = LAB / drift_view_item["path"]
    check("drift-view-current", sha256(drift_view_path) == drift_view_item["sha256"], sha256(drift_view_path))
    check("drift-view-projection-parity", drift_view_path.read_text(encoding="utf-8") == foundation_renderer.drift(drift).rstrip() + "\n", str(drift_view_path.relative_to(LAB)))

    decision_renderer = load_module("decision_renderer_admission", ROOT / decision["source_direction"]["generator"])
    decision_view = ROOT / decision["source_direction"]["human_projection"]
    check("decision-projection-parity", decision_view.read_text(encoding="utf-8") == decision_renderer.render(decision), str(decision_view.relative_to(LAB)))
    check("non-effects-explicit", len(decision.get("excluded_effects", [])) == 6 and any("stable release" in x for x in decision["excluded_effects"]) and any("No artifact type" in x for x in decision["excluded_effects"]), decision.get("excluded_effects"))
    check("successor-route-explicit", len(decision.get("successor_obligations", [])) == 4 and decision["successor_obligations"][0].startswith("Re-enter routing"), decision.get("successor_obligations"))

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-definition-admission-validation/v1",
        "subject": decision["decision_id"],
        "result": result,
        "authority_effect": "evidence-only-does-not-perform-admission",
        "checks": checks,
        "summary": {"passed": sum(item["result"] == "PASS" for item in checks), "failed": sum(item["result"] == "FAIL" for item in checks), "total": len(checks)},
        "claim_ceiling": "PASS proves current exact-byte closure, owner selection, machine/human projection parity, and preserved successor blockers for this admission. It does not authorize or validate successor context construction, migration, implementation, publication, deployment, or stable release."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"DEFINITION_CTX00_ADMISSION_VALIDATION={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
