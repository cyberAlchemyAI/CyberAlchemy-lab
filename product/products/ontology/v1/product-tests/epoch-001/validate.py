#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[5]
RECEIPT = ROOT / "receipts/validation.json"
PRODUCT_MANIFEST = LAB / "product/products/ontology/v1/runtime/Cargo.toml"
TEST_MANIFEST = ROOT / "Cargo.toml"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(
    arguments: list[str], *, target: str = "test", full_output: bool = False
) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["CARGO_TARGET_DIR"] = str(ROOT / "target" / target)
    completed = subprocess.run(
        arguments,
        cwd=LAB,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (completed.stdout + completed.stderr).strip()
    return {
        "returncode": completed.returncode,
        "output": output if full_output else output[-4000:],
    }


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    profile = load(ROOT / "test-profile.json")
    checks: list[dict[str, Any]] = []

    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    bound = []
    for item in profile["bound_inputs"]:
        path = LAB / item["path"]
        actual = sha(path) if path.is_file() else None
        bound.append({**item, "actual_sha256": actual, "matches": actual == item["sha256"]})
    check(
        "E2E-01-EXACT-INPUT-BINDINGS",
        len(bound) == 12 and all(item["matches"] for item in bound),
        bound,
    )

    predecessor = profile["predecessor"]
    predecessor_actual = {
        "candidate": sha(LAB / predecessor["candidate_ref"]),
        "receipt": sha(LAB / predecessor["test_receipt_ref"]),
    }
    check(
        "E2E-02-PREDECESSOR-IMMUTABLE",
        predecessor_actual["candidate"] == predecessor["candidate_sha256"]
        and predecessor_actual["receipt"] == predecessor["test_receipt_sha256"],
        predecessor_actual,
    )

    source_receipt = load(
        LAB / "product/products/ontology/v1/product-ontology/source-package/receipts/validation.json"
    )
    source_bindings = load(
        LAB / "product/products/ontology/v1/product-ontology/source-package/source-bindings.json"
    )
    check(
        "E2E-03-SOURCE-CLOSURE-EVIDENCE",
        source_receipt["result"] == "PASS"
        and len(source_bindings["bindings"]) == 8
        and all(item["binding_status"] in {"current", "drift-reconciled-by-successor-binding"} for item in source_bindings["bindings"]),
        {
            "source_receipt": source_receipt["result"],
            "binding_count": len(source_bindings["bindings"]),
            "statuses": sorted({item["binding_status"] for item in source_bindings["bindings"]}),
        },
    )

    materialize_first = run(["python3", str(ROOT / "materialize.py")])
    first_source = (ROOT / "selected-source.json").read_bytes() if (ROOT / "selected-source.json").is_file() else b""
    first_projection = (ROOT / "SOURCE.md").read_bytes() if (ROOT / "SOURCE.md").is_file() else b""
    materialize_second = run(["python3", str(ROOT / "materialize.py")])
    check(
        "E2E-04-DETERMINISTIC-SOURCE-MATERIALIZATION",
        materialize_first["returncode"] == materialize_second["returncode"] == 0
        and first_source == (ROOT / "selected-source.json").read_bytes()
        and first_projection == (ROOT / "SOURCE.md").read_bytes(),
        {
            "selected_source_sha256": sha(ROOT / "selected-source.json"),
            "source_projection_sha256": sha(ROOT / "SOURCE.md"),
        },
    )

    source = load(ROOT / "selected-source.json")
    selection = profile["source_selection"]
    imported_sources = load(
        LAB / "product/products/ontology/v1/product-ontology/source-package/imported/sources.json"
    )["sources"]
    known_sources = {item["id"] for item in imported_sources}
    referenced_sources = {
        ref["source_id"]
        for item in source["nodes"] + source["relations"]
        for ref in item["source_refs"]
    }
    check(
        "E2E-05-REAL-SOURCE-TRACE",
        len(source["nodes"]) == selection["expected_nodes"]
        and len(source["relations"]) == selection["expected_relations"]
        and len(source["residue"]) == selection["expected_residue"]
        and len(known_sources) == selection["expected_sources"]
        and referenced_sources <= known_sources,
        {
            "nodes": len(source["nodes"]),
            "relations": len(source["relations"]),
            "residue": len(source["residue"]),
            "known_sources": len(known_sources),
            "referenced_sources": sorted(referenced_sources),
            "unresolved_sources": sorted(referenced_sources - known_sources),
        },
    )

    generator = import_module(ROOT / "generator.py", "e2e_generator")
    product_test_projection = ROOT / "PRODUCT-TEST.md"
    source_materializer = import_module(ROOT / "materialize.py", "e2e_materializer")
    check(
        "E2E-06-GENERATED-PROJECTION-PARITY",
        product_test_projection.read_text(encoding="utf-8") == generator.render(profile)
        and (ROOT / "SOURCE.md").read_text(encoding="utf-8") == source_materializer.render_source(source),
        {
            "product_test_projection_sha256": sha(product_test_projection),
            "source_projection_sha256": sha(ROOT / "SOURCE.md"),
        },
    )

    fmt = run(["cargo", "fmt", "--manifest-path", str(TEST_MANIFEST), "--check"])
    clippy = run(
        [
            "cargo", "clippy", "--offline", "--manifest-path", str(TEST_MANIFEST),
            "--all-targets", "--", "-D", "warnings",
        ]
    )
    tests = run(["cargo", "test", "--offline", "--manifest-path", str(TEST_MANIFEST)])
    check(
        "E2E-07-RUST-PRODUCT-TESTS",
        fmt["returncode"] == clippy["returncode"] == tests["returncode"] == 0
        and "9 passed; 0 failed" in tests["output"],
        {
            "fmt_returncode": fmt["returncode"],
            "clippy_returncode": clippy["returncode"],
            "tests_returncode": tests["returncode"],
            "rust_product_tests": 9,
            "passing_summary_observed": "9 passed; 0 failed" in tests["output"],
        },
    )

    package_path = ROOT / "ontology-package.json"
    build_first = run(
        [
            "cargo", "run", "--offline", "--quiet", "--manifest-path", str(PRODUCT_MANIFEST),
            "--", "build", str(ROOT / "selected-source.json"), str(package_path),
        ],
        target="product-runtime",
    )
    first_package = package_path.read_bytes() if package_path.is_file() else b""
    build_second = run(
        [
            "cargo", "run", "--offline", "--quiet", "--manifest-path", str(PRODUCT_MANIFEST),
            "--", "build", str(ROOT / "selected-source.json"), str(package_path),
        ],
        target="product-runtime",
    )
    validate = run(
        [
            "cargo", "run", "--offline", "--quiet", "--manifest-path", str(PRODUCT_MANIFEST),
            "--", "validate", str(package_path),
        ],
        target="product-runtime",
    )
    project = run(
        [
            "cargo", "run", "--offline", "--quiet", "--manifest-path", str(PRODUCT_MANIFEST),
            "--", "project", str(package_path),
        ],
        target="product-runtime",
        full_output=True,
    )
    if project["returncode"] == 0:
        (ROOT / "ONTOLOGY-PACKAGE.md").write_text(project["output"] + "\n", encoding="utf-8")
    package = load(package_path) if package_path.is_file() else {}
    check(
        "E2E-08-DETERMINISTIC-PACKAGE-CONSTRUCTION",
        build_first["returncode"] == build_second["returncode"] == validate["returncode"] == project["returncode"] == 0
        and first_package == package_path.read_bytes()
        and len(package.get("nodes", [])) == 23
        and len(package.get("relations", [])) == 24
        and len(package.get("residue", [])) == 5
        and package.get("source_binding", {}).get("sha256") == sha(ROOT / "selected-source.json")
        and package.get("authority_effect") == "none",
        {
            "build_first": build_first,
            "build_second": build_second,
            "validate": validate,
            "package_sha256": sha(package_path) if package_path.is_file() else None,
            "package_counts": {
                "nodes": len(package.get("nodes", [])),
                "relations": len(package.get("relations", [])),
                "residue": len(package.get("residue", [])),
            },
        },
    )

    projection_text = (ROOT / "ONTOLOGY-PACKAGE.md").read_text(encoding="utf-8") if (ROOT / "ONTOLOGY-PACKAGE.md").is_file() else ""
    check(
        "E2E-09-PACKAGE-PROJECTION-AND-AUTHORITY-BOUNDARY",
        projection_text.startswith("<!-- Generated by cal-ontology-product")
        and f"Source digest: `{sha(ROOT / 'selected-source.json')}`" in projection_text
        and profile["authority_effect"] == source["authority_effect"] == package.get("authority_effect") == "none"
        and profile["status"] == "product-test-candidate",
        {
            "package_projection_sha256": sha(ROOT / "ONTOLOGY-PACKAGE.md") if (ROOT / "ONTOLOGY-PACKAGE.md").is_file() else None,
            "authority_effect": package.get("authority_effect"),
            "product_approval_granted": False,
        },
    )

    failures = [item for item in checks if item["result"] == "FAIL"]
    receipt = {
        "schema_version": "cyberalchemy-lab-ontology-product-end-to-end-validation/v1",
        "test_epoch_id": profile["test_epoch_id"],
        "result": "PASS" if not failures else "FAIL",
        "authority_effect": "none",
        "product_approval_granted": False,
        "profile_sha256": sha(ROOT / "test-profile.json"),
        "selected_source_sha256": sha(ROOT / "selected-source.json"),
        "package_sha256": sha(package_path) if package_path.is_file() else None,
        "summary": {
            "passed": len(checks) - len(failures),
            "failed": len(failures),
            "total": len(checks),
            "rust_product_tests": 9,
            "nodes": len(source["nodes"]),
            "relations": len(source["relations"]),
            "typed_residue": len(source["residue"]),
        },
        "capabilities_proved": [
            "source-to-package-trace",
            "deterministic-package-construction",
            "bounded-retrieval",
            "typed-residue-preservation",
            "evolution",
            "replay",
            "checkpoint-recovery",
            "context-coordination",
            "runtime-replacement",
            "authority-mutation-rejection",
        ],
        "checks": checks,
        "approval_boundary": {
            "eligible_if_result_pass": True,
            "decision": "Product approval only",
            "granted": False,
        },
        "claim_ceiling": "PASS proves this exact private end-to-end Product test epoch against the selected source and package digests. It makes a subsequently bound immutable candidate eligible for one Product approval decision but does not grant that approval or any other authority.",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": receipt["result"], "summary": receipt["summary"]}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
