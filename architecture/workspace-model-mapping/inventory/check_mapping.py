#!/usr/bin/env python3
"""Capture/check this navigation package; never mutate Lab source or runtime state."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parent.parent
SELF = PACKAGE.relative_to(ROOT).as_posix() + "/"
MISSING_REFERENCES = ["craft/work/outcomes/current-verification/broader-qualification.json"]
BODY_WAR_LINKS = ["implementation", "product/lab", "craft/formalization", "craft/impl",
    "ontology-lifecycle/runtime", "ontology-lifecycle/runtime-candidates",
    "ontology-lifecycle/execution-prototypes", "docs/plans", "docs/proposals",
    "evidence/migrations", "output", "website/promotion"]
COLLISION_FILES = ["craft/project/project.json", "coordination/projects/craft/v1/project.json",
    "craft/product/product.json", "product/products/craft/v1/product.json"]


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def paths(*args):
    return {p.decode("utf-8", "surrogateescape") for p in git("ls-files", "-z", *args).split(b"\0") if p}


def fingerprint(relative):
    data = (ROOT / relative).read_bytes()
    return {"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "byte_length": len(data)}


def markdown_sources(allow_capture_outputs=False):
    selected, errors = set(COLLISION_FILES), []
    for doc in sorted(PACKAGE.rglob("*.md")):
        for number, line in enumerate(doc.read_text().splitlines(), 1):
            if line != line.rstrip():
                errors.append(f"trailing whitespace: {doc.relative_to(ROOT)}:{number}")
        for raw in re.findall(r"\[[^\]]*\]\(([^)]+)\)", doc.read_text()):
            raw = raw.strip().strip("<>")
            parsed = urlsplit(raw)
            if parsed.scheme or raw.startswith("//"):
                continue
            target = (doc.parent / unquote(parsed.path)).resolve() if parsed.path else doc
            if not target.exists():
                if allow_capture_outputs and target in {HERE / "source-baseline.json", HERE / "coverage.json"}:
                    continue
                errors.append(f"missing Markdown target: {doc.relative_to(ROOT)} -> {raw}")
                continue
            if parsed.fragment and target.suffix == ".md":
                headings = re.findall(r"^#+\s+(.+)$", target.read_text(), re.M)
                anchors = {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}
                if unquote(parsed.fragment) not in anchors:
                    errors.append(f"missing heading: {doc.relative_to(ROOT)} -> {raw}")
            if target.is_file() and not target.is_relative_to(PACKAGE):
                if target.is_relative_to(ROOT):
                    selected.add(target.relative_to(ROOT).as_posix())
                else:
                    errors.append(f"external file content not selected: {raw}")
    return sorted(selected), errors


def external_links():
    base = ROOT.parent / "body-war"
    result = []
    for relative in BODY_WAR_LINKS:
        p = base / relative
        result.append({"path": str(p), "is_symlink": p.is_symlink(),
            "target": str(p.readlink()) if p.is_symlink() else None,
            "resolved_target": str(p.resolve()) if p.is_symlink() else None,
            "resolves_to_existing_target": p.exists() if p.is_symlink() else False})
    return result


def collisions():
    a, b, c, d = [ROOT / p for p in COLLISION_FILES]
    pc, pd = json.loads(c.read_text()), json.loads(d.read_text())
    return {"project_records_byte_identical": a.read_bytes() == b.read_bytes(),
        "product_subject_identical": pc["product_id"] == pd["product_id"],
        "product_records_byte_identical": c.read_bytes() == d.read_bytes(),
        "product_versions": [{"path": p.relative_to(ROOT).as_posix(),
            "schema_version": obj["schema_version"], "version": obj["version"]}
            for p, obj in [(c, pc), (d, pd)]]}


def rules_and_errors():
    data = json.loads((HERE / "path-map.json").read_text())
    rules = data["regions"]
    errors = []
    for key in ["id", "prefix"]:
        if len({r[key] for r in rules}) != len(rules):
            errors.append(f"duplicate region {key}")
    for r in rules:
        for key in ["owner_scope", "roles", "proposed_home", "disposition", "note"]:
            if not r.get(key): errors.append(f"missing {key}: {r['id']}")
    return sorted(rules, key=lambda r: len(r["prefix"]), reverse=True), errors


def selection(rules, include_missing):
    tracked = paths("--cached")
    other = paths("--others", "--exclude-standard")
    missing = paths("--deleted") if include_missing else set()
    counts, roots, unclassified = defaultdict(Counter), defaultdict(Counter), []
    chosen = (tracked | other) - {p for p in tracked | other if p.startswith(SELF)}
    for p in sorted(chosen):
        region = next((r for r in rules if p == r["prefix"] or p.startswith(r["prefix"] + "/")), None)
        if region is None:
            unclassified.append(p)
            continue
        kind = "tracked_missing" if p in missing else "tracked_present" if p in tracked else "untracked_present"
        counts[region["id"]][kind] += 1
        roots[p.split("/")[0]][kind] += 1
    return {"selection": "tracked plus non-ignored untracked; mapping package excluded",
        "missing_status_captured": include_missing, "selected_path_count": len(chosen),
        "unclassified_count": len(unclassified), "unclassified_paths": unclassified,
        "by_region": dict(sorted(counts.items())), "by_root": dict(sorted(roots.items())),
        "totals": dict(sum(counts.values(), Counter()))}


def write_json(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--capture", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rules, errors = rules_and_errors()
    selected, link_errors = markdown_sources(allow_capture_outputs=args.capture)
    errors.extend(link_errors)
    current = [fingerprint(p) for p in selected if (ROOT / p).is_file()]
    if len(current) != len(selected): errors.append("one or more required evidence files missing")
    if args.capture and not errors:
        mapping_fingerprint = fingerprint((HERE / "path-map.json").relative_to(ROOT).as_posix())
        coverage = selection(rules, include_missing=True)
        if coverage["unclassified_count"]:
            errors.append(f"{coverage['unclassified_count']} unclassified paths")
        if current != [fingerprint(p) for p in selected]:
            errors.append("selected evidence changed during capture; review before retry")
        if mapping_fingerprint != fingerprint(mapping_fingerprint["path"]):
            errors.append("path map changed during capture; review before retry")
        if not errors:
            captured = datetime.now(timezone.utc).isoformat()
            coverage.update({"captured_at_utc": captured, "authority_effect": "none",
                "mapping_fingerprint": mapping_fingerprint, "region_count": len(rules)})
            baseline = {"observed_client_date": "2026-11-05", "captured_at_utc": captured,
                "repository_root": str(ROOT), "git_head": git("rev-parse", "HEAD").decode().strip(),
                "scope": "selected linked source files, not an atomic whole-repository byte snapshot",
                "authority_effect": "none", "files": current, "collisions": collisions(),
                "missing_references": [{"path": p, "exists": (ROOT / p).exists()} for p in MISSING_REFERENCES],
                "external_consumer_links": external_links()}
            write_json("source-baseline.json", baseline)
            write_json("coverage.json", coverage)
            print(json.dumps({"captured": True, "source_files": len(current), "regions": len(rules),
                "selected_paths": coverage["selected_path_count"], "totals": coverage["totals"]}))
    elif args.check and not errors:
        baseline = json.loads((HERE / "source-baseline.json").read_text())
        coverage = json.loads((HERE / "coverage.json").read_text())
        if coverage["mapping_fingerprint"] != fingerprint(coverage["mapping_fingerprint"]["path"]):
            errors.append("path map changed since coverage capture")
        if coverage["region_count"] != len(rules): errors.append("captured region count changed")
        if baseline["files"] != current: errors.append("selected evidence list/hash/length changed")
        if baseline["collisions"] != collisions(): errors.append("identity collision observations changed")
        if baseline["external_consumer_links"] != external_links(): errors.append("external consumer links changed")
        for item in baseline["missing_references"]:
            if item["exists"] != (ROOT / item["path"]).exists(): errors.append(f"reference availability changed: {item['path']}")
        live = selection(rules, include_missing=False)
        if live["unclassified_count"]: errors.append(f"{live['unclassified_count']} current paths have no region")
        if set(coverage["by_region"]) - {r["id"] for r in rules}: errors.append("unknown captured region")
        total = sum(sum(v.values()) for v in coverage["by_region"].values())
        if coverage["unclassified_count"] or total != coverage["selected_path_count"]:
            errors.append("captured coverage incomplete")
        if coverage["totals"] != dict(sum((Counter(v) for v in coverage["by_region"].values()), Counter())):
            errors.append("captured totals inconsistent")
        if not errors:
            print(json.dumps({"ok": True, "source_files": len(current), "regions": len(rules),
                "captured_paths": coverage["selected_path_count"], "current_paths": live["selected_path_count"],
                "current_unclassified": live["unclassified_count"], "markdown_files": len(list(PACKAGE.rglob('*.md'))),
                "external_links": len(baseline["external_consumer_links"]), "runtime_tests_run": False}))
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
