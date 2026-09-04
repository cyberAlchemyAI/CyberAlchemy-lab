#!/usr/bin/env python3
"""Independently validate CML-07 final admission decision 0031."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE_REPO = LAB.parent / "domainspec-core"
BUNDLE = LAB / "docs/admission-bundles/0004-cml07-craft-identity-v1"
MANIFEST_PATH = BUNDLE / "manifest.json"
BUNDLE_RECEIPT_PATH = BUNDLE / "receipts/validation.json"
RECEIPT_PATH = ROOT / "receipts/admission-validation.json"
RECEIPT_MD_PATH = ROOT / "receipts/ADMISSION-VALIDATION.md"

EXPECTED_MANIFEST_SHA256 = "6d492c6d711e493e1fa0103c00951fbe21472548bbd9d16bf77ebaecd4997437"
EXPECTED_BUNDLE_RECEIPT_SHA256 = "688fb15bee259b8dde79cd4a82c85a2d53dd7f0a637a834d1dd4edde8ce8ba9c"
EXPECTED_DECISION_ID = "CAL-DECISION-0031-CML07-CRAFT-IDENTITY-V1"
EXPECTED_TOKEN = (
    "ADMIT-CML07-CRAFT-IDENTITY-V1 "
    f"manifest={EXPECTED_MANIFEST_SHA256} receipt={EXPECTED_BUNDLE_RECEIPT_SHA256}"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RENDER = load_module("cml07_decision_0031_render", ROOT / "render.py")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = [
        "<!-- GENERATED FILE: canonical source is admission-validation.json. -->",
        "",
        "# CML-07 Craft Identity v1 Admission Validation",
        "",
        f"- Subject: `{receipt['subject']}`",
        f"- Result: **{receipt['result']}**",
        f"- Checks: `{receipt['summary']['passed']}/{receipt['summary']['total']}`",
        "- Authority effect: `evidence-only`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{item['check_id']}`: **{item['result']}**" for item in receipt["checks"])
    lines.extend(["", "## Claim ceiling", "", receipt["claim_ceiling"], ""])
    return "\n".join(lines)


def main() -> int:
    manifest = load(MANIFEST_PATH)
    bundle_receipt = load(BUNDLE_RECEIPT_PATH)
    authorization = load(ROOT / "authorization.json")
    decision = load(ROOT / "decision.json")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "BLOCK", "detail": detail})

    manifest_sha = sha(MANIFEST_PATH)
    bundle_receipt_sha = sha(BUNDLE_RECEIPT_PATH)
    check("approved-manifest-current", manifest_sha == EXPECTED_MANIFEST_SHA256, manifest_sha)
    check(
        "approved-bundle-receipt-current-pass",
        bundle_receipt_sha == EXPECTED_BUNDLE_RECEIPT_SHA256 and bundle_receipt.get("result") == "PASS",
        {"sha256": bundle_receipt_sha, "result": bundle_receipt.get("result")},
    )

    authorization_ok = (
        authorization.get("status") == "exact-owner-authorized"
        and authorization.get("principal_id") == "person:<vrondelli>"
        and authorization.get("selection_token") == EXPECTED_TOKEN
        and authorization.get("manifest", {}).get("sha256") == manifest_sha
        and authorization.get("validation_receipt", {}).get("sha256") == bundle_receipt_sha
        and authorization.get("validation_receipt", {}).get("required_result") == "PASS"
        and authorization.get("decision_boundary") == "end-of-complete-cml07-workflow"
        and authorization.get("approval_interactions") == 1
    )
    check(
        "exact-owner-authorization-bound-once",
        authorization_ok,
        {"authorization_id": authorization.get("authorization_id"), "principal": authorization.get("principal_id"), "approval_interactions": authorization.get("approval_interactions")},
    )
    check(
        "authorization-projection-generated-from-machine",
        (ROOT / "AUTHORIZATION.md").read_text(encoding="utf-8") == RENDER.render_authorization(authorization),
        sha(ROOT / "AUTHORIZATION.md"),
    )

    decision_ok = (
        decision.get("decision_id") == EXPECTED_DECISION_ID
        and decision.get("status") == "owner-admitted"
        and decision.get("selection", {}).get("selection_token") == EXPECTED_TOKEN
        and decision.get("selection", {}).get("manifest_sha256") == manifest_sha
        and decision.get("selection", {}).get("validation_receipt_sha256") == bundle_receipt_sha
        and decision.get("selection", {}).get("approval_interactions") == 1
        and manifest.get("decision_request_set", {}).get("prospective_decision_id") == EXPECTED_DECISION_ID
    )
    check(
        "decision-owner-admitted-and-digest-bound",
        decision_ok,
        {"decision_id": decision.get("decision_id"), "status": decision.get("status"), "recorded_at": decision.get("selection", {}).get("recorded_at")},
    )
    check(
        "decision-projection-generated-from-machine",
        (ROOT / "DECISION.md").read_text(encoding="utf-8") == RENDER.render_decision(decision),
        sha(ROOT / "DECISION.md"),
    )

    predecessor_results = {}
    for item in manifest["predecessor_bindings"]:
        path = LAB / item["path"]
        predecessor_results[item["path"]] = sha(path) if path.is_file() else "missing"
    check(
        "all-predecessor-bindings-current",
        all(predecessor_results[item["path"]] == item["sha256"] for item in manifest["predecessor_bindings"]),
        predecessor_results,
    )

    material_results = []
    for item in manifest["candidate_artifacts"]:
        path_pairs = [
            ("machine_path", "machine_sha256"),
            ("projection_path", "projection_sha256"),
            ("schema_path", "schema_sha256"),
            ("validation_receipt_path", "validation_receipt_sha256"),
            ("validation_projection_path", "validation_projection_sha256"),
        ]
        current = all(
            (LAB / item[path_key]).is_file()
            and sha(LAB / item[path_key]) == item[sha_key]
            for path_key, sha_key in path_pairs
        )
        validation_result = load(LAB / item["validation_receipt_path"]).get("result")
        material_results.append({"identity_ref": item["identity_ref"], "current": current, "validation": validation_result})
    check(
        "six-carrier-material-sets-current",
        len(material_results) == 6 and all(item["current"] and item["validation"] == "PASS" for item in material_results),
        material_results,
    )

    evidence_results = {}
    for item in manifest["evidence"]:
        path = LAB / item["path"]
        evidence_results[item["path"]] = sha(path) if path.is_file() else "missing"
    check(
        "complete-evidence-surface-current",
        all(evidence_results[item["path"]] == item["sha256"] for item in manifest["evidence"]),
        evidence_results,
    )

    admissions = load(LAB / "authority/decisions/source-admission/craft-identity-v1/v1/admissions.json")
    source_results = []
    for admission in admissions["admissions"]:
        selected_sha, file_sha = selected_source_sha(admission)
        current = selected_sha == admission["selected_sha256"] and file_sha == admission["source_file_sha256_at_authoring"]
        source_results.append({"admission_id": admission["admission_id"], "current": current, "selected_sha256": selected_sha, "source_file_sha256": file_sha})
    check(
        "all-eight-external-source-selections-current",
        len(source_results) == 8 and all(item["current"] for item in source_results),
        source_results,
    )

    request_by_ref = {item["identity_ref"]: item for item in manifest["decision_request_set"]["requests"]}
    manifest_by_ref = {item["identity_ref"]: item for item in manifest["candidate_artifacts"]}
    decision_by_ref = {item["identity_ref"]: item for item in decision["admitted_carriers"]}
    refs = list(manifest_by_ref)
    binding_results = []
    for ref in refs:
        request = request_by_ref.get(ref, {})
        manifest_item = manifest_by_ref[ref]
        admitted = decision_by_ref.get(ref, {})
        exact = (
            request.get("request_id") == admitted.get("request_id")
            and request.get("owner_role") == admitted.get("owner_role")
            and manifest_item.get("artifact_type_ref") == admitted.get("artifact_type_ref")
            and manifest_item.get("machine_path") == admitted.get("machine_path")
            and manifest_item.get("machine_sha256") == admitted.get("machine_sha256")
            and admitted.get("decision_overlay_status") == "admitted-current"
        )
        carrier = load(LAB / manifest_item["machine_path"])
        preserved = carrier.get("status") == "candidate-unadmitted" and carrier.get("authority_effect") == "none"
        binding_results.append({"identity_ref": ref, "binding_exact": exact, "candidate_bytes_preserved": preserved})
    check(
        "six-independent-requests-admitted-one-to-one",
        len(request_by_ref) == len(manifest_by_ref) == len(decision_by_ref) == 6
        and all(item["binding_exact"] and item["candidate_bytes_preserved"] for item in binding_results),
        binding_results,
    )

    graph_manifest = manifest_by_ref["CAL-IDENTITY-GRAPH-CRAFT-V1"]
    graph = load(LAB / graph_manifest["machine_path"])
    graph_relations = [
        {"relation_id": item["relation_id"], "relation_kind": item["relation_kind"], "source_ref": item["source_ref"], "target_ref": item["target_ref"]}
        for item in graph["relations"]
    ]
    check(
        "five-graph-relations-admitted-exactly",
        len(graph_relations) == len(decision.get("admitted_relations", [])) == 5
        and graph_relations == decision.get("admitted_relations"),
        graph_relations,
    )

    assessment_path = LAB / decision["recognized_conformance"]["assessment_path"]
    assessment = load(assessment_path)
    expected_conformance = {
        "validation_result": "PASS",
        "schema_conformance": "PASS",
        "identity_contract_conformance": "PASS",
        "carrier_admission": "candidate-unadmitted",
        "implementation_conformance": "not_evaluable",
        "runtime_conformance": "not_evaluable",
    }
    recognized = decision["recognized_conformance"]
    check(
        "scoped-conformance-recognized-with-ceilings",
        sha(assessment_path) == recognized["assessment_sha256"]
        and assessment.get("result") == "PASS"
        and assessment.get("assessment") == expected_conformance
        and recognized == {
            "assessment_path": str(assessment_path.relative_to(LAB)),
            "assessment_sha256": sha(assessment_path),
            "validation_result": "PASS",
            "schema_conformance": "PASS",
            "identity_contract_conformance": "PASS",
            "implementation_conformance": "not_evaluable",
            "runtime_conformance": "not_evaluable",
        },
        recognized,
    )

    expected_result = {
        "result": "complete-cml07-craft-identity-admission",
        "approval_interactions": 1,
        "decision_requests_admitted": 6,
        "identity_carriers_admitted": 6,
        "identity_relations_admitted": 5,
        "candidate_files_rewritten": 0,
        "postimages_installed": 0,
        "craft_root_bounded_context": "absent",
        "goal_achievement": "not_proven",
        "migration_completion": "not_proven",
        "product_feature_admission": "not_evaluable",
        "product_capability_admission": "not_evaluable",
        "schema_conformance": "PASS",
        "identity_contract_conformance": "PASS",
        "implementation_conformance": "not_evaluable",
        "runtime_conformance": "not_evaluable",
        "cml07_status": "complete-at-identity-contract-boundary",
    }
    check("admission-counts-and-claim-ceilings-exact", decision.get("admission_result") == expected_result, decision.get("admission_result"))
    check(
        "single-approval-boundary-preserved",
        manifest["decision_boundary"]["intermediate_approvals"] == 0
        and manifest["decision_boundary"]["final_approvals"] == 1
        and manifest["decision_request_set"]["approval_interactions_required"] == 1
        and decision["selection"]["approval_interactions"] == 1,
        manifest["decision_boundary"],
    )
    check("no-craft-root-bounded-context", not (LAB / "contexts/craft").exists(), "contexts/craft is absent")
    transaction = decision.get("transaction_model", {})
    check(
        "overlay-only-candidate-bytes-preserved",
        transaction.get("kind") == "decision-overlay-only"
        and transaction.get("candidate_bytes_preserved") is True
        and transaction.get("postimages") == [],
        transaction,
    )

    failed = [item for item in checks if item["result"] != "PASS"]
    receipt = {
        "schema_version": "cyberalchemy-lab-cml07-craft-identity-admission-validation/v1",
        "subject": EXPECTED_DECISION_ID,
        "result": "BLOCK" if failed else "PASS",
        "authority_effect": "evidence-only",
        "checks": checks,
        "summary": {"total": len(checks), "passed": len(checks) - len(failed), "blocked": len(failed)},
        "materials": {
            "manifest_sha256": manifest_sha,
            "bundle_receipt_sha256": bundle_receipt_sha,
            "authorization_sha256": sha(ROOT / "authorization.json"),
            "authorization_projection_sha256": sha(ROOT / "AUTHORIZATION.md"),
            "decision_sha256": sha(ROOT / "decision.json"),
            "decision_projection_sha256": sha(ROOT / "DECISION.md"),
        },
        "source_direction": {
            "canonical": "admission-validation.json",
            "human_projection": "ADMISSION-VALIDATION.md",
            "projection_policy": "generated-only",
            "generator": "validate.py",
        },
        "claim_ceiling": "PASS proves only the exact decision-overlay admission of the six CML-07 Craft identity carriers and five bound graph relations, plus recognition of schema and identity-contract conformance. It does not prove Goal achievement, migration completion, Product Feature or Product Capability admission, implementation or runtime conformance, commit, push, publication, release, deployment, source deletion, or stable-release state.",
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT_MD_PATH.write_text(render_receipt(receipt), encoding="utf-8")

    print(f"CML07_CRAFT_IDENTITY_ADMISSION_VALIDATION={receipt['result']}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"RECEIPT_SHA256={sha(RECEIPT_PATH)}")
    for item in failed:
        print(f"BLOCK {item['check_id']}: {item['detail']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
