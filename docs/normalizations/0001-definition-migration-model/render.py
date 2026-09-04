#!/usr/bin/env python3
"""Render the human projection of the NORMALIZE-01 machine record."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "normalization.json"
OUTPUT = ROOT / "NORMALIZATION.md"


def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(headers: list[str], rows: list[list[object]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    lines.extend("| " + " | ".join(esc(cell) for cell in row) + " |" for row in rows)
    return lines


def section(lines: list[str], title: str) -> None:
    lines.extend(["", f"## {title}", ""])


def render(data: dict) -> str:
    counts = data["accepted_outcome_counts"]
    lines = [
        "<!-- GENERATED FILE: edit normalization.json and run render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Human projection generated from `normalization.json`; it is not canonical.",
        "",
        f"- Normalization: `{data['normalization_id']}`",
        f"- Status: `{data['status']}`",
        f"- Decision posture: `{data['decision_posture']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Target effect: {data['scope']['target_effect']}",
    ]

    section(lines, "Outcome")
    lines.extend(table(
        ["Revise", "Reclassify", "Split", "Collapse", "Drop", "Active", "Withdrawn preserved"],
        [[counts["revise"], counts["reclassify"], counts["split"], counts["collapse"],
          counts["drop"], counts["active_total"], counts["withdrawn_preserved"]]],
    ))

    section(lines, "Normalization rules")
    lines.extend(f"{i}. {rule}" for i, rule in enumerate(data["normalization_rules"], 1))

    section(lines, "Distill trace")
    distill = data["distill"]
    lines.extend([
        f"Optimization goal: {distill['optimization_goal']}",
        "",
        f"Smallest coherent unit: **{distill['smallest_coherent_unit']['name']}** — "
        f"{distill['smallest_coherent_unit']['responsibility']}",
        "",
    ])
    for rnd in distill["rounds"]:
        lines.extend([
            f"### Round {rnd['round']}", "",
            f"- Proposal: {rnd['proposer_claim']}",
            f"- Objection ({rnd['balancer_objection_category']}): {rnd['balancer_objection']}",
            f"- Reconciliation: {rnd['reconciliation']}", "",
        ])
    lines.append(f"Verdict: `{distill['verdict']}`")

    section(lines, "Owner scopes")
    lines.extend(table(
        ["ID", "Name", "DDD bounded-context status", "Boundary note"],
        [[x["owner_scope_id"], x["name"], x["ddd_bounded_context_status"], x["note"]]
         for x in data["owner_scopes"]],
    ))

    section(lines, "Artifact types")
    lines.extend(table(
        ["ID", "Name", "Family", "Distinct validation purpose"],
        [[x["artifact_type_id"], x["name"], x["family"], x["distinct_validation_purpose"]]
         for x in data["artifact_types"]],
    ))

    section(lines, "Profiles")
    lines.extend(table(
        ["ID", "Name", "Artifact type"],
        [[x["profile_id"], x["name"], x["artifact_type_ref"]] for x in data["profiles"]],
    ))

    section(lines, "Typed relation kinds")
    lines.extend(table(
        ["ID", "Direction", "Inverse projection"],
        [[x["relation_kind_id"], x["direction"], x["inverse_projection"]]
         for x in data["relation_kinds"]],
    ))

    section(lines, "Semantic concepts")
    lines.extend(table(
        ["ID", "Term", "Kind", "Carrier", "Owner scope"],
        [[x["concept_id"], x["term"], x["semantic_kind"], x["carrier_ref"], x["owner_scope"]]
         for x in data["semantic_concepts"]],
    ))

    section(lines, "Generated surfaces")
    lines.extend(table(
        ["ID", "Name", "Canonical inputs"],
        [[x["derived_surface_id"], x["name"], x["source"]] for x in data["derived_surfaces"]],
    ))

    section(lines, "Migration decisions")
    lines.extend(table(
        ["Legacy ID", "Legacy term", "Decision", "Normalized targets"],
        [[x["legacy_id"], x["legacy_term"], x["decision"], ", ".join(x["targets"])]
         for x in data["migration_decisions"]],
    ))

    section(lines, "Withdrawn identifiers")
    lines.extend(table(
        ["Legacy ID", "Preserved successor"],
        [[x["legacy_id"], x["successor_id"]] for x in data["withdrawn_ids"]],
    ))

    section(lines, "Dependency order")
    lines.extend(table(
        ["Wave", "Name", "Requires", "Outputs", "Effect"],
        [[x["wave"], x["name"], ", ".join(x["requires"]), ", ".join(x["outputs"]), x["effect"]]
         for x in data["dependency_order"]],
    ))

    section(lines, "Open owner decisions")
    for item in data["unresolved_decisions"]:
        lines.extend([
            f"### {item['decision_id']}", "",
            item["question"], "",
            f"Blocks: {item['blocking_for']}", "",
            f"Recommended default: {item['recommended_default']}", "",
        ])

    section(lines, "Claim ceiling")
    lines.append(data["claim_ceiling"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    OUTPUT.write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
