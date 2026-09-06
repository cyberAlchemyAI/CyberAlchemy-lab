#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

def run_case(source_root: Path, validator: Path, mutate, expected_prefix: str):
    with tempfile.TemporaryDirectory(prefix="cal-d65-s5-hostile-") as temporary:
        root = Path(temporary) / "candidate"
        shutil.copytree(source_root, root)
        mutate(root)
        result = subprocess.run(["python3", str(validator), "--package-root", str(root)], text=True, capture_output=True)
        try:
            receipt = json.loads(result.stdout)
            failures = receipt.get("failures", [])
        except Exception:
            failures = ["INVALID_VALIDATOR_OUTPUT"]
        passed = result.returncode != 0 and any(value.startswith(expected_prefix) for value in failures)
        return passed, failures

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    root = Path(__file__).parent
    validator = root / "validate.py"

    def drift_source(candidate: Path):
        path = candidate / "sources.json"
        data = json.loads(path.read_text())
        data["records"][0]["sha256"] = "0" * 64
        path.write_text(json.dumps(data, indent=2) + "\n")

    def drop_system_node(candidate: Path):
        path = candidate / "generated/system-ontology.json"
        data = json.loads(path.read_text())
        data["semantic_graph"]["nodes"] = data["semantic_graph"]["nodes"][1:]
        path.write_text(json.dumps(data, indent=2) + "\n")

    def tamper_graph(candidate: Path):
        path = candidate / "generated/graph.json"
        data = json.loads(path.read_text())
        data["project_id"] = "tampered-project"
        path.write_text(json.dumps(data, indent=2) + "\n")

    definitions = [
        ("selected-source-digest-drift", drift_source, "SELECTED_SOURCE_DIGEST_DRIFT"),
        ("system-ontology-node-removal", drop_system_node, "MATERIALIZED_OUTPUT_DRIFT:system-ontology.json"),
        ("compiled-graph-tamper", tamper_graph, "MATERIALIZED_OUTPUT_DRIFT:graph.json"),
    ]
    cases = []
    for name, mutation, expected in definitions:
        passed, failures = run_case(root, validator, mutation, expected)
        cases.append({"case": name, "result": "PASS" if passed else "BLOCK", "observed_failure_codes": failures})
    receipt = {
        "schema_version": "cal-d65-s5-hostile-check-receipt/v1",
        "result": "PASS" if all(case["result"] == "PASS" for case in cases) else "BLOCK",
        "cases": cases,
        "claim_ceiling": "Hostile PASS proves only that these selected mutations fail closed; it grants no system-ontology admission or successor authority.",
    }
    rendered = json.dumps(receipt, indent=2) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(rendered)
    print(rendered, end="")
    return 0 if receipt["result"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
