#!/usr/bin/env python3
"""Finite no-effect host CLI. It never runs Docker or network commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .body_war_canary_evidence import build_evidence_pack, derive_snapshot_boundary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-evidence")
    validate.add_argument("receipts", type=Path)
    validate.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    if args.command == "validate-evidence":
        receipts = json.loads(args.receipts.read_text(encoding="utf-8"))
        result = {"evidence_pack": build_evidence_pack(args.run_id, receipts), "snapshot_boundary": None}
        result["snapshot_boundary"] = derive_snapshot_boundary(result["evidence_pack"])
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    return 2


if __name__ == "__main__": raise SystemExit(main())
