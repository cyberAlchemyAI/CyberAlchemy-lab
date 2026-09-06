#!/usr/bin/env python3
"""Generate human projections from the canonical Ontology Product migration plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[2]
PLAN_DIR = Path("docs/migration-plans/0002-ontology-product-context-migration-v1")
PLAN_PATH = PLAN_DIR / "plan.json"
DISPATCH_PATH = PLAN_DIR / "dispatch.json"


def header(source: str) -> list[str]:
    return [f"<!-- Generated from {source}. Do not edit this projection. -->", ""]


def render_plan(plan: dict[str, Any]) -> str:
    identity = plan["identity_model"]
    lines = header("plan.json") + [
        "# Ontology Product and context migration plan",
        "",
        "## Outcome brief",
        "",
        "The migration subject is the **CyberAlchemy Ontology Product**. Governance and Ontology Lifecycle remain independent Bounded Contexts. Craft receives and coordinates the work; it is not the migration subject.",
        "",
        f"- Plan: `{plan['plan_id']}`",
        f"- State: `{plan['status']}`",
        f"- Current construction frontier: `{plan['work_plan']['product_construction_frontier']}`",
        f"- Current source validation: `{plan['source_epoch']['validator_status']}`",
        f"- Approval policy: `{plan['workflow_preferences']['approval_mode']}`",
        "",
        "## Boundary and next decision",
        "",
        "No Product or Context bytes should be migrated yet. The next bounded action is to author the L0 source-closure candidate for the three drifted selectors. After L0 passes, the sequence continues without intermediate approval requests until the integrated L4 candidate is ready for one product-approval decision.",
        "",
        "## Identity architecture",
        "",
        f"- Migrated Product: `{identity['migration_subject']['source_product_id']}` → `{identity['migration_subject']['destination_path']}`",
        f"- Work receiver: `{identity['work_receiver']['product_ref']}`",
        f"- Context Map: `{identity['context_map']['context_map_ref']}`",
        f"- Planned coordination carrier: `{identity['planned_coordination_context']['destination_path']}`",
        "- Bounded Contexts:",
    ]
    lines.extend(f"  - `{row['context_ref']}` — {row['role']}" for row in identity["semantic_contexts"])
    lines += ["", "## Source blocker", ""]
    for drift in plan["source_epoch"]["source_drift"]:
        lines.append(f"- `{drift['source_id']}` — `{drift['recorded_sha256']}` → `{drift['current_sha256']}`; owner `{drift['owner']}`")
    lines += ["", "## Migration layers", ""]
    for layer in plan["layers"]:
        lines += [
            f"### `{layer['layer_id']}` — {layer['name']}",
            "",
            f"- State: `{layer['state']}`",
            f"- Smallest unit: `{layer['smallest_working_unit']}`",
            f"- Decision unlocked: {layer['decision_unlocked']}",
            f"- Exit: {'; '.join(layer['exit_evidence'])}",
            "",
        ]
    lines += ["## Orthogonality", ""]
    lines.extend(f"- {rule}" for rule in plan["orthogonality_rules"])
    lines += ["", "## Approval boundary", "", plan["workflow_preferences"]["approval_boundary"]["decision"], "", "This approval grants Product approval only; it does not grant admission, activation, cutover, publication, release, deployment, or source deletion.", "", "## Claim ceiling", "", plan["claim_ceiling"], ""]
    return "\n".join(lines)


def render_layering(plan: dict[str, Any]) -> str:
    lines = header("plan.json") + ["# Implementation layering", "", "Each layer exists because it unlocks a distinct decision and reduces a different risk.", ""]
    for layer in plan["layers"]:
        lines += [f"## `{layer['layer_id']}`", "", f"**After this layer, we know:** {layer['decision_unlocked']}", "", f"- State: `{layer['state']}`", f"- Smallest working unit: `{layer['smallest_working_unit']}`", "- Included:", ""]
        lines.extend(f"  - {item}" for item in layer["included"])
        lines += ["", "- Deferred:", ""]
        lines.extend(f"  - {item}" for item in layer["deferred"])
        lines += ["", "- Exit evidence:", ""]
        lines.extend(f"  - {item}" for item in layer["exit_evidence"])
        lines.append("")
    return "\n".join(lines)


def render_work_pack(plan: dict[str, Any]) -> str:
    lines = header("plan.json") + [
        "# Product/context migration work pack",
        "",
        f"- Current frontier: `{plan['work_plan']['product_construction_frontier']}`",
        "- Execution designation: `non-executing-planning-candidate`",
        "- Internal gate behavior: continue after PASS; fail closed on a causal failure; do not request intermediate approvals.",
        "",
        "## Craft receiver contract",
        "",
        f"- Receiver: `{plan['craft_intake_contract']['receiver_product_ref']}`",
        f"- State: `{plan['craft_intake_contract']['status']}`",
        f"- Boundary: {plan['craft_intake_contract']['write_boundary']}",
        "",
        "## Product-construction sequence",
        "",
    ]
    for index, layer in enumerate(plan["layers"], 1):
        lines.append(f"{index}. `{layer['smallest_working_unit']}` — {layer['name']} (`{layer['state']}`)")
    lines += ["", "## Runnable now", ""]
    lines.extend(f"- {item}" for item in plan["work_plan"]["runnable_now"])
    lines += ["", "## Causal blockers", ""]
    for item in plan["work_plan"]["causal_blockers"]:
        lines.append(f"- `{item['blocker_id']}` affects `{item['affects']}` — {item['condition']} Owner: `{item['owner']}`.")
    lines += ["", "## Operational support", ""]
    for item in plan["work_plan"]["operational_support"]:
        lines.append(f"- {item['task']} — owner `{item['owner']}`; affects `{item['affected_stage']}`; `{item['blocking_posture']}`.")
    lines += ["", "## Closeout", ""]
    lines.extend(f"- {item}" for item in plan["closeout_obligations"])
    lines += ["", "## Claim ceiling", "", plan["claim_ceiling"], ""]
    return "\n".join(lines)


def render_distill(plan: dict[str, Any]) -> str:
    distill = plan["distill"]
    lines = header("plan.json") + [
        "# Distill result",
        "",
        f"- Mode: `{distill['mode']}`",
        f"- Verdict: `{distill['verdict']}`",
        f"- Smallest coherent unit: `{distill['smallest_coherent_unit']}`",
        "",
        "## Proposer/Balancer trace",
        "",
    ]
    for row in distill["rounds"]:
        lines += [f"### Round {row['round']}", "", f"- Proposer: {row['proposer']}", f"- Balancer (`{row['balancer_objection_category']}`): {row['balancer']}", f"- Reconciliation: `{row['reconciliation']}`", ""]
    lines += ["## Recomposition proof", "", distill["recomposition_proof"], "", "## Deferred complexity", "", distill["deferred_complexity"], ""]
    return "\n".join(lines)


def render_dispatch(dispatch: dict[str, Any]) -> str:
    lines = header("dispatch.json") + [
        "# Migration planning dispatch",
        "",
        f"- Dispatch: `{dispatch['dispatch_id']}`",
        f"- Mode: `{dispatch['mode']}`",
        f"- Subagents: `{dispatch['subagent_strategy']['status']}`",
        "- Authority: planning and validation only",
        "",
        "## Steps",
        "",
    ]
    for index, step in enumerate(dispatch["steps"], 1):
        lines.append(f"{index}. `{step['step_id']}` — {step['name']} via `{step['capability_ref']}`")
    lines += ["", "## Gates", ""]
    for gate in dispatch["gates"]:
        lines.append(f"- `{gate['gate_id']}` — {gate['condition']} On failure: `{gate['on_fail']}`.")
    lines += ["", "## Promotion guardrails", ""]
    lines.extend(f"- {rule}" for rule in dispatch["promotion_guardrails"])
    lines.append("")
    return "\n".join(lines)


def projections(plan: dict[str, Any], dispatch: dict[str, Any]) -> dict[Path, str]:
    return {
        PLAN_DIR / "PLAN.md": render_plan(plan),
        PLAN_DIR / "LAYERING.md": render_layering(plan),
        PLAN_DIR / "WORK-PACK.md": render_work_pack(plan),
        PLAN_DIR / "DISTILL.md": render_distill(plan),
        PLAN_DIR / "DISPATCH.md": render_dispatch(dispatch),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    plan = json.loads((LAB_ROOT / PLAN_PATH).read_text())
    dispatch = json.loads((LAB_ROOT / DISPATCH_PATH).read_text())
    failures: list[str] = []
    for relative, content in projections(plan, dispatch).items():
        path = LAB_ROOT / relative
        if args.check:
            if not path.is_file() or path.read_text() != content:
                failures.append(relative.as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    print(json.dumps({"result": "PASS" if not failures else "FAIL", "mode": "check" if args.check else "generate", "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
