#!/usr/bin/env python3
"""Deterministically project one Definition/v2 machine record to Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


GENERATOR_ID = "cal.generator.definition-markdown/v2"


def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def bullets(lines: list[str], values: list[str], empty: str = "None declared.") -> None:
    if values:
        lines.extend(f"- {value}" for value in values)
    else:
        lines.append(empty)


def render(definition: dict) -> str:
    formal = definition["voices"]["scientific_formal"]
    plain = definition["voices"]["plain_language"]
    domain = definition["voices"]["domain_context"]
    lines = [
        "<!-- GENERATED FILE: edit definition.json and run the bound generator. -->",
        "",
        f"# {definition['term']}",
        "",
        "> Human projection generated from the machine-canonical `definition.json`.",
        "",
        f"- Definition ID: `{definition['definition_id']}`",
        f"- Version: `{definition['version']}`",
        f"- Semantic owner: `{definition['semantic_owner_ref']}`",
        f"- Authority scope: `{definition['scope']['authority_scope_ref']}`",
        f"- Lifecycle posture reference: `{definition['classification']['lifecycle_posture_ref']}`",
        "",
        "## Scientific/formal voice",
        "",
        formal["normative_statement"],
    ]
    if formal["formal_expression"] is not None:
        lines.extend(["", "```text", formal["formal_expression"], "```"])
    lines.extend(["", "### Notation", ""])
    if formal["notation"]:
        lines.extend(["| Symbol | Meaning |", "| --- | --- |"])
        lines.extend(f"| {esc(item['symbol'])} | {esc(item['meaning'])} |" for item in formal["notation"])
    else:
        lines.append("No notation is required.")
    lines.extend(["", "### Boundary conditions", ""])
    bullets(lines, formal["boundary_conditions"])
    lines.extend(["", "### Testable conditions", ""])
    bullets(lines, formal["testable_conditions"])

    lines.extend(["", "## Plain-language voice", "", plain["explanation"]])
    lines.extend([
        "", "## Domain-context voice", "",
        f"Workspace: `{domain['workspace_ref']}`", "", domain["explanation"], "",
        "### Examples", "",
    ])
    bullets(lines, domain["examples"])

    lines.extend(["", "## Applicability", "", definition["scope"]["applicability"], "", "### Exclusions", ""])
    bullets(lines, definition["scope"]["exclusions"])
    lines.extend(["", "## Boundaries", ""])
    bullets(lines, definition["boundaries"])

    lines.extend(["", "## Sources", ""])
    if definition["source_refs"]:
        lines.extend(["| Source | Selector | Digest | Admission posture |", "| --- | --- | --- | --- |"])
        for item in definition["source_refs"]:
            lines.append(
                f"| {esc(item['source_ref'])} | {esc(item['selector'])} | `{item['content_sha256']}` | "
                f"`{item['admission_posture']}` |"
            )
    else:
        lines.append("No sources declared.")

    lines.extend(["", "## Primary consumers", ""])
    bullets(lines, definition["primary_consumer_refs"])
    lines.extend([
        "", "## Lookup and drift", "",
        f"- Index: `{definition['index_entry']['index_ref']}` / `{definition['index_entry']['entry_id']}`",
        f"- Drift owner: `{definition['drift_route']['owner_ref']}`",
        f"- Audit: `{definition['drift_route']['audit_ref']}`",
        f"- Challenge route: `{definition['drift_route']['challenge_ref']}`",
        "", "## Typed relations", "",
    ])
    if definition["typed_relations"]:
        lines.extend(["| Kind | From | To | Owner |", "| --- | --- | --- | --- |"])
        for item in definition["typed_relations"]:
            lines.append("| " + " | ".join(esc(item[k]) for k in ("relation_kind_ref", "from_ref", "to_ref", "owner_ref")) + " |")
    else:
        lines.append("No typed relations declared.")
    lines.extend(["", "## Evidence", ""])
    bullets(lines, definition["evidence_refs"])
    lines.extend(["", "## Residue", ""])
    bullets(lines, definition["residue_refs"])
    lines.extend(["", "## Claim ceiling", "", definition["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.write_text(render(data), encoding="utf-8")


if __name__ == "__main__":
    main()
