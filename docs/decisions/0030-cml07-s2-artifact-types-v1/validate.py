#!/usr/bin/env python3
"""Validate and render evidence for decision 0030 without rewriting candidates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
BUNDLE = LAB / "docs/admission-bundles/0003-cml07-s2-artifact-types-v1"
RECEIPT = ROOT / "receipts/admission-validation.json"
RECEIPT_MD = ROOT / "receipts/ADMISSION-VALIDATION.md"

EXPECTED_MANIFEST_SHA256 = "e8570f086738bd10e12f49cb05fde3b04df0feb635066e437aa3e50792e4e1a5"
EXPECTED_BUNDLE_RECEIPT_SHA256 = "686bc908b5ad0ed22588c32dd2c8c511335bd35acfabf045615e9266884cb4a1"
EXPECTED_DECISION_ID = "CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1"
EXPECTED_TOKEN = (
    "ADMIT-CML07-S2-IDENTITY-ARTIFACT-TYPES "
    f"manifest={EXPECTED_MANIFEST_SHA256} receipt={EXPECTED_BUNDLE_RECEIPT_SHA256}"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_authorization(data: dict) -> str:
    return (
        "<!-- GENERATED FILE: canonical source is authorization.json. -->\n\n"
        "# CML-07 S2 Artifact Type Authorization\n\n"
        f"- Authorization: `{data['authorization_id']}`\n"
        f"- Principal: `{data['principal_id']}`\n"
        f"- Status: `{data['status']}`\n"
        f"- Boundary: `{data['decision_boundary']}`\n"
        f"- Manifest: `{data['manifest']['sha256']}`\n"
        f"- Validation receipt: `{data['validation_receipt']['sha256']}`\n\n"
        "## Authority ceiling\n\n"
        f"{data['authority_ceiling']}\n"
    )


def render_decision(data: dict) -> str:
    admitted = "".join(
        f"- `{item['artifact_type_ref']}`\n" for item in data["admitted_artifact_types"]
    )
    return (
        "<!-- GENERATED FILE: canonical source is decision.json. -->\n\n"
        "# CML-07 S2 Identity Artifact Types v1 Admission\n\n"
        f"- Decision: `{data['decision_id']}`\n"
        f"- Status: `{data['status']}`\n"
        f"- Artifact Types admitted: `{data['admission_result']['artifact_types_admitted']}`\n"
        f"- Candidate files rewritten: `{data['admission_result']['candidate_files_rewritten']}`\n"
        f"- S3 posture: `{data['admission_result']['s3_posture']}`\n\n"
        "## Independently admitted types\n\n"
        f"{admitted}\n"
        "## Separation\n\n"
        f"{data['authority_basis']['separation_rule']}\n\n"
        "## Claim ceiling\n\n"
        f"{data['claim_ceiling']}\n"
    )


def render_receipt(data: dict) -> str:
    rows = "".join(
        f"- `{item['check_id']}`: **{item['result']}**\n" for item in data["checks"]
    )
    return (
        "<!-- GENERATED FILE: canonical source is admission-validation.json. -->\n\n"
        "# CML-07 S2 Artifact Type Admission Validation\n\n"
        f"- Subject: `{data['subject']}`\n"
        f"- Result: **{data['result']}**\n"
        f"- Checks: `{data['summary']['passed']}/{data['summary']['total']}`\n"
        "- Authority effect: `evidence-only`\n\n"
        "## Checks\n\n"
        f"{rows}\n"
        "## Claim ceiling\n\n"
        f"{data['claim_ceiling']}\n"
    )


def main() -> int:
    manifest_path = BUNDLE / "manifest.json"
    bundle_receipt_path = BUNDLE / "receipts/validation.json"
    authorization_path = ROOT / "authorization.json"
    decision_path = ROOT / "decision.json"
    authorization_projection_path = ROOT / "AUTHORIZATION.md"
    decision_projection_path = ROOT / "DECISION.md"

    manifest = load(manifest_path)
    bundle_receipt = load(bundle_receipt_path)
    authorization = load(authorization_path)
    decision = load(decision_path)
    checks: list[dict] = []

    def check(check_id: str, ok: bool, detail) -> None:
        checks.append(
            {
                "check_id": check_id,
                "detail": detail,
                "result": "PASS" if ok else "BLOCK",
            }
        )

    manifest_sha = sha(manifest_path)
    bundle_receipt_sha = sha(bundle_receipt_path)
    check(
        "approved-manifest-current",
        manifest_sha == EXPECTED_MANIFEST_SHA256,
        manifest_sha,
    )
    check(
        "approved-receipt-current-pass",
        bundle_receipt_sha == EXPECTED_BUNDLE_RECEIPT_SHA256
        and bundle_receipt.get("result") == "PASS",
        {"sha256": bundle_receipt_sha, "result": bundle_receipt.get("result")},
    )

    authorization_ok = (
        authorization.get("status") == "exact-owner-authorized"
        and authorization.get("principal_id") == "person:<vrondelli>"
        and authorization.get("selection_token") == EXPECTED_TOKEN
        and authorization.get("manifest", {}).get("sha256") == manifest_sha
        and authorization.get("validation_receipt", {}).get("sha256") == bundle_receipt_sha
        and authorization.get("validation_receipt", {}).get("required_result") == "PASS"
        and authorization.get("decision_boundary")
        == "end-of-cml07-s2-artifact-type-workflow"
    )
    check(
        "exact-owner-authorization-bound",
        authorization_ok,
        {
            "authorization_id": authorization.get("authorization_id"),
            "principal_id": authorization.get("principal_id"),
            "boundary": authorization.get("decision_boundary"),
        },
    )
    check(
        "authorization-projection-generated-from-machine",
        authorization_projection_path.read_text(encoding="utf-8")
        == render_authorization(authorization),
        sha(authorization_projection_path),
    )

    decision_ok = (
        decision.get("decision_id") == EXPECTED_DECISION_ID
        and decision.get("status") == "owner-admitted"
        and decision.get("selection", {}).get("selection_token") == EXPECTED_TOKEN
        and decision.get("selection", {}).get("manifest_sha256") == manifest_sha
        and decision.get("selection", {}).get("validation_receipt_sha256")
        == bundle_receipt_sha
        and decision.get("authority_basis", {}).get("principal_id")
        == authorization.get("principal_id")
        and manifest.get("prospective_decision_id") == EXPECTED_DECISION_ID
    )
    check(
        "decision-owner-admitted-and-digest-bound",
        decision_ok,
        {
            "decision_id": decision.get("decision_id"),
            "status": decision.get("status"),
            "manifest_sha256": decision.get("selection", {}).get("manifest_sha256"),
            "receipt_sha256": decision.get("selection", {}).get(
                "validation_receipt_sha256"
            ),
        },
    )
    check(
        "decision-projection-generated-from-machine",
        decision_projection_path.read_text(encoding="utf-8") == render_decision(decision),
        sha(decision_projection_path),
    )

    manifest_refs = [item["artifact_type_ref"] for item in manifest["artifact_types"]]
    request_refs = [item["artifact_type_ref"] for item in manifest["decision_requests"]]
    decision_refs = [
        item["artifact_type_ref"] for item in decision["admitted_artifact_types"]
    ]
    one_to_one = (
        len(manifest_refs) == len(request_refs) == len(decision_refs) == 6
        and len(set(manifest_refs)) == 6
        and manifest_refs == request_refs == decision_refs
        and len({item["request_id"] for item in manifest["decision_requests"]}) == 6
    )
    check("six-requests-admitted-one-to-one", one_to_one, decision_refs)

    input_results = {}
    for item in manifest["candidate_inputs"]:
        path = LAB / item["path"]
        current = path.is_file() and sha(path) == item["sha256"]
        input_results[item["path"]] = sha(path) if path.is_file() else "missing"
        input_results[item["path"] + "#current"] = current
    check(
        "all-bound-candidate-inputs-current",
        all(value is True for key, value in input_results.items() if key.endswith("#current")),
        {key: value for key, value in input_results.items() if not key.endswith("#current")},
    )

    decision_by_ref = {
        item["artifact_type_ref"]: item for item in decision["admitted_artifact_types"]
    }
    type_results = []
    candidate_separation = True
    type_materials_exact = True
    schemas_closed = True
    identity_fields = []
    for item in manifest["artifact_types"]:
        ref = item["artifact_type_ref"]
        admitted = decision_by_ref.get(ref, {})
        paths = {
            "artifact": LAB / item["artifact_path"],
            "schema": LAB / item["schema_path"],
            "projection": LAB / item["projection_path"],
            "receipt": LAB / item["receipt_path"],
        }
        exact = all(
            path.is_file() and sha(path) == item[f"{name}_sha256"]
            for name, path in paths.items()
        )
        artifact = load(paths["artifact"])
        schema = load(paths["schema"])
        type_receipt = load(paths["receipt"])
        preserved = (
            artifact.get("status") == "candidate-unadmitted"
            and artifact.get("authority_effect") == "none"
            and admitted.get("decision_overlay_status") == "admitted-current"
        )
        admission_binding_exact = (
            admitted.get("artifact_path") == item["artifact_path"]
            and admitted.get("artifact_sha256") == item["artifact_sha256"]
            and admitted.get("schema_path") == item["schema_path"]
            and admitted.get("schema_sha256") == item["schema_sha256"]
            and admitted.get("validation_receipt_path") == item["receipt_path"]
            and admitted.get("validation_receipt_sha256") == item["receipt_sha256"]
        )
        closed = (
            artifact.get("instance_contract", {}).get("closed_representation") is True
            and schema.get("additionalProperties") is False
        )
        identity_field = artifact.get("instance_contract", {}).get("identity_field")
        identity_fields.append(identity_field)
        type_materials_exact = (
            type_materials_exact
            and exact
            and type_receipt.get("result") == "PASS"
            and admission_binding_exact
        )
        candidate_separation = candidate_separation and preserved
        schemas_closed = schemas_closed and closed and bool(identity_field)
        type_results.append(
            {
                "artifact_type_ref": ref,
                "materials_current": exact,
                "type_receipt": type_receipt.get("result"),
                "candidate_bytes_preserved": preserved,
                "admission_binding_exact": admission_binding_exact,
                "closed_schema": closed,
                "identity_field": identity_field,
            }
        )

    check("six-type-material-quadruples-current", type_materials_exact, type_results)
    check(
        "candidate-and-admission-state-separated",
        candidate_separation,
        {
            "candidate_files_rewritten": decision["admission_result"].get(
                "candidate_files_rewritten"
            ),
            "overlay_status": "admitted-current",
        },
    )
    check(
        "closed-schemas-have-distinct-identity-fields",
        schemas_closed
        and len(identity_fields) == 6
        and len(set(identity_fields)) == 6
        and None not in identity_fields,
        identity_fields,
    )

    expected_result = {
        "result": "complete-cml07-s2-artifact-type-admission",
        "decision_requests_admitted": 6,
        "artifact_types_admitted": 6,
        "candidate_files_rewritten": 0,
        "postimages_installed": 0,
        "identity_carriers_admitted": 0,
        "identity_contract_conformance": "not_evaluable-until-s3",
        "implementation_conformance": "not_evaluable",
        "runtime_conformance": "not_evaluable",
        "s3_posture": "evaluable-not-executed",
    }
    transaction = decision.get("transaction_model", {})
    check(
        "overlay-only-admission-counts-and-effects",
        decision.get("admission_result") == expected_result
        and transaction.get("kind") == "decision-overlay-only"
        and transaction.get("candidate_bytes_preserved") is True
        and transaction.get("postimages") == [],
        {"admission_result": decision.get("admission_result"), "transaction": transaction},
    )
    check(
        "single-boundary-preserves-six-authorities",
        manifest.get("decision_boundary", {}).get("mode") == "single-checkpoint"
        and manifest.get("decision_boundary", {}).get("placement")
        == authorization.get("decision_boundary")
        and len({item["artifact_type_ref"] for item in decision["admitted_artifact_types"]})
        == 6,
        manifest.get("decision_boundary"),
    )
    check(
        "s3-and-conformance-not-executed",
        decision.get("admission_result", {}).get("identity_carriers_admitted") == 0
        and decision.get("admission_result", {}).get("s3_posture")
        == "evaluable-not-executed"
        and decision.get("admission_result", {}).get("identity_contract_conformance")
        == "not_evaluable-until-s3"
        and decision.get("admission_result", {}).get("implementation_conformance")
        == "not_evaluable"
        and decision.get("admission_result", {}).get("runtime_conformance")
        == "not_evaluable",
        {
            "identity_carriers_admitted": decision.get("admission_result", {}).get(
                "identity_carriers_admitted"
            ),
            "s3_posture": decision.get("admission_result", {}).get("s3_posture"),
        },
    )

    failed = [item for item in checks if item["result"] != "PASS"]
    receipt = {
        "schema_version": "cyberalchemy-lab-cml07-s2-artifact-type-admission-decision-validation/v1",
        "subject": EXPECTED_DECISION_ID,
        "result": "BLOCK" if failed else "PASS",
        "authority_effect": "evidence-only",
        "checks": checks,
        "summary": {
            "total": len(checks),
            "passed": len(checks) - len(failed),
            "blocked": len(failed),
        },
        "materials": {
            "manifest_sha256": manifest_sha,
            "bundle_receipt_sha256": bundle_receipt_sha,
            "authorization_sha256": sha(authorization_path),
            "authorization_projection_sha256": sha(authorization_projection_path),
            "decision_sha256": sha(decision_path),
            "decision_projection_sha256": sha(decision_projection_path),
        },
        "source_direction": {
            "canonical": "admission-validation.json",
            "human_projection": "ADMISSION-VALIDATION.md",
            "projection_policy": "generated-only",
            "generator": "validate.py",
        },
        "claim_ceiling": (
            "PASS proves only the decision-overlay admission of the six exact CML-07 S2 "
            "Artifact Type contracts at the approved single boundary, with candidate bytes "
            "preserved. It makes S3 candidate authoring evaluable; it does not execute S3, "
            "admit identity carriers, establish identity-contract, implementation, or runtime "
            "conformance, commit, push, publish, deploy, or establish a stable release."
        ),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    RECEIPT_MD.write_text(render_receipt(receipt), encoding="utf-8")

    print(f"CML07_S2_ARTIFACT_TYPE_ADMISSION_VALIDATION={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"RECEIPT_SHA256={sha(RECEIPT)}")
    for item in failed:
        print(f"BLOCK {item['check_id']}: {item['detail']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
