#!/usr/bin/env python3
"""Build the read-only DomainSpec v2 development migration inventory.

The source repository is never modified. The machine JSON is canonical; both
Markdown files are deterministic projections of machine data.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
import shutil
import subprocess
from typing import Any, Iterable

import yaml


SOURCE_REPO = Path("/home/vrondelli/projects/domainspec-core")
SOURCE_PROJECT_REL = Path("projects/domainspec-v2")
SOURCE_PROJECT = SOURCE_REPO / SOURCE_PROJECT_REL
SOURCE_DEVELOPMENT = SOURCE_PROJECT / "development"
LAB_ROOT = Path("/home/vrondelli/projects/CyberAlchemy-lab")
CRAFT_ROOT = LAB_ROOT / "craft"
OUTPUT_ROOT = LAB_ROOT / "evidence/migrations/domainspec-v2-to-craft/development-inventory"
RECEIPTS_ROOT = OUTPUT_ROOT / "receipts"
COPY_MANIFEST = LAB_ROOT / "evidence/migrations/domainspec-v2-to-craft/source-epoch.json"
LEDGER = SOURCE_PROJECT / ".craft/ledger.yml"
BASELINE = SOURCE_DEVELOPMENT / "meta-type-instantiation-cli/CANONICAL-IMPLEMENTED-BASELINE.v2.json"

SCHEMA_VERSION = "cyberalchemy-lab-development-migration-inventory/v1"
INVENTORY_ID = "CAL-CRAFT-DEVELOPMENT-INVENTORY-01"

GENERATED_PATH_PARTS = {
    ".cache",
    ".lake",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
GENERATED_SUFFIXES = {
    ".a", ".bin", ".class", ".dll", ".dylib", ".exe", ".hi", ".jar",
    ".o", ".olean", ".pyc", ".so", ".timestamp",
}
CODE_OR_FORMALIZATION_SUFFIXES = {
    ".c", ".cc", ".cjs", ".cpp", ".cs", ".css", ".go", ".h", ".hpp",
    ".html", ".java", ".js", ".json", ".jsx", ".lean", ".md", ".mjs",
    ".py", ".rb", ".rs", ".scala", ".sh", ".sql", ".toml", ".ts",
    ".tsx", ".xml", ".yaml", ".yml",
}
CONTROL_BUNDLE_RELATIVE = (
    "development/meta-type-instantiation-cli/CANONICAL-IMPLEMENTED-BASELINE.v2.json",
    "development/meta-type-instantiation-cli/OWNER-CANONICAL-DOCS-AND-BASELINE-V2-DECISION.json",
    "development/meta-type-instantiation-cli/validate-baseline.mjs",
    "development/implementation-conformance/ontology-experiment/ontology.json",
    "development/implementation-conformance/ontology-experiment/domain-meta-types.projection.json",
    "development/implementation-conformance/ontology-experiment/materialize-current-meta-type-state.mjs",
)
OPERATIONAL_SUPPORT_DIRS = {
    "operational-resilience-observability-deployment-integration",
}


def run_git(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args], cwd=SOURCE_REPO, check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def pretty_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_relative(repo_relative: str) -> str | None:
    prefix = SOURCE_PROJECT_REL.as_posix() + "/"
    if not repo_relative.startswith(prefix):
        return None
    return repo_relative[len(prefix):]


def development_directory(project_path: str) -> str | None:
    if not project_path.startswith("development/"):
        return None
    rest = project_path[len("development/"):]
    return rest.split("/", 1)[0] if rest else None


def is_generated_residue(project_path: str) -> bool:
    p = Path(project_path)
    return bool(GENERATED_PATH_PARTS.intersection(p.parts)) or p.suffix.lower() in GENERATED_SUFFIXES


def is_code_or_formalization(project_path: str) -> bool:
    return Path(project_path).suffix.lower() in CODE_OR_FORMALIZATION_SUFFIXES and not is_generated_residue(project_path)


def normalize_ledger_development_path(raw: str) -> str | None:
    path = raw.replace("\\", "/")
    project_prefix = "[repo-root]/projects/domainspec-v2/"
    if path.startswith(project_prefix):
        path = path[len(project_prefix):]
    source_prefix = "projects/domainspec-v2/"
    if path.startswith(source_prefix):
        path = path[len(source_prefix):]
    if path.startswith("[repo-root]/cyberAlchemy-v2/") or path.startswith("cyberAlchemy-v2/"):
        return None
    return path if path.startswith("development/") else None


def aggregate_entries(paths: Iterable[str], include_hash: bool) -> tuple[list[dict[str, Any]], str]:
    entries: list[dict[str, Any]] = []
    for repo_path in sorted(paths):
        path = SOURCE_REPO / repo_path
        if not path.is_file():
            continue
        stat = path.stat()
        entry: dict[str, Any] = {"path": repo_path, "size": stat.st_size}
        if include_hash:
            entry["sha256"] = sha256_file(path)
        entries.append(entry)
    digest = sha256_bytes(canonical_bytes(entries))
    return entries, digest


def craft_tree_digest() -> str:
    entries: list[dict[str, Any]] = []
    for path in sorted(p for p in CRAFT_ROOT.rglob("*") if p.is_file() and not p.is_symlink()):
        entries.append({
            "path": path.relative_to(CRAFT_ROOT).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return sha256_bytes(canonical_bytes(entries))


def source_epoch() -> dict[str, Any]:
    tracked = run_git("ls-files", "--", SOURCE_DEVELOPMENT.relative_to(SOURCE_REPO).as_posix())
    untracked = run_git(
        "ls-files", "--others", "--exclude-standard", "--",
        SOURCE_DEVELOPMENT.relative_to(SOURCE_REPO).as_posix(),
    )
    source_like_untracked = [
        p for p in untracked
        if (rel := project_relative(p)) is not None and not is_generated_residue(rel)
    ]
    _, tracked_digest = aggregate_entries(tracked, include_hash=True)
    _, source_like_untracked_digest = aggregate_entries(source_like_untracked, include_hash=True)
    return {
        "tracked_count": len(tracked),
        "untracked_nonignored_count": len(untracked),
        "source_like_untracked_count": len(source_like_untracked),
        "tracked_tree_sha256": tracked_digest,
        "source_like_untracked_tree_sha256": source_like_untracked_digest,
        "status_porcelain": run_git("status", "--porcelain=v1", "--", SOURCE_DEVELOPMENT.relative_to(SOURCE_REPO).as_posix()),
    }


def path_entry(project_path: str) -> dict[str, Any]:
    source_path = SOURCE_PROJECT / project_path
    entry: dict[str, Any] = {
        "source_path": f"projects/domainspec-v2/{project_path}",
        "destination_path": f"craft/{project_path}",
        "exists_in_source": source_path.is_file(),
        "exists_in_craft": (CRAFT_ROOT / project_path).is_file(),
    }
    if source_path.is_file():
        entry["size"] = source_path.stat().st_size
        entry["sha256"] = sha256_file(source_path)
    return entry


def load_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        yaml.safe_load(LEDGER.read_text()),
        json.loads(BASELINE.read_text()),
        json.loads(COPY_MANIFEST.read_text()),
    )


def find_stable_referrers(directory_names: list[str], stable_paths: list[str]) -> dict[str, list[str]]:
    refs: dict[str, set[str]] = {name: set() for name in directory_names}
    needles = {
        name: (
            f"projects/domainspec-v2/development/{name}",
            f"development/{name}",
        )
        for name in directory_names
    }
    for repo_path in stable_paths:
        path = SOURCE_REPO / repo_path
        try:
            if path.stat().st_size > 8 * 1024 * 1024:
                continue
            text = path.read_text(errors="strict")
        except (OSError, UnicodeError):
            continue
        for name, (absolute_needle, relative_needle) in needles.items():
            if absolute_needle in text:
                refs[name].add(repo_path)
                continue
            offset = text.find(relative_needle)
            while offset >= 0:
                prefix = text[max(0, offset - 24):offset]
                if "cyberAlchemy-v2/" not in prefix:
                    refs[name].add(repo_path)
                    break
                offset = text.find(relative_needle, offset + 1)
    return {name: sorted(paths) for name, paths in refs.items()}


def render_inventory(data: dict[str, Any]) -> str:
    summary = data["summary"]
    baseline = data["baseline_closure"]
    lines = [
        "# DomainSpec v2 development migration inventory",
        "",
        "> Generated from `inventory.json`. The JSON is canonical; this file is a human projection.",
        "",
        "## Result",
        "",
        "Important development material was not moved, but copying the whole development tree would mix admitted baseline dependencies, active writer-owned work, historical evidence, and generated residue.",
        "",
        f"- Development directories: **{summary['development_directories']}**",
        f"- Git-tracked files: **{summary['tracked_files']}**",
        f"- Untracked nonignored files: **{summary['untracked_nonignored_files']}**",
        f"- Ignored files: **{summary['ignored_files']}**",
        f"- Ledger artifacts under development: **{summary['ledger_development_artifacts']}**",
        f"- Frozen baseline inventory: **{baseline['inventory_files']} files; {baseline['present_current_source_bytes_in_craft']} current source paths present, {baseline['missing_paths_from_craft']} paths missing**",
        f"- Exact baseline state: **{baseline['exact_baseline_bytes_in_craft']} exact, {baseline['source_drifted_members']} current source members drifted from the admitted hashes**",
        "",
        "## Confirmed gaps",
        "",
    ]
    for finding in data["findings"]:
        lines.append(f"- **{finding['finding_id']}** — {finding['statement']}")
    lines.extend([
        "",
        "## Baseline bridge inputs",
        "",
        "These records are required to preserve and explain the old baseline epoch. Because 24 source members have drifted, they must not be rebound as the current baseline without a successor-baseline decision.",
        "",
    ])
    for entry in baseline["required_control_bundle"]:
        state = "already present" if entry["exists_in_craft"] else "missing"
        lines.append(f"- `{entry['source_path']}` — {state}")
    lines.extend(["", "Missing frozen inventory members:", ""])
    for entry in baseline["missing_inventory_members"]:
        lines.append(f"- `{entry['source_path']}`")
    validator = data["external_validation"]["baseline_validator"]
    lines.extend([
        "",
        "Baseline validator execution:",
        "",
        f"- **{validator['status']}** — {validator['detail']}",
    ])
    lines.extend([
        "",
        "## Directory classification",
        "",
        "| Directory | Tracked | Untracked | Ignored | Ledger | Stable refs | Baseline | Lane | Tier | Recommendation |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ])
    for row in data["directories"]:
        lines.append(
            f"| `{row['directory']}` | {row['counts']['tracked']} | {row['counts']['untracked_nonignored']} | "
            f"{row['counts']['ignored']} | {len(row['ledger_artifacts'])} | {row['stable_referrers']['count']} | "
            f"{len(row['baseline_inventory_members'])} | {row['work_lane']} | {row['migration_tier']} | {row['recommended_action']} |"
        )
    lines.extend([
        "",
        "## Migration order",
        "",
    ])
    for step in data["recommended_sequence"]:
        lines.append(f"{step['order']}. **{step['name']}** — {step['action']}")
    lines.extend([
        "",
        "## Claim ceiling",
        "",
        data["claim_ceiling"],
        "",
    ])
    return "\n".join(lines)


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = [
        "# Development inventory validation",
        "",
        "> Generated from `validation.json`. The JSON is canonical; this file is a human projection.",
        "",
        f"Overall result: **{receipt['result']}**",
        "",
    ]
    for check in receipt["checks"]:
        lines.append(f"- **{check['result']}** `{check['check_id']}` — {check['detail']}")
    lines.extend(["", "## External check", ""])
    validator = receipt["external_checks"]["baseline_validator"]
    lines.append(f"- **{validator['status']}** `BASELINE-V2-RUNTIME-VALIDATOR` — {validator['detail']}")
    lines.extend(["", "## Claim ceiling", "", receipt["claim_ceiling"], ""])
    return "\n".join(lines)


def build_inventory() -> dict[str, Any]:
    ledger, baseline, copy_manifest = load_inputs()
    development_dirs = sorted(path.name for path in SOURCE_DEVELOPMENT.iterdir() if path.is_dir())
    tracked_repo = run_git("ls-files", "--", SOURCE_DEVELOPMENT.relative_to(SOURCE_REPO).as_posix())
    untracked_repo = run_git("ls-files", "--others", "--exclude-standard", "--", SOURCE_DEVELOPMENT.relative_to(SOURCE_REPO).as_posix())
    ignored_repo = run_git("ls-files", "--others", "--ignored", "--exclude-standard", "--", SOURCE_DEVELOPMENT.relative_to(SOURCE_REPO).as_posix())
    stable_repo = [
        path for path in run_git("ls-files", "--", SOURCE_PROJECT_REL.as_posix())
        if not path.startswith(f"{SOURCE_PROJECT_REL.as_posix()}/development/")
    ]
    referrers = find_stable_referrers(development_dirs, stable_repo)

    tracked_by_dir: dict[str, list[str]] = defaultdict(list)
    untracked_by_dir: dict[str, list[str]] = defaultdict(list)
    ignored_by_dir: dict[str, list[str]] = defaultdict(list)
    for bucket, paths in ((tracked_by_dir, tracked_repo), (untracked_by_dir, untracked_repo), (ignored_by_dir, ignored_repo)):
        for repo_path in paths:
            project_path = project_relative(repo_path)
            if project_path and (directory := development_directory(project_path)):
                bucket[directory].append(project_path)

    status_by_dir: dict[str, list[str]] = defaultdict(list)
    for line in run_git("status", "--porcelain=v1", "--", SOURCE_DEVELOPMENT.relative_to(SOURCE_REPO).as_posix()):
        raw_path = line[3:].split(" -> ")[-1]
        project_path = project_relative(raw_path.rstrip("/"))
        if project_path and (directory := development_directory(project_path)):
            status_by_dir[directory].append(line)

    ledger_artifacts_by_dir: dict[str, list[dict[str, Any]]] = defaultdict(list)
    ledger_dev_artifacts: list[dict[str, Any]] = []
    for artifact in ledger.get("artifacts", []):
        normalized = normalize_ledger_development_path(str(artifact.get("path", "")))
        if not normalized:
            continue
        row = {
            "artifact_id": artifact.get("artifact_id"),
            "path": normalized,
            "status": artifact.get("status"),
            "artifact_type": artifact.get("artifact_type"),
        }
        ledger_dev_artifacts.append(row)
        directory = development_directory(normalized)
        if directory:
            ledger_artifacts_by_dir[directory].append(row)

    baseline_by_dir: dict[str, list[dict[str, Any]]] = defaultdict(list)
    missing_baseline_paths: list[dict[str, Any]] = []
    source_drifted_baseline: list[dict[str, Any]] = []
    exact_baseline_in_craft = 0
    current_source_in_craft = 0
    for member in baseline["inventory"]:
        source_path = str(member["path"])
        prefix = SOURCE_PROJECT_REL.as_posix() + "/"
        if not source_path.startswith(prefix):
            continue
        project_path = source_path[len(prefix):]
        source = SOURCE_PROJECT / project_path
        destination = CRAFT_ROOT / project_path
        source_sha = sha256_file(source) if source.is_file() else None
        craft_sha = sha256_file(destination) if destination.is_file() else None
        row = {
            "source_path": source_path,
            "destination_path": f"craft/{project_path}",
            "sha256": member["sha256"],
            "size": member["bytes"],
            "source_sha256": source_sha,
            "craft_sha256": craft_sha,
            "path_present_in_craft": destination.is_file(),
            "source_matches_baseline": source_sha == member["sha256"],
            "craft_matches_baseline": craft_sha == member["sha256"],
            "craft_matches_current_source": craft_sha is not None and craft_sha == source_sha,
        }
        if row["craft_matches_baseline"]:
            exact_baseline_in_craft += 1
        if row["craft_matches_current_source"]:
            current_source_in_craft += 1
        if not row["path_present_in_craft"]:
            missing_baseline_paths.append(row)
        elif not row["source_matches_baseline"]:
            source_drifted_baseline.append(row)
        if (directory := development_directory(project_path)):
            baseline_by_dir[directory].append(row)

    copied_hashes = Counter(entry["sha256"] for entry in copy_manifest["entries"])
    directory_rows: list[dict[str, Any]] = []
    for directory in development_dirs:
        tracked = tracked_by_dir[directory]
        untracked = untracked_by_dir[directory]
        ignored = ignored_by_dir[directory]
        source_like_untracked = [path for path in untracked if not is_generated_residue(path)]
        generated_untracked = [path for path in untracked if is_generated_residue(path)]
        unique_code = 0
        duplicate_count = 0
        bytes_tracked_untracked = 0
        for project_path in tracked + untracked:
            path = SOURCE_PROJECT / project_path
            if not path.is_file():
                continue
            bytes_tracked_untracked += path.stat().st_size
            if is_code_or_formalization(project_path):
                unique_code += 1
            if project_path in tracked and copied_hashes[sha256_file(path)]:
                duplicate_count += 1

        ledger_rows = sorted(ledger_artifacts_by_dir[directory], key=lambda row: (str(row["path"]), str(row["artifact_id"])))
        baseline_rows = sorted(baseline_by_dir[directory], key=lambda row: row["source_path"])
        has_dirty = bool(status_by_dir[directory])
        is_baseline_closure = bool(baseline_rows) or directory in {"meta-type-instantiation-cli", "implementation-conformance"}
        if is_baseline_closure:
            tier = "T0_REQUIRED_BASELINE_CLOSURE"
            action = "author an exact dependency-closed copy and path-rebinding candidate"
        elif has_dirty and source_like_untracked:
            tier = "HOLD_ACTIVE_WRITER"
            action = "inventory now; freeze an immutable source epoch before any copy"
        elif ledger_rows:
            tier = "T1_ACTIVE_LEDGER_EVIDENCE"
            action = "migrate as a separately bounded evidence or product-history bundle"
        elif referrers[directory]:
            tier = "T2_REFERENCED_DEVELOPMENT_HISTORY"
            action = "preserve externally or migrate only with the referencing surface"
        else:
            tier = "T3_UNREFERENCED_DEVELOPMENT_HISTORY"
            action = "retain in source history; do not copy by default"

        work_lane = "operational-support" if directory in OPERATIONAL_SUPPORT_DIRS else "product-construction-or-evidence"
        facets = []
        if baseline_rows:
            facets.append("frozen-baseline-member")
        if directory == "meta-type-instantiation-cli":
            facets.append("baseline-control-plane")
        if directory == "implementation-conformance":
            facets.append("derived-current-state-control-plane")
        if ledger_rows:
            facets.append("ledger-addressed")
        if referrers[directory]:
            facets.append("stable-tree-referenced")
        if has_dirty:
            facets.append("dirty-or-untracked")
        if generated_untracked or ignored:
            facets.append("contains-generated-residue")
        directory_rows.append({
            "directory": directory,
            "source_path": f"projects/domainspec-v2/development/{directory}/",
            "counts": {
                "tracked": len(tracked),
                "untracked_nonignored": len(untracked),
                "source_like_untracked": len(source_like_untracked),
                "generated_untracked": len(generated_untracked),
                "ignored": len(ignored),
                "code_or_formalization": unique_code,
                "exact_content_duplicates_in_copied_tree": duplicate_count,
            },
            "bytes_tracked_and_untracked": bytes_tracked_untracked,
            "dirty_status": sorted(status_by_dir[directory]),
            "source_like_untracked_examples": sorted(source_like_untracked)[:40],
            "ledger_artifacts": ledger_rows,
            "stable_referrers": {"count": len(referrers[directory]), "paths": referrers[directory]},
            "baseline_inventory_members": baseline_rows,
            "facets": facets,
            "work_lane": work_lane,
            "migration_tier": tier,
            "recommended_action": action,
        })

    required_control_bundle = [path_entry(path) for path in CONTROL_BUNDLE_RELATIVE]
    active_writer_dirs = [row["directory"] for row in directory_rows if row["migration_tier"] == "HOLD_ACTIVE_WRITER"]
    tier_counts = Counter(row["migration_tier"] for row in directory_rows)
    node_path = shutil.which("node")
    baseline_validator = {
        "status": "not_evaluable",
        "detail": "`node` is not available on the current shell PATH; no runtime validator claim is made.",
    }
    if node_path:
        result = subprocess.run(
            [node_path, "development/meta-type-instantiation-cli/validate-baseline.mjs"],
            cwd=SOURCE_PROJECT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, check=False,
        )
        baseline_validator = {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "detail": f"validator exited {result.returncode}",
            "output": result.stdout[-12000:],
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "inventory_id": INVENTORY_ID,
        "status": "research-inventory",
        "authority_effect": "none",
        "source_direction": {
            "from": "projects/domainspec-v2/development/",
            "to": "CyberAlchemy-lab/craft/",
            "operation": "read-only inventory; no copy performed",
        },
        "inputs": {
            "ledger": {"path": "projects/domainspec-v2/.craft/ledger.yml", "sha256": sha256_file(LEDGER)},
            "baseline": {"path": "projects/domainspec-v2/development/meta-type-instantiation-cli/CANONICAL-IMPLEMENTED-BASELINE.v2.json", "sha256": sha256_file(BASELINE), "baseline_id": baseline["baseline_id"], "baseline_digest": baseline["baseline_digest"]},
            "copy_manifest": {"path": "evidence/migrations/domainspec-v2-to-craft/source-epoch.json", "sha256": sha256_file(COPY_MANIFEST), "selected_tree_sha256": copy_manifest["selected_tree_sha256"]},
        },
        "summary": {
            "development_directories": len(development_dirs),
            "tracked_files": len(tracked_repo),
            "untracked_nonignored_files": len(untracked_repo),
            "ignored_files": len(ignored_repo),
            "ledger_development_artifacts": len(ledger_dev_artifacts),
            "migration_tiers": dict(sorted(tier_counts.items())),
            "active_writer_hold_directories": active_writer_dirs,
        },
        "external_validation": {
            "baseline_validator": baseline_validator,
        },
        "findings": [
            {"finding_id": "DEV-GAP-01", "statement": f"The admitted baseline inventory has {len(baseline['inventory'])} members; {current_source_in_craft} current source bytes are present in Craft and {len(missing_baseline_paths)} development paths are absent."},
            {"finding_id": "DEV-GAP-02", "statement": f"The admitted baseline is also semantically stale against {len(source_drifted_baseline)} current source members. Those same current bytes were copied exactly into Craft, so this is source-baseline drift, not Craft-only drift."},
            {"finding_id": "DEV-GAP-03", "statement": "The baseline manifest, owner decision, validator, ontology current-state views, and materializer remain outside Craft, so the copied current-definition projections do not have local validation closure."},
            {"finding_id": "DEV-GAP-04", "statement": f"The copied Craft ledger still addresses {len(ledger_dev_artifacts)} development artifacts that were excluded from the transplant."},
            {"finding_id": "DEV-GAP-05", "statement": f"Active writer-owned work exists in {', '.join(active_writer_dirs) if active_writer_dirs else 'no directories'} and must not be silently frozen by this inventory."},
            {"finding_id": "DEV-GAP-06", "statement": "Ignored and generated build residue is evidence of local execution state, not a migration candidate."},
        ],
        "baseline_closure": {
            "baseline_id": baseline["baseline_id"],
            "baseline_digest": baseline["baseline_digest"],
            "inventory_files": len(baseline["inventory"]),
            "present_current_source_bytes_in_craft": current_source_in_craft,
            "exact_baseline_bytes_in_craft": exact_baseline_in_craft,
            "missing_paths_from_craft": len(missing_baseline_paths),
            "source_drifted_members": len(source_drifted_baseline),
            "missing_inventory_members": missing_baseline_paths,
            "source_drifted_inventory_members": source_drifted_baseline,
            "required_control_bundle": required_control_bundle,
            "closure_state": "incomplete" if missing_baseline_paths or source_drifted_baseline or any(not row["exists_in_craft"] for row in required_control_bundle) else "complete",
        },
        "ledger_development_artifacts": sorted(ledger_dev_artifacts, key=lambda row: (str(row["path"]), str(row["artifact_id"]))),
        "directories": directory_rows,
        "recommended_sequence": [
            {"order": 1, "name": "Resolve the baseline epoch", "action": "Review the 24 current-source changes against baseline v2 and choose a successor current-baseline candidate or an explicit restoration. Do not label baseline v2 current while this drift remains."},
            {"order": 2, "name": "Preserve the baseline bridge", "action": "Author one exact historical bridge candidate for the six control-plane records plus the five missing frozen members, retaining their old identity and claim ceiling."},
            {"order": 3, "name": "Reconcile copied ledger references", "action": "For every development artifact reference, choose local migration, explicit external source binding, or deliberate retirement; never leave an accidental broken local path."},
            {"order": 4, "name": "Freeze active writer-owned work", "action": "Create a new immutable source epoch for EVF and the EVF reference consumer only after their current owner declares the selected bytes stable."},
            {"order": 5, "name": "Migrate bounded product and evidence bundles", "action": "Move T1 bundles by dependency closure and lane, keeping product-construction evidence separate from operational-support residue."},
            {"order": 6, "name": "Retain history without bulk copying", "action": "Keep T2 and T3 development history at an explicit source locator unless a live consumer proves it is needed."},
        ],
        "claim_ceiling": "This inventory proves only the observed source population, exact current baseline gap, ledger-addressed surfaces, and migration classifications at this source epoch. It does not accept, admit, copy, rebind, activate, publish, release, deploy, or retire any artifact.",
    }


def validate(data: dict[str, Any], source_before: dict[str, Any], craft_before: str) -> dict[str, Any]:
    source_after = source_epoch()
    craft_after = craft_tree_digest()
    directory_names = sorted(path.name for path in SOURCE_DEVELOPMENT.iterdir() if path.is_dir())
    inventory_names = [row["directory"] for row in data["directories"]]
    ledger_paths = [row["path"] for row in data["ledger_development_artifacts"]]
    represented_ledger_paths = [artifact["path"] for row in data["directories"] for artifact in row["ledger_artifacts"]]
    checks = [
        ("INV-01-DIRECTORY-COVERAGE", inventory_names == directory_names and len(inventory_names) == len(set(inventory_names)), f"{len(inventory_names)} directories represented exactly once"),
        ("INV-02-TRACKED-COUNT", data["summary"]["tracked_files"] == source_after["tracked_count"], f"{source_after['tracked_count']} tracked development files"),
        ("INV-03-UNTRACKED-COUNT", data["summary"]["untracked_nonignored_files"] == source_after["untracked_nonignored_count"], f"{source_after['untracked_nonignored_count']} untracked nonignored development files"),
        ("INV-04-LEDGER-COVERAGE", Counter(ledger_paths) == Counter(represented_ledger_paths), f"{len(ledger_paths)} ledger development artifact records classified"),
        ("INV-05-BASELINE-DENOMINATOR", data["baseline_closure"]["inventory_files"] == 771, "canonical baseline denominator is 771"),
        ("INV-06-BASELINE-RECONCILIATION", data["baseline_closure"]["present_current_source_bytes_in_craft"] + data["baseline_closure"]["missing_paths_from_craft"] == data["baseline_closure"]["inventory_files"] and data["baseline_closure"]["exact_baseline_bytes_in_craft"] + data["baseline_closure"]["source_drifted_members"] + data["baseline_closure"]["missing_paths_from_craft"] == data["baseline_closure"]["inventory_files"], f"{data['baseline_closure']['exact_baseline_bytes_in_craft']} exact baseline bytes, {data['baseline_closure']['source_drifted_members']} source-drifted members, and {data['baseline_closure']['missing_paths_from_craft']} missing paths reconcile to 771"),
        ("INV-06A-NO-CRAFT-ONLY-BASELINE-DRIFT", data["baseline_closure"]["present_current_source_bytes_in_craft"] + data["baseline_closure"]["missing_paths_from_craft"] == data["baseline_closure"]["inventory_files"], "every present baseline member in Craft exactly matches the current source byte"),
        ("INV-07-SOURCE-UNCHANGED", source_before == source_after, "tracked, source-like untracked, and status epochs unchanged during generation"),
        ("INV-08-CRAFT-UNCHANGED", craft_before == craft_after, "Craft tree digest unchanged; no development file was copied"),
        ("INV-09-MACHINE-PARSEABLE", json.loads(pretty_json(data))["inventory_id"] == INVENTORY_ID, "canonical inventory parses as JSON"),
        ("INV-10-PROJECTION-DETERMINISTIC", render_inventory(data) == render_inventory(json.loads(pretty_json(data))), "human projection is deterministic from canonical JSON"),
        ("INV-11-ACTIVE-WRITER-HOLD", "evolvable-validation-framework" in data["summary"]["active_writer_hold_directories"] and "evf-reference-consumer" in data["summary"]["active_writer_hold_directories"], "current EVF and reference-consumer bytes are held from migration"),
        ("INV-12-NONAUTHORITY", data["authority_effect"] == "none", "inventory grants no migration or lifecycle authority"),
    ]
    rows = [{"check_id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail} for check_id, passed, detail in checks]
    return {
        "schema_version": "cyberalchemy-lab-development-migration-inventory-validation/v1",
        "inventory_id": INVENTORY_ID,
        "result": "PASS" if all(row["result"] == "PASS" for row in rows) else "FAIL",
        "checks": rows,
        "external_checks": data["external_validation"],
        "source_epoch": source_after,
        "craft_tree_sha256": craft_after,
        "inventory_sha256": sha256_bytes(canonical_bytes(data)),
        "projection_sha256": sha256_bytes(render_inventory(data).encode()),
        "claim_ceiling": "PASS establishes deterministic inventory coverage and no-effect generation only. It does not authorize or perform migration, acceptance, admission, publication, release, deployment, or retirement.",
    }


def main() -> int:
    source_before = source_epoch()
    craft_before = craft_tree_digest()
    data = build_inventory()
    receipt = validate(data, source_before, craft_before)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    RECEIPTS_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "inventory.json").write_text(pretty_json(data))
    (OUTPUT_ROOT / "INVENTORY.md").write_text(render_inventory(data))
    (RECEIPTS_ROOT / "validation.json").write_text(pretty_json(receipt))
    (RECEIPTS_ROOT / "VALIDATION.md").write_text(render_receipt(receipt))
    print(json.dumps({
        "result": receipt["result"],
        "inventory_sha256": receipt["inventory_sha256"],
        "projection_sha256": receipt["projection_sha256"],
        "summary": data["summary"],
        "baseline_closure": {
            key: data["baseline_closure"][key]
            for key in ("inventory_files", "present_current_source_bytes_in_craft", "exact_baseline_bytes_in_craft", "source_drifted_members", "missing_paths_from_craft", "closure_state")
        },
    }, indent=2))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
