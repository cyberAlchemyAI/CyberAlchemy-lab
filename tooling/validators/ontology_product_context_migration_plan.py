#!/usr/bin/env python3
"""Validate the Ontology Product and Bounded Context migration planning candidate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = Path("/home/vrondelli/projects/domainspec-core")
PLAN_DIR = Path("docs/migration-plans/0002-ontology-product-context-migration-v1")
PLAN_PATH = PLAN_DIR / "plan.json"
DISPATCH_PATH = PLAN_DIR / "dispatch.json"
GENERATOR_PATH = Path("tooling/generators/ontology_product_context_migration_plan.py")
RECEIPT_PATH = PLAN_DIR / "receipts/validation.json"
RECEIPT_VIEW_PATH = PLAN_DIR / "receipts/VALIDATION.md"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def load_generator():
    spec = importlib.util.spec_from_file_location("ontology_product_context_migration_generator", LAB_ROOT / GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_dispatch(dispatch_path: Path) -> tuple[bool, str]:
    validator = SOURCE_ROOT / ".agents/skills/dispatch-spec/scripts/validate-dispatch.py"
    completed = subprocess.run(["python3", str(validator), str(dispatch_path)], cwd=SOURCE_ROOT, text=True, capture_output=True, check=False)
    output = (completed.stdout + completed.stderr).strip()
    return completed.returncode == 0, output


def render_receipt(receipt: dict[str, Any]) -> str:
    lines = [
        "<!-- Generated from validation.json. Do not edit this projection. -->",
        "",
        "# Ontology Product/context migration plan validation",
        "",
        f"- Result: `{receipt['validation_result']}`",
        f"- Checks: `{receipt['summary']['checks_passed']}/{receipt['summary']['checks_total']}`",
        f"- Plan digest: `{receipt['artifacts']['plan_sha256']}`",
        f"- Dispatch digest: `{receipt['artifacts']['dispatch_sha256']}`",
        f"- Source package status: `{receipt['source_status']}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{row['result']}` — `{row['check_id']}`: {row['detail']}" for row in receipt["validation"])
    lines += ["", "## Blockers", ""]
    lines.extend(f"- {item}" for item in receipt["blockers"])
    lines += ["", "## Residue", "", receipt["residue"], "", "## Claim ceiling", "", receipt["claim_ceiling"], ""]
    return "\n".join(lines)


def main() -> int:
    plan_file = LAB_ROOT / PLAN_PATH
    dispatch_file = LAB_ROOT / DISPATCH_PATH
    plan = json.loads(plan_file.read_text())
    dispatch = json.loads(dispatch_file.read_text())
    generator = load_generator()
    checks: list[dict[str, str]] = []

    def check(check_id: str, condition: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "result": "PASS" if condition else "FAIL", "detail": detail})

    package_exact = True
    for row in plan["source_epoch"]["selected_package_files"]:
        path = SOURCE_ROOT / row["path"]
        package_exact = package_exact and path.is_file() and path.stat().st_size == row["size"] and sha256_file(path) == row["sha256"]
    check("MIG2-01-SOURCE-PACKAGE-EPOCH", package_exact, "all nine selected Ontology Product package files match the recorded size and digest")

    drifts_exact = True
    for row in plan["source_epoch"]["source_drift"]:
        path = SOURCE_ROOT / row["path"]
        drifts_exact = drifts_exact and path.is_file() and sha256_file(path) == row["current_sha256"] and row["recorded_sha256"] != row["current_sha256"]
    check("MIG2-02-SOURCE-DRIFT-CURRENT", drifts_exact and len(plan["source_epoch"]["source_drift"]) == 3, "the exact three known source drifts remain current and explicit")

    source_run = subprocess.run(["python3", "cyberAlchemy-v2/ontology/ontology-product/validate.py"], cwd=SOURCE_ROOT, text=True, capture_output=True, check=False, env={"PYTHONDONTWRITEBYTECODE": "1"})
    try:
        source_receipt = json.loads(source_run.stdout)
    except json.JSONDecodeError:
        source_receipt = {}
    expected_errors = {f"source digest drift: {row['source_id']}" for row in plan["source_epoch"]["source_drift"]}
    check("MIG2-03-SOURCE-BLOCK-PRESERVED", source_receipt.get("status") == "BLOCK" and set(source_receipt.get("errors", [])) == expected_errors and source_receipt.get("material_digest") == plan["source_epoch"]["material_digest"], "current source validation is BLOCK only on the three recorded digest drifts; the plan does not bypass it")

    identity = plan["identity_model"]
    check("MIG2-04-SUBJECT-IDENTITY", identity["migration_subject"]["source_product_id"] == "CA2-PRODUCT-ONTOLOGY" and identity["work_receiver"]["product_ref"] == "CA2-PRODUCT-CRAFT/v1", "Ontology Product is the subject and Craft is only the work receiver")
    context_refs = [row["context_ref"] for row in identity["semantic_contexts"]]
    check("MIG2-05-CONTEXT-ORTHOGONALITY", context_refs == ["cal.context.governance/v3", "cal.context.ontology-lifecycle/v3"] and identity["planned_coordination_context"]["bounded_context_refs"] == context_refs, "the coordination carrier references the two independent v3 contexts explicitly")
    check("MIG2-06-CONTEXT-MAP-OWNERSHIP", identity["context_map"]["context_map_ref"] == "cal.context-map.governance-ontology-lifecycle/v2" and "cannot infer or duplicate" in identity["context_map"]["constraint"], "the Context Map remains the sole endpoint-relationship owner")

    layer_ids = [row["layer_id"] for row in plan["layers"]]
    swu_ids = [row["smallest_working_unit"] for row in plan["layers"]]
    check("MIG2-07-LAYERING", len(layer_ids) == 5 and len(set(layer_ids)) == 5 and len(set(swu_ids)) == 5 and layer_ids[0] == "L0-SOURCE-SEMANTIC-CLOSURE" and layer_ids[-1] == "L4-INTEGRATED-PRODUCT-CANDIDATE", "five decision layers progress from source closure to one integrated Product candidate")
    check("MIG2-08-SMALLEST-FIRST-UNIT", plan["distill"]["smallest_coherent_unit"] == "SWU-CML11-101-SOURCE-CLOSURE" and plan["work_plan"]["product_construction_frontier"] == "SWU-CML11-101-SOURCE-CLOSURE", "Distill and the work plan select the reversible source-closure unit first")
    check("MIG2-09-DISTILL-TRACE", plan["distill"]["mode"] == "standard" and len(plan["distill"]["rounds"]) == 2 and plan["distill"]["rounds"][0]["reconciliation"] == "reject" and plan["distill"]["rounds"][1]["reconciliation"] == "accept-with-L0-source-closure-first", "the Proposer/Balancer trace rejects capability-to-Product collapse and accepts the source-gated Product target")

    preference = plan["workflow_preferences"]
    check("MIG2-10-SINGLE-APPROVAL-BOUNDARY", preference["approval_mode"] == "single-final-product-boundary" and preference["approval_boundary"]["eligible_after_layer"] == "L4-INTEGRATED-PRODUCT-CANDIDATE" and len(preference["approval_boundary"]["not_granted"]) == 7, "one configurable Product approval boundary follows L4 and grants no later lifecycle authority")
    check("MIG2-11-CRAFT-NONMUTATION", plan["craft_intake_contract"]["status"] == "planned-not-written" and len(plan["craft_intake_contract"]["work_items"]) == 5 and "No Craft ledger mutation" in plan["craft_intake_contract"]["write_boundary"], "Craft receives a planned five-unit intake only; no ledger mutation is authorized")
    check("MIG2-12-SUCCESSOR-PRESERVATION", plan["subject_correction"]["supersedes_candidate_ref"].endswith("0001-craft-development-closure-v1/plan.json") and "Preserve candidate 0001" in plan["subject_correction"]["preservation_rule"], "the mis-scoped predecessor is superseded but preserved")

    dispatch_ok, dispatch_output = validate_dispatch(dispatch_file)
    check("MIG2-13-DISPATCH-SPEC", dispatch_ok, "dispatch-spec validator accepts the sequential no-subagent planning route" if dispatch_ok else dispatch_output[-600:])
    check("MIG2-14-DISPATCH-LINK", plan["dispatch_ref"] == DISPATCH_PATH.as_posix() and dispatch["intent"]["target_artifact"] == PLAN_PATH.as_posix(), "plan and dispatch reference each other through concrete paths")

    rendered = generator.projections(plan, dispatch)
    projections_exact = all((LAB_ROOT / path).is_file() and (LAB_ROOT / path).read_text() == content for path, content in rendered.items())
    deterministic = rendered == generator.projections(json.loads(canonical_json(plan)), json.loads(canonical_json(dispatch)))
    check("MIG2-15-GENERATED-PROJECTIONS", projections_exact, "all five human views equal their canonical generated projections")
    check("MIG2-16-DETERMINISM", deterministic, "projection generation is byte-deterministic")
    check("MIG2-17-NONAUTHORITY", plan["authority_effect"] == "none" and not plan["route"]["execution_candidate"] and dispatch["subagent_strategy"]["status"] == "none", "the package is non-executing, non-authoritative, and uses no delegated agents")

    result = "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL"
    blockers = [
        "CML11-B01: three source-selector digest drifts block Product copying until L0 semantic closure passes.",
        "CML11-B02: v3 contexts and Context Map v2 remain candidate-unadmitted; candidate coordination can be authored, but admitted-context conformance is not evaluable.",
        "CML11-B03: external Goal-package validation remains not evaluated and cannot support Goal achievement claims."
    ]
    receipt = {
        "schema_version": "cyberalchemy-lab-product-context-migration-validation/v1",
        "dispatch_id": dispatch["dispatch_id"],
        "status": result,
        "validation_result": result,
        "authority_effect": "none",
        "artifacts": {
            "plan_ref": PLAN_PATH.as_posix(),
            "plan_sha256": sha256_file(plan_file),
            "dispatch_ref": DISPATCH_PATH.as_posix(),
            "dispatch_sha256": sha256_file(dispatch_file),
            "human_projections": [path.as_posix() for path in rendered]
        },
        "source_status": source_receipt.get("status", "not_evaluable"),
        "summary": {"checks_passed": sum(row["result"] == "PASS" for row in checks), "checks_total": len(checks), "layers": len(plan["layers"]), "work_items": len(plan["craft_intake_contract"]["work_items"]), "source_drifts": len(plan["source_epoch"]["source_drift"])},
        "validation": checks,
        "blockers": blockers,
        "residue": "The next runnable construction unit is source semantic closure. Product identity, coordination, package copy, and integrated testing remain downstream and non-evaluable until their causal predecessors pass.",
        "claim_ceiling": "PASS proves only that the corrected migration plan is internally consistent, source-current at this planning epoch, dispatch-valid, orthogonal, deterministically projected, and governed by one final Product approval boundary. It does not make the blocked source package pass, mutate Craft, copy files, create or admit Product or Context artifacts, authorize implementation, approve the product, or authorize admission, activation, cutover, publication, release, deployment, or source retirement."
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
