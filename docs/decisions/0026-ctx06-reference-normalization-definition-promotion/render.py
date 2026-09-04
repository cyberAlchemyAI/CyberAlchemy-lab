#!/usr/bin/env python3
"""Render the CTX06 Definition admission decision and live Definition projections."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
DECISION_SOURCE = ROOT / "decision.json"
DECISION_OUTPUT = ROOT / "DECISION.md"
REGISTRY_SOURCE = LAB / "authority/definitions/registry.json"
REGISTRY_OUTPUT = LAB / "authority/definitions/DEFINITIONS-INDEX.md"
DRIFT_SOURCE = LAB / "authority/definitions/drift-audit.json"
DRIFT_OUTPUT = LAB / "authority/definitions/DEFINITION-DRIFT-AUDIT.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def render_registry(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit registry.json and rerun the bound decision renderer. -->",
        "",
        "# CyberAlchemy Lab Definition Index",
        "",
        "> Generated from `registry.json`; this view is not canonical.",
        "",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Owner: `{data['owner_ref']}`",
        f"- Admission decision: `{data['admission_decision_ref']}`",
        "",
        "## Definition versions",
        "",
        "| ID | Version | Term | Lifecycle | Current | Path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in sorted(data["entries"], key=lambda x: (x["definition_id"], x["version"])):
        exact_ref = f"{item['definition_id']}@{item['version']}"
        current = "yes" if data["current_lookup"].get(item["definition_id"]) == exact_ref else "no"
        lines.append(
            f"| `{item['definition_id']}` | `{item['version']}` | {item['term']} | "
            f"`{item['lifecycle_state']}` | `{current}` | `{item['path']}` |"
        )
    lines.extend(["", "## Current lookup", ""])
    for definition_id, exact_ref in sorted(data["current_lookup"].items()):
        lines.append(f"- `{definition_id}` -> `{exact_ref}`")
    lines.extend(["", "## Identity rule", "", data["identity_rule"], "", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render_drift(data: dict) -> str:
    lines = [
        "<!-- GENERATED FILE: edit drift-audit.json and rerun the bound decision renderer. -->",
        "",
        "# Post-CTX06 Definition drift audit",
        "",
        "> Generated from the machine-canonical `drift-audit.json`.",
        "",
        "## Summary",
        "",
    ]
    lines.extend(f"- {key.replace('_', ' ').title()}: `{value}`" for key, value in data["summary"].items())
    lines.extend(["", "## Findings", ""])
    for item in data["findings"]:
        lines.extend(
            [
                f"### {item['finding_id']} ({item['severity']}, {item['status']})",
                "",
                item["condition"],
                "",
                f"Target: `{item['target']}`",
                "",
                f"Remediation: {item['remediation']}",
                "",
                f"Blocking for: {item['blocking_for']}",
                "",
            ]
        )
    lines.extend(["## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def render_decision(data: dict) -> str:
    selection = data["selection"]
    result = data["admission_result"]
    lines = [
        "<!-- GENERATED FILE: edit decision.json and rerun render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Machine-canonical decision; this Markdown is a generated projection.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Selection: `{selection['selection_token']}`",
        f"- Principal: `{selection['selected_by_principal']}` as `{selection['selected_role']}`",
        f"- Recorded: `{selection['recorded_at']}`",
        "",
        "## Admitted Definition successors",
        "",
        "| Definition | Version | Predecessor | Digest |",
        "| --- | --- | --- | --- |",
    ]
    for item in data["admitted_definitions"]:
        lines.append(f"| `{item['definition_id']}` | `{item['version']}` | `{item['predecessor_ref']}` | `{item['sha256']}` |")
    lines.extend(
        [
            "",
            "## Admission result",
            "",
            f"- Successor Definitions admitted: `{result['successor_definitions_admitted']}`",
            f"- Canonical Definition versions: `{result['canonical_definition_versions']}`",
            f"- Current Definition terms: `{result['current_definition_terms']}`",
            f"- Predecessors withdrawn: `{result['predecessors_withdrawn']}`",
            f"- Artifact types revised: `{result['artifact_types_revised']}`",
            "",
            "## Materialization",
            "",
            data["materialization"]["rule"],
            "",
            data["materialization"]["predecessor_boundary"],
            "",
            data["materialization"]["lookup_boundary"],
            "",
            "## Excluded effects",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines.extend(["", "## Successor obligations", ""])
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines)


def main() -> None:
    write(REGISTRY_OUTPUT, render_registry(load(REGISTRY_SOURCE)))
    write(DRIFT_OUTPUT, render_drift(load(DRIFT_SOURCE)))
    if DECISION_SOURCE.is_file():
        write(DECISION_OUTPUT, render_decision(load(DECISION_SOURCE)))


if __name__ == "__main__":
    main()
