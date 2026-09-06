#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

NODE = "/home/vrondelli/.nvm/versions/node/v26.8.1/bin/node"
TSX = "/home/vrondelli/projects/domainspec-core/implementation/domainspec/backend/node_modules/tsx/dist/cli.mjs"
OUTPUTS = ["graph.json", "source-manifest.json", "event-sourcing-contract.json", "system-ontology.json", "compile-receipt.json"]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path: Path):
    return json.loads(path.read_text())

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, default=Path(__file__).parent)
    parser.add_argument("--compiler", type=Path, default=Path(__file__).parent / "compiler.ts")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    root = args.package_root.resolve()
    failures = []
    checks = []

    try:
        profile = load(root / "profile.json")
        sources = load(root / "sources.json")
        schema = load(root / "schema.json")
        if profile.get("stage") != "D65-S5" or profile.get("status") != "candidate-not-admitted" or profile.get("owner_gate") != "G-D65-COMPILE" or profile.get("implementation_binding_present") is not False:
            failures.append("PROFILE_BOUNDARY_INVALID")
        if schema.get("$id") != "cal-d65-system-ontology-package/v1":
            failures.append("SCHEMA_ID_INVALID")
        observed_ids = []
        for record in sources.get("records", []):
            observed_ids.append(record.get("source_id"))
            path = Path(record.get("path", ""))
            if not path.is_file():
                failures.append(f"SELECTED_SOURCE_MISSING:{record.get('source_id')}")
            elif digest(path) != record.get("sha256"):
                failures.append(f"SELECTED_SOURCE_DIGEST_DRIFT:{record.get('source_id')}")
        if len(observed_ids) != len(set(observed_ids)) or len(observed_ids) != 9:
            failures.append("SELECTED_SOURCE_SET_INVALID")
        checks.append({"check": "selected-source-currentness", "records": len(observed_ids), "result": "PASS" if not any(x.startswith("SELECTED_SOURCE") for x in failures) else "BLOCK"})

        compiled_roots = []
        compiler_errors = []
        with tempfile.TemporaryDirectory(prefix="cal-d65-s5-") as temporary:
            temporary_root = Path(temporary)
            for name in ("run-a", "run-b"):
                output_root = temporary_root / name
                result = subprocess.run(
                    [NODE, TSX, str(args.compiler.resolve()), "--output-root", str(output_root), "--sources-path", str(root / "sources.json")],
                    text=True,
                    capture_output=True,
                    env={**os.environ, "TMPDIR": "/tmp"},
                )
                if result.returncode != 0:
                    compiler_errors.append(result.stderr.strip() or result.stdout.strip())
                compiled_roots.append(output_root)
            if compiler_errors:
                for error in compiler_errors:
                    try:
                        code = json.loads(error.splitlines()[-1]).get("error", "COMPILE_FAILED")
                    except Exception:
                        code = "COMPILE_FAILED"
                    failures.append(code)
            else:
                for name in OUTPUTS:
                    first = (compiled_roots[0] / name).read_bytes()
                    second = (compiled_roots[1] / name).read_bytes()
                    if first != second:
                        failures.append(f"DOUBLE_COMPILE_MISMATCH:{name}")
                    materialized = root / "generated" / name
                    if not materialized.is_file() or first != materialized.read_bytes():
                        failures.append(f"MATERIALIZED_OUTPUT_DRIFT:{name}")
                checks.append({"check": "external-double-compilation", "outputs": len(OUTPUTS), "result": "PASS" if not any("COMPILE" in x or "OUTPUT_DRIFT" in x for x in failures) else "BLOCK"})

        if not compiler_errors and all((root / "generated" / name).is_file() for name in OUTPUTS):
            graph = load(root / "generated/graph.json")
            manifest = load(root / "generated/source-manifest.json")
            event_contract = load(root / "generated/event-sourcing-contract.json")
            system = load(root / "generated/system-ontology.json")
            compile_receipt = load(root / "generated/compile-receipt.json")
            if graph.get("nodes") != system.get("semantic_graph", {}).get("nodes") or graph.get("edges") != system.get("semantic_graph", {}).get("edges"):
                failures.append("GRAPH_SYSTEM_ONTOLOGY_EQUALITY")
            graph_ids = {n["node_id"] for n in graph.get("nodes", [])} | {e["edge_id"] for e in graph.get("edges", [])}
            manifest_ids = {r["graph_id"] for r in manifest.get("records", [])}
            if graph_ids != manifest_ids:
                failures.append("GRAPH_PROVENANCE_CLOSURE")
            if event_contract != system.get("event_calculus", {}).get("contract"):
                failures.append("EVENT_SYSTEM_ONTOLOGY_EQUALITY")
            projection_ids = {p["projectionId"] for p in event_contract.get("projections", [])}
            calculated = {p["projectionId"] for p in system.get("event_calculus", {}).get("projection_contracts", [])}
            if projection_ids != calculated:
                failures.append("PROJECTION_CALCULUS_CLOSURE")
            if compile_receipt.get("result") != "PASS" or compile_receipt.get("deterministic_internal_double_compile") is not True:
                failures.append("COMPILE_RECEIPT_INVALID")
            if len(graph.get("nodes", [])) != 41 or len(graph.get("edges", [])) != 43:
                failures.append("GRAPH_COUNT_INVALID")
            if [len(event_contract.get(key, [])) for key in ("streams", "events", "projections", "joins")] != [5, 5, 3, 2]:
                failures.append("EVENT_CONTRACT_COUNT_INVALID")
            if system.get("status") != "candidate-unadmitted" or system.get("authority") != "generated-system-runtime-read-model":
                failures.append("SYSTEM_ONTOLOGY_BOUNDARY_INVALID")
            if system.get("source", {}).get("admission_option_id") != "D65SRC-1":
                failures.append("SOURCE_ADMISSION_BINDING_INVALID")
            checks.extend([
                {"check": "graph-system-ontology-equality", "nodes": len(graph.get("nodes", [])), "edges": len(graph.get("edges", [])), "result": "PASS" if "GRAPH_SYSTEM_ONTOLOGY_EQUALITY" not in failures else "BLOCK"},
                {"check": "graph-provenance-closure", "records": len(manifest.get("records", [])), "result": "PASS" if "GRAPH_PROVENANCE_CLOSURE" not in failures else "BLOCK"},
                {"check": "event-calculus-closure", "streams": len(event_contract.get("streams", [])), "events": len(event_contract.get("events", [])), "projections": len(event_contract.get("projections", [])), "joins": len(event_contract.get("joins", [])), "result": "PASS" if not any(x in failures for x in ("EVENT_SYSTEM_ONTOLOGY_EQUALITY", "PROJECTION_CALCULUS_CLOSURE", "EVENT_CONTRACT_COUNT_INVALID")) else "BLOCK"},
                {"check": "successor-boundary", "implementation_binding_present": False, "result": "PASS"},
            ])

    except Exception as error:
        failures.append(f"VALIDATOR_EXCEPTION:{error}")

    receipt = {
        "schema_version": "cal-d65-s5-validation-receipt/v1",
        "package_id": "cal-ontology-runtime-integration-system-ontology-epoch-001",
        "stage": "D65-S5",
        "result": "PASS" if not failures else "BLOCK",
        "checks": checks,
        "failures": sorted(set(failures)),
        "gate_id": "G-D65-COMPILE",
        "gate_state": "BLOCK",
        "gate_blocker": "Validated candidate still requires system-ontology owner admission.",
        "admission_granted": False,
        "successor_execution_authorized": False,
        "claim_ceiling": "PASS validates the exact deterministic D65-S5 candidate only. It does not admit the system ontology or authorize D65-S6.",
    }
    rendered = json.dumps(receipt, indent=2) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(rendered)
    print(rendered, end="")
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
