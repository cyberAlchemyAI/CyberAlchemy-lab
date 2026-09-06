#!/usr/bin/env python3
"""Generate human projections for the canonical Craft development migration plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = Path("docs/migration-plans/0001-craft-development-closure-v1/plan.json")
OUTPUTS = {
    "plan": PLAN_PATH.with_name("PLAN.md"),
    "layering": PLAN_PATH.with_name("LAYERING.md"),
    "work_pack": PLAN_PATH.with_name("WORK-PACK.md"),
    "distill": PLAN_PATH.with_name("DISTILL.md"),
}


def generated_header(view: str) -> list[str]:
    return [
        f"<!-- Generated {view} projection from plan.json by tooling/generators/craft_development_migration_plan.py. Do not edit. -->",
        "",
    ]


def render_plan(plan: dict[str, Any]) -> str:
    lines = generated_header("Plan") + [
        f"# {plan['title']}",
        "",
        f"- Plan: `{plan['plan_id']}`",
        f"- Status: `{plan['status']}`",
        f"- Authority effect: `{plan['authority_effect']}`",
        f"- Current frontier: `{plan['work_plan']['product_construction_frontier']}`",
        "",
        "## Outcome",
        "",
        plan["objective"],
        "",
        "The first migration unit is an eleven-file historical baseline bridge. It is deliberately not the current baseline: twenty-four current source members differ from baseline v2 and require a successor candidate.",
        "",
        "## Boundary and next decision",
        "",
        f"- Plan capability: `{plan['plan_capability']['artifact_authored']}` — {plan['plan_capability']['reason']}",
        "- No development file is copied by this plan.",
        "- Next bounded action: explicitly route implementation of `SWU-CML11-001-HISTORICAL-BASELINE-BRIDGE` after refreshing its eleven source hashes.",
        "",
        "## Construction rule",
        "",
        plan["construction_rule"],
        "",
        "## Migration layers",
        "",
    ]
    for layer in plan["layers"]:
        lines.extend([
            f"### `{layer['layer_id']}` — {layer['name']}",
            "",
            f"- State: `{layer['state']}`",
            f"- Decision: {layer['decision_question']}",
            f"- Minimum unit: {layer['minimum_working_unit']}",
            f"- Exit: {'; '.join(layer['exit_evidence'])}",
            f"- Promotion: {layer['promotion_decision']}",
            "",
        ])
    preference = plan["workflow_preferences"]
    boundary = preference["approval_boundary"]
    lines.extend([
        "## Approval boundary",
        "",
        f"- Mode: `{preference['approval_mode']}`",
        f"- Internal gates: `{preference['internal_wave_behavior']}`",
        f"- Eligible after: `{boundary['eligible_after_layer']}`",
        f"- Decision: `{boundary['decision']}`",
        f"- Effect: `{boundary['effect_if_approved']}`",
        f"- Later authority: `{boundary['later_authority_effects']}`",
        "",
        "## Two-lane work plan",
        "",
        f"- Product frontier: `{plan['work_plan']['product_construction_frontier']}`",
        f"- Causal construction blockers: `{len(plan['work_plan']['causal_construction_blockers'])}`",
        "- Runnable product work:",
        "",
    ])
    lines.extend(f"  - {item}" for item in plan["work_plan"]["runnable_product_work"])
    lines.extend(["", "Operational support:", ""])
    for item in plan["work_plan"]["operational_support"]:
        affected = item["affected_layer"] or "no construction stage"
        lines.append(f"- `{item['task']}` — owner `{item['owner']}`; affects `{affected}`; posture `{item['blocking_posture']}`")
    lines.extend(["", "## Claim ceiling", "", plan["claim_ceiling"], ""])
    return "\n".join(lines)


def render_layering(plan: dict[str, Any]) -> str:
    lines = generated_header("Implementation Layering") + [
        "# Craft development migration implementation layering",
        "",
        f"- Target: `{plan['plan_id']}`",
        f"- Layer count: `{len(plan['layers'])}`",
        "- Recommended next layer: `L0-HISTORICAL-BASELINE-BRIDGE`",
        "- Boundary heuristic: decision unlocked + visible outcome + risk reduced versus implementation + verification + coordination cost.",
        "",
    ]
    for layer in plan["layers"]:
        lines.extend([
            f"## `{layer['layer_id']}` — {layer['name']}",
            "",
            f"**After this layer, we know whether:** {layer['decision_question'].removeprefix('After this layer, we know whether ').rstrip('.')}",
            "",
            f"- State: `{layer['state']}`",
            f"- Minimum working unit: {layer['minimum_working_unit']}",
            f"- Operator-visible outcome: {layer['operator_visible_outcome']}",
            f"- Risk reduced: {layer['risk_reduced']}",
            f"- Main costs: {'; '.join(layer['cost_drivers'])}",
            f"- Promotion decision: {layer['promotion_decision']}",
            "",
            "Included:",
            "",
        ])
        lines.extend(f"- {item}" for item in layer["included"])
        lines.extend(["", "Deferred:", ""])
        lines.extend(f"- {item}" for item in layer["deferred"])
        lines.extend(["", "Exit evidence:", ""])
        lines.extend(f"- {item}" for item in layer["exit_evidence"])
        lines.extend(["", "Non-regression:", ""])
        lines.extend(f"- {item}" for item in layer["non_regression"])
        lines.append("")
    return "\n".join(lines)


def render_work_pack(plan: dict[str, Any]) -> str:
    validations = {item["validation_id"]: item for item in plan["validation_obligations"]}
    swus = {item["swu_id"]: item for item in plan["swus"]}
    details = {item["task_id"]: item for item in plan["implementation_details"]}
    lines = generated_header("Work Pack") + [
        "# Craft development closure work pack",
        "",
        f"- Plan: `{plan['plan_id']}`",
        f"- Execution designation: `{'execution-candidate' if plan['plan_capability']['execution_candidate'] else 'non-executing-planning-candidate'}`",
        f"- Current frontier: `{plan['work_plan']['product_construction_frontier']}`",
        "- Internal behavior: continue on PASS and fail closed on a real failure; no intermediate approval requests.",
        "",
        "## Exact L0 allowlist",
        "",
    ]
    for entry in plan["baseline_bridge"]["entries"]:
        lines.append(f"- `{entry['source_path']}` → `{entry['destination_path']}` (`sha256:{entry['sha256']}`)")
    lines.append("")
    for task in plan["tasks"]:
        lines.extend([
            f"## `{task['task_id']}` — {task['title']}",
            "",
            f"- Owner: `{task['owner']}`",
            f"- Lane: `{task['lane']}`",
            f"- Status: `{task['status']}`",
            f"- Next action: {task['next_action']}",
            "",
        ])
        for swu_id in task["swu_ids"]:
            swu = swus[swu_id]
            lines.extend([
                f"### `{swu_id}`",
                "",
                f"- Primary behavior: {swu['primary_behavior']}",
                f"- Split analysis: {swu['split_analysis']}",
                f"- Acceptance boundary: {swu['acceptance_boundary']}",
                "- Write scope:",
                "",
            ])
            lines.extend(f"  - `{item}`" for item in swu["write_scope"])
            lines.append("")
        detail = details[task["task_id"]]
        lines.extend(["Implementation rules:", ""])
        lines.extend(f"{index}. {rule}" for index, rule in enumerate(detail["ordered_rules"], start=1))
        lines.extend(["", f"Rollback: {detail['rollback_rule']}", "", "Validations:", ""])
        for validation_id in task["validation_ids"]:
            validation = validations[validation_id]
            lines.append(f"- `{validation_id}` — `{validation['command']}` → {validation['expected_result']}")
        lines.append("")
    lines.extend(["## Closeout obligations", ""])
    lines.extend(f"- {item}" for item in plan["closeout_obligations"])
    lines.extend(["", "## Claim ceiling", "", plan["claim_ceiling"], ""])
    return "\n".join(lines)


def render_distill(plan: dict[str, Any]) -> str:
    distill = plan["distill"]
    lines = generated_header("Distill") + [
        "# Distill result — Craft development migration",
        "",
        f"- Target context: `{plan['plan_id']}`",
        "- Objective: select the smallest coherent migration unit that preserves development closure without importing stale authority or active unfinished work.",
        f"- Mode: `{distill['mode']}`",
        f"- Recursive rounds: `{len(distill['rounds'])}/{distill['budget']['recursive_rounds']}`",
        f"- Verdict: `{distill['verdict']}`",
        f"- Current smallest coherent unit: `{distill['smallest_coherent_unit']}`",
        "",
        "## Role conversation trace",
        "",
    ]
    for row in distill["rounds"]:
        lines.extend([
            f"### Round {row['round']}",
            "",
            f"- Proposer: {row['proposer_claim']}",
            f"- Evidence/assumption: {row['evidence_or_assumption']}",
            f"- Balancer objection (`{row['balancer_objection_category']}`): {row['balancer_objection']}",
            f"- Reconciliation: `{row['reconciliation']}`",
            "",
        ])
    lines.extend([
        "## Closure and recomposition",
        "",
        distill["recomposition_proof"],
        "",
        f"- Evolution profile: {distill['evolution_profile']}",
        f"- Deferred complexity: {distill['deferred_complexity']}",
        f"- Premortem: {distill['premortem']}",
        f"- Frame expiry: {distill['frame_expiry']}",
        f"- Evidence emission: `{distill['evidence_emission']}`",
        f"- Telemetry: `{distill['telemetry']}`",
        "- Next route: owner review, then `CA2-ROUTE-IMPLEMENT` for the exact L0 SWU.",
        "",
    ])
    return "\n".join(lines)


def projections(plan: dict[str, Any]) -> dict[Path, str]:
    return {
        OUTPUTS["plan"]: render_plan(plan),
        OUTPUTS["layering"]: render_layering(plan),
        OUTPUTS["work_pack"]: render_work_pack(plan),
        OUTPUTS["distill"]: render_distill(plan),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    plan = json.loads((LAB_ROOT / PLAN_PATH).read_text())
    failures: list[str] = []
    for relative, text in projections(plan).items():
        path = LAB_ROOT / relative
        data = text.encode()
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                failures.append(relative.as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists() or path.read_bytes() != data:
                path.write_bytes(data)
    print(json.dumps({"result": "PASS" if not failures else "FAIL", "mode": "check" if args.check else "generate", "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
