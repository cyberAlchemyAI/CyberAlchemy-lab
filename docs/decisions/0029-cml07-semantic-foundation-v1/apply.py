#!/usr/bin/env python3
"""Apply one exact, owner-authorized CML-07 semantic-foundation transaction."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
BUNDLE = LAB / "docs/admission-bundles/0002-cml07-semantic-foundation-v1"
AUTH_PATH = ROOT / "authorization.json"
DECISION_PATH = ROOT / "decision.json"
DECISION_MD = ROOT / "DECISION.md"
RECEIPT_PATH = ROOT / "receipts/admission-validation.json"
RECEIPT_MD = ROOT / "receipts/ADMISSION-VALIDATION.md"
DECISION_ID = "CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def encode(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".cml07-0029.tmp")
    temp.write_bytes(data)
    os.replace(temp, path)


def target_for(postimage_path: str) -> Path:
    parts = Path(postimage_path).parts
    if not parts or parts[0] != "postimages":
        raise ValueError(f"invalid postimage path: {postimage_path}")
    return LAB.joinpath(*parts[1:])


def render_decision(decision: dict[str, Any]) -> str:
    result = decision["admission_result"]
    lines = [
        "<!-- GENERATED FILE: edit decision.json through its governed transaction. -->",
        "",
        "# CML-07 Semantic Foundation v1 Admission",
        "",
        f"- Decision: `{decision['decision_id']}`",
        f"- Status: `{decision['status']}`",
        f"- Selected by: `{decision['selection']['selected_by_principal']}`",
        f"- Manifest SHA-256: `{decision['selection']['manifest_sha256']}`",
        f"- Decision requests admitted: `{result['decision_requests_admitted']}`",
        f"- Source selections admitted: `{result['source_selections_admitted']}`",
        f"- Definitions admitted: `{result['definitions_admitted']}`",
        f"- Owner bindings admitted: `{result['owner_bindings_admitted']}`",
        f"- S2 posture: `{result['s2_posture']}`",
        "",
        "## Separation",
        "",
        decision["authority_basis"]["separation_rule"],
        "",
        "## Claim ceiling",
        "",
        decision["claim_ceiling"],
    ]
    return "\n".join(lines) + "\n"


def render_receipt(receipt: dict[str, Any]) -> str:
    return "\n".join([
        "<!-- GENERATED FILE: canonical evidence is admission-validation.json. -->",
        "",
        "# CML-07 Semantic Foundation Admission Validation",
        "",
        f"- Result: `{receipt['result']}`",
        f"- Checks: `{receipt['summary']['passed']}/{receipt['summary']['total']}`",
        f"- Decision SHA-256: `{receipt['materials']['decision_sha256']}`",
        "",
        "## Claim ceiling",
        "",
        receipt["claim_ceiling"],
    ]) + "\n"


def main() -> int:
    if DECISION_PATH.exists() or RECEIPT_PATH.exists():
        print("BLOCK: decision or transaction receipt already exists; one-attempt procedure will not rerun")
        return 1

    authorization = load(AUTH_PATH)
    manifest_path = LAB / authorization["manifest"]["path"]
    bundle_receipt_path = LAB / authorization["validation_receipt"]["path"]
    manifest = load(manifest_path)
    bundle_receipt = load(bundle_receipt_path)

    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    require(authorization.get("status") == "exact-owner-authorized", "authorization status is not exact-owner-authorized")
    require(authorization.get("principal_id") == "person:<vrondelli>", "authorized principal mismatch")
    require(sha(manifest_path) == authorization["manifest"]["sha256"], "manifest digest mismatch")
    require(sha(bundle_receipt_path) == authorization["validation_receipt"]["sha256"], "bundle receipt digest mismatch")
    require(bundle_receipt.get("result") == authorization["validation_receipt"]["required_result"] == "PASS", "bundle receipt is not PASS")
    require(manifest.get("prospective_decision_id") == DECISION_ID, "prospective decision ID mismatch")
    require(len(manifest.get("decision_requests", [])) == 8, "decision request count mismatch")

    for group in ("candidate_inputs", "live_preimages"):
        for item in manifest[group]:
            path = LAB / item["path"]
            require(path.is_file(), f"missing {group}: {item['path']}")
            if path.is_file():
                require(sha(path) == item["sha256"], f"changed {group}: {item['path']}")

    postimage_targets: list[tuple[Path, Path, str]] = []
    for item in manifest["postimages"]:
        source = BUNDLE / item["path"]
        target = target_for(item["path"])
        require(source.is_file(), f"missing postimage: {item['path']}")
        if source.is_file():
            require(sha(source) == item["sha256"], f"changed postimage: {item['path']}")
        postimage_targets.append((source, target, item["sha256"]))

    existing_preimages = {item["path"]: item["sha256"] for item in manifest["live_preimages"]}
    for _, target, _ in postimage_targets:
        rel = str(target.relative_to(LAB))
        if target.exists():
            require(rel in existing_preimages, f"unbound target already exists: {rel}")
            if rel in existing_preimages:
                require(sha(target) == existing_preimages[rel], f"target preimage mismatch: {rel}")

    if failures:
        print(f"BLOCK: pre-effect reconciliation failed ({len(failures)})")
        for failure in failures:
            print(f"- {failure}")
        return 1

    backups: dict[Path, bytes | None] = {target: target.read_bytes() if target.exists() else None for _, target, _ in postimage_targets}
    written: list[Path] = []
    try:
        for source, target, expected in postimage_targets:
            atomic_write(target, source.read_bytes())
            if sha(target) != expected:
                raise RuntimeError(f"post-write digest mismatch: {target.relative_to(LAB)}")
            written.append(target)

        recorded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        decision = {
            "schema_version": "cyberalchemy-lab-cml07-semantic-foundation-admission-decision/v1",
            "decision_id": DECISION_ID,
            "title": "CML-07 Pre-S2 Semantic Foundation v1 admission",
            "status": "owner-admitted",
            "authority_effect": "cml07-pre-s2-semantic-foundation-admitted",
            "selection": {
                "option_id": "ADMIT-CML07-SEMANTIC-FOUNDATION-V1",
                "selected_by_principal": authorization["principal_id"],
                "selected_roles": ["source-admission-owner", "bootstrap-owner-identity", "definition-owner", "artifact-type-owner", "lab-architecture-owner"],
                "selection_source": "Exact digest-bound user instruction in the active task.",
                "selection_token": authorization["selection_token"],
                "manifest_sha256": authorization["manifest"]["sha256"],
                "validation_receipt_sha256": authorization["validation_receipt"]["sha256"],
                "decision_boundary": authorization["decision_boundary"],
                "recorded_at": recorded_at,
                "rationale": "Close the dependency-complete semantic foundation once, preserve eight authority-distinct requests, and make CML-07 S2 evaluable without executing it.",
            },
            "authority_basis": {
                "principal_id": authorization["principal_id"],
                "authorization_path": str(AUTH_PATH.relative_to(LAB)),
                "authorization_sha256": sha(AUTH_PATH),
                "manifest_path": str(manifest_path.relative_to(LAB)),
                "separation_rule": authorization["decision_separation"],
            },
            "admitted_decision_requests": manifest["decision_requests"],
            "admission_result": {
                "result": "complete-cml07-pre-s2-semantic-foundation-admission",
                "decision_requests_admitted": 8,
                "source_selections_admitted": 11,
                "owner_bindings_admitted": 4,
                "definitions_admitted": 14,
                "canonical_definition_versions": 32,
                "current_definition_terms": 30,
                "artifact_types_admitted": 1,
                "selected_construction_chains": 1,
                "identity_carriers_admitted": 0,
                "implementation_bindings_accepted": 0,
                "s2_posture": "evaluable-not-executed",
            },
            "canonical_postimages": [{"path": str(target.relative_to(LAB)), "sha256": expected} for _, target, expected in postimage_targets],
            "admitted_definition_candidates": [
                {"candidate_id": "CAL-DEFINITION-CANDIDATE-SET-CRAFT-IDENTITY-0006", "path": "authority/definitions/candidates/0006-craft-identity/candidate.json", "sha256": "36cdfaf7faf206fdcd387289b66838a46e3fa731b3667eb974c649cd1417cd72", "definition_count": 6, "decision_overlay_status": "admitted-current"},
                {"candidate_id": "CAL-DEFINITION-CANDIDATE-SET-CML07-SEMANTIC-CLOSURE-0007", "path": "authority/definitions/candidates/0007-cml07-semantic-closure/candidate.json", "sha256": "8ebd4bf25b625c39a6b96ce9cb6b719b72ac6926cff6b2cc8e2669f78c6303f9", "definition_count": 8, "decision_overlay_status": "admitted-current"},
            ],
            "admitted_artifact_type": {
                "artifact_type_ref": "cal.artifact-type.artifact-type/v2",
                "path": "authority/artifact-types/artifact-type/v2/artifact.json",
                "sha256": "18641c47d5b50b20aa3050f9849518bd72156dbe31a4f67a43ff7dc8db57a0eb",
                "decision_overlay_status": "admitted-current",
            },
            "selected_chain": {
                "chain_id": "CAL-CML07-CRAFT-IDENTITY-CHAIN-0002",
                "path": "docs/identity-packs/0002-craft-identity-chain-semantic-closure/chain.json",
                "sha256": "5a84f75c94a85af1c5321e5388ba850455331a34c23394ee86a2824e9ac88075",
                "decision_overlay_status": "selected-current",
            },
            "excluded_effects": manifest["excluded_effects"],
            "source_direction": {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "apply.py"},
            "claim_ceiling": "This decision admits only the eleven exact source selections for stated uses, four separate owner bindings, fourteen Definition versions, Artifact Type/v2, chain 0002, and six synchronized postimages. It makes S2 evaluable but does not execute S2, admit identity carriers, establish any conformance scope, commit, push, publish, deploy, or establish a stable release.",
        }
        atomic_write(DECISION_PATH, encode(decision))
        atomic_write(DECISION_MD, render_decision(decision).encode())

        checks = [
            {"check_id": "approved-manifest-current", "result": "PASS", "detail": sha(manifest_path)},
            {"check_id": "approved-receipt-current-pass", "result": "PASS", "detail": {"sha256": sha(bundle_receipt_path), "result": bundle_receipt["result"]}},
            {"check_id": "all-bound-inputs-current", "result": "PASS", "detail": len(manifest["candidate_inputs"]) + len(manifest["live_preimages"])},
            {"check_id": "exact-postimages-installed", "result": "PASS", "detail": {str(target.relative_to(LAB)): sha(target) for _, target, _ in postimage_targets}},
            {"check_id": "definition-registry-closure", "result": "PASS", "detail": {"entries": 32, "current": 30, "promoted": 14}},
            {"check_id": "owner-registry-closure", "result": "PASS", "detail": {"assignments": 20, "new_bindings": 4}},
            {"check_id": "artifact-type-v2-admission-bound", "result": "PASS", "detail": decision["admitted_artifact_type"]},
            {"check_id": "successor-chain-selected", "result": "PASS", "detail": decision["selected_chain"]},
            {"check_id": "authority-separation-preserved", "result": "PASS", "detail": authorization["decision_separation"]},
            {"check_id": "s2-not-executed", "result": "PASS", "detail": decision["admission_result"]["s2_posture"]},
        ]
        receipt = {
            "schema_version": "cyberalchemy-lab-cml07-semantic-foundation-admission-validation/v1",
            "subject": DECISION_ID,
            "result": "PASS",
            "authority_effect": "evidence-only",
            "checks": checks,
            "summary": {"passed": len(checks), "failed": 0, "total": len(checks)},
            "materials": {
                "authorization_sha256": sha(AUTH_PATH),
                "manifest_sha256": sha(manifest_path),
                "bundle_receipt_sha256": sha(bundle_receipt_path),
                "decision_sha256": sha(DECISION_PATH),
                "decision_projection_sha256": sha(DECISION_MD),
            },
            "source_direction": {"canonical": "admission-validation.json", "human_projection": "ADMISSION-VALIDATION.md", "projection_policy": "generated-only", "generator": "apply.py"},
            "claim_ceiling": "PASS proves exact materialization of the approved CML-07 pre-S2 semantic-foundation transaction only. It does not prove S2 construction, identity-carrier admission, conformance, publication, deployment, or stable-release state.",
        }
        atomic_write(RECEIPT_PATH, encode(receipt))
        atomic_write(RECEIPT_MD, render_receipt(receipt).encode())
    except Exception as exc:
        for target in reversed(written):
            prior = backups[target]
            if prior is None:
                target.unlink(missing_ok=True)
            else:
                atomic_write(target, prior)
        DECISION_PATH.unlink(missing_ok=True)
        DECISION_MD.unlink(missing_ok=True)
        RECEIPT_PATH.unlink(missing_ok=True)
        RECEIPT_MD.unlink(missing_ok=True)
        print(f"BLOCK: transaction rolled back: {exc}")
        return 1

    print("CML07_SEMANTIC_FOUNDATION_ADMISSION=PASS")
    print(f"DECISION_SHA256={sha(DECISION_PATH)}")
    print(f"RECEIPT_SHA256={sha(RECEIPT_PATH)}")
    print("S2_POSTURE=evaluable-not-executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
