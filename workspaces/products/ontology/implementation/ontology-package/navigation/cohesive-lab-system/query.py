#!/usr/bin/env python3
"""Source-current read-only queries over the admitted cohesive root."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import validate


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
NAVIGATION = HERE / "navigation.json"
SOURCES = HERE / "sources.json"


def emit(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def one(items: list[dict[str, Any]], key: str, identity: str) -> dict[str, Any] | None:
    return next((item for item in items if item.get(key) == identity), None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=[
        "summary", "list-components", "get-component", "list-relations", "get-relation",
        "list-residue", "route-residue", "list-review-routes", "route-review", "get-source-ontology",
    ])
    parser.add_argument("identity", nargs="?")
    args = parser.parse_args()

    validation = validate.validate()
    if validation["result"] != "PASS":
        emit({"result": "BLOCK", "error": "navigation projection is not source-current", "failed_checks": validation["failed_checks"]})
        return 1
    nav = validate.load(NAVIGATION)

    if args.operation == "summary":
        output: Any = {
            "result": "PASS",
            "projection_id": nav["projection_id"],
            "root": nav["root"],
            "counts": validation["counts"],
            "work_lanes": nav["work_lanes"],
            "authority_effect": "none",
        }
    elif args.operation == "list-components":
        output = nav["components"]
    elif args.operation == "get-component":
        output = one(nav["components"], "component_id", args.identity or "")
    elif args.operation == "list-relations":
        output = nav["relations"]
    elif args.operation == "get-relation":
        output = one(nav["relations"], "relation_id", args.identity or "")
    elif args.operation == "list-residue":
        output = nav["residue_routes"]
    elif args.operation == "route-residue":
        output = one(nav["residue_routes"], "residue_id", args.identity or "") or one(nav["residue_routes"], "route_id", args.identity or "")
    elif args.operation == "list-review-routes":
        output = nav["review_routes"]
    elif args.operation == "route-review":
        output = one(nav["review_routes"], "group_id", args.identity or "") or one(nav["review_routes"], "route_id", args.identity or "")
    else:
        sources = validate.load(SOURCES)
        inventory_source = next(item for item in sources["sources"] if item["source_id"] == "LEGACY-ONTOLOGY-INVENTORY")
        inventory = validate.load(REPO / inventory_source["path"])
        output = [
            item for item in inventory["packages"]
            if item.get("ontology_id") == args.identity or item.get("profile_path") == args.identity
        ]

    if output is None or output == []:
        emit({"result": "BLOCK", "error": "unknown identity", "operation": args.operation, "identity": args.identity})
        return 2
    emit(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
