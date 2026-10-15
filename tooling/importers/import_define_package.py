#!/usr/bin/env python3
"""Import an exact private Define source snapshot; never activate its runtime.

The destination must be new. Existing imports are inspected using --inspect.
Only the two named, Git-tracked source trees are copied. No source validators,
tests, model clients, compilers, gateways, or installation commands are run.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile

LAB = Path(__file__).resolve().parents[2]
EXECUTION = "evidence/migrations/cyberalchemy-v2-to-lab/executions/0080-define-package-import"
ROOTS = ("define", "implementation/define-cli")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def git(source: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()


def records(value: object):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from records(item)
    elif isinstance(value, list):
        for item in value:
            yield from records(item)


def inspect(lab: Path) -> dict:
    manifest = json.loads((lab / EXECUTION / "manifest.json").read_text())
    failures = []
    expected = set()
    for row in manifest["files"]:
        path = lab / row["destination"]
        expected.add(path.relative_to(lab / "define/source").as_posix())
        if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != row["sha256"] or path.stat().st_size != row["size_bytes"]:
            failures.append(row["destination"])
    actual = {p.relative_to(lab / "define/source").as_posix() for p in (lab / "define/source").rglob("*") if p.is_file()}
    failures.extend(sorted(actual ^ expected))
    inventory_digest = digest(json.dumps(manifest["files"], sort_keys=True, separators=(",", ":")).encode())
    if inventory_digest != manifest["inventory_sha256"]:
        failures.append("inventory_sha256")
    return {"inspection": "PASS" if not failures else "BLOCK", "file_count": len(expected), "failures": failures,
            "inventory_sha256": inventory_digest, "authority_effect": "none", "runtime_tests_run": False}


def import_package(source: Path, lab: Path, captured_on: str) -> dict:
    source = source.resolve()
    if source.name != "cyberAlchemy-v2":
        raise ValueError("Expected the source checkout cyberAlchemy-v2")
    target = lab / "define/source"
    evidence = lab / EXECUTION
    if target.exists() or evidence.exists():
        raise ValueError("Refusing to overwrite an existing source snapshot or import execution")
    predecessor = lab / "evidence/migrations/cyberalchemy-v2-to-lab/executions/0064-define-bridge-context-import/package-snapshot.tar.gz"
    if not predecessor.is_file():
        raise ValueError("Missing preserved 0064 predecessor archive")
    tracked = git(source, "ls-files", "-z", "--", *ROOTS).split("\0")
    paths = sorted(x for x in tracked if x)
    present = {p.relative_to(source).as_posix() for root in ROOTS for p in (source / root).rglob("*") if p.is_file()}
    if present != set(paths):
        raise ValueError("Source scope contains missing, untracked or ignored files; review before copying")
    for rel in paths:
        path = source / rel
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Unsupported source entry: {rel}")
    profile = json.loads((source / "define/profile.json").read_text())
    if profile["status"] != "candidate" or profile["authority_effect"] != "none":
        raise ValueError("Source standing changed; review before importing")
    material = {"define/" + rel for rel in profile["material_files"]}
    if not material <= set(paths):
        raise ValueError("Missing declared parent material")
    before = {rel: digest((source / rel).read_bytes()) for rel in paths}
    source_head = git(source, "rev-parse", "HEAD")
    source_status = git(source, "status", "--porcelain=v1", "--", *ROOTS)
    entries = []
    for rel in paths:
        if rel.startswith("implementation/define-cli/"):
            role = "candidate-cli-source"
        elif rel in material:
            role = "parent-declared-material"
        elif rel.startswith(("define/reviews/", "define/candidates/")):
            role = "source-review-or-intake-evidence"
        elif rel.startswith("define/business-ontology/"):
            role = "business-child-package"
        elif rel.startswith("define/system-ontology/"):
            role = "system-child-package"
        elif rel.startswith("define/capabilities/"):
            role = "capability-package"
        else:
            role = "source-receipt-or-collaboration-evidence"
        dest = target / "cyberAlchemy-v2" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / rel, dest)
        entries.append({"source": "cyberAlchemy-v2/" + rel, "destination": dest.relative_to(lab).as_posix(),
                        "sha256": before[rel], "size_bytes": dest.stat().st_size, "classification": role})
    if git(source, "rev-parse", "HEAD") != source_head or any(digest((source / rel).read_bytes()) != before[rel] for rel in paths):
        raise ValueError("Source changed during import; retain the partial snapshot for diagnosis")
    summary = dict(collections.Counter(x["classification"] for x in entries))
    manifest = {"schema_version": "cal.define-source-import/v1", "execution_id": "0080-define-package-import",
                "captured_on": captured_on, "source_checkout": str(source), "source_commit": source_head,
                "selected_source_status": source_status, "source_package_id": profile["package_id"],
                "source_package_version": profile["package_version"], "visibility": "private",
                "import_standing": "candidate-source-snapshot", "authority_effect": "none",
                "admission": "not-requested", "runtime_activation": "not-performed",
                "selected_roots": list(ROOTS), "classification_counts": summary, "files": entries,
                "inventory_sha256": digest(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode())}
    write_json(evidence / "manifest.json", manifest)

    # Compare only overlapping selected paths; absence from the old context
    # archive is not a statement that the source file was newly authored.
    old = {}
    with tarfile.open(predecessor) as archive:
        for member in archive.getmembers():
            if member.isfile() and member.name.startswith("cyberAlchemy-v2/define/"):
                old[member.name] = digest(archive.extractfile(member).read())
    current = {e["source"]: e["sha256"] for e in entries if e["source"].startswith("cyberAlchemy-v2/define/")}
    comparison = {"predecessor": predecessor.relative_to(lab).as_posix(),
                  "unchanged": sorted(k for k in current.keys() & old.keys() if current[k] == old[k]),
                  "changed": [{"path": k, "previous_sha256": old[k], "imported_sha256": current[k]}
                              for k in sorted(current.keys() & old.keys()) if current[k] != old[k]],
                  "not_in_predecessor": sorted(current.keys() - old.keys()),
                  "predecessor_only": sorted(old.keys() - current.keys()), "previous_import_modified": False}
    write_json(evidence / "predecessor-comparison.json", comparison)

    # Record exact declared fingerprint standing without rewriting a single pin.
    # These files are evidence in their original owner scope, not Lab authority.
    dependencies = []
    selected_source_paths = {e["source"] for e in entries}
    for rel in paths:
        if not rel.endswith(".json") or "/generated/" in rel:
            continue
        try:
            value = json.loads((source / rel).read_text())
        except (ValueError, UnicodeError):
            continue
        for row in records(value):
            path, expected = row.get("path"), row.get("sha256")
            if not isinstance(path, str) or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                continue
            if not path.startswith(("cyberAlchemy-v2/", "projects/", "arcanum/", "domainspec-core/")):
                continue
            candidate = source.parent / path
            if path.startswith("projects/domainspec-v2/"):
                candidate = source.parent / "domainspec-core" / path
            elif path.startswith("arcanum/"):
                candidate = source.parent / "domainspec-core" / path
            # No path can escape the selected workspace through a declared ref.
            safe = candidate.resolve().is_relative_to(source.parent.resolve())
            actual = digest(candidate.read_bytes()) if safe and candidate.is_file() else None
            copied = path in selected_source_paths
            dependencies.append({"declared_in": "cyberAlchemy-v2/" + rel, "path": path, "expected_sha256": expected,
                                 "observed_sha256": actual, "standing": "exact" if actual == expected else "drift" if actual else "unavailable",
                                 "included_in_snapshot": copied})
    write_json(evidence / "dependency-standing.json", {"scope": "workspace-qualified path/sha256 records in selected non-generated JSON",
               "counts": dict(collections.Counter(r["standing"] for r in dependencies)), "records": dependencies,
               "pins_rewritten": False, "behavioral_conformance_assessed": False})

    # Syntactic import map only: does not execute modules or establish runtime closure.
    imports = []
    pattern = re.compile(r"(?:from\s*|import\s*\(\s*)[\"'](\.[^\"']+)[\"']")
    imported_paths = set(paths)
    for rel in paths:
        if not rel.startswith("implementation/define-cli/") or Path(rel).suffix not in (".mjs", ".js", ".ts"):
            continue
        for ref in pattern.findall((source / rel).read_text()):
            resolved = ((source / rel).parent / ref).resolve()
            if not resolved.is_relative_to(source):
                continue
            dep = resolved.relative_to(source).as_posix()
            if dep not in imported_paths:
                imports.append({"importer": "cyberAlchemy-v2/" + rel, "specifier": ref,
                                "target": "cyberAlchemy-v2/" + dep, "present_in_source": resolved.is_file()})
    write_json(evidence / "external-code-imports.json", {"scope": "literal relative imports in CLI .mjs/.js/.ts files; includes tests and scripts",
               "records": imports, "unique_targets": sorted({r["target"] for r in imports}),
               "runtime_dependency_closure": "not-established", "dynamic_and_filesystem_dependencies": "not-exhaustively-resolved"})
    result = inspect(lab)
    write_json(evidence / "import-integrity.json", result)
    if result["inspection"] != "PASS":
        raise ValueError("Copied snapshot integrity failed")
    return {"files": len(entries), "classifications": summary, "dependency_counts": collections.Counter(r["standing"] for r in dependencies),
            "changed_predecessor_files": len(comparison["changed"]), "newly_selected_files": len(comparison["not_in_predecessor"]),
            "external_code_targets": len({r["target"] for r in imports}), "integrity": result["inspection"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=LAB.parent / "cyberAlchemy-v2")
    parser.add_argument("--destination", type=Path, default=LAB)
    parser.add_argument("--captured-on", default="2026-10-11")
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    result = inspect(args.destination) if args.inspect else import_package(args.source, args.destination, args.captured_on)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
