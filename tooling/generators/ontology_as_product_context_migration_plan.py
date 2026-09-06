#!/usr/bin/env python3
"""Generate human projections for the Ontology-as-a-Product migration successor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = Path("docs/migration-plans/0003-ontology-as-product-context-migration-v1")


def head(source: str) -> list[str]:
    return [f"<!-- Generated from {source}. Do not edit. -->", ""]


def render_semantic(model: dict[str, Any]) -> str:
    subjects = {row["subject_id"]: row for row in model["subjects"]}
    lines = head("semantic-model.json") + [
        "# Ontology-as-a-Product semantic model",
        "",
        "```text",
        "Product: CA2-PRODUCT-ONTOLOGY",
        "  includes capability: CA2-CAP-ONTOLOGY-TYPED-MEANING",
        "    produces output: CA2-OUTPUT-ONTOLOGY-PACKAGE",
        "",
        "Product Ontology: cav2.ontology-product",
        "  represents: CA2-PRODUCT-ONTOLOGY",
        "",
        "Craft: receives migration work only",
        "```",
        "",
        "## Subjects",
        "",
    ]
    for subject in model["subjects"]:
        lines += [f"### `{subject['subject_id']}`", "", f"- Role: `{subject['role']}`", f"- Kind: `{subject['subject_kind_ref']}`", f"- Meaning: {subject['statement']}", ""]
    lines += ["## Generated labels", ""]
    for label in model["derived_labels"]:
        lines += [f"### {label['label']}", "", f"- Derivation: {label['derivation']}", f"- Purpose: {label['purpose']}", f"- Canonical axis: `{str(label['canonical_axis']).lower()}`", f"- Forbidden: {label['forbidden_use']}", ""]
    lines += ["## Non-collapse invariants", ""]
    lines.extend(f"- `{item}`" for item in model["non_collapse_invariants"])
    lines += ["", "## Practical distinction", "", f"- Product: {subjects['CA2-PRODUCT-ONTOLOGY']['statement']}", f"- Product Ontology: {subjects['cav2.ontology-product']['statement']}", f"- Product output: {subjects['CA2-OUTPUT-ONTOLOGY-PACKAGE']['statement']}", "", "## Claim ceiling", "", model["claim_ceiling"], ""]
    return "\n".join(lines)


def render_plan(plan: dict[str, Any]) -> str:
    architecture = plan["product_architecture"]
    lines = head("plan.json") + [
        "# Ontology-as-a-Product migration",
        "",
        "## Outcome brief",
        "",
        "The migration now treats the Ontology Product as a Product whose core value-bearing output is a governed ontology package. Its Product Ontology is a separate semantic scaffold that describes the Product. Craft receives the work; contexts and runtimes support the Product without becoming it.",
        "",
        f"- Plan: `{plan['plan_id']}`",
        f"- Product: `{architecture['product']['product_ref']}`",
        f"- Product Ontology: `{architecture['product_ontology']['ontology_ref']}`",
        f"- Core output: `{architecture['core_output']['output_ref']}`",
        f"- Current frontier: `{plan['two_lane_work']['product_construction_frontier']}`",
        "",
        "## Boundary and next decision",
        "",
        "The semantic correction is implemented and validated in this planning epoch. The next construction action is source closure for the three drifted Product Ontology dependencies, followed by the Product identity/scaffold migration. No approval is requested until the complete L4 Product candidate is tested.",
        "",
        "## Architecture",
        "",
        f"- Product meaning: {architecture['product']['meaning']}",
        f"- Product Ontology role: {architecture['product_ontology']['role']}",
        f"- Core output role: {architecture['core_output']['role']}",
        f"- Runtime boundary: {architecture['runtime_boundary']}",
        "",
        "## Layers",
        "",
    ]
    for layer in plan["layers"]:
        lines += [f"### `{layer['layer_id']}` — {layer['name']}", "", f"- State: `{layer['state']}`", f"- SWU: `{layer['swu_id']}`", f"- Decision: {layer['decision_unlocked']}", f"- Output: {layer['output']}", ""]
    boundary = plan["workflow_preferences"]["approval_boundary"]
    lines += ["## Approval", "", f"- Eligible after: `{boundary['eligible_after_layer']}`", f"- Decision: {boundary['decision']}", f"- Effect: `{boundary['effect_if_approved']}`", "", "## Claim ceiling", "", plan["claim_ceiling"], ""]
    return "\n".join(lines)


def render_layering(plan: dict[str, Any]) -> str:
    lines = head("plan.json") + ["# Implementation layering", ""]
    for layer in plan["layers"]:
        lines += [f"## `{layer['layer_id']}`", "", f"**After this layer, we know:** {layer['decision_unlocked']}", "", f"- State: `{layer['state']}`", f"- Smallest unit: `{layer['swu_id']}`", f"- Concrete output: {layer['output']}", "- Exit evidence:", ""]
        lines.extend(f"  - {item}" for item in layer["exit_evidence"])
        lines.append("")
    return "\n".join(lines)


def render_work_pack(plan: dict[str, Any]) -> str:
    work = plan["two_lane_work"]
    lines = head("plan.json") + ["# Ontology-as-a-Product work pack", "", f"- Construction frontier: `{work['product_construction_frontier']}`", "- Execution designation: `non-executing-planning-candidate`", "- Internal behavior: continue on PASS, fail closed on a causal blocker, request approval only after L4.", "", "## Product construction", ""]
    for index, layer in enumerate(plan["layers"], 1):
        lines.append(f"{index}. `{layer['swu_id']}` — {layer['name']} (`{layer['state']}`)")
    lines += ["", "## Runnable now", ""]
    lines.extend(f"- {item}" for item in work["runnable_product_work"])
    lines += ["", "## Causal blockers", ""]
    for blocker in work["causal_blockers"]:
        lines.append(f"- `{blocker['blocker_id']}` affects `{blocker['affected_stage']}` — {blocker['condition']} Owner: `{blocker['owner']}`.")
    lines += ["", "## Operational support", ""]
    for item in work["operational_support"]:
        lines.append(f"- {item['task']} — owner `{item['owner']}`; affects `{item['affected_stage']}`; `{item['blocking_posture']}`.")
    lines += ["", "## Craft intake", "", f"- State: `{plan['craft_intake']['status']}`", f"- Receiver: `{plan['craft_intake']['receiver_ref']}`", f"- Boundary: {plan['craft_intake']['boundary']}", ""]
    return "\n".join(lines)


def render_definitions(plan: dict[str, Any]) -> str:
    audit = plan["definitions_governance"]
    lines = head("plan.json") + ["# Definitions governance audit", "", "- Definitions updated: `none`", "- Definition voices complete: `yes` for the two selected canonical bindings", "- Index synced: `not applicable`; no Definition was changed", f"- Drift found: `{str(audit['drift_found']).lower()}`", f"- Undefined critical terms: `{len(audit['undefined_critical_terms'])}`", f"- Conflicting consumers: `{len(audit['conflicting_consumer_refs'])}`", f"- Canonical source: `{audit['canonical_source']}`", "", "## Decision", "", audit["decision"], "", "## Remediation", "", audit["remediation"], ""]
    return "\n".join(lines)


def render_dispatch(dispatch: dict[str, Any]) -> str:
    lines = head("dispatch.json") + ["# Successor authoring dispatch", "", f"- Dispatch: `{dispatch['dispatch_id']}`", f"- Mode: `{dispatch['mode']}`", f"- Subagents: `{dispatch['subagent_strategy']['status']}`", "", "## Steps", ""]
    for index, step in enumerate(dispatch["steps"], 1):
        lines.append(f"{index}. `{step['step_id']}` — {step['name']} via `{step['capability_ref']}`")
    lines += ["", "## Gates", ""]
    for gate in dispatch["gates"]:
        lines.append(f"- `{gate['gate_id']}` — {gate['condition']} On failure: `{gate['on_fail']}`.")
    lines += ["", "## Guardrails", ""]
    lines.extend(f"- {item}" for item in dispatch["promotion_guardrails"])
    lines.append("")
    return "\n".join(lines)


def projections(plan: dict[str, Any], model: dict[str, Any], dispatch: dict[str, Any]) -> dict[Path, str]:
    return {
        BASE / "PLAN.md": render_plan(plan),
        BASE / "SEMANTIC-MODEL.md": render_semantic(model),
        BASE / "LAYERING.md": render_layering(plan),
        BASE / "WORK-PACK.md": render_work_pack(plan),
        BASE / "DEFINITIONS-AUDIT.md": render_definitions(plan),
        BASE / "DISPATCH.md": render_dispatch(dispatch),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    plan = json.loads((ROOT / BASE / "plan.json").read_text())
    model = json.loads((ROOT / BASE / "semantic-model.json").read_text())
    dispatch = json.loads((ROOT / BASE / "dispatch.json").read_text())
    failures: list[str] = []
    for relative, content in projections(plan, model, dispatch).items():
        path = ROOT / relative
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
