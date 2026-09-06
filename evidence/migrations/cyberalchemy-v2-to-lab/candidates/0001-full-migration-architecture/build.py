#!/usr/bin/env python3
"""Build the exact, non-effectful CyberAlchemy-v2 to Lab migration envelope."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
SOURCE = Path("/home/vrondelli/projects/domainspec-core/cyberAlchemy-v2")
DEFINITION_ROOT = LAB / "authority/definitions/candidates/0011-repository-migration-manifest"
TYPE_ROOT = LAB / "authority/artifact-types/repository-migration-manifest/v1/candidates/0001"
REQUEST_SCHEMA = LAB / "authority/artifact-types/artifact-type-request/v1/candidates/0002-executable-surface/schema.json"
OWNED_PREFIXES = (
    ROOT.relative_to(LAB).as_posix() + "/",
    DEFINITION_ROOT.relative_to(LAB).as_posix() + "/",
    TYPE_ROOT.relative_to(LAB).as_posix() + "/",
)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stream_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def root_digest(entries: Iterable[dict[str, Any]], path_key: str = "path") -> str:
    digest = hashlib.sha256()
    for item in sorted(entries, key=lambda value: value[path_key]):
        digest.update(item[path_key].encode("utf-8", "surrogateescape"))
        digest.update(b"\0")
        digest.update(str(item.get("sha256", "")).encode())
        digest.update(b"\0")
        digest.update(str(item.get("size", 0)).encode())
        digest.update(b"\n")
    return digest.hexdigest()


def git_snapshot(path: Path) -> dict[str, Any]:
    def run(*args: str) -> str | None:
        result = subprocess.run(["git", "-C", str(path), *args], text=True, capture_output=True)
        return result.stdout.strip() if result.returncode == 0 else None
    return {"head": run("rev-parse", "HEAD"), "status_porcelain_sha256": hashlib.sha256((run("status", "--porcelain=v1", "--untracked-files=all") or "").encode()).hexdigest()}


def match_rule(relative: str, rules: list[dict[str, Any]]) -> tuple[dict[str, Any], str] | None:
    matches: list[tuple[dict[str, Any], str]] = []
    for rule in rules:
        if rule.get("source_exact") == relative:
            matches.append((rule, rule["target_exact"]))
        prefix = rule.get("source_prefix")
        if prefix and relative.startswith(prefix):
            suffix = relative[len(prefix):] if rule.get("strip_source_prefix") else relative
            matches.append((rule, rule["target_prefix"] + suffix))
    if len(matches) != 1:
        return None
    return matches[0]


def scan_excluded(root: Path, relative_root: str) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    bytes_total = 0
    paths: list[str] = []
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        current_rel = current_path.relative_to(SOURCE).as_posix()
        counts["directory"] += 1
        paths.append(current_rel)
        for name in dirs:
            path = current_path / name
            if path.is_symlink():
                counts["symlink"] += 1
                paths.append(path.relative_to(SOURCE).as_posix())
        for name in files:
            path = current_path / name
            rel = path.relative_to(SOURCE).as_posix()
            paths.append(rel)
            try:
                info = path.lstat()
            except FileNotFoundError:
                counts["vanished"] += 1
                continue
            if stat.S_ISREG(info.st_mode):
                counts["regular-file"] += 1
                bytes_total += info.st_size
            elif stat.S_ISLNK(info.st_mode):
                counts["symlink"] += 1
            else:
                counts["special"] += 1
    return {
        "path": relative_root,
        "disposition": "excluded-directory-tree",
        "counts": dict(sorted(counts.items())),
        "entry_count": sum(counts.values()),
        "regular_file_bytes": bytes_total,
        "path_set_sha256": hashlib.sha256("\n".join(sorted(paths)).encode("utf-8", "surrogateescape")).hexdigest(),
    }


def source_inventory() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[str]]:
    policy = load(ROOT / "exclusion-policy.json")
    rules = load(ROOT / "mapping-rules.json")["rules"]
    excluded_names = set(policy["excluded_directory_names"])
    excluded_suffixes = tuple(policy["excluded_file_suffixes"])
    observed: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    excluded_entries: list[dict[str, Any]] = []
    excluded_groups: list[dict[str, Any]] = []
    unmapped: list[str] = []

    for current, dirs, files in os.walk(SOURCE, topdown=True, followlinks=False):
        current_path = Path(current)
        kept_dirs: list[str] = []
        for name in sorted(dirs):
            path = current_path / name
            rel = path.relative_to(SOURCE).as_posix()
            if path.is_symlink():
                info = path.lstat()
                item = {"path": rel, "kind": "symlink", "size": info.st_size, "mode": stat.S_IMODE(info.st_mode), "disposition": "excluded-symlink", "link_target": os.readlink(path)}
                observed.append(item); excluded_entries.append(item)
            elif name in excluded_names:
                excluded_groups.append(scan_excluded(path, rel))
            else:
                info = path.lstat()
                observed.append({"path": rel, "kind": "directory", "size": info.st_size, "mode": stat.S_IMODE(info.st_mode), "disposition": "structural-container-not-copied"})
                kept_dirs.append(name)
        dirs[:] = kept_dirs
        for name in sorted(files):
            path = current_path / name
            rel = path.relative_to(SOURCE).as_posix()
            try:
                info = path.lstat()
            except FileNotFoundError:
                item = {"path": rel, "kind": "vanished", "size": 0, "mode": 0, "disposition": "excluded-race"}
                observed.append(item); excluded_entries.append(item); continue
            if stat.S_ISLNK(info.st_mode):
                item = {"path": rel, "kind": "symlink", "size": info.st_size, "mode": stat.S_IMODE(info.st_mode), "disposition": "excluded-symlink", "link_target": os.readlink(path)}
                observed.append(item); excluded_entries.append(item); continue
            if not stat.S_ISREG(info.st_mode):
                item = {"path": rel, "kind": "special", "size": info.st_size, "mode": stat.S_IMODE(info.st_mode), "disposition": "excluded-special-file"}
                observed.append(item); excluded_entries.append(item); continue
            if rel.endswith(excluded_suffixes):
                item = {"path": rel, "kind": "regular-file", "size": info.st_size, "mode": stat.S_IMODE(info.st_mode), "disposition": "excluded-file-suffix"}
                observed.append(item); excluded_entries.append(item); continue
            match = match_rule(rel, rules)
            item = {"path": rel, "kind": "regular-file", "size": info.st_size, "mode": stat.S_IMODE(info.st_mode), "sha256": stream_sha(path), "disposition": "copy-selected" if match else "blocked-unmapped"}
            observed.append(item)
            if not match:
                unmapped.append(rel)
                continue
            rule, target = match
            item.update({"mapping_rule_id": rule["rule_id"], "plane": rule["plane"], "target_path": target})
            selected.append(item)

    accounted_count = len(observed) + sum(group["entry_count"] for group in excluded_groups)
    inventory = {
        "schema_version": "cyberalchemy-lab-source-inventory/v1", "inventory_id": "CAL-CAV2-SOURCE-INVENTORY-0001", "status": "candidate-observation", "authority_effect": "none",
        "source_root": str(SOURCE), "source_git": git_snapshot(SOURCE),
        "counts": {"observed_individual_entries": len(observed), "excluded_group_entries": sum(group["entry_count"] for group in excluded_groups), "accounted_entries": accounted_count, "structural_directories": sum(1 for item in observed if item["kind"] == "directory"), "selected_regular_files": len(selected), "excluded_individual_entries": len(excluded_entries), "excluded_directory_groups": len(excluded_groups), "unmapped_regular_files": len(unmapped)},
        "selected_regular_file_bytes": sum(item["size"] for item in selected), "selected_root_sha256": root_digest(selected), "entries": observed,
        "claim_ceiling": "Exact filesystem observation for this candidate build only; inventory does not admit, approve, copy, or delete bytes.",
    }
    exclusions = {
        "schema_version": "cyberalchemy-lab-exclusion-inventory/v1", "inventory_id": "CAL-CAV2-EXCLUSION-INVENTORY-0001", "policy_ref": "exclusion-policy.json", "policy_sha256": sha(ROOT / "exclusion-policy.json"), "status": "candidate-observation", "authority_effect": "none",
        "directory_groups": excluded_groups, "individual_entries": excluded_entries,
        "counts": {"directory_groups": len(excluded_groups), "grouped_entries": sum(group["entry_count"] for group in excluded_groups), "individual_entries": len(excluded_entries)},
        "claim_ceiling": "Accounting for non-copied entries only; exclusion does not authorize deletion.",
    }
    return inventory, exclusions, selected, unmapped


def target_baseline() -> dict[str, Any]:
    excluded_names = set(load(ROOT / "exclusion-policy.json")["excluded_directory_names"]) | {".git"}
    entries: list[dict[str, Any]] = []
    for current, dirs, files in os.walk(LAB, topdown=True, followlinks=False):
        current_path = Path(current)
        dirs[:] = sorted(name for name in dirs if name not in excluded_names)
        for name in sorted(files):
            path = current_path / name
            rel = path.relative_to(LAB).as_posix()
            if rel.startswith(OWNED_PREFIXES):
                continue
            info = path.lstat()
            if stat.S_ISREG(info.st_mode):
                entries.append({"path": rel, "kind": "regular-file", "size": info.st_size, "mode": stat.S_IMODE(info.st_mode), "sha256": stream_sha(path)})
            elif stat.S_ISLNK(info.st_mode):
                entries.append({"path": rel, "kind": "symlink", "size": info.st_size, "mode": stat.S_IMODE(info.st_mode), "link_target": os.readlink(path), "sha256": hashlib.sha256(os.readlink(path).encode()).hexdigest()})
    return {
        "schema_version": "cyberalchemy-lab-target-baseline/v1", "baseline_id": "CAL-LAB-TARGET-BASELINE-0001", "status": "candidate-observation", "authority_effect": "none", "target_root": str(LAB), "target_git": git_snapshot(LAB), "candidate_owned_prefix_exclusions": list(OWNED_PREFIXES), "entry_count": len(entries), "root_sha256": root_digest(entries), "entries": entries,
        "claim_ceiling": "Pre-migration target observation excluding this self-referential candidate surface; it grants no write or overwrite authority.",
    }


def render_candidate(candidate: dict[str, Any]) -> str:
    lines = ["<!-- GENERATED FILE: canonical data is candidate.json. -->", "", "# CyberAlchemy-v2 to CyberAlchemy-lab Migration Candidate", "", f"- Candidate: `{candidate['candidate_id']}`", f"- Status: `{candidate['status']}`", f"- Authority effect: `{candidate['authority_effect']}`", "", "## Product construction frontier", "", candidate["construction"]["product_frontier"], "", "## Approval boundary", "", candidate["approval_boundary"]["meaning"], "", "## Claim ceiling", "", candidate["claim_ceiling"]]
    return "\n".join(lines)


def render_migration(data: dict[str, Any]) -> str:
    return "\n".join(["<!-- GENERATED FILE: canonical data is migration.json. -->", "", "# CyberAlchemy-v2 to CyberAlchemy-lab Migration Manifest", "", f"- Manifest: `{data['migration_manifest_id']}`", f"- Status: `{data['status']}`", f"- Authority effect: `{data['authority_effect']}`", f"- Source: `{data['source_repository']['path']}`", f"- Target: `{data['target_repository']['path']}`", f"- Additive only: `{str(data['copy_semantics']['additive_only']).lower()}`", f"- Overwrite: `{str(data['copy_semantics']['overwrite']).lower()}`", f"- Execution authority: `{str(data['execution_authority']).lower()}`", "", "## Claim ceiling", "", data["claim_ceiling"]])


def material_paths() -> list[Path]:
    bases = [ROOT, DEFINITION_ROOT, TYPE_ROOT]
    paths: list[Path] = []
    for base in bases:
        for path in base.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts or "receipts" in path.parts or path.name in {"manifest.json", "MANIFEST.md"}:
                continue
            paths.append(path)
    paths += [LAB / "tooling/generators/artifact_surface.py", LAB / "tooling/validators/artifact_surface_candidate_2.py", REQUEST_SCHEMA]
    return sorted(set(paths), key=lambda path: path.relative_to(LAB).as_posix())


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "author.py")], check=True, cwd=LAB)
    subprocess.run([sys.executable, str(DEFINITION_ROOT / "build.py")], check=True, cwd=LAB)
    subprocess.run([sys.executable, str(TYPE_ROOT / "generator.py")], check=True, cwd=LAB)

    inventory, exclusions, selected, unmapped = source_inventory()
    baseline = target_baseline()
    baseline_by_path = {item["path"]: item for item in baseline["entries"]}
    destination_counts = Counter(item["target_path"] for item in selected)
    duplicate_destinations = sorted(path for path, count in destination_counts.items() if count > 1)
    allow_entries: list[dict[str, Any]] = []
    collisions: list[dict[str, Any]] = []
    for item in selected:
        existing = baseline_by_path.get(item["target_path"])
        action = "create" if existing is None else "preserve-existing" if existing.get("sha256") == item["sha256"] else "block-divergent-collision"
        entry = {"source_path": item["path"], "source_sha256": item["sha256"], "size": item["size"], "mode": item["mode"], "mapping_rule_id": item["mapping_rule_id"], "plane": item["plane"], "target_path": item["target_path"], "action": action}
        allow_entries.append(entry)
        if action == "block-divergent-collision": collisions.append(entry)
    allowlist = {
        "schema_version": "cyberalchemy-lab-copy-allowlist/v1", "allowlist_id": "CAL-CAV2-COPY-ALLOWLIST-0001", "status": "candidate", "authority_effect": "none", "source_inventory_sha256": "pending", "target_baseline_sha256": "pending", "entries": allow_entries,
        "counts": dict(Counter(item["action"] for item in allow_entries)), "duplicate_destinations": duplicate_destinations, "divergent_collisions": collisions,
        "claim_ceiling": "Exact candidate copy set only; it does not authorize target mutation or source deletion.",
    }
    dump(ROOT / "source-inventory.json", inventory)
    dump(ROOT / "exclusion-inventory.json", exclusions)
    dump(ROOT / "target-baseline.json", baseline)
    allowlist["source_inventory_sha256"] = sha(ROOT / "source-inventory.json")
    allowlist["target_baseline_sha256"] = sha(ROOT / "target-baseline.json")
    dump(ROOT / "copy-allowlist.json", allowlist)

    post_entries = [{"path": item["target_path"], "sha256": item["source_sha256"], "size": item["size"]} for item in allow_entries]
    expected = {
        "schema_version": "cyberalchemy-lab-expected-postimage/v1", "postimage_id": "CAL-CAV2-TO-LAB-POSTIMAGE-0001", "status": "candidate", "authority_effect": "none", "allowlist_sha256": sha(ROOT / "copy-allowlist.json"), "target_baseline_sha256": sha(ROOT / "target-baseline.json"), "imported_entry_count": len(post_entries), "imported_root_sha256": root_digest(post_entries), "create_count": sum(item["action"] == "create" for item in allow_entries), "preserve_existing_count": sum(item["action"] == "preserve-existing" for item in allow_entries), "collision_count": len(collisions), "duplicate_destination_count": len(duplicate_destinations), "claim_ceiling": "Expected imported subtree digest only; not evidence that migration occurred or that imports are admitted or active.",
    }
    dump(ROOT / "expected-postimage.json", expected)
    rollback_paths = sorted((item["target_path"] for item in allow_entries if item["action"] == "create"), key=lambda value: (value.count("/"), value), reverse=True)
    rollback = {
        "schema_version": "cyberalchemy-lab-migration-rollback/v1", "rollback_id": "CAL-CAV2-TO-LAB-ROLLBACK-0001", "status": "candidate-description", "authority_effect": "none", "allowlist_sha256": sha(ROOT / "copy-allowlist.json"), "remove_only_if_execution_receipt_matches": True, "created_file_paths": rollback_paths, "created_file_count": len(rollback_paths), "source_paths": [], "overwrite_restoration_paths": [], "procedure": ["Require separate rollback authorization bound to the execution receipt.", "Verify each candidate path is inside the allowlist create-set and still has the copied source digest.", "Remove files deepest-first; remove only empty directories created by the execution journal.", "Never mutate the source repository."], "claim_ceiling": "Rollback description only; it grants no deletion authority.",
    }
    dump(ROOT / "rollback.json", rollback)
    migration = {
        "schema_version": "cyberalchemy-lab-repository-migration-manifest/v1", "migration_manifest_id": "CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-MANIFEST-0001", "version": "1.0.0-test-candidate.1", "status": "candidate-unapproved", "authority_effect": "none",
        "source_repository": {"path": str(SOURCE), "inventory": {"path": "source-inventory.json", "sha256": sha(ROOT / "source-inventory.json")}},
        "target_repository": {"path": str(LAB), "baseline": {"path": "target-baseline.json", "sha256": sha(ROOT / "target-baseline.json")}},
        "architecture": {"path": "architecture/architecture.json", "sha256": sha(ROOT / "architecture/architecture.json")}, "mapping_rules": {"path": "mapping-rules.json", "sha256": sha(ROOT / "mapping-rules.json")}, "exclusion_inventory": {"path": "exclusion-inventory.json", "sha256": sha(ROOT / "exclusion-inventory.json")}, "copy_allowlist": {"path": "copy-allowlist.json", "sha256": sha(ROOT / "copy-allowlist.json")}, "expected_postimage": {"path": "expected-postimage.json", "sha256": sha(ROOT / "expected-postimage.json")}, "rollback_ref": {"path": "rollback.json", "sha256": sha(ROOT / "rollback.json")},
        "copy_semantics": {"additive_only": True, "overwrite": False, "source_mutation": False, "import_grants_authority": False}, "execution_authority": False,
        "validation_obligations": ["complete-source-accounting", "current-source-digests", "unique-total-mapping", "no-divergent-collisions", "current-target-baseline", "dry-run-no-effect", "isolated-copy-rehearsal", "expected-postimage-closure", "rollback-create-set-closure"],
        "semantic_definition_refs": ["cal.definition.repository-migration-manifest@1.0.0-candidate.1", "cal.definition.validation@1.0.0-candidate.1", "cal.definition.artifact-type@1.0.0-candidate.1"],
        "source_direction": {"canonical": "migration.json", "human_projection": "MIGRATION.md", "projection_policy": "generated-only", "generator_ref": "build.py"},
        "claim_ceiling": "Exact product candidate only; no approval, execution, admission, activation, source deletion, overwrite, commit, push, publication, release, or deployment follows.",
    }
    dump(ROOT / "migration.json", migration)
    candidate = load(ROOT / "candidate.json")
    candidate["status"] = "test-candidate-built" if not (unmapped or duplicate_destinations or collisions) else "candidate-built-with-blockers"
    dump(ROOT / "candidate.json", candidate)
    write(ROOT / "CANDIDATE.md", render_candidate(candidate))
    write(ROOT / "MIGRATION.md", render_migration(migration))

    manifest = {
        "schema_version": "cyberalchemy-lab-candidate-byte-manifest/v1", "manifest_id": "CAL-CYBERALCHEMY-V2-TO-LAB-MIGRATION-CANDIDATE-MANIFEST-0001", "candidate_id": candidate["candidate_id"], "status": "candidate-digest-closure", "authority_effect": "none",
        "materials": [{"path": path.relative_to(LAB).as_posix(), "sha256": sha(path)} for path in material_paths()],
        "source_inventory_sha256": sha(ROOT / "source-inventory.json"), "target_baseline_sha256": sha(ROOT / "target-baseline.json"), "copy_allowlist_sha256": sha(ROOT / "copy-allowlist.json"), "expected_postimage_sha256": sha(ROOT / "expected-postimage.json"), "rollback_sha256": sha(ROOT / "rollback.json"),
        "source_direction": {"canonical": "manifest.json", "human_projection": "MANIFEST.md", "projection_policy": "generated-only", "generator": "build.py"},
        "claim_ceiling": "Immutable candidate review envelope only; it does not approve, admit, activate, execute, delete, overwrite, commit, push, publish, release, or deploy.",
    }
    dump(ROOT / "manifest.json", manifest)
    lines = ["<!-- GENERATED FILE: canonical data is manifest.json. -->", "", "# Migration Candidate Manifest", "", f"- Manifest: `{manifest['manifest_id']}`", f"- Materials: `{len(manifest['materials'])}`", f"- Source inventory: `{manifest['source_inventory_sha256']}`", f"- Copy allowlist: `{manifest['copy_allowlist_sha256']}`", "", "## Claim ceiling", "", manifest["claim_ceiling"]]
    write(ROOT / "MANIFEST.md", "\n".join(lines))
    build_receipt = {"schema_version": "cyberalchemy-lab-migration-build-receipt/v1", "result": "PASS" if not (unmapped or duplicate_destinations or collisions) else "BLOCK", "authority_effect": "none", "counts": {**inventory["counts"], **allowlist["counts"], "divergent_collisions": len(collisions), "duplicate_destinations": len(duplicate_destinations)}, "materials": {"manifest_sha256": sha(ROOT / "manifest.json"), "source_inventory_sha256": sha(ROOT / "source-inventory.json"), "copy_allowlist_sha256": sha(ROOT / "copy-allowlist.json")}, "blockers": {"unmapped": unmapped, "duplicate_destinations": duplicate_destinations, "collisions": collisions}, "claim_ceiling": "Build evidence only; no migration effect occurred."}
    dump(ROOT / "receipts/build.json", build_receipt)
    print(f"MIGRATION_CANDIDATE_BUILD={build_receipt['result']}")
    print(f"SOURCE_ACCOUNTED={inventory['counts']['accounted_entries']}")
    print(f"SELECTED_FILES={len(selected)}")
    print(f"SELECTED_BYTES={inventory['selected_regular_file_bytes']}")
    print(f"CREATE={allowlist['counts'].get('create', 0)}")
    print(f"PRESERVE_EXISTING={allowlist['counts'].get('preserve-existing', 0)}")
    print(f"MANIFEST_SHA256={sha(ROOT / 'manifest.json')}")
    raise SystemExit(0 if build_receipt["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
