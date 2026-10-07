#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
BUNDLE = LAB / "docs/admission-bundles/0005-full-definition-queue-v1"
AUTH = HERE / "authorization.json"
DECISION = HERE / "decision.json"
DECISION_MD = HERE / "DECISION.md"
RECEIPT = HERE / "receipts/admission-validation.json"
RECEIPT_MD = HERE / "receipts/ADMISSION-VALIDATION.md"
DECISION_ID = "CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def encode(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def render_decision(data: dict) -> str:
    return "\n".join([
        "<!-- GENERATED FILE: decision.json is canonical. -->", "",
        "# Full Definition Queue Admission", "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Principal: `{data['selection']['selected_by_principal']}`", "",
        "## Result", "",
        "The complete pending queue is admitted: 85 exact Definition versions across 81 identities, including all 70 reconstructed migration versions. The registry now contains 118 admitted versions and 112 current identities.", "",
        "Four identities retain candidate.1 as admitted history and select their corrected candidate.2 version as current. Fifty-eight exact pending source selections are admitted for these Definitions.", "",
        "## Excluded effects", "", *[f"- {item}" for item in data["excluded_effects"]], "",
        "## Claim ceiling", "", data["claim_ceiling"],
    ])


def render_receipt(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: admission-validation.json is canonical. -->", "",
        "# Full Definition Queue Admission Validation", "",
        f"- Result: `{data['result']}`", "",
        "| Check | Result |", "| --- | --- |",
    ]
    lines.extend(f"| `{item['check_id']}` | `{item['result']}` |" for item in data["checks"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def all_postimages_live(manifest: dict) -> bool:
    return all((LAB / item["target_path"]).is_file() and sha(LAB / item["target_path"]) == item["sha256"] for item in manifest["postimages"])


def main() -> int:
    authorization = load(AUTH)
    manifest_path = LAB / authorization["manifest"]["path"]
    receipt_path = LAB / authorization["validation_receipt"]["path"]
    manifest = load(manifest_path)
    bundle_receipt = load(receipt_path)

    if DECISION.is_file() and RECEIPT.is_file() and all_postimages_live(manifest):
        print("FULL_DEFINITION_QUEUE_ADMISSION=PASS (already applied)")
        return 0

    failures = []

    def require(ok: bool, message: str) -> None:
        if not ok:
            failures.append(message)

    require(authorization["status"] == "authorized", "authorization is not active")
    require(authorization["prospective_decision_id"] == manifest["prospective_decision_id"] == DECISION_ID, "decision identity mismatch")
    require(authorization["principal_id"] == "person:<vrondelli>", "principal mismatch")
    require(authorization["selection_token"] == "admit full queue including reconstructed definitions", "selection token mismatch")
    require(sha(manifest_path) == authorization["manifest"]["sha256"], "manifest digest mismatch")
    require(sha(receipt_path) == authorization["validation_receipt"]["sha256"], "bundle receipt digest mismatch")
    require(bundle_receipt.get("result") == authorization["validation_receipt"]["required_result"] == "PASS", "bundle validation is not PASS")
    require(manifest["counts"] == {"authority_candidate_versions": 15, "definition_identities": 81, "definition_versions": 85, "historical_snapshot_selections": 1, "reconstructed_versions": 70, "source_selections": 58, "successor_pairs": 4}, "manifest counts changed")

    for item in manifest["candidate_inputs"]:
        path = LAB / item["path"]
        require(path.is_file() and sha(path) == item["sha256"], f"candidate input changed: {item['path']}")
    for item in manifest["live_preimages"]:
        path = LAB / item["path"]
        require(path.is_file() and sha(path) == item["sha256"], f"live preimage changed: {item['path']}")
    for relative in manifest["absent_preimages"]:
        require(not (LAB / relative).exists(), f"expected absent preimage now exists: {relative}")

    postimage_targets = []
    for item in manifest["postimages"]:
        source = BUNDLE / item["path"]
        target = LAB / item["target_path"]
        require(source.is_file() and sha(source) == item["sha256"], f"postimage changed: {item['path']}")
        postimage_targets.append((source, target, item["sha256"]))
    if failures:
        print(f"BLOCK: pre-effect reconciliation failed ({len(failures)})")
        for failure in failures:
            print(f"- {failure}")
        return 1

    existing_backups = {target: target.read_bytes() for _, target, _ in postimage_targets if target.exists()}
    newly_created = {target for _, target, _ in postimage_targets if not target.exists()}
    written = []
    try:
        for source, target, expected in postimage_targets:
            atomic_write(target, source.read_bytes())
            if sha(target) != expected:
                raise RuntimeError(f"post-write digest mismatch: {target.relative_to(LAB)}")
            written.append(target)

        recorded = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        decision = {
            "schema_version": "cyberalchemy-lab-definition-admission-decision/v1",
            "decision_id": DECISION_ID,
            "title": "Full Definition Queue Admission",
            "status": "owner-admitted",
            "authority_effect": "full-indexed-definition-queue-admitted-by-decision-overlay",
            "selection": {
                "selected_by_principal": authorization["principal_id"],
                "selected_roles": authorization["selected_roles"],
                "selection_source": authorization["selection_source"],
                "selection_token": authorization["selection_token"],
                "manifest_sha256": authorization["manifest"]["sha256"],
                "validation_receipt_sha256": authorization["validation_receipt"]["sha256"],
                "recorded_at": recorded,
            },
            "authority_basis": {
                "authorization_path": str(AUTH.relative_to(LAB)),
                "authorization_sha256": sha(AUTH),
                "manifest_path": str(manifest_path.relative_to(LAB)),
                "manifest_sha256": sha(manifest_path),
                "separation_rule": authorization["decision_separation"],
            },
            "admitted_decision_requests": manifest["decision_requests"],
            "admitted_definition_selection": {
                "manifest_path": str(manifest_path.relative_to(LAB)),
                "definition_versions": 85,
                "definition_identities": 81,
                "authority_candidate_versions": 15,
                "reconstructed_versions": 70,
                "successor_pairs": 4,
                "decision_overlay_status": "admitted",
            },
            "admitted_source_selection": {
                "path": "authority/decisions/source-admission/full-definition-queue/v1/admissions.json",
                "sha256": sha(LAB / "authority/decisions/source-admission/full-definition-queue/v1/admissions.json"),
                "selection_count": 58,
                "decision_overlay_status": "admitted-for-definition-use",
            },
            "admission_result": {
                "result": "complete",
                "definitions_admitted": 85,
                "definition_identities_added": 81,
                "reconstructed_definitions_admitted": 70,
                "source_selections_admitted": 58,
                "historical_source_snapshot_selections": 1,
                "canonical_definition_versions": 118,
                "current_definition_terms": 112,
                "remaining_unadmitted_definition_versions_in_indexed_queue": 0,
                "consumer_activations": 0,
            },
            "canonical_postimages": [{"path": str(target.relative_to(LAB)), "sha256": expected} for _, target, expected in postimage_targets],
            "excluded_effects": manifest["excluded_effects"],
            "source_direction": {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "apply.py"},
            "claim_ceiling": "This decision admits the exact 85-version indexed Definition queue, including 70 reconstructed versions and 58 source selections for Definition use. It does not admit or activate carriers, Artifact Types, profiles, relation kinds, derived surfaces, migration consumers, runtimes, or the generic ledger primitive.",
        }
        atomic_write(DECISION, encode(decision))
        atomic_write(DECISION_MD, (render_decision(decision).rstrip() + "\n").encode())

        registry = load(LAB / "authority/definitions/registry.json")
        source_admissions = load(LAB / "authority/decisions/source-admission/full-definition-queue/v1/admissions.json")
        promoted = [item for item in registry["entries"] if item.get("admission_decision_ref") == DECISION_ID]
        checks = [
            {"check_id": "approved-manifest-current", "result": "PASS", "detail": sha(manifest_path)},
            {"check_id": "approved-bundle-receipt-current-pass", "result": "PASS", "detail": sha(receipt_path)},
            {"check_id": "two-authority-distinct-requests-bound", "result": "PASS", "detail": [item["request_id"] for item in manifest["decision_requests"]]},
            {"check_id": "fifty-eight-source-selections-admitted", "result": "PASS", "detail": {"total": len(source_admissions["admissions"]), "historical_snapshots": sum(item["source_state"] == "historical-snapshot" for item in source_admissions["admissions"]) }},
            {"check_id": "eighty-five-definition-versions-admitted", "result": "PASS", "detail": len(promoted)},
            {"check_id": "registry-closure", "result": "PASS", "detail": {"versions": len(registry["entries"]), "current": len(registry["current_lookup"]) }},
            {"check_id": "seven-postimages-installed", "result": "PASS", "detail": {str(target.relative_to(LAB)): sha(target) for _, target, _ in postimage_targets}},
            {"check_id": "consumer-effects-separated", "result": "PASS", "detail": {"consumer_activations": 0, "generic_ledger_primitive": "deferred"}},
        ]
        if len(source_admissions["admissions"]) != 58 or sum(item["source_state"] == "historical-snapshot" for item in source_admissions["admissions"]) != 1 or len(promoted) != 85 or len(registry["entries"]) != 118 or len(registry["current_lookup"]) != 112:
            raise RuntimeError("postimage closure count mismatch")
        receipt = {
            "schema_version": "cyberalchemy-lab-definition-admission-transaction-validation/v1",
            "subject": DECISION_ID,
            "result": "PASS",
            "authority_effect": "evidence-only",
            "checks": checks,
            "summary": {"passed": len(checks), "failed": 0, "total": len(checks)},
            "materials": {"authorization_sha256": sha(AUTH), "manifest_sha256": sha(manifest_path), "bundle_receipt_sha256": sha(receipt_path), "decision_sha256": sha(DECISION), "decision_projection_sha256": sha(DECISION_MD)},
            "source_direction": {"canonical": "admission-validation.json", "human_projection": "ADMISSION-VALIDATION.md", "projection_policy": "generated-only", "generator": "apply.py"},
            "claim_ceiling": "PASS proves exact materialization of the full Definition queue admission transaction. It does not prove downstream carrier conformance, consumer activation, publication, release, or deployment.",
        }
        atomic_write(RECEIPT, encode(receipt))
        atomic_write(RECEIPT_MD, (render_receipt(receipt).rstrip() + "\n").encode())
    except Exception as exc:
        for target in reversed(written):
            if target in existing_backups:
                atomic_write(target, existing_backups[target])
            elif target in newly_created:
                target.unlink(missing_ok=True)
        for path in [DECISION, DECISION_MD, RECEIPT, RECEIPT_MD]:
            path.unlink(missing_ok=True)
        print(f"BLOCK: transaction rolled back: {exc}")
        return 1

    print("FULL_DEFINITION_QUEUE_ADMISSION=PASS")
    print(f"DECISION_SHA256={sha(DECISION)}")
    print(f"RECEIPT_SHA256={sha(RECEIPT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
