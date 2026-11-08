#!/usr/bin/env python3
"""Cold, read-only replay of the retained T31 local output evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from inventory import inventory
from run import TRANSITIONS, link_episode


def check_report(report: dict, rows: list) -> None:
    expected = {
        "schema_version": "lab-T31-local-output-episode/v1",
        "inventory": {"workflows": 10, "transitions": 28},
        "observed_terminal_output_transitions": rows,
        "observed_count": len(rows),
        "remaining_transition_count": 28 - len(rows),
        "zero_output_substitute_accepted": False,
        "source_or_authority_effect": "none",
        "native_output_journal_or_all28_qualified": False,
        "w03_regression": "NOT-RUN; candidate assessment unsupported",
        "claim_ceiling": "Two isolated original candidate producer paths with original bytes and later Work references. The 26 other output-bearing transitions, signed current Source8 cut, native output journal and final T31 qualification remain open.",
    }
    if report != expected:
        raise ValueError("retained T31 claim or output lineage changed")


def verify(root: Path) -> dict:
    selected = inventory()
    if json.loads((root / "INVENTORY.json").read_bytes()) != selected:
        raise ValueError("retained original workflow inventory changed")
    report = json.loads((root / "RESULT.json").read_bytes())
    rows = [link_episode(kind, root, selected) for kind in TRANSITIONS]
    check_report(report, rows)
    return {"result": "PASS", "observed": len(rows), "remaining": 28 - len(rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root.resolve()), sort_keys=True))
