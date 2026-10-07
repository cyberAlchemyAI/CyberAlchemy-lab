#!/usr/bin/env python3
"""Navigate every inventoried repository path through the governance map."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path

from project import HERE, ROOT, checked, inputs, normalize, read_json


def zone_for(path: str, zones: list[dict]) -> dict | None:
    matches = [zone for zone in zones if (path.startswith(zone["prefix"]) if zone["prefix"] else "/" not in path)]
    return max(matches, key=lambda zone: len(zone["prefix"])) if matches else None


def status_index() -> dict[str, list[dict]]:
    sources, _, _, artifacts, relations, types, _, bootstrap_artifacts, bootstrap_relations = inputs()
    bindings = {item["id"]: item for item in sources["bindings"]}
    definitions = checked(bindings["definition-registry"]["path"], bindings["definition-registry"]["sha256"])
    current = definitions["current_lookup"]
    found: dict[str, list[dict]] = {}

    def add(path: str, item: dict) -> None:
        found.setdefault(path, []).append(item)

    for item in definitions["entries"]:
        identity = item["definition_id"]
        add(item["path"], {"subject_kind": "definition-version", "identity_ref": identity,
                           "version": item["version"], "effective_state": item["lifecycle_state"],
                           "is_current": current.get(identity) == identity + "@" + item["version"],
                           "admission_decision_ref": item["admission_decision_ref"]})
    for item in types["admitted_contracts"]:
        entry = {"subject_kind": "artifact-type-contract", "identity_ref": item["artifact_type_ref"],
                 "effective_state": item["lifecycle_state"], "admission_decision_ref": item["admission_decision_ref"]}
        add(item["artifact_path"], {**entry, "material_role": "artifact-contract"})
        add(item["schema_path"], {**entry, "material_role": "schema"})
    predecessor = bootstrap_artifacts["predecessor_transition"]
    for overlay in (artifacts, bootstrap_artifacts):
        for raw in overlay["entries"]:
            item = normalize(raw)
            effective = predecessor["to"] if item["identity_ref"] == predecessor["identity_ref"] else item["lifecycle_state"]
            base = {"subject_kind": "artifact-instance", "identity_ref": item["identity_ref"],
                    "effective_state": effective, "admission_decision_ref": item["admission_decision_ref"]}
            add(item["source_path"], {**base, "material_role": "source-candidate"})
            add(item["admitted_instance_path"], {**base, "material_role": "admitted-copy"})
    for overlay in (relations, bootstrap_relations):
        for raw in overlay["entries"]:
            item = normalize(raw)
            base = {"subject_kind": "typed-relation-instance", "identity_ref": item["relation_id"],
                    "relation_kind_ref": item["relation_kind_ref"], "effective_state": item["lifecycle_state"],
                    "admission_decision_ref": item["admission_decision_ref"]}
            add(item["source_path"], {**base, "material_role": "source-candidate"})
            add(item["admitted_instance_path"], {**base, "material_role": "admitted-copy"})
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--summary", action="store_true", help="count every path by governance zone")
    group.add_argument("--path", help="inspect one exact repository-relative path")
    group.add_argument("--zone", help="list paths in one governance zone")
    group.add_argument("--check", action="store_true", help="check inventory freshness and total zone coverage")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    mapping = read_json(HERE / "repository-map.json")
    inventory = read_json(ROOT / mapping["coverage_source"])
    zones = mapping["zones"]
    if len({zone["id"] for zone in zones}) != len(zones) or len({zone["prefix"] for zone in zones}) != len(zones):
        raise ValueError("duplicate governance zone id or prefix")
    by_path = {item["path"]: item for item in inventory["files"]}
    assigned = {path: zone_for(path, zones) for path in by_path}
    missing = [path for path, zone in assigned.items() if zone is None]
    if missing:
        raise ValueError(f"unmapped repository paths: {missing[:10]}")
    if args.check:
        result = subprocess.run(["python3", "tooling/inventory/build_inventory.py", "--check"],
                                cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            raise ValueError(result.stderr.strip() or result.stdout.strip())
        zone_ids = {zone["id"] for zone in zones}
        counts = Counter(zone["id"] for zone in assigned.values())
        unused = sorted(zone_ids - counts.keys())
        if unused:
            raise ValueError(f"zones without inventoried files: {unused}")
        governed_paths = status_index()
        missing_governed = sorted(set(governed_paths) - set(by_path))
        if missing_governed:
            raise ValueError(f"governed source paths outside inventory: {missing_governed[:10]}")
        for edge in mapping["integration_edges"]:
            if edge["from"] not in zone_ids or edge["to"] not in zone_ids:
                raise ValueError(f"unknown integration zone: {edge}")
            for path in edge["evidence_paths"]:
                if not (ROOT / path).exists():
                    raise ValueError(f"missing integration evidence path: {path}")
        print(f"governance map valid: {len(by_path)} paths; {len(zones)} zones; {len(governed_paths)} exact governed-match paths; {len(mapping['integration_edges'])} source-linked integration edges")
        return
    if args.summary:
        counts = Counter(zone["id"] for zone in assigned.values())
        print(json.dumps({"inventoried_paths": len(by_path), "tracked": inventory["summary"]["tracked_count"],
                          "untracked": inventory["summary"]["untracked_count"],
                          "exact_governed_match_paths": len(status_index()),
                          "zone_counts": dict(sorted(counts.items())), "unmapped": 0,
                          "claim_ceiling": mapping["claim_ceiling"]}, indent=2))
        return
    if args.zone:
        if args.zone not in {zone["id"] for zone in zones}:
            parser.error(f"unknown zone: {args.zone}")
        paths = sorted(path for path, zone in assigned.items() if zone["id"] == args.zone)
        print(json.dumps({"zone": args.zone, "total_paths": len(paths), "offset": args.offset,
                          "paths": paths[args.offset:args.offset + args.limit]}, indent=2))
        return
    record = by_path.get(args.path)
    if record is None:
        parser.error("path not in the current inventory selection; refresh the inventory or check Git ignores")
    zone = assigned[args.path]
    result = {"file": record, "zone": zone, "authority": "resolve exact source named by status_route",
              "provenance": {"path": record["path"], "sha256": record["sha256"], "tracking": record["tracking"]},
              "lifecycle": "do not infer from path", "exact_governed_matches": status_index().get(args.path, []),
              "authority_effect": "none"}
    if args.path.startswith("docs/decisions/") and args.path.endswith("/decision.json"):
        decision = read_json(ROOT / args.path)
        result["decision_record"] = {key: decision.get(key) for key in ("decision_id", "status", "authority_effect", "claim_ceiling")}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
