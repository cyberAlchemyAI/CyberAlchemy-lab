#!/usr/bin/env python3
"""Render deterministic human views for the governed-node Definition Pack."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_pack(pack: dict, handled: dict, semantics: dict, drift: dict) -> str:
    records = handled["records"]
    lines = [
        "# Governed Ontology Node Definition Pack",
        "",
        f"Pack: `{pack['pack_id']}`",
        "",
        f"Status: `{pack['status']}`",
        "",
        f"Authority effect: `{pack['authority_effect']}`",
        "",
        "## Outcome",
        "",
        pack["goal"],
        "",
        "This pack defines the candidate meaning that executable node, relation, governance, challenge, exact-reference, and context-projection schemas must preserve. It does not implement those schemas.",
        "",
        "## Stable model",
        "",
        "```text",
        "semantic subject events -> OntologySemanticState",
        "governance events --exact event id + digest + cursor--> OntologyGovernanceState",
        "identity + semantic state + governance state -> GovernedOntologyNodeView",
        "ContextSelector + governed views -> ContextProjection",
        "```",
        "",
        "Canonical events remain the replay source. Nodes, snapshots, indexes, governed views, and context projections are calculated read models.",
        "",
        "## Confidence-axis correction",
        "",
        "The source plan used `semantic confidence` and `governance confidence`. Those phrases are rejected aliases because they hide the selected `CAV2-D23` separation:",
        "",
        "- `evidence_confidence` states how strongly current evidence supports one exact semantic claim epoch.",
        "- `commitment_confidence` states how strongly the responsible owner is prepared to rely on that epoch.",
        "- `evidence_strength` assesses one evidence item's support under declared conditions. It informs evidence confidence but is not another confidence axis.",
        "",
        "## Definition registry",
        "",
        "| ID | Term | Disposition | Plain-language voice |",
        "|---|---|---|---|",
    ]
    for record in records:
        plain = record["definition"]["plain_language_voice"].replace("|", "\\|")
        lines.append(f"| `{record['concept_id']}` | {record['term']} | `{record['current_disposition']}` | {plain} |")
    lines.extend(["", "## Definition voices", ""])
    for record in records:
        definition = record["definition"]
        lines.extend([
            f"### {record['term']} (`{record['concept_id']}`)",
            "",
            f"Normative: {definition['normative_voice']}",
            "",
            f"Formal: `{definition['formal_voice']}`",
            "",
            f"Operational: {definition['operational_interpretation']}",
            "",
            f"Plain language: {definition['plain_language_voice']}",
            "",
            f"CyberAlchemy Lab context: {definition['domain_context_voice']}",
            "",
            f"Boundary: {definition['boundary']}",
            "",
        ])
    lines.extend([
        "## Schema-semantics coverage",
        "",
        f"The definition-level contract contains `{len(semantics['records'])}` closed record meanings, `{len(semantics['cross_record_invariants'])}` cross-record invariants, and `{len(semantics['negative_witness_requirements'])}` required negative witnesses.",
        "",
        "Executable status:",
        "",
        f"- JSON Schema: `{semantics['implementation_boundary']['json_schema_status']}`",
        f"- Negative fixtures: `{semantics['implementation_boundary']['negative_fixture_status']}`",
        "",
        "## Open questions",
        "",
    ])
    for question in pack["open_questions"]:
        lines.append(f"- `{question['question_id']}`: {question['question']} Blocks: {question['blocks']}. Owner: {question['owner_route']}.")
    lines.extend([
        "",
        "## Drift audit",
        "",
        f"Selected-scope findings: `{drift['summary']['finding_count']}`; open: `{drift['summary']['open_count']}`; handled: `{drift['summary']['handled_count']}`.",
        "",
    ])
    for finding in drift["findings"]:
        lines.append(f"- `{finding['finding_id']}` (`{finding['status']}`): {finding['observed']} Remediation: {finding['remediation']}")
    lines.extend([
        "",
        "## W1 result",
        "",
        f"- `SWU-W1-001`: `{pack['w1_result']['SWU-W1-001']}`",
        f"- `SWU-W1-002`: `{pack['w1_result']['SWU-W1-002']}`",
        f"- `G-W1`: `{pack['w1_result']['G-W1']}`",
        "",
        "Remaining blockers:",
        "",
        bullets(pack["w1_result"]["blockers"]),
        "",
        "## Claim ceiling",
        "",
        pack["claim_ceiling"],
        "",
    ])
    return "\n".join(lines)


def render_index(handled: dict) -> str:
    rows: list[tuple[str, str, str, str]] = []
    for record in handled["records"]:
        rows.append((record["term"].lower(), record["term"], record["concept_id"], record["current_disposition"]))
        for alias in record.get("aliases", []):
            rows.append((alias.lower(), alias, record["concept_id"], "alias"))
        for alias in record.get("rejected_aliases", []):
            rows.append((alias.lower(), alias, record["concept_id"], "rejected-alias"))
    rows.sort()
    lines = [
        "# Governed Ontology Node Definitions Index",
        "",
        "This is a generated lookup view of `handled-definitions.json`. It does not promote candidate definitions.",
        "",
        "| Lookup term | Concept ID | Posture |",
        "|---|---|---|",
    ]
    for _, term, concept_id, posture in rows:
        lines.append(f"| {term} | `{concept_id}` | `{posture}` |")
    lines.append("")
    return "\n".join(lines)


def rendered() -> dict[str, str]:
    pack = json.loads((ROOT / "definition-pack.json").read_text(encoding="utf-8"))
    handled = json.loads((ROOT / "handled-definitions.json").read_text(encoding="utf-8"))
    semantics = json.loads((ROOT / "schema-semantics.json").read_text(encoding="utf-8"))
    drift = json.loads((ROOT / "definition-drift-audit.json").read_text(encoding="utf-8"))
    return {
        "DEFINITION-PACK.md": render_pack(pack, handled, semantics, drift),
        "DEFINITIONS-INDEX.md": render_index(handled),
    }


def main() -> int:
    for name, content in rendered().items():
        (ROOT / name).write_text(content, encoding="utf-8")
    print("RENDER=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
