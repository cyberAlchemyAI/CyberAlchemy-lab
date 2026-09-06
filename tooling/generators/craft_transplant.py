#!/usr/bin/env python3
"""Copy the tracked DomainSpec v2 product workspace into Craft byte-for-byte."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_REPOSITORY = Path("/home/vrondelli/projects/domainspec-core")
SOURCE_ROOT = Path("projects/domainspec-v2")
DESTINATION_ROOT = Path("craft")
PROPOSAL_PATH = Path("docs/proposals/0005-craft-transplant-architecture/proposal.json")
PROPOSAL_VIEW_PATH = PROPOSAL_PATH.with_name("PROPOSAL.md")
CHAIN_PATH = Path("docs/construction-chains/0003-craft-source-transplant-v1/chain.json")
CHAIN_VIEW_PATH = CHAIN_PATH.with_name("CHAIN.md")
EVIDENCE_ROOT = Path("evidence/migrations/domainspec-v2-to-craft")
MANIFEST_PATH = EVIDENCE_ROOT / "source-epoch.json"
MANIFEST_VIEW_PATH = EVIDENCE_ROOT / "SOURCE-EPOCH.md"


def run_git(repository: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repository, text=True, stderr=subprocess.STDOUT
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_if_changed(path: Path, data: bytes) -> None:
    if path.exists() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def selected_source_paths(source_repository: Path) -> list[Path]:
    raw = run_git(source_repository, "ls-files", "--", SOURCE_ROOT.as_posix())
    selected = []
    development_prefix = f"{SOURCE_ROOT.as_posix()}/development/"
    for line in raw.splitlines():
        if not line or line.startswith(development_prefix):
            continue
        selected.append(Path(line))
    return sorted(selected, key=lambda item: item.as_posix())


def tracked_development_count(source_repository: Path) -> int:
    raw = run_git(source_repository, "ls-files", "--", SOURCE_ROOT.as_posix())
    prefix = f"{SOURCE_ROOT.as_posix()}/development/"
    return sum(1 for line in raw.splitlines() if line.startswith(prefix))


def untracked_paths(source_repository: Path) -> list[str]:
    raw = run_git(
        source_repository,
        "ls-files",
        "--others",
        "--exclude-standard",
        "--",
        SOURCE_ROOT.as_posix(),
    )
    return sorted(line for line in raw.splitlines() if line)


def ignored_count(source_repository: Path) -> int:
    raw = run_git(
        source_repository,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "--",
        SOURCE_ROOT.as_posix(),
    )
    return sum(1 for line in raw.splitlines() if line)


def source_entry(source_repository: Path, source_path: Path) -> dict[str, Any]:
    absolute = source_repository / source_path
    if absolute.is_symlink():
        raise RuntimeError(f"symlink is outside the transplant contract: {source_path}")
    if not absolute.is_file():
        raise RuntimeError(f"selected source is not a regular file: {source_path}")
    relative = source_path.relative_to(SOURCE_ROOT)
    destination = DESTINATION_ROOT / relative
    mode = stat.S_IMODE(absolute.stat().st_mode)
    return {
        "source_path": source_path.as_posix(),
        "destination_path": destination.as_posix(),
        "sha256": sha256_file(absolute),
        "size": absolute.stat().st_size,
        "mode": f"{mode:04o}",
        "classification": "source-preserving-candidate-copy",
    }


def copy_entries(
    source_repository: Path, destination_repository: Path, entries: list[dict[str, Any]]
) -> None:
    for entry in entries:
        source = source_repository / entry["source_path"]
        destination = destination_repository / entry["destination_path"]
        if destination.exists():
            if not destination.is_file():
                raise RuntimeError(f"destination collision is not a file: {destination}")
            if sha256_file(destination) != entry["sha256"]:
                raise RuntimeError(f"destination collision has different bytes: {destination}")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        os.chmod(destination, int(entry["mode"], 8))


def render_proposal(proposal: dict[str, Any]) -> str:
    architecture = proposal["architecture"]
    contract = proposal["copy_contract"]
    lines = [
        "<!-- Generated from proposal.json by tooling/generators/craft_transplant.py. Do not edit. -->",
        "",
        f"# {proposal['title']}",
        "",
        f"- Proposal: `{proposal['proposal_id']}`",
        f"- Status: `{proposal['status']}`",
        f"- Decision posture: `{proposal['decision_posture']}`",
        f"- Authority effect: `{proposal['authority_effect']}`",
        "",
        "## Objective",
        "",
        proposal["objective"],
        "",
        "## Architecture",
        "",
    ]
    for plane in architecture["lab_planes"]:
        lines.append(
            f"- `{plane['path']}` — {plane['role']}. {plane['boundary']}"
        )
    lines.extend(["", "### Craft workspace", ""])
    for path in architecture["workspace_layout"]:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            f"**Identity.** {architecture['identity_rule']}",
            "",
            f"**Cohesion.** {architecture['cohesion_rule']}",
            "",
            f"**Contexts.** {architecture['context_rule']}",
            "",
            "## Copy contract",
            "",
            f"- Source: `{contract['source_repository']}/{contract['source_root']}`",
            f"- Destination: `{contract['destination_repository']}/{contract['destination_root']}`",
            f"- Selection: {contract['selection']}",
            f"- Mapping: {contract['path_mapping']}",
            f"- Bytes: {contract['byte_policy']}",
            f"- Modes: {contract['mode_policy']}",
            f"- Collisions: {contract['collision_policy']}",
            "",
            "Excluded:",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in contract["excluded"])
    effect = proposal["construction_effect"]
    lines.extend(
        [
            "",
            "## Construction effect",
            "",
            f"- Current frontier: {effect['current_frontier']}",
            f"- Superseded strategy: {effect['supersedes_strategy']}",
            f"- Preserved evidence: {effect['preserves']}",
            f"- Next frontier: {effect['next_frontier']}",
            "",
            "## Rollback",
            "",
            f"- Before admission: {proposal['rollback']['before_admission']}",
            f"- Source effect: `{proposal['rollback']['source_repository_effect']}`",
            f"- Legacy v1 effect: `{proposal['rollback']['legacy_v1_effect']}`",
            "",
            "## Claim ceiling",
            "",
            proposal["claim_ceiling"],
            "",
        ]
    )
    return "\n".join(lines)


def render_manifest(manifest: dict[str, Any]) -> str:
    counts = manifest["counts"]
    lines = [
        "<!-- Generated from source-epoch.json by tooling/generators/craft_transplant.py. Do not edit. -->",
        "",
        "# DomainSpec v2 to Craft source epoch",
        "",
        f"- Epoch: `{manifest['source_epoch_id']}`",
        f"- Status: `{manifest['status']}`",
        f"- Source commit: `{manifest['source']['git_head']}`",
        f"- Selected files: `{counts['selected_files']}`",
        f"- Selected bytes: `{counts['selected_bytes']}`",
        f"- Aggregate digest: `{manifest['selected_tree_sha256']}`",
        f"- Tracked development files excluded: `{counts['tracked_development_excluded']}`",
        f"- Untracked files excluded: `{counts['untracked_excluded']}`",
        f"- Ignored files excluded: `{counts['ignored_excluded']}`",
        "",
        "## Copy boundary",
        "",
        "The exact version-controlled DomainSpec v2 product tree outside `development/` is copied beneath `craft/` with relative paths, bytes, and file modes preserved. The copy is a candidate source transplant, not an admission or activation.",
        "",
        "## Untracked non-development exclusions",
        "",
    ]
    nondevelopment = manifest["exclusions"]["untracked_non_development"]
    if nondevelopment:
        lines.extend(f"- `{item['path']}` (`sha256:{item['sha256']}`)" for item in nondevelopment)
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Verification",
            "",
            "Every entry in the canonical manifest records source path, destination path, SHA-256, byte size, mode, and candidate classification. Use `tooling/validators/craft_transplant.py` to independently re-open the source and destination bytes.",
            "",
            "## Claim ceiling",
            "",
            manifest["claim_ceiling"],
            "",
        ]
    )
    return "\n".join(lines)


def render_chain(chain: dict[str, Any]) -> str:
    lines = [
        "<!-- Generated from chain.json by tooling/generators/craft_transplant.py. Do not edit. -->",
        "",
        f"# {chain['title']}",
        "",
        f"- Chain: `{chain['chain_id']}`",
        f"- Status: `{chain['status']}`",
        f"- Authority effect: `{chain['authority_effect']}`",
        f"- Current frontier: `{chain['work_plan']['product_construction_frontier']}`",
        "",
        "## Objective",
        "",
        chain["objective"],
        "",
        "## Construction rule",
        "",
        chain["construction_rule"],
        "",
        "## Stages",
        "",
    ]
    for index, stage in enumerate(chain["stages"], start=1):
        dependencies = ", ".join(stage["depends_on"]) or "none"
        lines.extend(
            [
                f"### {index}. `{stage['stage_id']}`",
                "",
                f"- Lane: `{stage['lane']}`",
                f"- State: `{stage['state']}`",
                f"- Depends on: {dependencies}",
                f"- Objective: {stage['objective']}",
                f"- Exit evidence: {stage['exit_evidence']}",
                f"- Authority effect: `{stage['authority_effect']}`",
                "",
            ]
        )
    boundary = chain["approval_boundary"]
    lines.extend(
        [
            "## Approval boundary",
            "",
            f"- Mode: `{boundary['mode']}`",
            f"- Workflow: `{boundary['configured_for_workflow']}`",
            f"- Eligible after: `{boundary['eligible_after_stage']}`",
            f"- Decision stage: `{boundary['decision_stage']}`",
            f"- Approved effect: `{boundary['effect_if_approved']}`",
            f"- Operational authority: `{boundary['operational_authority']}`",
            "",
            "## Work plan",
            "",
            f"- Product-construction frontier: `{chain['work_plan']['product_construction_frontier']}`",
            f"- Causal construction blockers: `{len(chain['work_plan']['causal_construction_blockers'])}`",
            "- Operational support remains separately owned and cannot hide runnable product work.",
            "",
            "## Claim ceiling",
            "",
            chain["claim_ceiling"],
            "",
        ]
    )
    return "\n".join(lines)


def build_manifest(source_repository: Path) -> dict[str, Any]:
    paths = selected_source_paths(source_repository)
    entries = [source_entry(source_repository, path) for path in paths]
    untracked = untracked_paths(source_repository)
    development_prefix = f"{SOURCE_ROOT.as_posix()}/development/"
    untracked_non_development = []
    for path_text in untracked:
        if path_text.startswith(development_prefix):
            continue
        path = Path(path_text)
        absolute = source_repository / path
        untracked_non_development.append(
            {
                "path": path_text,
                "sha256": sha256_file(absolute),
                "size": absolute.stat().st_size,
                "reason": "untracked-source-byte-outside-selected-version-controlled-closure",
            }
        )
    selected_tree_sha256 = sha256_bytes(canonical_json_bytes(entries))
    git_head = run_git(source_repository, "rev-parse", "HEAD").strip()
    return {
        "schema_version": "cyberalchemy-lab-craft-transplant-source-epoch/v1",
        "source_epoch_id": f"CAL-CRAFT-TRANSPLANT-{git_head[:12]}-{selected_tree_sha256[:12]}",
        "status": "candidate-source-transplant",
        "authority_effect": "none",
        "source_direction": {
            "canonical": MANIFEST_PATH.as_posix(),
            "human_projection": MANIFEST_VIEW_PATH.as_posix(),
            "projection_policy": "generated-only",
            "generator": "tooling/generators/craft_transplant.py",
        },
        "architecture_ref": PROPOSAL_PATH.as_posix(),
        "source": {
            "repository": str(source_repository),
            "root": SOURCE_ROOT.as_posix(),
            "git_head": git_head,
            "access": "read-only",
        },
        "destination": {
            "repository": str(LAB_ROOT),
            "root": DESTINATION_ROOT.as_posix(),
            "posture": "candidate-not-admitted-not-active",
        },
        "selection": {
            "rule": "git-tracked-and-not-development",
            "include": [f"{SOURCE_ROOT.as_posix()}/**"],
            "exclude": [
                f"{SOURCE_ROOT.as_posix()}/development/**",
                "all-untracked-files",
                "all-ignored-files",
            ],
            "mapping": f"{SOURCE_ROOT.as_posix()}/<relative> -> {DESTINATION_ROOT.as_posix()}/<relative>",
        },
        "counts": {
            "selected_files": len(entries),
            "selected_bytes": sum(entry["size"] for entry in entries),
            "tracked_development_excluded": tracked_development_count(source_repository),
            "untracked_excluded": len(untracked),
            "ignored_excluded": ignored_count(source_repository),
        },
        "selected_tree_sha256": selected_tree_sha256,
        "entries": entries,
        "exclusions": {
            "untracked_non_development": untracked_non_development,
            "development": "excluded-whole-subtree",
            "frozen_v1": "implementation/domainspec remains external evidence and is not copied",
            "p0_p2": "existing CyberAlchemy-lab prototype evidence remains unchanged",
        },
        "rollback": {
            "source_effect": "none",
            "destination_scope": [
                DESTINATION_ROOT.as_posix(),
                EVIDENCE_ROOT.as_posix(),
                PROPOSAL_PATH.parent.as_posix(),
                CHAIN_PATH.parent.as_posix(),
                "tooling/generators/craft_transplant.py",
                "tooling/validators/craft_transplant.py",
            ],
            "destructive_action_authorized": False,
        },
        "claim_ceiling": "This manifest proves only an exact candidate copy of the selected source bytes. It does not rename internal DomainSpec strings, rebind paths, admit meaning, activate a runtime, approve a Product, or authorize publication, release, or deployment.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-repository", type=Path, default=DEFAULT_SOURCE_REPOSITORY)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source_repository = args.source_repository.resolve()
    proposal = json.loads((LAB_ROOT / PROPOSAL_PATH).read_text(encoding="utf-8"))
    chain = json.loads((LAB_ROOT / CHAIN_PATH).read_text(encoding="utf-8"))
    manifest = build_manifest(source_repository)

    if not args.apply:
        print(canonical_json_bytes({"result": "dry-run", "counts": manifest["counts"]}).decode(), end="")
        return 0

    copy_entries(source_repository, LAB_ROOT, manifest["entries"])
    write_if_changed(LAB_ROOT / PROPOSAL_VIEW_PATH, render_proposal(proposal).encode("utf-8"))
    write_if_changed(LAB_ROOT / CHAIN_VIEW_PATH, render_chain(chain).encode("utf-8"))
    write_if_changed(LAB_ROOT / MANIFEST_PATH, canonical_json_bytes(manifest))
    write_if_changed(LAB_ROOT / MANIFEST_VIEW_PATH, render_manifest(manifest).encode("utf-8"))
    print(canonical_json_bytes({"result": "PASS", "source_epoch_id": manifest["source_epoch_id"], "counts": manifest["counts"]}).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
