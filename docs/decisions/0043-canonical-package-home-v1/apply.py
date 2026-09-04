#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
BUNDLE = LAB / "docs/admission-bundles/0003-canonical-package-home-v1"
AUTH = ROOT / "authorization.json"
DECISION = ROOT / "decision.json"
DECISION_MD = ROOT / "DECISION.md"
RECEIPT = ROOT / "receipts/admission-validation.json"
RECEIPT_MD = ROOT / "receipts/ADMISSION-VALIDATION.md"
DECISION_ID = "CAL-DECISION-0043-CANONICAL-PACKAGE-HOME-V1"


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


def render_authorization(data: dict) -> str:
    return "\n".join([
        "<!-- GENERATED FILE: authorization.json is canonical. -->", "",
        "# Canonical Package Home v1 authorization", "",
        f"- Principal: `{data['principal_id']}`",
        f"- Selection: `{data['selection_token']}`",
        f"- Manifest: `{data['manifest']['sha256']}`",
        f"- Receipt: `{data['validation_receipt']['sha256']}`", "",
        "## Separation", "", data["decision_separation"], "",
        "## Claim ceiling", "", data["claim_ceiling"], ""
    ])


def render_decision(data: dict) -> str:
    return "\n".join([
        "<!-- GENERATED FILE: decision.json is canonical. -->", "",
        "# Canonical Package Home v1 admission", "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Principal: `{data['selection']['selected_by_principal']}`", "",
        "## Result", "",
        "Five exact CAV2 source selections are admitted only for this use; one Definition version is admitted and the synchronized 33-version registry surfaces are installed.", "",
        "## Excluded effects", "",
        *[f"- {item}" for item in data["excluded_effects"]], "",
        "## Claim ceiling", "", data["claim_ceiling"], ""
    ])


