#!/usr/bin/env python3
"""Build the non-effectful CML-07 S2 Artifact Type admission boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
BUNDLE_PATH = ROOT / "bundle.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render(bundle: dict[str, Any], receipt: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical source is bundle.json. -->",
        "",
        "# CML-07 S2 Identity Artifact Type Admission Boundary",
        "",
        f"- Result: `{receipt['result']}`",
        f"- Manifest SHA-256: `{receipt['materials']['manifest_sha256']}`",
        f"- Receipt SHA-256: `{sha(ROOT / 'receipts/validation.json')}`",
        f"- Decision requests: `{len(bundle['decision_requests'])}`",
        f"- Transaction: `{bundle['transaction_model']['kind']}`",
        "",
        "## Independent requests",
        "",
    ]
    for item in bundle["decision_requests"]:
        lines.append(f"- `{item['request_id']}` — `{item['artifact_type_ref']}`")
    lines.extend(["", "## Claim ceiling", "", bundle["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    bundle = load(BUNDLE_PATH)
    checks = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    observed_inputs = {
        item["path"]: sha(LAB / item["path"]) if (LAB / item["path"]).is_file() else "missing"
        for item in bundle["candidate_inputs"]
    }
    check("all-candidate-inputs-current", all(observed_inputs[item["path"]] == item["sha256"] for item in bundle["candidate_inputs"]), observed_inputs)
    pack = load(LAB / "docs/artifact-type-packs/0003-cml07-identity-artifact-types-v1/pack.json")
    pack_manifest = load(LAB / "docs/artifact-type-packs/0003-cml07-identity-artifact-types-v1/manifest.json")
    pack_receipt = load(LAB / "docs/artifact-type-packs/0003-cml07-identity-artifact-types-v1/receipts/validation.json")
    suite_receipt = load(LAB / "tests/conformance/cml07-craft-identity/s2-artifact-types/receipts/validation.json")
    decision = load(LAB / "docs/decisions/0029-cml07-semantic-foundation-v1/decision.json")
    check("predecessor-admits-s2-semantics", decision["status"] == "owner-admitted" and decision["admission_result"]["s2_posture"] == "evaluable-not-executed", decision["admission_result"])
    check("pack-and-suite-pass", pack_receipt["result"] == suite_receipt["result"] == "PASS", {"pack": pack_receipt["result"], "suite": suite_receipt["result"]})
    check("pack-manifest-ready", pack_manifest["status"] == "candidate-ready-for-review" and len(pack_manifest["artifact_types"]) == 6, {"status": pack_manifest["status"], "types": len(pack_manifest["artifact_types"])})

    artifact_checks = []
    for item in pack["artifact_types"]:
        artifact = load(LAB / item["artifact_path"])
        schema = load(LAB / item["schema_path"])
        receipt = load(LAB / item["receipt_path"])
        artifact_checks.append({
            "artifact_type_ref": item["artifact_type_ref"],
            "artifact_current": sha(LAB / item["artifact_path"]) == item["artifact_sha256"],
            "schema_current": sha(LAB / item["schema_path"]) == item["schema_sha256"],
            "receipt_current_pass": sha(LAB / item["receipt_path"]) == item["receipt_sha256"] and receipt["result"] == "PASS",
            "candidate_no_effect": artifact["status"] == "candidate-unadmitted" and artifact["authority_effect"] == "none",
            "schema_closed": schema["additionalProperties"] is False,
            "definitions_admitted": all(binding["admission_posture"] == "admitted" for binding in artifact["semantic_definition_bindings"]),
        })
    check("six-artifact-types-exact-and-ready", len(artifact_checks) == 6 and all(all(value for key, value in item.items() if key != "artifact_type_ref") for item in artifact_checks), artifact_checks)

    request_refs = [item["artifact_type_ref"] for item in bundle["decision_requests"]]
    pack_refs = [item["artifact_type_ref"] for item in pack["artifact_types"]]
    check("six-requests-map-one-to-one", len(request_refs) == len(set(request_refs)) == 6 and request_refs == pack_refs, request_refs)
    check("single-boundary-preserves-separation", bundle["decision_boundary"]["mode"] == "single-checkpoint" and len({item["request_id"] for item in bundle["decision_requests"]}) == 6, bundle["decision_boundary"])
    check("overlay-only-no-postimages", bundle["transaction_model"]["kind"] == "decision-overlay-only" and bundle["transaction_model"]["live_preimages"] == bundle["transaction_model"]["postimages"] == [], bundle["transaction_model"])
    check("bundle-remains-non-effectful", bundle["status"] == "candidate-unadmitted" and bundle["authority_effect"] == "none", bundle["claim_ceiling"])

    blocked = [item for item in checks if item["result"] == "BLOCK"]
    manifest = {
        "schema_version": "cyberalchemy-lab-cml07-s2-artifact-type-admission-manifest/v1",
        "manifest_id": "CAL-CML07-S2-ARTIFACT-TYPE-ADMISSION-MANIFEST-0003",
        "status": "candidate-ready-for-exact-owner-decision" if not blocked else "blocked",
        "authority_effect": "none",
        "bundle_path": str(BUNDLE_PATH.relative_to(LAB)),
        "bundle_sha256": sha(BUNDLE_PATH),
        "prospective_decision_id": bundle["prospective_decision_id"],
        "decision_boundary": bundle["decision_boundary"],
        "decision_requests": bundle["decision_requests"],
        "candidate_inputs": bundle["candidate_inputs"],
        "artifact_types": pack["artifact_types"],
        "transaction_model": bundle["transaction_model"],
        "rollback_policy": bundle["rollback_policy"],
        "excluded_effects": bundle["excluded_effects"],
        "claim_ceiling": "This immutable manifest is ready for one exact artifact-type-owner decision only after its receipt passes. It has no admission, S3 construction, conformance, publication, or deployment effect by itself.",
    }
    dump(ROOT / "manifest.json", manifest)
    receipt = {
        "schema_version": "cyberalchemy-lab-cml07-s2-artifact-type-admission-validation/v1",
        "subject": manifest["manifest_id"],
        "result": "PASS" if not blocked else "BLOCK",
        "promotion_eligibility": "eligible-for-one-exact-digest-bound-owner-decision" if not blocked else "blocked",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"passed": len(checks) - len(blocked), "blocked": len(blocked), "total": len(checks)},
        "materials": {"bundle_sha256": sha(BUNDLE_PATH), "manifest_sha256": sha(ROOT / "manifest.json")},
        "claim_ceiling": "PASS proves exact S2 cohort currentness, candidate schema conformance, six-request separation, and overlay-only transaction scope. It does not admit a type or authorize S3.",
    }
    dump(ROOT / "receipts/validation.json", receipt)
    (ROOT / "BUNDLE.md").write_text(render(bundle, receipt), encoding="utf-8")
    print(f"CML07_S2_ADMISSION_BUNDLE={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"MANIFEST_SHA256={receipt['materials']['manifest_sha256']}")
    print(f"RECEIPT_SHA256={sha(ROOT / 'receipts/validation.json')}")
    return 0 if not blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
