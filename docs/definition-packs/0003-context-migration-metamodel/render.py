#!/usr/bin/env python3
"""Render CTX-00 human projections from canonical machine records."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PACK_PATH = ROOT / "definition-pack.json"
HANDLED_PATH = ROOT / "handled-definitions.json"
AUDIT_PATH = ROOT / "definition-drift-audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_pack(pack: dict, handled: dict, audit: dict) -> str:
    dispositions = pack["disposition_summary"]
    lines = [
        "<!-- GENERATED FILE: edit canonical JSON and run render.py. -->",
        "",
        f"# {pack['title']}",
        "",
        "> Generated from `definition-pack.json`, `handled-definitions.json`, and `definition-drift-audit.json`; this Markdown is not canonical.",
        "",
        f"- Pack: `{pack['pack_id']}`",
        f"- Status: `{pack['status']}`",
        f"- Authority effect: `{pack['authority_effect']}`",
        f"- Promotion ready: `{str(audit['summary']['promotion_ready']).lower()}`",
        "",
        "## Goal",
        "",
        pack["goal"],
        "",
        "## Intent",
        "",
        pack["intent"],
        "",
        "## Dispositions",
        "",
        f"- Reuse: `{len(dispositions['reuse'])}`",
        f"- Specialize: `{len(dispositions['specialize'])}`",
        f"- Revise: `{len(dispositions['revise'])}`",
        f"- Propose: `{len(dispositions['propose'])}`",
        f"- Open: `{len(dispositions['open'])}`",
        "",
        "| ID | Term | Disposition | Plain-language voice |",
        "|---|---|---|---|",
    ]
    for record in handled["records"]:
        plain = record["definition"]["plain_language_voice"].replace("|", "\\|")
        lines.append(f"| `{record['concept_id']}` | {record['term']} | `{record['current_disposition']}` | {plain} |")

    lines.extend(["", "## Candidate definitions", ""])
    for record in handled["records"]:
        definition = record["definition"]
        lines.extend([
            f"### {record['term']} (`{record['concept_id']}`)",
            "",
            f"Disposition: `{record['current_disposition']}`  ",
            f"Owner: `{record['semantic_owner_ref']}`  ",
            f"Status: `{record['candidate_status']}`",
            "",
            f"**Scientific/formal voice:** {definition['scientific_formal_voice']}",
            "",
            f"**Formal model:** `{definition['formal_model']}`",
            "",
            f"**Operational interpretation:** {definition['operational_interpretation']}",
            "",
            f"**Plain-language voice:** {definition['plain_language_voice']}",
            "",
            f"**CyberAlchemy Lab context:** {definition['domain_context_voice']}",
            "",
            f"**Boundary:** {definition['boundary']}",
            "",
            "Promotion blockers:",
            "",
        ])
        lines.extend(f"- {item}" for item in record["promotion_blockers"])
        lines.append("")

    lines.extend(["## Explicit relationships", ""])
    for relation in pack["relationships"]:
        lines.append(
            f"- `{relation['source_concept_id']}` --`{relation['relation_kind']}`--> "
            f"`{relation['target_concept_id']}`: {relation['meaning']}"
        )

    lines.extend(["", "## Drift and blockers", ""])
    for finding in audit["findings"]:
        lines.append(f"- `{finding['finding_id']}` ({finding['severity']}): {finding['conflict']} Remediation: {finding['remediation']}")

    lines.extend(["", "## Promotion blockers", ""])
    lines.extend(f"- {item}" for item in pack["promotion_blockers"])
    lines.extend(["", "## Successor gates", ""])
    lines.extend(f"- `{item}`" for item in pack["successor_gates"])
    lines.extend(["", "## Claim ceiling", "", pack["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def render_index(pack: dict, handled: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit canonical JSON and run render.py. -->",
        "",
        "# CTX-00 Candidate Definitions Index",
        "",
        "> Generated lookup projection. It is not a canonical definition registry.",
        "",
        f"Pack: `{pack['pack_id']}`",
        "",
        "| ID | Term | Disposition | Status | Owner |",
        "|---|---|---|---|---|",
    ]
    for record in sorted(handled["records"], key=lambda item: item["concept_id"]):
        lines.append(
            f"| `{record['concept_id']}` | {record['term']} | `{record['current_disposition']}` | "
            f"`{record['candidate_status']}` | `{record['semantic_owner_ref']}` |"
        )
    lines.extend([
        "",
        "No row is canonical or admitted. Promotion requires the separate gates named by the pack.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def rendered() -> dict[str, str]:
    pack = load(PACK_PATH)
    handled = load(HANDLED_PATH)
    audit = load(AUDIT_PATH)
    return {
        "DEFINITION-PACK.md": render_pack(pack, handled, audit),
        "DEFINITIONS-INDEX.md": render_index(pack, handled),
    }


def main() -> None:
    for name, text in rendered().items():
        (ROOT / name).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