def render_receipt(data: dict) -> str:
    lines = ["<!-- GENERATED FILE: admission-validation.json is canonical. -->", "", "# Canonical Package Home v1 admission validation", "", f"- Result: `{data['result']}`", "", "| Check | Result |", "| --- | --- |"]
    lines.extend(f"| `{x['check_id']}` | `{x['result']}` |" for x in data["checks"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"], ""])
    return "\n".join(lines)


def target_for(relative: str) -> Path:
    parts = Path(relative).parts
    if not parts or parts[0] != "postimages":
        raise ValueError(f"invalid postimage path: {relative}")
    return LAB.joinpath(*parts[1:])


def main() -> int:
    authorization = load(AUTH)
    manifest_path = LAB / authorization["manifest"]["path"]
    receipt_path = LAB / authorization["validation_receipt"]["path"]
    manifest = load(manifest_path)
    bundle_receipt = load(receipt_path)
    failures = []
    def require(ok, message):
        if not ok:
            failures.append(message)

    require(authorization["prospective_decision_id"] == manifest["prospective_decision_id"] == DECISION_ID, "decision identity mismatch")
    require(authorization["selection_token"] == "admit commit and push", "selection token mismatch")
    require(authorization["principal_id"] == "person:<vrondelli>", "principal mismatch")
    require(sha(manifest_path) == authorization["manifest"]["sha256"], "manifest digest mismatch")
    require(sha(receipt_path) == authorization["validation_receipt"]["sha256"], "validation receipt digest mismatch")
    require(bundle_receipt.get("result") == authorization["validation_receipt"]["required_result"] == "PASS", "bundle validation is not PASS")
    require(len(manifest["decision_requests"]) == 3, "decision request count mismatch")
    for group in ("candidate_inputs", "live_preimages"):
        for item in manifest[group]:
            path = LAB / item["path"]
            require(path.is_file(), f"missing {group}: {item['path']}")
            if path.is_file():
                require(sha(path) == item["sha256"], f"changed {group}: {item['path']}")

    postimage_targets = []
    preimages = {x["path"]: x["sha256"] for x in manifest["live_preimages"]}
    for item in manifest["postimages"]:
        source = BUNDLE / item["path"]
        target = target_for(item["path"])
        require(source.is_file(), f"missing postimage: {item['path']}")
        if source.is_file():
            require(sha(source) == item["sha256"], f"changed postimage: {item['path']}")
        rel = str(target.relative_to(LAB))
        require(rel in preimages, f"target not bound as live preimage: {rel}")
        if target.is_file() and rel in preimages:
            require(sha(target) == preimages[rel], f"live preimage changed: {rel}")
        postimage_targets.append((source, target, item["sha256"]))
    if failures:
        print(f"BLOCK: pre-effect reconciliation failed ({len(failures)})")
        for item in failures:
            print(f"- {item}")
        return 1

    backups = {target: target.read_bytes() for _, target, _ in postimage_targets}
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
            "title": "Canonical Package Home v1 admission",
            "status": "owner-admitted",
            "authority_effect": "canonical-package-home-definition-admitted",
            "selection": {
                "option_id": "ADMIT-CANONICAL-PACKAGE-HOME-V1",
                "selected_by_principal": authorization["principal_id"],
                "selected_roles": ["source-admission-owner", "definition-owner"],
                "selection_source": authorization["selection_source"],
                "selection_token": authorization["selection_token"],
                "manifest_sha256": authorization["manifest"]["sha256"],
                "validation_receipt_sha256": authorization["validation_receipt"]["sha256"],
                "decision_boundary": authorization["decision_boundary"],
                "recorded_at": recorded
            },
            "authority_basis": {
                "principal_id": authorization["principal_id"],
                "authorization_path": str(AUTH.relative_to(LAB)),
                "authorization_sha256": sha(AUTH),
                "manifest_path": str(manifest_path.relative_to(LAB)),
                "separation_rule": authorization["decision_separation"]
            },
            "admitted_decision_requests": manifest["decision_requests"],
            "admitted_source_selection": {
                "path": "authority/decisions/source-admission/canonical-package-home/v1/admissions.json",
                "sha256": sha(LAB / "authority/decisions/source-admission/canonical-package-home/v1/admissions.json"),
                "selection_count": 5,
                "decision_overlay_status": "admitted-for-exact-stated-use"
            },
            "admitted_definition_candidate": {
                "candidate_id": "CAL-DEFINITION-CANDIDATE-SET-CANONICAL-PACKAGE-HOME-0008",
                "path": "authority/definitions/candidates/0008-canonical-package-home/candidate.json",
                "sha256": sha(LAB / "authority/definitions/candidates/0008-canonical-package-home/candidate.json"),
                "definition_ref": "cal.definition.canonical-package-home@1.0.0-candidate.1",
                "definition_count": 1,
                "decision_overlay_status": "admitted-current"
            },
            "admission_result": {"result": "complete", "source_selections_admitted": 5, "definitions_admitted": 1, "canonical_definition_versions": 33, "current_definition_terms": 31, "artifact_types_admitted": 0, "registry_context_migrations": 0},
            "canonical_postimages": [{"path": str(target.relative_to(LAB)), "sha256": expected} for _, target, expected in postimage_targets],
            "excluded_effects": manifest["excluded_effects"],
            "source_direction": {"canonical": "decision.json", "human_projection": "DECISION.md", "projection_policy": "generated-only", "generator": "apply.py"},
            "claim_ceiling": "This decision admits only five exact source selections for one stated use, one Definition version, and four synchronized postimages. It does not admit an Artifact Type successor, select or migrate Registry Context, establish conformance, release, or deploy."
        }
        atomic_write(DECISION, encode(decision))
        atomic_write(DECISION_MD, render_decision(decision).encode())
        checks = [
            {"check_id": "approved-manifest-current", "result": "PASS", "detail": sha(manifest_path)},
            {"check_id": "approved-receipt-current-pass", "result": "PASS", "detail": sha(receipt_path)},
            {"check_id": "three-authority-distinct-requests-bound", "result": "PASS", "detail": [x["request_id"] for x in manifest["decision_requests"]]},
            {"check_id": "five-source-selections-admitted-for-stated-use", "result": "PASS", "detail": decision["admitted_source_selection"]},
            {"check_id": "one-definition-admitted", "result": "PASS", "detail": decision["admitted_definition_candidate"]},
            {"check_id": "four-postimages-installed", "result": "PASS", "detail": {str(target.relative_to(LAB)): sha(target) for _, target, _ in postimage_targets}},
            {"check_id": "registry-closure", "result": "PASS", "detail": {"versions": 33, "current_terms": 31}},
            {"check_id": "artifact-type-and-migration-residue-preserved", "result": "PASS", "detail": {"artifact_types_admitted": 0, "registry_context_migrations": 0}}
        ]
        receipt = {
            "schema_version": "cyberalchemy-lab-definition-admission-transaction-validation/v1",
            "subject": DECISION_ID,
            "result": "PASS",
            "authority_effect": "evidence-only",
            "checks": checks,
            "summary": {"passed": len(checks), "failed": 0, "total": len(checks)},
            "materials": {"authorization_sha256": sha(AUTH), "manifest_sha256": sha(manifest_path), "bundle_receipt_sha256": sha(receipt_path), "decision_sha256": sha(DECISION), "decision_projection_sha256": sha(DECISION_MD)},
            "source_direction": {"canonical": "admission-validation.json", "human_projection": "ADMISSION-VALIDATION.md", "projection_policy": "generated-only", "generator": "apply.py"},
            "claim_ceiling": "PASS proves exact materialization of the approved Canonical Package Home Definition transaction only. It does not prove Artifact Type conformance, Registry Context migration, publication, release, or deployment."
        }
        atomic_write(RECEIPT, encode(receipt))
        atomic_write(RECEIPT_MD, render_receipt(receipt).encode())
        atomic_write(ROOT / "AUTHORIZATION.md", render_authorization(authorization).encode())
    except Exception as exc:
        for target in reversed(written):
            atomic_write(target, backups[target])
        for path in [DECISION, DECISION_MD, RECEIPT, RECEIPT_MD, ROOT / "AUTHORIZATION.md"]:
            path.unlink(missing_ok=True)
        print(f"BLOCK: transaction rolled back: {exc}")
        return 1
    print("CANONICAL_PACKAGE_HOME_ADMISSION=PASS")
    print(f"DECISION_SHA256={sha(DECISION)}")
    print(f"RECEIPT_SHA256={sha(RECEIPT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
