#!/usr/bin/env python3
"""Build the single-boundary final CML-07 Craft identity admission bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE_REPO = LAB.parent / "domainspec-core"
BUNDLE_PATH = ROOT / "bundle.json"
MANIFEST_PATH = ROOT / "manifest.json"
RECEIPT_PATH = ROOT / "receipts/validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_bundle(bundle: dict[str, Any], manifest: dict[str, Any], receipt: dict[str, Any]) -> str:
    manifest_sha = sha(MANIFEST_PATH)
    receipt_sha = sha(RECEIPT_PATH)
    lines = [
        "<!-- GENERATED FILE: canonical sources are bundle.json, manifest.json, and receipts/validation.json. -->",
        "",
        "# CML-07 Craft Identity v1 Final Admission Bundle",
        "",
        f"- Bundle: `{bundle['bundle_id']}`",
        f"- Result: **{receipt['result']}**",
        f"- Candidate carriers: `{len(bundle['candidate_artifacts'])}`",
        f"- Independent requests: `{len(bundle['decision_request_set']['requests'])}`",
        f"- Approval interactions required: `{bundle['decision_request_set']['approval_interactions_required']}`",
        f"- Manifest: `{manifest_sha}`",
        f"- Validation receipt: `{receipt_sha}`",
        "",
        "## Candidate carriers",
        "",
    ]
    for item in manifest["candidate_artifacts"]:
        lines.append(
            f"- `{item['identity_ref']}` — `{item['artifact_type_ref']}` — owner `role:{item['owner_role']}`"
        )
    lines.extend(["", "## Single approval boundary", "", bundle["decision_boundary"]["rule"], "", "## Exact approval token", ""])
    if receipt["result"] == "PASS":
        lines.append(
            f"`ADMIT-CML07-CRAFT-IDENTITY-V1 manifest={manifest_sha} receipt={receipt_sha}`"
        )
    else:
        lines.append("No approval token is available while validation is blocked.")
    lines.extend(["", "## Claim ceiling", "", bundle["claim_ceiling"], ""])
    return "\n".join(lines)


def render_manifest(manifest: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical source is manifest.json. -->",
        "",
        "# CML-07 Craft Identity v1 Manifest",
        "",
        f"- Manifest: `{manifest['manifest_id']}`",
        f"- Status: `{manifest['status']}`",
        f"- Candidate artifacts: `{len(manifest['candidate_artifacts'])}`",
        f"- Decision requests: `{len(manifest['decision_request_set']['requests'])}`",
        f"- Approval interactions: `{manifest['decision_request_set']['approval_interactions_required']}`",
        "",
        "## Frozen carriers",
        "",
    ]
    for item in manifest["candidate_artifacts"]:
        lines.append(f"- `{item['identity_ref']}`: `{item['machine_sha256']}`")
    lines.extend(["", "## Transaction", "", "Admission is a decision overlay. Candidate bytes are preserved and there are no live postimages.", "", "## Claim ceiling", "", manifest["claim_ceiling"], ""])
    return "\n".join(lines)


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical source is validation.json. -->",
        "",
        "# CML-07 Craft Identity v1 Bundle Validation",
        "",
        f"- Subject: `{receipt['subject']}`",
        f"- Result: **{receipt['result']}**",
        f"- Checks: `{receipt['summary']['passed']}/{receipt['summary']['total']}`",
        "- Authority effect: `none`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{item['check_id']}`: **{item['result']}**" for item in receipt["checks"])
    lines.extend(["", "## Claim ceiling", "", receipt["claim_ceiling"], ""])
    return "\n".join(lines)


def selected_source_sha(admission: dict[str, Any]) -> tuple[str, str]:
    path = SOURCE_REPO / admission["source_path"]
    file_sha = sha(path) if path.is_file() else "missing"
    if admission["selector_kind"] == "whole-file-v1":
        return file_sha, file_sha
    if admission["selector_kind"] == "line-range-v1" and path.is_file():
        lines = path.read_bytes().splitlines(keepends=True)
        selected = b"".join(lines[admission["start_line"] - 1 : admission["end_line"]])
        return hashlib.sha256(selected).hexdigest(), file_sha
    return "unsupported-selector", file_sha


def main() -> int:
    bundle = load(BUNDLE_PATH)
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    predecessor_results = {}
    for item in bundle["predecessor_bindings"]:
        path = LAB / item["path"]
        predecessor_results[item["path"]] = sha(path) if path.is_file() else "missing"
    check(
        "all-predecessor-bindings-current",
        all(predecessor_results[item["path"]] == item["sha256"] for item in bundle["predecessor_bindings"]),
        predecessor_results,
    )

    decision29 = load(LAB / "docs/decisions/0029-cml07-semantic-foundation-v1/decision.json")
    decision30 = load(LAB / "docs/decisions/0030-cml07-s2-artifact-types-v1/decision.json")
    check(
        "semantic-and-artifact-type-admissions-close",
        decision29.get("status") == "owner-admitted"
        and decision29.get("admission_result", {}).get("definitions_admitted") == 14
        and decision30.get("status") == "owner-admitted"
        and decision30.get("admission_result", {}).get("artifact_types_admitted") == 6,
        {"semantic": decision29.get("admission_result"), "artifact_types": decision30.get("admission_result")},
    )

    admissions = load(LAB / "authority/decisions/source-admission/craft-identity-v1/v1/admissions.json")
    source_results = []
    for admission in admissions["admissions"]:
        selected_sha, file_sha = selected_source_sha(admission)
        current = (
            selected_sha == admission["selected_sha256"]
            and file_sha == admission["source_file_sha256_at_authoring"]
        )
        source_results.append({"admission_id": admission["admission_id"], "current": current, "selected_sha256": selected_sha, "source_file_sha256": file_sha})
    check(
        "all-eight-source-selections-current",
        len(source_results) == 8 and all(item["current"] for item in source_results),
        source_results,
    )

    artifact_entries = []
    carrier_states = []
    individual_receipts_pass = True
    for item in bundle["candidate_artifacts"]:
        machine = LAB / item["machine_path"]
        projection = LAB / item["projection_path"]
        schema = LAB / item["schema_path"]
        validation = LAB / item["validation_receipt_path"]
        validation_projection_rel = f"evidence/validation/cml07-craft-identity/receipts/{item['subject_id'].upper()}-VALIDATION.md"
        validation_projection = LAB / validation_projection_rel
        carrier = load(machine)
        validation_data = load(validation)
        identity_fields = ["product_id", "project_id", "binding_id", "goal_id", "lineage_id", "graph_id"]
        observed_identity = next((carrier[field] for field in identity_fields if field in carrier), None)
        current = all(path.is_file() for path in [machine, projection, schema, validation, validation_projection])
        state_ok = carrier.get("status") == "candidate-unadmitted" and carrier.get("authority_effect") == "none"
        receipt_ok = validation_data.get("result") == "PASS" and validation_data.get("subject") == item["identity_ref"]
        individual_receipts_pass = individual_receipts_pass and receipt_ok
        carrier_states.append({"identity_ref": observed_identity, "expected": item["identity_ref"], "state_ok": state_ok, "receipt": validation_data.get("result")})
        artifact_entries.append(
            {
                **item,
                "machine_sha256": sha(machine) if machine.is_file() else "missing",
                "projection_sha256": sha(projection) if projection.is_file() else "missing",
                "schema_sha256": sha(schema) if schema.is_file() else "missing",
                "validation_receipt_sha256": sha(validation) if validation.is_file() else "missing",
                "validation_projection_path": validation_projection_rel,
                "validation_projection_sha256": sha(validation_projection) if validation_projection.is_file() else "missing",
                "materials_present": current,
                "candidate_state": "candidate-unadmitted" if state_ok else "invalid",
            }
        )
    check(
        "six-candidate-carrier-material-sets-present",
        len(artifact_entries) == 6 and all(item["materials_present"] for item in artifact_entries),
        artifact_entries,
    )
    check(
        "six-carriers-remain-non-effectful-candidates",
        all(item["state_ok"] and item["identity_ref"] == item["expected"] for item in carrier_states),
        carrier_states,
    )
    check(
        "six-individual-validation-receipts-pass",
        individual_receipts_pass,
        [{"identity_ref": item["identity_ref"], "receipt_sha256": item["validation_receipt_sha256"]} for item in artifact_entries],
    )

    evidence_entries = []
    for key, relative in bundle["evidence_bindings"].items():
        path = LAB / relative
        evidence_entries.append({"kind": key, "path": relative, "sha256": sha(path) if path.is_file() else "missing"})
    check(
        "complete-s4-evidence-surface-present",
        all(item["sha256"] != "missing" for item in evidence_entries),
        evidence_entries,
    )

    validation = load(LAB / bundle["evidence_bindings"]["aggregate_validation_path"])
    conformance = load(LAB / bundle["evidence_bindings"]["conformance_assessment_path"])
    check(
        "aggregate-validation-pass",
        validation.get("result") == "PASS" and validation.get("summary", {}).get("blocked") == 0,
        {"result": validation.get("result"), "summary": validation.get("summary")},
    )
    expected_scopes = {
        "validation_result": "PASS",
        "schema_conformance": "PASS",
        "identity_contract_conformance": "PASS",
        "carrier_admission": "candidate-unadmitted",
        "implementation_conformance": "not_evaluable",
        "runtime_conformance": "not_evaluable",
    }
    check(
        "scoped-conformance-pass-with-runtime-separation",
        conformance.get("result") == "PASS" and conformance.get("assessment") == expected_scopes,
        conformance.get("assessment"),
    )

    request_set = bundle["decision_request_set"]
    request_refs = [item["identity_ref"] for item in request_set["requests"]]
    artifact_refs = [item["identity_ref"] for item in bundle["candidate_artifacts"]]
    owner_roles = {item["role_id"] for item in load(LAB / "authority/owners/foundation-01/v1/candidates/0004-craft-identity/owners.json")["role_assignments"]}
    request_ids = [item["request_id"] for item in request_set["requests"]]
    check(
        "six-decision-requests-map-one-to-one",
        len(request_refs) == len(set(request_refs)) == len(request_ids) == len(set(request_ids)) == 6
        and request_refs == artifact_refs
        and all(item["owner_role"] in owner_roles for item in request_set["requests"]),
        {"identity_refs": request_refs, "owner_roles": [item["owner_role"] for item in request_set["requests"]]},
    )
    check(
        "single-final-approval-boundary",
        bundle["decision_boundary"]["intermediate_approvals"] == 0
        and bundle["decision_boundary"]["final_approvals"] == 1
        and request_set["approval_interactions_required"] == 1,
        bundle["decision_boundary"],
    )
    check(
        "no-craft-root-bounded-context",
        not (LAB / "contexts/craft").exists(),
        "contexts/craft is absent",
    )
    transaction = bundle["transaction_model"]
    check(
        "overlay-only-rollback-rehearsal",
        transaction["kind"] == "decision-overlay-only"
        and transaction["candidate_bytes_preserved"] is True
        and transaction["live_preimages"] == []
        and transaction["postimages"] == [],
        {"rehearsal": "remove or reject an incomplete decision package; no candidate rollback required", "transaction": transaction},
    )

    failed = [item for item in checks if item["result"] != "PASS"]
    material_inputs = [
        {"path": str(BUNDLE_PATH.relative_to(LAB)), "sha256": sha(BUNDLE_PATH)},
        {"path": str(Path(__file__).resolve().relative_to(LAB)), "sha256": sha(Path(__file__).resolve())},
    ]
    manifest = {
        "schema_version": "cyberalchemy-lab-cml07-craft-identity-admission-manifest/v1",
        "manifest_id": "CAL-CML07-CRAFT-IDENTITY-ADMISSION-MANIFEST-0004",
        "status": "candidate-ready-for-exact-owner-decision" if not failed else "candidate-blocked",
        "authority_effect": "none",
        "bundle": {"path": str(BUNDLE_PATH.relative_to(LAB)), "sha256": sha(BUNDLE_PATH)},
        "builder": {"path": str(Path(__file__).resolve().relative_to(LAB)), "sha256": sha(Path(__file__).resolve())},
        "predecessor_bindings": bundle["predecessor_bindings"],
        "candidate_artifacts": artifact_entries,
        "evidence": evidence_entries,
        "decision_boundary": bundle["decision_boundary"],
        "decision_request_set": request_set,
        "transaction_model": transaction,
        "excluded_effects": bundle["excluded_effects"],
        "source_direction": {"canonical": "manifest.json", "human_projection": "MANIFEST.md", "projection_policy": "generated-only", "generator": "build.py"},
        "claim_ceiling": bundle["claim_ceiling"],
    }
    write_json(MANIFEST_PATH, manifest)
    (ROOT / "MANIFEST.md").write_text(render_manifest(manifest), encoding="utf-8")

    receipt = {
        "schema_version": "cyberalchemy-lab-cml07-craft-identity-admission-bundle-validation/v1",
        "subject": manifest["manifest_id"],
        "result": "BLOCK" if failed else "PASS",
        "authority_effect": "none",
        "checks": checks,
        "summary": {"total": len(checks), "passed": len(checks) - len(failed), "blocked": len(failed)},
        "materials": {
            "bundle_sha256": sha(BUNDLE_PATH),
            "builder_sha256": sha(Path(__file__).resolve()),
            "manifest_sha256": sha(MANIFEST_PATH),
            "manifest_projection_sha256": sha(ROOT / "MANIFEST.md"),
            "inputs": material_inputs,
        },
        "promotion_eligibility": "eligible-for-one-exact-digest-bound-final-owner-decision" if not failed else "not-eligible",
        "source_direction": {"canonical": "validation.json", "human_projection": "VALIDATION.md", "projection_policy": "generated-only", "generator": "build.py"},
        "claim_ceiling": bundle["claim_ceiling"],
    }
    write_json(RECEIPT_PATH, receipt)
    (ROOT / "receipts/VALIDATION.md").write_text(render_receipt(receipt), encoding="utf-8")
    (ROOT / "BUNDLE.md").write_text(render_bundle(bundle, manifest, receipt), encoding="utf-8")

    print(f"CML07_FINAL_ADMISSION_BUNDLE={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"MANIFEST_SHA256={sha(MANIFEST_PATH)}")
    print(f"RECEIPT_SHA256={sha(RECEIPT_PATH)}")
    for item in failed:
        print(f"BLOCK {item['check_id']}: {item['detail']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
