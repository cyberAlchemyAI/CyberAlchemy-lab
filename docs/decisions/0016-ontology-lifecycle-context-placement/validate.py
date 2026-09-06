#!/usr/bin/env python3
"""Validate the bounded Ontology Lifecycle context-placement decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from render import OUTPUT, SOURCE, render


ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parents[2]
RECEIPT = ROOT / "receipts/validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    data = load(SOURCE)
    request_path = ROOT / data["admissibility"]["request_ref"]
    receipt_path = ROOT / data["admissibility"]["receipt_ref"]
    request = load(request_path)
    admissibility = load(receipt_path)
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    check(
        "decision-identity",
        data.get("decision_id") == "CAL-DECISION-0016-ONTOLOGY-LIFECYCLE-CONTEXT-PLACEMENT"
        and data.get("status") == "owner-selected-planning-candidate",
        f"decision_id={data.get('decision_id')!r} status={data.get('status')!r}",
    )
    check(
        "bounded-authority-effect",
        data.get("authority_effect") == "context-placement-planning-selection-only",
        f"authority_effect={data.get('authority_effect')!r}",
    )
    direction = data.get("source_direction", {})
    check(
        "machine-canonical-human-generated",
        direction.get("canonical") == SOURCE.name
        and direction.get("human_projection") == OUTPUT.name
        and direction.get("projection_policy") == "generated-only",
        json.dumps(direction, sort_keys=True),
    )
    check(
        "admissibility-request-current",
        sha256(request_path) == data["admissibility"]["request_sha256"],
        f"actual={sha256(request_path)}",
    )
    check(
        "admissibility-receipt-current",
        sha256(receipt_path) == data["admissibility"]["receipt_sha256"],
        f"actual={sha256(receipt_path)}",
    )
    check(
        "admissibility-request-digest",
        canonical_digest(request) == data["admissibility"]["request_digest"] == admissibility.get("requestDigest"),
        f"computed={canonical_digest(request)} receipt={admissibility.get('requestDigest')}",
    )
    selected = data.get("selection", {}).get("option_id")
    check(
        "selected-option-admissible",
        selected == "OLC-2-SEPARATE-BOUNDED-CONTEXT"
        and admissibility.get("routeOutcome") == "gate"
        and selected in admissibility.get("admissibleOptionIds", [])
        and selected in admissibility.get("presentedOptionIds", []),
        f"selected={selected!r} route={admissibility.get('routeOutcome')!r}",
    )
    selected_request = next((item for item in request.get("candidates", []) if item.get("optionId") == selected), {})
    check(
        "owner-gated-selection",
        selected_request.get("hazardClass") == "authority"
        and selected_request.get("ownerGate") is not None
        and data.get("selection", {}).get("selected_by_principal") == "person:<vrondelli>"
        and data.get("selection", {}).get("selection_source") == "user instruction Continue with option 2",
        json.dumps({"request": selected_request, "selection": data.get("selection")}, sort_keys=True),
    )
    check(
        "unbound-role-not-inflated",
        data.get("selection", {}).get("selected_under_role") == "candidate:lab-architecture-owner"
        and data.get("selection", {}).get("role_binding_status") == "unbound-candidate-role",
        json.dumps(data.get("selection"), sort_keys=True),
    )

    stale_evidence = []
    for binding in data.get("evidence_bindings", []):
        path = (LAB_ROOT / binding["path"]).resolve()
        if not path.is_file() or sha256(path) != binding["sha256"]:
            stale_evidence.append(binding["path"])
    check("evidence-digest-closure", not stale_evidence, f"stale_or_missing={stale_evidence}")

    architecture_decision = load(LAB_ROOT / "docs/decisions/0004-lab-architecture-selection/decision.json")
    check(
        "selected-architecture-baseline",
        architecture_decision.get("status") == "owner-selected"
        and architecture_decision.get("authority_effect") == "architecture-planning-selection-only"
        and any(
            item.get("proposal_id") == "CAL-PROP-0001"
            and item.get("sha256") == "c4174297bfa71818012b77848a7cb8560b47d303b30f062144f2dc03c478932f"
            for item in architecture_decision.get("accepted_architecture_graph", [])
        ),
        json.dumps({"status": architecture_decision.get("status"), "effect": architecture_decision.get("authority_effect")}, sort_keys=True),
    )
    project_decision = load(LAB_ROOT / "docs/decisions/0014-ontology-runtime-integration-project/decision.json")
    check(
        "ontology-lifecycle-project-distinct",
        project_decision.get("selection", {}).get("project_id") == "CA2-PROJECT-CYBERALCHEMY-LAB-ONTOLOGY-LIFECYCLE"
        and project_decision.get("authority_effect") == "none",
        json.dumps(project_decision.get("selection"), sort_keys=True),
    )

    model = data.get("selected_context_model", {})
    boundary = model.get("governance_boundary", {})
    check(
        "separate-context-candidate",
        model.get("bounded_context_candidate_id") == "CAL-BC-ONTOLOGY-LIFECYCLE"
        and model.get("classification") == "separate-bounded-context-candidate"
        and model.get("candidate_target_path") == "contexts/ontology-lifecycle",
        json.dumps(model, sort_keys=True),
    )
    check(
        "directional-governance-boundary",
        boundary.get("upstream_context") == "Governance"
        and boundary.get("downstream_context") == "Ontology Lifecycle"
        and boundary.get("dependency_direction") == "Ontology Lifecycle -> Governance"
        and boundary.get("context_map_pattern") == "unresolved",
        json.dumps(boundary, sort_keys=True),
    )
    check(
        "current-package-not-relocated",
        model.get("current_package_path") == "ontology-lifecycle"
        and model.get("current_package_disposition") == "retain-in-place-until-context-admission-and-migration-authorization"
        and (LAB_ROOT / "ontology-lifecycle").is_dir()
        and not (LAB_ROOT / "contexts").exists(),
        json.dumps({"current": model.get("current_package_disposition"), "contexts_exists": (LAB_ROOT / "contexts").exists()}, sort_keys=True),
    )
    non_collapse = " ".join(model.get("non_collapse_rules", []))
    check(
        "identity-non-collapse",
        all(term in non_collapse for term in ("not the existing ontology-lifecycle directory", "not its Project, Goal, Product Capability", "does not transfer semantic ownership or authority")),
        non_collapse,
    )

    resolved = {item["residue_id"] for item in data.get("residue_transition", {}).get("resolved", [])}
    remaining = {item["residue_id"] for item in data.get("residue_transition", {}).get("remaining", [])}
    check(
        "residue-transition-bounded",
        resolved == {"CAL-CTX-R1-ONTOLOGY-LIFECYCLE-PLACEMENT"}
        and remaining == {
            "CAL-CTX-R2-ACCOUNTABLE-ROLES",
            "CAL-CTX-R3-CONTEXT-METAMODEL",
            "CAL-CTX-R4-GOVERNANCE-CONTEXT",
            "CAL-CTX-R5-ONTOLOGY-LIFECYCLE-CONTEXT",
            "CAL-CTX-R6-CONTEXT-MAP-PATTERN",
            "CAL-CTX-R7-MIGRATION",
        },
        f"resolved={sorted(resolved)} remaining={sorted(remaining)}",
    )
    exclusions = " ".join(data.get("excluded_effects", []))
    check(
        "admission-migration-publication-excluded",
        all(term in exclusions for term in ("does not admit either Ontology Lifecycle or Governance", "does not create the contexts/ directory", "does not admit external CyberAlchemy-v2 source", "does not authorize Git commit")),
        exclusions,
    )
    result_record = data.get("decision_result", {})
    check(
        "decision-result-pass",
        result_record.get("result") == "complete-context-placement-planning-selection"
        and result_record.get("decision_gate_result") == "PASS"
        and result_record.get("blocker_decisions_resolved") == 1
        and result_record.get("blocker_decisions_remaining") == 0
        and result_record.get("next_gate") == "CTX-00-CONTEXT-METAMODEL",
        json.dumps(result_record, sort_keys=True),
    )

    rendered_a = render(data)
    rendered_b = render(data)
    check("two-run-render-determinism", rendered_a == rendered_b, f"sha256={hashlib.sha256(rendered_a.encode()).hexdigest()}")
    check(
        "projection-parity",
        OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == rendered_a,
        "DECISION.md must exactly equal render(decision.json)",
    )

    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-decision-validation/v0",
        "decision_id": data.get("decision_id"),
        "result": result,
        "authority_effect": "none",
        "checks": checks,
        "materials": {
            "decision_json_sha256": sha256(SOURCE),
            "decision_md_sha256": sha256(OUTPUT) if OUTPUT.is_file() else None,
            "admissibility_request_sha256": sha256(request_path),
            "admissibility_receipt_sha256": sha256(receipt_path),
            "evidence_bindings": {item["path"]: item["sha256"] for item in data.get("evidence_bindings", [])},
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
