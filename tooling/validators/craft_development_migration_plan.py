#!/usr/bin/env python3
"""Independently validate the Craft development migration planning candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = Path("/home/vrondelli/projects/domainspec-core")
PLAN_PATH = Path("docs/migration-plans/0001-craft-development-closure-v1/plan.json")
INVENTORY_PATH = Path("evidence/migrations/domainspec-v2-to-craft/development-inventory/inventory.json")
GENERATOR_PATH = Path("tooling/generators/craft_development_migration_plan.py")
RECEIPT_PATH = PLAN_PATH.parent / "receipts/validation.json"
RECEIPT_VIEW_PATH = RECEIPT_PATH.with_name("VALIDATION.md")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def load_generator():
    spec = importlib.util.spec_from_file_location("craft_development_migration_plan_generator", LAB_ROOT / GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load projection generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = [
        "<!-- Generated from validation.json by tooling/validators/craft_development_migration_plan.py. Do not edit. -->",
        "",
        "# Craft development migration plan validation",
        "",
        f"- Result: `{receipt['result']}`",
        f"- Checks: `{receipt['summary']['checks_passed']}/{receipt['summary']['checks_total']}`",
        f"- Plan digest: `{receipt['plan_sha256']}`",
        f"- Development inventory digest: `{receipt['inventory_sha256']}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{row['result']}` — `{row['check_id']}`: {row['detail']}" for row in receipt["checks"])
    lines.extend([
        "",
        "## Boundary",
        "",
        receipt["claim_ceiling"],
        "",
    ])
    return "\n".join(lines)


def acyclic(waves: list[dict[str, Any]]) -> bool:
    dependencies = {wave["wave_id"]: set(wave["depends_on"]) for wave in waves}
    done: set[str] = set()
    while len(done) < len(dependencies):
        ready = {wave_id for wave_id, refs in dependencies.items() if wave_id not in done and refs <= done}
        if not ready:
            return False
        done.update(ready)
    return True


def main() -> int:
    plan_file = LAB_ROOT / PLAN_PATH
    inventory_file = LAB_ROOT / INVENTORY_PATH
    plan = json.loads(plan_file.read_text())
    inventory = json.loads(inventory_file.read_text())
    generator = load_generator()
    checks: list[dict[str, str]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    inventory_sha = sha256_file(inventory_file)
    check("PLAN-01-INPUT-DIGEST", plan["inputs"]["development_inventory"]["sha256"] == inventory_sha, "plan binds the exact current development inventory")

    bridge = plan["baseline_bridge"]["entries"]
    expected_rows = inventory["baseline_closure"]["required_control_bundle"] + inventory["baseline_closure"]["missing_inventory_members"]
    expected = sorted((row["source_path"], row["destination_path"], row["sha256"], row["size"]) for row in expected_rows)
    actual = sorted((row["source_path"], row["destination_path"], row["sha256"], row["size"]) for row in bridge)
    check("PLAN-02-L0-SELECTION", len(bridge) == 11 and actual == expected, "L0 is exactly the six control records plus five missing frozen members")
    check("PLAN-03-L0-UNIQUE", len({row["source_path"] for row in bridge}) == 11 and len({row["destination_path"] for row in bridge}) == 11, "all eleven source and destination paths are unique")

    sources_exact = True
    destinations_absent = True
    for row in bridge:
        source = SOURCE_ROOT / row["source_path"]
        destination = LAB_ROOT / row["destination_path"]
        sources_exact = sources_exact and source.is_file() and source.stat().st_size == row["size"] and sha256_file(source) == row["sha256"]
        destinations_absent = destinations_absent and not destination.exists()
    check("PLAN-04-SOURCE-EPOCH-CURRENT", sources_exact, "all eleven selected source files still match recorded sizes and hashes")
    check("PLAN-05-DESTINATION-PREFLIGHT", destinations_absent, "all eleven planned destinations are absent at the planning epoch")
    check("PLAN-06-NO-ACTIVE-WRITER-IN-L0", not any("evolvable-validation-framework" in row["source_path"] or "evf-reference-consumer" in row["source_path"] for row in bridge), "L0 contains no active EVF writer-owned path")
    check("PLAN-07-HISTORICAL-STATUS", plan["baseline_bridge"]["classification"] == "historical-baseline-v2-bridge-not-current-authority" and inventory["baseline_closure"]["source_drifted_members"] == 24, "baseline v2 is historical-only and the 24-member drift denominator remains explicit")

    layer_ids = [row["layer_id"] for row in plan["layers"]]
    check("PLAN-08-LAYERING", len(layer_ids) == 5 and len(set(layer_ids)) == 5 and layer_ids[0] == "L0-HISTORICAL-BASELINE-BRIDGE" and layer_ids[-1] == "L4-INTEGRATED-CRAFT-CANDIDATE", "five decision layers progress from historical bridge to integrated candidate")
    check("PLAN-09-WAVE-GRAPH", len(plan["waves"]) == 5 and acyclic(plan["waves"]), "five-wave dependency graph is closed and acyclic")

    tasks = {row["task_id"]: row for row in plan["tasks"]}
    swus = {row["swu_id"]: row for row in plan["swus"]}
    validations = {row["validation_id"]: row for row in plan["validation_obligations"]}
    task_closure = all(
        swu_id in swus and swus[swu_id]["task_id"] == task_id
        for task_id, task in tasks.items()
        for swu_id in task["swu_ids"]
    ) and all(validation_id in validations for task in tasks.values() for validation_id in task["validation_ids"])
    check("PLAN-10-TASK-SWU-VALIDATION-CLOSURE", len(tasks) == 5 and len(swus) == 5 and task_closure, "each task owns one smallest working unit and all validation references resolve")
    check("PLAN-11-SMALLEST-FIRST-UNIT", plan["distill"]["smallest_coherent_unit"] == "SWU-CML11-001-HISTORICAL-BASELINE-BRIDGE" and swus["SWU-CML11-001-HISTORICAL-BASELINE-BRIDGE"]["task_id"] == "TASK-CML11-001", "Distill selects the exact reversible eleven-file bridge as the first unit")
    check("PLAN-12-DISTILL-TRACE", plan["distill"]["mode"] == "standard" and len(plan["distill"]["rounds"]) == 2 and plan["distill"]["verdict"] == "pass", "Standard Distill preserves two Proposer/Balancer rounds and a recomposition proof")

    preference = plan["workflow_preferences"]
    internal_approval_terms = [gate for gate in plan["gates"] if "approval" in gate["pass_condition"].lower()]
    check("PLAN-13-SINGLE-APPROVAL-BOUNDARY", preference["approval_mode"] == "single-final-product-boundary" and preference["approval_boundary"]["eligible_after_layer"] == "L4-INTEGRATED-CRAFT-CANDIDATE" and not internal_approval_terms, "only the configurable final product boundary requests approval")
    check("PLAN-14-TWO-LANE-PLAN", plan["work_plan"]["product_construction_frontier"] == "SWU-CML11-001-HISTORICAL-BASELINE-BRIDGE" and len(plan["work_plan"]["operational_support"]) == 3, "runnable product work, future operational prerequisites, and deferred effects remain separate")
    check("PLAN-15-NONAUTHORITY", plan["authority_effect"] == "none" and not plan["plan_capability"]["execution_candidate"], "the package is a non-executing planning candidate with zero authority effect")

    rendered = generator.projections(plan)
    projections_exact = all((LAB_ROOT / path).is_file() and (LAB_ROOT / path).read_text() == text for path, text in rendered.items())
    deterministic = rendered == generator.projections(json.loads(canonical_json(plan)))
    check("PLAN-16-GENERATED-PROJECTIONS", projections_exact, "all four human views equal their canonical generated projections")
    check("PLAN-17-DETERMINISM", deterministic, "projection generation is byte-deterministic")

    result = "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-development-migration-plan-validation/v1",
        "plan_ref": PLAN_PATH.as_posix(),
        "result": result,
        "authority_effect": "none",
        "source_direction": {
            "canonical": RECEIPT_PATH.as_posix(),
            "human_projection": RECEIPT_VIEW_PATH.as_posix(),
            "projection_policy": "generated-only",
            "generator": "tooling/validators/craft_development_migration_plan.py"
        },
        "plan_sha256": sha256_file(plan_file),
        "inventory_sha256": inventory_sha,
        "summary": {
            "checks_passed": sum(row["result"] == "PASS" for row in checks),
            "checks_total": len(checks),
            "l0_entries": len(bridge),
            "layers": len(plan["layers"]),
            "waves": len(plan["waves"]),
            "swus": len(plan["swus"])
        },
        "checks": checks,
        "failures": [row["check_id"] for row in checks if row["result"] == "FAIL"],
        "claim_ceiling": "PASS proves planning consistency, exact L0 selection, current preflight hashes, deterministic human projections, and a single final product-approval boundary. It does not establish admitted Invoke Plan status, authorize implementation, copy files, accept the 24 drift dispositions, admit a baseline, publish, release, deploy, or delete source material."
    }
    receipt_text = canonical_json(receipt)
    receipt_path = LAB_ROOT / RECEIPT_PATH
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text)
    (LAB_ROOT / RECEIPT_VIEW_PATH).write_text(render_receipt(receipt))
    print(receipt_text, end="")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
