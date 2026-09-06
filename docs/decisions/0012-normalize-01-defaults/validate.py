#!/usr/bin/env python3
"""Validate the digest-bound NORMALIZE-01 owner decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from render import OUTPUT, SOURCE, render


ROOT = Path(__file__).resolve().parent
LAB_ROOT = ROOT.parents[2]
RECEIPT = ROOT / "receipts" / "validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    request_path = ROOT / data["admissibility"]["request_ref"]
    receipt_path = ROOT / data["admissibility"]["receipt_ref"]
    request = json.loads(request_path.read_text(encoding="utf-8"))
    admissibility = json.loads(receipt_path.read_text(encoding="utf-8"))
    candidate_path = LAB_ROOT / data["accepted_candidate"]["path"]
    candidate_receipt_path = LAB_ROOT / data["accepted_candidate"]["validation_receipt_path"]
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate_receipt = json.loads(candidate_receipt_path.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    check("decision-identity", data.get("decision_id") == "CAL-DECISION-0012-NORMALIZE-01-DEFAULTS",
          f"decision_id={data.get('decision_id')!r}")
    check("bounded-authority-effect",
          data.get("authority_effect") == "definition-migration-planning-selection-only",
          f"authority_effect={data.get('authority_effect')!r}")
    check("candidate-artifact-unadmitted",
          data.get("artifact_type", {}).get("artifact_type_status") == "candidate-unadmitted",
          f"artifact_type_status={data.get('artifact_type', {}).get('artifact_type_status')!r}")
    direction = data.get("source_direction", {})
    check("machine-canonical-human-generated",
          direction.get("canonical") == SOURCE.name and direction.get("human_projection") == OUTPUT.name
          and direction.get("projection_policy") == "generated-only",
          json.dumps(direction, sort_keys=True))

    check("admissibility-request-current",
          sha256(request_path) == data["admissibility"]["request_sha256"],
          f"actual={sha256(request_path)}")
    check("admissibility-receipt-current",
          sha256(receipt_path) == data["admissibility"]["receipt_sha256"],
          f"actual={sha256(receipt_path)}")
    check("admissibility-request-digest",
          canonical_digest(request) == data["admissibility"]["request_digest"] == admissibility.get("requestDigest"),
          f"computed={canonical_digest(request)} receipt={admissibility.get('requestDigest')}")
    selected = data.get("selection", {}).get("option_id")
    check("selected-option-admissible",
          admissibility.get("routeOutcome") == "gate"
          and selected in admissibility.get("admissibleOptionIds", [])
          and selected in admissibility.get("presentedOptionIds", []),
          f"selected={selected!r} route={admissibility.get('routeOutcome')!r}")
    check("exact-owner-selection-token",
          data.get("selection", {}).get("selection_source") == "user token NORMALIZE-01-ACCEPT-DEFAULTS",
          f"source={data.get('selection', {}).get('selection_source')!r}")

    check("accepted-candidate-current",
          sha256(candidate_path) == data["accepted_candidate"]["sha256"],
          f"actual={sha256(candidate_path)}")
    check("accepted-validation-current",
          sha256(candidate_receipt_path) == data["accepted_candidate"]["validation_receipt_sha256"],
          f"actual={sha256(candidate_receipt_path)}")
    check("accepted-validation-pass",
          candidate_receipt.get("result") == data["accepted_candidate"]["validation_result"] == "PASS"
          and candidate_receipt.get("normalization_id") == candidate.get("normalization_id"),
          f"result={candidate_receipt.get('result')!r}")

    resolved = data.get("resolved_defaults", [])
    expected_ids = [f"NORM-OQ-{i}" for i in range(1, 6)]
    check("five-defaults-resolved", [x.get("decision_id") for x in resolved] == expected_ids,
          f"ids={[x.get('decision_id') for x in resolved]}")
    source_defaults = {x["decision_id"]: x["recommended_default"] for x in candidate.get("unresolved_decisions", [])}
    selected_defaults = {x["decision_id"]: x["selection"] for x in resolved}
    check("selected-defaults-match-candidate", selected_defaults == source_defaults,
          f"source_ids={sorted(source_defaults)} selected_ids={sorted(selected_defaults)}")
    check("resolved-effects-nonpromoting",
          all(x.get("authority_effect") in {"none", "planning-selection-only"} for x in resolved),
          f"effects={[x.get('authority_effect') for x in resolved]}")
    result_record = data.get("normalization_result", {})
    check("decision-gate-pass",
          result_record.get("decision_gate_result") == "PASS"
          and result_record.get("blocker_decisions_resolved") == 5
          and result_record.get("blocker_decisions_remaining") == 0,
          json.dumps(result_record, sort_keys=True))

    rendered_a = render(data)
    rendered_b = render(data)
    check("two-run-render-determinism", rendered_a == rendered_b,
          f"sha256={hashlib.sha256(rendered_a.encode()).hexdigest()}")
    check("projection-parity", OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == rendered_a,
          "DECISION.md must exactly equal render(decision.json)")

    result = "PASS" if all(x["result"] == "PASS" for x in checks) else "FAIL"
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
            "accepted_normalization_sha256": sha256(candidate_path),
            "accepted_normalization_validation_sha256": sha256(candidate_receipt_path)
        },
        "claim_ceiling": data.get("claim_ceiling")
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{result}: {sum(x['result'] == 'PASS' for x in checks)}/{len(checks)} checks passed")
    for item in checks:
        if item["result"] == "FAIL":
            print(f"FAIL {item['check_id']}: {item['detail']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
