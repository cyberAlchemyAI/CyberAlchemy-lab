#!/usr/bin/env python3
"""Apply the exact digest-bound Craft foundation admission transaction."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
BUNDLE_ROOT = LAB / "docs/admission-bundles/0001-craft-foundation-v1"
MANIFEST = BUNDLE_ROOT / "manifest.json"
BUNDLE_RECEIPT = BUNDLE_ROOT / "receipts/validation.json"
AUTHORIZATION = ROOT / "authorization.json"
EXPECTED_MANIFEST = "c748d25ae38c43a30f38d64f4b66875bd3ed5286eb5805e1ae4d8f9841842c32"
EXPECTED_RECEIPT = "417665855df9f0a8781fcd1a3a6db56027467c7c97cd34422c2daf8fc35b4747"
DECISION_ID = "CAL-DECISION-0028-CRAFT-FOUNDATION-V1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp-craft-foundation")
    temp.write_bytes(data)
    os.replace(temp, path)


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def owner_projection(owner: dict[str, Any]) -> bytes:
    renderer_path = LAB / "authority/foundation/v1/render.py"
    spec = importlib.util.spec_from_file_location("foundation_renderer", renderer_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("foundation renderer unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return (module.owners(owner).rstrip() + "\n").encode()


def decision_projection(decision: dict[str, Any]) -> bytes:
    lines = [
        "<!-- GENERATED FILE: edit decision.json and run validate.py. -->",
        "",
        "# Craft Definition and Interaction Foundation v1 Admission",
        "",
        f"- Decision: `{decision['decision_id']}`",
        f"- Status: `{decision['status']}`",
        f"- Principal: `{decision['selection']['selected_by_principal']}`",
        f"- Manifest: `{decision['selection']['manifest_sha256']}`",
        f"- Validation receipt: `{decision['selection']['validation_receipt_sha256']}`",
        "",
        "## Admitted effects",
        "",
    ]
    lines += [f"- {item}" for item in decision["admitted_effects"]]
    lines += ["", "## Context disposition", "", decision["context_disposition"]["effect"], "", "## Excluded effects", ""]
    lines += [f"- {item}" for item in decision["excluded_effects"]]
    lines += ["", "## Claim ceiling", "", decision["claim_ceiling"]]
    return ("\n".join(lines).rstrip() + "\n").encode()


def main() -> int:
    if sha(MANIFEST) != EXPECTED_MANIFEST or sha(BUNDLE_RECEIPT) != EXPECTED_RECEIPT:
        raise SystemExit("BLOCK: approved manifest or receipt digest changed")
    manifest, receipt, auth = load(MANIFEST), load(BUNDLE_RECEIPT), load(AUTHORIZATION)
    if receipt.get("result") != "PASS" or auth["manifest"]["sha256"] != EXPECTED_MANIFEST or auth["validation_receipt"]["sha256"] != EXPECTED_RECEIPT:
        raise SystemExit("BLOCK: authorization or validation result mismatch")

    for item in manifest["candidate_inputs"] + manifest["live_preimages"]:
        if sha(LAB / item["path"]) != item["sha256"]:
            raise SystemExit(f"BLOCK: bound input drift: {item['path']}")
    for item in manifest["postimages"]:
        if sha(BUNDLE_ROOT / item["path"]) != item["sha256"]:
            raise SystemExit(f"BLOCK: postimage drift: {item['path']}")

    source_record = load(LAB / manifest["source_admission_candidate"]["path"])
    owner_binding = load(LAB / manifest["owner_binding_candidate"]["path"])
    if sha(LAB / manifest["source_admission_candidate"]["path"]) != manifest["source_admission_candidate"]["sha256"]:
        raise SystemExit("BLOCK: source-admission candidate drift")
    if sha(LAB / manifest["owner_binding_candidate"]["path"]) != manifest["owner_binding_candidate"]["sha256"]:
        raise SystemExit("BLOCK: owner-binding candidate drift")

    target_map: list[tuple[Path, Path]] = []
    for item in manifest["postimages"]:
        source = BUNDLE_ROOT / item["path"]
        rel = Path(item["path"])
        if rel.parts[0] != "postimages":
            raise SystemExit("BLOCK: non-postimage target")
        target_map.append((source, LAB.joinpath(*rel.parts[1:])))

    owner_target = LAB / "authority/owners/foundation-01/v1/candidates/0003-craft-product/owners.json"
    owner_md_target = owner_target.with_name("OWNERS.md")
    decision_target = ROOT / "decision.json"
    decision_md_target = ROOT / "DECISION.md"
    transaction_receipt = ROOT / "receipts/admission-validation.json"
    mutable_targets = [target for _, target in target_map] + [owner_md_target, decision_target, decision_md_target, transaction_receipt]
    baselines = {path: path.read_bytes() if path.exists() else None for path in mutable_targets}

    try:
        for source, target in target_map:
            atomic_write(target, source.read_bytes())
        owner = load(owner_target)
        atomic_write(owner_md_target, owner_projection(owner))

        admitted_definitions = []
        for candidate_dir in ("0004-change-lifecycle-selection", "0005-craft-workflow-interaction"):
            candidate = load(LAB / f"authority/definitions/candidates/{candidate_dir}/candidate.json")
            for item in candidate["definitions"]:
                definition_path = LAB / item["path"]
                admitted_definitions.append({
                    "definition_id": item["definition_id"],
                    "version": item["version"],
                    "path": item["path"],
                    "sha256": sha(definition_path),
                    "decision_overlay_status": "admitted-current",
                })

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        decision = {
            "schema_version": "cyberalchemy-lab-craft-foundation-admission-decision/v1",
            "decision_id": DECISION_ID,
            "title": "Craft Definition and Interaction Foundation v1 admission",
            "status": "owner-admitted",
            "authority_effect": "five-source-selections-one-owner-binding-eight-definitions-and-bound-registry-postimages-admitted",
            "selection": {
                "option_id": "ADMIT-CRAFT-FOUNDATION-V1",
                "selection_token": auth["selection_token"],
                "selected_by_principal": auth["principal_id"],
                "selected_roles": ["source-admission-owner", "bootstrap-owner-identity", "definition-owner"],
                "selection_source": "Exact digest-bound user instruction in the active task.",
                "recorded_at": now,
                "manifest_sha256": EXPECTED_MANIFEST,
                "validation_receipt_sha256": EXPECTED_RECEIPT,
                "decision_boundary": auth["decision_boundary"],
                "rationale": "Close one dependency-complete semantic foundation at one human checkpoint while preserving the separate authority of every clause."
            },
            "authority_basis": {
                "foundation_owner_decision": "docs/decisions/0013-foundation-01-admission/decision.json",
                "operational_owner_decision": "docs/decisions/0022-context-operational-owner-promotion/decision.json",
                "definition_artifact_type_decision": "docs/decisions/0015-definition-v1-admission/decision.json",
                "principal_id": auth["principal_id"],
                "separation_rule": auth["decision_separation"]
            },
            "admitted_source_selections": source_record["admissions"],
            "admitted_owner_binding": {
                "candidate_path": str((LAB / manifest["owner_binding_candidate"]["path"]).relative_to(LAB)),
                "candidate_sha256": manifest["owner_binding_candidate"]["sha256"],
                "registry_postimage_path": str(owner_target.relative_to(LAB)),
                "registry_postimage_sha256": sha(owner_target),
                "assignment": owner_binding["assignment"],
                "decision_overlay_status": "admitted-active"
            },
            "admitted_definitions": admitted_definitions,
            "context_disposition": manifest["context_disposition"],
            "canonical_postimages": [{"path": str(target.relative_to(LAB)), "sha256": sha(target)} for _, target in target_map],
            "generated_projections": [{"path": str(owner_md_target.relative_to(LAB)), "sha256": sha(owner_md_target), "authority_effect": "none"}],
            "admitted_effects": [
                "Five exact external source selections are admitted for their stated Definition evidence uses.",
                "The exact craft-product-owner role is bound to person:<vrondelli> with separate scope.",
                "Three change-lifecycle and five Craft workflow interaction Definition versions are admitted.",
                "Craft Product is explicitly not inferred to be a root Bounded Context.",
                "The exact Definition registry, generated index, and drift-audit postimages are installed."
            ],
            "admission_result": {
                "result": "complete-craft-foundation-v1-admission",
                "source_selections_admitted": 5,
                "owner_bindings_admitted": 1,
                "definitions_admitted": 8,
                "canonical_definition_versions": 18,
                "current_definition_terms": 16,
                "bounded_contexts_created": 0,
                "implementation_bindings_accepted": 0
            },
            "excluded_effects": manifest["excluded_effects"],
            "claim_ceiling": "This decision admits only the exact source selections, Craft Product owner binding, eight Definition versions, context non-inference disposition, and synchronized Definition/owner postimages bound to the approved manifest. It does not admit Product or Project instances, create a Bounded Context, activate workflow enforcement, accept an implementation binding, commit, push, publish, deploy, or establish a stable release."
        }
        atomic_write(decision_target, json_bytes(decision))
        atomic_write(decision_md_target, decision_projection(decision))

        checks = []
        def check(check_id: str, ok: bool, detail: Any) -> None:
            checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})
        check("approved-manifest-current", sha(MANIFEST) == EXPECTED_MANIFEST, sha(MANIFEST))
        check("approved-receipt-current-pass", sha(BUNDLE_RECEIPT) == EXPECTED_RECEIPT and receipt["result"] == "PASS", {"sha256": sha(BUNDLE_RECEIPT), "result": receipt["result"]})
        check("exact-postimages-installed", all(sha(source) == sha(target) for source, target in target_map), {str(target.relative_to(LAB)): sha(target) for _, target in target_map})
        check("owner-projection-generated", owner_md_target.read_bytes() == owner_projection(owner), sha(owner_md_target))
        live_registry = load(LAB / "authority/definitions/registry.json")
        check("definition-registry-closure", len(live_registry["entries"]) == 18 and len(live_registry["current_lookup"]) == 16, {"entries": len(live_registry["entries"]), "current": len(live_registry["current_lookup"])})
        check("decision-authority-bound", decision["selection"]["selection_token"] == auth["selection_token"] and decision["status"] == "owner-admitted", decision["selection"])
        check("authority-separation-preserved", len(decision["selection"]["selected_roles"]) == 3 and "does not merge" in auth["decision_separation"], auth["decision_separation"])
        check("context-non-inference-preserved", decision["context_disposition"]["selection"] == "product-not-implicitly-bounded-context" and decision["admission_result"]["bounded_contexts_created"] == 0, decision["context_disposition"])
        failed = [item for item in checks if item["result"] == "FAIL"]
        if failed:
            raise RuntimeError("post-admission validation failed: " + ",".join(item["check_id"] for item in failed))
        result = {
            "schema_version": "cyberalchemy-lab-craft-foundation-admission-validation/v1",
            "subject": DECISION_ID,
            "result": "PASS",
            "authority_effect": "evidence-only",
            "checks": checks,
            "summary": {"passed": len(checks), "failed": 0, "total": len(checks)},
            "materials": {"authorization_sha256": sha(AUTHORIZATION), "decision_sha256": sha(decision_target), "decision_projection_sha256": sha(decision_md_target), "manifest_sha256": EXPECTED_MANIFEST, "bundle_receipt_sha256": EXPECTED_RECEIPT},
            "claim_ceiling": "PASS proves exact materialization of the approved Craft foundation admission only. It does not prove runtime implementation, publication, deployment, or stable-release state."
        }
        atomic_write(transaction_receipt, json_bytes(result))
        print("CRAFT_FOUNDATION_ADMISSION=PASS")
        print(f"DECISION_SHA256={sha(decision_target)}")
        print(f"ADMISSION_RECEIPT_SHA256={sha(transaction_receipt)}")
        return 0
    except Exception as error:
        for path, data in baselines.items():
            if data is None:
                if path.exists():
                    path.unlink()
            else:
                atomic_write(path, data)
        failure = {
            "schema_version": "cyberalchemy-lab-craft-foundation-admission-validation/v1",
            "subject": DECISION_ID,
            "result": "FAIL-ROLLED-BACK",
            "authority_effect": "evidence-only",
            "error": str(error),
            "manifest_sha256": EXPECTED_MANIFEST,
            "bundle_receipt_sha256": EXPECTED_RECEIPT,
            "claim_ceiling": "The admission attempt failed and all material targets were restored. Authorization exists, but admission is not established."
        }
        atomic_write(transaction_receipt, json_bytes(failure))
        print(f"CRAFT_FOUNDATION_ADMISSION=FAIL-ROLLED-BACK: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
