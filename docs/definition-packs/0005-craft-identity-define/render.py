#!/usr/bin/env python3
"""Render the human view of the machine-canonical CML-07 Define records."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "definition-pack.json"
HANDLED = ROOT / "handled-definitions.json"
OUTPUT = ROOT / "DEFINITION-PACK.md"
LAB = ROOT.parents[2]
SOURCE = Path("/home/vrondelli/projects/domainspec-core")
REUSE_SOURCE_IDS = {
    "CAV2-D20": "SRC-CAV2-D20",
    "CAV2-D32": "SRC-CAV2-D32",
    "CAV2-D59": "SRC-CAV2-D59",
    "CAV2-D60": "SRC-CAV2-D60",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def selected_text(pack: dict, source_id: str) -> tuple[dict, str]:
    item = next(x for x in pack["source_refs"] if x["source_id"] == source_id)
    base = LAB if item["repository"] == "CyberAlchemy-lab" else SOURCE
    path = base / item["path"]
    if item["selector_kind"] == "whole-file":
        text = path.read_text(encoding="utf-8")
    else:
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        text = "".join(lines[item["start_line"] - 1:item["end_line"]])
    return item, text.rstrip()


def quoted(lines: list[str], text: str) -> None:
    lines.extend("> " + line if line else ">" for line in text.splitlines())


def render(pack: dict, handled: dict) -> str:
    records = {x["record_id"]: x for x in handled["records"]}
    lines = [
        "<!-- GENERATED FILE: edit definition-pack.json or handled-definitions.json and run render.py. -->",
        "",
        "# CML-07 Craft Identity Define Pack",
        "",
        "> Generated from machine-canonical Define records. Candidate only; authority effect is none.",
        "",
        f"- Pack: `{pack['pack_id']}`",
        f"- Route: `{pack['producer']['route_id']}`",
        f"- Producer: `{pack['producer']['package_id']}@{pack['producer']['package_version']}`",
        f"- Status: `{pack['status']}`",
        f"- Consumer: `{pack['consumer']['consumer_id']}`",
        "",
        "## Goal",
        "",
        pack["goal"],
        "",
        "## Intent",
        "",
        pack["original_intent"],
        "",
        "## Context",
        "",
        pack["context"]["statement"],
        "",
        f"Context sufficiency: `{pack['context_sufficiency']['status']}`.",
        "",
        "## Concept dispositions",
        "",
        "| Concept | Term | Disposition | Decision owner |",
        "| --- | --- | --- | --- |",
    ]
    for concept in pack["concepts"]:
        record = records[concept["handled_definition_ref"]]
        lines.append(f"| `{concept['concept_id']}` | {concept['term']} | `{concept['current_disposition']}` | `{record['decision_owner_route']}` |")
    lines += ["", "## Resolved definitions", ""]
    for concept in pack["concepts"]:
        record = records[concept["handled_definition_ref"]]
        disposition = record["current_disposition"]
        lines += [
            f"### {record['term']} (`{record['concept_id']}`)",
            "",
            f"- Disposition: `{disposition}`",
            f"- Decision owner: `{record['decision_owner_route']}`",
            f"- Context: {record['context']}",
            f"- Intended use: {record['intended_use']}",
            "",
        ]
        if disposition == "reuse":
            binding = record["reuse"]
            source, text = selected_text(pack, REUSE_SOURCE_IDS[binding["canonical_definition_id"]])
            selector = f"lines:{source['start_line']}-{source['end_line']}" if source["selector_kind"] == "line-range" else "whole-file"
            lines += [
                "#### Exact reused canonical definition",
                "",
                f"- Source definition: `{binding['canonical_definition_id']}`",
                f"- Source: `{source['repository']}:{source['path']}`",
                f"- Selector: `{selector}`",
                f"- Selected digest: `{binding['source_digest']}`",
                f"- Source owner: `{binding['source_owner_route']}`",
                "",
            ]
            quoted(lines, text)
            lines.append("")
        elif disposition in {"propose", "specialize"}:
            payload = record[disposition]
            lines += [
                "#### Normative result",
                "",
                payload["normative_voice"],
                "",
                "#### Formal result",
                "",
                "```text",
                payload["formal_voice"],
                "```",
                "",
                "#### Plain-language result",
                "",
                payload["plain_language_voice"],
                "",
                "#### Domain-context result",
                "",
                payload["domain_context_voice"],
                "",
                "#### Boundary",
                "",
                payload["boundary"],
                "",
                f"Candidate posture: `{payload['status']}`; canonical target: `{payload['canonical_target']}`.",
                "",
            ]
        else:
            payload = record["open"]
            lines += ["#### Open result", "", payload["question"], "", f"- Stop required: `{str(payload['stop_required']).lower()}`", f"- Next action: {payload['next_action']}", ""]
    lines += ["## Explicit relations", ""]
    for relation in pack["relationships"]:
        lines.append(f"- `{relation['source_concept_id']}` — `{relation['relation']}` → `{relation['target_concept_id']}`")
    lines += ["", "## Open questions and stops", ""]
    for item in pack["open_questions_and_conflicts"]:
        lines += [f"### {item['question_id']}", "", item["question"], "", f"- Construction stop: `{str(item['stop_required_for_promotion_or_construction']).lower()}`", f"- Next action: {item['next_action']}", ""]
    lines += ["## Allowed uses", ""] + [f"- {x}" for x in pack["allowed_uses"]]
    lines += ["", "## Blocked actions", ""] + [f"- {x}" for x in pack["blocked_actions"]]
    lines += ["", "## Claim ceiling", "", pack["claim_ceiling"]]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(load(PACK), load(HANDLED)), encoding="utf-8")


if __name__ == "__main__":
    main()
