#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[3]
MANIFEST = HERE / "manifest.json"
RECEIPT = HERE / "receipts/validation.json"

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    manifest = load(MANIFEST)
    failures: list[str] = []

    decision_ref = manifest.get("admission_decision", {})
    source_ref = manifest.get("source_graph", {})
    version_ref = manifest.get("versioned_graph", {})
    human_ref = manifest.get("human_graph", {})
    decision_path = LAB / decision_ref.get("path", "")
    source_path = LAB / source_ref.get("path", "")
    version_path = HERE / version_ref.get("path", "")
    human_path = HERE / human_ref.get("path", "")

    for name, path, expected in (
        ("decision", decision_path, decision_ref.get("sha256")),
        ("source-graph", source_path, source_ref.get("sha256")),
        ("versioned-graph", version_path, version_ref.get("sha256")),
        ("human-graph", human_path, human_ref.get("sha256")),
    ):
        if not path.is_file():
            failures.append(f"{name}-missing")
        elif digest(path) != expected:
            failures.append(f"{name}-digest-mismatch")

    if not failures:
        decision = load(decision_path)
        source = load(source_path)
        version = load(version_path)
        human = human_path.read_text(encoding="utf-8")
        if decision.get("decision_id") != "CAL-D65SYS-0020" or decision.get("selection", {}).get("option_id") != "D65SYS-1":
            failures.append("admission-decision-invalid")
        if source_path.read_bytes() != version_path.read_bytes() or source != version:
            failures.append("graph-copy-not-byte-identical")
        if len(version.get("nodes", [])) != 41 or len(version.get("edges", [])) != 43:
            failures.append("graph-count-invalid")
        rendered = []
        for edge in version.get("edges", []):
            source_name = edge["from"].split(".")[-1]
            target_name = edge["to"].split(".")[-1]
            rendered.append(f"{source_name} -{edge['type']}-> {target_name}")
        if any(human.count(line) != 1 for line in rendered):
            failures.append("human-edge-projection-incomplete")
        if manifest.get("canonical_replay_source") is not False:
            failures.append("canonical-replay-boundary-invalid")

    receipt = {
        "schema_version": "cal.system-ontology-graph-version-validation/v1",
        "version_id": manifest.get("version_id"),
        "result": "PASS" if not failures else "BLOCK",
        "failed_checks": failures,
        "checks": {
            "admission_decision_current": not any(item.startswith("decision") or item == "admission-decision-invalid" for item in failures),
            "graph_copy_byte_identical": "graph-copy-not-byte-identical" not in failures,
            "graph_counts": "graph-count-invalid" not in failures,
            "human_edge_projection": "human-edge-projection-incomplete" not in failures,
            "canonical_replay_boundary": "canonical-replay-boundary-invalid" not in failures
        },
        "graph_sha256": version_ref.get("sha256"),
        "nodes": 41,
        "edges": 43,
        "implementation_authorized": False,
        "claim_ceiling": "PASS validates only the admitted versioned graph copy and readable edge projection."
    }
    if args.write_receipt:
        RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
