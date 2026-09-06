#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_cargo(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    with tempfile.TemporaryDirectory(prefix="cal-p2-independent-") as target:
        env["CARGO_TARGET_DIR"] = target
        return subprocess.run(
            ["cargo", *args, "--manifest-path", str(ROOT / "implementation/Cargo.toml"), "--locked", "--offline"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )


def main() -> int:
    product = load(ROOT / "product/product-capability.json")
    business = load(ROOT / "business/business-ontology.json")
    project = load(ROOT / "domainspec/project.json")
    graph = load(ROOT / "compiled/graph.json")
    system = load(ROOT / "compiled/system-ontology.json")
    implementation = load(ROOT / "implementation/manifest.json")
    smoke = load(ROOT / "evidence/smoke-test.json")
    primary = load(ROOT / "receipts/p2-validation.json")

    checks: list[dict[str, Any]] = []
    def check(check_id: str, ok: bool, detail: Any) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if ok else "FAIL", "detail": detail})

    check("primary-receipt-pass", primary["result"] == "PASS" and primary["required_stage_state"] == "TESTED_PROTOTYPE", primary["summary"])
    check("capability-feature-identity-separated", product["capability_id"] != product["product_feature_relation"]["feature_id"], {"capability": product["capability_id"], "feature": product["product_feature_relation"]["feature_id"]})
    check("no-context-explicit", product["context_posture"]["kind"] == "explicit-no-context" and project["context_posture"]["bounded_context_ref"] is None, project["context_posture"])
    check("business-traces-capability", business["capability_binding"]["sha256"] == sha(ROOT / "product/product-capability.json"), business["capability_binding"])
    project_bindings = {item["role"]: item for item in project["input_bindings"]}
    check("specification-traces-business", project_bindings["capability-local-business-ontology-prototype"]["sha256"] == sha(ROOT / "business/business-ontology.json"), project_bindings["capability-local-business-ontology-prototype"])
    check("graph-traces-specification", graph["generated_from"]["sha256"] == sha(ROOT / "domainspec/project.json"), graph["generated_from"])
    check("system-traces-graph", system["generated_from"]["sha256"] == sha(ROOT / "compiled/graph.json"), system["generated_from"])
    check("implementation-traces-system", implementation["input_binding"]["sha256"] == sha(ROOT / "compiled/system-ontology.json"), implementation["input_binding"])
    check("smoke-traces-implementation", smoke["implementation_binding"]["sha256"] == sha(ROOT / "implementation/manifest.json"), smoke["implementation_binding"])
    check("selected-witness-only", business["closure"]["selected_legacy_ids"] == ["DS-D1.1"] and project["recursion_stop"]["value"] == 1, business["closure"])
    check("zero-authority-chain", all(item.get("authority_effect") == "none" for item in (product, business, project, graph, system, implementation, smoke, primary)), None)

    test = run_cargo(["test", "--quiet"])
    run = run_cargo(["run", "--quiet"])
    check("independent-rust-test", test.returncode == 0, {"exit_code": test.returncode, "stderr": test.stderr})
    check("independent-rust-smoke", run.returncode == 0 and run.stdout.strip() == smoke["expected_stdout"], {"exit_code": run.returncode, "stdout": run.stdout.strip(), "stderr": run.stderr})

    failed = [item for item in checks if item["result"] == "FAIL"]
    result = "PASS" if not failed else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-independent-prototype-validation/v1",
        "subject": "CAL-P2-DEFINITION-SNAPSHOT-CONSTRUCTION-VERTICAL",
        "stage_id": "CML09-P2-BUILD-THIN-END-TO-END-PRODUCT-PROTOTYPE",
        "result": result,
        "checks": checks,
        "summary": {"passed": len(checks) - len(failed), "failed": len(failed), "total": len(checks)},
        "primary_receipt_binding": {"path": "receipts/p2-validation.json", "sha256": sha(ROOT / "receipts/p2-validation.json")},
        "authority_effect": "none",
        "claim_ceiling": "Independent PASS corroborates only the exact P2 trace and local Rust smoke result. It grants no semantic admission, broad runtime conformance, product approval, migration, activation, publication, or deployment authority."
    }
    out = ROOT / "evidence/independent-validation.json"
    dump(out, receipt)
    human = [
        "<!-- GENERATED FILE: run p2-validate.py. -->",
        "",
        "# Independent CML09-P2 Validation",
        "",
        f"- Result: `{result}`",
        f"- Checks: `{receipt['summary']['passed']}/{receipt['summary']['total']}`",
        "",
        "| Check | Result |",
        "| --- | --- |",
        *[f"| `{item['check_id']}` | `{item['result']}` |" for item in checks],
        "",
        "## Claim ceiling",
        "",
        receipt["claim_ceiling"],
        "",
    ]
    (ROOT / "evidence/INDEPENDENT-VALIDATION.md").write_text("\n".join(human), encoding="utf-8")
    print(f"INDEPENDENT_CML09_P2={result}")
    print(f"CHECKS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
