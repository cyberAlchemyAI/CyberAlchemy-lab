#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPECTED_TOKEN = "APPROVE-CAV2-LAB-RECONSTRUCTION-0003"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_digest(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_bytes(canonical_bytes(value))


def verify_preconditions(token: str) -> tuple[dict, dict, dict, dict]:
    request = load(ROOT / "decision-request.json")
    manifest = load(ROOT / "manifest.json")
    candidate_validation = load(ROOT / "receipts/validation.json")
    admissibility_request = load(HERE / "admissibility-request.json")
    admissibility = load(HERE / "admissibility.json")

    if token != EXPECTED_TOKEN or token != request.get("approval_token"):
        raise ValueError("approval token does not match the exact candidate request")
    if request.get("status") != "ready-for-owner-review":
        raise ValueError("decision request is not ready for owner review")
    for subject in request["exact_subjects"]:
        subject_path = ROOT / subject["path"]
        if not subject_path.is_file() or digest(subject_path) != subject["sha256"]:
            raise ValueError(f'decision subject drift: {subject["path"]}')
    if candidate_validation.get("result") != "PASS":
        raise ValueError("candidate validation is not PASS")
    if not all(item.get("result") == "PASS" for item in candidate_validation["checks"]):
        raise ValueError("candidate validation contains a non-PASS check")
    if admissibility.get("requestDigest") != canonical_digest(admissibility_request):
        raise ValueError("admissibility request binding drift")
    if admissibility.get("routeOutcome") != "gate":
        raise ValueError("admissibility did not route through the human gate")
    if token not in admissibility.get("admissibleOptionIds", []):
        raise ValueError("selected token is not structurally admissible")
    if manifest.get("authority_effect") != "none":
        raise ValueError("candidate manifest exceeds its authority ceiling")
    return request, manifest, candidate_validation, admissibility


def build_decision(token: str, recorded_at: str) -> dict:
    request, manifest, candidate_validation, admissibility = verify_preconditions(token)
    return {
        "schema_version": "cyberalchemy-lab-planning-selection-decision/v1",
        "decision_id": "CAL-CAV2-LAB-RECONSTRUCTION-0003-PLANNING-SELECTION-0001",
        "status": "selected-planning-baseline",
        "recorded_at_utc": recorded_at,
        "source": {
            "kind": "interactive-user-exact-token",
            "selected_token": token,
            "selected_token_sha256": hashlib.sha256(token.encode("utf-8")).hexdigest(),
            "principal_assertion": None,
            "identity_assurance": "interactive-session-presence-only-not-cryptographically-verified",
            "rationale": "The user supplied the exact approval token and no additional rationale.",
        },
        "request_binding": {
            "path": "decision-request.json",
            "request_id": request["request_id"],
            "sha256": digest(ROOT / "decision-request.json"),
        },
        "candidate_evidence": {
            "manifest_path": "manifest.json",
            "manifest_id": manifest["manifest_id"],
            "manifest_sha256": digest(ROOT / "manifest.json"),
            "validation_path": "receipts/validation.json",
            "validation_sha256": digest(ROOT / "receipts/validation.json"),
            "validation_result": candidate_validation["result"],
            "validation_checks": candidate_validation["summary"]["total"],
        },
        "admissibility_binding": {
            "request_path": "decisions/0001-planning-selection/admissibility-request.json",
            "request_sha256": digest(HERE / "admissibility-request.json"),
            "receipt_path": "decisions/0001-planning-selection/admissibility.json",
            "receipt_sha256": digest(HERE / "admissibility.json"),
            "request_digest": admissibility["requestDigest"],
            "route_outcome": admissibility["routeOutcome"],
            "selected_option_id": token,
        },
        "exact_subjects": request["exact_subjects"],
        "selected_decisions": request["distinct_decisions"],
        "decision_effect": {
            "authority_effect": "planning-selection-only",
            "d65_successor": "selected-as-normalization-planning-baseline",
            "target_scaffolds": "selected-as-family-refinement-baseline",
            "ontology_routes": "selected-as-migration-routing-baseline",
            "inferred_ontology_types": "two-business-system-bridge-proposals-selected-for-later-context-owned-refinement",
        },
        "next_construction_frontier": request[
            "next_construction_frontier_if_approved"
        ],
        "remaining_blockers": [
            "The 176 prototype scaffolds require family-specific refinement, validation, and separate admission decisions.",
            "The six D65 successor targets require authoring and validation against the selected successor mapping.",
            "The competing DomainSpec lineage claims remain unresolved and must be handled by Craft.",
            "No ontology, runtime, migration execution, publication, release, or deployment authority exists.",
        ],
        "non_effects": request["non_effects"],
        "authority_effect": "planning-selection-only",
        "claim_ceiling": "This record proves that the exact interactive approval token selected the three digest-bound planning baselines. It does not authenticate a legal identity, admit a Definition or Artifact Type, choose a conflicting DomainSpec source epoch, activate an ontology or runtime, execute migration, or authorize Git publication, release, deployment, or another external effect.",
    }


