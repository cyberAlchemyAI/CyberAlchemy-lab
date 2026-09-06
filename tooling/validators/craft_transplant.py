#!/usr/bin/env python3
"""Independently verify the source-preserving Craft transplant."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[2]
SOURCE_REPOSITORY = Path("/home/vrondelli/projects/domainspec-core")
SOURCE_ROOT = Path("projects/domainspec-v2")
DESTINATION_ROOT = Path("craft")
PROPOSAL = Path("docs/proposals/0005-craft-transplant-architecture/proposal.json")
PROPOSAL_VIEW = PROPOSAL.with_name("PROPOSAL.md")
CHAIN = Path("docs/construction-chains/0003-craft-source-transplant-v1/chain.json")
CHAIN_VIEW = CHAIN.with_name("CHAIN.md")
MANIFEST = Path("evidence/migrations/domainspec-v2-to-craft/source-epoch.json")
MANIFEST_VIEW = Path("evidence/migrations/domainspec-v2-to-craft/SOURCE-EPOCH.md")
RECEIPT = Path("evidence/migrations/domainspec-v2-to-craft/receipts/validation.json")
RECEIPT_VIEW = RECEIPT.with_name("VALIDATION.md")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def selected_git_paths() -> list[str]:
    raw = subprocess.check_output(
        ["git", "ls-files", "--", SOURCE_ROOT.as_posix()],
        cwd=SOURCE_REPOSITORY,
        text=True,
    )
    prefix = f"{SOURCE_ROOT.as_posix()}/development/"
    return sorted(line for line in raw.splitlines() if line and not line.startswith(prefix))


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = [
        "<!-- Generated from validation.json by tooling/validators/craft_transplant.py. Do not edit. -->",
        "",
        "# Craft transplant validation",
        "",
        f"- Result: `{receipt['result']}`",
        f"- Files verified: `{receipt['summary']['files_verified']}`",
        f"- Bytes verified: `{receipt['summary']['bytes_verified']}`",
        f"- Source tree digest: `{receipt['summary']['selected_tree_sha256']}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{check['result']}` — {check['id']}: {check['detail']}" for check in receipt["checks"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            receipt["claim_ceiling"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    manifest = json.loads((LAB_ROOT / MANIFEST).read_text(encoding="utf-8"))
    proposal = json.loads((LAB_ROOT / PROPOSAL).read_text(encoding="utf-8"))
    chain = json.loads((LAB_ROOT / CHAIN).read_text(encoding="utf-8"))
    failures: list[str] = []
    checks: list[dict[str, str]] = []

    def check(identifier: str, condition: bool, detail: str) -> None:
        checks.append({"id": identifier, "result": "PASS" if condition else "FAIL", "detail": detail})
        if not condition:
            failures.append(identifier)

    selected_paths = selected_git_paths()
    manifest_source_paths = [entry["source_path"] for entry in manifest["entries"]]
    check("source-selection-exact", manifest_source_paths == selected_paths, f"manifest and Git selection contain {len(selected_paths)} ordered paths")

    entry_digests: list[dict[str, Any]] = []
    total_bytes = 0
    byte_match = True
    mode_match = True
    for entry in manifest["entries"]:
        source = SOURCE_REPOSITORY / entry["source_path"]
        destination = LAB_ROOT / entry["destination_path"]
        if not source.is_file() or not destination.is_file():
            byte_match = False
            mode_match = False
            continue
        source_digest = sha256_file(source)
        destination_digest = sha256_file(destination)
        byte_match = byte_match and source_digest == entry["sha256"] == destination_digest
        source_mode = stat.S_IMODE(source.stat().st_mode)
        destination_mode = stat.S_IMODE(destination.stat().st_mode)
        mode_match = mode_match and source_mode == int(entry["mode"], 8) == destination_mode
        total_bytes += destination.stat().st_size
        entry_digests.append(entry)
    check("copied-bytes-exact", byte_match, "every source, manifest, and destination SHA-256 matches")
    check("copied-modes-exact", mode_match, "every selected source and destination permission mode matches")

    expected_destinations = {entry["destination_path"] for entry in manifest["entries"]}
    actual_destinations = {
        path.relative_to(LAB_ROOT).as_posix()
        for path in (LAB_ROOT / DESTINATION_ROOT).rglob("*")
        if path.is_file()
    }
    check("destination-closure", actual_destinations == expected_destinations, f"destination contains exactly {len(actual_destinations)} selected files")
    check("development-excluded", not (LAB_ROOT / DESTINATION_ROOT / "development").exists(), "no development subtree was copied")

    aggregate = hashlib.sha256(canonical_json_bytes(entry_digests)).hexdigest()
    check("tree-digest-exact", aggregate == manifest["selected_tree_sha256"], "ordered entry manifest reproduces the selected tree digest")
    check("counts-exact", manifest["counts"]["selected_files"] == len(entry_digests) and manifest["counts"]["selected_bytes"] == total_bytes, "manifest counts equal reopened destination files")
    check("source-remains-read-only", manifest["source"]["access"] == "read-only" and proposal["copy_contract"]["source_mutation"] == "forbidden", "copy contract grants no source mutation")
    check("prototype-not-overwritten", not any(path.startswith("product/prototypes/") for path in expected_destinations), "P0-P2 paths are outside the transplant destination")
    check("authority-zero", manifest["authority_effect"] == "none" and proposal["authority_effect"] == "none", "copy and proposal claim no admission or activation")
    check("human-projections-present", (LAB_ROOT / PROPOSAL_VIEW).is_file() and (LAB_ROOT / CHAIN_VIEW).is_file() and (LAB_ROOT / MANIFEST_VIEW).is_file(), "proposal, construction chain, and source epoch have colocated generated human views")
    stages = {stage["stage_id"]: stage for stage in chain["stages"]}
    copy_stage = stages.get("CML10R-T0-COPY-SOURCE-WORKSPACE", {})
    check("construction-chain-bound", chain.get("architecture_ref") == PROPOSAL.as_posix() and copy_stage.get("evidence_ref") == RECEIPT.as_posix(), "successor chain binds the transplant architecture and validation receipt")
    check("next-frontier-runnable", chain["work_plan"]["product_construction_frontier"] == "CML10R-T1-INVENTORY-ACTIVE-NAME-AND-PATH-BINDINGS" and stages["CML10R-T1-INVENTORY-ACTIVE-NAME-AND-PATH-BINDINGS"]["state"] == "runnable", "the next product-construction frontier is the read-only rebinding inventory")

    result = "PASS" if not failures else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-craft-transplant-validation/v1",
        "result": result,
        "authority_effect": "none",
        "source_direction": {
            "canonical": RECEIPT.as_posix(),
            "human_projection": RECEIPT_VIEW.as_posix(),
            "projection_policy": "generated-only",
            "generator": "tooling/validators/craft_transplant.py",
        },
        "architecture_ref": PROPOSAL.as_posix(),
        "manifest_ref": MANIFEST.as_posix(),
        "summary": {
            "files_verified": len(entry_digests),
            "bytes_verified": total_bytes,
            "selected_tree_sha256": aggregate,
            "checks_passed": sum(1 for item in checks if item["result"] == "PASS"),
            "checks_total": len(checks),
        },
        "checks": checks,
        "failures": failures,
        "claim_ceiling": "PASS proves only that the selected tracked DomainSpec v2 files were copied under craft/ with exact bytes, modes, inventory closure, and zero claimed authority. It does not prove active-name rebinding, runtime conformance, product approval, admission, release, or deployment.",
    }
    receipt_bytes = canonical_json_bytes(receipt)
    receipt_path = LAB_ROOT / RECEIPT
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    if not receipt_path.exists() or receipt_path.read_bytes() != receipt_bytes:
        receipt_path.write_bytes(receipt_bytes)
    view_bytes = render_receipt(receipt).encode("utf-8")
    view_path = LAB_ROOT / RECEIPT_VIEW
    if not view_path.exists() or view_path.read_bytes() != view_bytes:
        view_path.write_bytes(view_bytes)
    print(receipt_bytes.decode(), end="")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
