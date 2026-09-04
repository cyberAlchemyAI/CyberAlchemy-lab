#!/usr/bin/env python3
"""Render the human projection of the Foundation-01 admission decision."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "decision.json"
OUTPUT = ROOT / "DECISION.md"


def esc(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render(data: dict) -> str:
    accepted = data["accepted_candidate"]
    state = data["definition_authority_state"]
    lines = [
        "<!-- GENERATED FILE: edit decision.json and run render.py. -->",
        "",
        f"# {data['title']}",
        "",
        "> Human projection generated from `decision.json`; it is not canonical.",
        "",
        f"- Decision: `{data['decision_id']}`",
        f"- Status: `{data['status']}`",
        f"- Selected option: `{data['selection']['option_id']}`",
        f"- Principal: `{data['selection']['selected_by_principal']}`",
        f"- Authority effect: `{data['authority_effect']}`",
        f"- Manifest: `{accepted['manifest_sha256']}`",
        f"- Validation receipt: `{accepted['validation_receipt_sha256']}`",
        "",
        "## Outcome",
        "",
        data["admission_result"]["effect"],
        "",
        "## Role-scoped determinations",
        "",
        "| Role | Admitted effect | Non-effect |",
        "| --- | --- | --- |",
    ]
    for item in data["role_scoped_determinations"]:
        lines.append(
            "| " + " | ".join(esc(item[key]) for key in ("role_id", "effect", "non_effect")) + " |"
        )

    lines.extend(["", "## Admitted artifact types", ""])
    lines.extend(f"- `{item}`" for item in data["admitted_artifact_types"])

    lines.extend([
        "",
        "## Admitted records",
        "",
        "| Record | Path | Digest | Effect |",
        "| --- | --- | --- | --- |",
    ])
    for item in data["admitted_records"]:
        lines.append(
            "| " + " | ".join(esc(item[key]) for key in ("record_id", "path", "sha256", "admission_effect")) + " |"
        )

    lines.extend([
        "",
        "## Exact source admissions",
        "",
        "| Selector | Digest | Target use |",
        "| --- | --- | --- |",
    ])
    for item in data["source_admissions"]:
        lines.append(
            "| " + " | ".join(esc(item[key]) for key in ("selector", "selected_sha256", "target_use")) + " |"
        )

    lines.extend([
        "",
        "## Definition authority state",
        "",
        f"- Canonical registry: `{state['canonical_registry_path']}`",
        f"- Admitted entries: `{state['admitted_entry_count']}`",
        f"- Undefined critical terms: `{state['undefined_critical_terms']}`",
        f"- Drift snapshot: `{state['drift_snapshot_posture']}`",
        f"- Required next audit: {state['required_next_audit']}",
        "",
        "## Decision Gate",
        "",
        f"- Result: `{data['admission_result']['decision_gate_result']}`",
        f"- Route outcome: `{data['admissibility']['route_outcome']}`",
        f"- Request digest: `{data['admissibility']['request_digest']}`",
        f"- Limitation: {data['admissibility']['ordering_limitation']}",
        "",
        "## Explicit exclusions",
        "",
    ])
    lines.extend(f"- {item}" for item in data["excluded_effects"])
    lines.extend(["", "## Successor obligations", ""])
    lines.extend(f"- {item}" for item in data["successor_obligations"])
    lines.extend(["", "## Claim ceiling", "", data["claim_ceiling"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.write_text(render(json.loads(SOURCE.read_text(encoding="utf-8"))), encoding="utf-8")


if __name__ == "__main__":
    main()
