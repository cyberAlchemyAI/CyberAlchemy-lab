#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
RECEIPT = ROOT / "receipts/validation.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    binding = load(ROOT / "binding.json")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("RB-01-IDENTITY-AND-POSTURE", binding["binding_id"] == "cal.binding.ontology-product-lifecycle" and binding["status"] == "test-candidate" and binding["authority_effect"] == "none", {key: binding[key] for key in ("binding_id", "status", "authority_effect")})
    source_rows = []
    for runtime in binding["runtime_implementations"]:
        for source in runtime["source_bindings"]:
            path = LAB / source["path"]
            source_rows.append({"runtime_id": runtime["runtime_id"], "path": source["path"], "expected": source["sha256"], "actual": sha(path) if path.is_file() else None})
    check("RB-02-RUNTIME-SOURCE-BINDINGS", all(row["expected"] == row["actual"] for row in source_rows), source_rows)

    coordination = binding["coordination_context"]
    coordination_path = LAB / coordination["path"]
    context_rows = [{"path": coordination["path"], "expected": coordination["sha256"], "actual": sha(coordination_path)}]
    for context in binding["semantic_contexts"]:
        path = LAB / context["path"]
        context_rows.append({"path": context["path"], "expected": context["sha256"], "actual": sha(path)})
    map_binding = binding["context_map"]
    map_path = LAB / map_binding["path"]
    context_rows.append({"path": map_binding["path"], "expected": map_binding["sha256"], "actual": sha(map_path)})
    check("RB-03-CONTEXT-SOURCE-BINDINGS", all(row["expected"] == row["actual"] for row in context_rows), context_rows)

    coordination_data = load(coordination_path)
    context_map = load(map_path)
    expected_contexts = [item["context_ref"] for item in binding["semantic_contexts"]]
    check("RB-04-CONTEXT-MAP-OWNERSHIP", coordination_data["bounded_context_refs"] == expected_contexts == context_map["context_refs"] and all(item["ownership"] == "external-semantic-owner" for item in binding["semantic_contexts"]) and map_binding["ownership"] == "context-map-owner", {"coordination": coordination_data["bounded_context_refs"], "map": context_map["context_refs"]})
    runtimes = binding["runtime_implementations"]
    check("RB-05-REPLACEABLE-IMPLEMENTATIONS", len(runtimes) == 2 and all(item["replaceable"] and not item["adopted"] and item["authority_effect"] == "none" for item in runtimes) and {item["role"] for item in runtimes} == {"selected-existing-adapter", "independent-test-double"}, [{"runtime_id": item["runtime_id"], "role": item["role"]} for item in runtimes])
    owners = binding["owner_boundaries"]
    check("RB-06-OWNER-NON-COLLAPSE", owners["meaning_owners_unchanged"] and not owners["runtime_owns_product"] and not owners["runtime_owns_source_meaning"] and owners["product_owner_ref"] != owners["runtime_binding_owner_ref"], owners)

    run = subprocess.run(["cargo", "test", "--manifest-path", str(ROOT / "Cargo.toml"), "--", "--test-threads=1"], cwd=LAB, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    check("RB-07-RUST-PRODUCT-TESTS", run.returncode == 0 and "5 passed; 0 failed" in run.stdout, {"returncode": run.returncode, "summary_present": "5 passed; 0 failed" in run.stdout})

    generator_path = ROOT / "generator.py"
    spec = importlib.util.spec_from_file_location("binding_generator", generator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    projection = ROOT / "BINDING.md"
    check("RB-08-GENERATOR-BINDING", binding["source_direction"]["generator_sha256"] == sha(generator_path), {"expected": binding["source_direction"]["generator_sha256"], "actual": sha(generator_path)})
    check("RB-09-PROJECTION-PARITY", projection.is_file() and projection.read_text(encoding="utf-8") == module.render(binding), sha(projection) if projection.is_file() else "missing")

    failures = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-runtime-binding-validation/v1",
        "binding_id": binding["binding_id"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "summary": {"passed": len(checks) - len(failures), "failed": len(failures), "total": len(checks), "rust_product_tests": 5},
        "checks": checks,
        "materials": {"binding_sha256": sha(ROOT / "binding.json"), "rust_source_sha256": sha(ROOT / "src/lib.rs"), "rust_tests_sha256": sha(ROOT / "tests/l3_product.rs"), "cargo_lock_sha256": sha(ROOT / "Cargo.lock")},
        "capabilities_proved": ["evolution", "replay", "checkpoint-recovery", "context-observation", "runtime-replacement", "hostile-chain-rejection"],
        "claim_ceiling": "PASS proves Product-port behavior for two replaceable private test adapters over the exact selected sources. It does not adopt a runtime, admit a binding, or grant operational authority."
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
