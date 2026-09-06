#!/usr/bin/env python3
"""Render deterministic Markdown views from continuous-plan.json."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "continuous-plan.json"


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_plan(plan: dict) -> str:
    waves = plan["waves"]
    lines = [
        f"# {plan['title']}",
        "",
        f"Plan ID: `{plan['plan_id']}`  ",
        f"Status: `{plan['status']}`  ",
        f"Execution authority: `{plan['execution_authority']}`",
        "",
        "## Outcome",
        "",
        plan["objective"],
        "",
        "This is a non-executing successor plan. It preserves the current thin deterministic witness and starts at the unresolved governed-node architecture decision. A future terminal PASS proves only a validated candidate for one frozen epoch.",
        "",
        "## Continuous path",
        "",
        "```text",
        "W0 architecture selection",
        " -> W1 definitions and schemas",
        " -> W2 Product Capability and business ontology",
        " -> W3 authored DomainSpec and event-source contract",
        " -> W4 deterministic graph and system ontology",
        " -> W5 Rust reducer and projections",
        " -> W6 exact binding and non-vacuous conformance",
        " -> W7 isolated migration rehearsal",
        " -> W8 aggregate immutable-epoch validation",
        "```",
        "",
        "Each wave has a local gate. W8 joins all evidence; it does not postpone basic validation or grant acceptance.",
        "",
        "## Preserved evidence",
        "",
        bullets(plan["continuity"]["preserved_evidence"]),
        "",
        "## Open blockers",
        "",
    ]
    for blocker in plan["blockers"]:
        lines.extend([
            f"- `{blocker['id']}` blocks `{blocker['blocks_wave']}`: {blocker['reason']} Resolution: {blocker['resolution']}",
        ])
    lines.extend(["", "## Waves", "", "| Wave | Layer | Outcome | Gate owner | Current state |", "|---|---|---|---|---|"])
    for wave in waves:
        lines.append(f"| `{wave['id']}` | `{wave['layer']}` | {wave['objective']} | {wave['gate']['owner']} | `{wave['status']}` |")
    lines.extend(["", "## Final validation", "", plan["final_validation"]["pass_condition"], "", "Required checks:", ""])
    validation_by_id = {v["id"]: v for v in plan["validations"]}
    for validation_id in plan["final_validation"]["required_validation_ids"]:
        validation = validation_by_id[validation_id]
        lines.append(f"- `{validation_id}` — {validation['expected']}")
    lines.extend([
        "",
        "## Execution boundary",
        "",
        f"Next route: `{plan['execution_entry']['next_route']}`. Task Session allowed: `{str(plan['execution_entry']['task_session_allowed']).lower()}`. {plan['execution_entry']['reason']}",
        "",
        "Claim ceiling:",
        "",
        bullets(plan["claim_ceiling"]),
        "",
    ])
    return "\n".join(lines)


def render_layering(plan: dict) -> str:
    lines = [
        "# Implementation layering",
        "",
        f"Source: `{plan['plan_id']}` / `continuous-plan.json`",
        "",
        "The layers are dependency and authority boundaries, not code folders. A later layer is not evaluable until its predecessors have current passing receipts.",
        "",
    ]
    wave_by_id = {wave["id"]: wave for wave in plan["waves"]}
    for layer in plan["layers"]:
        lines.extend([
            f"## {layer['id']} — {layer['name']}",
            "",
            f"Decision question: {layer['decision_question']}",
            "",
        ])
        for wave_id in layer["waves"]:
            wave = wave_by_id[wave_id]
            lines.append(f"- `{wave_id}` {wave['name']}: {wave['objective']}")
        lines.append("")
    lines.extend([
        "## Cross-layer invariants",
        "",
        "- Canonical append-only events are the replay source; snapshots and projections are disposable read models.",
        "- Each node or relation state is calculated from the latest valid event in its own subject stream.",
        "- Semantic and governance streams remain distinct and join only through exact event identity, digest, and commit position.",
        "- Product Capability and capability-local business ontology precede DomainSpec source; compiled graphs precede implementation binding.",
        "- Every receipt binds one immutable source epoch. Drift reopens the affected gate.",
        "- Migration rehearsal follows accepted conformance and never implies cutover.",
        "",
        "## Layer promotion rule",
        "",
        "Promotion to the next layer requires every gate in the current layer to PASS. A block yields explicit residue and makes dependent checks `not_evaluable`; it cannot be bypassed by a later focused PASS.",
        "",
    ])
    return "\n".join(lines)


def render_work_pack(plan: dict) -> str:
    lines = [
        "# Continuous work pack",
        "",
        f"Work Pack: `{plan['plan_id']}`  ",
        f"Designation: `{plan['status']}`  ",
        "Execution entry: blocked",
        "",
        "This Work Pack is descriptive until W0 and the admitted Design prerequisites close. Each SWU has one primary behavior, an explicit owner/write scope, done criteria, and validation bindings.",
        "",
    ]
    validation_by_id = {v["id"]: v for v in plan["validations"]}
    for wave in plan["waves"]:
        deps = ", ".join(wave["depends_on"]) or "none"
        lines.extend([
            f"## {wave['id']} — {wave['name']}",
            "",
            f"Layer: `{wave['layer']}`  ",
            f"Depends on: `{deps}`  ",
            f"Current state: `{wave['status']}`",
            "",
            wave["objective"],
            "",
        ])
        for swu in wave["swus"]:
            lines.extend([
                f"### {swu['id']}",
                "",
                f"Primary behavior: {swu['primary_behavior']}",
                "",
                f"Owner: {swu['owner']}",
                "",
                "Write scope:",
                "",
                bullets([f"`{path}`" for path in swu["write_scope"]]),
                "",
                "Done criteria:",
                "",
                bullets(swu["done_criteria"]),
                "",
                "Validation:",
                "",
            ])
            for validation_id in swu["validation_ids"]:
                lines.append(f"- `{validation_id}` — {validation_by_id[validation_id]['expected']}")
            lines.extend(["", f"Split analysis: {swu['split_analysis']}", ""])
        lines.extend([
            f"Gate `{wave['gate']['id']}` — owner: {wave['gate']['owner']}",
            "",
            f"Pass condition: {wave['gate']['pass_condition']}",
            "",
            f"Failure action: `{wave['gate']['on_fail']}`",
            "",
        ])
    lines.extend([
        "## Terminal claim ceiling",
        "",
        bullets(plan["claim_ceiling"]),
        "",
    ])
    return "\n".join(lines)


def rendered(plan: dict) -> dict[str, str]:
    return {
        "PLAN.md": render_plan(plan),
        "IMPLEMENTATION-LAYERING.md": render_layering(plan),
        "WORK-PACK.md": render_work_pack(plan),
    }


def main() -> int:
    plan = json.loads(SOURCE.read_text(encoding="utf-8"))
    for name, content in rendered(plan).items():
        (ROOT / name).write_text(content, encoding="utf-8")
    print("RENDER=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