def render_decision(decision: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is decision.json. -->",
        "",
        "# Reconstruction 0003 Planning Selection",
        "",
        f'- Decision: `{decision["decision_id"]}`',
        f'- Status: `{decision["status"]}`',
        f'- Recorded at: `{decision["recorded_at_utc"]}`',
        f'- Authority effect: `{decision["authority_effect"]}`',
        f'- Bound request: `{decision["request_binding"]["sha256"]}`',
        "",
        "## Selected planning decisions",
        "",
    ]
    for selected in decision["selected_decisions"]:
        lines.append(
            f'- `{selected["decision_id"]}` — {selected["selection_if_approved"]}; {selected["effect"]}.'
        )
    lines.extend(["", "## Remaining blockers", ""])
    for blocker in decision["remaining_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Claim ceiling", "", decision["claim_ceiling"], ""])
    return "\n".join(lines)


def render_admissibility_request(request: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is admissibility-request.json. -->",
        "",
        "# Planning Selection Admissibility Request",
        "",
        f'- Decision: `{request["decisionId"]}`',
        f'- Options: `{len(request["candidates"])}`',
        "",
        "| Option | Kind | Status | Hazard |",
        "|---|---|---|---|",
    ]
    for option in request["candidates"]:
        lines.append(
            f'| `{option["optionId"]}` | `{option["optionKind"]}` | '
            f'`{option["structuralStatus"]}` | `{option["hazardClass"]}` |'
        )
    lines.extend(
        [
            "",
            "This request classifies the options structurally. It neither selects an option nor grants authority.",
            "",
        ]
    )
    return "\n".join(lines)


