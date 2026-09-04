#!/usr/bin/env python3
"""Candidate-local composition of a successor over candidate 0006's postimage."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def composed_registry_postimage(module, root: Path, candidate: dict[str, Any]) -> dict[str, Any]:
    lab = root.parents[3]
    predecessor = module.load(lab / candidate["predecessor_registry"]["path"])
    entries = list(predecessor["entries"])
    lookup = dict(predecessor["proposed_current_lookup"])
    for item in candidate["definitions"]:
        source = lab / item["path"]
        record = module.load(source)
        entries.append({
            "definition_id": record["definition_id"],
            "version": record["version"],
            "term": record["term"],
            "path": item["path"],
            "sha256": module.sha(source),
            "lifecycle_state": "candidate-unadmitted",
        })
        lookup[record["definition_id"]] = f"{record['definition_id']}@{record['version']}"
    entries.sort(key=lambda value: (value["definition_id"], value["version"]))
    return {
        "schema_version": "cyberalchemy-lab-definition-registry-postimage/v1",
        "record_id": candidate["registry_postimage_id"],
        "status": "candidate-postimage",
        "authority_effect": "none",
        "owner_ref": "role:definition-owner",
        "predecessor": candidate["predecessor_registry"],
        "predecessor_candidate": candidate["predecessor_candidate"],
        "candidate_source": "candidate.json",
        "entries": entries,
        "proposed_current_lookup": dict(sorted(lookup.items())),
        "source_direction": {
            "canonical": "registry-postimage.json",
            "human_projection": "DEFINITIONS-INDEX.md",
            "projection_policy": "generated-only",
            "generator_ref": candidate["source_direction"]["generator_ref"],
            "generator_sha256": module.sha(root / "render.py"),
        },
        "claim_ceiling": candidate["registry_claim_ceiling"],
    }