def render_admissibility(receipt: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is admissibility.json. -->",
        "",
        "# Planning Selection Admissibility Receipt",
        "",
        f'- Decision: `{receipt["decisionId"]}`',
        f'- Route: `{receipt["routeOutcome"]}`',
        f'- Human gate required: `{str(receipt["decisionGateRequired"]).lower()}`',
        f'- Request digest: `{receipt["requestDigest"]}`',
        "",
        "## Admissible options",
        "",
    ]
    lines.extend(f'- `{option_id}`' for option_id in receipt["admissibleOptionIds"])
    lines.extend(
        [
            "",
            "This receipt proves structural routing only. It records no human selection and grants no authority.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_decision() -> dict:
    decision_path = HERE / "decision.json"
    decision = load(decision_path)
    request, manifest, candidate_validation, admissibility = verify_preconditions(
        decision["source"]["selected_token"]
    )
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append(
            {
                "check_id": check_id,
                "result": "PASS" if condition else "BLOCK",
                "detail": detail,
            }
        )

    check(
        "exact-token-selected",
        decision["source"]["selected_token"] == EXPECTED_TOKEN
        and decision["admissibility_binding"]["selected_option_id"] == EXPECTED_TOKEN,
        "The recorded token is the exact structurally admissible option selected by the user.",
    )
    check(
        "request-binding-current",
        decision["request_binding"]["sha256"] == digest(ROOT / "decision-request.json")
        and decision["request_binding"]["request_id"] == request["request_id"],
        "The decision binds the current immutable request bytes and identity.",
    )
    check(
        "subject-digest-closure",
        decision["exact_subjects"] == request["exact_subjects"]
        and all(
            digest(ROOT / item["path"]) == item["sha256"]
            for item in decision["exact_subjects"]
        ),
        "Every selected planning subject still matches its reviewed digest.",
    )
    check(
        "candidate-evidence-current",
        decision["candidate_evidence"]["manifest_sha256"]
        == digest(ROOT / "manifest.json")
        and decision["candidate_evidence"]["validation_sha256"]
        == digest(ROOT / "receipts/validation.json")
        and manifest["manifest_id"] == decision["candidate_evidence"]["manifest_id"]
        and candidate_validation["result"] == "PASS",
        "The manifest and 45-check candidate validation remain exact.",
    )
    check(
        "admissibility-binding-current",
        decision["admissibility_binding"]["request_sha256"]
        == digest(HERE / "admissibility-request.json")
        and decision["admissibility_binding"]["receipt_sha256"]
        == digest(HERE / "admissibility.json")
        and decision["admissibility_binding"]["request_digest"]
        == admissibility["requestDigest"],
        "The structural option request and gate receipt are exact.",
    )
    check(
        "three-decisions-selected",
        decision["selected_decisions"] == request["distinct_decisions"]
        and len(decision["selected_decisions"]) == 3,
        "The one token selects exactly the three independently enumerated planning decisions.",
    )
    check(
        "planning-only-effect",
        decision["authority_effect"] == "planning-selection-only"
        and decision["non_effects"] == request["non_effects"],
        "The decision grants planning selection only and preserves every declared non-effect.",
    )
    check(
        "identity-assurance-bounded",
        decision["source"]["principal_assertion"] is None
        and "not-cryptographically-verified"
        in decision["source"]["identity_assurance"],
        "Interactive provenance is recorded without inventing principal authentication.",
    )
    check(
        "human-projection-exact",
        (HERE / "DECISION.md").read_text(encoding="utf-8")
        == render_decision(decision),
        "The human decision view is generated exactly from canonical machine data.",
    )
    check(
        "admissibility-projections-exact",
        (HERE / "ADMISSIBILITY-REQUEST.md").read_text(encoding="utf-8")
        == render_admissibility_request(load(HERE / "admissibility-request.json"))
        and (HERE / "ADMISSIBILITY.md").read_text(encoding="utf-8")
        == render_admissibility(admissibility),
        "Both structural-gate human views are exact generated projections.",
    )
    result = "PASS" if all(item["result"] == "PASS" for item in checks) else "BLOCK"
    return {
        "schema_version": "cyberalchemy-lab-planning-selection-validation/v1",
        "decision_id": decision["decision_id"],
        "decision_sha256": digest(decision_path),
        "result": result,
        "checks": checks,
        "summary": {
            "passed": sum(item["result"] == "PASS" for item in checks),
            "total": len(checks),
            "selected_planning_decisions": len(decision["selected_decisions"]),
            "remaining_blockers": len(decision["remaining_blockers"]),
        },
        "authority_effect": "none",
        "claim_ceiling": "PASS validates the exact planning-selection record only. Validation does not authenticate identity, admit artifacts, activate runtimes, execute migration, commit, push, publish, release, or deploy.",
    }


def render_validation(receipt: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical data is validation.json. -->",
        "",
        "# Planning Selection Validation",
        "",
        f'- Result: `{receipt["result"]}`',
        f'- Checks: `{receipt["summary"]["passed"]}/{receipt["summary"]["total"]}`',
        f'- Authority effect: `{receipt["authority_effect"]}`',
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for item in receipt["checks"]:
        lines.append(
            f'| `{item["check_id"]}` | `{item["result"]}` | {item["detail"]} |'
        )
    lines.extend(["", "## Claim ceiling", "", receipt["claim_ceiling"], ""])
    return "\n".join(lines)


def record(token: str, recorded_at: str) -> None:
    decision = build_decision(token, recorded_at)
    decision_path = HERE / "decision.json"
    if decision_path.exists():
        existing = load(decision_path)
        if existing != decision:
            raise ValueError("an immutable decision already exists with different bytes")
    else:
        dump(decision_path, decision)
    admissibility_request = load(HERE / "admissibility-request.json")
    admissibility = load(HERE / "admissibility.json")
    (HERE / "ADMISSIBILITY-REQUEST.md").write_text(
        render_admissibility_request(admissibility_request), encoding="utf-8"
    )
    (HERE / "ADMISSIBILITY.md").write_text(
        render_admissibility(admissibility), encoding="utf-8"
    )
    (HERE / "DECISION.md").write_text(render_decision(decision), encoding="utf-8")
    receipt = validate_decision()
    dump(HERE / "validation.json", receipt)
    (HERE / "VALIDATION.md").write_text(
        render_validation(receipt), encoding="utf-8"
    )
    print(f'PLANNING_SELECTION={receipt["result"]}')
    print(f'CHECKS={receipt["summary"]["passed"]}/{receipt["summary"]["total"]}')
    if receipt["result"] != "PASS":
        raise SystemExit(1)


def validate_only() -> None:
    receipt = validate_decision()
    expected = load(HERE / "validation.json")
    if receipt != expected:
        raise ValueError("stored validation receipt is stale")
    if (HERE / "VALIDATION.md").read_text(encoding="utf-8") != render_validation(
        receipt
    ):
        raise ValueError("stored validation human projection is stale")
    if (HERE / "ADMISSIBILITY-REQUEST.md").read_text(
        encoding="utf-8"
    ) != render_admissibility_request(load(HERE / "admissibility-request.json")):
        raise ValueError("admissibility request human projection is stale")
    if (HERE / "ADMISSIBILITY.md").read_text(
        encoding="utf-8"
    ) != render_admissibility(load(HERE / "admissibility.json")):
        raise ValueError("admissibility receipt human projection is stale")
    print(f'PLANNING_SELECTION={receipt["result"]}')
    print(f'CHECKS={receipt["summary"]["passed"]}/{receipt["summary"]["total"]}')


def main() -> None:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)
    record_parser = subcommands.add_parser("record")
    record_parser.add_argument("--token", required=True)
    record_parser.add_argument("--recorded-at", required=True)
    subcommands.add_parser("validate")
    args = parser.parse_args()
    if args.command == "record":
        record(args.token, args.recorded_at)
    else:
        validate_only()


if __name__ == "__main__":
    main()
